#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet send lock-unspents identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletSendLockUnspentsIdentityTest(BitcoinTestFramework):
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
        miner_wallet_name = "andaluz_send_lock_unspents_miner"
        sender_wallet_name = "andaluz_send_lock_unspents_sender"
        receiver_wallet_name = "andaluz_send_lock_unspents_receiver"

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

        self.log.info("Selecting exact Andaluzcoin input")

        sender_utxos = sender.listunspent(
            101,
            9999999,
            [sender_mining_address],
        )

        assert_equal(len(sender_utxos), 1)

        selected_utxo = sender_utxos[0]

        assert_equal(
            selected_utxo["amount"],
            coinbase_amount,
        )

        selected_outpoint = {
            "txid": selected_utxo["txid"],
            "vout": selected_utxo["vout"],
        }

        assert_equal(
            sender.listlockunspent(),
            [],
        )

        #
        # First send: lock_unspents=True
        #

        first_receiver_address = receiver.getnewaddress(
            "andaluz-send-lock-unspents-first",
            "bech32",
        )

        self.assert_valid_wallet_address(
            receiver,
            first_receiver_address,
        )

        self.log.info(
            "Creating non-broadcast send transaction with lock_unspents enabled"
        )

        mempool_before = self.nodes[0].getrawmempool()

        first_result = sender.send(
            outputs={
                first_receiver_address: payment_amount,
            },
            fee_rate=fee_rate_sat_vb,
            options={
                "inputs": [
                    selected_outpoint,
                ],
                "add_inputs": False,
                "add_to_wallet": False,
                "lock_unspents": True,
            },
        )

        assert_equal(
            first_result["complete"],
            True,
        )

        assert "txid" in first_result, first_result
        assert "hex" in first_result, first_result

        first_txid = first_result["txid"]
        first_hex = first_result["hex"]

        assert_equal(len(first_txid), 64)
        assert first_hex, first_result

        self.log.info(
            "Checking first transaction uses exact selected input"
        )

        decoded_first = self.nodes[0].decoderawtransaction(
            first_hex,
        )

        assert_equal(
            decoded_first["txid"],
            first_txid,
        )

        first_inputs = [
            {
                "txid": vin["txid"],
                "vout": vin["vout"],
            }
            for vin in decoded_first["vin"]
        ]

        assert_equal(
            first_inputs,
            [selected_outpoint],
        )

        first_recipient_outputs = [
            output
            for output in decoded_first["vout"]
            if output["scriptPubKey"].get("address")
            == first_receiver_address
        ]

        assert_equal(
            len(first_recipient_outputs),
            1,
        )

        assert_equal(
            first_recipient_outputs[0]["value"],
            payment_amount,
        )

        self.log.info(
            "Checking selected input became wallet-locked"
        )

        locked_coins = sender.listlockunspent()

        assert_equal(
            len(locked_coins),
            1,
        )

        assert selected_outpoint in locked_coins, locked_coins

        self.log.info(
            "Checking lock-unspents transaction was not broadcast"
        )

        assert_equal(
            self.nodes[0].getrawmempool(),
            mempool_before,
        )

        assert not self.wallet_has_txid(
            sender,
            first_txid,
        ), first_txid

        assert not self.wallet_has_txid(
            receiver,
            first_txid,
        ), first_txid

        assert_equal(
            sender.getbalance(),
            initial_sender_balance,
        )

        assert_equal(
            receiver.getbalance(),
            Decimal("0E-8"),
        )

        first_accept_result = self.nodes[0].testmempoolaccept(
            [first_hex],
        )

        assert_equal(
            len(first_accept_result),
            1,
        )

        assert_equal(
            first_accept_result[0]["txid"],
            first_txid,
        )

        assert_equal(
            first_accept_result[0]["allowed"],
            True,
        )

        #
        # Second send: manually select same locked input.
        # Modern send should automatically unlock the explicitly
        # selected coin when lock_unspents is not requested.
        #

        second_receiver_address = receiver.getnewaddress(
            "andaluz-send-lock-unspents-second",
            "bech32",
        )

        self.assert_valid_wallet_address(
            receiver,
            second_receiver_address,
        )

        self.log.info(
            "Manually selecting locked input again without lock_unspents"
        )

        second_result = sender.send(
            outputs={
                second_receiver_address: payment_amount,
            },
            fee_rate=fee_rate_sat_vb,
            options={
                "inputs": [
                    selected_outpoint,
                ],
                "add_inputs": False,
                "add_to_wallet": False,
            },
        )

        assert_equal(
            second_result["complete"],
            True,
        )

        assert "txid" in second_result, second_result
        assert "hex" in second_result, second_result

        second_txid = second_result["txid"]
        second_hex = second_result["hex"]

        assert_equal(len(second_txid), 64)
        assert second_hex, second_result

        self.log.info(
            "Checking second transaction uses the same exact selected input"
        )

        decoded_second = self.nodes[0].decoderawtransaction(
            second_hex,
        )

        assert_equal(
            decoded_second["txid"],
            second_txid,
        )

        second_inputs = [
            {
                "txid": vin["txid"],
                "vout": vin["vout"],
            }
            for vin in decoded_second["vin"]
        ]

        assert_equal(
            second_inputs,
            [selected_outpoint],
        )

        second_recipient_outputs = [
            output
            for output in decoded_second["vout"]
            if output["scriptPubKey"].get("address")
            == second_receiver_address
        ]

        assert_equal(
            len(second_recipient_outputs),
            1,
        )

        assert_equal(
            second_recipient_outputs[0]["value"],
            payment_amount,
        )

        self.log.info(
            "Checking manually selected locked input remains explicitly locked"
        )

        locked_after_second_send = sender.listlockunspent()

        assert_equal(
            len(locked_after_second_send),
            1,
        )

        assert selected_outpoint in locked_after_second_send, (
            locked_after_second_send
        )

        self.log.info(
            "Explicitly unlocking selected Andaluzcoin input"
        )

        assert_equal(
            sender.lockunspent(
                True,
                [selected_outpoint],
            ),
            True,
        )

        assert_equal(
            sender.listlockunspent(),
            [],
        )

        self.log.info(
            "Checking second transaction was still not broadcast automatically"
        )

        assert_equal(
            self.nodes[0].getrawmempool(),
            mempool_before,
        )

        assert not self.wallet_has_txid(
            sender,
            second_txid,
        ), second_txid

        assert not self.wallet_has_txid(
            receiver,
            second_txid,
        ), second_txid

        assert_equal(
            sender.getbalance(),
            initial_sender_balance,
        )

        assert_equal(
            receiver.getbalance(),
            Decimal("0E-8"),
        )

        second_accept_result = self.nodes[0].testmempoolaccept(
            [second_hex],
        )

        assert_equal(
            len(second_accept_result),
            1,
        )

        assert_equal(
            second_accept_result[0]["txid"],
            second_txid,
        )

        assert_equal(
            second_accept_result[0]["allowed"],
            True,
        )

        #
        # Broadcast the second transaction to prove the automatically
        # unlocked input remains normally spendable.
        #

        self.log.info(
            "Broadcasting second transaction after automatic unlock"
        )

        broadcast_txid = self.nodes[0].sendrawtransaction(
            second_hex,
        )

        assert_equal(
            broadcast_txid,
            second_txid,
        )

        assert second_txid in self.nodes[0].getrawmempool(), (
            second_txid,
            self.nodes[0].getrawmempool(),
        )

        assert first_txid not in self.nodes[0].getrawmempool(), (
            first_txid,
            self.nodes[0].getrawmempool(),
        )

        self.nodes[0].syncwithvalidationinterfacequeue()

        self.log.info(
            "Checking sender recognizes explicitly broadcast transaction"
        )

        self.wait_until(
            lambda: self.wallet_has_txid(
                sender,
                second_txid,
            ),
            timeout=60,
        )

        sender_pending_tx = sender.gettransaction(
            second_txid,
        )

        assert_equal(
            sender_pending_tx["amount"],
            -payment_amount,
        )

        assert sender_pending_tx["fee"] < Decimal("0"), (
            sender_pending_tx
        )

        assert_equal(
            sender_pending_tx["confirmations"],
            0,
        )

        actual_fee = -sender_pending_tx["fee"]

        assert actual_fee > Decimal("0"), actual_fee

        sender_pending_entry = self.find_wallet_tx(
            sender,
            second_txid,
            "send",
        )

        assert_equal(
            sender_pending_entry["amount"],
            -payment_amount,
        )

        assert_equal(
            sender_pending_entry["confirmations"],
            0,
        )

        self.log.info(
            "Checking receiver sees pending ALUZ"
        )

        self.wait_until(
            lambda:
                receiver.getbalances()["mine"]["untrusted_pending"]
                == payment_amount,
            timeout=60,
        )

        receiver_pending_tx = receiver.gettransaction(
            second_txid,
        )

        assert_equal(
            receiver_pending_tx["amount"],
            payment_amount,
        )

        assert_equal(
            receiver_pending_tx["confirmations"],
            0,
        )

        assert not self.wallet_has_txid(
            receiver,
            first_txid,
        ), first_txid

        #
        # Confirmation
        #

        self.log.info(
            "Confirming automatically unlocked explicit-input transaction"
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
            - actual_fee
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
            second_txid,
        )

        assert_equal(
            sender_confirmed_tx["amount"],
            -payment_amount,
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
            second_txid,
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
            second_txid,
            "send",
        )

        receiver_confirmed_entry = self.find_wallet_tx(
            receiver,
            second_txid,
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
            "Checking final wallet lock state"
        )

        assert_equal(
            sender.listlockunspent(),
            [],
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
    AndaluzWalletSendLockUnspentsIdentityTest(__file__).main()
