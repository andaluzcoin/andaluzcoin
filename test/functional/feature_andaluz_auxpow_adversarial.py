#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying COPYING.
"""Finite differential/resource research on unchanged detached R0 decoders.

No real AuxPoW, work, transaction validity, transport allocation or security
guarantee. Fixtures/oracles use no R0 construction, encoding or hash helpers.
Case order, mutations and corpus framing are fixed; no runtime randomness.
"""
import argparse
import hashlib
import math
import sys
import unittest
from unittest import mock

import feature_andaluz_auxpow_serialization as r0


DOMAIN = bytes(range(32))
CHILD = bytes(range(80))
MARKER = bytes.fromhex('fabe6d6d')
PREFIX = b'AP79\x01'
CASE_CAP = 4096
INPUT_CAP = 16385  # Includes one deliberate R0-overcap sentinel.
CORPUS_PREFIX = b'ALUZ-R0-CORPUS-281\x00'
# Sealed after initial generation; independently corroborated outside this file.
EXPECTED_CORPUS = (3449, 1599, 1850,
                   'da83fbf9c52a4c2cd091fc906011e682c6acf76a200c41e0ff8eadc726693278')


def le(value, width=4):
    return value.to_bytes(width, 'little')


def length(value):
    """Independent fixture encoder, not a decoder or production interface."""
    if value < 253:
        return bytes((value,))
    for tag, width in ((253, 2), (254, 4), (255, 8)):
        if value < 1 << (8 * width):
            return bytes((tag,)) + le(value, width)
    raise ValueError('fixture length outside uint64')


def double_hash(raw):
    return hashlib.sha256(hashlib.sha256(raw).digest()).digest()


def transaction(outputs, input_script=b'\x01\x01'):
    outputs = tuple(outputs)
    return (le(1) + b'\x01' + bytes(32) + b'\xff' * 4
            + length(len(input_script)) + input_script + b'\xff' * 4
            + length(len(outputs))
            + b''.join(le(value, 8) + length(len(script)) + script for value, script in outputs)
            + bytes(4))


def record(outputs, *, parent_branch=(), auxiliary_branch=(), auxiliary_index=0,
           parent_root=None, input_script=b'\x01\x01', domain=DOMAIN, child=CHILD):
    """Construct bytes and expected normalized fields directly from the grammar."""
    outputs = tuple(outputs)
    tx = transaction(outputs, input_script)
    if parent_root is None:
        if parent_branch:
            raise ValueError('branched fixture requires independent root')
        parent_root = double_hash(tx)
    parent = le(4) + b'\x33' * 32 + parent_root + bytes(12)
    raw = (PREFIX + domain + child + length(len(tx)) + tx
           + length(len(parent_branch)) + b''.join(parent_branch) + bytes(4)
           + length(len(auxiliary_branch)) + b''.join(auxiliary_branch)
           + le(auxiliary_index) + parent)
    expected = (domain, child, tx, outputs, tuple(parent_branch), 0,
                tuple(auxiliary_branch), auxiliary_index, parent)
    return raw, expected


def commitment(root, size, nonce):
    return MARKER + bytes.fromhex(root)[::-1] + le(size) + le(nonce)


ZERO_SCRIPT = commitment('a16523acc3578eef2892e54a69b410378bfffa29a079b926b015d5d27c94d77a', 1, 0)
BRANCH_SCRIPT = commitment('df23f4b7fb2199275459196c7140e341095e2bb24475204bdcde7d7dccbd346b', 8, 1)
MAX_SCRIPT = commitment('0cb3c9e99758a3c4b90bd46ae311039d7b9ee94c2ffe58b427cdcc4d502bf014', 1 << 30, 0xffffffff)
MINIMAL = record(((0, b''),))
ZERO = record(((0, ZERO_SCRIPT),))
BRANCHED = record(((0, BRANCH_SCRIPT),), parent_branch=(b'\x50' * 32, b'\x51' * 32),
                  auxiliary_branch=tuple(bytes((v,)) * 32 for v in (0x78, 0x79, 0x7a)),
                  auxiliary_index=2,
                  parent_root=bytes.fromhex('03f924df1ba7dc5b31f6164e566f92c74e9a9ddab2f1725ee137654cac4e18f3'))
