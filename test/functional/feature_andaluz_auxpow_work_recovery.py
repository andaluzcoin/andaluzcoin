#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying COPYING.
"""Offline target/work, hypothetical mode and synthetic participation research.

No real headers, AuxPoW proofs, mining, node activation, reorg or live hash rate.
Current ALUZ baseline: 092f9de32de2c7ca765ce7431daf907900d10dd9.
Literal integer vectors independently corroborated with C++17/Boost.
"""
import argparse
from fractions import Fraction
import math
import sys
import unittest


LIMIT = (1 << 232) - 1
UINT32 = (1 << 32) - 1
UINT256 = (1 << 256) - 1
SPAN = 1209600
SPACING = 600
INTERVAL = 2016
GENESIS_BITS = 0x1e00ffff
EASY = 0x1d00ffff
HARD = 0x1c7fffff
MAX_RECORDS = 8192  # Research resource guard, not a consensus limit.
WORK_VECTORS = ((GENESIS_BITS, 16777472), (EASY, 4295032833), (HARD, 8589935616))
RETARGET_VECTORS = (
    (EASY, 0, 0x1c3fffc0), (EASY, 302400, 0x1c3fffc0),
    (EASY, SPAN, EASY), (EASY, 4838400, 0x1d03fffc),
    (EASY, 6000000, 0x1d03fffc),
    (EASY, 1209000, 0x1d00ffde),
    (GENESIS_BITS, 0, 0x1d3fffc0), (GENESIS_BITS, 302400, 0x1d3fffc0),
    (GENESIS_BITS, SPAN, GENESIS_BITS),
    (GENESIS_BITS, 4838400, GENESIS_BITS), (GENESIS_BITS, 6000000, GENESIS_BITS),
    (GENESIS_BITS, 1209000, 0x1e00ffde),
)


def integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError('integer outside research domain')
    return value


def target(bits):
    integer(bits, 0, UINT32)
    size, word = bits >> 24, bits & 0x007fffff
    if size <= 3:
        word >>= 8 * (3 - size)
        value = word
    else:
        value = word << (8 * (size - 3))
    negative = word != 0 and bool(bits & 0x00800000)
    overflow = word != 0 and (size > 34 or (word > 0xff and size > 33)
                              or (word > 0xffff and size > 32))
    if negative or overflow or value == 0 or value > LIMIT:
        raise ValueError('invalid mainnet numeric target')
    return value


def compact(value):
    integer(value, 0, UINT256)
    size = (value.bit_length() + 7) // 8
    word = value << (8 * (3 - size)) if size <= 3 else value >> (8 * (size - 3))
    if word & 0x00800000:
        word >>= 8
        size += 1
    return (size << 24) | word


def block_work(bits):
    # Numeric mainnet target validation is intentionally separate from bits context.
    return (1 << 256) // (target(bits) + 1)


