#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying COPYING.
"""Offline signed-version/domain research, NOT an AuxPoW or ALUZ validator.

Signed division precedent: namecoin/namecoin-core commit
942b14038f3ae704b6c2d50355de835d3ee92288, src/primitives/pureheader.h.
Literal boundary rows were independently checked with C++17 signed arithmetic;
synthetic SHA256d literals with OpenSSL. No chain ID or wire format is proposed.
"""
import argparse
import hashlib
import math
import sys
import unittest


INT32_MIN = -(1 << 31)
INT32_MAX = (1 << 31) - 1
UINT32_MAX = (1 << 32) - 1
CHAIN_DIVISOR = 1 << 16
AUXPOW_FLAG = 1 << 8
TOP_BITS = 0x20000000
TOP_MASK = 0xe0000000
# signed version, uint32 representation, C++ quotient, unsigned upper16,
# floor quotient, bit8, top001. These are predicates, NOT acceptance results.
VERSION_VECTORS = (
    (-2147483648, 0x80000000, -32768, 32768, -32768, False, False),
    (-65537, 0xfffeffff, -1, 65534, -2, True, False),
    (-65536, 0xffff0000, -1, 65535, -1, False, False),
    (-65535, 0xffff0001, 0, 65535, -1, False, False),
    (-1, 0xffffffff, 0, 65535, -1, True, False),
    (0, 0x00000000, 0, 0, 0, False, False),
    (255, 0x000000ff, 0, 0, 0, False, False),
    (256, 0x00000100, 0, 0, 0, True, False),
    (65535, 0x0000ffff, 0, 0, 0, True, False),
    (65536, 0x00010000, 1, 1, 1, False, False),
    (536870912, 0x20000000, 8192, 8192, 8192, False, True),
    (536871168, 0x20000100, 8192, 8192, 8192, True, True),
    (2147483647, 0x7fffffff, 32767, 32767, 32767, True, False),
)
# Synthetic data and research label only; neither genesis is a real network.
DOMAIN_LABEL = b'ALUZ-AUXPOW-RESEARCH-ONLY\x00'
GENESIS_A = bytes(range(32))
GENESIS_B = GENESIS_A[::-1]
CHILD = b'\x42' * 32


