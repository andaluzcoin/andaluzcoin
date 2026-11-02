#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying COPYING.
"""Detached R0 serialization/linkage/activation research, NOT an ALUZ validator.

AP79/version1, limits and synthetic domains are experimental study choices.
Two independent decoders share no parsing helpers. No real proof work, full
transaction validity, parent-network context or node activation is checked.
"""
import argparse
import hashlib
import io as _b_io
import math
import struct as _b_struct
import sys
import unittest


PROFILE = b'AP79\x01'
MAX_PROOF = 16384
MAX_TX = 4096
MAX_BRANCH = 30
DOMAIN = bytes(range(32))
CHILD = bytes(range(80))
MARKER = bytes.fromhex('fabe6d6d')
LEAF_LABEL = b'ALUZ-AUXPOW-R0\x00'


class CursorA:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def take(self, count):
        if count < 0 or count > len(self.data) - self.pos:
            raise ValueError('A truncated field')
        result = self.data[self.pos:self.pos + count]
        self.pos += count
        return result

    def compact(self, limit):
        prefix = self.take(1)[0]
        if prefix < 253:
            value = prefix
        else:
            width, minimum = {253: (2, 253), 254: (4, 65536), 255: (8, 1 << 32)}[prefix]
            value = int.from_bytes(self.take(width), 'little')
            if value < minimum:
                raise ValueError('A nonminimal CompactSize')
        if value > limit:
            raise ValueError('A count exceeds profile bound')
        return value


def coinbase_a(raw):
    tx = CursorA(raw)
    tx.take(4)
    if tx.compact(1) != 1:
        raise ValueError('A non-witness single input required')
    if tx.take(32) != bytes(32) or tx.take(4) != b'\xff' * 4:
        raise ValueError('A null coinbase prevout required')
    size = tx.compact(100)
    if size < 2:
        raise ValueError('A short input script')
    tx.take(size)
    tx.take(4)
    count = tx.compact(16)
    if count < 1:
        raise ValueError('A output required')
    outputs = []
    for _ in range(count):
        value = int.from_bytes(tx.take(8), 'little')
        size = tx.compact(1024)
        outputs.append((value, tx.take(size)))
    tx.take(4)
    if tx.pos != len(raw):
        raise ValueError('A trailing transaction bytes')
    return tuple(outputs)


def parse_a(data):
    if type(data) is not bytes or len(data) > MAX_PROOF:
        raise ValueError('A proof type/size')
    r = CursorA(data)
    if r.take(5) != PROFILE:
        raise ValueError('A unknown profile')
    domain, child = r.take(32), r.take(80)
    tx = r.take(r.compact(MAX_TX))
    outputs = coinbase_a(tx)
    parent_count = r.compact(MAX_BRANCH)
    parent_branch = tuple(r.take(32) for _ in range(parent_count))
    parent_index = int.from_bytes(r.take(4), 'little')
    if parent_index != 0:
        raise ValueError('A parent index must be zero')
    aux_count = r.compact(MAX_BRANCH)
    aux_branch = tuple(r.take(32) for _ in range(aux_count))
    aux_index = int.from_bytes(r.take(4), 'little')
    if aux_index >= 1 << aux_count:
        raise ValueError('A auxiliary index outside tree')
    parent = r.take(80)
    if r.pos != len(data):
        raise ValueError('A trailing profile bytes')
    return domain, child, tx, outputs, parent_branch, parent_index, aux_branch, aux_index, parent


# Parser B was independently implemented from the grammar using BytesIO/struct.
class _BInput:
    def __init__(self, raw):
        self.stream = _b_io.BytesIO(raw)

    def take(self, amount):
        value = self.stream.read(amount)
        if len(value) != amount:
            raise ValueError('B: incomplete field')
        return value

    def number32(self):
        return _b_struct.unpack('<I', self.take(4))[0]

    def compact(self, ceiling):
        first = self.take(1)[0]
        if first < 253:
            value = first
        elif first == 253:
            value = _b_struct.unpack('<H', self.take(2))[0]
            if value < 253:
                raise ValueError('B: noncanonical CompactSize16')
        elif first == 254:
            value = _b_struct.unpack('<I', self.take(4))[0]
            if value < 65536:
                raise ValueError('B: noncanonical CompactSize32')
        else:
            value = _b_struct.unpack('<Q', self.take(8))[0]
            if value < 4294967296:
                raise ValueError('B: noncanonical CompactSize64')
        if value > ceiling:
            raise ValueError('B: count or length exceeds research bound')
        return value

    def finished(self):
        if self.stream.read(1):
            raise ValueError('B: trailing data')


