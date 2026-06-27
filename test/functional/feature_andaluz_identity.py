#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin post-v31 runtime identity."""

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzIdentityTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True
        self.chain = ""
        self.extra_args = [[
            "-dnsseed=0",
            "-fixedseeds=0",
            "-connect=0",
        ]]

    def run_test(self):
        self.log.info("Checking Andaluzcoin mainnet genesis hash")
        assert_equal(
            self.nodes[0].getblockhash(0),
            "000000f7dca7651a1397fd0bc99b2a456dbb2d23470834b6290aadec4b46d15c",
        )

        self.log.info("Checking Andaluzcoin P2P runtime subversion")
        subversion = self.nodes[0].getnetworkinfo()["subversion"]
        assert subversion.startswith("/AndaluzcoinCore:"), subversion
        assert "Satoshi" not in subversion, subversion
        assert "Bitcoin" not in subversion, subversion

        self.log.info("Checking chain identity")
        assert_equal(self.nodes[0].getblockchaininfo()["chain"], "main")


if __name__ == "__main__":
    AndaluzIdentityTest(__file__).main()
