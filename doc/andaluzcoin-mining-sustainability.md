# Andaluzcoin mining sustainability research

## 1. Executive summary

**Research only; public economic mainnet remains NO-GO.** This milestone changes no
consensus rules and authorizes no launch. Simulated intervals establish neither
real hash rate nor attack resistance. All 21 gates in the
[readiness checklist](andaluzcoin-mainnet-readiness.md) remain unchecked.

The confirmed risk has two parts: difficulty changes require blocks, and the
actual genesis target already saturates the maximum representable MAIN target.
The full integers differ: `powLimit = 2^232 - 1`, while
`reference_target = 65535 * 2^216`. Their ratio is approximately
`1.0000152590218967`; **both encode to `0x1e00ffff`**. This explicitly supersedes
the preliminary, incorrect approximately 256× headroom assumption. The simulator's
initial above-limit regression vector exposed that mistake; source arithmetic
and subsequent checks confirm the correction.

At the normalized genesis baseline, sustained 50%, 90% and 99% losses imply
conditional means of 20, 100 and 1000 minutes, respectively, even after retargets.
Changing DAA alone while preserving this limit cannot restore ten-minute means
at those rates. A faster DAA might help when difficulty previously increased;
this is a separate design question. Zero miners produce no blocks under any DAA.

## 2. Source-verified current MAIN rules

Baseline commit `3ffd48fe6c5c6ccb9dcb223407de3d7f539c8ebc`, tag
`v0.2.74-mainnet-readiness-documentation-identity`; inspected 2026-10-25.
Repository source is authoritative for ALUZ; third-party precedents are not rules
for this chain. See also the [chain specification](chain-spec.md).

| Fact | Source location at baseline |
| --- | --- |
| Header hash is double SHA256 (SHA256d) | [block.cpp](../src/primitives/block.cpp), `CBlockHeader::GetHash`, lines 15–17; [hash.h](../src/hash.h), `HashWriter::GetHash`, lines 109–121 |
| 600-second spacing; 1,209,600-second / 14-day timespan | [chainparams.cpp](../src/kernel/chainparams.cpp), `CMainParams`, lines 108–114 |
| 2016-block interval | [params.h](../src/consensus/params.h), `DifficultyAdjustmentInterval`, line 126 |
| No minimum-difficulty exception; retarget enabled; BIP94 false | `CMainParams`, lines 111–114 |
| powLimit `000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff`; genesis nBits `0x1e00ffff`; subsidy halving 210000 | `CMainParams`, lines 90, 108 and 146–155 |
| Boundary ancestor selection and clamp/scaling | [pow.cpp](../src/pow.cpp), `GetNextWorkRequired`, lines 14–48; `CalculateNextWorkRequired`, lines 50–85 |
| Negative, zero, overflow and above-limit rejection | `DeriveTarget` in pow.cpp, lines 147–163 |
| Compact sign, overflow and rounding; bounded multiplication | [arith_uint256.cpp](../src/arith_uint256.cpp), `SetCompact`/`GetCompact`, lines 175–219; multiplication lines 47–57 |

Off-boundary MAIN blocks retain previous nBits regardless of wall time. For next
height 2016, use timestamps of heights 0 and 2015: **2015 intervals**, not 2016.
For next height 4032, use heights 2016 and 4031. Clamp the difference to
[302400, 4838400] seconds. Decode the previous target, multiply by bounded span,
integer-divide by 1209600, cap at full powLimit, then compact-encode. There is no
wall-clock-only emergency adjustment. The clamp bounds target scaling to ¼–4×
before compact truncation and saturation; difficulty varies inversely.

The largest valid MAIN product is below `2^256`, so unlimited Python multiplication
matches uint256 multiplication for this range. At the theoretical target 1, a
short span truncates the computed target to zero: C++ returns nBits zero, which
`DeriveTarget` rejects. The model preserves and tests this edge, never silently
substituting target 1. Scenario targets do not approach it.

ALUZ implements SHA256d, not the Scrypt mining family discussed in the readiness
document's Litecoin/Dogecoin comparison. That family's merged-mining software
cannot be assumed compatible with this fork.

## 3. Simulation methodology and reproduction

