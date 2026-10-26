#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.
"""Bounded offline MAIN DAA model v1; synthetic timestamps, never PoW headers.

See doc/andaluzcoin-mining-sustainability.md for assumptions and interpretation.
Standard-library runner: no framework, thread, daemon, socket or file writes.
"""

import argparse
import io
import json
import math
import random
import statistics
import sys
import unittest

SPAN = 1209600
INTERVAL = 2016
LIMIT = int('000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff', 16)
GENESIS_BITS = 0x1e00ffff
SEEDS = tuple(range(27500, 27509))
HORIZON = 8 * INTERVAL


def decode(bits):
    """SetCompact + DeriveTarget range rules; noncanonical valid forms allowed."""
    if not isinstance(bits, int) or not 0 <= bits <= 0xffffffff:
        raise ValueError('nBits must be uint32')
    size, word = bits >> 24, bits & 0x7fffff
    if size <= 3:
        word >>= 8 * (3 - size)
        target = word
    else:
        target = word << (8 * (size - 3))
    overflow = word != 0 and (size > 34 or (word > 0xff and size > 33) or (word > 0xffff and size > 32))
    if (word and bits & 0x800000) or overflow or not 0 < target <= LIMIT:
        raise ValueError('invalid MAIN target')
    return target


def encode(target):
    """Unsigned GetCompact; discard low bytes, normalize sign bit."""
    if not isinstance(target, int) or not 0 < target <= LIMIT:
        raise ValueError('target outside MAIN range')
    size = (target.bit_length() + 7) // 8
    word = target << (8 * (3 - size)) if size <= 3 else target >> (8 * (size - 3))
    if word & 0x800000:
        word >>= 8
        size += 1
    return (size << 24) | word


REFERENCE = decode(GENESIS_BITS)


