#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet dust and change identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal, assert_raises_rpc_error


class AndaluzWalletDustChangeIdentityTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True
        self.chain = "regtest"
        self.wallet_names = []
        self.extra_args = [[
            "-dnsseed=0",
            "-fixedseeds=0",
            "-connect=0",
            "-fallbackfee=0.00010000",
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

    def run_test(self):
        miner_wallet_name = "andaluz_dust_change_miner"
        sender_wallet_name = "andaluz_dust_change_sender"
        receiver_wallet_name = "andaluz_dust_change_receiver"

        coinbase_amount = Decimal("50.00000000")
        payment_amount = Decimal("0.01000000")
        dust_amount = Decimal("0.00000001")

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

        assert_equal(
            sender.getbalances()["mine"]["trusted"],
            coinbase_amount,
        )

        self.log.info("Creating small-payment Andaluzcoin receiver address")
        receiver_address = receiver.getnewaddress(
            "andaluz-dust-change-receiver",
            "bech32",
        )
        self.assert_valid_wallet_address(receiver, receiver_address)

        self.log.info("Sending normal small Andaluzcoin payment")
        txid = sender.sendtoaddress(
            address=receiver_address,
            amount=payment_amount,
        )

        assert txid in self.nodes[0].getrawmempool(), (
            txid,
            self.nodes[0].getrawmempool(),
        )

        self.nodes[0].syncwithvalidationinterfacequeue()

        sender_unconfirmed_tx = sender.gettransaction(
            txid=txid,
            verbose=True,
        )

        assert sender_unconfirmed_tx["fee"] < Decimal("0"), sender_unconfirmed_tx
        actual_fee = -sender_unconfirmed_tx["fee"]
        assert actual_fee > Decimal("0"), actual_fee

        decoded_tx = sender_unconfirmed_tx["decoded"]

        self.log.info("Checking payment and automatic Andaluzcoin change outputs")
        assert_equal(len(decoded_tx["vout"]), 2)

        payment_outputs = []
        change_outputs = []

        for vout in decoded_tx["vout"]:
            script_pub_key = vout["scriptPubKey"]
            assert "address" in script_pub_key, vout

            output_address = script_pub_key["address"]

            if output_address == receiver_address:
                payment_outputs.append(vout)
                assert "ischange" not in vout, vout
                continue

            sender_address_info = sender.getaddressinfo(output_address)

            if sender_address_info["ischange"]:
                change_outputs.append(vout)
                assert_equal(sender_address_info["ismine"], True)
                assert_equal(sender_address_info["solvable"], True)
                assert_equal(vout["ischange"], True)

        assert_equal(len(payment_outputs), 1)
        assert_equal(len(change_outputs), 1)

        payment_output = payment_outputs[0]
        change_output = change_outputs[0]

        assert_equal(payment_output["value"], payment_amount)

        expected_change = coinbase_amount - payment_amount - actual_fee
        assert_equal(change_output["value"], expected_change)

        # A valid wallet-created change output must be far above a one-satoshi
        # dust output.
        assert change_output["value"] > dust_amount, change_output

        self.log.info("Checking receiver sees pending small ALUZ payment")
        self.wait_until(
            lambda: receiver.getbalances()["mine"]["untrusted_pending"]
            == payment_amount,
            timeout=60,
        )

        receiver_pending_tx = receiver.gettransaction(txid)
        assert_equal(receiver_pending_tx["amount"], payment_amount)
        assert_equal(receiver_pending_tx["confirmations"], 0)

        self.log.info("Confirming small Andaluzcoin payment")
        confirm_block_hash = self.nodes[0].generatetoaddress(
            1,
            miner_mining_address,
            called_by_framework=True,
        )[0]

        assert_equal(self.nodes[0].getbestblockhash(), confirm_block_hash)
        assert_equal(self.nodes[0].getmempoolinfo()["size"], 0)

        self.nodes[0].syncwithvalidationinterfacequeue()

        expected_sender_balance = (
            coinbase_amount
            - payment_amount
            - actual_fee
        )

        self.wait_until(
            lambda: receiver.getbalances()["mine"]["trusted"]
            == payment_amount,
            timeout=60,
        )

        self.wait_until(
            lambda: sender.getbalances()["mine"]["trusted"]
            == expected_sender_balance,
            timeout=60,
        )

        self.log.info("Checking confirmed sender and receiver accounting")
        sender_confirmed_tx = sender.gettransaction(txid)
        assert_equal(sender_confirmed_tx["amount"], -payment_amount)
        assert_equal(sender_confirmed_tx["fee"], -actual_fee)
        assert_equal(sender_confirmed_tx["confirmations"], 1)
        assert_equal(sender_confirmed_tx["blockhash"], confirm_block_hash)

        receiver_confirmed_tx = receiver.gettransaction(txid)
        assert_equal(receiver_confirmed_tx["amount"], payment_amount)
        assert_equal(receiver_confirmed_tx["confirmations"], 1)
        assert_equal(receiver_confirmed_tx["blockhash"], confirm_block_hash)

        assert_equal(sender.getbalance(), expected_sender_balance)
        assert_equal(receiver.getbalance(), payment_amount)

        self.log.info("Checking wallet rejects explicit one-satoshi dust output")
        sender_balance_before_dust = sender.getbalance()
        receiver_balance_before_dust = receiver.getbalance()
        mempool_before_dust = self.nodes[0].getrawmempool()

        dust_receiver_address = receiver.getnewaddress(
            "andaluz-dust-receiver",
            "bech32",
        )
        remainder_address = sender.getnewaddress(
            "andaluz-dust-remainder",
            "bech32",
        )

        self.assert_valid_wallet_address(receiver, dust_receiver_address)
        self.assert_valid_wallet_address(sender, remainder_address)

        assert_raises_rpc_error(
            -8,
            f"Specified output amount to {dust_receiver_address} is below dust threshold",
            sender.sendall,
            recipients=[
                {dust_receiver_address: dust_amount},
                remainder_address,
            ],
        )

        self.nodes[0].syncwithvalidationinterfacequeue()

        self.log.info("Checking rejected dust attempt changed no wallet state")
        assert_equal(sender.getbalance(), sender_balance_before_dust)
        assert_equal(receiver.getbalance(), receiver_balance_before_dust)
        assert_equal(self.nodes[0].getrawmempool(), mempool_before_dust)

        self.log.info("Checking final Andaluzcoin wallet identities")
        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletDustChangeIdentityTest(__file__).main()