def retarget(bits, elapsed):
    integer(elapsed, -UINT32, UINT32)
    old = target(bits)
    bounded = max(SPAN // 4, min(elapsed, SPAN * 4))
    product = old * bounded
    if product > UINT256:
        raise ValueError('research multiply overflow guard')
    return compact(min(product // SPAN, LIMIT))


def next_bits(history, candidate_time):
    """Current mainnet arithmetic on trusted abstract ancestry, not a validator."""
    integer(candidate_time, 0, UINT32)
    if type(history) is not tuple or not 1 <= len(history) <= MAX_RECORDS:
        raise ValueError('bounded tuple ancestry required')
    previous = None
    for row in history:
        if type(row) is not tuple or len(row) != 3:
            raise ValueError('height/time/bits triple required')
        height, timestamp, bits = row
        integer(height, 0, UINT32)
        integer(timestamp, 0, UINT32)
        target(bits)
        if previous is not None and height != previous + 1:
            raise ValueError('noncontiguous ancestry')
        previous = height
    height, timestamp, bits = history[-1]
    if height == UINT32:
        raise ValueError('study height overflow')
    if (height + 1) % INTERVAL:
        return bits  # Mainnet has no candidate-time min-difficulty escape.
    if len(history) < INTERVAL:
        raise ValueError('missing retarget ancestry')
    return retarget(bits, timestamp - history[-INTERVAL][1])


def mode_allowed(height, boundary, policy, mode, flag, proof):
    integer(height, 0, UINT32)
    integer(boundary, 0, UINT32)
    if type(flag) is not bool or type(proof) is not bool:
        raise ValueError('boolean route predicates required')
    if policy not in ('legacy', 'hybrid', 'auxonly') or mode not in ('legacy', 'aux'):
        return False
    if flag != proof or flag != (mode == 'aux'):
        return False
    allowed = ('legacy',) if height < boundary or policy == 'legacy' else (
        ('legacy', 'aux') if policy == 'hybrid' else ('aux',))
    return mode in allowed


def candidate_credit(bits, expected_bits, mode, work_hash, *, height=10, boundary=10,
                     policy='hybrid', flag=False, proof=False, linked=True, parent_bits=0):
    """Hypothetical route predicates; supplied hash/linkage/context are assumptions."""
    integer(bits, 0, UINT32)
    integer(expected_bits, 0, UINT32)
    if bits != expected_bits:
        raise ValueError('contextually unexpected bits')
    numeric_target = target(bits)
    integer(work_hash, 0, UINT256)
    integer(parent_bits, 0, UINT32)  # Opaque metadata, not the child target.
    if type(linked) is not bool:
        raise ValueError('boolean synthetic linkage predicate required')
    if not mode_allowed(height, boundary, policy, mode, flag, proof):
        raise ValueError('hypothetical mode rejected')
    if mode == 'aux' and not linked:
        raise ValueError('assumed auxiliary linkage rejected')
    if work_hash > numeric_target:
        raise ValueError('hash exceeds child target')
    return block_work(bits)


def accepted_work(submissions):
    """Once-only accounting of already validated synthetic child credits."""
    if type(submissions) is not tuple or len(submissions) > MAX_RECORDS:
        raise ValueError('bounded submission tuple required')
    seen = {}
    for row in submissions:
        if type(row) is not tuple or len(row) != 2:
            raise ValueError('child-label/credit pair required')
        label, work = row
        if type(label) is not str or not 1 <= len(label) <= 64:
            raise ValueError('bounded synthetic label required')
        integer(work, 1, UINT256)
        if label in seen and seen[label] != work:
            raise ValueError('conflicting credit for one synthetic child')
        seen[label] = work
    total = sum(seen.values())
    if total > UINT256:
        raise ValueError('research chainwork overflow guard')
    return total


def prefer(left, right):
    integer(left, 0, UINT256)
    integer(right, 0, UINT256)
    return None if left == right else ('left' if left > right else 'right')


def fraction(value):
    if type(value) is not Fraction or not 0 <= value <= 1:
        raise ValueError('exact normalized Fraction required')
    if value.numerator.bit_length() > 64 or value.denominator.bit_length() > 64:
        raise ValueError('research fraction bound')
    return value


def participating(direct, auxiliary, direct_remaining, aux_remaining, policy):
    for value in (direct, auxiliary, direct_remaining, aux_remaining):
        fraction(value)
    if direct + auxiliary != 1 or policy not in ('legacy', 'hybrid', 'auxonly'):
        raise ValueError('normalized weights and known hypothetical policy required')
    d, a = direct * direct_remaining, auxiliary * aux_remaining
    return d if policy == 'legacy' else (a if policy == 'auxonly' else d + a)


def expected_seconds(participation, bits=GENESIS_BITS, reference_bits=GENESIS_BITS):
    fraction(participation)
    current, reference = target(bits), target(reference_bits)
    if participation == 0:
        return None  # No finite honest arrival expectation, not a recovery timeout.
    return Fraction(SPACING * (reference + 1), current + 1) / participation


def epoch(elapsed, bits=EASY):
    # Synthetic trusted timestamp records, not mined/validated blocks.
    return tuple((height, height * elapsed // (INTERVAL - 1), bits) for height in range(INTERVAL))


class ResearchTests(unittest.TestCase):
    def test_independent_target_and_work_vectors(self):
        self.assertEqual(LIMIT, int('000000' + 'ff' * 29, 16))
        self.assertEqual(target(GENESIS_BITS), 65535 << 216)
        for bits, work in WORK_VECTORS:
            self.assertEqual(block_work(bits), work)
            self.assertEqual(compact(target(bits)), bits)
        self.assertEqual(block_work(0x1c3fffc0), 17180131332)
        self.assertEqual(block_work(0x1d03fffc), 1073758208)

    def test_numeric_target_and_hash_boundaries(self):
        for bits in (0, 0x1e80ffff, 0x23000001, 0x1e010000, 0x1f00ffff, 0x01000001):
            with self.subTest(bits=hex(bits)):
                with self.assertRaises(ValueError):
                    target(bits)
        for bad in (-1, 1 << 32, True, None, 1.0):
            with self.assertRaises(ValueError):
                target(bad)
        self.assertEqual(candidate_credit(EASY, EASY, 'legacy', target(EASY)), 4295032833)
        with self.assertRaises(ValueError):
            candidate_credit(EASY, EASY, 'legacy', target(EASY) + 1)
        # Numeric helper permits equal targets encoded differently; context is exact bits.
        self.assertEqual(target(0x02000100), target(0x01010000))
        with self.assertRaises(ValueError):
            candidate_credit(0x02000100, 0x01010000, 'legacy', 0)

    def test_independent_retarget_vectors(self):
        for old, elapsed, expected in RETARGET_VECTORS:
            with self.subTest(old=hex(old), elapsed=elapsed):
                self.assertEqual(retarget(old, elapsed), expected)
        self.assertEqual(retarget(EASY, -1), retarget(EASY, 302400))
        self.assertEqual((LIMIT * (SPAN * 4)).bit_length(), 255)
        self.assertLessEqual(LIMIT * (SPAN * 4), UINT256)
        for bad in (True, None, 1.0, UINT32 + 1):
            with self.assertRaises(ValueError):
                retarget(EASY, bad)

    def test_epoch_endpoint_and_no_wall_clock_escape(self):
        records = epoch(2015 * 600)
        self.assertEqual(records[-1][1] - records[0][1], 1209000)
        self.assertEqual(next_bits(records, 1209600), retarget(EASY, 1209000))
        self.assertEqual(next_bits(records, 1209600), 0x1d00ffde)
        self.assertEqual(block_work(0x1d00ffde), 4297196676)
        self.assertEqual(block_work(0x1e00ffde), 16785924)
        self.assertNotEqual(next_bits(records, 1209600), EASY)
        ordinary = ((12, 7200, GENESIS_BITS),)
        self.assertEqual(next_bits(ordinary, 7201), GENESIS_BITS)
        self.assertEqual(next_bits(ordinary, UINT32), GENESIS_BITS)
        with self.assertRaises(ValueError):
            next_bits(((2015, 1209000, EASY),), 1209600)
        with self.assertRaises(ValueError):
            next_bits(((1, 0, EASY), (3, 1, EASY)), 2)

    def test_retarget_underflow_and_compact_truncation(self):
        self.assertEqual(compact(0), 0)
        self.assertEqual(block_work(0x01010000), 1 << 255)
        self.assertEqual(retarget(0x01010000, 302400), 0)
        with self.assertRaises(ValueError):
            candidate_credit(0, 0, 'legacy', 0)
        raw = target(EASY) * 1209000 // SPAN
        effective = target(0x1d00ffde)
        self.assertEqual(effective,
                         26945959878413409543308697848967893194344791167682687052265147072512)
        self.assertLess(effective, raw)

    def test_once_only_work_and_opaque_parent_difficulty(self):
        direct = candidate_credit(EASY, EASY, 'legacy', 0)
        aux = candidate_credit(EASY, EASY, 'aux', target(EASY), flag=True, proof=True)
        self.assertEqual(direct, aux)
        for parent_bits in (0, HARD, EASY, GENESIS_BITS, UINT32):
            self.assertEqual(candidate_credit(EASY, EASY, 'aux', 1, flag=True, proof=True,
                                             parent_bits=parent_bits), direct)
        # Alternative proof submissions for one child do not add work.
        self.assertEqual(accepted_work((('childA', aux),) * 3), direct)
        self.assertEqual(accepted_work((('childA', aux), ('childB', direct))), 2 * direct)
        with self.assertRaises(ValueError):
            accepted_work((('childA', direct), ('childA', block_work(HARD))))
        # Separate child-chain ledgers are not summed into one security/work claim.
        self.assertEqual(accepted_work((('chainA-child', aux),)),
                         accepted_work((('chainB-child', aux),)))

    def test_context_precedes_high_work_credit(self):
        self.assertGreater(block_work(HARD), block_work(EASY))
        accepted = []
        with self.assertRaises(ValueError):
            accepted.append(('bad', candidate_credit(HARD, EASY, 'legacy', 0)))
        self.assertEqual(accepted_work(tuple(accepted)), 0)
        # The same synthetic hash meets two numeric targets, only in permitted contexts.
        self.assertEqual(candidate_credit(EASY, EASY, 'legacy', 1), 4295032833)
        self.assertEqual(candidate_credit(HARD, HARD, 'legacy', 1), 8589935616)
        with self.assertRaises(ValueError):
            candidate_credit(EASY, EASY, 'aux', 0, flag=True, proof=True, linked=False)

    def test_fork_work_and_equal_work_tie(self):
        # Separate hypothetically valid target contexts; no author-selected difficulty.
        longer = accepted_work(tuple((str(i), block_work(EASY)) for i in range(3)))
        shorter = accepted_work(tuple((str(i), block_work(HARD)) for i in range(2)))
        self.assertEqual(longer, 12885098499)
        self.assertEqual(shorter, 17179871232)
        self.assertEqual(prefer(longer, shorter), 'right')
        self.assertIsNone(prefer(longer, longer))
        with self.assertRaises(ValueError):
            accepted_work((('a', 1 << 255), ('b', 1 << 255)))

    def test_branch_specific_retarget_and_mode_context(self):
        fast, slow = epoch(302400), epoch(4838400)
        fast_bits, slow_bits = next_bits(fast, 302401), next_bits(slow, 4838401)
        self.assertEqual((fast_bits, slow_bits), (0x1c3fffc0, 0x1d03fffc))
        self.assertGreater(candidate_credit(fast_bits, fast_bits, 'aux', 0, height=2016,
                                           boundary=2016, policy='auxonly', flag=True, proof=True), 0)
        with self.assertRaises(ValueError):
            candidate_credit(fast_bits, slow_bits, 'aux', 0, height=2016,
                             boundary=2016, policy='auxonly', flag=True, proof=True)
        # A synthetic reorg to a pre-boundary branch must not reuse tip-global mode.
        self.assertTrue(mode_allowed(2016, 2016, 'auxonly', 'aux', True, True))
        self.assertFalse(mode_allowed(2015, 2016, 'auxonly', 'aux', True, True))
        self.assertTrue(mode_allowed(2015, 2016, 'auxonly', 'legacy', False, False))
        self.assertFalse(mode_allowed(2016, 2016, 'auxonly', 'legacy', False, False))
        for mode, flag, proof in (('unknown', False, False), ('aux', False, True), ('legacy', True, True)):
            with self.assertRaises(ValueError):
                candidate_credit(EASY, EASY, mode, 0, flag=flag, proof=proof)

    def test_saturated_loss_and_total_disappearance(self):
        for participation, seconds in ((Fraction(1), 600), (Fraction(1, 2), 1200),
                                       (Fraction(1, 10), 6000), (Fraction(1, 100), 60000)):
            self.assertEqual(expected_seconds(participation), seconds)
            capped = retarget(GENESIS_BITS, SPAN * 4)
            self.assertEqual(capped, GENESIS_BITS)
            self.assertEqual(expected_seconds(participation, capped), seconds)
        self.assertIsNone(expected_seconds(Fraction(0)))
        self.assertEqual(compact(LIMIT), GENESIS_BITS)
        self.assertGreater(LIMIT, target(GENESIS_BITS))

    def test_pool_exit_by_hypothetical_mode(self):
        d, a = Fraction(1, 10), Fraction(9, 10)
        self.assertEqual(participating(d, a, Fraction(1), Fraction(1), 'hybrid'), 1)
        exit_aux = participating(d, a, Fraction(1), Fraction(0), 'hybrid')
        self.assertEqual(expected_seconds(exit_aux), 6000)
        self.assertIsNone(expected_seconds(participating(d, a, Fraction(1), Fraction(0), 'auxonly')))
        self.assertEqual(expected_seconds(participating(d, a, Fraction(1), Fraction(1), 'legacy')), 6000)
        self.assertEqual(expected_seconds(participating(d, a, Fraction(1), Fraction(1), 'auxonly')), Fraction(2000, 3))
        partial = participating(d, a, Fraction(1), Fraction(1, 100), 'hybrid')
        self.assertEqual(partial, Fraction(109, 1000))
        self.assertEqual(expected_seconds(partial), Fraction(600000, 109))
        self.assertIsNone(expected_seconds(participating(Fraction(1), Fraction(0),
                                                       Fraction(1), Fraction(1), 'auxonly')))

    def test_harder_target_control_and_quantized_recovery(self):
        eased = retarget(EASY, SPAN * 4)
        actual = expected_seconds(Fraction(1, 4), eased, EASY)
        exact = Fraction(600 * 4 * (target(EASY) + 1), target(eased) + 1)
        self.assertEqual(actual, exact)
        denominator = 107838141164045237972625905378895965344043594954296656344551092387841
        self.assertEqual(actual, 600 + Fraction(1800, denominator))
        self.assertGreater(actual, 600)  # Exact +1 probability, not floored work ratio.
        self.assertLess(actual, 601)
        severe = expected_seconds(Fraction(1, 100), eased, EASY)
        self.assertEqual(severe, 15000 + Fraction(45000, denominator))
        self.assertGreater(severe, 15000)
        self.assertLess(severe, 15001)
        self.assertNotEqual(eased, GENESIS_BITS)

    def test_model_input_bounds(self):
        for bad in (0.5, True, None, Fraction(-1), Fraction(2), Fraction(1, 1 << 65)):
            with self.assertRaises(ValueError):
                expected_seconds(bad)
        with self.assertRaises(ValueError):
            participating(Fraction(1), Fraction(1), Fraction(1), Fraction(1), 'hybrid')
        with self.assertRaises(ValueError):
            next_bits(((0, 0, EASY),) * (MAX_RECORDS + 1), 1)
        with self.assertRaises(ValueError):
            accepted_work((('x', 1),) * (MAX_RECORDS + 1))
        with self.assertRaises(ValueError):
            candidate_credit(EASY, EASY, 'legacy', True)


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
