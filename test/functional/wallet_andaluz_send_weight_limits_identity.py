#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet send transaction-weight limits identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal, assert_raises_rpc_error


class AndaluzWalletSendWeightLimitsIdentityTest(BitcoinTestFramework):
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

    def assert_legacy_wallet_address(self, wallet, address):
        assert_equal(
            self.nodes[0].validateaddress(address)["isvalid"],
            True,
        )

        address_info = wallet.getaddressinfo(address)

        assert_equal(address_info["ismine"], True)
        assert_equal(address_info["solvable"], True)
        assert_equal(address_info["iswitness"], False)

    def run_test(self):
        miner_wallet_name = "andaluz_send_weight_limits_miner"
        source_wallet_name = "andaluz_send_weight_limits_source"
        weight_wallet_name = "andaluz_send_weight_limits_wallet"

        coinbase_amount = Decimal("50.00000000")
        source_coinbase_count = 4
        individual_amount = Decimal("0.10000000")
        output_count = 1472
        oversized_input_count = 1471

        total_funding_amount = (
            individual_amount
            * output_count
        )

        target_amount = (
            individual_amount
            * oversized_input_count
        )

        self.log.info(
            "Checking initial Andaluzcoin runtime identity"
        )
        self.assert_andaluz_runtime_identity()

        self.log.info("Creating Andaluzcoin wallets")

        self.nodes[0].createwallet(
            wallet_name=miner_wallet_name,
        )

        self.nodes[0].createwallet(
            wallet_name=source_wallet_name,
        )

        self.nodes[0].createwallet(
            wallet_name=weight_wallet_name,
        )

        miner = self.nodes[0].get_wallet_rpc(
            miner_wallet_name,
        )

        source = self.nodes[0].get_wallet_rpc(
            source_wallet_name,
        )

        weight_wallet = self.nodes[0].get_wallet_rpc(
            weight_wallet_name,
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
            weight_wallet,
            weight_wallet_name,
        )

        self.log.info(
            "Mining spendable ALUZ for large-output funding transaction"
        )

        source_mining_address = source.getnewaddress(
            "",
            "bech32",
        )

        miner_mining_address = miner.getnewaddress(
            "",
            "bech32",
        )

        source_blocks = self.nodes[0].generatetoaddress(
            source_coinbase_count,
            source_mining_address,
            called_by_framework=True,
        )

        assert_equal(
            len(source_blocks),
            source_coinbase_count,
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

        self.nodes[0].syncwithvalidationinterfacequeue()

        expected_source_balance = (
            coinbase_amount
            * source_coinbase_count
        )

        assert_equal(
            source.getbalances()["mine"]["trusted"],
            expected_source_balance,
        )

        self.log.info(
            "Creating 1472 legacy Andaluzcoin destinations"
        )

        legacy_addresses = [
            weight_wallet.getnewaddress(
                "",
                "legacy",
            )
            for _ in range(output_count)
        ]

        assert_equal(
            len(legacy_addresses),
            output_count,
        )

        self.assert_legacy_wallet_address(
            weight_wallet,
            legacy_addresses[0],
        )

        self.assert_legacy_wallet_address(
            weight_wallet,
            legacy_addresses[-1],
        )

        funding_outputs = [
            {
                address: individual_amount,
            }
            for address in legacy_addresses
        ]

        self.log.info(
            "Funding 1472 independent 0.1 ALUZ legacy outputs"
        )

        funding_result = source.send(
            outputs=funding_outputs,
        )

        assert_equal(
            funding_result["complete"],
            True,
        )

        assert "txid" in funding_result, funding_result

        funding_txid = funding_result["txid"]

        assert_equal(
            len(funding_txid),
            64,
        )

        assert funding_txid in self.nodes[0].getrawmempool(), (
            self.nodes[0].getrawmempool()
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

        self.log.info(
            "Checking 1472 spendable weight-limit UTXOs"
        )

        inputs = weight_wallet.listunspent()

        assert_equal(
            len(inputs),
            output_count,
        )

        for utxo in inputs:
            assert_equal(
                utxo["amount"],
                individual_amount,
            )

            assert_equal(
                utxo["confirmations"],
                1,
            )

        assert_equal(
            weight_wallet.getbalance(),
            total_funding_amount,
        )

        mempool_before = set(
            self.nodes[0].getrawmempool()
        )

        assert_equal(
            mempool_before,
            set(),
        )

        self.log.info(
            "Checking fully preset oversized send is rejected"
        )

        preset_destination = weight_wallet.getnewaddress(
            "andaluz-weight-preset",
            "bech32",
        )

        assert_raises_rpc_error(
            -4,
            "Transaction too large",
            weight_wallet.send,
            outputs=[
                {
                    preset_destination: target_amount,
                }
            ],
            options={
                "inputs": inputs,
                "add_inputs": False,
            },
        )

        self.log.info(
            "Checking automatic input selection weight limit"
        )

        automatic_destination = weight_wallet.getnewaddress(
            "andaluz-weight-automatic",
            "bech32",
        )

        assert_raises_rpc_error(
            -4,
            (
                "The inputs size exceeds the maximum weight. "
                "Please try sending a smaller amount or manually "
                "consolidating your wallet's UTXOs"
            ),
            weight_wallet.send,
            outputs=[
                {
                    automatic_destination: target_amount,
                }
            ],
        )

        self.log.info(
            "Checking preset plus automatic input selection weight limit"
        )

        partial_inputs = inputs[:1000]

        assert_equal(
            len(partial_inputs),
            1000,
        )

        mixed_destination = weight_wallet.getnewaddress(
            "andaluz-weight-mixed",
            "bech32",
        )

        assert_raises_rpc_error(
            -4,
            (
                "The combination of the pre-selected inputs and the "
                "wallet automatic inputs selection exceeds the transaction "
                "maximum weight. Please try sending a smaller amount or "
                "manually consolidating your wallet's UTXOs"
            ),
            weight_wallet.send,
            outputs=[
                {
                    mixed_destination: target_amount,
                }
            ],
            options={
                "inputs": partial_inputs,
                "add_inputs": True,
            },
        )

        self.log.info(
            "Checking rejected oversized sends changed no state"
        )

        assert_equal(
            set(self.nodes[0].getrawmempool()),
            mempool_before,
        )

        assert_equal(
            weight_wallet.getbalance(),
            total_funding_amount,
        )

        remaining_utxos = weight_wallet.listunspent()

        assert_equal(
            len(remaining_utxos),
            output_count,
        )

        assert_equal(
            weight_wallet.listlockunspent(),
            [],
        )

        remaining_outpoints = {
            (
                utxo["txid"],
                utxo["vout"],
            )
            for utxo in remaining_utxos
        }

        original_outpoints = {
            (
                utxo["txid"],
                utxo["vout"],
            )
            for utxo in inputs
        }

        assert_equal(
            remaining_outpoints,
            original_outpoints,
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
            weight_wallet,
            weight_wallet_name,
        )

        self.log.info(
            "Checking final Andaluzcoin runtime identity"
        )

        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletSendWeightLimitsIdentityTest(__file__).main()
