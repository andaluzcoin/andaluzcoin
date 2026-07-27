#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin mined block subsidy identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzMinedBlockSubsidyIdentityTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True
        self.chain = "regtest"
        self.extra_args = [[
            "-dnsseed=0",
            "-fixedseeds=0",
            "-connect=0",
        ]]

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

        self.log.info("Mining first Andaluzcoin block")
        mining_addr = self.nodes[0].get_deterministic_priv_key().address
        mined_blocks = self.nodes[0].generatetoaddress(
            1,
            mining_addr,
            called_by_framework=True,
        )
        assert_equal(len(mined_blocks), 1)

        block_hash = mined_blocks[0]
        assert_equal(self.nodes[0].getblockcount(), 1)
        assert_equal(self.nodes[0].getbestblockhash(), block_hash)

        self.log.info("Checking mined block coinbase subsidy")
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
    AndaluzMinedBlockSubsidyIdentityTest(__file__).main()
