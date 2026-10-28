# SHA256d AuxPoW feasibility and security architecture — v0.2.76

## 1. Executive decision

**NO-GO for public economic mainnet. No consensus change is implemented or
activated.** SHA256d merged mining is a plausible subject for separately
approved engineering research. End-to-end ALUZ feasibility is **UNPROVEN**.

Four questions require separate evidence:

| Question | Finding at this milestone |
| --- | --- |
| Can evidence bind a child candidate to parent work? | Cryptographic linkage has third-party precedent; a bounded toy illustrates byte binding only. |
| What would ALUZ validators accept? | Current standalone PoW only. Future proof format, validation and activation are open. |
| Will independent miners submit ALUZ work? | UNKNOWN; no pool compatibility commitment or outreach. |
| Will ALUZ resist concentration, reorgs and miner exit? | UNKNOWN; neither parent hash totals nor toy tests establish this. |

Recommendations below are engineering judgments, not a launch decision or an
economic-security proof. Bitcoin's total hash rate is **not** committed ALUZ
participation and does **not** automatically confer Bitcoin security on ALUZ.

## 2. Verified current ALUZ facts

Scope baseline: `a6cd2e557ad59a3d8893acd65322d85c7fbd069f`, annotated tag
`v0.2.75-pow-mining-sustainability-research`; research branch
`research/sha256d-auxpow-feasibility`. Source inspected 2026-10-28 UTC.

[Main parameters](../src/kernel/chainparams.cpp) `CMainParams`, lines 98–155:
SHA256d, 600-second intended spacing, 1209600-second target timespan, 2016-block
interval, retarget enabled, no mainnet minimum-difficulty exception.
`powLimit = 000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff`;
genesis `nBits = 0x1e00ffff`. Mainnet magic `b6a96458`, P2P port 29444, genesis
`000000f7dca7651a1397fd0bc99b2a456dbb2d23470834b6290aadec4b46d15c`.
Mainnet DNS/fixed seeds are empty. These identify configured rules, not a live
public network. See [chain specification](chain-spec.md).

[PoW code](../src/pow.cpp) `GetNextWorkRequired`,
`CalculateNextWorkRequired`, `DeriveTarget`, `CheckProofOfWorkImpl` and
[consensus parameters](../src/consensus/params.h) define target handling.
Timespan is clamped to one quarter/four times target; easing stops at powLimit.
The [v0.2.75 study](andaluzcoin-mining-sustainability.md) demonstrates
powLimit/reference_target ≈ 1.0000152590218967 and identical compact encoding
`0x1e00ffff`: no useful genesis easing headroom. AuxPoW changes neither this
limit nor the DAA. ASERT is also unimplemented and inactive.

[Header serialization](../src/primitives/block.h) `CBlockHeader` writes version,
previous hash, Merkle root, time, bits, nonce (4+32+32+4+4+4 = 80 bytes).
[GetHash](../src/primitives/block.cpp) line 15 uses
[HashWriter::GetHash](../src/hash.h), line 115: double SHA256. A future parent
header hash would be a separate work input; the child block identifier must
remain precisely defined, avoiding circular proof hashing. Proof inclusion in
block/header serialization, disk/P2P messages and header-only synchronization
cannot be assumed backward compatible.

[Validation](../src/validation.cpp) `CheckBlockHeader` line 3860 currently
compares child `GetHash()` with child nBits; `ContextualCheckBlockHeader` line
4112 checks expected difficulty/time. Presync header checks and accumulated
work at lines 4056/4094 also require future audit. [Miner templates](../src/node/miner.cpp)
`BlockAssembler::CreateNewBlock` produce ordinary child templates. None provides
an existing ALUZ AuxPoW path. [PoW unit tests](../src/test/pow_tests.cpp) test
current rules; passing them is regression evidence only.

## 3. External source map and caveats

