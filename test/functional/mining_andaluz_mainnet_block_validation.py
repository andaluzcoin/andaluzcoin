#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Validate two precomputed mainnet blocks, rejection paths, and runtime identity."""

from copy import deepcopy
import json
from pathlib import Path

from test_framework.blocktools import create_coinbase
from test_framework.messages import CBlock, SEQUENCE_FINAL, uint256_from_compact
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


GENESIS = "000000f7dca7651a1397fd0bc99b2a456dbb2d23470834b6290aadec4b46d15c"
BITS = 0x1e00ffff
COINBASE_SCRIPT_PUBKEY = "76a914eadbac7f36c37e39361168b7aaee3cb24a25312d88ac"


class AndaluzMainnetBlockValidationTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 2
        self.setup_clean_chain = True
        self.chain = ""
        # Historical fixture tips must leave IBD so the nodes announce blocks.
        # This override applies only to these test nodes.
        self.extra_args = [["-dnsseed=0", "-fixedseeds=0", "-connect=0", "-maxtipage=315360000"] for _ in range(self.num_nodes)]

    def assert_chain_identity(self, height, tip):
        for node in self.nodes:
            info = node.getblockchaininfo()
            assert_equal(info["chain"], "main")
            assert_equal(info["blocks"], height)
            assert_equal(info["bestblockhash"], tip)
            assert_equal(node.getblockhash(0), GENESIS)
            subversion = node.getnetworkinfo()["subversion"]
            assert subversion.startswith("/AndaluzcoinCore:"), subversion
            assert "Satoshi" not in subversion, subversion
            assert "Bitcoin" not in subversion, subversion

    def assert_proposal(self, block, expected, height, tip):
        assert_equal(self.nodes[0].getblocktemplate({
            "mode": "proposal", "rules": ["segwit"],
            "data": block.serialize(with_witness=False).hex(),
        }), expected)
        self.assert_chain_identity(height, tip)

    def run_test(self):
        with (Path(__file__).resolve().parent / "data/mainnet_alt.json").open(encoding="utf-8") as fixture:
            blocks = json.load(fixture)

        self.assert_chain_identity(0, GENESIS)
        for node in self.nodes:
            peers = node.getpeerinfo()
            assert_equal(len(peers), 1)
            assert peers[0]["version"] > 0
            assert not node.getblockchaininfo()["initialblockdownload"]
        self.log.info("Both mainnet nodes are connected and outside initial block download")
        tip = GENESIS
        for height in (1, 2):
            self.log.info("Checking precomputed mainnet block %d", height)
            block = CBlock()
            block.nVersion = 0x20000000
            block.hashPrevBlock = int(tip, 16)
            block.nTime = blocks["timestamps"][height - 1]
            block.nBits = BITS
            block.nNonce = blocks["nonces"][height - 1]
            block.vtx = [create_coinbase(height=height, script_pubkey=bytes.fromhex(COINBASE_SCRIPT_PUBKEY), halving_period=210000)]
            block.vtx[0].nLockTime = 0
            block.vtx[0].vin[0].nSequence = SEQUENCE_FINAL
            block.hashMerkleRoot = block.calc_merkle_root()
            # Independently check the fixture's PoW; never solve a mainnet block.
            assert block.hash_int <= uint256_from_compact(BITS)
            self.assert_proposal(block, None, height - 1, tip)

            bad_bits = deepcopy(block)
            bad_bits.nBits = 0x1d00ffff
            self.assert_proposal(bad_bits, "bad-diffbits", height - 1, tip)

            bad_amount = deepcopy(block)
            bad_amount.vtx[0].vout[0].nValue += 1
            bad_amount.hashMerkleRoot = bad_amount.calc_merkle_root()
            self.assert_proposal(bad_amount, "bad-cb-amount", height - 1, tip)

            bad_height = deepcopy(block)
            bad_height.vtx[0].vin[0].scriptSig = create_coinbase(height=height + 1).vin[0].scriptSig
            bad_height.hashMerkleRoot = bad_height.calc_merkle_root()
            self.assert_proposal(bad_height, "bad-cb-height", height - 1, tip)

            bad_merkle = deepcopy(block)
            bad_merkle.hashMerkleRoot ^= 1
            self.assert_proposal(bad_merkle, "bad-txnmrklroot", height - 1, tip)

            insufficient_pow = deepcopy(block)
            insufficient_pow.nNonce = (block.nNonce + 1) & 0xffffffff
            while insufficient_pow.hash_int <= uint256_from_compact(BITS):
                insufficient_pow.nNonce = (insufficient_pow.nNonce + 1) & 0xffffffff
            assert insufficient_pow.hash_hex != block.hash_hex
            assert_equal(self.nodes[0].submitblock(insufficient_pow.serialize(with_witness=False).hex()), "high-hash")
            self.assert_chain_identity(height - 1, tip)

            # Only submit the intact fixture block with this header hash.
            assert_equal(self.nodes[0].submitblock(block.serialize(with_witness=False).hex()), None)
            self.sync_blocks()
            tip = block.hash_hex
            self.assert_chain_identity(height, tip)
            for node in self.nodes:
                assert not node.getblockchaininfo()["initialblockdownload"]
                assert_equal(node.getblockhash(height), tip)
                assert_equal(node.getblock(tip)["bits"], "1e00ffff")
            self.log.info("Block %d propagated to node 1: %s", height, tip)


if __name__ == "__main__":
    AndaluzMainnetBlockValidationTest(__file__).main()