[Executable model v1](../test/functional/feature_andaluz_pow_sustainability.py) uses
only Python's standard library. Owner-approved Part 2 replaces the failed
zero-node framework lifecycle with `unittest` and strict `argparse`: no framework,
NetworkThread, daemon, listener, RPC, database or PoW nonce search. Runner metadata
`--configfile`, `--cachedir`, `--portseed`, `--tmpdir` is accepted and explicitly
unused; it cannot change model seeds or write files. Unknown arguments fail;
optimized Python is rejected so assertions cannot disappear. Successful runs
have empty stderr and exit zero only after both test groups pass.

```sh
python3 test/functional/feature_andaluz_pow_sustainability.py --configfile=build/test/config.ini
build/test/functional/test_runner.py --jobs=1 feature_andaluz_pow_sustainability.py
python3 test/functional/feature_andaluz_pow_sustainability.py --summary-json > /tmp/aluz-pow-summary.json
```

The initial build-tree runner attempt failed because the new test's
configure-generated link was missing. A temporary `/tmp` runner layout passed
while that limitation was investigated.

After owner review, `cmake -S . -B build` successfully regenerated the link.
The exact original build-tree runner then **PASSED (1/1 tests, 3 seconds)** on
2026-10-25. No tracked CMake or build-system files were changed. The
[test CMake glob](../test/CMakeLists.txt) creates functional-test links during
configuration. The earlier failure is preserved in the execution report as
historical troubleshooting evidence.

Each scenario runs nine fixed seeds **27500 through 27508**, with at most **16128
blocks (eight epochs)** per trial. `random.Random(seed)` supplies exponential
inter-arrival times. The conditional mean in seconds is
`600 * (reference_target / current_target) / relative_rate` for positive rate.
Thus easier targets shorten waits. Rates have no asserted real-world hash-rate
units; reference rate 1 is synthetic calibration to 600 seconds at genesis.
Target arithmetic is integer-only; floating point is used only for synthetic
waiting times and presentation ratios. Cumulative continuous arrival time is
floored to whole seconds for idealized timestamps; no minimum wait is imposed.
Cross-version libm/RNG details can affect final decimal places; reproduce with
the recorded Python version in the execution report. No actual hashes or valid
headers are generated.

A shock at next height 1, 1008 or 2015 starts before that block's waiting time.
Remaining blocks until the first retarget **decision** are respectively
2015, 1008 and 1. Required blocks through the adjusted block at height 2016 are
2016, 1009 and 2. Decision time is when parent 2015 exists; the new target can
only be observed in a chain after the additional boundary block arrives. Both
metrics appear below. This convention removes the ambiguous meaning of
“one block before boundary”: height 2015 must still arrive in the end scenario.

Constant loss/gain scenarios use rates 0.5, 0.1, 0.01 and 3. Restoration switches
from 0.1 to 0.5 or 1 at height 3024, regardless of elapsed time. Oscillation
alternates rates 0.1/3 in 252-block phases beginning with low participation;
this is a block-index assumption, not a miner profitability model. Near-limit
loss starts at `encode(powLimit)` and intentionally duplicates genesis compact.
The additional hypothetical harder-target scenario starts at reference/16;
its prior calibrated participation would be 16, dropping 90% to 1.6 at height 1.

Recovery means **first entry** of the conditional expected interval into
[480,720] seconds, not realized wait time or sustained recovery. Count blocks
produced since shock; zero means already in band. NOT MET means absent over the
bounded horizon, not a general proof of permanent non-recovery. Zero rate
separately means no blocks, no boundary computation and unattainable delays;
zero recorded progress does not mean wall time stops in reality.

The test covers literal compact vectors, noncanonical valid decoding, invalid
sign/zero/overflow/limit values, independent small integer examples, first and
subsequent epoch boundaries, 2015-interval genesis arithmetic, source PoW
vectors, stochastic direction/phase timing, exact seed reproducibility,
restoration schedules, capped losses, harder-target clamp and disappearance
at genesis and just before a boundary. A temporary independent C++ probe matched
2060 vectors against compiled repository `arith_uint256.cpp`; the existing
compiled `pow_tests` suite passed. This is useful coverage, not exhaustive
consensus equivalence. The probe and detailed JSON are outside git.