Accessed 2026-10-28; mutable `master` snapshots, exact upstream commits
**UNVERIFIED** (GitHub commits API inaccessible through research tool).

| Primary source | Supported claim / limit |
| --- | --- |
| [Namecoin Core auxpow.cpp](https://github.com/namecoin/namecoin-core/blob/master/src/auxpow.cpp), `CAuxPow::check`, `getExpectedIndex`, `CheckMerkleBranch` | Existing linkage-validation precedent; not ALUZ rules. |
| [Namecoin Core auxpow.h](https://raw.githubusercontent.com/namecoin/namecoin-core/master/src/auxpow.h), `CAuxPow::SERIALIZE_METHODS` | Transaction, branches, index and parent-header serialization precedent; not ALUZ encoding. |
| [Historical Namecoin description](https://github.com/vinced/namecoin/blob/master/doc/README_merged-mining.md), Background | Historical conceptual flow and auxiliary target comparison; historical single-child statements are not current specifications. |
| [Official Namecoin FAQ](https://www.namecoin.org/docs/faq/), merged-mining parent question | SHA256d-family parent choice; no ALUZ pool support inferred. |

In the inspected `auxpow.cpp`, `check` bounds the auxiliary branch to 30,
checks parent membership at index zero, reverses the auxiliary root for script
search, and checks tree size/nonce-derived index. Strict chain-ID checks depend
on parameters. Marker uniqueness/adjacency is checked when present; a historical
markerless root within the first 20 script bytes is also permitted. ALUZ must
explicitly decide its own stricter canonical policy; it must not silently inherit
that exception. `getExpectedIndex` maps nonce and chain ID into tree slots.
These are partial code observations, not a complete Namecoin audit or proof of
parent-network validity. No upstream implementation is copied into this toy.

## 4. Conceptual end-to-end flow

```text
Child candidate (transactions + previous tip + child target + identity)
       | precisely specified child identifier
       v
Auxiliary tree leaf / siblings / deterministic slot (future decision)
       | root commitment, canonical placement and network separation
       v
Parent coinbase transaction ---> parent transaction Merkle root
       |                                |
       +-- coinbase + membership proof  v
                                Parent header / SHA256d work
                                        |
                 +----------------------+---------------------+
                 |                      |                     |
          Pool share threshold    CHILD target met     PARENT target met
          accounting only         candidate evidence   possible parent block
                 |                      |                     |
       no child acceptance       independent child      parent node validates
       implied                   validator              its OWN full rules
                                        |
                     parse/proof/target + all child consensus
                                        |
                             candidate acceptance or error
                             then child chainwork selection
```

Shares may satisfy only a pool threshold; some satisfy the child target without
satisfying the parent network target. Even a header below the parent target is
not proof that the parent network accepts a full block. Parent block acceptance
is not inherently required for child work acceptance; any ALUZ restrictions
would need a justified explicit specification.

## 5. Evidence and proof obligations matrix

Labels: **CURRENT** = verified ALUZ CURRENT, **PRECEDENT** = Namecoin precedent,
**OPEN** = ALUZ OPEN DECISION, **TOY** = toy checks only. Every proposed boundary
below is future work; no production files were edited.

| Obligation | Evidence status | Exact future boundary / missing decision |
| --- | --- | --- |
| Child header/identifier | CURRENT ordinary hash; OPEN future binding; TOY 32-byte ID | `primitives/block.h/.cpp`: define immutable candidate identity and proof exclusion/inclusion. |
| Commitment format/position | PRECEDENT script search; OPEN canonical format; TOY fixed prefix/marker | Future separate proof parser, `primitives/transaction.h` transaction interpretation; strict duplicates/position. |
| Auxiliary Merkle siblings/index | PRECEDENT; OPEN real tree; TOY generic binary branches only | Future verifier beside `pow.h/.cpp`; tree size, nonce/index coupling, ordering. |
| Parent coinbase transaction | PRECEDENT; OPEN; no TOY tx checks | `primitives/transaction.h/.cpp`: bounded decoding, txid/witness distinction, prevout and script rules. |
| Parent Merkle membership | PRECEDENT; OPEN; TOY synthetic membership | Future proof verifier: enforce coinbase index zero and canonical branch/count policy. |
| Parent header | CURRENT child layout only; PRECEDENT parent field; OPEN; TOY layout | `primitives/block.h`, future separate parent-header representation and allowed fields. |
| SHA256d work vs CHILD nBits | CURRENT standalone; OPEN parent work routing; no TOY work check | `validation.cpp` CheckBlockHeader, header presync and `pow.cpp` target range/context. |
| Parent/child chain-ID separation | PRECEDENT parameter-dependent; OPEN; TOY domains only | `kernel/chainparams.cpp`, `consensus/params.h`, future proof verifier; no ID assigned. |
| Length/depth limits | PRECEDENT aux bound; OPEN production allocation limits; TOY 128 bytes/4 levels | Future parser before allocation, bounded CPU and total message/disk sizes. |
| Canonical encoding | OPEN; TOY exact local bytes only | `primitives/block.h` plus future proof serializer; trailing data, varints, ambiguity. |
| Version/activation | CURRENT ordinary header; OPEN; absent TOY | `consensus/params.h`, `validation.cpp` ContextualCheckBlockHeader; no bit selected. |
| Old PoW acceptance | CURRENT standalone accepted; OPEN future policy; absent TOY | `validation.cpp` proof dispatch and contextual activation. |
| Branch work/selection | CURRENT GetBlockProof use; OPEN hybrid accounting; absent TOY | `chain.cpp` GetBlockProof and `validation.cpp` nChainWork/header presync; count work once. |
| Errors | CURRENT header rejection; OPEN new errors; TOY ValueError | Future parser/validator: deterministic failures, no partial acceptance or cache bypass. |

## 6. Architecture options and compatibility

| Option | Compatibility and work accounting | Principal risks |
| --- | --- | --- |
| Keep standalone SHA256d | Current format and DAA; no new proof route | Does not recruit miners automatically; stall and concentration remain. |
| Future legacy plus AuxPoW | Explicit mode discriminator, same child target if chosen, count each accepted child block once | Old nodes may reject new headers/proofs; separate mode targets could distort chainwork; migration and mode-switch attacks require tests. |
| Future AuxPoW-only | Standalone blocks rejected after separately specified activation | Mandatory miner/validator upgrade, exclusion and exit dependency, recovery more difficult. |

No option or activation is selected. New serialization may alter block IDs,
header size, storage and relay behavior. Old mining nodes can continue producing
blocks rejected by upgraded nodes or build a divergent chain. Even keeping a
legacy path does not establish backward compatibility with auxiliary proofs.
A chainwork design must use validated child difficulty, never pool share counts
or multiply credited parent work. Parent reorgs are not automatically child
reorgs when parent acceptance is not required. Child forks still compete under
specified child work rules. Post-activation rollback can itself split consensus;
operator downgrade is not a safe automatic recovery mechanism.

## 7. Domain, chain ID and replay security

No ALUZ AuxPoW chain ID is approved, reserved or proposed as final. Current
ALUZ magic/ports/genesis do not substitute for proof-domain rules. Inspection
of the Namecoin slot function shows that finite-depth slots depend on chain ID
modulo a power of two: different IDs can collide even without numeric equality.
Nonce changes do not establish global collision freedom. Selection needs dated
source-pinned inventories of deployed SHA256d auxiliary IDs, version-bit layouts,
parent-ID policies and multi-child interoperability vectors. There is no proven
exhaustive registry here. This was a code-level collision analysis; an ecosystem
allocation/collision inventory remains **UNVERIFIED**, and no chain ID was
selected. Relevant repositories must be searched in a separately scoped study.

Future reviewers must specify parent same-ID rejection, allowed parent family,
network-specific domains, mainnet/testnet/regtest isolation, auxiliary tree depth,
size, nonce/index function and byte order. A pool must handle conflicting slots
and multiple children deterministically or report inability to include a child.
Version-bit reuse can change candidate identity or collide with signaling.
Canonical marker/root uniqueness, position, trailing bytes and alternate encoding
rules must reject ambiguity. Historical permissive marker handling is a design
choice, not an ALUZ obligation.

The toy uses literal `TOY-NET-A` and `TOY-NET-B` before a 32-byte child ID in a
SHA256d commitment. This illustrates domain binding only; it has no numeric
chain ID, actual network replay policy, nonce coupling or real auxiliary tree.

## 8. Threat model

All mitigations below are future requirements or operational recommendations;
severity is qualitative engineering assessment, not measured attack cost.

| Threat / severity | Preconditions and detection | Mitigation / remaining assumption | Toy reach |
| --- | --- | --- | --- |
| Majority child work/censorship — critical | Hostile effective child work exceeds honest work; independent tip/inclusion monitoring | Independent participation, reorg response, reviewed confirmation policy; honest work remains unproven | None |
| Concentration — critical | One pool controls much child submission even with diverse parent miners; ownership inventory | Independent control/failure domains; parent miner count alone insufficient | None |
| Pool equivocation/exclusion — high | Operator builds conflicting child tips or omits ALUZ; compare templates and tips | Independently auditable submissions and authorized operator trials | None |
| Withheld child shares — high | Pool receives child-valid work but does not submit; compare authorized share/submission logs | Timely child job/submission paths and alerts; observability unproven | None |
| Parent invalidity misconception — high | Treating parent header as evidence of accepted parent block | Specify exactly child proof requirements; independent child validation | Layout/linkage only |
| Proof replay — critical | Missing candidate/domain/slot binding | Canonical child binding, ID policy and nonce/index vectors | Altered child and toy-domain detection only |
| Branch/allocation/CPU DoS — high | Attacker supplies huge/malformed serialized proof before allocation bound | Preallocation limits, fuzzing and resource budgets | Fixed local byte/depth bounds only |
| Coinbase mutations — high | ExtraNonce, payout or witness edits invalidate membership/commitment | Regenerate complete proof atomically; canonical txid rules | Synthetic blob/sibling corruption |
| Reorg/chainwork accounting — critical | Incorrect proof mode dispatch, double credit or target mismatch | Independent mixed-mode fork vectors and work comparison | None |
| Cross-network replay — critical | Shared domain/activation or ambiguous serialization | Explicit network identity and cross-network rejection vectors | Two invented domains only |
| Activation split — critical | Different heights/time/signaling or old-node interpretation | Reviewed fork coordination and boundary/recovery tests | None |
| Outage/zero miners — high | Pool exits, loses child daemon/job service or stops payouts | Diverse operators, regeneration/recovery drills and monitoring | None |

Collision resistance of SHA256d and correct local cryptographic libraries are
assumptions. A Merkle membership proof does not establish that all transactions
are valid or even available. Concentrated merged mining may make child attacks
cheap relative to honest child participation; no quantitative claim follows.

## 9. Difficulty economics and interactions

AuxPoW is a method of supplying candidate work, not a DAA. At genesis the target
is already compact-saturated. If participation drops, the 2016-block epoch can
stall; wall time alone does not ease mainnet difficulty. After sustained added
work hardens difficulty, rapid pool exit could leave a long recovery epoch.
Zero miners produce zero blocks. Changing powLimit or adopting ASERT would be
separate consensus decisions requiring independent justification.

Child acceptance must compare the designated work hash to the contextual child
target, including nBits validity/range, rather than parent nBits or a pool share
target. Parent work can qualify for the child while failing the parent target.
Hybrid accounting must not sum pool shares, credit a proof twice, or infer extra
child chainwork from an exceptionally low hash. Define any mode-specific target
policy and test the resulting fork incentives before implementation.

Miner incentives include child subsidy/fees against integration, monitoring,
validation, bandwidth, storage, orphan risk, custody and payout costs. Rewards
without a reliable payout/withdrawal path need not attract participants. Price,
liquidity, costs, miner revenue and actual support are unknown; no forecast,
51% attack price, rental availability or Bitcoin-security equivalence is given.

## 10. Operational feasibility inventory

Outreach **NOT PERFORMED**. No external accounts, mining interfaces or chain RPC
were accessed. These are classes to investigate, not supported ALUZ products.

| Interface/class | Status / evidence needed when separately authorized | Failure mode / operator requirement |
| --- | --- | --- |
| Child template and proof-submission interface | UNKNOWN; versioned specification and isolated adapter interoperability | Stale candidate, wrong tip/target; run and monitor validated child nodes |
| SHA256d pool job assembler | UNKNOWN; exact software/version support and independent operator commitments | Commitment overwritten or slot conflict; rebuild proofs on job mutations |
| Parent mining job/share protocol | UNKNOWN; prove coinbase commitment survives negotiated job construction | Upstream job changes/exclusion; retain child-valid shares below parent threshold |
| Share-to-child submission/payout service | UNKNOWN; authorized end-to-end evidence | Withholding, duplicate credit, payout failure; reconcile and alert |
| Validator/storage/relay tooling | Current ordinary headers only; future benchmarks required | Old nodes reject proof format; bounded decoding and durable proof retention |

Measure proof overhead, parse cost, relay latency and stale rates on a separately
approved isolated prototype. No benchmark is inferred from this toy. Operators
need independent ownership evidence, version inventory, reproducible releases,
backup/recovery, child-tip monitoring and safe payout practices. Deployment would
need fork coordination and a reviewed recovery plan; rollback after a consensus
change must not assume older binaries can validate the new chain.

## 11. Future specification checklist and activation/reorg matrix

All entries are **OPEN DECISIONS**, not permission to edit consensus:

- Specify chain ID/domain, parent-ID policy, version-bit allocation, byte order,
  header identity, proof serialization and canonical marker/root placement.
- Specify actual coinbase transaction and witness/txid parsing, prevout/input
  policy, branch indices/counts, auxiliary size/nonce coupling, multiple children,
  mutation handling and preallocation memory/CPU/message limits.
- Specify contextual child nBits, powLimit, timestamps/MTP, parent-field policy,
  work dispatch, branch chainwork and duplicate-proof handling.
- Specify height/time/signaling activation, legacy acceptance, old/new node
  compatibility, regeneration, downtime recovery and post-activation rollback.

| Future independent test dimension | Required cases and acceptance evidence |
| --- | --- |
| Activation boundary | Before/at/after activation; all modes; old/new nodes and miners; malformed or missing proofs |
| Fork/reorg | Reorg across activation and epoch boundary, mixed modes, equal work ties, withheld branches; agreed child chainwork |
| Target/time | Invalid/negative/overflow/cap nBits, parent vs child targets, MTP/future timestamps, retarget context |
| Serialization/DoS | Truncation, noncanonical integers, trailing bytes, maximum+1 sizes, deep branches, resource budget and differential fuzzing |
| Replay/multiple children | Same/different networks, parent same ID, colliding IDs/slots, nonce changes, duplicate markers/roots |
| Coinbase mutations | ExtraNonce, reward/script changes, witness/nonwitness variants, empty/malformed inputs and branch regeneration |
| Recovery | Child service restart, stale template, parent job change, all miners exit, proof storage/reindex and coordinated recovery |

Require two independently implemented validators to agree on positive and
negative serialized vectors before considering production changes. The current
toy supplies none of these consensus-validation assurances.

## 12. Test method and reproducibility

[Test executable](../test/functional/feature_andaluz_auxpow_feasibility.py) is
standard-library-only, deterministic and independent of BitcoinTestFramework.
Fifteen named unittest methods include three positive/vector methods and twelve
negative/boundary methods with subcases. Raw binary hashes are exactly 32 bytes;
index bits select left/right from lowest bit upward. Four levels maximum,
128-byte maximum synthetic commitment input, and no odd-leaf duplication policy.

A synthetic leaf is SHA256d of `TOY-COINBASE:` + `|TOY-COMMIT|` + SHA256d of
`TOY-CHILD:` + domain + child ID, optionally followed by bounded padding. Marker
must occur once at the fixed offset. Generic parent membership is illustrated;
there is no actual coinbase-position consensus assertion. Synthetic header root
occupies bytes 36–67; nonce/time/bits are fixed zero with no target comparison.
A separate source-fixed ALUZ genesis header vector checks SHA256d and display
byte reversal. It is not a newly mined header or an AuxPoW block.

Independent OpenSSL SHA256 twice over raw `00*32 || 01*32` yields
`705ede9d42476fc3e5a978b042ce790a193678f46d19f47ec4ab46539c47b76d`;
over `02*32 || 03*32` yields
`1b12c142ca6fabe6cccf4aa52aff1f21882ec49da2dd4c1cf70abffcc45f591b`;
over those two digests yields
`ac41efca4951b1260054e1155fd8f6c3f42a5b521f1161b20f3c053d3159816c`.
Expected values are literals, not the tested function's output. Genesis fields
and expected hash are independently fixed in baseline chainparams.cpp:135–151;
OpenSSL also reproduced that value.

Exact local validation commands (repository root):

```sh
export PYTHONPYCACHEPREFIX=/tmp/aluz-276-pycache
python3 -m py_compile test/functional/feature_andaluz_auxpow_feasibility.py
python3 test/functional/feature_andaluz_auxpow_feasibility.py
build/test/functional/test_runner.py --jobs=1 feature_andaluz_auxpow_feasibility.py
build/test/functional/test_runner.py --jobs=1 --timeout-factor=40 feature_andaluz_auxpow_feasibility.py
build/test/functional/test_runner.py --jobs=1 --timeout-factor=40 --v2transport --usecli feature_andaluz_auxpow_feasibility.py
build/test/functional/test_runner.py --jobs=1 --timeout-factor=40 --previous-releases feature_andaluz_auxpow_feasibility.py
python3 test/functional/feature_andaluz_auxpow_feasibility.py --timeout-factor=40 --previous-releases --coveragedir=/tmp/aluz-276-cov-unused
python3 test/functional/feature_andaluz_auxpow_feasibility.py --v1transport --nocleanup --randomseed=123
build/bin/test_bitcoin --run_test=pow_tests --log_level=test_suite
```

If the new build link is absent, use `cmake -S . -B build` with existing cached
flags. The child explicitly ignores known metadata paths without opening or
creating them. Unknown/abbreviated flags are errors (exit 2), types are checked,
and optimized Python is rejected. Successful test output uses stdout, with
empty stderr. An external in-memory harness injecting `self.assertEqual(1,2)`
verified failure exit 1; no fail-open test switch is shipped.

Mutation coverage: child ID, missing/duplicate/misplaced marker, sibling,
left/right order, negative/out-of-range index, parent root, truncated hashes,
depth maximum+1, input maximum+1, and cross-toy-domain replay. Bounds at the
maximum also pass. No network, RPC, socket, daemon, wallet, nonce search, threads,
processes or file writes occur inside the child. External runner orchestration
owns temporary paths and processes. This is not a parser fuzzer, real proof
verifier, benchmark, economic simulation or complete memory/CPU DoS test.

No real coinbase/script parsing, prevout validation, real auxiliary tree,
chain-ID/nonce/index coupling, parent header validity/work-vs-child-nBits,
real candidate validation, actual duplicate-root policy, chainwork, network
replay, activation, reorg/time consensus or parent transaction semantics are
covered. Global RPC coverage is deliberately not run for this sole no-RPC test;
full multi-test GitHub CI integration remains **UNVERIFIED**, not claimed passed.

## 13. Recommendation and staged gates

Keep current PoW unchanged and submit this evidence to owner and ChatGPT review.
All [readiness gates](andaluzcoin-mainnet-readiness.md#mining-security-and-difficulty-viability)
remain unchecked. Even the modeling/architecture gates require independent
review and further evidence.

Next three separately authorized engineering milestones:

1. Produce a source-pinned candidate specification and exhaustive decision log,
   including chain-ID collision inventory, canonical encodings, targets,
   activation and legacy-mode policy. Gate: independent consensus reviewers
   agree on ambiguities and rejection rules, with no ID presumed reserved.
2. Build isolated independent proof parsers/verifiers against the agreed
   specification; differential vectors, adversarial resource tests, mixed-mode
   work and activation/reorg tests. Gate: reproducible cross-implementation
   agreement and malformed-proof resistance, followed by security review.
3. Establish separately authorized software/operator compatibility evidence and
   isolated operational trials, including payouts, child share submission,
   concentration, pool exit and recovery. Gate: independent sustained commitment
   and measured operating/security limits; no automatic mainnet approval.

**v0.2.76 offers evidence, not permission for v0.2.77 consensus work, pool
contact, public mining or mainnet release.** No pool availability, revenue or
attack-price conclusion is justified. Stop here for owner and ChatGPT review.

## 14. Sources, unknowns and independent review

Local immutable baseline references are in section 2; implementation boundaries
in section 5. [Transactions](../src/primitives/transaction.h)
`SerializeTransaction` and [transaction hashing](../src/primitives/transaction.cpp)
`ComputeHash/ComputeWitnessHash` distinguish real tx serialization from toy
bytes. [Raw hash representation](../src/uint256.h) and
[test message serialization](../test/functional/test_framework/messages.py)
provide local endian cross-checks. [CMake](../test/CMakeLists.txt),
[runner](../test/functional/test_runner.py),
[CI test invocation](../ci/test/03_test_script.sh) and
[workflow](../.github/workflows/ci.yml) ground CLI integration.
[Bootstrap guidance](andaluzcoin-mainnet-bootstrap.md) describes prelaunch
operations, not existing public infrastructure.

External primary sources, successfully accessed 2026-10-28: Namecoin Core
`master` auxpow.cpp/.h, historical vinced/namecoin `master` README and official
FAQ (links in section 3). Commit lookup endpoint
`https://api.github.com/repos/namecoin/namecoin-core/commits/master` returned
an accessibility error; exact upstream commits remain UNVERIFIED. These
snapshots need version pinning before a normative future specification.
No secondary summary supplies consensus authority.

| Assumption/unknown | Consequence / dissenting choice requiring review |
| --- | --- |
| SHA256d collision resistance and local library correctness | Binding illustration relies on cryptography; no security proof supplied. |
| Domain/ID/encoding not selected | Canonical new format versus historical exceptions; flexible parent family versus restrictive policy remain disputed choices. |
| Legacy plus auxiliary versus auxiliary-only | Compatibility, accounting and exit risks differ; neither chosen. |
| Parent acceptance not inherently required | Requiring parent inclusion would add liveness/dependency rules needing separate analysis. |
| DAA unchanged for this study | Separate DAA research may still be needed; merged mining cannot cure genesis saturation. |
| Participation, costs and ownership unknown | No live security budget or willingness inference permitted. |
| Toy scope intentionally incomplete | Independent consensus parser, cryptography, operations and economic review required. |

The two external engineering reports contain commands, observations and scope
checks. Review must include untracked new code/documentation as ordinary git
diff alone omits them. No code was staged, committed, published or tagged.
