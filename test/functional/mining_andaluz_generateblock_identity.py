#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin generateblock mining identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzGenerateBlockMiningIdentityTest(BitcoinTestFramework):
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

    def run_test(self):
        self.log.info("Checking initial Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()
        assert_equal(self.nodes[0].getblockcount(), 0)

        self.log.info("Creating Andaluzcoin mining wallet")
        self.nodes[0].createwallet(wallet_name="miner")
        miner = self.nodes[0].get_wallet_rpc("miner")

        mining_addr = miner.getnewaddress("", "bech32")
        assert_equal(self.nodes[0].validateaddress(mining_addr)["isvalid"], True)

        self.log.info("Mining block with generateblock RPC")
        generate_result = self.nodes[0].generateblock(
            mining_addr,
            [],
            called_by_framework=True,
        )
        assert "hash" in generate_result, generate_result

        block_hash = generate_result["hash"]
        assert_equal(self.nodes[0].getblockcount(), 1)
        assert_equal(self.nodes[0].getbestblockhash(), block_hash)
        assert_equal(self.nodes[0].getblockhash(1), block_hash)

        self.log.info("Checking generated block coinbase identity")
        block = self.nodes[0].getblock(block_hash, 2)
        assert_equal(block["height"], 1)
        assert_equal(block["hash"], block_hash)
        assert_equal(len(block["tx"]), 1)

        coinbase_tx = block["tx"][0]
        assert "coinbase" in coinbase_tx["vin"][0]
        assert_equal(coinbase_tx["vout"][0]["value"], Decimal("50.00000000"))

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzGenerateBlockMiningIdentityTest(__file__).main()
