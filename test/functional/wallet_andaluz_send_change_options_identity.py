#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet send change-options identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletSendChangeOptionsIdentityTest(BitcoinTestFramework):
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

        return wallet_address_info

    def wallet_has_txid(self, wallet, txid):
        return any(
            entry.get("txid") == txid
            for entry in wallet.listtransactions("*", 100)
        )

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
        miner_wallet_name = "andaluz_send_change_miner"
        sender_wallet_name = "andaluz_send_change_sender"
        receiver_wallet_name = "andaluz_send_change_receiver"

        coinbase_amount = Decimal("50.00000000")
        payment_amount = Decimal("1.25000000")
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

        receiver_address = receiver.getnewaddress(
            "andaluz-send-change-receiver",
            "bech32",
        )

        self.assert_valid_wallet_address(
            receiver,
            receiver_address,
        )

        #
        # Explicit change address + explicit change position
        #

        self.log.info(
            "Creating explicit Andaluzcoin change address"
        )

        explicit_change_address = sender.getrawchangeaddress(
            "bech32",
        )

        explicit_change_info = self.assert_valid_wallet_address(
            sender,
            explicit_change_address,
        )

        assert_equal(
            explicit_change_info["ischange"],
            True,
        )

        self.log.info(
            "Creating send transaction with explicit change address and position"
        )

        mempool_before = self.nodes[0].getrawmempool()

        explicit_result = sender.send(
            outputs={
                receiver_address: payment_amount,
            },
            fee_rate=fee_rate_sat_vb,
            options={
                "add_to_wallet": False,
                "change_address": explicit_change_address,
                "change_position": 0,
            },
        )

        assert_equal(
            explicit_result["complete"],
            True,
        )

        assert "txid" in explicit_result, explicit_result
        assert "hex" in explicit_result, explicit_result

        explicit_txid = explicit_result["txid"]
        explicit_hex = explicit_result["hex"]

        assert_equal(len(explicit_txid), 64)
        assert explicit_hex, explicit_result

        decoded_explicit = self.nodes[0].decoderawtransaction(
            explicit_hex,
        )

        assert_equal(
            decoded_explicit["txid"],
            explicit_txid,
        )

        assert len(decoded_explicit["vout"]) >= 2, decoded_explicit

        self.log.info(
            "Checking explicit change output is exactly vout 0"
        )

        assert_equal(
            decoded_explicit["vout"][0]["scriptPubKey"].get("address"),
            explicit_change_address,
        )

        recipient_outputs = [
            output
            for output in decoded_explicit["vout"]
            if output["scriptPubKey"].get("address")
            == receiver_address
        ]

        assert_equal(
            len(recipient_outputs),
            1,
        )

        assert_equal(
            recipient_outputs[0]["value"],
            payment_amount,
        )

        assert recipient_outputs[0]["n"] != 0, recipient_outputs[0]

        explicit_change_amount = (
            decoded_explicit["vout"][0]["value"]
        )

        assert explicit_change_amount > Decimal("0"), (
            explicit_change_amount
        )

        explicit_fee = (
            coinbase_amount
            - payment_amount
            - explicit_change_amount
        )

        assert explicit_fee > Decimal("0"), explicit_fee

        self.log.info(
            "Checking explicit-change transaction was not broadcast"
        )

        assert_equal(
            self.nodes[0].getrawmempool(),
            mempool_before,
        )

        assert not self.wallet_has_txid(
            sender,
            explicit_txid,
        ), explicit_txid

        assert not self.wallet_has_txid(
            receiver,
            explicit_txid,
        ), explicit_txid

        assert_equal(
            sender.getbalance(),
            initial_sender_balance,
        )

        assert_equal(
            receiver.getbalance(),
            Decimal("0E-8"),
        )

        #
        # Explicit change type
        #

        self.log.info(
            "Creating transaction with legacy Andaluzcoin change type"
        )

        legacy_result = sender.send(
            outputs={
                receiver_address: payment_amount,
            },
            fee_rate=fee_rate_sat_vb,
            options={
                "add_to_wallet": False,
                "change_type": "legacy",
                "change_position": 0,
            },
        )

        assert_equal(
            legacy_result["complete"],
            True,
        )

        assert "txid" in legacy_result, legacy_result
        assert "hex" in legacy_result, legacy_result

        legacy_txid = legacy_result["txid"]
        legacy_hex = legacy_result["hex"]

        assert_equal(len(legacy_txid), 64)
        assert legacy_hex, legacy_result

        decoded_legacy = self.nodes[0].decoderawtransaction(
            legacy_hex,
        )

        assert_equal(
            decoded_legacy["txid"],
            legacy_txid,
        )

        legacy_change_address = (
            decoded_legacy["vout"][0]["scriptPubKey"].get("address")
        )

        assert legacy_change_address, decoded_legacy

        self.log.info(
            "Checking generated change output is legacy and positioned at vout 0"
        )

        legacy_validate = self.nodes[0].validateaddress(
            legacy_change_address,
        )

        assert_equal(
            legacy_validate["isvalid"],
            True,
        )

        assert_equal(
            legacy_validate["iswitness"],
            False,
        )

        legacy_change_info = sender.getaddressinfo(
            legacy_change_address,
        )

        assert_equal(
            legacy_change_info["ismine"],
            True,
        )

        assert_equal(
            legacy_change_info["solvable"],
            True,
        )

        assert_equal(
            legacy_change_info["ischange"],
            True,
        )

        legacy_recipient_outputs = [
            output
            for output in decoded_legacy["vout"]
            if output["scriptPubKey"].get("address")
            == receiver_address
        ]

        assert_equal(
            len(legacy_recipient_outputs),
            1,
        )

        assert_equal(
            legacy_recipient_outputs[0]["value"],
            payment_amount,
        )

        assert legacy_recipient_outputs[0]["n"] != 0, (
            legacy_recipient_outputs[0]
        )

        self.log.info(
            "Checking legacy-change transaction was also not broadcast"
        )

        assert_equal(
            self.nodes[0].getrawmempool(),
            mempool_before,
        )

        assert not self.wallet_has_txid(
            sender,
            legacy_txid,
        ), legacy_txid

        assert not self.wallet_has_txid(
            receiver,
            legacy_txid,
        ), legacy_txid

        assert_equal(
            sender.getbalance(),
            initial_sender_balance,
        )

        assert_equal(
            receiver.getbalance(),
            Decimal("0E-8"),
        )

        #
        # Broadcast the explicit-change transaction
        #

        self.log.info(
            "Checking explicit-change transaction is mempool-valid"
        )

        accept_result = self.nodes[0].testmempoolaccept(
            [explicit_hex],
        )

        assert_equal(
            len(accept_result),
            1,
        )

        assert_equal(
            accept_result[0]["txid"],
            explicit_txid,
        )

        assert_equal(
            accept_result[0]["allowed"],
            True,
        )

        self.log.info(
            "Broadcasting explicit-change Andaluzcoin transaction"
        )

        broadcast_txid = self.nodes[0].sendrawtransaction(
            explicit_hex,
        )

        assert_equal(
            broadcast_txid,
            explicit_txid,
        )

        assert explicit_txid in self.nodes[0].getrawmempool(), (
            explicit_txid,
            self.nodes[0].getrawmempool(),
        )

        self.nodes[0].syncwithvalidationinterfacequeue()

        self.wait_until(
            lambda: self.wallet_has_txid(
                sender,
                explicit_txid,
            ),
            timeout=60,
        )

        sender_pending_tx = sender.gettransaction(
            explicit_txid,
        )

        assert_equal(
            sender_pending_tx["amount"],
            -payment_amount,
        )

        assert_equal(
            sender_pending_tx["fee"],
            -explicit_fee,
        )

        assert_equal(
            sender_pending_tx["confirmations"],
            0,
        )

        sender_list_entry = self.find_wallet_tx(
            sender,
            explicit_txid,
            "send",
        )

        assert_equal(
            sender_list_entry["amount"],
            -payment_amount,
        )

        assert_equal(
            sender_list_entry["confirmations"],
            0,
        )

        self.log.info(
            "Checking receiver pending ALUZ accounting"
        )

        self.wait_until(
            lambda:
                receiver.getbalances()["mine"]["untrusted_pending"]
                == payment_amount,
            timeout=60,
        )

        receiver_pending_tx = receiver.gettransaction(
            explicit_txid,
        )

        assert_equal(
            receiver_pending_tx["amount"],
            payment_amount,
        )

        assert_equal(
            receiver_pending_tx["confirmations"],
            0,
        )

        #
        # Confirm transaction
        #

        self.log.info(
            "Confirming explicit-change Andaluzcoin transaction"
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

        expected_sender_balance = (
            initial_sender_balance
            - payment_amount
            - explicit_fee
        )

        self.wait_until(
            lambda:
                sender.getbalances()["mine"]["trusted"]
                == expected_sender_balance,
            timeout=60,
        )

        self.wait_until(
            lambda:
                receiver.getbalances()["mine"]["trusted"]
                == payment_amount,
            timeout=60,
        )

        self.log.info(
            "Checking confirmed sender accounting"
        )

        sender_confirmed_tx = sender.gettransaction(
            explicit_txid,
        )

        assert_equal(
            sender_confirmed_tx["amount"],
            -payment_amount,
        )

        assert_equal(
            sender_confirmed_tx["fee"],
            -explicit_fee,
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
            "Checking explicit change output is owned as change"
        )

        confirmed_change_info = sender.getaddressinfo(
            explicit_change_address,
        )

        assert_equal(
            confirmed_change_info["ismine"],
            True,
        )

        assert_equal(
            confirmed_change_info["ischange"],
            True,
        )

        self.log.info(
            "Checking confirmed receiver accounting"
        )

        receiver_confirmed_tx = receiver.gettransaction(
            explicit_txid,
        )

        assert_equal(
            receiver_confirmed_tx["amount"],
            payment_amount,
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
            payment_amount,
        )

        sender_confirmed_entry = self.find_wallet_tx(
            sender,
            explicit_txid,
            "send",
        )

        receiver_confirmed_entry = self.find_wallet_tx(
            receiver,
            explicit_txid,
            "receive",
        )

        assert_equal(
            sender_confirmed_entry["amount"],
            -payment_amount,
        )

        assert_equal(
            sender_confirmed_entry["confirmations"],
            1,
        )

        assert_equal(
            receiver_confirmed_entry["amount"],
            payment_amount,
        )

        assert_equal(
            receiver_confirmed_entry["confirmations"],
            1,
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
    AndaluzWalletSendChangeOptionsIdentityTest(__file__).main()