Omissions include reorgs, MTP and future timestamp rules, uint32 header timestamp
range, timestamp manipulation, orphan/stale blocks, propagation/latency,
selfish/adversarial mining, endogenous miner incentives and actual block/header
validation. Exponential means are not maximum waits; tails are unbounded.
Nine-seed p90 is an empirical nearest-rank statistic (the largest of nine), not
a population confidence bound or a guaranteed confirmation timeline.

## 4. Quantitative results

All trials use the settings above. Days are seconds / 86400. First table reports
nine-seed medians and empirical p90; target and recovery tables show seed 27500.
Rows at rate zero are conditional unattainable outcomes, not fabricated blocks.

| Scenario | Blocks to decision / adjusted block | Decision median / p90 (days) | Adjusted-block arrival median / p90 (days) |
| --- | ---: | ---: | ---: |
| baseline | 2015 / 2016 | 13.91358 / 14.53238 | 13.91893 / 14.54425 |
| loss50 | 2015 / 2016 | 27.82716 / 29.06475 | 27.83780 / 29.08851 |
| loss90-start | 2015 / 2016 | 139.13580 / 145.32375 | 139.18901 / 145.44254 |
| loss99 | 2015 / 2016 | 1391.35799 / 1453.23755 | 1391.89005 / 1454.42536 |
| loss90-middle | 1008 / 1009 | 70.07979 / 74.35552 | 70.09428 / 74.47430 |
| loss90-end | 1 / 2 | 0.01888 / 0.04905 | 0.08437 / 0.23390 |
| restore-partial | 2015 / 2016 | 139.13580 / 145.32375 | 139.18901 / 145.44254 |
| restore-full | 2015 / 2016 | 139.13580 / 145.32375 | 139.18901 / 145.44254 |
| gain3 | 2015 / 2016 | 4.63786 / 4.84413 | 4.64321 / 4.85557 |
| oscillate | 2015 / 2016 | 71.86885 / 75.34194 | 71.87010 / 75.34590 |
| zero | 2015 / 2016 | unattainable | unattainable |
| limit-loss99 | 2015 / 2016 | 1391.35799 / 1453.23755 | 1391.89005 / 1454.42536 |
| harder-loss90 | 2015 / 2016 | 139.13580 / 145.32375 | 139.14910 / 145.35345 |

Counts in the zero row describe the missing work required, not work completed.
The next table gives **both** retarget outcomes (heights 2016 / 4032): nBits,
target/reference ratio T/Tref, inverse difficulty ratio Tref/T, and conditional
expected seconds just after adjustment. Oscillation happens to be in its high
phase at both boundaries; it still alternates 6000/200-second means.

| Scenario | First / second nBits | First / second T/Tref | First / second Tref/T | Mean seconds at shock → after first / second |
| --- | --- | ---: | ---: | ---: |
| baseline | `1e00ffff` / `1e00f56b` | 1.000000 / 0.958679 | 1.000000 / 1.043102 | 600.00 → 600.00 / 625.86 |
| loss50 | `1e00ffff` / `1e00ffff` | 1.000000 / 1.000000 | 1.000000 / 1.000000 | 1200.00 → 1200.00 / 1200.00 |
| loss90-start | `1e00ffff` / `1e00ffff` | 1.000000 / 1.000000 | 1.000000 / 1.000000 | 6000.00 → 6000.00 / 6000.00 |
| loss99 | `1e00ffff` / `1e00ffff` | 1.000000 / 1.000000 | 1.000000 / 1.000000 | 60000.00 → 60000.00 / 60000.00 |
| loss90-middle | `1e00ffff` / `1e00ffff` | 1.000000 / 1.000000 | 1.000000 / 1.000000 | 6000.00 → 6000.00 / 6000.00 |
| loss90-end | `1e00ffff` / `1e00ffff` | 1.000000 / 1.000000 | 1.000000 / 1.000000 | 6000.00 → 6000.00 / 6000.00 |
| restore-partial | `1e00ffff` / `1e00ffff` | 1.000000 / 1.000000 | 1.000000 / 1.000000 | 6000.00 → 6000.00 / 1200.00 |
| restore-full | `1e00ffff` / `1e00ffff` | 1.000000 / 1.000000 | 1.000000 / 1.000000 | 6000.00 → 6000.00 / 600.00 |
| gain3 | `1d562d56` / `1d51ce70` | 0.336634 / 0.319561 | 2.970582 / 3.129292 | 200.00 → 594.12 / 625.86 |
| oscillate | `1e00ffff` / `1e00ffff` | 1.000000 / 1.000000 | 1.000000 / 1.000000 | 6000.00 → 200.00 / 200.00 |
| zero | none | none | none | infinite → none |
| limit-loss99 | `1e00ffff` / `1e00ffff` | 1.000000 / 1.000000 | 1.000000 / 1.000000 | 60000.00 → 60000.00 / 60000.00 |
| harder-loss90 | `1d3fffc0` / `1e009963` | 0.250000 / 0.599176 | 4.000000 / 1.668959 | 6000.00 → 1500.00 / 625.86 |