def integer(value, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError('integer outside research domain')
    return value


def signed_version(value):
    return integer(value, INT32_MIN, INT32_MAX)


def version_bits(value):
    return signed_version(value) & UINT32_MAX


def truncating_division(value, divisor):
    """C++ quotient toward zero, without float conversion or signed overflow."""
    signed_version(value)
    integer(divisor, 1, INT32_MAX)
    quotient = abs(value) // divisor
    return -quotient if value < 0 else quotient


def chain_id(value):
    return truncating_division(value, CHAIN_DIVISOR)


def signed_remainder(value, divisor):
    return value - truncating_division(value, divisor) * divisor


def positive_encoding(chain, low16):
    """Bounded mathematical encoding; not an upstream setter or ALUZ format."""
    integer(chain, 0, 32767)
    integer(low16, 0, 65535)
    return chain * CHAIN_DIVISOR + low16


def synthetic_domain_hash(genesis, child):
    """90 fixed bytes; no real proof, transaction or network-context checks."""
    for field in (genesis, child):
        if type(field) is not bytes or len(field) != 32:
            raise ValueError('exact synthetic 32-byte field required')
    first = hashlib.sha256(DOMAIN_LABEL + genesis + child).digest()
    return hashlib.sha256(first).digest()


class ResearchTests(unittest.TestCase):
    def test_signed_boundary_vectors(self):
        for value, bits, quotient, upper, floor, auxpow, top in VERSION_VECTORS:
            with self.subTest(value=value):
                self.assertEqual(version_bits(value), bits)
                self.assertEqual(chain_id(value), quotient)
                self.assertEqual(bits >> 16, upper)
                self.assertEqual(value // CHAIN_DIVISOR, floor)
                self.assertEqual(bool(bits & AUXPOW_FLAG), auxpow)
                self.assertEqual((bits & TOP_MASK) == TOP_BITS, top)

    def test_signed_wire_bytes(self):
        # Only the four-byte integer field is represented, not a block header.
        for value, encoded in ((INT32_MIN, '00000080'), (-65537, 'fffffeff'),
                               (-65535, '0100ffff'), (-1, 'ffffffff'),
                               (0, '00000000'), (65536, '00000100'),
                               (TOP_BITS, '00000020'), (INT32_MAX, 'ffffff7f')):
            raw = bytes.fromhex(encoded)
            self.assertEqual(value.to_bytes(4, 'little', signed=True), raw)
            self.assertEqual(int.from_bytes(raw, 'little', signed=True), value)

    def test_negative_remainder_is_not_unsigned_mask(self):
        # Namecoin's GetBaseVersion uses signed %256; Myriad uses low8 mask.
        for value, base, low8 in ((-1, -1, 255), (-65532, -252, 4)):
            self.assertEqual(signed_remainder(value, 256), base)
            self.assertEqual(version_bits(value) & 255, low8)
        # Negative ID -1 combined with base4 need not round-trip as ID -1.
        self.assertEqual((-65536 | 4), -65532)
        self.assertEqual(chain_id(-65532), 0)
        # A negative remainder retains sign bits; it is not a cleared high word.
        self.assertEqual(signed_remainder(-1, 65536) | 65536, -1)

    def test_nonnegative_encoding_boundaries(self):
        # Independently cross-checked C++ int64 intermediates; no signed wrap.
        for chain in (0, 1, 8192, 32767):
            for low16 in (0, 256, 65535):
                with self.subTest(chain=chain, low16=low16):
                    value = positive_encoding(chain, low16)
                    self.assertLessEqual(value, INT32_MAX)
                    self.assertEqual(chain_id(value), chain)
                    self.assertEqual(value & 65535, low16)
        self.assertEqual(positive_encoding(1, 260), 0x00010104)
        self.assertEqual(positive_encoding(32767, 65535), INT32_MAX)
        for low16, wide in ((0, 2147483648), (256, 2147483904),
                            (65535, 2147549183)):
            self.assertEqual(32768 * CHAIN_DIVISOR + low16, wide)
            self.assertGreater(wide, INT32_MAX)
            with self.assertRaises(ValueError):
                positive_encoding(32768, low16)

    def test_invalid_model_parameters(self):
        for invalid in (INT32_MIN - 1, INT32_MAX + 1, True, False, 1.0, '1', None):
            with self.assertRaises(ValueError):
                chain_id(invalid)
        for invalid in (-1, 32768, True, 1.0, None):
            with self.assertRaises(ValueError):
                positive_encoding(invalid, 4)
        for invalid in (-1, 65536, True, 1.0, None):
            with self.assertRaises(ValueError):
                positive_encoding(1, invalid)
        for invalid in (0, -1, INT32_MAX + 1, True, 1.0):
            with self.assertRaises(ValueError):
                truncating_division(1, invalid)

    def test_signaling_overlap(self):
        # Strict-ID1 cannot simply inherit the BIP9 prefix in this model.
        self.assertEqual(chain_id(TOP_BITS | 0x00010104), 8193)
        # Source-derived Myriad example: configured90 != effective8282.
        myriad_example = TOP_BITS | positive_encoding(90, AUXPOW_FLAG)
        self.assertEqual(myriad_example, 0x205a0100)
        self.assertEqual(chain_id(myriad_example), 8282)
        self.assertNotEqual(chain_id(myriad_example), 90)
        # All nonnegative high-word IDs: top001 iff ID is in this range.
        for chain in range(32768):
            value = positive_encoding(chain, 0)
            self.assertEqual((value & TOP_MASK) == TOP_BITS, 8192 <= chain < 16384)
        # High signaling bits modify extracted ID; bit8 shares the proof flag.
        for bit in range(16, 29):
            self.assertEqual(chain_id(TOP_BITS | (1 << bit)), 8192 | (1 << (bit - 16)))
        self.assertEqual(TOP_BITS | (1 << 8), 0x20000100)
        self.assertTrue((TOP_BITS | (1 << 8)) & AUXPOW_FLAG)

    def test_synthetic_domain_vectors(self):
        self.assertEqual(len(DOMAIN_LABEL + GENESIS_A + CHILD), 90)
        self.assertEqual(synthetic_domain_hash(GENESIS_A, CHILD).hex(),
                         'a076cef2fb01bf1549dd75131fb0ff1777e9581163962b0ecf6b705ffd4ae308')
        self.assertEqual(synthetic_domain_hash(GENESIS_B, CHILD).hex(),
                         '225fde6d4d13b73c2724d63320b28846a494654c20899dedd9f7dc3cfb94b4f2')

    def test_synthetic_domain_mutations(self):
        original = synthetic_domain_hash(GENESIS_A, CHILD)
        self.assertEqual(original, synthetic_domain_hash(GENESIS_A, CHILD))
        self.assertNotEqual(original, synthetic_domain_hash(GENESIS_B, CHILD))
        self.assertNotEqual(original, synthetic_domain_hash(GENESIS_A, CHILD[:-1] + b'\x43'))
        # Equal child bytes alone carry no network distinction in this example.
        self.assertEqual(CHILD, bytes.fromhex('42' * 32))
        for invalid in (b'', CHILD[:-1], CHILD + b'\x00', bytearray(CHILD), None):
            with self.assertRaises(ValueError):
                synthetic_domain_hash(invalid, CHILD)
            with self.assertRaises(ValueError):
                synthetic_domain_hash(GENESIS_A, invalid)


def positive_float(text):
    value = float(text)
    if not math.isfinite(value) or value <= 0:
        raise argparse.ArgumentTypeError('finite positive value required')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    for name in ('configfile', 'cachedir', 'tmpdir', 'coveragedir'):
        parser.add_argument('--' + name)
    for name in ('portseed', 'randomseed'):
        parser.add_argument('--' + name, type=int)
    parser.add_argument('--timeout-factor', type=positive_float)
    for name in ('v1transport', 'v2transport', 'usecli', 'previous-releases', 'nocleanup'):
        parser.add_argument('--' + name, action='store_true')
    parser.parse_args()
    if sys.flags.optimize:
        parser.error('optimized Python is unsupported for this research test')
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ResearchTests)
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