MAXIMAL = record(((0, MAX_SCRIPT),) + ((0, b'\x55' * 1024),) * 3 + ((0, b'\x55' * 874),),
                 parent_branch=tuple(bytes((0x50 + i,)) * 32 for i in range(30)),
                 auxiliary_branch=tuple(bytes((0x78 + i,)) * 32 for i in range(30)),
                 auxiliary_index=497393936,
                 parent_root=bytes.fromhex('471654683cb2f5d7f61194f3fb2ccceac46e0376bfb35e8fcc03f378b54c1029'))
SEEDS = (('minimal', MINIMAL), ('zero', ZERO), ('branched', BRANCHED), ('maximal', MAXIMAL))
SEALS = (
    (270, 'b272a2710e55ec3614fb09b38a5f915a286b13cc288b4b35cd06e680b88e0417'),
    (314, '3bc6dcddc5c6fac2435387a39bde62dedc135775b5b9bbd72177ec5eb6fabfe0'),
    (474, '5710dab227cd9ebf2e429830873afb47cafff39dc82bcba06abbb44eee9a96de'),
    (6226, '4e9f003b44a721c5f2b625b278ee6f56f343c4e4205a8790eb6b3e198a48c805'),
)


def replace(raw, start, size, replacement):
    return raw[:start] + replacement + raw[start + size:]


def outer(tx, suffix=ZERO[0][224:]):
    # Reframe an independently constructed transaction, with fixed outer fields.
    return PREFIX + DOMAIN + CHILD + length(len(tx)) + tx + suffix


def positions(expected):
    tx, parent_branch, auxiliary_branch = expected[2], expected[4], expected[6]
    parent_count = 117 + len(length(len(tx))) + len(tx)
    parent_index = parent_count + 1 + 32 * len(parent_branch)
    auxiliary_count = parent_index + 4
    auxiliary_index = auxiliary_count + 1 + 32 * len(auxiliary_branch)
    return parent_count, parent_index, auxiliary_count, auxiliary_index, auxiliary_index + 4


def oracle_cases():
    """label, bytes, independently expected tuple (None=reject), linkage label."""
    for name, (raw, expected) in SEEDS:
        yield name, raw, expected, name != 'minimal'
    for name, offset, field, field_offset in (('parent-version', 234, 8, 0),
                                            ('parent-bits', 306, 8, 72)):
        raw, expected = ZERO
        changed = replace(raw, offset, 4, b'\xff' * 4)
        fields = list(expected)
        fields[field] = replace(fields[field], field_offset, 4, b'\xff' * 4)
        yield name, changed, tuple(fields), True  # Opaque headers: no PoW/version check.
    for name, domain, child in (('wrong-domain', DOMAIN[::-1], CHILD),
                                ('changed-child', DOMAIN, b'\xff' * 80)):
        raw, expected = record(((0, ZERO_SCRIPT),), domain=domain, child=child)
        yield name, raw, expected, False
    for name, outputs, script_in, linked in (
            ('paid-commitment', ((1, ZERO_SCRIPT),), b'\x01\x01', False),
            ('duplicate-output-marker', ((0, ZERO_SCRIPT), (0, ZERO_SCRIPT)), b'\x01\x01', False),
            ('input-marker', ((0, ZERO_SCRIPT),), MARKER + b'\x01\x01', False),
            ('unvalidated-money', ((0, ZERO_SCRIPT), (0xffffffffffffffff, b'')), b'\x01\x01', True),
            ('input-script100', ((0, b''),), b'\x55' * 100, False),
            ('output-script253', ((0, b'\x55' * 253),), b'\x01\x01', False),
            ('output-script1024', ((0, b'\x55' * 1024),), b'\x01\x01', False),
            ('outputs16', ((0, b''),) * 16, b'\x01\x01', False)):
        raw, expected = record(outputs, input_script=script_in)
        yield name, raw, expected, linked
    zero, tx = ZERO[0], ZERO[1][2]
    for name, raw in (
            ('empty', b''), ('overcap', bytes(INPUT_CAP)), ('unknown-profile', b'NO79' + zero[4:]),
            ('unknown-version', replace(zero, 4, 1, b'\x02')), ('trailing', zero + b'\x00'),
            ('witness-marker', outer(replace(tx, 4, 1, b'\x00\x01'))),
            ('nonnull-prevout', outer(replace(tx, 5, 1, b'\x01'))),
            ('wrong-previndex', outer(replace(tx, 37, 4, bytes(4)))),
            ('input-script101', record(((0, b''),), input_script=b'\x55' * 101)[0]),
            ('output-script1025', record(((0, b'\x55' * 1025),))[0]),
            ('outputs17', record(((0, b''),) * 17)[0]),
            ('parent-index1', replace(zero, 225, 4, le(1))),
            ('aux-index1-depth0', replace(zero, 230, 4, le(1)))):
        yield name, raw, None, None