def _b_coinbase_outputs(raw):
    """Decode only the explicitly bounded nonwitness coinbase subset."""
    reader = _BInput(raw)
    reader.take(4)  # Opaque transaction version, not a validity decision.
    inputs = reader.compact(1)
    if inputs != 1:
        # In particular, a zero witness marker cannot enter this profile.
        raise ValueError('B: exactly one nonwitness input required')
    if reader.take(32) != bytes(32):
        raise ValueError('B: nonzero coinbase previous hash')
    if reader.number32() != 4294967295:
        raise ValueError('B: wrong coinbase previous index')
    script_length = reader.compact(100)
    if script_length < 2:
        raise ValueError('B: short input script')
    reader.take(script_length)
    reader.take(4)  # Opaque sequence.
    count = reader.compact(16)
    if count < 1:
        raise ValueError('B: at least one output required')
    outputs = []
    for _ in range(count):
        amount = _b_struct.unpack('<Q', reader.take(8))[0]
        length = reader.compact(1024)
        script = reader.take(length)
        outputs.append((amount, script))
    reader.take(4)  # Opaque locktime.
    reader.finished()
    return tuple(outputs)


def parse_b(data):
    """Return normalized R0 fields, or ValueError for every profile rejection."""
    # Perform these checks before constructing a stream or inspecting fields.
    if type(data) is not bytes:
        raise ValueError('B: exact bytes input required')
    if len(data) > 16384:
        raise ValueError('B: envelope exceeds research byte cap')
    reader = _BInput(data)
    if reader.take(4) != b'AP79':
        raise ValueError('B: wrong research magic')
    if reader.take(1) != b'\x01':
        raise ValueError('B: wrong research profile version')
    domain = reader.take(32)
    child = reader.take(80)
    transaction_length = reader.compact(4096)
    transaction = reader.take(transaction_length)
    outputs = _b_coinbase_outputs(transaction)
    parent_count = reader.compact(30)
    parent_branch = tuple(reader.take(32) for _ in range(parent_count))
    parent_index = reader.number32()
    if parent_index != 0:
        raise ValueError('B: parent index must be zero')
    auxiliary_count = reader.compact(30)
    auxiliary_branch = tuple(reader.take(32) for _ in range(auxiliary_count))
    auxiliary_index = reader.number32()
    if auxiliary_index >= (1 << auxiliary_count):
        raise ValueError('B: auxiliary index outside branch range')
    parent_header = reader.take(80)
    reader.finished()
    return (domain, child, transaction, outputs, parent_branch, parent_index,
            auxiliary_branch, auxiliary_index, parent_header)