| Scenario | First recovery: blocks / days (seed 27500) | Trials entering band / 9 |
| --- | ---: | ---: |
| baseline | 0 / 0.00000 | 9 |
| loss50 | NOT MET | 0 |
| loss90-start | NOT MET | 0 |
| loss99 | NOT MET | 0 |
| loss90-middle | NOT MET | 0 |
| loss90-end | NOT MET | 0 |
| restore-partial | NOT MET | 0 |
| restore-full | 3023 / 204.81486 | 9 |
| gain3 | 2015 / 4.71289 | 9 |
| oscillate | NOT MET | 0 |
| zero | unattainable | 0 |
| limit-loss99 | NOT MET | 0 |
| harder-loss90 | 4031 / 174.96854 | 9 |

An independent expectation check before the first decision is
`remaining_blocks * 600 / rate`, since target is constant over those waits.
For 90% loss at start/middle/end that gives 12,090,000 / 6,048,000 / 6,000
seconds. These analytical means differ from empirical medians, especially for
the one-block end shock. Its nine-seed p90 is not a conservative population
bound: an exponential 6000-second wait has a theoretical p90 of about 13,816
seconds. The small fixed seed set must not be used for service guarantees.

The median first decision takes about 13.91 days at baseline, 139.14 days after
90% loss, and 1391.36 days after 99% loss. Later shocks shorten exposure before
the first boundary; they do not create target headroom. Even an immediate
boundary cannot ease past the compact limit. Full restoration's recovery at
height 3024 is caused by assumed participation, not automatic emergency relief.
Partial restoration to half baseline leaves a 1200-second conditional mean.
Random baseline epochs can modestly harden or ease difficulty; saturation
prevents easing below the genesis difficulty.

In the hypothetical harder-target case, initial mean is 6000 seconds. First
retarget increases target exactly 4×, reducing mean to 1500 seconds; the second
reaches about 625.86 seconds in seed 27500. This isolates the cap's multi-epoch
recovery constraint without inventing genesis headroom. Fast 3× participation
hardens difficulty at the first retarget and enters band. These interval
observations say nothing about who controls work or whether a reorg is affordable.

## 5. Option A — retain the current DAA

Retention preserves existing validation/serialization compatibility and the
small, familiar retarget implementation. It avoids a new activation boundary.
Its operational weaknesses are long periods before adjustment, 4× bounded easing
when headroom exists, and complete saturation at the baseline target studied.
Operators cannot fix stalls with wall-clock waiting or a policy-only RPC change.

Engineering judgment: quantify sustained independent participation and
concentration before considering public operation. Define alert thresholds,
confirmation policies, assigned incident owners and stalled-chain drills.
Any future pool discussion requires separate owner authorization; this research
establishes no compatible pool, commitment, viable reward economics or available
mining capacity. Retaining rules is an option to assess, not a launch approval.

## 6. Option B — ASERT research, not implemented

