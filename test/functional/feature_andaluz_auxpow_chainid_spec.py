#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying COPYING.
"""Offline research only; no real transaction/proof/work validator.

Slot precedent: namecoin/namecoin-core commit
942b14038f3ae704b6c2d50355de835d3ee92288, src/auxpow.cpp:143-165.
Nonnegative signed-int IDs only; this domain is NOT a header encoding.
Fixed vectors independently corroborated with GCC 13.3 C++17 uint64 arithmetic.
The fixed synthetic envelope below is TOY TEST ONLY, not a proposed wire format.
"""
import argparse
import math
import sys
import unittest


MAX_NONCE = (1 << 32) - 1
MAX_ID = (1 << 31) - 1
MARKER = bytes.fromhex('fabe6d6d')
DOMAIN = b'TOY1'
CHILD = bytes(range(32))
# h, nonce, illustrative ID, independently fixed slot
VECTORS = (
    (0, 0, 0, 0), (0, MAX_NONCE, MAX_ID, 0),
    (1, 0, 1, 1), (2, 0, 1, 3), (2, 0, 17, 3),
    (4, 0, 1, 11), (4, 0, 17, 11), (4, 1, 90, 9),
    (8, 0, 1, 235), (8, MAX_NONCE, 17, 82),
    (16, 1, 1, 65364), (16, MAX_NONCE, MAX_ID, 11688),
    (30, 0, 0, 333190782), (30, 1, 90, 909525817),
    (30, MAX_NONCE, MAX_ID, 259206568),
    (30, 2147483648, 17, 839338939),
)
UNCOVERED = frozenset(('real coinbase', 'transaction serialization',
                       'witness txids', 'parent work', 'contextual child validation'))


def bounded(value, maximum):
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError('integer outside study domain')
    return value


def slot(height, nonce, chain_id):
    bounded(height, 30)
    bounded(nonce, MAX_NONCE)
    bounded(chain_id, MAX_ID)
    modulus = 1 << height
    first = (nonce * 1103515245 + 12345) % modulus
    return ((first + chain_id) * 1103515245 + 12345) % modulus


def le32(value):
    return bounded(value, MAX_NONCE).to_bytes(4, 'little')


def read_le32(data):
    if type(data) is not bytes or len(data) != 4:
        raise ValueError('exact four-byte field required')
    return int.from_bytes(data, 'little')


def display_hash(data):
    if type(data) is not bytes or len(data) != 32:
        raise ValueError('exact 32-byte field required')
    return data[::-1].hex()


def toy_decode(data, height, chain_id, expected_domain=DOMAIN, expected_child=CHILD):
    """Fixed non-transaction fields: marker/domain/child/LE32 size/nonce/index.

    84 bytes, deliberately unlike a coinbase or real AuxPoW serialization.
    Child appears twice: one commitment position and one root-like toy field.
    No hashing, Merkle branch or production proof validation is performed.
    """
    bounded(height, 30)
    bounded(chain_id, MAX_ID)
    if type(data) is not bytes or len(data) != 84:
        raise ValueError('toy length')
    if data[:4] != MARKER or data.count(MARKER) != 1:
        raise ValueError('toy marker placement or uniqueness')
    if data[4:8] != expected_domain or data[8:40] != expected_child:
        raise ValueError('toy domain or child')
    if data[40:72] != expected_child[::-1]:
        raise ValueError('toy root byte order')
    size, nonce, index = (read_le32(data[i:i + 4]) for i in (72, 76, 80))
    if size != 1 << height or index != slot(height, nonce, chain_id):
        raise ValueError('toy size or index')
    return nonce, index


def example():
    # Independently fixed h=4, nonce=0, illustrative ID=1, slot=11.
    return MARKER + DOMAIN + CHILD + CHILD[::-1] + bytes.fromhex(
        '10000000 00000000 0b000000')


