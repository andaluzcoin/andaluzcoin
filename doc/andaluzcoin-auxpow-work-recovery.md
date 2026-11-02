# Mixed-mode difficulty, chainwork and pool-exit recovery research

## 1. Decision and scope

**v0.2.80 is research only; public economic mainnet remains NO-GO.**
All 21 [readiness gates](andaluzcoin-mainnet-readiness.md) remain unchecked.
No mainnet parameter, production code, wallet policy, ID, version bit,
serialization, proof format or activation is changed or selected.

This follows [issue #95](https://github.com/andaluzcoin/andaluzcoin/issues/95)
and the third [recorded research step](andaluzcoin-auxpow-candidate-specification.md#15-conclusions-sources-and-next-milestones).
Frozen ALUZ baseline is `092f9de32de2c7ca765ce7431daf907900d10dd9`, tagged
`v0.2.79-auxpow-proof-serialization-activation-research`.
The [R0 parser/activation study](andaluzcoin-auxpow-proof-serialization-activation.md)
and [encoding/domain study](andaluzcoin-auxpow-chainid-domain-compatibility.md)
leave real consensus integration blocked; this work does not bypass those gates.

Three evidence layers must remain separate:

1. **ALUZ CURRENT**: source-faithful compact target, mainnet retarget and
   per-child work arithmetic, corroborated with independent integer vectors.
2. **HYPOTHETICAL**: direct/auxiliary route predicates, abstract accepted-work
   accounting and branch/mode comparisons. ALUZ implements only direct work.
3. **SYNTHETIC**: normalized honest participation and exact expected-arrival
   fractions. No live hash rate, pool commitment or economic evidence is used.

The [offline stdlib test](../test/functional/feature_andaluz_auxpow_work_recovery.py)
contains no node, real header/proof, mining, socket, network, file access,
subprocess, random trial or live-chain data. Mathematical mode permission and
caller-supplied hash/linkage assumptions are not AuxPoW acceptance or a security audit.

## 2. Immutable source ledger

Every link below pins the same ALUZ baseline; no moving upstream behavior is
substituted for current ALUZ rules.

| Source | Verified behavior / evidence limit |
| --- | --- |
| [main parameters:98](https://github.com/andaluzcoin/andaluzcoin/blob/092f9de32de2c7ca765ce7431daf907900d10dd9/src/kernel/chainparams.cpp#L98), [genesis:139](https://github.com/andaluzcoin/andaluzcoin/blob/092f9de32de2c7ca765ce7431daf907900d10dd9/src/kernel/chainparams.cpp#L139) | powLimit `000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff`; spacing 600, timespan 1209600, no mainnet min-difficulty escape or BIP94 path; genesis bits `1e00ffff`. |
| [params.h:126](https://github.com/andaluzcoin/andaluzcoin/blob/092f9de32de2c7ca765ce7431daf907900d10dd9/src/consensus/params.h#L126), [pow.cpp:14-47](https://github.com/andaluzcoin/andaluzcoin/blob/092f9de32de2c7ca765ce7431daf907900d10dd9/src/pow.cpp#L14) | Interval 2016; ordinary next height retains parent bits. At a boundary select ancestor at lastheightâˆ’2015. Candidate timestamp does not enable mainnet fallback. |
| [pow.cpp:50-84](https://github.com/andaluzcoin/andaluzcoin/blob/092f9de32de2c7ca765ce7431daf907900d10dd9/src/pow.cpp#L50) | Clamp elapsed to 302400..4838400, multiply target, integer divide by 1209600, cap full powLimit, compact encode. Mainnet does not use the BIP94 first-block-target alternative. |
| [arith_uint256.cpp:48](https://github.com/andaluzcoin/andaluzcoin/blob/092f9de32de2c7ca765ce7431daf907900d10dd9/src/arith_uint256.cpp#L48), [compact:175-215](https://github.com/andaluzcoin/andaluzcoin/blob/092f9de32de2c7ca765ce7431daf907900d10dd9/src/arith_uint256.cpp#L175) | Production arithmetic is fixed 256-bit; compact conversion truncates and has sign/overflow rules. Prove the modeled valid domain cannot overflow before using unbounded Python integers. |
| [DeriveTarget:146-170](https://github.com/andaluzcoin/andaluzcoin/blob/092f9de32de2c7ca765ce7431daf907900d10dd9/src/pow.cpp#L146) | Reject negative, zero, overflowing or above-limit target; hash<=target is numerically valid. This helper alone does not require canonical re-encoding or contextual bits equality. |
| [chain.cpp:121-133](https://github.com/andaluzcoin/andaluzcoin/blob/092f9de32de2c7ca765ce7431daf907900d10dd9/src/chain.cpp#L121), [chain.h:301](https://github.com/andaluzcoin/andaluzcoin/blob/092f9de32de2c7ca765ce7431daf907900d10dd9/src/chain.h#L301) | Work from nBits is floor(2^256/(target+1)); GetBitsProof alone has no mainnet powLimit check. Validate target/context before accepted credit. |
| [blockstorage.cpp:224-250](https://github.com/andaluzcoin/andaluzcoin/blob/092f9de32de2c7ca765ce7431daf907900d10dd9/src/node/blockstorage.cpp#L224) | Child hash keys the block index; duplicate returns existing entry, new child adds its work once to parent chainwork. No auxiliary route exists today. |
| [work comparator:174-191](https://github.com/andaluzcoin/andaluzcoin/blob/092f9de32de2c7ca765ce7431daf907900d10dd9/src/node/blockstorage.cpp#L174) | Highest chainwork first, then local sequenceID/pointer ordering. Equal work is not a universal height-based tie-break. |
| [FindMostWorkChain:3142](https://github.com/andaluzcoin/andaluzcoin/blob/092f9de32de2c7ca765ce7431daf907900d10dd9/src/validation.cpp#L3142) | More work does not override known invalidity or missing block data. A candidate is not thereby fully valid. |
| [CheckBlockHeader:3860](https://github.com/andaluzcoin/andaluzcoin/blob/092f9de32de2c7ca765ce7431daf907900d10dd9/src/validation.cpp#L3860), [context:4112-4152](https://github.com/andaluzcoin/andaluzcoin/blob/092f9de32de2c7ca765ce7431daf907900d10dd9/src/validation.cpp#L4112) | Current direct child PoW plus exact GetNextWorkRequired bits, MTP/future-time/version gates. Numeric targets alone are insufficient. |

This is a focused source audit, not a complete historical consensus audit or
verification of all validation call paths, fuzz bypasses, disk state and caches.

## 3. Target arithmetic and endpoint specification

Let full limit `L=2^232âˆ’1`; let `T(bits)` be the decoded compact target.
`nBits` is compact **target encoding**, not CompactSize transaction framing.
The model accepts only uint32 bits with nonnegative, nonzero, nonoverflowing
decoded target<=L. Sign and overflow use the source's post-small-exponent
mantissa rules. Invalid-target intermediate Python magnitude need not equal
the production decoder's truncated storage; such cases reject using the flags.

At a retarget boundary:

`new_bits = Compact(min(L, floor(T(old_bits) * clamp(elapsed,302400,4838400) / 1209600)))`.

Order matters: multiply before division, then cap before compact truncation.
Compact truncates lower bytes, not rounding to nearest. The largest valid
multiply `L*4838400` occupies 255 bits, below 2^256; unbounded Python arithmetic
therefore agrees in this specific valid-mainnet multiplication domain.
Do not generalize that proof to other networks, larger limits or other formulas.

The first retarget candidate is height 2016, using timestamps at heights 0 and 2015.
At nominal 600-second spacing the elapsed input is **1209000**, not1209600:
2016 blocks contain2015 endpoint gaps. Candidate block time is not an endpoint.
At height 4032 the corresponding endpoints are2016 and 4031. The test rejects
missing/noncontiguous abstract ancestry instead of silently using a global tip.
Negative/zero elapsed arithmetic inputs clamp to the minimum; accepting such
a schedule in the helper does not prove MTP/future-time validity.

Numeric target validity differs from exact contextual bits: `02000100` and
canonical `01010000` both decode target 1, but a candidate with the former
cannot substitute for the latter when expected bits are the latter. The
model checks exact expected bits **before awarding any work**. The node has
additional gates omitted by this abstract model.

Encoding and acceptance are also separate at zero: a valid numerical target 1
retargeted at the quarter-span clamp truncates to 0, and source GetCompact
returns bits 0. The arithmetic model preserves this edge; numeric validation
then rejects zero and awards no work. It is not a new consensus rule or a
claim that this extreme target occurs on the observed chain.

## 4. Independent fixed integer vectors

An independent GCC13.3 C++17/Boost.Multiprecision reference, compiled with
`-Wall -Wextra -Werror -pedantic`, corroborated target decoding, work, retarget
and fixed-width safety. Source and full outputs are retained with the execution
report outside the production tree.

| Child nBits | Exact credited work | Role |
| --- | ---: | --- |
| 1e00ffff | 16777472 | Current genesis/compact-limit reference |
| 1d00ffff | 4295032833 | Hypothetical harder-target control |
| 1c7fffff | 8589935616 | Distinct hypothetical hard context |
| 1c3fffc0 | 17180131332 | Quarter-target result from 1d00ffff |
| 1d03fffc | 1073758208 | Four-times-target result from 1d00ffff |

| Starting bits | Elapsed input | Final bits |
| --- | ---: | --- |
| 1d00ffff | 0 or 302400 | 1c3fffc0 |
| 1d00ffff | 1209600 | 1d00ffff |
| 1d00ffff | 1209000 (2015 nominal gaps) | 1d00ffde |
| 1d00ffff | 4838400 or 6000000 | 1d03fffc |
| 1e00ffff | 0 or 302400 | 1d3fffc0 |
| 1e00ffff | 1209600,4838400 or 6000000 | 1e00ffff |
| 1e00ffff | 1209000 | 1e00ffde |

The endpoint result 1d00ffde credits 4297196676 work;1e00ffde credits 16785924.
Its effective decoded target is strictly below the raw retarget quotient due
to compact precision truncation, independently corroborated by the reference.

Fixed rejection examples include zero, `1e80ffff` (negative), `23000001`
(overflow), `1e010000` (one above full limit), `1f00ffff` (above limit without
overflow), and a small exponent/mantissa that decodes zero. Hash exactly equal
to the target passes the numeric predicate; one above rejects.

`T(1e00ffff)=65535*2^216`, while `L=2^232âˆ’1`. Both compact-encode to 1e00ffff.
The full-limit work would be16777216, **not**16777472; the current compact
target is slightly smaller. `L/Tâ‰ˆ1.0000152590218967` does not provide a new,
easier encoded target above the saturated reference.

## 5. Hypothetical mixed-mode credit and duplicate submissions

The model's mode policy is an external study input: before hypothetical H,
legacy only; after H, legacy/hybrid/auxiliary-only alternatives as previously
studied. Flag and proof booleans must agree with mode. An auxiliary route
also requires a caller-supplied true linkage predicate. Unknown/inconsistent
modes reject. No actual version-bit dispatch, proof parser or activation is used.

`candidate_credit` first requires exact contextual bits, validates the child
target, mode predicates and a supplied uint256 work-hash value<=child target.
For direct mode that value stands for a child hash; for auxiliary mode it
stands for parent work, **without computing or authenticating either hash**.
True linkage is an assumption, not evidence of valid commitments. All accepted
routes receive just `floor(2^256/(child_target+1))`.

- Direct versus auxiliary mode does not create a bonus.
- A work hash much lower than target does not create extra credited work.
- Parent nBits is opaque metadata, not the child target or a work multiplier.
  A malformed parent nBits can pass these abstract predicates; no full parent
  network/block/header validity is asserted.
- Alternative proofs/submissions for one already accepted synthetic child label
  are deduplicated; no second work increment. Conflicting credits reject.
- Separate child-chain ledgers are separate accounting contexts. A shared
  parent proof does not pool their chainwork into one ledger/security claim.

`accepted_work` consumes **already validated synthetic credits** and bounded
labels. Labels are not cryptographically authenticated child hashes, and the
helper is not a raw-input validator or proof of within-chain replay safety.
It does not reconstruct real header identity, ancestry or proof commitments.
Likewise, target-context inputs for the shorter/heavier example below are
assumed valid in their own histories; a block author cannot select harder
bits arbitrarily to inflate accepted work.

The study guards cumulative sums above UINT256_MAX instead of modeling native
wraparound; that refusal is a research boundary, not a new consensus rule.
All reported branch totals remain far below that bound. Current per-child
increment arithmetic is source-derived; this is not a full block-index simulator.

## 6. Synthetic forks and branch-specific context

Exclude a common ancestor equally from these independently fixed comparisons:

| Branch suffix | Children | Added work | Abstract result |
| --- | ---: | ---: | --- |
| Three children at 1d00ffff | 3 | 12885098499 | Less work despite greater count |
| Two children at 1c7fffff | 2 | 17179871232 | Greater work by 4294772733 |
| Equal-work alternatives | Any represented suffix | Equal | Model reports tie; no invented production tie-break |

An invalid high-work candidate rejected by expected-bits equality adds **zero**
work; a favorable work total does not override invalidity. Actual block-data,
transaction, script, MTP, future-time, ancestry, deployment and cache gates are
not evaluated here. Work comparison is only one part of real candidate handling.

Two trusted synthetic 2016-record timestamp histories illustrate retarget context:
fast elapsed 302400 yields 1c3fffc0; slow elapsed 4838400 yields 1d03fffc. Each
branch derives its own next expected bits. A candidate using the fast branch's
bits in the slow branch rejects, even if its supplied hash is numerically tiny.
Historical records are scenario inputs, not mined or fully validated headers.

At an illustrative H=2016, auxiliary-only mode is permitted at candidate
height 2016, but not on a pre-boundary candidate at 2015; legacy permissions
reverse accordingly. This demonstrates why a tip-global mode flag cannot be
reused across branch contexts. It is **not** an actual reorg, node activation,
rollback, persistence, chain-selection or old-node compatibility test. No real
ALUZ activation at 2016 is proposed. `next_bits` also assumes supplied history
is already valid except for its explicit shape/numeric checks; it does not
validate every historical expected target or contextual timestamp.

## 7. Exact synthetic participation and arrival expectations

Assume a normalized honest-work reference that would produce a 600-second
mean at reference target `T0`. No observed ALUZ hash rate is asserted. A
fraction `q` of that reference participates and submits valid child commitments.
For uniform independent work hashes and current target `T`:

`E[seconds] = 600 * (T0+1)/(T+1) / q`, for q>0.

This uses exact `Fraction` probability arithmetic, not a ratio of floored
chainwork credits. At q=0 the result is **no finite arrival expectation**,
represented by None, not a zero-second wait, capped timeout or recovery block.
No stochastic simulation or adversarial fork probability is claimed.

Let direct and auxiliary reference weights d+a=1 and remaining supply factors
rd,ra in 0..1. Under hypothetical policies, participating q is d*rd for legacy,
d*rd+a*ra for hybrid, or a*ra for auxiliary-only. Parent-chain hash rate counts
only under the stated assumption of constructing and submitting valid child
commitments. More validating nodes alone do not supply mining work.

| Scenario at reference target | q | Exact expected seconds |
| --- | --- | ---: |
| Baseline | 1 | 600 |
| 50% total work loss | 1/2 | 1200 |
| 90% total work loss | 1/10 | 6000 |
| 99% total work loss | 1/100 | 60000 |
| d=1/10,a=9/10 hybrid, all auxiliary supply exits | 1/10 | 6000 |
| Same weights, auxiliary-only after all auxiliary exits | 0 | No finite expectation |
| Same weights, legacy-only before/after auxiliary exit | 1/10 | 6000 |
| Same weights, auxiliary-only before exit | 9/10 | 2000/3 |
| Same weights, hybrid with 1% auxiliary supply remaining | 109/1000 | 600000/109 |
| No auxiliary participants, auxiliary-only | 0 | No finite expectation |

These are conditional mathematical expectations, not measured intervals,
guaranteed production, pool promises, profitability, decentralization or
security-budget evidence. They omit variance, latency, fees, payout incentives,
withholding, censorship, correlated exits, adversarial strategies and reorg risk.

## 8. Saturation versus a harder-target control

At the actual genesis/compact-limit reference, a slow epoch's retarget is
capped/recompacted back to 1e00ffff. Thus the listed 1200/6000/60000-second
post-loss expectations remain unchanged even after a clamped slow retarget.
Wall time alone does not lower mainnet difficulty: an ordinary next block
keeps its prior bits even with a far-future candidate timestamp in this helper.
That timestamp is not claimed valid under omitted node time checks.
If nobody produces a block, the next height/retarget boundary cannot advance.
AuxPoW mode labels alone cannot restore unavailable or unwilling participants.

The expressly hypothetical harder reference 1d00ffff illustrates a different
case. A maximum clamped easing gives1d03fffc, a fourfold numeric target.
With q=1/4 relative to that harder reference, the exact expectation is slightly
**above 600 seconds**, because `(T0+1)/(4*T0+1)` is not exactly 1/4. At q=1/100
after only that single easing it remains slightly above 15000 seconds. This
control demonstrates retarget limits/quantization; it is not a proposal to
reset ALUZ difficulty or a complete recovery simulation across future epochs.
The independent reference gives exact forms `600+1800/D` and `15000+45000/D`,
where `D=4*T0+1`; the tests pin that denominator and both expressions.

## 9. Bounds, reproduction and evidence limits

Model history/submission tuples are limited to 8192 records, synthetic labels
to 64 characters, and normalized Fraction inputs to 64-bit numerator/denominator.
Heights/timestamps/bits and work values use explicit uint32/uint256 study
domains; booleans are not silently accepted as integers. These are research
resource guards, not network limits. All loops are bounded; supplied history
and credits carry the trust preconditions described above.

The committed test covers fixed arithmetic vectors, exact target/hash equality
and failures, contextual bits before credit, duplicate submissions, work/fork
comparisons, branch-specific boundaries, no wall-clock escape and exact-rational
exit/control scenarios. It does not import previous toy tests as validation
dependencies; those run separately as regressions.

```sh
python3 test/functional/feature_andaluz_auxpow_work_recovery.py
build/test/functional/test_runner.py --jobs=1 feature_andaluz_auxpow_work_recovery.py
build/test/functional/test_runner.py --jobs=1 --timeout-factor=40 feature_andaluz_auxpow_work_recovery.py
build/test/functional/test_runner.py --jobs=1 --timeout-factor=40 --v2transport --usecli feature_andaluz_auxpow_work_recovery.py
build/test/functional/test_runner.py --jobs=1 --timeout-factor=40 --previous-releases feature_andaluz_auxpow_work_recovery.py
build/test/functional/test_runner.py --jobs=1 feature_andaluz_auxpow_work_recovery.py feature_andaluz_auxpow_serialization.py feature_andaluz_auxpow_chainid_domain.py feature_andaluz_auxpow_chainid_spec.py feature_andaluz_auxpow_feasibility.py
build/bin/test_bitcoin --run_test=pow_tests --log_level=test_suite
```

Regenerate the new script link with `cmake -S . -B build` if needed. The child
accepts only enumerated runner metadata without opening metadata paths;
unknown/abbreviated/invalid options and optimized Python reject. Failed tests
exit nonzero and successful child output is stdout. The issue/PR report records
fresh tests, negative/injected-failure checks, links/whitespace, independent
reference source/results, CI revision and skipped/unavailable checks. Commands
here are reproduction instructions, not multi-platform pass claims.

## 10. Decision log and remaining production gates

| Unresolved area | Evidence from this study | Still required |
| --- | --- | --- |
| Child work / mixed modes | Once-only target-based arithmetic and hypothetical route predicates | Real header identity, target context and complete proof validation; no ID/bit/layout inferred. |
| Fork / activation | Branch-local arithmetic and symbolic mode-boundary counterexamples | Node transition/reorg/cache/rollback and old-node tests under an owner-reviewed actual design. |
| Pool-exit recovery | Exact conditional expectations and saturated-limit finding | Independent participation, long-running valid block production and separately authorized operational evidence. |
| Security and incentives | Explicit exclusions, no security guarantee | Independent threat, concentration, censorship, attack-cost and economic review. |
| Resource / validity | Bounded offline arithmetic, not a full validator | Real parser/transport/validation DoS review, fuzzing and integration-specific security audit. |

The owner's standing approval covers routine research releases after required
checks and technical review pass. It does not resolve these critical production
choices. Actual consensus/ID/activation changes, deployment or outreach need
separate owner review. All 21 readiness gates remain unchecked; mainnet NO-GO.