The [2020 BCH specification](https://upgradespecs.bitcoincashnode.org/2020-11-15-asert/)
describes an anchored schedule using height/time deltas, an anchor target and the
anchor parent's timestamp. Its `aserti3-2d` choice uses a two-day half-life and
fixed-point polynomial arithmetic with precise signed rounding and shifts.
It specifies MTP-based activation and anchor determination. The
[protocol overview](https://documentation.cash/protocol/blockchain/proof-of-work/difficulty-adjustment-algorithm.html)
also distinguishes these historical DAA rules.

Proposed ALUZ research must independently specify anchor selection across forks,
height offsets, time deltas, half-life and activation coordination. Test noise
versus response across several candidate half-lives; BCH's setting is not an ALUZ
recommendation. Require independent integer implementations and published vector
agreement, including negative deltas, overflow, powLimit, compact edges and
reorgs across activation. A floating-point exponential illustration is not
consensus code and must never be copied into production validation.

Expected benefit is per-block response after difficulty has hardened, conditional
on blocks continuing. Study MTP/future-time constraints and adversarial timestamp
strategies with a threat model; responsiveness alone does not establish safety.
An absent next miner still stalls progress, and retaining the current powLimit
retains genesis saturation. No ASERT implementation, performance comparison or
activation has been delivered by this milestone.

## 7. Option C — SHA256d AuxPoW research, not implemented

The [historical Namecoin merged-mining design](https://github.com/vinced/namecoin/blob/master/doc/README_merged-mining.md)
uses a parent coinbase commitment, auxiliary and coinbase Merkle branches, and a
parent header whose hash satisfies the child target. Its historical deployment
status is not current ALUZ support. The
[Namecoin FAQ](https://www.namecoin.org/docs/faq/) describes SHA256d parent-family
agility: Bitcoin is a precedent, not a guarantee that all Bitcoin miners
participate or that the parent must be Bitcoin.

A proposed ALUZ design would need child block validation/serialization rules,
chain ID and commitment-slot domain separation, duplicate/ambiguous commitment
rejection, bounded proof parsing, parent-header checks, and an explicit policy
on legacy standalone PoW. Activation changes consensus and compatibility;
unmodified nodes cannot be assumed to accept new proofs. Acceptance of child
work need not require finding a valid parent-network block.

Require an actual software/pool compatibility inventory, independent malformed
proof/serialization tests, activation/reorg vectors and isolated prototype
interop. Parent work is useful only if interested compatible miners/pools
commit to and submit child work. Verify operational overhead, payouts and miner
incentives with separately approved evidence; availability and revenue are
unknown. SHA256d Bitcoin-family mining is relevant here; Litecoin/Dogecoin Scrypt
merged mining is not a drop-in implementation for ALUZ. Concentrated child
participation may retain substantial reorg and censorship risk even with a
large parent network. Software alone supplies neither Bitcoin-equivalent
security nor economic viability.

## 8. Engineering comparison

DAA selection and AuxPoW are separate design dimensions: AuxPoW may coexist with
legacy retargeting or a future DAA. It is not itself a difficulty algorithm.
The matrix is engineering assessment, not a benchmark of unimplemented options.

| Dimension | A: retain 2016 DAA | B: ASERT research | C: SHA256d AuxPoW research |
| --- | --- | --- | --- |
| Responsiveness | Epoch boundary; easing bounded and capped | Per-block candidate response; still requires miners and target room | Participation mechanism; response follows chosen child DAA |
| Consensus change size | None | Target computation plus activation/anchor rules | Proof/validation/serialization/chain ID plus activation |
| Compatibility | Existing nodes/miners | Coordinated validator upgrade/fork | Validator and pool/software upgrade; legacy PoW decision |
| Required tests | Current integer edges; shock/stall drills | Independent fixed-point vectors, timestamps, forks, adversarial schedules | Proof parsing, commitments, chain ID, parent/child targets, interop and forks |
| Operational dependence | Sustained independent miners and monitoring | Same plus coordinated upgrade operators | Interested compatible parent miners/pools plus child operation |
| Economic feasibility | Unknown actual security budget | No new income or miner guarantee | Unknown incentive, support and payout overhead |
| Failure modes | Stall, cap/limit saturation, timestamp abuse | Wrong rounding/anchor, noisy tuning, activation split, zero miners | Invalid/ambiguous proofs, concentration, withheld child work, upgrade split |
| Unproven assumption | Sufficient stable participation | Safer overall behavior under ALUZ conditions | Willing sustained independent child commitments |

## 9. Security and public launch

Interval resilience is not proof-of-work security or reorg resistance. Majority
work attacks can reverse transactions or censor confirmations; concentrated or
rented participation can alter threat exposure. No rental cost or attack budget
is measured here, and no economic forecasts are justified by normalized rates.
Eclipse conditions, reorganizations, timestamp abuse and correlated withdrawal
need explicit adversarial analysis. Under zero miners nothing advances; under
severe loss, exponential long tails amplify operational uncertainty.

The [Mining security and difficulty viability gates](andaluzcoin-mainnet-readiness.md#mining-security-and-difficulty-viability)
still require real independent hash-rate and concentration evidence, sustained
production, reviewed shock acceptance bounds, attack modeling and assigned
monitoring/incident response with successful drills. This model is a research
input, not independent review or completion of even the modeling gate.
Consensus audit, recovery, deployment security and all other readiness gates
also remain unresolved. NO-GO is unchanged.

## 10. Recommendation and staged acceptance criteria

Keep this milestone offline and submit its complete diff, both reports and
model assumptions to the owner and an independent consensus reviewer. Acceptance
for this research is exact agreement on documented integer examples/source
vectors, reproducible bounded scenarios, direct and registered tests passing,
and explicit acknowledgment of saturation and omitted security effects.

Next, independently reproduce the current model and extend adversarial timestamp
and reorg modeling in a separately reviewed research scope. Require reviewers
to agree on block-count conventions, distributions and failure definitions.
For an ASERT experiment, first publish an ALUZ-specific candidate specification
and acceptance bounds for noise, stalls and adversarial timestamp schedules;
then require agreement of two independent integer implementations with all
reference and activation/reorg vectors. Do not select a half-life from one trace.
For AuxPoW, first produce a threat model and proof/serialization/chain-ID design,
then demonstrate malformed-proof rejection and isolated cross-implementation
interop before any operational trial. Test pool withdrawal and concentration
rather than assuming parent-chain security transfers.

Real participation/security-budget evidence and reviewed operational response
bounds remain separate prerequisites. **Any eventual consensus change, external
pool outreach, deployment or release decision requires explicit owner approval.**
No automatic change or release recommendation follows from these results.

## 11. Source and evidence appendix

Repository facts above are proven only to the source inspection and vector
coverage stated, at commit `3ffd48fe6c5c6ccb9dcb223407de3d7f539c8ebc` / baseline tag,
2026-10-25. Existing [PoW tests](../src/test/pow_tests.cpp) include inherited
Bitcoin numerical vectors using harder targets (e.g. `0x1d00ffff`), not evidence
that ALUZ genesis has that target. The current suite also contains explicit
ALUZ MAIN parameter checks; it passed without modifying inherited expectations.
The “pow limit” inherited test name alone does not prove ALUZ saturation.

The [precomputed mainnet validation test](../test/functional/mining_andaluz_mainnet_block_validation.py),
[chain recovery test](../test/functional/mining_andaluz_mainnet_chain_recovery.py)
and [template identity test](../test/functional/mining_andaluz_getblocktemplate_identity.py)
were inspected, not run here: they start nodes, and the template test mines.
They do not validate a synthetic multi-epoch DAA trace. Operational context:
[bootstrap](andaluzcoin-mainnet-bootstrap.md) and [development notes](andaluzcoin-dev-notes.md).

Primary external sources, retrieved successfully on **2026-10-25**, establish
third-party historical designs only:

- [BCH ASERT 2020 specification](https://upgradespecs.bitcoincashnode.org/2020-11-15-asert/): anchor, integer arithmetic and activation requirements.
- [BCH DAA overview](https://documentation.cash/protocol/blockchain/proof-of-work/difficulty-adjustment-algorithm.html): historical algorithms and ASERT overview.
- [Namecoin FAQ](https://www.namecoin.org/docs/faq/): SHA256d merged-mining precedent; no ALUZ pool support inferred.
- [Historical Namecoin design](https://github.com/vinced/namecoin/blob/master/doc/README_merged-mining.md): commitment/proof structure; not a modern deployment guide.

Scenario tables are our own model observations. Comparative risks and proposed
acceptance criteria are engineering judgments requiring independent review.
No external URL was treated as ALUZ runtime authority. Detailed command outputs,
failures, durations, environment and final scope checks are saved in the
out-of-repository `v0.2.75-execution-report.txt`; pre-edit findings and explicit
correction are in `v0.2.75-mining-analysis.md`. No CSV, JSON or probe is committed.