def sha256d(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def root_hash(leaf, siblings, index):
    for sibling in siblings:
        leaf = sha256d(sibling + leaf if index & 1 else leaf + sibling)
        index >>= 1
    return leaf


def slot(height, nonce, chain_id):
    modulus = 1 << height
    first = (nonce * 1103515245 + 12345) % modulus
    return ((first + chain_id) * 1103515245 + 12345) % modulus


def linked_model(parsed, expected_domain, research_id):
    """Only R0 linkage on parser-produced tuples, NOT a raw-input validator."""
    if type(expected_domain) is not bytes or len(expected_domain) != 32:
        raise ValueError('synthetic expected domain required')
    if type(research_id) is not int or not 0 <= research_id <= 32767:
        raise ValueError('bounded illustrative ID required')
    domain, child, tx, outputs, parent_branch, parent_index, aux_branch, aux_index, parent = parsed
    if domain != expected_domain:
        return False
    leaf = sha256d(LEAF_LABEL + domain + sha256d(child))
    root = root_hash(leaf, aux_branch, aux_index)
    commits = [(value, script) for value, script in outputs if MARKER in script]
    if tx.count(MARKER) != 1 or len(commits) != 1:
        return False
    value, script = commits[0]
    if value != 0 or len(script) != 44 or script[:4] != MARKER or script[4:36] != root[::-1]:
        return False
    size, nonce = (int.from_bytes(script[i:i + 4], 'little') for i in (36, 40))
    if size != 1 << len(aux_branch) or aux_index != slot(len(aux_branch), nonce, research_id):
        return False
    return root_hash(sha256d(tx), parent_branch, parent_index) == parent[36:68]


def activation_model(height, boundary, policy, mode, flag, proof, context=True):
    """Parameterized truth table, not node signaling/activation/reorg code."""
    if any(type(v) is not int or not 0 <= v <= 0xffffffff for v in (height, boundary)):
        raise ValueError('symbolic uint32 height required')
    if any(type(v) is not bool for v in (flag, proof, context)):
        raise ValueError('boolean predicates required')
    if not context or policy not in ('legacy', 'hybrid', 'auxonly') or mode not in ('legacy', 'aux'):
        return False
    if flag != proof or flag != (mode == 'aux'):
        return False
    allowed = ('legacy',) if height < boundary or policy == 'legacy' else (
        ('legacy', 'aux') if policy == 'hybrid' else ('aux',))
    return mode in allowed


def cs(value):
    if value < 253:
        return bytes([value])
    if value <= 65535:
        return b'\xfd' + value.to_bytes(2, 'little')
    if value <= 0xffffffff:
        return b'\xfe' + value.to_bytes(4, 'little')
    return b'\xff' + value.to_bytes(8, 'little')


def make_tx(script, input_script=b'\x01\x01', outputs=None):
    if outputs is None:
        outputs = ((0, script),)
    return (bytes.fromhex('01000000 01') + bytes(32) + b'\xff' * 4
            + cs(len(input_script)) + input_script + b'\xff' * 4 + cs(len(outputs))
            + b''.join(v.to_bytes(8, 'little') + cs(len(s)) + s for v, s in outputs) + bytes(4))


def envelope(tx, parent_branch=(), aux_branch=(), aux_index=0, domain=DOMAIN, child=CHILD, parent=None):
    if parent is None:
        parent = bytes.fromhex('04000000') + b'\x33' * 32 + root_hash(sha256d(tx), parent_branch, 0) + bytes(12)
    return (PROFILE + domain + child + cs(len(tx)) + tx + cs(len(parent_branch))
            + b''.join(parent_branch) + bytes(4) + cs(len(aux_branch))
            + b''.join(aux_branch) + aux_index.to_bytes(4, 'little') + parent)


def fixture(parent_depth=0, aux_depth=0, nonce=0, research_id=7, domain=DOMAIN):
    parent_branch = tuple(bytes([i + 80]) * 32 for i in range(parent_depth))
    aux_branch = tuple(bytes([i + 120]) * 32 for i in range(aux_depth))
    index = slot(aux_depth, nonce, research_id)
    leaf = sha256d(LEAF_LABEL + domain + sha256d(CHILD))
    root = root_hash(leaf, aux_branch, index)
    script = MARKER + root[::-1] + (1 << aux_depth).to_bytes(4, 'little') + nonce.to_bytes(4, 'little')
    return envelope(make_tx(script), parent_branch, aux_branch, index, domain)


class ResearchTests(unittest.TestCase):
    def accepted(self, data):
        a, b = parse_a(data), parse_b(data)
        self.assertEqual(a, b)
        return a

    def rejected(self, data):
        for parser in (parse_a, parse_b):
            with self.subTest(parser=parser.__name__):
                with self.assertRaises(ValueError):
                    parser(data)

    def test_fixed_zero_branch_vector(self):
        raw = fixture()
        self.assertEqual(len(raw), 314)
        self.assertEqual(raw[117], 106)
        parsed = self.accepted(raw)
        self.assertEqual(parsed[0], DOMAIN)
        self.assertEqual(parsed[1], CHILD)
        self.assertEqual(len(parsed[2]), 106)
        self.assertEqual(parsed[4:8], ((), 0, (), 0))
        self.assertTrue(linked_model(parsed, DOMAIN, 7))
        self.assertEqual(sha256d(CHILD).hex(),
                         '852c98044fb00507122ff63bda7b529566348fc204f72b00dff1afd7b40501e4')
        self.assertEqual(sha256d(LEAF_LABEL + DOMAIN + sha256d(CHILD)).hex(),
                         'a16523acc3578eef2892e54a69b410378bfffa29a079b926b015d5d27c94d77a')
        self.assertEqual(sha256d(parsed[2]).hex(),
                         '351b305a551698238ec6de2203a256911d5bf87f3d99ad6d01e80d8a4a1b234f')
        self.assertEqual(sha256d(parsed[8]).hex(),
                         'b26fc616776149ef456ae89800c5934a05395f615ab4fa8b7ce1b9cc2036ed0f')
        self.assertEqual(sha256d(raw).hex(),
                         '3bc6dcddc5c6fac2435387a39bde62dedc135775b5b9bbd72177ec5eb6fabfe0')

    def test_independent_nonzero_branch_vector(self):
        raw = fixture(2, 3, 1)
        parsed = self.accepted(raw)
        self.assertEqual(len(raw), 474)
        self.assertEqual(parsed[7], 2)  # Independently derived slot; directions 0,1,0.
        leaf = sha256d(LEAF_LABEL + DOMAIN + sha256d(CHILD))
        expected = (
            '7a3d1e0367914a8ed1a6d83c05a0cae73f2c58575427622576ebcd4c859339f5',
            'd06c5c92076aecc60830852fd8f597e0cd76ff766f517d0725e1329950d15e6f',
            'df23f4b7fb2199275459196c7140e341095e2bb24475204bdcde7d7dccbd346b',
        )
        for depth, literal in enumerate(expected, 1):
            self.assertEqual(root_hash(leaf, parsed[6][:depth], 2).hex(), literal)
        self.assertEqual(sha256d(parsed[2]).hex(),
                         '24c99cd69a98a0e98a5c48518635b0f63c891038d05da86c8cbfbd8ddc60dc75')
        self.assertEqual(root_hash(sha256d(parsed[2]), parsed[4][:1], 0).hex(),
                         '59aaf40411d3442293c9e76511eaf295aec0780098f248ee545c44eafd7d5823')
        self.assertEqual(parsed[8][36:68].hex(),
                         '03f924df1ba7dc5b31f6164e566f92c74e9a9ddab2f1725ee137654cac4e18f3')
        self.assertEqual(sha256d(raw).hex(),
                         '5710dab227cd9ebf2e429830873afb47cafff39dc82bcba06abbb44eee9a96de')
        self.assertTrue(linked_model(parsed, DOMAIN, 7))

    def test_positive_depth_corpus(self):
        for parent_depth, aux_depth, nonce in ((0, 0, 0), (1, 1, 0), (2, 4, 1),
                                               (30, 30, 0xffffffff)):
            with self.subTest(parent=parent_depth, aux=aux_depth, nonce=nonce):
                self.assertTrue(linked_model(self.accepted(fixture(parent_depth, aux_depth, nonce)), DOMAIN, 7))

    def test_all_truncations_and_surplus(self):
        raw = fixture(2, 3, 1)
        for end in range(len(raw)):
            with self.subTest(end=end):
                self.rejected(raw[:end])
        self.rejected(raw + b'\x00')
        self.rejected(raw + raw)

    def test_profile_and_input_limits(self):
        raw = fixture()
        for bad in (bytearray(raw), None, 'AP79', bytes(MAX_PROOF + 1), b'',
                    b'FAIL' + raw[4:], raw[:4] + b'\x02' + raw[5:]):
            self.rejected(bad)

    def test_length_and_count_corpus(self):
        raw = fixture()
        # Fixed vector offsets: txlen117, parentcount224, parentindex225,
        # auxcount229, auxindex230, parentheader234.
        for position, original in ((117, 106), (224, 0), (229, 0)):
            for encoded in (b'\xfd' + original.to_bytes(2, 'little'),
                            b'\xfe' + original.to_bytes(4, 'little'),
                            b'\xff' + original.to_bytes(8, 'little')):
                self.rejected(raw[:position] + encoded + raw[position + 1:])
        for encoded in (cs(MAX_TX + 1), cs(65536), cs(1 << 32), b'\xff' + b'\xff' * 8):
            self.rejected(raw[:117] + encoded + raw[118:])
        for position in (224, 229):
            self.rejected(raw[:position] + cs(31) + raw[position + 1:])
            self.rejected(raw[:position] + b'\xff' + b'\xff' * 8 + raw[position + 1:])
        self.rejected(raw[:117] + b'\x69' + raw[118:])
        self.rejected(raw[:117] + b'\x6b' + raw[118:])
        self.rejected(raw[:225] + bytes.fromhex('01000000') + raw[229:])
        self.rejected(raw[:230] + bytes.fromhex('01000000') + raw[234:])

    def test_auxiliary_index_boundaries(self):
        tx = make_tx(b'')
        for index in (0, (1 << 30) - 1):
            raw = envelope(tx, aux_branch=(bytes(32),) * 30, aux_index=index)
            self.assertEqual(self.accepted(raw)[7], index)
        for index in (1 << 30, 0xffffffff):
            self.rejected(envelope(tx, aux_branch=(bytes(32),) * 30, aux_index=index))

    def test_coinbase_subset_rejections(self):
        good = parse_a(fixture())[2]
        cases = [good[:4] + b'\x00\x01' + good[5:],  # witness marker/flag
                 good[:4] + b'\x02' + good[5:],
                 good[:5] + b'\x01' + good[6:],
                 good[:37] + bytes(4) + good[41:],
                 good[:48] + b'\x00' + good[49:],
                 good + b'\x00']
        for raw in cases:
            self.rejected(envelope(raw))
        for size in (0, 1, 101):
            self.rejected(envelope(make_tx(b'', input_script=b'\x01' * size)))
        self.rejected(envelope(make_tx(b'\x01' * 1025)))
        self.rejected(envelope(make_tx(b'', outputs=((0, b''),) * 17)))
        # Nonminimal input-count, script-length, output-count and output-script length.
        for position in (4, 41, 48, 57):
            old = good[position]
            self.rejected(envelope(good[:position] + b'\xfd' + old.to_bytes(2, 'little') + good[position + 1:]))

    def test_canonical_compactsize_positive_and_bounds(self):
        # Canonical 253-byte script and a transaction-length fd prefix both decode.
        tx = make_tx(b'\x55' * 253)
        parsed = self.accepted(envelope(tx))
        self.assertEqual(parsed[3], ((0, b'\x55' * 253),))
        for size in (100,):
            self.accepted(envelope(make_tx(b'', input_script=b'\x01' * size)))
        self.accepted(envelope(make_tx(b'\x55' * 1024)))
        self.accepted(envelope(make_tx(b'', outputs=((0, b''),) * 16)))
        outputs = tuple((0, b'\x55' * size) for size in (1024, 1024, 1024, 927))
        boundary_tx = make_tx(b'', outputs=outputs)
        self.assertEqual(len(boundary_tx), 4096)
        maximal = envelope(boundary_tx, (bytes(32),) * 30, (bytes(32),) * 30)
        self.assertEqual(len(maximal), 6226)
        self.accepted(maximal)
        over_tx = make_tx(b'', outputs=outputs[:-1] + ((0, b'\x55' * 928),))
        self.assertEqual(len(over_tx), 4097)
        self.rejected(envelope(over_tx))

    def test_linkage_mutations_are_not_parse_failures(self):
        raw = fixture(1, 2, 1)
        parsed = self.accepted(raw)
        self.assertFalse(linked_model(parsed, DOMAIN[::-1], 7))
        for index, changed in ((0, DOMAIN[::-1]), (1, b'\xff' * 80),
                               (4, (b'\xff' * 32,)),
                               (6, (b'\xff' * 32,) * 2),
                               (8, parsed[8][:36] + bytes(32) + parsed[8][68:])):
            altered = list(parsed)
            altered[index] = changed
            self.assertFalse(linked_model(tuple(altered), DOMAIN, 7))
        self.assertFalse(linked_model(parsed, DOMAIN, 8))
        for invalid in (-1, 32768, True, None):
            with self.assertRaises(ValueError):
                linked_model(parsed, DOMAIN, invalid)

    def test_commitment_canonicality_and_endian(self):
        parsed = self.accepted(fixture())
        script = parsed[3][0][1]
        for bad in (script[4:], b'\x00' + script, script + b'\x00',
                    script[:4] + script[4:36][::-1] + script[36:],
                    script[:36] + bytes.fromhex('00000001') + script[40:]):
            self.assertFalse(linked_model(self.accepted(envelope(make_tx(bad))), DOMAIN, 7))
        duplicated = make_tx(script, outputs=((0, script), (0, script)))
        self.assertFalse(linked_model(self.accepted(envelope(duplicated)), DOMAIN, 7))
        paid = make_tx(script, outputs=((1, script),))
        self.assertFalse(linked_model(self.accepted(envelope(paid)), DOMAIN, 7))
        # At height1 changing nonce changes expected slot; at height0 it cannot.
        branched = self.accepted(fixture(aux_depth=1))
        changed_nonce = branched[3][0][1][:-4] + bytes.fromhex('01000000')
        changed = envelope(make_tx(changed_nonce), aux_branch=branched[6], aux_index=branched[7])
        self.assertFalse(linked_model(self.accepted(changed), DOMAIN, 7))

    def test_work_is_explicitly_uncovered(self):
        parsed = self.accepted(fixture())
        self.assertEqual(parsed[8][72:76], bytes(4))  # invalid/zero nBits
        self.assertTrue(linked_model(parsed, DOMAIN, 7))
        # Successful linkage with zero nBits proves this is NOT proof-of-work validation.

    def test_full_transaction_validity_is_uncovered(self):
        script = self.accepted(fixture())[3][0][1]
        tx = make_tx(script, outputs=((0, script), (0xffffffffffffffff, b'')))
        parsed = self.accepted(envelope(tx))
        self.assertEqual(parsed[3][1][0], 0xffffffffffffffff)
        self.assertTrue(linked_model(parsed, DOMAIN, 7))
        # Values are opaque uint64 fields here, not valid signed amounts/MoneyRange.

    def test_activation_boundary_table(self):
        # Hypothetical H=10 only; no actual ALUZ activation is proposed.
        rows = (
            (9, 'hybrid', True, False), (10, 'hybrid', True, True),
            (11, 'hybrid', True, True), (9, 'auxonly', True, False),
            (10, 'auxonly', False, True), (11, 'auxonly', False, True),
            (10, 'legacy', True, False),
        )
        for height, policy, legacy_ok, aux_ok in rows:
            self.assertEqual(activation_model(height, 10, policy, 'legacy', False, False), legacy_ok)
            self.assertEqual(activation_model(height, 10, policy, 'aux', True, True), aux_ok)
        self.assertFalse(activation_model(10, 10, 'hybrid', 'unknown', False, False))
        self.assertFalse(activation_model(10, 10, 'unknown', 'aux', True, True))
        self.assertFalse(activation_model(10, 10, 'hybrid', 'aux', True, True, False))
        for mode, flag, proof in (('legacy', True, True), ('legacy', False, True),
                                  ('aux', False, True), ('aux', True, False), ('aux', False, False)):
            self.assertFalse(activation_model(10, 10, 'hybrid', mode, flag, proof))
        # Re-evaluating the same predicates against branch-specific heights changes outcome.
        self.assertFalse(activation_model(9, 10, 'auxonly', 'aux', True, True))
        self.assertTrue(activation_model(10, 10, 'auxonly', 'aux', True, True))
        self.assertTrue(activation_model(0, 0, 'auxonly', 'aux', True, True))
        self.assertTrue(activation_model(0xffffffff, 0xffffffff, 'auxonly', 'aux', True, True))
        self.assertFalse(activation_model(0xfffffffe, 0xffffffff, 'auxonly', 'aux', True, True))
        for invalid in (-1, 1 << 32, True, None, 1.0):
            with self.assertRaises(ValueError):
                activation_model(invalid, 10, 'hybrid', 'aux', True, True)
            with self.assertRaises(ValueError):
                activation_model(10, invalid, 'hybrid', 'aux', True, True)
        with self.assertRaises(ValueError):
            activation_model(10, 10, 'hybrid', 'aux', 1, True)


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