def corpus():
    """Stream fixed grammar controls, exhaustively small and sampled mutations."""
    for name, raw, _, _ in oracle_cases():
        yield 'oracle/' + name, raw
    for name, (raw, _) in SEEDS:
        cuts = range(len(raw)) if len(raw) < 1000 else sorted(
            set(range(118)) | set(range(len(raw) - 80, len(raw)))
            | {119, 120, 121, 4095, 4096, 4097, 4215, 4216, 5180, 5181, 6145, 6146})
        for end in cuts:
            yield f'truncate/{name}/{end}', raw[:end]
        for suffix_no, suffix in enumerate((b'\x00', b'\xff', PREFIX, raw)):
            yield f'extend/{name}/{suffix_no}', raw + suffix
    for name, (raw, _) in SEEDS[1:3]:
        for position in range(len(raw)):
            for bit in (0, 7):
                yield f'bit/{name}/{position}/{bit}', replace(raw, position, 1, bytes((raw[position] ^ (1 << bit),)))
    # Fixed 32-bit LCG solely selects deterministic byte substitutions.
    state = 0x02815eed
    for case in range(256):
        name, (raw, _) = SEEDS[case % 4]
        state = (1664525 * state + 1013904223) & 0xffffffff
        position = state % len(raw)
        state = (1664525 * state + 1013904223) & 0xffffffff
        byte = state >> 24
        if byte == raw[position]:
            byte ^= 1
        yield f'lcg/{case}/{name}/{position}', replace(raw, position, 1, bytes((byte,)))
    raw = ZERO[0]
    for position in (0, 4, 5, 36, 37, 116, 117, 118, 159, 160, 166, 175, 176,
                     219, 220, 223, 224, 225, 228, 229, 230, 233, 234, 269, 270, 301, 302, 313, 314):
        for byte in (0, 253, 255):
            yield f'insert/{position}/{byte}', replace(raw, position, 0, bytes((byte,)))
        if position < len(raw):
            yield f'delete/{position}', replace(raw, position, 1, b'')
    values = (0, 1, 30, 31, 100, 101, 252, 253, 255, 256, 1024, 1025, 4096, 4097,
              65535, 65536, 0xffffffff, 1 << 32, (1 << 64) - 1)
    for position in (117, 122, 159, 166, 175, 224, 229):
        for value in values:
            yield f'compact/{position}/{value}', replace(raw, position, 1, length(value))
        for tag, width in ((253, 2), (254, 4), (255, 8)):
            yield f'nonminimal/{position}/{tag}', replace(raw, position, 1, bytes((tag,)) + le(raw[position], width))
    for name, (raw, expected) in SEEDS:
        _, parent_index, _, aux_index, _ = positions(expected)
        for value in (0, 1, 30, 1 << 30, 0xffffffff):
            yield f'parent-index/{name}/{value}', replace(raw, parent_index, 4, le(value))
        depth = len(expected[6])
        for value in sorted({0, 1, (1 << depth) - 1, 1 << depth, 0xffffffff}):
            yield f'aux-index/{name}/{value}', replace(raw, aux_index, 4, le(value))


