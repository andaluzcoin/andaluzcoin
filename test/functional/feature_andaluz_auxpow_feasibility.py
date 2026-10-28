#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.
"""TOY RESEARCH MODEL: deterministic offline SHA256d/Merkle linkage only.

Not canonical Namecoin consensus, an ALUZ PoW validator, a wire proof, or a
block accepted by a node. No network, file I/O, subprocesses or nonce search.
No Bitcoin transaction/script/coinbase-prevout parsing, real auxiliary tree,
chain-ID/nonce/index coupling, child block validation, parent field validation,
work-vs-child-nBits, difficulty/chainwork, activation, time/reorg rules, actual
network replay protection or production memory/CPU DoS resistance is tested.
Toy duplicate-marker policy is not a real duplicate-root/commitment policy.
"""

import argparse
import hashlib
import math
import struct
import sys
import unittest

MAX_DEPTH = 4
MAX_INPUT = 128
PREFIX = b'TOY-COINBASE:'
MARKER = b'|TOY-COMMIT|'
DOMAIN_A = b'TOY-NET-A'
DOMAIN_B = b'TOY-NET-B'


def sha256d(data):
    """Raw digest bytes; Bitcoin-style displayed hash is digest[::-1].hex()."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def hash32(value):
    if not isinstance(value, bytes) or len(value) != 32:
        raise ValueError('hash must be 32 raw bytes')
    return value


def merkle(leaf, siblings, index):
    """Index bits low to high: 0 => hash(node || sibling), 1 => reversed.

    Hashes are raw digest bytes, never ASCII hex or display-order bytes.
    Empty branch is a single leaf. No odd-leaf duplication algorithm implied.
    """
    node = hash32(leaf)
    if not isinstance(siblings, (tuple, list)) or len(siblings) > MAX_DEPTH:
        raise ValueError('branch depth')
    if type(index) is not int or not 0 <= index < (1 << len(siblings)):
        raise ValueError('branch index')
    for level, sibling in enumerate(siblings):
        sibling = hash32(sibling)
        node = sha256d(sibling + node if index >> level & 1 else node + sibling)
    return node


def commitment(domain, child):
    """Fixed toy domains only; neither is a proposed ALUZ chain ID."""
    if domain not in (DOMAIN_A, DOMAIN_B):
        raise ValueError('unknown toy domain')
    return sha256d(b'TOY-CHILD:' + domain + hash32(child))


def coinbase_like(domain, child, padding=b''):
    """Synthetic bytes, deliberately not a Bitcoin transaction."""
    blob = PREFIX + MARKER + commitment(domain, child) + padding
    if len(blob) > MAX_INPUT:
        raise ValueError('commitment input too large')
    return blob


def check_link(domain, child, blob, siblings, index, parent_root):
    """Check toy placement + binding + membership; NOT a PoW verifier."""
    expected = commitment(domain, child)
    if not isinstance(blob, bytes) or len(blob) > MAX_INPUT:
        raise ValueError('commitment input too large/type')
    start = len(PREFIX)
    if blob.count(MARKER) != 1:
        raise ValueError('missing/duplicate marker')
    if not blob.startswith(PREFIX + MARKER):
        raise ValueError('marker placement')
    if blob[start + len(MARKER):start + len(MARKER) + 32] != expected:
        raise ValueError('child commitment')
    root = merkle(sha256d(blob), siblings, index)
    if root != hash32(parent_root):
        raise ValueError('parent Merkle root')
    return root


def header(root):
    """Synthetic 80-byte layout only; nonce fixed at zero, no work claim."""
    return struct.pack('<i', 1) + bytes(32) + hash32(root) + struct.pack('<III', 0, 0, 0)


# Independent constants: OpenSSL dgst -sha256 -binary twice over raw bytes.
# Leaves are 00*32, 01*32, 02*32, 03*32. Not real transaction IDs.
PAIR = bytes.fromhex('705ede9d42476fc3e5a978b042ce790a193678f46d19f47ec4ab46539c47b76d')
RIGHT = bytes.fromhex('1b12c142ca6fabe6cccf4aa52aff1f21882ec49da2dd4c1cf70abffcc45f591b')
FOUR = bytes.fromhex('ac41efca4951b1260054e1155fd8f6c3f42a5b521f1161b20f3c053d3159816c')


class LinkageTests(unittest.TestCase):
    def setUp(self):
        self.child = bytes.fromhex('11' * 32)
        self.blob = coinbase_like(DOMAIN_A, self.child)
        self.sibling = bytes.fromhex('22' * 32)
        self.root = sha256d(sha256d(self.blob) + self.sibling)

    def verify(self, **changes):
        args = dict(domain=DOMAIN_A, child=self.child, blob=self.blob,
                    siblings=[self.sibling], index=0, parent_root=self.root)
        args.update(changes)
        return check_link(**args)

    def test_source_fixed_sha256d_vector(self):
        # src/kernel/chainparams.cpp:135-151 at frozen a6cd2e5, source literal
        # genesis fields and asserted hash. This is a historical vector only.
        raw = (struct.pack('<i', 1) + bytes(32)
               + bytes.fromhex('14a3ed7e9a74a76a935c96b7101d9e5cd4c974534838d77c48bdadb15e103e2a')[::-1]
               + struct.pack('<III', 1769731200, 0x1e00ffff, 549347))
        self.assertEqual(len(raw), 80)
        self.assertEqual(sha256d(raw)[::-1].hex(),
                         '000000f7dca7651a1397fd0bc99b2a456dbb2d23470834b6290aadec4b46d15c')
        self.assertEqual(raw[36:68][::-1].hex(),
                         '14a3ed7e9a74a76a935c96b7101d9e5cd4c974534838d77c48bdadb15e103e2a')

    def test_independent_one_two_four_leaf_vectors(self):
        a, b, c, d = (bytes([i]) * 32 for i in range(4))
        self.assertEqual(merkle(a, [], 0), a)
        self.assertEqual(merkle(a, [b], 0), PAIR)
        self.assertEqual(merkle(b, [a], 1), PAIR)
        self.assertEqual(merkle(c, [d], 0), RIGHT)
        for leaf, branch, index in ((a, [b, RIGHT], 0), (b, [a, RIGHT], 1),
                                    (c, [d, PAIR], 2), (d, [c, PAIR], 3)):
            with self.subTest(index=index):
                self.assertEqual(merkle(leaf, branch, index), FOUR)

    def test_positive_link_and_header_layout(self):
        self.assertEqual(self.verify(), self.root)
        raw = header(self.root)
        self.assertEqual(len(raw), 80)
        self.assertEqual(raw[:4], b'\x01\x00\x00\x00')
        self.assertEqual(raw[4:36], bytes(32))
        self.assertEqual(raw[36:68], self.root)
        self.assertEqual(raw[68:], bytes(12))

    def test_altered_child(self):
        with self.assertRaisesRegex(ValueError, 'child commitment'):
            self.verify(child=bytes(32))

    def test_missing_marker(self):
        with self.assertRaisesRegex(ValueError, 'missing/duplicate'):
            self.verify(blob=self.blob.replace(MARKER, b''))

    def test_duplicate_marker(self):
        with self.assertRaisesRegex(ValueError, 'missing/duplicate'):
            self.verify(blob=self.blob + MARKER)

    def test_marker_placement(self):
        with self.assertRaisesRegex(ValueError, 'placement'):
            self.verify(blob=b'x' + self.blob)

    def test_corrupted_sibling(self):
        with self.assertRaisesRegex(ValueError, 'parent Merkle root'):
            self.verify(siblings=[bytes(32)])

    def test_reversed_left_right(self):
        with self.assertRaisesRegex(ValueError, 'parent Merkle root'):
            self.verify(index=1)

    def test_wrong_indices(self):
        for index in (-1, 2, True):
            with self.subTest(index=index), self.assertRaisesRegex(ValueError, 'index'):
                self.verify(index=index)

    def test_wrong_parent_root(self):
        with self.assertRaisesRegex(ValueError, 'parent Merkle root'):
            self.verify(parent_root=bytes(32))

    def test_truncated_hashes(self):
        for changes in (dict(child=bytes(31)), dict(siblings=[bytes(31)]),
                        dict(parent_root=bytes(31))):
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, '32 raw bytes'):
                self.verify(**changes)
        with self.assertRaises(ValueError):
            merkle(bytes(31), [], 0)

    def test_depth_bounds(self):
        self.assertEqual(len(merkle(bytes(32), [self.sibling] * MAX_DEPTH, 15)), 32)
        with self.assertRaisesRegex(ValueError, 'depth'):
            self.verify(siblings=[self.sibling] * (MAX_DEPTH + 1))
        with self.assertRaises(ValueError):
            merkle(bytes(32), [], 1)

    def test_input_bounds(self):
        full = coinbase_like(DOMAIN_A, self.child, b'x' * (MAX_INPUT - len(self.blob)))
        self.assertEqual(len(full), MAX_INPUT)
        self.verify(blob=full, parent_root=sha256d(sha256d(full) + self.sibling))
        with self.assertRaisesRegex(ValueError, 'too large'):
            self.verify(blob=full + b'x')
        with self.assertRaises(ValueError):
            coinbase_like(DOMAIN_A, self.child, b'x' * MAX_INPUT)

    def test_two_toy_domains_replay(self):
        with self.assertRaisesRegex(ValueError, 'child commitment'):
            self.verify(domain=DOMAIN_B)
        other = coinbase_like(DOMAIN_B, self.child)
        self.verify(domain=DOMAIN_B, blob=other,
                    parent_root=sha256d(sha256d(other) + self.sibling))
        with self.assertRaises(ValueError):
            self.verify(domain=b'UNAPPROVED')


def positive_float(value):
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise argparse.ArgumentTypeError('must be positive and finite')
    return result


def main():
    parser = argparse.ArgumentParser(allow_abbrev=False, description=__doc__)
    # Runner/CI metadata only. Never open paths, start nodes, or emit RPC coverage.
    for name in ('configfile', 'cachedir', 'tmpdir', 'coveragedir'):
        parser.add_argument('--' + name, help='ignored offline runner metadata')
    for name in ('portseed', 'randomseed'):
        parser.add_argument('--' + name, type=int, help='ignored offline runner metadata')
    parser.add_argument('--timeout-factor', type=positive_float, help='ignored offline metadata')
    transports = parser.add_mutually_exclusive_group()
    for name in ('v1transport', 'v2transport'):
        transports.add_argument('--' + name, action='store_true', help='ignored offline metadata')
    for name in ('usecli', 'previous-releases', 'nocleanup'):
        parser.add_argument('--' + name, action='store_true', help='ignored offline metadata')
    parser.parse_args()
    if not __debug__:
        parser.error('optimized Python is unsupported for research tests')
    print('TOY RESEARCH MODEL; no consensus proof, target check or mining')
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(LinkageTests))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