class ResearchTests(unittest.TestCase):
    def test_fixed_vectors(self):
        for height, nonce, chain_id, expected in VECTORS:
            with self.subTest(h=height, nonce=nonce, chain_id=chain_id):
                self.assertEqual(slot(height, nonce, chain_id), expected)

    def test_collision_matrix(self):
        for height in (0, 1, 2, 4, 8, 16, 30):
            for nonce in (0, 1, 2147483648, MAX_NONCE):
                with self.subTest(h=height, nonce=nonce):
                    size = 1 << height
                    self.assertEqual(slot(height, nonce, 1), slot(height, nonce, 1 + size))
                    self.assertEqual(slot(height, nonce, 1), slot(height, nonce, 1))
                    if height:
                        self.assertNotEqual(slot(height, nonce, 0), slot(height, nonce, 1))
                    else:
                        self.assertEqual(slot(height, nonce, 0), slot(height, nonce, MAX_ID))
        self.assertEqual(slot(4, 0, 1), slot(4, 0, 17))
        self.assertNotEqual(slot(8, 0, 1), slot(8, 0, 17))

    def test_parameter_domains(self):
        for position, maximum in enumerate((30, MAX_NONCE, MAX_ID)):
            for invalid in (-1, maximum + 1, True, False, 1.0, '1', None):
                args = [4, 0, 1]
                args[position] = invalid
                with self.subTest(position=position, invalid=invalid):
                    with self.assertRaises(ValueError):
                        slot(*args)

    def test_le32_vectors(self):
        for value, encoded in ((0, '00000000'), (1, '01000000'),
                               (0x12345678, '78563412'), (MAX_NONCE, 'ffffffff')):
            self.assertEqual(le32(value).hex(), encoded)
            self.assertEqual(read_le32(bytes.fromhex(encoded)), value)
        for invalid in (-1, MAX_NONCE + 1, True, 1.0):
            with self.assertRaises(ValueError):
                le32(invalid)
        # Fixed-width decoder rejects CompactSize-like, extended and short fields.
        for invalid in (b'', b'\x01', b'\xfd\x01\x00', b'\x00' * 5, bytearray(4)):
            with self.assertRaises(ValueError):
                read_le32(invalid)

    def test_hash_display(self):
        self.assertEqual(display_hash(CHILD),
                         '1f1e1d1c1b1a191817161514131211100f0e0d0c0b0a09080706050403020100')
        self.assertEqual(bytes.fromhex(display_hash(CHILD))[::-1], CHILD)
        for invalid in (CHILD[:-1], CHILD + b'\x00', b'', bytearray(CHILD)):
            with self.assertRaises(ValueError):
                display_hash(invalid)

    def test_toy_positive(self):
        self.assertEqual(toy_decode(example(), 4, 1), (0, 11))

    def test_toy_rejections(self):
        good = example()
        cases = [good[:-1], good + b'\x00', MARKER + good,
                 b'\x00' + good[1:], good[4:] + good[:4],
                 good[:4] + b'TOY2' + good[8:],
                 good[:8] + b'\xff' + good[9:],
                 good[:40] + CHILD + good[72:]]
        for start, replacement in ((72, le32(3)), (72, le32(32)),
                                    (76, le32(1)), (80, le32(12)),
                                    (72, bytes.fromhex('00000010')),
                                    (80, le32(MAX_NONCE))):
            cases.append(good[:start] + replacement + good[start + 4:])
        # Duplicate marker inside a fixed-size child field also fails.
        cases.append(good[:8] + MARKER + good[12:])
        for malformed in cases:
            with self.subTest(encoded=malformed.hex()):
                with self.assertRaises(ValueError):
                    toy_decode(malformed, 4, 1)
        with self.assertRaises(ValueError):
            toy_decode(good, 4, 1, expected_domain=b'TOY2')
        with self.assertRaises(ValueError):
            toy_decode(good, 4, 1, expected_child=b'\xff' * 32)

    def test_noncoverage_is_explicit(self):
        self.assertEqual(len(UNCOVERED), 5)
        self.assertIn('parent work', UNCOVERED)
        self.assertIn('witness txids', UNCOVERED)
        # Documentary negative: no validator exists for these dimensions.
        for name in ('validate_coinbase', 'validate_transaction', 'validate_witness',
                     'validate_parent_work', 'validate_contextual_child'):
            self.assertNotIn(name, globals())


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
