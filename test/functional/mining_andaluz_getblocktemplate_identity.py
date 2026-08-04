#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin getblocktemplate mining identity."""

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzGetBlockTemplateMiningIdentityTest(BitcoinTestFramework):
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

    def assert_template_identity(self, template, expected_height, expected_previous_hash):
        assert_equal(template["height"], expected_height)
        assert_equal(template["previousblockhash"], expected_previous_hash)

        assert "bits" in template, template
        assert "target" in template, template
        assert "transactions" in template, template
        assert "coinbasevalue" in template, template

        assert isinstance(template["bits"], str), template
        assert isinstance(template["target"], str), template
        assert len(template["bits"]) > 0, template
        assert len(template["target"]) > 0, template

    def run_test(self):
        self.log.info("Checking initial Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()
        assert_equal(self.nodes[0].getblockcount(), 0)

        genesis_hash = self.nodes[0].getblockhash(0)

        self.log.info("Checking initial Andaluzcoin getblocktemplate identity")
        template = self.nodes[0].getblocktemplate({"rules": ["segwit"]})
        self.assert_template_identity(
            template,
            expected_height=1,
            expected_previous_hash=genesis_hash,
        )

        self.log.info("Mining block from current template chain state")
        mining_addr = self.nodes[0].get_deterministic_priv_key().address
        mined_blocks = self.nodes[0].generatetoaddress(
            1,
            mining_addr,
            called_by_framework=True,
        )
        assert_equal(len(mined_blocks), 1)

        mined_block_hash = mined_blocks[0]
        assert_equal(self.nodes[0].getblockcount(), 1)
        assert_equal(self.nodes[0].getbestblockhash(), mined_block_hash)

        self.log.info("Checking next Andaluzcoin getblocktemplate advances")
        next_template = self.nodes[0].getblocktemplate({"rules": ["segwit"]})
        self.assert_template_identity(
            next_template,
            expected_height=2,
            expected_previous_hash=mined_block_hash,
        )

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzGetBlockTemplateMiningIdentityTest(__file__).main()
