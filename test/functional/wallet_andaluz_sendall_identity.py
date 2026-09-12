#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet sendall identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletSendAllIdentityTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True
        self.chain = "regtest"
        self.wallet_names = []
        self.extra_args = [[
            "-dnsseed=0",
            "-fixedseeds=0",
            "-connect=0",
        ]]

    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    def assert_andaluz_runtime_identity(self):
        assert_equal(self.nodes[0].getblockchaininfo()["chain"], "regtest")

        subversion = self.nodes[0].getnetworkinfo()["subversion"]
        assert subversion.startswith("/AndaluzcoinCore:"), subversion
        assert "Satoshi" not in subversion, subversion
        assert "Bitcoin" not in subversion, subversion

    def assert_wallet_identity(self, wallet, wallet_name):
        wallet_info = wallet.getwalletinfo()
        assert_equal(wallet_info["walletname"], wallet_name)
        assert_equal(wallet_info["private_keys_enabled"], True)
        assert_equal(wallet_info["descriptors"], True)
        assert_equal(wallet_info["format"], "sqlite")

    def assert_valid_wallet_address(self, wallet, address):
        address_info = self.nodes[0].validateaddress(address)
        assert_equal(address_info["isvalid"], True)

        wallet_address_info = wallet.getaddressinfo(address)
        assert_equal(wallet_address_info["ismine"], True)
        assert_equal(wallet_address_info["solvable"], True)

    def find_wallet_tx(self, wallet, txid, category):
        matches = [
            entry for entry in wallet.listtransactions("*", 100)
            if entry.get("txid") == txid
            and entry.get("category") == category
        ]

        assert_equal(len(matches), 1)
        return matches[0]

    def run_test(self):
        miner_wallet_name = "andaluz_sendall_miner"
        sender_wallet_name = "andaluz_sendall_sender"
        receiver_wallet_name = "andaluz_sendall_receiver"

        coinbase_amount = Decimal("50.00000000")
        fee_rate_sat_vb = 10

        self.log.info("Checking initial Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()

        self.log.info("Creating Andaluzcoin miner, sender, and receiver wallets")
        self.nodes[0].createwallet(wallet_name=miner_wallet_name)
        self.nodes[0].createwallet(wallet_name=sender_wallet_name)
        self.nodes[0].createwallet(wallet_name=receiver_wallet_name)

        miner = self.nodes[0].get_wallet_rpc(miner_wallet_name)
        sender = self.nodes[0].get_wallet_rpc(sender_wallet_name)
        receiver = self.nodes[0].get_wallet_rpc(receiver_wallet_name)

        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Mining spendable Andaluzcoin balance to sender")
        sender_mining_address = sender.getnewaddress("", "bech32")
        miner_mining_address = miner.getnewaddress("", "bech32")

        self.assert_valid_wallet_address(sender, sender_mining_address)
        self.assert_valid_wallet_address(miner, miner_mining_address)

        sender_blocks = self.nodes[0].generatetoaddress(
            1,
            sender_mining_address,
            called_by_framework=True,
        )
        assert_equal(len(sender_blocks), 1)

        maturity_blocks = self.nodes[0].generatetoaddress(
            100,
            miner_mining_address,
            called_by_framework=True,
        )
        assert_equal(len(maturity_blocks), 100)

        self.nodes[0].syncwithvalidationinterfacequeue()

        initial_sender_balance = sender.getbalances()["mine"]["trusted"]

        assert_equal(initial_sender_balance, coinbase_amount)
        assert_equal(
            receiver.getbalances()["mine"]["trusted"],
            Decimal("0E-8"),
        )

        self.log.info("Creating Andaluzcoin sendall receiver address")
        receiver_address = receiver.getnewaddress(
            "andaluz-sendall-receiver",
            "bech32",
        )
        self.assert_valid_wallet_address(receiver, receiver_address)

        self.log.info("Sweeping sender wallet with Andaluzcoin sendall RPC")
        sendall_result = sender.sendall(
            recipients=[receiver_address],
            fee_rate=fee_rate_sat_vb,
        )

        assert_equal(sendall_result["complete"], True)
        assert "txid" in sendall_result, sendall_result

        txid = sendall_result["txid"]
        assert_equal(len(txid), 64)

        self.log.info("Checking sendall transaction entered mempool")
        assert txid in self.nodes[0].getrawmempool(), (
            txid,
            self.nodes[0].getrawmempool(),
        )

        self.nodes[0].syncwithvalidationinterfacequeue()

        self.log.info("Checking sender sendall transaction")
        sender_pending_tx = sender.gettransaction(
            txid=txid,
            verbose=True,
        )

        assert sender_pending_tx["fee"] < Decimal("0"), sender_pending_tx
        assert_equal(sender_pending_tx["confirmations"], 0)

        actual_fee = -sender_pending_tx["fee"]
        assert actual_fee > Decimal("0"), actual_fee

        expected_receiver_amount = initial_sender_balance - actual_fee
        assert expected_receiver_amount > Decimal("0"), expected_receiver_amount

        assert_equal(
            sender_pending_tx["amount"],
            -expected_receiver_amount,
        )

        decoded_tx = sender_pending_tx["decoded"]

        self.log.info("Checking sendall produced one sweep output")
        assert_equal(len(decoded_tx["vout"]), 1)

        sweep_output = decoded_tx["vout"][0]

        assert_equal(
            sweep_output["scriptPubKey"]["address"],
            receiver_address,
        )
        assert_equal(
            sweep_output["value"],
            expected_receiver_amount,
        )

        self.log.info("Checking sender wallet was swept completely")
        assert_equal(
            sender.getbalances()["mine"]["trusted"],
            Decimal("0E-8"),
        )
        assert_equal(
            sender.getbalance(),
            Decimal("0E-8"),
        )

        self.log.info("Checking sender wallet history")
        sender_list_entry = self.find_wallet_tx(
            sender,
            txid,
            "send",
        )

        assert_equal(
            sender_list_entry["amount"],
            -expected_receiver_amount,
        )
        assert_equal(
            sender_list_entry["confirmations"],
            0,
        )

        self.log.info("Checking receiver sees pending swept ALUZ")
        self.wait_until(
            lambda: receiver.getbalances()["mine"]["untrusted_pending"]
            == expected_receiver_amount,
            timeout=60,
        )

        receiver_pending_tx = receiver.gettransaction(txid)

        assert_equal(
            receiver_pending_tx["amount"],
            expected_receiver_amount,
        )
        assert_equal(
            receiver_pending_tx["confirmations"],
            0,
        )

        receiver_list_entry = self.find_wallet_tx(
            receiver,
            txid,
            "receive",
        )

        assert_equal(
            receiver_list_entry["amount"],
            expected_receiver_amount,
        )
        assert_equal(
            receiver_list_entry["confirmations"],
            0,
        )

        self.log.info("Confirming Andaluzcoin sendall transaction")
        confirm_block_hash = self.nodes[0].generatetoaddress(
            1,
            miner_mining_address,
            called_by_framework=True,
        )[0]

        assert_equal(
            self.nodes[0].getbestblockhash(),
            confirm_block_hash,
        )
        assert_equal(
            self.nodes[0].getmempoolinfo()["size"],
            0,
        )

        self.nodes[0].syncwithvalidationinterfacequeue()

        self.wait_until(
            lambda: receiver.getbalances()["mine"]["trusted"]
            == expected_receiver_amount,
            timeout=60,
        )

        self.log.info("Checking confirmed sender sweep accounting")
        sender_confirmed_tx = sender.gettransaction(txid)

        assert_equal(
            sender_confirmed_tx["amount"],
            -expected_receiver_amount,
        )
        assert_equal(
            sender_confirmed_tx["fee"],
            -actual_fee,
        )
        assert_equal(
            sender_confirmed_tx["confirmations"],
            1,
        )
        assert_equal(
            sender_confirmed_tx["blockhash"],
            confirm_block_hash,
        )

        assert_equal(
            sender.getbalance(),
            Decimal("0E-8"),
        )

        self.log.info("Checking confirmed receiver sweep accounting")
        receiver_confirmed_tx = receiver.gettransaction(txid)

        assert_equal(
            receiver_confirmed_tx["amount"],
            expected_receiver_amount,
        )
        assert_equal(
            receiver_confirmed_tx["confirmations"],
            1,
        )
        assert_equal(
            receiver_confirmed_tx["blockhash"],
            confirm_block_hash,
        )

        assert_equal(
            receiver.getbalance(),
            expected_receiver_amount,
        )

        self.log.info("Checking confirmed wallet history")
        sender_confirmed_entry = self.find_wallet_tx(
            sender,
            txid,
            "send",
        )
        receiver_confirmed_entry = self.find_wallet_tx(
            receiver,
            txid,
            "receive",
        )

        assert_equal(
            sender_confirmed_entry["amount"],
            -expected_receiver_amount,
        )
        assert_equal(
            sender_confirmed_entry["confirmations"],
            1,
        )

        assert_equal(
            receiver_confirmed_entry["amount"],
            expected_receiver_amount,
        )
        assert_equal(
            receiver_confirmed_entry["confirmations"],
            1,
        )

        self.log.info("Checking sendall conservation of ALUZ value")
        assert_equal(
            expected_receiver_amount + actual_fee,
            initial_sender_balance,
        )

        self.log.info("Checking final Andaluzcoin wallet identities")
        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletSendAllIdentityTest(__file__).main()
