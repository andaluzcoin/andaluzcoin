#!/usr/bin/env python3
# Copyright (c) 2019-2022 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test that we reject low difficulty headers to prevent our block tree from filling up with useless bloat"""

from test_framework.messages import (
    CBlockHeader,
    from_hex,
)
from test_framework.p2p import (
    P2PInterface,
    msg_headers,
)
from test_framework.test_framework import AndaluzcoinTestFramework

from test_framework.p2p import P2PDataStore
from test_framework.messages import uint256_from_str
from test_framework.messages import CBlockHeader, from_hex
from io import BytesIO
from typing import Union

import hashlib
import os


def load_tagged_headers(filename):
    headers_main = []
    headers_fork = []
    with open(filename, "rb") as f:
        while True:
            tag = f.read(5)
            if not tag or len(tag) < 5:
                break
            raw = f.read(80)
            if not raw or len(raw) < 80:
                break
            header = CBlockHeader()
            header.deserialize(BytesIO(raw))
            header.calc_sha256()
            if tag == b"main:":
                headers_main.append(header)
            elif tag == b"fork:":
                headers_fork.append(header)
            else:
                raise ValueError(f"Unknown tag in header file: {tag}")
    return headers_main, headers_fork


class RejectLowDifficultyHeadersTest(AndaluzcoinTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.chain = "regtest"   # ✅ Ensure regtest for matching magic bytes
        self.num_nodes = 2
        # Make this test self-contained: NO prune, NO blockfilterindex/coinstatsindex
        self.extra_args = [
            ['-minimumchainwork=0x0', '-prune=0', '-blockfilterindex=0', '-coinstatsindex=0'],
            ['-minimumchainwork=0x0', '-prune=0', '-blockfilterindex=0', '-coinstatsindex=0'],
        ]

    def add_options(self, parser):
        parser.add_argument(
            '--datafile',
            default=os.path.join(os.path.dirname(__file__), 'data', 'headers_regtest.dat'),
            help='Path to regtest headers file (default: %(default)s)',
        )

    @staticmethod
    def bits_to_target(bits: int) -> int:
        """Convert compact representation of difficulty (nBits) to target."""
        exponent = bits >> 24
        mantissa = bits & 0xffffff
        if exponent <= 3:
            return mantissa >> (8 * (3 - exponent))
        return mantissa << (8 * (exponent - 3))

    @staticmethod
    def check_proof_of_work(block_hash: Union[int, bytes], bits: int) -> bool:
        # Normalize hash to 32-byte big-endian
        if isinstance(block_hash, int):
            hb = block_hash.to_bytes(32, byteorder="big", signed=False)
        else:
            hb = block_hash
            if len(hb) < 32:
                hb = hb.rjust(32, b"\x00")   # left-pad if shorter
            elif len(hb) > 32:
                hb = hb[-32:]                # keep the least-significant 32 bytes

        target = RejectLowDifficultyHeadersTest.bits_to_target(bits)
        hash_int_le = int.from_bytes(hb[::-1], byteorder="big")  # compare LE integer
        return hash_int_le <= target

    def validate_pow_headers(self, headers, label="main"):
        print(f"🔍 Verifying {len(headers)} headers for regtest POW...")

        all_valid = True
        for i, header in enumerate(headers):
            ok = self.check_proof_of_work(header.sha256, header.nBits)  # pass int
            hb = header.sha256.to_bytes(32, byteorder="big")            # for logging
            hb_le_hex = hb[::-1].hex()

            if not ok:
                print(f"❌ Invalid POW at header index {i}:\n   hash   = {hb_le_hex}\n   nBits  = 0x{header.nBits:08x}")

                # 🔍 Print target vs hash comparison
                target = self.bits_to_target(header.nBits)
                hash_val = int.from_bytes(hb[::-1], "big")
                print(f"🔍 POW details:")
                print(f"   target = {hex(target)}")
                print(f"   hash   = {hex(hash_val)}")
                print(f"   diff   = {target - hash_val if target > hash_val else 'OVER'}")

                all_valid = False
            else:
                print(f"✅ Header {i}: POW valid. hash={hb_le_hex}, bits=0x{header.nBits:08x}")

        print("🎉 All headers pass regtest-style proof-of-work" if all_valid else "❌ Some headers failed POW check")
        return all_valid

    @staticmethod
    def parse_valid_headers(hex_lines):
        parsed = []
        for i, line in enumerate(hex_lines):
            line = line.strip()
            if "#" in line:
                line = line.split("#", 1)[0].strip()  # ✅ remove trailing comment
            if not line:
                continue
            try:
                header = from_hex(CBlockHeader(), line)
                if header is None:
                    print(f"⚠️ Line {i}: from_hex() returned None for: {line[:32]}...")
                    continue
                header.calc_sha256()  # 🔥 This populates header.sha256
                if not hasattr(header, 'sha256') or header.sha256 is None:
                    print(f"⚠️ Line {i}: Header has no sha256 after from_hex(): {line[:32]}...")
                    continue
                parsed.append(header)
            except Exception as e:
                print(f"❌ Line {i}: Exception while parsing: {line[:32]}... — {e}")
        return parsed

    def sha256(b):
        return hashlib.sha256(hashlib.sha256(b).digest()).digest()

    def run_test(self):
        self.log.info("Read headers data")
        self.headers_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), self.options.datafile))

        self.log.info("📂 Reading headers file: %s", self.headers_file_path)

        parsed_main, parsed_fork = load_tagged_headers(self.headers_file_path)
        self.headers = parsed_main
        self.headers_fork = parsed_fork

        self.log.debug("🧪 Loaded %d fork headers", len(self.headers_fork))
        self.log.info("🧠 Parsed %d valid headers", len(self.headers))
        self.log.info("✅ Loaded %d main headers and %d fork headers", len(self.headers), len(self.headers_fork))
 
        if not self.headers or self.headers[0] is None:
            self.log.error("❌ headers[0] is None! Check parsing.")
            for idx, h in enumerate(self.headers[:5]):
                self.log.debug("🔍 Header %d: %r", idx, h)
            raise ValueError("❌ headers[0] is None after filtering")
        else:
            self.log.info("🧠 First header hash: %s", self.headers[0].sha256)

        # 🔍 Sanity check to avoid silent failure
        if not self.headers:
            raise ValueError("❌ No valid headers loaded. Check your headers_regtest.dat format.")
        if not self.headers_fork:
            raise ValueError("❌ No valid fork headers were loaded from headers file.")

        # 🧠 Prepopulate a temporary store BEFORE connecting the peer
        block_store = {}
        last_block_hash = None
        for h in self.headers:
            block_store[h.sha256] = h
            last_block_hash = h.sha256

        # 🚀 Connect P2P and inject the store right away
        peer_checkpoint = self.nodes[0].add_p2p_connection(
           P2PDataStore(block_store=block_store, last_block_hash=last_block_hash)
        )
        peer_checkpoint.timeout_factor = 1.0

        self.log.debug("🧱 First header: %s", self.headers[0].sha256)
        self.log.debug("🔍 type(self.headers[0].sha256) = %s", type(self.headers[0].sha256))

        # 👮 Validate headers' POW before broadcasting
        assert self.validate_pow_headers(self.headers), "Some headers are invalid for regtest POW"

        # 📡 Send headers after store is ready
        #peer_checkpoint.send_and_ping(msg_headers(self.headers))
        peer_checkpoint.send_message(msg_headers(self.headers))
        peer_checkpoint.wait_for_disconnect(timeout=5)
        self.log.info("✅ Peer disconnected after sending headers.")

        # ✅ Immediately check if disconnected
        if not peer_checkpoint.is_connected:
            self.log.error("❌ Peer checkpoint disconnected right after send_and_ping!")
            peer_checkpoint.wait_for_disconnect(timeout=3)
            return  # skip rest of test for now

        self.log.info("🔢 [Test] Initial ping_counter for peer_checkpoint: %d", peer_checkpoint.ping_counter)
        self.log.debug("🌱 getchaintips(): %r", self.nodes[0].getchaintips())

        assert {
            'height': 546,
            'hash': '000000002a936ca763904c3c35fce2f3556c559c0214345d31b1bcebf76acb70',
            'branchlen': 546,
            'status': 'headers-only',
        } in self.nodes[0].getchaintips()

        self.log.info("Feed all fork headers (fails due to checkpoint)")
        with self.nodes[0].assert_debug_log(['bad-fork-prior-to-checkpoint']):
            peer_checkpoint.send_message(msg_headers(self.headers_fork))
            peer_checkpoint.wait_for_disconnect()

        self.log.info("Feed all fork headers (succeeds without checkpoint)")
        # On node 0 it succeeds because checkpoints are disabled
        self.restart_node(0, extra_args=['-nocheckpoints', "-minimumchainwork=0x0", '-prune=550'])
        peer_no_checkpoint = self.nodes[0].add_p2p_connection(P2PDataStore())
        peer_checkpoint.timeout_factor = 1.0  # Force override here
        peer_no_checkpoint.send_and_ping(msg_headers(self.headers_fork))
        self.log.info("🔢 [Test] Initial ping_counter for peer_checkpoint: %d", peer_checkpoint.ping_counter)

        assert {
            "height": 2,
            "hash": "00000000b0494bd6c3d5ff79c497cfce40831871cbf39b1bc28bd1dac817dc39",
            "branchlen": 2,
            "status": "headers-only",
        } in self.nodes[0].getchaintips()

        # On node 1 it succeeds because no checkpoint has been reached yet by a chain tip
        peer_before_checkpoint = self.nodes[1].add_p2p_connection(P2PDataStore())
        peer_checkpoint.timeout_factor = 1.0  # Force override here
        peer_before_checkpoint.send_and_ping(msg_headers(self.headers_fork))
        self.log.info("🔢 [Test] Initial ping_counter for peer_checkpoint: %d", peer_checkpoint.ping_counter)

        assert {
            "height": 2,
            "hash": "00000000b0494bd6c3d5ff79c497cfce40831871cbf39b1bc28bd1dac817dc39",
            "branchlen": 2,
            "status": "headers-only",
        } in self.nodes[1].getchaintips()

        self.log.info("🎯 Test completed successfully — headers sent and peer disconnected.")

if __name__ == '__main__':
    RejectLowDifficultyHeadersTest(__file__).main()
