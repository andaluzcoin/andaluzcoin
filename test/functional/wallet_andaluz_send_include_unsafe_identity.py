#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet send include-unsafe identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal, assert_raises_rpc_error


class AndaluzWalletSendIncludeUnsafeIdentityTest(BitcoinTestFramework):
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
        miner_wallet_name = "andaluz_send_include_unsafe_miner"
        source_wallet_name = "andaluz_send_include_unsafe_source"
        unsafe_wallet_name = "andaluz_send_include_unsafe_spender"
        receiver_wallet_name = "andaluz_send_include_unsafe_receiver"

        coinbase_amount = Decimal("50.00000000")
        unsafe_funding_amount = Decimal("2.00000000")
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
            wallet_name=unsafe_wallet_name,
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

        unsafe_spender = self.nodes[1].get_wallet_rpc(
            unsafe_wallet_name,
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
            unsafe_spender,
            unsafe_wallet_name,
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

        assert_equal(
            unsafe_spender.getbalance(),
            Decimal("0E-8"),
        )

        self.log.info(
            "Creating destination in separate Andaluzcoin wallet"
        )

        unsafe_address = unsafe_spender.getnewaddress(
            "andaluz-unsafe-incoming",
            "bech32",
        )

        receiver_address = receiver.getnewaddress(
            "andaluz-include-unsafe-receiver",
            "bech32",
        )

        self.assert_valid_wallet_address(
            self.nodes[1],
            unsafe_spender,
            unsafe_address,
        )

        self.assert_valid_wallet_address(
            self.nodes[0],
            receiver,
            receiver_address,
        )

        self.log.info(
            "Creating unconfirmed external 2 ALUZ payment"
        )

        funding_txid = source.sendtoaddress(
            unsafe_address,
            unsafe_funding_amount,
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

        self.nodes[0].syncwithvalidationinterfacequeue()
        self.nodes[1].syncwithvalidationinterfacequeue()

        self.log.info(
            "Checking incoming payment is unconfirmed and unsafe"
        )

        self.wait_until(
            lambda:
                unsafe_spender.getbalances()["mine"]["untrusted_pending"]
                == unsafe_funding_amount,
            timeout=60,
        )

        unsafe_balances = unsafe_spender.getbalances()["mine"]

        assert_equal(
            unsafe_balances["trusted"],
            Decimal("0E-8"),
        )

        assert_equal(
            unsafe_balances["untrusted_pending"],
            unsafe_funding_amount,
        )

        funding_utxos = [
            utxo
            for utxo in unsafe_spender.listunspent(
                0,
                9999999,
                [],
                True,
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
            unsafe_funding_amount,
        )

        assert_equal(
            funding_utxo["confirmations"],
            0,
        )

        assert_equal(
            funding_utxo["safe"],
            False,
        )

        mempool_before_rejection_0 = set(
            self.nodes[0].getrawmempool()
        )

        mempool_before_rejection_1 = set(
            self.nodes[1].getrawmempool()
        )

        assert_equal(
            mempool_before_rejection_0,
            {funding_txid},
        )

        assert_equal(
            mempool_before_rejection_1,
            {funding_txid},
        )

        self.log.info(
            "Checking modern send rejects unsafe input by default"
        )

        assert_raises_rpc_error(
            -4,
            "Insufficient funds",
            unsafe_spender.send,
            outputs={
                receiver_address: payment_amount,
            },
            fee_rate=fee_rate_sat_vb,
        )

        self.log.info(
            "Checking rejected send changed no mempool or balance state"
        )

        assert_equal(
            set(self.nodes[0].getrawmempool()),
            mempool_before_rejection_0,
        )

        assert_equal(
            set(self.nodes[1].getrawmempool()),
            mempool_before_rejection_1,
        )

        assert_equal(
            unsafe_spender.getbalances()["mine"]["trusted"],
            Decimal("0E-8"),
        )

        assert_equal(
            unsafe_spender.getbalances()["mine"]["untrusted_pending"],
            unsafe_funding_amount,
        )

        assert_equal(
            receiver.getbalance(),
            Decimal("0E-8"),
        )

        self.log.info(
            "Retrying modern send with include_unsafe=true"
        )

        send_result = unsafe_spender.send(
            outputs={
                receiver_address: payment_amount,
            },
            fee_rate=fee_rate_sat_vb,
            options={
                "include_unsafe": True,
            },
        )

        assert_equal(
            send_result["complete"],
            True,
        )

        assert "txid" in send_result, send_result

        spend_txid = send_result["txid"]

        assert_equal(
            len(spend_txid),
            64,
        )

        self.sync_all()

        self.log.info(
            "Checking include-unsafe transaction was broadcast"
        )

        mempool_0 = set(
            self.nodes[0].getrawmempool()
        )

        mempool_1 = set(
            self.nodes[1].getrawmempool()
        )

        assert_equal(
            mempool_0,
            {
                funding_txid,
                spend_txid,
            },
        )

        assert_equal(
            mempool_1,
            {
                funding_txid,
                spend_txid,
            },
        )

        self.nodes[0].syncwithvalidationinterfacequeue()
        self.nodes[1].syncwithvalidationinterfacequeue()

        self.log.info(
            "Checking child transaction spends unsafe funding transaction"
        )

        unsafe_pending_tx = unsafe_spender.gettransaction(
            txid=spend_txid,
            verbose=True,
        )

        assert_equal(
            unsafe_pending_tx["confirmations"],
            0,
        )

        assert_equal(
            unsafe_pending_tx["amount"],
            -payment_amount,
        )

        assert unsafe_pending_tx["fee"] < Decimal("0"), (
            unsafe_pending_tx
        )

        actual_fee = -unsafe_pending_tx["fee"]

        assert actual_fee > Decimal("0"), actual_fee
        assert actual_fee < payment_amount, actual_fee

        decoded_tx = unsafe_pending_tx["decoded"]

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

        self.log.info(
            "Checking receiver sees pending 1 ALUZ child payment"
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
            "Confirming unsafe parent and include-unsafe child"
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

        expected_unsafe_balance = (
            unsafe_funding_amount
            - payment_amount
            - actual_fee
        )

        self.wait_until(
            lambda:
                unsafe_spender.getbalances()["mine"]["trusted"]
                == expected_unsafe_balance,
            timeout=60,
        )

        self.wait_until(
            lambda:
                receiver.getbalances()["mine"]["trusted"]
                == payment_amount,
            timeout=60,
        )

        self.log.info(
            "Checking confirmed include-unsafe sender accounting"
        )

        unsafe_confirmed_tx = unsafe_spender.gettransaction(
            spend_txid,
        )

        assert_equal(
            unsafe_confirmed_tx["amount"],
            -payment_amount,
        )

        assert_equal(
            unsafe_confirmed_tx["fee"],
            -actual_fee,
        )

        assert_equal(
            unsafe_confirmed_tx["confirmations"],
            1,
        )

        assert_equal(
            unsafe_confirmed_tx["blockhash"],
            confirm_block_hash,
        )

        assert_equal(
            unsafe_spender.getbalance(),
            expected_unsafe_balance,
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

        receiver_confirmed_entry = self.find_wallet_tx(
            receiver,
            spend_txid,
            "receive",
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
            unsafe_spender,
            unsafe_wallet_name,
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
    AndaluzWalletSendIncludeUnsafeIdentityTest(__file__).main()
