#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet send add-inputs identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal, assert_raises_rpc_error


class AndaluzWalletSendAddInputsIdentityTest(BitcoinTestFramework):
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
        miner_wallet_name = "andaluz_send_add_inputs_miner"
        sender_wallet_name = "andaluz_send_add_inputs_sender"
        receiver_wallet_name = "andaluz_send_add_inputs_receiver"

        coinbase_amount = Decimal("50.00000000")
        initial_sender_balance = coinbase_amount * 2
        payment_amount = Decimal("51.00000000")
        fee_rate_sat_vb = 10

        insufficient_inputs_error = (
            "The preselected coins total amount does not cover the transaction target. "
            "Please allow other inputs to be automatically selected or include more coins manually"
        )

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

        self.log.info("Mining two independent spendable ALUZ UTXOs")

        sender_mining_address = sender.getnewaddress("", "bech32")
        miner_mining_address = miner.getnewaddress("", "bech32")

        self.assert_valid_wallet_address(sender, sender_mining_address)
        self.assert_valid_wallet_address(miner, miner_mining_address)

        sender_blocks = self.nodes[0].generatetoaddress(
            2,
            sender_mining_address,
            called_by_framework=True,
        )
        assert_equal(len(sender_blocks), 2)

        maturity_blocks = self.nodes[0].generatetoaddress(
            100,
            miner_mining_address,
            called_by_framework=True,
        )
        assert_equal(len(maturity_blocks), 100)

        self.nodes[0].syncwithvalidationinterfacequeue()

        assert_equal(
            sender.getbalances()["mine"]["trusted"],
            initial_sender_balance,
        )

        assert_equal(
            receiver.getbalance(),
            Decimal("0E-8"),
        )

        self.log.info("Selecting one insufficient 50 ALUZ preset input")

        sender_utxos = sender.listunspent(
            101,
            9999999,
            [sender_mining_address],
        )

        assert_equal(len(sender_utxos), 2)

        for utxo in sender_utxos:
            assert_equal(
                utxo["amount"],
                coinbase_amount,
            )

        sorted_utxos = sorted(
            sender_utxos,
            key=lambda utxo: (
                utxo["txid"],
                utxo["vout"],
            ),
        )

        selected_utxo = sorted_utxos[0]
        supplemental_utxo = sorted_utxos[1]

        selected_outpoint = {
            "txid": selected_utxo["txid"],
            "vout": selected_utxo["vout"],
        }

        supplemental_outpoint = {
            "txid": supplemental_utxo["txid"],
            "vout": supplemental_utxo["vout"],
        }

        receiver_address = receiver.getnewaddress(
            "andaluz-send-add-inputs-receiver",
            "bech32",
        )

        self.assert_valid_wallet_address(
            receiver,
            receiver_address,
        )

        mempool_before = self.nodes[0].getrawmempool()

        self.log.info(
            "Checking preset input alone is insufficient when add_inputs is omitted"
        )

        assert_raises_rpc_error(
            -4,
            insufficient_inputs_error,
            sender.send,
            outputs={
                receiver_address: payment_amount,
            },
            fee_rate=fee_rate_sat_vb,
            options={
                "inputs": [
                    selected_outpoint,
                ],
                "add_to_wallet": False,
            },
        )

        self.log.info(
            "Checking preset input alone is insufficient with add_inputs=false"
        )

        assert_raises_rpc_error(
            -4,
            insufficient_inputs_error,
            sender.send,
            outputs={
                receiver_address: payment_amount,
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

        self.log.info("Checking rejected attempts changed no wallet state")

        assert_equal(
            self.nodes[0].getrawmempool(),
            mempool_before,
        )

        assert_equal(
            sender.getbalance(),
            initial_sender_balance,
        )

        assert_equal(
            receiver.getbalance(),
            Decimal("0E-8"),
        )

        assert_equal(
            sender.listlockunspent(),
            [],
        )

        self.log.info(
            "Creating transaction with preset input and add_inputs=true"
        )

        send_result = sender.send(
            outputs={
                receiver_address: payment_amount,
            },
            fee_rate=fee_rate_sat_vb,
            options={
                "inputs": [
                    selected_outpoint,
                ],
                "add_inputs": True,
                "add_to_wallet": False,
            },
        )

        assert_equal(
            send_result["complete"],
            True,
        )

        assert "txid" in send_result, send_result
        assert "hex" in send_result, send_result

        txid = send_result["txid"]
        raw_hex = send_result["hex"]

        assert_equal(len(txid), 64)
        assert raw_hex, send_result

        self.log.info(
            "Checking wallet automatically supplemented the preset input"
        )

        decoded_tx = self.nodes[0].decoderawtransaction(
            raw_hex,
        )

        assert_equal(
            decoded_tx["txid"],
            txid,
        )

        decoded_inputs = {
            (
                vin["txid"],
                vin["vout"],
            )
            for vin in decoded_tx["vin"]
        }

        expected_inputs = {
            (
                selected_outpoint["txid"],
                selected_outpoint["vout"],
            ),
            (
                supplemental_outpoint["txid"],
                supplemental_outpoint["vout"],
            ),
        }

        assert_equal(
            decoded_inputs,
            expected_inputs,
        )

        assert_equal(
            len(decoded_tx["vin"]),
            2,
        )

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
            payment_amount,
        )

        total_input_amount = (
            selected_utxo["amount"]
            + supplemental_utxo["amount"]
        )

        total_output_amount = sum(
            (
                output["value"]
                for output in decoded_tx["vout"]
            ),
            Decimal("0E-8"),
        )

        decoded_fee = (
            total_input_amount
            - total_output_amount
        )

        assert decoded_fee > Decimal("0"), decoded_fee

        self.log.info(
            "Checking add-inputs transaction was not automatically broadcast"
        )

        assert_equal(
            self.nodes[0].getrawmempool(),
            mempool_before,
        )

        assert not self.wallet_has_txid(
            sender,
            txid,
        ), txid

        assert not self.wallet_has_txid(
            receiver,
            txid,
        ), txid

        assert_equal(
            sender.getbalance(),
            initial_sender_balance,
        )

        assert_equal(
            receiver.getbalance(),
            Decimal("0E-8"),
        )

        self.log.info(
            "Checking completed transaction is mempool-valid"
        )

        accept_result = self.nodes[0].testmempoolaccept(
            [raw_hex],
        )

        assert_equal(
            len(accept_result),
            1,
        )

        assert_equal(
            accept_result[0]["txid"],
            txid,
        )

        assert_equal(
            accept_result[0]["allowed"],
            True,
        )

        self.log.info(
            "Broadcasting add-inputs Andaluzcoin transaction"
        )

        broadcast_txid = self.nodes[0].sendrawtransaction(
            raw_hex,
        )

        assert_equal(
            broadcast_txid,
            txid,
        )

        assert txid in self.nodes[0].getrawmempool(), (
            txid,
            self.nodes[0].getrawmempool(),
        )

        self.nodes[0].syncwithvalidationinterfacequeue()

        self.wait_until(
            lambda: self.wallet_has_txid(
                sender,
                txid,
            ),
            timeout=60,
        )

        self.log.info(
            "Checking sender pending accounting"
        )

        sender_pending_tx = sender.gettransaction(
            txid,
        )

        assert_equal(
            sender_pending_tx["amount"],
            -payment_amount,
        )

        assert_equal(
            sender_pending_tx["fee"],
            -decoded_fee,
        )

        assert_equal(
            sender_pending_tx["confirmations"],
            0,
        )

        sender_pending_entry = self.find_wallet_tx(
            sender,
            txid,
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
            "Checking receiver sees pending 51 ALUZ payment"
        )

        self.wait_until(
            lambda:
                receiver.getbalances()["mine"]["untrusted_pending"]
                == payment_amount,
            timeout=60,
        )

        receiver_pending_tx = receiver.gettransaction(
            txid,
        )

        assert_equal(
            receiver_pending_tx["amount"],
            payment_amount,
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
            payment_amount,
        )

        assert_equal(
            receiver_pending_entry["confirmations"],
            0,
        )

        self.log.info(
            "Confirming add-inputs Andaluzcoin transaction"
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
            - decoded_fee
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
            txid,
        )

        assert_equal(
            sender_confirmed_tx["amount"],
            -payment_amount,
        )

        assert_equal(
            sender_confirmed_tx["fee"],
            -decoded_fee,
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
    AndaluzWalletSendAddInputsIdentityTest(__file__).main()
