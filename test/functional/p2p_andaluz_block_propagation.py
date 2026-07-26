#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin block propagation identity."""

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzBlockPropagationTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 2
        self.setup_clean_chain = True
        self.chain = "regtest"
        self.extra_args = [
            [
                "-listen=1",
            ],
            [
                "-listen=1",
            ],
        ]

    def assert_andaluz_runtime_identity(self, node):
        assert_equal(node.getblockchaininfo()["chain"], "regtest")

        subversion = node.getnetworkinfo()["subversion"]
        assert subversion.startswith("/AndaluzcoinCore:"), subversion
        assert "Satoshi" not in subversion, subversion
        assert "Bitcoin" not in subversion, subversion

    def run_test(self):
        self.log.info("Checking initial Andaluzcoin runtime identity")
        for node in self.nodes:
            self.assert_andaluz_runtime_identity(node)
            assert_equal(node.getblockcount(), 0)

        self.log.info("Connecting Andaluzcoin nodes")
        self.connect_nodes(0, 1)
        self.wait_until(lambda: self.nodes[0].getconnectioncount() >= 1, timeout=30)
        self.wait_until(lambda: self.nodes[1].getconnectioncount() >= 1, timeout=30)

        self.log.info("Mining block on node 0")
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

        self.log.info("Waiting for block propagation to node 1")
        self.sync_blocks()

        assert_equal(self.nodes[1].getblockcount(), 1)
        assert_equal(self.nodes[1].getbestblockhash(), block_hash)
        assert_equal(self.nodes[1].getblockhash(1), block_hash)

        block = self.nodes[1].getblock(block_hash)
        assert_equal(block["height"], 1)
        assert_equal(block["hash"], block_hash)

        self.log.info("Checking final Andaluzcoin runtime identity")
        for node in self.nodes:
            self.assert_andaluz_runtime_identity(node)


if __name__ == "__main__":
    AndaluzBlockPropagationTest(__file__).main()