def outcome(parser, raw):
    try:
        return True, parser(raw)
    except ValueError:
        return False, None  # Every other exception propagates and fails the test.


def check_pair(raw):
    a, b = outcome(r0.parse_a, raw), outcome(r0.parse_b, raw)
    if a != b:
        raise AssertionError('R0 decoder outcome or normalized-field disagreement')
    return a


def bounded_corpus():
    """Apply identical case/input/label guards to every corpus consumer."""
    labels = set()
    for total, (label, raw) in enumerate(corpus(), 1):
        if total > CASE_CAP or type(raw) is not bytes or len(raw) > INPUT_CAP or label in labels:
            raise AssertionError('corpus budget/type/unique-label violation')
        labels.add(label)
        yield label, raw


def summarize():
    identity = hashlib.sha256(CORPUS_PREFIX)
    total = accepted = 0
    for label, raw in bounded_corpus():
        total += 1
        encoded = label.encode('ascii')
        identity.update(le(len(encoded), 2) + encoded + le(len(raw)) + raw)
        accepted += check_pair(raw)[0]
    return total, accepted, total - accepted, identity.hexdigest()


def observe(parser, raw):
    """Reversible logical-read observation; not memory/RSS instrumentation."""
    name = 'CursorA' if parser is r0.parse_a else '_BInput'
    original = getattr(r0, name)
    stats = {'constructors': 0, 'takes': 0, 'eof': 0, 'requests': []}

    class Observed(original):
        def __init__(self, data):
            self.observer_number = stats['constructors']
            stats['constructors'] += 1
            super().__init__(data)

        def take(self, count):
            position = self.pos if name == 'CursorA' else self.stream.tell()
            stats['takes'] += 1
            stats['requests'].append((self.observer_number, position, count))
            return super().take(count)

        def finished(self):
            stats['eof'] += 1
            return super().finished()

    with mock.patch.object(r0, name, Observed):
        result = outcome(parser, raw)
    if getattr(r0, name) is not original:
        raise AssertionError('read observer was not restored')
    return result, stats


