#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify real-mainnet encrypted relay and coexistence with unencrypted v1.

BIP324 does not authenticate operators or replace application chain validation.
The wrong-magic probe checks v1 prefix detection on a v2-capable listener only.
"""

import json
from pathlib import Path
import socket

from test_framework.blocktools import create_coinbase
from test_framework.messages import CBlock, MAGIC_BYTES, NODE_P2P_V2, SEQUENCE_FINAL, uint256_from_compact
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal, p2p_port


GENESIS = "000000f7dca7651a1397fd0bc99b2a456dbb2d23470834b6290aadec4b46d15c"
BITS = 0x1e00ffff
COINBASE_SCRIPT_PUBKEY = "76a914eadbac7f36c37e39361168b7aaee3cb24a25312d88ac"
BITCOIN_MAGIC = b"\xf9\xbe\xb4\xd9"


class AndaluzMainnetV2TransportIdentityTest(BitcoinTestFramework):
    def set_test_params(self):
        self.chain = ""
        self.setup_clean_chain = True
        self.num_nodes = 3
        self.bind_to_localhost_only = True
        self.extra_args = [[
            "-dnsseed=0", "-fixedseeds=0", "-dns=0", "-connect=0",
            "-listen=1", "-maxtipage=315360000",
            f"-v2transport={int(i != 2)}",
        ] for i in range(self.num_nodes)]

    def setup_network(self):
        self.setup_nodes()

    def assert_identity(self, height, tip):
        for node in self.nodes:
            info = node.getblockchaininfo()
            assert_equal(info["chain"], "main")
            assert_equal(info["blocks"], height)
            assert_equal(info["bestblockhash"], tip)
            assert_equal(node.getblockhash(0), GENESIS)
            assert not info["initialblockdownload"]
            subversion = node.getnetworkinfo()["subversion"]
            assert subversion.startswith("/AndaluzcoinCore:"), subversion
            assert "Bitcoin" not in subversion and "Satoshi" not in subversion

    def assert_topology(self):
        for node, count in zip(self.nodes, (1, 2, 1)):
            peers = node.getpeerinfo()
            assert_equal(len(peers), count)
            assert all(p["addr"].startswith("127.0.0.1:") for p in peers)

    def check_link(self, client, server, transport):
        source, destination = self.nodes[client], self.nodes[server]
        target = f"127.0.0.1:{p2p_port(server)}"
        self.wait_until(lambda: any(not p["inbound"] and p["addr"] == target
                                   for p in source.getpeerinfo()), timeout=30)
        outbound, = [p for p in source.getpeerinfo() if not p["inbound"] and p["addr"] == target]
        self.wait_until(lambda: any(p["inbound"] and p["addr"] == outbound["addrbind"]
                                   for p in destination.getpeerinfo()), timeout=30)
        inbound, = [p for p in destination.getpeerinfo()
                    if p["inbound"] and p["addr"] == outbound["addrbind"]]
        assert_equal(inbound["addrbind"], target)
        assert_equal(outbound["connection_type"], "manual")
        assert_equal(inbound["connection_type"], "inbound")
        for peer, remote in ((outbound, destination), (inbound, source)):
            assert_equal(peer["transport_protocol_type"], transport)
            assert peer["version"] > 0
            assert_equal(peer["subver"], remote.getnetworkinfo()["subversion"])
            # connect_nodes waits for these pongs after version/verack completion.
            assert peer["bytesrecv_per_msg"]["pong"] >= 29
            if transport == "v2":
                assert_equal(len(peer["session_id"]), 64)
                assert_equal(bytes.fromhex(peer["session_id"]).hex(), peer["session_id"])
            else:
                assert_equal(peer["session_id"], "")
        assert_equal(outbound["session_id"], inbound["session_id"])
        self.log.info("Link %d->%d: %s session_id=%s", client, server, transport, outbound["session_id"])
        return outbound, inbound

    def run_test(self):
        assert_equal(MAGIC_BYTES[""], b"\xb6\xa9\x64\x58")
        assert_equal(MAGIC_BYTES["mainnet"], MAGIC_BYTES[""])
        assert MAGIC_BYTES[""] != BITCOIN_MAGIC
        self.assert_identity(0, GENESIS)
        for i, node in enumerate(self.nodes):
            assert_equal(node.getpeerinfo(), [])
            network = node.getnetworkinfo()
            assert_equal(bool(int(network["localservices"], 16) & NODE_P2P_V2), i != 2)
            assert_equal("P2P_V2" in network["localservicesnames"], i != 2)

        self.log.info("Establishing real mainnet v2 with no v1 fallback")
        with self.nodes[0].assert_debug_log(
                ["start sending v2 handshake to peer"],
                unexpected_msgs=["retrying with v1 transport protocol for peer"]):
            self.connect_nodes(0, 1, peer_advertises_v2=True)
        original, _ = self.check_link(0, 1, "v2")
        self.assert_identity(0, GENESIS)

        self.log.info("Checking v1-only initiator, then v2-capable initiator using v1")
        self.connect_nodes(2, 1, peer_advertises_v2=False)
        self.check_link(2, 1, "v1")
        self.assert_topology()
        self.disconnect_nodes(2, 1)
        assert_equal(self.nodes[2].getpeerinfo(), [])
        assert_equal(len(self.nodes[1].getpeerinfo()), 1)
        self.connect_nodes(1, 2, peer_advertises_v2=False)
        self.check_link(1, 2, "v1")
        self.assert_topology()
        self.assert_identity(0, GENESIS)

        self.log.info("Relaying only the first fixed mainnet block from node 0")
        with (Path(__file__).resolve().parent / "data/mainnet_alt.json").open(encoding="utf-8") as fixture:
            data = json.load(fixture)
        block = CBlock()
        block.nVersion = 0x20000000
        block.hashPrevBlock = int(GENESIS, 16)
        block.nTime = data["timestamps"][0]
        block.nBits = BITS
        block.nNonce = data["nonces"][0]
        block.vtx = [create_coinbase(height=1, script_pubkey=bytes.fromhex(COINBASE_SCRIPT_PUBKEY), halving_period=210000)]
        block.vtx[0].nLockTime = 0
        block.vtx[0].vin[0].nSequence = SEQUENCE_FINAL
        block.hashMerkleRoot = block.calc_merkle_root()
        assert block.hash_int <= uint256_from_compact(BITS)
        assert_equal(self.nodes[0].submitblock(block.serialize(with_witness=False).hex()), None)
        self.sync_blocks(timeout=60)
        self.assert_identity(1, block.hash_hex)
        for node in self.nodes:
            assert_equal(node.getblockhash(1), block.hash_hex)
            assert_equal(node.getblockheader(block.hash_hex)["bits"], "1e00ffff")
        relayed, _ = self.check_link(0, 1, "v2")
        assert_equal(relayed["session_id"], original["session_id"])
        self.log.info("Fixture relayed through v2 and v1: %s", block.hash_hex)

        self.log.info("Rejecting Bitcoin v1 version prefix on v2-enabled mainnet listener")
        node = self.nodes[0]
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.settimeout(5)
            with node.wait_for_new_peer():
                probe.connect(("127.0.0.1", p2p_port(0)))
            probe_addr = f"127.0.0.1:{probe.getsockname()[1]}"
            self.wait_until(lambda: any(p["addr"] == probe_addr for p in node.getpeerinfo()), timeout=10)
            probe_peer, = [p for p in node.getpeerinfo() if p["addr"] == probe_addr]
            with node.assert_debug_log(
                    ["V2 transport error: V1 peer with wrong MessageStart f9beb4d9"], timeout=10):
                # As in upstream, include bytes beyond the detection prefix so
                # the KEY state processes it even at a socket-read boundary.
                probe.sendall(BITCOIN_MAGIC + b"version\x00\x00\x00\x00\x00" + b"somepayload")
                # Require remote removal before closing our socket.
                self.wait_until(lambda: all(p["id"] != probe_peer["id"]
                                           for p in node.getpeerinfo()), timeout=10)
        self.assert_topology()
        before = self.check_link(0, 1, "v2")
        for n in self.nodes[:2]:
            n.ping()
        for n, peer in zip(self.nodes[:2], before):
            self.wait_until(lambda: any(p["id"] == peer["id"]
                                       and p["bytesrecv_per_msg"].get("pong", 0) > peer["bytesrecv_per_msg"]["pong"]
                                       for p in n.getpeerinfo()), timeout=30)
        healthy, _ = self.check_link(0, 1, "v2")
        assert_equal(healthy["id"], original["id"])
        assert_equal(healthy["session_id"], original["session_id"])
        self.assert_identity(1, block.hash_hex)


if __name__ == "__main__":
    AndaluzMainnetV2TransportIdentityTest(__file__).main()
