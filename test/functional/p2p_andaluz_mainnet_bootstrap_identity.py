#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Exercise local manual mainnet bootstrap, launch configuration and recovery."""

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal, p2p_port


GENESIS = "000000f7dca7651a1397fd0bc99b2a456dbb2d23470834b6290aadec4b46d15c"


class AndaluzMainnetBootstrapTest(BitcoinTestFramework):
    def set_test_params(self):
        self.chain = ""
        self.setup_clean_chain = True
        self.num_nodes = 3
        self.bind_to_localhost_only = True
        # Framework connect=0 disables addrman outgoing, not the addnode worker.
        # Leave transport defaults unchanged; dedicated v2 identity is separate.
        self.extra_args = [["-dnsseed=0", "-fixedseeds=0", "-dns=0", "-listen=1"]
                           for _ in range(self.num_nodes)]

    def setup_network(self):
        self.setup_nodes()

    def assert_identity(self, indices=(0, 1, 2)):
        for i in indices:
            node = self.nodes[i]
            info = node.getblockchaininfo()
            assert_equal(info["chain"], "main")
            assert_equal(info["blocks"], 0)
            assert_equal(info["headers"], 0)
            assert_equal(info["bestblockhash"], GENESIS)
            assert_equal(node.getblockhash(0), GENESIS)
            network = node.getnetworkinfo()
            assert network["networkactive"]
            assert network["version"] > 0
            assert network["subversion"].startswith("/AndaluzcoinCore:"), network
            for peer in node.getpeerinfo():
                assert peer["addr"].startswith("127.0.0.1:"), peer

    def target(self, index):
        return f"127.0.0.1:{p2p_port(index)}"

    def check_link(self, client, server):
        source, destination = self.nodes[client], self.nodes[server]

        def ready(require_pong=False):
            for outbound in source.getpeerinfo():
                if outbound["inbound"] or outbound["addr"] != self.target(server):
                    continue
                for inbound in destination.getpeerinfo():
                    if (inbound["inbound"] and inbound["addr"] == outbound.get("addrbind")
                            and inbound.get("addrbind") == self.target(server)):
                        return all(p["version"] > 0
                                   and p["subver"].startswith("/AndaluzcoinCore:")
                                   and (not require_pong or "pingtime" in p)
                                   for p in (outbound, inbound))
            return False

        # pingtime demonstrates a post-handshake ping/pong on both ends.
        self.wait_until(ready, timeout=90)
        source.ping()
        destination.ping()
        self.wait_until(lambda: ready(require_pong=True), timeout=30)
        outbound = next(p for p in source.getpeerinfo()
                        if not p["inbound"] and p["addr"] == self.target(server))
        assert_equal(outbound["connection_type"], "manual")
        added = source.getaddednodeinfo(self.target(server))
        assert_equal(len(added), 1)
        assert_equal(added[0]["connected"], True)
        assert {"address": self.target(server), "connected": "outbound"} in added[0]["addresses"]

    def run_test(self):
        self.log.info("Checking three isolated fresh mainnet nodes")
        self.assert_identity()
        for node in self.nodes:
            assert_equal(node.getconnectioncount(), 0)
            assert_equal(node.getaddednodeinfo(), [])

        self.log.info("Node 1 joins known bootstrap node 0 using runtime addnode")
        self.nodes[1].addnode(self.target(0), "add")
        self.check_link(1, 0)
        self.assert_identity()

        self.log.info("Node 2 independently specifies node 1 as its manual peer")
        self.nodes[2].addnode(self.target(1), "add")
        self.check_link(2, 1)
        self.assert_identity()

        self.log.info("Restarting node 2 proves runtime addnode is volatile")
        self.restart_node(2)
        assert_equal(self.nodes[2].getaddednodeinfo(), [])
        assert_equal(self.nodes[2].getconnectioncount(), 0)
        self.assert_identity()

        self.log.info("Starting node 1 with explicit launch addnode configuration")
        # Save the operator-equivalent argument in the original launch args so
        # start_node(None) reapplies it, rather than relying on volatile RPC state.
        self.nodes[1].extra_args = self.extra_args[1] + [f"-addnode={self.target(0)}"]
        self.restart_node(1)
        self.check_link(1, 0)
        self.assert_identity()

        self.log.info("Full client restart reapplies the same configured bootstrap peer")
        self.restart_node(1)
        self.check_link(1, 0)
        self.nodes[2].addnode(self.target(1), "add")
        self.check_link(2, 1)
        self.assert_identity()

        self.log.info("Stopping bootstrap node 0; other nodes remain available")
        self.stop_node(0)
        self.wait_until(lambda: not any(p["addr"] == self.target(0)
                                       for p in self.nodes[1].getpeerinfo()), timeout=30)
        assert_equal(self.nodes[1].getaddednodeinfo(self.target(0))[0]["connected"], False)
        self.check_link(2, 1)
        self.assert_identity((1, 2))

        self.log.info("Restarting bootstrap; waiting for bounded automatic addnode recovery")
        # The worker may wait 60 seconds after a failed attempt. No mocktime,
        # onetry or framework connect_nodes shortcut supplies this reconnection.
        self.start_node(0)
        self.check_link(1, 0)
        self.check_link(2, 1)
        self.assert_identity()


if __name__ == "__main__":
    AndaluzMainnetBootstrapTest(__file__).main()
