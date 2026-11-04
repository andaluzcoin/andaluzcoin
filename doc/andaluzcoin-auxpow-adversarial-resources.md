# R0 adversarial conformance and resource-bound research

## 1. Status and evidence boundary

**v0.2.81 is research only; public economic mainnet remains NO-GO.**
All 21 [readiness gates](andaluzcoin-mainnet-readiness.md) remain unchecked.
No production parser, proof format, network limit, chain ID, version bit,
activation, mainnet parameter or descriptor-wallet-only policy is changed.

This follows [issue #97](https://github.com/andaluzcoin/andaluzcoin/issues/97)
and the unfinished isolated security/resource work in the
[original decision gates](andaluzcoin-auxpow-candidate-specification.md#14-decision-log-and-independent-acceptance-gates)
and [research sequence](andaluzcoin-auxpow-candidate-specification.md#15-conclusions-sources-and-next-milestones).
Frozen source baseline: `e5fe0905fc500fee92e2a3c26b3b7c1f1eaf87ad`.
A source pin is not an approval of production consensus integration.

The [R0 specification](andaluzcoin-auxpow-proof-serialization-activation.md)
defines an unselected detached study container. Its grammar and limits remain
the subject of this study, rather than newly chosen ALUZ network rules.
The [new offline driver](../test/functional/feature_andaluz_auxpow_adversarial.py)
extends deterministic conformance evidence for the existing reference parsers.
It does not complete a production DoS audit or demonstrate valid parent work,
full transaction validity, replay resistance or miner interoperability.

## 2. Immutable source ledger

Every baseline link below fixes the same ALUZ revision.

| Source | Observed behavior and relevant limit |
| --- | --- |
| [Cursor A and parse_a](https://github.com/andaluzcoin/andaluzcoin/blob/e5fe0905fc500fee92e2a3c26b3b7c1f1eaf87ad/test/functional/feature_andaluz_auxpow_serialization.py#L29) | Slicing traversal, canonical CompactSize, bounded transaction and branch parsing. |
| [Parser B](https://github.com/andaluzcoin/andaluzcoin/blob/e5fe0905fc500fee92e2a3c26b3b7c1f1eaf87ad/test/functional/feature_andaluz_auxpow_serialization.py#L107) | Separate BytesIO/struct decoder with its own length handling and EOF checks. |
| [Common linkage](https://github.com/andaluzcoin/andaluzcoin/blob/e5fe0905fc500fee92e2a3c26b3b7c1f1eaf87ad/test/functional/feature_andaluz_auxpow_serialization.py#L209) | Shared SHA256d, Merkle folding, slot and synthetic commitment predicates; agreement of decoders does not independently verify these helpers. |
| [Existing corpus](https://github.com/andaluzcoin/andaluzcoin/blob/e5fe0905fc500fee92e2a3c26b3b7c1f1eaf87ad/test/functional/feature_andaluz_auxpow_serialization.py#L300) | Fixed vectors, prefix truncations, length/count bounds, linkage mutations and explicit work/monetary noncoverage. |
| [R0 grammar and limits](https://github.com/andaluzcoin/andaluzcoin/blob/e5fe0905fc500fee92e2a3c26b3b7c1f1eaf87ad/doc/andaluzcoin-auxpow-proof-serialization-activation.md#L55) | Experimental envelope, nonwitness transaction subset and exact field bounds. |
| [R0 resource caveats](https://github.com/andaluzcoin/andaluzcoin/blob/e5fe0905fc500fee92e2a3c26b3b7c1f1eaf87ad/doc/andaluzcoin-auxpow-proof-serialization-activation.md#L273) | Existing allocation/transport/performance limits of the evidence; these remain open. |
| [Original security gate](https://github.com/andaluzcoin/andaluzcoin/blob/e5fe0905fc500fee92e2a3c26b3b7c1f1eaf87ad/doc/andaluzcoin-auxpow-candidate-specification.md#L288) | Adversarial/fuzz/resource tests, preallocation evidence and independently reviewed threat assumptions remain required for a real design. |

The pinned Namecoin serialization precedent remains documented in R0 section 2.
R0's output-script commitment, synthetic domain and detached wrapper are
intentional departures; this corpus is not an upstream interoperability suite.

## 3. Threat model and caller assumptions

The attacker-controlled object here is a complete Python byte string supplied
to the research decoder. Its labels, lengths, counts, opaque headers, scripts,
indices and trailing bytes can be changed. Cases do not contact a peer,
construct a live mining job, search a nonce or exercise an actual node.

The caller has already acquired and allocated the input. Rejecting a buffer
before a traversal object is constructed does not prevent upstream network,
decompression, transport buffering or caller allocation. Those layers are
outside this test boundary. BytesIO and slicing also have interpreter/native
implementation costs that the logical counters do not characterize.

Raw containers pass through a decoder before the common linkage model.
`linked_model` requires parser-produced normalized tuples; it is not hardened
here as an arbitrary untrusted-tuple interface. A caller's expected domain and
illustrative slot ID are separate study inputs, not authenticated chain context.
The grammar permits opaque header fields and unsigned monetary bit patterns.
Their acceptance must not be reclassified as complete consensus validity.

## 4. Field bounds and rejection points

| Field or activity | R0 study bound | Required observation |
| --- | --- | --- |
| Supplied container | Exact `bytes`, at most 16384 bytes | Wrong type or 16385-byte sentinel rejects before traversal construction. |
| Transaction payload | At most 4096 bytes | Count decoded canonically and bounded before payload read. |
| Input count/prevout | Exactly one null-prevout input | Zero/witness form, extra input or nonnull prevout rejects. |
| Input script | 2..100 bytes | Bounds checked before script payload read. |
| Output count | 1..16 | Bounds checked before output iteration. |
| Output script | 0..1024 bytes | Length checked before payload read. |
| Each Merkle branch | 0..30 siblings, 32 bytes each | Count checked before sibling iteration. |
| Parent index | Exactly zero | Nonzero rejects structurally. |
| Auxiliary index | Less than `2^auxiliary_depth` | Range checked independently of later slot equality. |
| Fixed fields | Domain 32, child 80, parent 80 bytes | Truncation rejects; headers remain opaque. |
| Transaction/container EOF | Exact consumption | Extra or concatenated data rejects. |

CompactSize requires shortest encoding: one byte through 252, then
`fd`/LE16, `fe`/LE32 or `ff`/LE64 at their respective thresholds.
A huge canonical count must fail its field bound before a payload request or
loop uses it. A nonminimal count fails canonicality even when its value fits.

The accepted-container maximum is independently calculable:
`117 + 3 + 4096 + 1 + 960 + 4 + 1 + 960 + 4 + 80 = 6226` bytes.
The 16384-byte input ceiling is a looser early guard, not another accepted
proof size. Every generated input is capped at 16385 bytes, including the
single-over-limit sentinel. The corpus has at most 4096 cases and is streamed;
the driver must not retain an unbounded list of mutated input copies.

## 5. Case classes and independent expectations

| Class | Structural parsing | Common linkage | Interpretation |
| --- | --- | --- | --- |
| Structural rejection | Both reject with the documented exception class | Not invoked | Invalid R0 grammar, canonicality or study bound. |
| Linkage rejection | Both accept and normalize as expected | False | Well-formed container with an inconsistent synthetic commitment/context. |
| Permitted mutation | Both accept as independently expected | May remain true | Opaque/permitted fields are not automatically invalid. |
| Known noncoverage | Both accept the documented case | May be true | Demonstrates an omitted work, monetary, identity or contextual check. |

Expected classes must be fixed from the grammar and independent evidence,
rather than inferred only because the two parsers return the same result.
Mutation locations and changed lengths must be derived from sealed fixture
offsets or independently checked field metadata. A mutated count can move
subsequent fields; stale offsets are not an acceptance oracle.

Do not assert that every bit or byte flip rejects. Parent version/time/bits/
nonce are opaque. A changed commitment can be accompanied by a recomputed
transaction and parent Merkle root, yielding synthetic linkage without valid
work. Conversely, a structural boundary mutation and a root mismatch fail at
different layers and need separate expected labels.

Useful fixed families include cap−1/cap/cap+1, all CompactSize discriminator
widths, truncated prefixes, nonminimal encodings, oversized count claims,
wrong indices, marker bytes in opaque/cross-field locations, extra data and
input-type variants. Existing independent zero/nonzero-branch hashes and
normalized field facts anchor the corpus without making shared builders an
independent validator.

## 6. Differential agreement and oracle limits

A/B decoder agreement detects differing interpretations or error behavior.
It cannot detect a mistake both implementations share, a common malformed
fixture, a shared hash/slot bug, or an incorrectly assigned expected class.
The same grammar authoring process also limits organizational independence.

Use independent facts alongside differential results: literal fixture bytes/
digests, hand-derived offsets, accepted-size arithmetic, canonical threshold
tables, expected normalized tuples and independently corroborated branch
directions. Record how every fixed oracle was obtained. Exact 64-hex checks
also guard documentation digest transcription; whitespace inside a digest
must not silently become another accepted literal.

Keep parsing, linkage and deliberately uncovered behavior distinct in reports.
No actual parent proof, child-header identity rule, activation transition,
network-domain authentication or production replay test follows from agreement.

## 7. Reversible resource instrumentation

Instrument existing read/traversal/hash boundaries without changing their
results. Restore all wrapped objects and functions on success and failure,
including the injected-exception path. Case generation and fixture hashing
occur outside the measured parse/linkage interval so their work is not
misreported as decoder cost. Apply the same fixtures without instrumentation
to check that observation preserves results.

Source-derived conservative maxima are **144 A `take` calls** and **145 B
`take` calls**, plus at most two B EOF reads: **147 B read operations**.
These combine at most 16 output iterations and 60 sibling reads. Field maxima
need not all be simultaneously reachable under the transaction cap.
The trace records requested widths and positions, not returned byte lengths.
A truncated request is not evidence that its requested length was allocated.

Probe reject-before-use behavior for the whole-buffer guard, transaction
length, output count/script length and each branch count. Confirm an oversized
declared value never drives a payload read or iteration before rejection.
These are logical call-order observations in this Python reference, not an
allocator proof, a bound on native memory, or a guarantee about another parser.

## 8. Hash and performance bounds

Successful linkage performs at most 30 auxiliary and 30 parent Merkle steps,
plus one child-header, one domain-leaf and one transaction double hash:
**63 SHA256d calls**, or 126 underlying SHA256 invocations.
Their first-pass preimages total at most
`80 + 79 + 4096 + 60*64 = 8095` bytes. Each second pass receives 32 bytes,
giving `8095 + 63*32 = 10111` bytes across both passes.
This excludes SHA padding, internal state, interpreter overhead and allocations.

The marker scans cover a bounded transaction/output set. Logical counts and
finite malformed-input probes do not establish production CPU cost, peak RSS,
native allocations, cache pressure or concurrency behavior. Timing or Python
heap observations must identify environment, measurement boundary and omitted
costs; avoid brittle universal wall-clock or memory thresholds in CI.
A deterministic generated corpus is not coverage-guided fuzzing or proof that
all malformed inputs have been considered.

## 9. Reproduction and execution record

Four independently constructed seeds have OpenSSL-derived complete-container
SHA256d seals. The driver uses none of the old R0 fixture/encoder/hash helpers.

| Seed | Bytes | SHA256d |
| --- | ---: | --- |
| Minimal parsing-only | 270 | `b272a2710e55ec3614fb09b38a5f915a286b13cc288b4b35cd06e680b88e0417` |
| Zero branch, linked | 314 | `3bc6dcddc5c6fac2435387a39bde62dedc135775b5b9bbd72177ec5eb6fabfe0` |
| Parent depth 2, auxiliary depth 3, linked | 474 | `5710dab227cd9ebf2e429830873afb47cafff39dc82bcba06abbb44eee9a96de` |
| Both depths 30, transaction 4096, linked | 6226 | `4e9f003b44a721c5f2b625b278ee6f56f343c4e4205a8790eb6b3e198a48c805` |

The maximal linked seed has output-script lengths 44, 1024, 1024, 1024 and 874.
Illustrative external ID 7 and nonce 4294967295 give slot 497393936, checked
independently with integer arithmetic. This establishes no actual ALUZ ID or
parent work. Fixed oracle rows carry expected normalized tuples and linkage
labels; the two parsers' agreement is additional evidence, not the oracle.

Generation order and family counts are fixed:

| Family | Cases | Rule |
| --- | ---: | --- |
| Fixed oracle rows | 29 | Seeds, opaque/linkage/noncoverage controls and structural failures. |
| Truncations | 1267 | Every strict prefix of the three smaller seeds; selected prefix, field-boundary and tail cuts of the largest. |
| Extensions | 16 | Append byte 00, byte ff, profile prefix or the same complete seed. |
| Bit mutations | 1576 | Every byte of the 314/474-byte seeds, flipping bit 0 then bit 7. |
| Byte substitutions | 256 | Four seeds in round-robin order; fixed LCG substitution rules. |
| Insertions/deletions | 115 | Three inserted byte values at 29 fixed offsets, then deletion where an original byte exists. |
| CompactSize fields | 154 | Nineteen fixed values and three nonminimal forms at seven offsets. |
| Parent/auxiliary indices | 36 | Fixed uint32 boundary sets at independently derived seed offsets. |

These are **3449 labeled cases**, not a claim of 3449 distinct byte strings.
The sealed differential result is **1599 parse accepts / 1850 parse rejects**;
accepted normalized outputs must agree exactly. The class counts are not an
independent consensus-validity classification of every generated mutation.
The LCG uses uint32 state 0x02815eed, multiplier 1664525 and increment 1013904223,
two steps per case: first selects an offset; the second supplies its high byte,
toggling bit 0 if unchanged. CLI seed metadata does not alter this corpus.
Ordered offset/value sets are fixed in the driver.

Corpus identity is SHA256 initialized with ASCII `ALUZ-R0-CORPUS-281` followed
by NUL. Each case appends label-length LE16, ASCII label, input-length LE32 and
exact input bytes. The sealed SHA256 is
`da83fbf9c52a4c2cd091fc906011e682c6acf76a200c41e0ff8eadc726693278`.
An independent mutator, using the declared rules and independent fixture bytes
without importing the driver or either parser, reproduced **2076069 input
bytes / 2157025 framed bytes** and the fingerprint; OpenSSL also matched it.
This corroborates corpus identity, not every semantic acceptance decision.
Every consumer applies the case/input/unique-label guard before decoding.

Observed corpus maxima are 99 A and 102 B logical reads. A separate 16-output
probe with fifteen 253-byte scripts and one empty script has transaction 4022,
container 6152 and 143 A / 146 B reads. These observations differ from the
conservative 144/147 ceilings. Separate probes cover truncated CompactSize
payloads, input-cap boundaries, early rejection and restoration after an
unexpected reader exception; they do not change the generated corpus seal.
The maximal linked oracle reaches the 63/8095/10111 hash bounds above.

Retain independent reference source, regeneration output, fresh environment/
timing/results, skipped or unavailable checks, technical review and exact CI
revision in [issue #97](https://github.com/andaluzcoin/andaluzcoin/issues/97) and
its PR report. Commands below reproduce the study; they are not independent
multi-platform pass claims or a production performance benchmark.

From a configured checkout, regenerate links with `cmake -S . -B build` if needed:

```sh
python3 test/functional/feature_andaluz_auxpow_adversarial.py
build/test/functional/test_runner.py --jobs=1 feature_andaluz_auxpow_adversarial.py
build/test/functional/test_runner.py --jobs=1 --timeout-factor=40 feature_andaluz_auxpow_adversarial.py
build/test/functional/test_runner.py --jobs=1 --timeout-factor=40 --v2transport --usecli feature_andaluz_auxpow_adversarial.py
build/test/functional/test_runner.py --jobs=1 --timeout-factor=40 --previous-releases feature_andaluz_auxpow_adversarial.py
build/test/functional/test_runner.py --jobs=1 feature_andaluz_auxpow_adversarial.py feature_andaluz_auxpow_work_recovery.py feature_andaluz_auxpow_serialization.py feature_andaluz_auxpow_chainid_domain.py feature_andaluz_auxpow_chainid_spec.py feature_andaluz_auxpow_feasibility.py
build/bin/test_bitcoin --run_test=pow_tests --log_level=test_suite
```

Only enumerated runner metadata is consumed; metadata paths are never opened.
Unknown/abbreviated options, invalid timeouts and optimized Python must reject;
an injected mismatch must exit nonzero. Reproduction commands are instructions,
not fresh validation or multi-platform success claims.

## 10. Remaining real-integration gates

See the [implementation-readiness dossier](andaluzcoin-auxpow-integration-readiness.md)
for the frozen validation, relay, storage and cache entry points, future test
obligations and owner decisions that precede any real parser/consensus patch.

Production review still needs an owner-selected complete format and threat
model, real transaction/witness/proof validation, transport/preallocation
budgets, adversarial resource and fuzz evidence, concurrency/cache analysis,
independent security review and old/new-node activation/reorg tests.
R0's small study caps cannot be promoted into production limits by inference.
Mainnet consensus and descriptor-wallet-only policy remain preserved.
No live mining, pool outreach, deployment or operational evidence is authorized
by this offline milestone; all 21 readiness gates and mainnet NO-GO remain.