def next_bits(height, bits, first_time, last_time):
    """Required bits for next height; timestamps of its epoch's first/last blocks."""
    if height < 1:
        raise ValueError('next height must be positive')
    target = decode(bits)
    if height % INTERVAL:
        return bits
    bounded = max(SPAN // 4, min(SPAN * 4, last_time - first_time))
    # C++ multiplication is uint256; MAIN maximum product is below 2**256.
    assert LIMIT * (SPAN * 4) < 1 << 256
    adjusted = min(LIMIT, target * bounded // SPAN)
    # GetCompact(0) returns 0, even though DeriveTarget would reject it.
    return encode(adjusted) if adjusted else 0


def mean_interval(bits, rate):
    if not math.isfinite(rate) or rate < 0:
        raise ValueError('rate must be finite and nonnegative')
    return math.inf if rate == 0 else 600 * (REFERENCE / decode(bits)) / rate


# shock is the NEXT block height at which participation changes, before its wait.
# encode(powLimit) equals genesis bits; the near-limit case checks that identity.
# harder-loss90 starts hypothetically at 1/16 reference target and rate 16, then 1.6.
SCENARIOS = (
    ('baseline', 1, lambda h: 1.0, GENESIS_BITS),
    ('loss50', 1, lambda h: 0.5, GENESIS_BITS),
    ('loss90-start', 1, lambda h: 0.1, GENESIS_BITS),
    ('loss99', 1, lambda h: 0.01, GENESIS_BITS),
    ('loss90-middle', 1008, lambda h: 1.0 if h < 1008 else 0.1, GENESIS_BITS),
    ('loss90-end', 2015, lambda h: 1.0 if h < 2015 else 0.1, GENESIS_BITS),
    ('restore-partial', 1, lambda h: 0.1 if h < 3024 else 0.5, GENESIS_BITS),
    ('restore-full', 1, lambda h: 0.1 if h < 3024 else 1.0, GENESIS_BITS),
    ('gain3', 1, lambda h: 3.0, GENESIS_BITS),
    ('oscillate', 1, lambda h: 0.1 if ((h - 1) // 252) % 2 == 0 else 3.0, GENESIS_BITS),
    ('zero', 1, lambda h: 0.0, GENESIS_BITS),
    ('limit-loss99', 1, lambda h: 0.01, encode(LIMIT)),
    ('harder-loss90', 1, lambda h: 1.6, encode(REFERENCE // 16)),
)


def simulate(scenario, seed):
    """Run <=8 epochs; floor cumulative continuous arrival time for timestamps.

    Boundary records occur when parent is available (before boundary block wait).
    Recovery = first conditional mean in [480,720] after shock, not persistence.
    """
    name, shock, rate_at, bits = scenario
    rng = random.Random(seed)
    times = [0]
    elapsed = 0.0
    shock_time = None
    recovery = None
    boundaries = []
    before = None
    boundary_arrival = None
    for height in range(1, HORIZON + 1):
        if height == shock:
            shock_time = elapsed
            before = mean_interval(bits, rate_at(height))
        rate = rate_at(height)
        # No block, no clock advancement, no boundary computation on disappearance.
        if rate == 0:
            break
        old = bits
        bits = next_bits(height, bits, times[height - INTERVAL] if height % INTERVAL == 0 else 0, times[-1])
        mean = mean_interval(bits, rate)
        if height % INTERVAL == 0:
            boundaries.append((height, elapsed, bits, decode(bits) / REFERENCE,
                               REFERENCE / decode(bits), mean, decode(bits) / decode(old)))
        if height >= shock and recovery is None and 480 <= mean <= 720:
            recovery = (height - shock, elapsed - shock_time)
        elapsed += rng.expovariate(1 / mean)
        times.append(math.floor(elapsed))
        if height == INTERVAL:
            boundary_arrival = elapsed - shock_time
    return dict(name=name, seed=seed, blocks=len(times) - 1, elapsed=elapsed,
                remaining=INTERVAL - ((shock - 1) % INTERVAL) - 1,
                before=before, boundaries=boundaries, recovery=recovery,
                delay=None if not boundaries else boundaries[0][1] - shock_time,
                boundary_arrival=boundary_arrival)


def trial_summary(scenario):
    trials = [simulate(scenario, seed) for seed in SEEDS]
    delays = sorted(t['delay'] for t in trials if t['delay'] is not None)
    return trials, (None if not delays else (statistics.median(delays), delays[math.ceil(.9 * len(delays)) - 1]))


def check_mechanics():
    # Literal values independently derivable by byte shifts, including sign normalization.
    for bits, target in ((0x01010000, 1), (0x02008000, 128), (0x03012345, 0x12345),
                         (0x04123456, 0x12345600), (GENESIS_BITS, 65535 << 216),
                         (0x1e00abcd, 43981 << 216), (0x1d0fffff, 1048575 << 208)):
        assert decode(bits) == target
        assert encode(target) == bits
    assert decode(0x02000100) == 1  # valid noncanonical form, canonicalized on encoding
    assert encode(decode(0x02000100)) == 0x01010000
    assert encode(LIMIT) == 0x1e00ffff
    assert decode(encode(LIMIT)) < LIMIT
    assert encode(0x12345678) == 0x04123456
    for bits in (0, 0x01800001, 0x1e80ffff, 0x23000001, 0x22000100,
                 0x21010000, 0x1e010000, -1, 1 << 32):
        try:
            decode(bits)
        except ValueError:
            pass
        else:
            raise AssertionError(f'accepted invalid nBits {bits}')
    for target in (0, -1, LIMIT + 1):
        try:
            encode(target)
        except ValueError:
            pass
        else:
            raise AssertionError('accepted invalid target')
    for height in (1, 2015, 2017, 4031):
        assert next_bits(height, GENESIS_BITS, 0, 10**15) == GENESIS_BITS
    # Small exact integer examples: 400/4=100; 400*4=1600; floor(101/4)=25.
    for height in (2016, 4032):
        assert decode(next_bits(height, encode(400), 100, 100)) == 100
        assert decode(next_bits(height, encode(400), 100, 100 + 10**12)) == 1600
        assert decode(next_bits(height, encode(101), 0, SPAN // 4)) == 25
        assert decode(next_bits(height, encode(400), 0, SPAN * 3 // 2)) == 600
    # Genesis-first period at exactly 600-second timestamps: span=2015*600.
    # 65535*2015//2016 = 65502 (compact discards fractional mantissa).
    assert next_bits(2016, GENESIS_BITS, 0, 2015 * 600) == 0x1e00ffde
    assert next_bits(2016, encode(LIMIT), 0, 4 * SPAN) == 0x1e00ffff
    # Existing C++ trusted source vectors, independently exercised by pow_tests.
    for bits, span, expected in ((0x1d00ffff, 1022578, 0x1d00d86a),
                                 (0x1c05a3f4, 289434, 0x1c0168fd),
                                 (0x1c387f6f, 6058000, 0x1d00e1fd)):
        assert next_bits(2016, bits, 0, span) == expected
    assert mean_interval(GENESIS_BITS, .1) == 6000
    assert mean_interval(GENESIS_BITS, 3) == 200
    assert mean_interval(encode(REFERENCE // 2), 1) == 1200
    # Independent integer scale followed by compact byte truncation.
    assert decode(next_bits(2016, encode(123456), 0, SPAN // 3)) == 41152
    assert next_bits(4032, GENESIS_BITS, 2016 * 600, 4031 * 600) == 0x1e00ffde
    assert decode(encode(LIMIT)) == REFERENCE
    assert next_bits(2016, encode(1), 0, 0) == 0
    assert mean_interval(GENESIS_BITS, 0) == math.inf
    for rate in (-1, math.nan, math.inf):
        try:
            mean_interval(GENESIS_BITS, rate)
        except ValueError:
            pass
        else:
            raise AssertionError('accepted invalid relative rate')


class AndaluzPowSustainabilityTest(unittest.TestCase):
    def test_mechanics(self):
        check_mechanics()

    def test_scenarios(self):
        results = {}
        for scenario in SCENARIOS:
            trials, spread = trial_summary(scenario)
            representative = trials[0]
            assert representative == simulate(scenario, SEEDS[0])
            results[scenario[0]] = (trials, spread)
            for trial in trials:
                assert trial['blocks'] <= HORIZON
                assert all(b[0] == (i + 1) * INTERVAL for i, b in enumerate(trial['boundaries']))
                assert all(0 < decode(b[2]) <= LIMIT for b in trial['boundaries'])
        base = results['baseline'][1][0]
        assert results['loss90-start'][1][0] > base * 8
        assert results['gain3'][1][0] < base / 2
        assert results['loss90-start'][1][0] > results['loss90-middle'][1][0] > results['loss90-end'][1][0]
        for trial in results['zero'][0]:
            assert trial['blocks'] == 0 and not trial['boundaries']
            assert trial['elapsed'] == 0 and trial['delay'] is None and trial['recovery'] is None
        for trial in results['loss99'][0]:
            assert trial['boundaries'][0][6] <= 4
            assert trial['boundaries'][0][5] > 10000
        for trial in results['limit-loss99'][0]:
            assert all(b[2] == 0x1e00ffff for b in trial['boundaries'])
        for trial in results['harder-loss90'][0]:
            assert trial['boundaries'][0][6] == 4
            assert trial['boundaries'][0][5] == 1500
            assert trial['recovery'] is not None
        # Vanishing immediately before a boundary cannot create its new block.
        gone = simulate(('gone-at-boundary', 2016, lambda h: 1 if h < 2016 else 0, GENESIS_BITS), SEEDS[0])
        assert gone['blocks'] == 2015 and not gone['boundaries']
        for name, shock, rate_at, bits in SCENARIOS:
            for h, expected in ((3023, .1), (3024, .5 if name == 'restore-partial' else 1.0)):
                if name in ('restore-partial', 'restore-full'):
                    assert rate_at(h) == expected
        for trial in results['restore-full'][0]:
            assert trial['recovery'][0] == 3023
        for name in ('loss50', 'loss90-start', 'loss99', 'restore-partial', 'limit-loss99'):
            assert all(t['recovery'] is None for t in results[name][0])
        for trial in results['loss90-end'][0]:
            assert trial['remaining'] == 1
            assert trial['boundary_arrival'] > trial['delay']


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    for option in ('configfile', 'cachedir', 'tmpdir'):
        parser.add_argument('--' + option, help='Accepted runner metadata; unused (no files or nodes)')
    parser.add_argument('--portseed', type=int, help='Accepted runner metadata; model uses fixed SEEDS')
    parser.add_argument('--timeout-factor', type=float, help='Accepted CI runner metadata; unused for offline tests')
    for flag in ('v2transport', 'usecli', 'previous-releases'):
        parser.add_argument('--' + flag, action='store_true',
                            help='Accepted CI runner flag; unused for offline tests')
    parser.add_argument('--coveragedir',
                        help='Accepted RPC coverage path; unused for offline tests')
    parser.add_argument('--summary-json', action='store_true', help='After passing tests, print detailed JSON to stdout')
    args = parser.parse_args()
    if not __debug__:
        parser.error('optimized Python disables model assertions; run without -O')
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AndaluzPowSustainabilityTest)
    test_output = io.StringIO() if args.summary_json else sys.stdout
    result = unittest.TextTestRunner(stream=test_output, verbosity=2).run(suite)
    if not result.wasSuccessful():
        if args.summary_json:
            print(test_output.getvalue(), end="")
        return 1
    if args.summary_json:
        summaries = []
        for scenario in SCENARIOS:
            trials, spread = trial_summary(scenario)
            summaries.append(dict(scenario=scenario[0], seeds=SEEDS, horizon=HORIZON,
                                  decision_median_p90=spread, trials=trials))
        # JSON null represents the zero-miner infinite conditional mean.
        for summary in summaries:
            for trial in summary['trials']:
                if math.isinf(trial['before']):
                    trial['before'] = None
        print(json.dumps(summaries, indent=2, allow_nan=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
