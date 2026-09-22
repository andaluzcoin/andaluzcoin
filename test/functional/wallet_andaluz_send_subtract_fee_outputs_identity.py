#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet send subtract-fee-from-outputs identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletSendSubtractFeeOutputsIdentityTest(BitcoinTestFramework):
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
        assert_equal(
            self.nodes[0].getblockchaininfo()["chain"],
            "regtest",
        )

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
            entry
            for entry in wallet.listtransactions("*", 100)
            if entry.get("txid") == txid
            and entry.get("category") == category
        ]

        assert_equal(len(matches), 1)
        return matches[0]

    def run_test(self):
        miner_wallet_name = "andaluz_send_subtract_fee_miner"
        sender_wallet_name = "andaluz_send_subtract_fee_sender"
        receiver_wallet_name = "andaluz_send_subtract_fee_receiver"

        coinbase_amount = Decimal("50.00000000")
        gross_amount = Decimal("1.00000000")
        fee_rate_sat_vb = 10

        self.log.info("Checking initial Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()

        self.log.info("Creating Andaluzcoin wallets")
        self.nodes[0].createwallet(wallet_name=miner_wallet_name)
        self.nodes[0].createwallet(wallet_name=sender_wallet_name)
        self.nodes[0].createwallet(wallet_name=receiver_wallet_name)

        miner = self.nodes[0].get_wallet_rpc(miner_wallet_name)
        sender = self.nodes[0].get_wallet_rpc(sender_wallet_name)
        receiver = self.nodes[0].get_wallet_rpc(receiver_wallet_name)

        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Mining spendable ALUZ to sender")

        sender_mining_address = sender.getnewaddress("", "bech32")
        miner_mining_address = miner.getnewaddress("", "bech32")

        self.assert_valid_wallet_address(
            sender,
            sender_mining_address,
        )

        self.assert_valid_wallet_address(
            miner,
            miner_mining_address,
        )

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

        initial_sender_balance = (
            sender.getbalances()["mine"]["trusted"]
        )

        assert_equal(
            initial_sender_balance,
            coinbase_amount,
        )

        assert_equal(
            receiver.getbalance(),
            Decimal("0E-8"),
        )

        self.log.info("Creating Andaluzcoin receiver address")

        receiver_address = receiver.getnewaddress(
            "andaluz-send-subtract-fee-receiver",
            "bech32",
        )

        self.assert_valid_wallet_address(
            receiver,
            receiver_address,
        )

        self.log.info(
            "Sending 1 ALUZ gross amount with fee subtracted from output 0"
        )

        send_result = sender.send(
            outputs={
                receiver_address: gross_amount,
            },
            fee_rate=fee_rate_sat_vb,
            options={
                "subtract_fee_from_outputs": [0],
            },
        )

        assert_equal(
            send_result["complete"],
            True,
        )

        assert "txid" in send_result, send_result

        txid = send_result["txid"]
        assert_equal(len(txid), 64)

        self.log.info(
            "Checking modern send transaction was broadcast"
        )

        assert txid in self.nodes[0].getrawmempool(), (
            txid,
            self.nodes[0].getrawmempool(),
        )

        self.nodes[0].syncwithvalidationinterfacequeue()

        self.log.info(
            "Checking sender fee and gross-debit accounting"
        )

        sender_pending_tx = sender.gettransaction(
            txid=txid,
            verbose=True,
        )

        assert sender_pending_tx["fee"] < Decimal("0"), (
            sender_pending_tx
        )

        actual_fee = -sender_pending_tx["fee"]

        assert actual_fee > Decimal("0"), actual_fee
        assert actual_fee < gross_amount, actual_fee

        expected_receiver_amount = (
            gross_amount
            - actual_fee
        )

        expected_sender_balance = (
            initial_sender_balance
            - gross_amount
        )

        assert_equal(
            sender_pending_tx["amount"],
            -expected_receiver_amount,
        )

        assert_equal(
            sender_pending_tx["confirmations"],
            0,
        )

        self.log.info(
            "Checking decoded receiver output has fee subtracted"
        )

        decoded_tx = sender_pending_tx["decoded"]

        recipient_outputs = [
            output
            for output in decoded_tx["vout"]
            if output["scriptPubKey"].get("address")
            == receiver_address
        ]

        assert_equal(
            len(recipient_outputs),
            1,
        )

        assert_equal(
            recipient_outputs[0]["value"],
            expected_receiver_amount,
        )

        assert recipient_outputs[0]["value"] < gross_amount, (
            recipient_outputs[0]
        )

        self.log.info(
            "Checking sender pending wallet history"
        )

        sender_pending_entry = self.find_wallet_tx(
            sender,
            txid,
            "send",
        )

        assert_equal(
            sender_pending_entry["amount"],
            -expected_receiver_amount,
        )

        assert_equal(
            sender_pending_entry["confirmations"],
            0,
        )

        self.log.info(
            "Checking receiver pending amount equals gross amount minus fee"
        )

        self.wait_until(
            lambda:
                receiver.getbalances()["mine"]["untrusted_pending"]
                == expected_receiver_amount,
            timeout=60,
        )

        receiver_pending_tx = receiver.gettransaction(
            txid,
        )

        assert_equal(
            receiver_pending_tx["amount"],
            expected_receiver_amount,
        )

        assert_equal(
            receiver_pending_tx["confirmations"],
            0,
        )

        receiver_pending_entry = self.find_wallet_tx(
            receiver,
            txid,
            "receive",
        )

        assert_equal(
            receiver_pending_entry["amount"],
            expected_receiver_amount,
        )

        assert_equal(
            receiver_pending_entry["confirmations"],
            0,
        )

        self.log.info(
            "Confirming subtract-fee-from-output transaction"
        )

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
            lambda:
                sender.getbalances()["mine"]["trusted"]
                == expected_sender_balance,
            timeout=60,
        )

        self.wait_until(
            lambda:
                receiver.getbalances()["mine"]["trusted"]
                == expected_receiver_amount,
            timeout=60,
        )

        self.log.info(
            "Checking confirmed sender accounting"
        )

        sender_confirmed_tx = sender.gettransaction(
            txid,
        )

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
            expected_sender_balance,
        )

        self.log.info(
            "Checking confirmed receiver accounting"
        )

        receiver_confirmed_tx = receiver.gettransaction(
            txid,
        )

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

        self.log.info(
            "Checking confirmed wallet history"
        )

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

        self.log.info(
            "Checking gross sender debit identity"
        )

        assert_equal(
            initial_sender_balance
            - sender.getbalance(),
            gross_amount,
        )

        assert_equal(
            expected_receiver_amount
            + actual_fee,
            gross_amount,
        )

        self.log.info(
            "Checking final Andaluzcoin wallet identities"
        )

        self.assert_wallet_identity(
            miner,
            miner_wallet_name,
        )

        self.assert_wallet_identity(
            sender,
            sender_wallet_name,
        )

        self.assert_wallet_identity(
            receiver,
            receiver_wallet_name,
        )

        self.log.info(
            "Checking final Andaluzcoin runtime identity"
        )

        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletSendSubtractFeeOutputsIdentityTest(__file__).main()
