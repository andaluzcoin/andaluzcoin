#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Recover two precomputed mainnet blocks through catch-up, restart and reindex."""

import json
from pathlib import Path

from test_framework.blocktools import create_coinbase
from test_framework.messages import CBlock, CBlockHeader, SEQUENCE_FINAL, uint256_from_compact
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal, assert_raises_rpc_error


GENESIS = "000000f7dca7651a1397fd0bc99b2a456dbb2d23470834b6290aadec4b46d15c"
BITS = 0x1e00ffff
COINBASE_SCRIPT_PUBKEY = "76a914eadbac7f36c37e39361168b7aaee3cb24a25312d88ac"


class AndaluzMainnetChainRecoveryTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 2
        self.setup_clean_chain = True
        self.chain = ""
        self.bind_to_localhost_only = True
        # The framework writes bind=127.0.0.1 to each ephemeral config.
        # Historical fixture tips must leave IBD to relay on every restart.
        self.extra_args = [[
            "-dnsseed=0", "-fixedseeds=0", "-connect=0",
            "-listen=1", "-maxtipage=315360000",
        ] for _ in range(self.num_nodes)]

    def assert_identity(self, node, height):
        info = node.getblockchaininfo()
        assert_equal(info["chain"], "main")
        assert_equal(info["blocks"], height)
        assert_equal(info["headers"], height)
        assert_equal(info["bestblockhash"], self.hashes[height])
        assert_equal(info["initialblockdownload"], False)
        # Genesis and both fixture blocks use the same compact target.
        work = (1 << 256) // (uint256_from_compact(BITS) + 1)
        assert_equal(int(info["chainwork"], 16), (height + 1) * work)
        for block_height in range(height + 1):
            block_hash = self.hashes[block_height]
            assert_equal(node.getblockhash(block_height), block_hash)
            header = node.getblockheader(block_hash)
            assert_equal(header["bits"], "1e00ffff")
            assert_equal(int(header["chainwork"], 16), (block_height + 1) * work)
            if block_height:
                assert_equal(node.getblockheader(block_hash, False), self.headers[block_height])
        subversion = node.getnetworkinfo()["subversion"]
        assert subversion.startswith("/AndaluzcoinCore:"), subversion
        assert "Satoshi" not in subversion, subversion
        assert "Bitcoin" not in subversion, subversion

    def assert_local_peers(self, count):
        for node in self.nodes:
            peers = node.getpeerinfo()
            assert_equal(len(peers), count)
            for peer in peers:
                assert peer["addr"].startswith("127.0.0.1:"), peer
                assert peer["version"] > 0, peer
                assert peer["subver"].startswith("/AndaluzcoinCore:"), peer

    def connect_and_check(self):
        self.connect_nodes(1, 0)
        self.sync_blocks()
        self.assert_local_peers(1)
        for node in self.nodes:
            self.assert_identity(node, 2)

    def run_test(self):
        with (Path(__file__).resolve().parent / "data/mainnet_alt.json").open(encoding="utf-8") as fixture:
            data = json.load(fixture)
        self.hashes = [GENESIS]
        self.headers = {}
        blocks = []
        for height in (1, 2):
            block = CBlock()
            block.nVersion = 0x20000000
            block.hashPrevBlock = int(self.hashes[-1], 16)
            block.nTime = data["timestamps"][height - 1]
            block.nBits = BITS
            block.nNonce = data["nonces"][height - 1]
            block.vtx = [create_coinbase(height=height, script_pubkey=bytes.fromhex(COINBASE_SCRIPT_PUBKEY), halving_period=210000)]
            block.vtx[0].nLockTime = 0
            block.vtx[0].vin[0].nSequence = SEQUENCE_FINAL
            block.hashMerkleRoot = block.calc_merkle_root()
            # Check existing work independently; never search for a nonce.
            assert block.hash_int <= uint256_from_compact(BITS)
            self.hashes.append(block.hash_hex)
            self.headers[height] = CBlockHeader(block).serialize().hex()
            blocks.append(block)

        self.log.info("Checking connected mainnet genesis and runtime identity")
        self.assert_local_peers(1)
        for node in self.nodes:
            self.assert_identity(node, 0)

        self.log.info("Submitting fixture block 1 and checking P2P synchronization")
        assert_equal(self.nodes[0].submitblock(blocks[0].serialize(with_witness=False).hex()), None)
        self.sync_blocks()
        for node in self.nodes:
            self.assert_identity(node, 1)
        block_one_info = self.nodes[1].getblockchaininfo()
        block_one_header = self.nodes[1].getblockheader(self.hashes[1], False)

        self.log.info("Stopping node 1; advancing only node 0 with fixture block 2")
        self.stop_node(1)
        assert self.nodes[1].is_node_stopped()
        self.wait_until(lambda: self.nodes[0].getconnectioncount() == 0)
        assert_equal(self.nodes[0].submitblock(blocks[1].serialize(with_witness=False).hex()), None)
        self.assert_identity(self.nodes[0], 2)
        assert self.nodes[1].is_node_stopped()

        self.log.info("Restarting node 1 and checking persisted block 1 before reconnecting")
        # None reuses the node's original args and original ephemeral datadir.
        self.start_node(1)
        self.assert_local_peers(0)
        self.assert_identity(self.nodes[1], 1)
        info = self.nodes[1].getblockchaininfo()
        for key in ("chain", "blocks", "bestblockhash", "chainwork"):
            assert_equal(info[key], block_one_info[key])
        assert_equal(self.nodes[1].getblockheader(self.hashes[1], False), block_one_header)
        assert_raises_rpc_error(-5, "Block not found", self.nodes[1].getblockheader, self.hashes[2])

        self.log.info("Explicitly reconnecting for real P2P catch-up to block 2")
        self.connect_and_check()

        self.log.info("Gracefully restarting both nodes without reindex; checking disk persistence")
        self.stop_nodes()
        self.start_nodes()
        self.assert_local_peers(0)
        for node in self.nodes:
            self.assert_identity(node, 2)
        self.connect_and_check()

        for flag in ("-reindex-chainstate", "-reindex"):
            self.log.info("Recovering node 1 with %s before reconnecting", flag)
            # Explicit restart args replace defaults, so include isolation and
            # maxtipage every time. Do not persist reindex in self.extra_args.
            self.restart_node(1, extra_args=self.extra_args[1] + [flag])
            self.wait_until(lambda: self.nodes[0].getconnectioncount() == 0)
            self.assert_local_peers(0)
            # start_node waits for import/reindex completion via mempool.loaded.
            self.assert_identity(self.nodes[1], 2)
            self.assert_identity(self.nodes[0], 2)
            self.connect_and_check()


if __name__ == "__main__":
    AndaluzMainnetChainRecoveryTest(__file__).main()
