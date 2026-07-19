#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin mainnet node-to-node connectivity identity."""

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzConnectivityTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 2
        self.setup_clean_chain = True
        self.chain = ""
        self.extra_args = [
            [
                "-dnsseed=0",
                "-fixedseeds=0",
                "-listen=1",
            ],
            [
                "-dnsseed=0",
                "-fixedseeds=0",
                "-listen=1",
            ],
        ]

    def run_test(self):
        expected_genesis_hash = "000000f7dca7651a1397fd0bc99b2a456dbb2d23470834b6290aadec4b46d15c"

        self.log.info("Checking both nodes start as Andaluzcoin mainnet")
        for node in self.nodes:
            blockchain_info = node.getblockchaininfo()
            assert_equal(blockchain_info["chain"], "main")
            assert_equal(blockchain_info["bestblockhash"], expected_genesis_hash)
            assert_equal(node.getblockhash(0), expected_genesis_hash)

            network_info = node.getnetworkinfo()
            assert network_info["subversion"].startswith("/AndaluzcoinCore:"), network_info["subversion"]
            assert "Satoshi" not in network_info["subversion"], network_info["subversion"]
            assert "Bitcoin" not in network_info["subversion"], network_info["subversion"]

        self.log.info("Connecting Andaluzcoin nodes")
        self.connect_nodes(0, 1)

        self.wait_until(lambda: self.nodes[0].getconnectioncount() >= 1, timeout=30)
        self.wait_until(lambda: self.nodes[1].getconnectioncount() >= 1, timeout=30)
        self.wait_until(lambda: len(self.nodes[0].getpeerinfo()) >= 1, timeout=30)
        self.wait_until(lambda: len(self.nodes[1].getpeerinfo()) >= 1, timeout=30)

        self.log.info("Checking peer identity after node-to-node connection")
        for node in self.nodes:
            peer_info = node.getpeerinfo()
            assert len(peer_info) >= 1, peer_info

            andaluz_peers = [
                peer for peer in peer_info
                if peer["subver"].startswith("/AndaluzcoinCore:")
            ]
            assert len(andaluz_peers) >= 1, peer_info

            for peer in peer_info:
                subversion = peer["subver"]
                assert "Satoshi" not in subversion, subversion
                assert "Bitcoin" not in subversion, subversion

            assert_equal(node.getblockchaininfo()["chain"], "main")
            assert_equal(node.getblockhash(0), expected_genesis_hash)


if __name__ == "__main__":
    AndaluzConnectivityTest(__file__).main()
