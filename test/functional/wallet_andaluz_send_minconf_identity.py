#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet send minconf identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal, assert_raises_rpc_error


class AndaluzWalletSendMinconfIdentityTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 2
        self.setup_clean_chain = True
        self.chain = "regtest"
        self.wallet_names = []
        self.extra_args = [
            [
                "-dnsseed=0",
                "-fixedseeds=0",
            ],
            [
                "-dnsseed=0",
                "-fixedseeds=0",
            ],
        ]

    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    def assert_andaluz_runtime_identity(self, node):
        assert_equal(
            node.getblockchaininfo()["chain"],
            "regtest",
        )

        subversion = node.getnetworkinfo()["subversion"]

        assert subversion.startswith("/AndaluzcoinCore:"), subversion
        assert "Satoshi" not in subversion, subversion
        assert "Bitcoin" not in subversion, subversion

    def assert_wallet_identity(self, wallet, wallet_name):
        wallet_info = wallet.getwalletinfo()

        assert_equal(wallet_info["walletname"], wallet_name)
        assert_equal(wallet_info["private_keys_enabled"], True)
        assert_equal(wallet_info["descriptors"], True)
        assert_equal(wallet_info["format"], "sqlite")

    def assert_valid_wallet_address(self, node, wallet, address):
        address_info = node.validateaddress(address)
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
        miner_wallet_name = "andaluz_send_minconf_miner"
        source_wallet_name = "andaluz_send_minconf_source"
        minconf_wallet_name = "andaluz_send_minconf_spender"
        receiver_wallet_name = "andaluz_send_minconf_receiver"

        coinbase_amount = Decimal("50.00000000")
        funding_amount = Decimal("2.00000000")
        payment_amount = Decimal("1.00000000")
        fee_rate_sat_vb = 10

        self.log.info("Checking initial Andaluzcoin runtime identity")

        self.assert_andaluz_runtime_identity(self.nodes[0])
        self.assert_andaluz_runtime_identity(self.nodes[1])

        self.log.info("Creating Andaluzcoin wallets")

        self.nodes[0].createwallet(
            wallet_name=miner_wallet_name,
        )

        self.nodes[0].createwallet(
            wallet_name=source_wallet_name,
        )

        self.nodes[0].createwallet(
            wallet_name=receiver_wallet_name,
        )

        self.nodes[1].createwallet(
            wallet_name=minconf_wallet_name,
        )

        miner = self.nodes[0].get_wallet_rpc(
            miner_wallet_name,
        )

        source = self.nodes[0].get_wallet_rpc(
            source_wallet_name,
        )

        receiver = self.nodes[0].get_wallet_rpc(
            receiver_wallet_name,
        )

        minconf_spender = self.nodes[1].get_wallet_rpc(
            minconf_wallet_name,
        )

        self.assert_wallet_identity(
            miner,
            miner_wallet_name,
        )

        self.assert_wallet_identity(
            source,
            source_wallet_name,
        )

        self.assert_wallet_identity(
            minconf_spender,
            minconf_wallet_name,
        )

        self.assert_wallet_identity(
            receiver,
            receiver_wallet_name,
        )

        self.log.info("Mining spendable ALUZ to source wallet")

        source_mining_address = source.getnewaddress(
            "",
            "bech32",
        )

        miner_mining_address = miner.getnewaddress(
            "",
            "bech32",
        )

        self.assert_valid_wallet_address(
            self.nodes[0],
            source,
            source_mining_address,
        )

        self.assert_valid_wallet_address(
            self.nodes[0],
            miner,
            miner_mining_address,
        )

        source_blocks = self.nodes[0].generatetoaddress(
            1,
            source_mining_address,
            called_by_framework=True,
        )

        assert_equal(
            len(source_blocks),
            1,
        )

        maturity_blocks = self.nodes[0].generatetoaddress(
            100,
            miner_mining_address,
            called_by_framework=True,
        )

        assert_equal(
            len(maturity_blocks),
            100,
        )

        self.sync_all()

        assert_equal(
            source.getbalances()["mine"]["trusted"],
            coinbase_amount,
        )

        self.log.info(
            "Funding minconf wallet with 2 ALUZ"
        )

        minconf_address = minconf_spender.getnewaddress(
            "andaluz-minconf-funding",
            "bech32",
        )

        self.assert_valid_wallet_address(
            self.nodes[1],
            minconf_spender,
            minconf_address,
        )

        funding_txid = source.sendtoaddress(
            minconf_address,
            funding_amount,
        )

        assert_equal(
            len(funding_txid),
            64,
        )

        self.sync_all()

        assert funding_txid in self.nodes[0].getrawmempool(), (
            self.nodes[0].getrawmempool()
        )

        assert funding_txid in self.nodes[1].getrawmempool(), (
            self.nodes[1].getrawmempool()
        )

        self.log.info(
            "Mining three confirmations for minconf funding transaction"
        )

        confirmation_blocks = self.nodes[0].generatetoaddress(
            3,
            miner_mining_address,
            called_by_framework=True,
        )

        assert_equal(
            len(confirmation_blocks),
            3,
        )

        self.sync_all()

        self.nodes[0].syncwithvalidationinterfacequeue()
        self.nodes[1].syncwithvalidationinterfacequeue()

        assert_equal(
            self.nodes[0].getmempoolinfo()["size"],
            0,
        )

        assert_equal(
            self.nodes[1].getmempoolinfo()["size"],
            0,
        )

        self.log.info(
            "Checking funding output has exactly three confirmations"
        )

        funding_utxos = [
            utxo
            for utxo in minconf_spender.listunspent(
                0,
                9999999,
            )
            if utxo["txid"] == funding_txid
        ]

        assert_equal(
            len(funding_utxos),
            1,
        )

        funding_utxo = funding_utxos[0]

        assert_equal(
            funding_utxo["amount"],
            funding_amount,
        )

        assert_equal(
            funding_utxo["confirmations"],
            3,
        )

        assert_equal(
            minconf_spender.getbalances()["mine"]["trusted"],
            funding_amount,
        )

        receiver_address = receiver.getnewaddress(
            "andaluz-send-minconf-receiver",
            "bech32",
        )

        self.assert_valid_wallet_address(
            self.nodes[0],
            receiver,
            receiver_address,
        )

        mempool_before = set(
            self.nodes[0].getrawmempool()
        )

        assert_equal(
            mempool_before,
            set(),
        )

        self.log.info(
            "Checking minconf=4 rejects three-confirmation funds"
        )

        assert_raises_rpc_error(
            -4,
            "Insufficient funds",
            minconf_spender.send,
            outputs={
                receiver_address: payment_amount,
            },
            fee_rate=fee_rate_sat_vb,
            options={
                "minconf": 4,
                "add_to_wallet": False,
            },
        )

        self.log.info(
            "Checking negative minconf is rejected"
        )

        assert_raises_rpc_error(
            -8,
            "Negative minconf",
            minconf_spender.send,
            outputs={
                receiver_address: payment_amount,
            },
            fee_rate=fee_rate_sat_vb,
            options={
                "minconf": -4,
                "add_to_wallet": False,
            },
        )

        self.log.info(
            "Checking rejected minconf attempts changed no state"
        )

        assert_equal(
            set(self.nodes[0].getrawmempool()),
            mempool_before,
        )

        assert_equal(
            set(self.nodes[1].getrawmempool()),
            mempool_before,
        )

        assert_equal(
            minconf_spender.getbalances()["mine"]["trusted"],
            funding_amount,
        )

        assert_equal(
            receiver.getbalance(),
            Decimal("0E-8"),
        )

        self.log.info(
            "Creating modern send with minconf=3"
        )

        send_result = minconf_spender.send(
            outputs={
                receiver_address: payment_amount,
            },
            fee_rate=fee_rate_sat_vb,
            options={
                "minconf": 3,
                "add_to_wallet": False,
            },
        )

        assert_equal(
            send_result["complete"],
            True,
        )

        assert "txid" in send_result, send_result
        assert "hex" in send_result, send_result

        spend_txid = send_result["txid"]
        raw_hex = send_result["hex"]

        assert_equal(
            len(spend_txid),
            64,
        )

        assert raw_hex, send_result

        self.log.info(
            "Checking minconf=3 selected the three-confirmation UTXO"
        )

        decoded_tx = self.nodes[1].decoderawtransaction(
            raw_hex,
        )

        assert_equal(
            decoded_tx["txid"],
            spend_txid,
        )

        assert_equal(
            len(decoded_tx["vin"]),
            1,
        )

        assert_equal(
            decoded_tx["vin"][0]["txid"],
            funding_txid,
        )

        assert_equal(
            decoded_tx["vin"][0]["vout"],
            funding_utxo["vout"],
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

        total_output_amount = sum(
            (
                output["value"]
                for output in decoded_tx["vout"]
            ),
            Decimal("0E-8"),
        )

        actual_fee = (
            funding_amount
            - total_output_amount
        )

        assert actual_fee > Decimal("0"), actual_fee
        assert actual_fee < payment_amount, actual_fee

        self.log.info(
            "Checking minconf transaction was not automatically broadcast"
        )

        assert_equal(
            set(self.nodes[0].getrawmempool()),
            set(),
        )

        assert_equal(
            set(self.nodes[1].getrawmempool()),
            set(),
        )

        assert not self.wallet_has_txid(
            minconf_spender,
            spend_txid,
        ), spend_txid

        assert not self.wallet_has_txid(
            receiver,
            spend_txid,
        ), spend_txid

        assert_equal(
            minconf_spender.getbalance(),
            funding_amount,
        )

        assert_equal(
            receiver.getbalance(),
            Decimal("0E-8"),
        )

        self.log.info(
            "Checking completed minconf transaction is mempool-valid"
        )

        accept_result = self.nodes[1].testmempoolaccept(
            [raw_hex],
        )

        assert_equal(
            len(accept_result),
            1,
        )

        assert_equal(
            accept_result[0]["txid"],
            spend_txid,
        )

        assert_equal(
            accept_result[0]["allowed"],
            True,
        )

        self.log.info(
            "Broadcasting minconf Andaluzcoin transaction"
        )

        broadcast_txid = self.nodes[1].sendrawtransaction(
            raw_hex,
        )

        assert_equal(
            broadcast_txid,
            spend_txid,
        )

        self.sync_all()

        assert spend_txid in self.nodes[0].getrawmempool(), (
            self.nodes[0].getrawmempool()
        )

        assert spend_txid in self.nodes[1].getrawmempool(), (
            self.nodes[1].getrawmempool()
        )

        self.nodes[0].syncwithvalidationinterfacequeue()
        self.nodes[1].syncwithvalidationinterfacequeue()

        self.wait_until(
            lambda: self.wallet_has_txid(
                minconf_spender,
                spend_txid,
            ),
            timeout=60,
        )

        self.log.info(
            "Checking sender pending accounting"
        )

        sender_pending_tx = minconf_spender.gettransaction(
            spend_txid,
        )

        assert_equal(
            sender_pending_tx["amount"],
            -payment_amount,
        )

        assert_equal(
            sender_pending_tx["fee"],
            -actual_fee,
        )

        assert_equal(
            sender_pending_tx["confirmations"],
            0,
        )

        sender_pending_entry = self.find_wallet_tx(
            minconf_spender,
            spend_txid,
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
            "Checking receiver pending accounting"
        )

        self.wait_until(
            lambda:
                receiver.getbalances()["mine"]["untrusted_pending"]
                == payment_amount,
            timeout=60,
        )

        receiver_pending_tx = receiver.gettransaction(
            spend_txid,
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
            spend_txid,
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
            "Confirming minconf Andaluzcoin transaction"
        )

        confirm_block_hash = self.nodes[0].generatetoaddress(
            1,
            miner_mining_address,
            called_by_framework=True,
        )[0]

        self.sync_all()

        assert_equal(
            self.nodes[0].getbestblockhash(),
            confirm_block_hash,
        )

        assert_equal(
            self.nodes[1].getbestblockhash(),
            confirm_block_hash,
        )

        assert_equal(
            self.nodes[0].getmempoolinfo()["size"],
            0,
        )

        assert_equal(
            self.nodes[1].getmempoolinfo()["size"],
            0,
        )

        self.nodes[0].syncwithvalidationinterfacequeue()
        self.nodes[1].syncwithvalidationinterfacequeue()

        expected_sender_balance = (
            funding_amount
            - payment_amount
            - actual_fee
        )

        self.wait_until(
            lambda:
                minconf_spender.getbalances()["mine"]["trusted"]
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

        sender_confirmed_tx = minconf_spender.gettransaction(
            spend_txid,
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
            minconf_spender.getbalance(),
            expected_sender_balance,
        )

        self.log.info(
            "Checking confirmed receiver accounting"
        )

        receiver_confirmed_tx = receiver.gettransaction(
            spend_txid,
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
            minconf_spender,
            spend_txid,
            "send",
        )

        receiver_confirmed_entry = self.find_wallet_tx(
            receiver,
            spend_txid,
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
            source,
            source_wallet_name,
        )

        self.assert_wallet_identity(
            minconf_spender,
            minconf_wallet_name,
        )

        self.assert_wallet_identity(
            receiver,
            receiver_wallet_name,
        )

        self.log.info(
            "Checking final Andaluzcoin runtime identity"
        )

        self.assert_andaluz_runtime_identity(
            self.nodes[0],
        )

        self.assert_andaluz_runtime_identity(
            self.nodes[1],
        )


if __name__ == "__main__":
    AndaluzWalletSendMinconfIdentityTest(__file__).main()