class ResearchTests(unittest.TestCase):
    def test_independent_fixed_oracles(self):
        for (name, (raw, expected)), (size, seal) in zip(SEEDS, SEALS):
            with self.subTest(seed=name):
                self.assertEqual(len(raw), size)
                self.assertEqual(double_hash(raw).hex(), seal)
                self.assertEqual(check_pair(raw), (True, expected))
        self.assertEqual(len(MAXIMAL[1][2]), 4096)
        for name, raw, expected, linked in oracle_cases():
            with self.subTest(oracle=name):
                result = check_pair(raw)
                self.assertEqual(result, (expected is not None, expected))
                if expected is not None:
                    self.assertIs(r0.linked_model(result[1], DOMAIN, 7), linked)

    def test_corpus_identity_and_differential_agreement(self):
        actual = summarize()
        self.assertEqual(actual, EXPECTED_CORPUS)
        self.assertGreater(actual[1], 0)
        self.assertGreater(actual[2], 0)
        print(f'Corpus total/accept/reject/SHA256: {actual}')

    def test_instrumented_corpus_preserves_results_and_read_bounds(self):
        maxima = [0, 0]
        for label, raw in bounded_corpus():
            baseline = check_pair(raw)
            for index, parser in enumerate((r0.parse_a, r0.parse_b)):
                measured, stats = observe(parser, raw)
                with self.subTest(case=label, decoder=index):
                    self.assertEqual(measured, baseline)
                    self.assertLessEqual(stats['constructors'], 2)
                    self.assertLessEqual(stats['takes'], (144, 145)[index])
                    self.assertLessEqual(stats['eof'], (0, 2)[index])
                    reads = stats['takes'] + stats['eof']
                    self.assertLessEqual(reads, (144, 147)[index])
                    maxima[index] = max(maxima[index], reads)
            if baseline[0]:
                fields = baseline[1]
                self.assertLessEqual(len(fields[3]), 16)
                self.assertLessEqual(len(fields[4]), 30)
                self.assertLessEqual(len(fields[6]), 30)
        print(f'Observed maximum logical reads A/B: {tuple(maxima)}')

    def test_rejection_before_construction_payload_or_branch_loop(self):
        raw, tx = ZERO[0], ZERO[1][2]
        for parser in (r0.parse_a, r0.parse_b):
            for bad in (bytes(INPUT_CAP), bytearray(raw), None):
                result, stats = observe(parser, bad)
                self.assertEqual(result, (False, None))
                self.assertEqual((stats['constructors'], stats['takes'], stats['eof']), (0, 0, 0))
            for position in (117, 224, 229):
                for encoded in (b'\xff' + b'\xff' * 8, b'\xfd' + le(raw[position], 2)):
                    bad = replace(raw, position, 1, encoded)
                    result, stats = observe(parser, bad)
                    self.assertEqual(result, (False, None))
                    self.assertEqual(stats['requests'][-1], (0, position + 1, len(encoded) - 1))
                    self.assertEqual(stats['constructors'], 1 if position == 117 else 2)
            # Inner field limits reject before script reads/output loops.
            for position, value in ((4, 2), (41, 101), (48, 17), (57, 1025)):
                encoded = length(value)
                bad = outer(replace(tx, position, 1, encoded))
                result, stats = observe(parser, bad)
                self.assertEqual(result, (False, None))
                last_offset = position if len(encoded) == 1 else position + 1
                last_width = 1 if len(encoded) == 1 else len(encoded) - 1
                self.assertEqual(stats['requests'][-1], (1, last_offset, last_width))
            for position in (4, 41, 48, 57):
                encoded = b'\xfd' + le(tx[position], 2)
                result, stats = observe(parser, outer(replace(tx, position, 1, encoded)))
                self.assertEqual(result, (False, None))
                self.assertEqual(stats['requests'][-1], (1, position + 1, 2))

    def test_truncated_compactsize_stops_at_width_read(self):
        raw, tx = ZERO[0], ZERO[1][2]
        for parser in (r0.parse_a, r0.parse_b):
            for tag, width in ((253, 2), (254, 4), (255, 8)):
                for available in range(width):
                    suffix = bytes((tag,)) + bytes(available)
                    for position in (117, 224, 229):
                        result, stats = observe(parser, raw[:position] + suffix)
                        self.assertEqual(result, (False, None))
                        self.assertEqual(stats['requests'][-1], (0, position + 1, width))
                        self.assertEqual(stats['constructors'], 1 if position == 117 else 2)
                    for position in (4, 41, 48, 57):
                        result, stats = observe(parser, outer(tx[:position] + suffix))
                        self.assertEqual(result, (False, None))
                        self.assertEqual(stats['requests'][-1], (1, position + 1, width))
                        self.assertEqual(stats['constructors'], 2)

    def test_supplied_buffer_cap_boundaries(self):
        for parser in (r0.parse_a, r0.parse_b):
            for size in (16383, 16384):
                raw = ZERO[0] + bytes(size - len(ZERO[0]))
                result, stats = observe(parser, raw)
                self.assertEqual(result, (False, None))
                self.assertEqual(stats['constructors'], 2)
            result, stats = observe(parser, bytes(16385))
            self.assertEqual(result, (False, None))
            self.assertEqual((stats['constructors'], stats['takes'], stats['eof']), (0, 0, 0))

    def test_observer_restores_classes_after_reader_exception(self):
        for parser, name in ((r0.parse_a, 'CursorA'), (r0.parse_b, '_BInput')):
            original = getattr(r0, name)
            original_take = original.take
            with mock.patch.object(original, 'take', side_effect=RuntimeError('injected reader failure')):
                with self.assertRaisesRegex(RuntimeError, 'injected reader failure'):
                    observe(parser, ZERO[0])
                self.assertIs(getattr(r0, name), original)
            self.assertIs(original.take, original_take)

    def test_many_outputs_and_sibling_bounds(self):
        # Separate from the sealed five-output maximum linkage fixture.
        outputs = ((0, b'\x55' * 1024),) * 3 + ((0, b'\x55' * 819),) + ((0, b''),) * 12
        raw, expected = record(outputs, parent_branch=(bytes(32),) * 30,
                               auxiliary_branch=(bytes(32),) * 30, parent_root=bytes(32))
        self.assertEqual((len(raw), len(expected[2]), len(expected[3])), (6226, 4096, 16))
        for parser in (r0.parse_a, r0.parse_b):
            measured, stats = observe(parser, raw)
            self.assertEqual(measured, (True, expected))
            self.assertLessEqual(stats['takes'] + stats['eof'], 144 if parser is r0.parse_a else 147)
        # Fifteen canonical fd scripts maximize read calls within the tx cap.
        raw, expected = record(((0, b'\x55' * 253),) * 15 + ((0, b''),),
                               parent_branch=(bytes(32),) * 30,
                               auxiliary_branch=(bytes(32),) * 30, parent_root=bytes(32))
        self.assertEqual((len(raw), len(expected[2])), (6152, 4022))
        for parser, reads in ((r0.parse_a, 143), (r0.parse_b, 146)):
            measured, stats = observe(parser, raw)
            self.assertEqual(measured, (True, expected))
            self.assertEqual(stats['takes'] + stats['eof'], reads)
        parent_count, parent_index, auxiliary_count, auxiliary_index, _ = positions(MAXIMAL[1])
        for offset in (parent_count, auxiliary_count):
            self.assertEqual(check_pair(replace(MAXIMAL[0], offset, 1, b'\x1f')), (False, None))
        for value in (1 << 30, 0xffffffff):
            self.assertEqual(check_pair(replace(MAXIMAL[0], auxiliary_index, 4, le(value))), (False, None))
        self.assertEqual(check_pair(replace(MAXIMAL[0], parent_index, 4, le(1))), (False, None))

    def test_linkage_hash_observer_and_noncoverage(self):
        original = r0.sha256d
        maximum = (0, 0, 0)
        for name, raw, expected, linked in oracle_cases():
            if expected is None:
                continue
            parsed = check_pair(raw)[1]  # Only parser-produced tuples enter linkage.
            baseline = r0.linked_model(parsed, DOMAIN, 7)
            sizes = []

            def observed(data):
                sizes.append(len(data))
                return original(data)

            with mock.patch.object(r0, 'sha256d', observed):
                self.assertIs(r0.linked_model(parsed, DOMAIN, 7), baseline)
            self.assertIs(r0.sha256d, original)
            self.assertIs(baseline, linked)
            counts = len(sizes), sum(sizes), sum(sizes) + 32 * len(sizes)
            self.assertLessEqual(counts[0], 63)
            self.assertLessEqual(counts[1], 8095)
            self.assertLessEqual(counts[2], 10111)
            maximum = tuple(max(a, b) for a, b in zip(maximum, counts))
            if name == 'maximal':
                self.assertEqual(counts, (63, 8095, 10111))
        self.assertEqual(maximum, (63, 8095, 10111))

    def test_evaluator_does_not_hide_disagreement_or_unexpected_exceptions(self):
        with mock.patch.object(r0, 'parse_b', return_value=()):
            with self.assertRaises(AssertionError):
                check_pair(ZERO[0])
        with mock.patch.object(r0, 'parse_b', side_effect=RuntimeError('injected observer control')):
            with self.assertRaises(RuntimeError):
                check_pair(ZERO[0])
        self.assertEqual(outcome(lambda _: (_ for _ in ()).throw(ValueError()), b''), (False, None))


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
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ResearchTests))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
