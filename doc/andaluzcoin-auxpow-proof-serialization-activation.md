# Bounded AuxPoW proof serialization and activation research

## 1. Status, scope and baseline

**v0.2.79 is research only. Public economic mainnet remains NO-GO.**
All 21 [readiness gates](andaluzcoin-mainnet-readiness.md) remain unchecked.
No production proof format, chain ID, domain, version bit, activation height,
strictness policy or network limit is selected. Mainnet consensus, identity,
network settings and descriptor-wallet-only policy are unchanged.

This implements the detached experimental-profile portion of the next research
step in [issue #93](https://github.com/andaluzcoin/andaluzcoin/issues/93), following
[v0.2.78](andaluzcoin-auxpow-chainid-domain-compatibility.md) and the
[original decision gates](andaluzcoin-auxpow-candidate-specification.md#14-decision-log-and-independent-acceptance-gates).
Baseline is `b6a72c9383f69c8646843f987f28102f96e7a85f`, annotated
`v0.2.78-auxpow-chainid-domain-compatibility-research`.
ALUZ still has its ordinary [80-byte header](../src/primitives/block.h),
[direct PoW rules](../src/pow.cpp) and existing
[version signaling](../src/versionbits.h). No production source is changed.

R0 is a **deliberately unselected offline research container**, not a Namecoin
proof or proposed official ALUZ serialization. Exact study choices make two
reference parsers comparable without resolving production design decisions.
Parser agreement and synthetic linkage do not establish valid parent work,
full transaction/block validity, replay resistance or interoperability.
Real consensus integration remains blocked on independent review and selection
of the open choices in section 10.

## 2. Immutable precedent and differences

PINNED PRECEDENT: Namecoin revision
`942b14038f3ae704b6c2d50355de835d3ee92288`, the same immutable source used by
the preceding studies. These observations describe code at that revision,
not current network operation or a full historical consensus audit.

| Source | Observed behavior | R0 difference / limitation |
| --- | --- | --- |
| [auxpow.h:87-104](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/auxpow.h#L87) | Witness-capable coinbase, redundant hashBlock, parent branch, local parent index, auxiliary branch/index, pure parent header | R0 wraps a nonwitness subset with explicit length/domain/child fields; omits hashBlock and retains an explicitly checked parent index. Not wire-compatible. |
| [block.h:41](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/primitives/block.h#L41) | Pure child header plus proof when its version flag is set | R0 has a detached container version; selects no ALUZ header flag or attachment rule. |
| [transaction.h:184-238](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/primitives/transaction.h#L184), [transaction.cpp:87](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/primitives/transaction.cpp#L87) | Witness encoding and txid/wtxid distinction; txid excludes witness | R0 rejects witness marker/flag form, uses SHA256d of its exact nonwitness bytes, and makes no witness-commitment claim. |
| [serialize.h:286-362](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/serialize.h#L286) | Canonical CompactSize and generic size guard | R0 applies smaller experimental per-field bounds before loops/payload reads. |
| [serialize.h:666](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/serialize.h#L666) | Generic vector allocation batching | Not a dedicated AuxPoW preallocation/resource budget; R0 makes no performance equivalence claim. |
| [auxpow.cpp:44-69](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/auxpow.cpp#L44) | Auxiliary branch<=30 checked after deserialization; parent Merkle index literal0; at least one input checked | R0 bounds both branches before iteration and parses exactly one null-prevout input. Serialized historical local nIndex/hashBlock are discarded, not checked as R0 checks its index. |
| [auxpow.cpp:70-139](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/auxpow.cpp#L70) | Root/marker in first input scriptSig; markerless historical mode, some trailing bytes accepted | R0 requires a fixed commitment in a zero-valued **output script**, unique marker in the transaction and exact script length. This is an intentional research departure, not a compatible repair. |
| [auxpow.cpp:143-184](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/auxpow.cpp#L143) | Slot arithmetic; indexed Merkle sibling folding | R0 studies those mathematical operations with bounded nonnegative illustrative ID inputs; chooses no header-ID decoder. |
| [validation.cpp:1886](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/validation.cpp#L1886), [pow.cpp:161](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/pow.cpp#L161) | Parent work compared against **child nBits**, proof/flag/context gates remain separate | R0 performs no PoW/target check, parent-ID check, chainwork or contextual acceptance. Successful linkage is insufficient. |

The source checker has no dedicated parent-branch depth cap. Generic
`MAX_SIZE=0x02000000` and vector allocation batches are not a total proof-byte
limit. These are distinct from R0's experimental resource choices.
The separate [basic transaction validator](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/consensus/tx_check.cpp#L19)
has additional monetary/size/input rules; this study does not assume the
AuxPoW checker automatically performs full parent transaction validation.

## 3. Exact experimental R0 grammar

**Every constant and restriction in this section is a study choice, not an
ALUZ network parameter.** Offsets after variable-length fields are computed
from canonical lengths; fixed-width integers below are unsigned little-endian.
Headers and hash fields are raw bytes, not reversed display strings.

| Order | Field | Exact encoding / parsing rule |
| --- | --- | --- |
| 1 | Research label and profile version | Four ASCII bytes `AP79`, then byte `01`; reject every other label/version. |
| 2 | Synthetic domain | Exactly32 bytes; parsing preserves it, linkage compares trusted expected-domain input. |
| 3 | Synthetic child header | Exactly80 opaque bytes; parsing does not interpret version, target or context. |
| 4 | Coinbase length and payload | Canonical CompactSize length<=4096, then exactly that many bytes of the subset in section 4. |
| 5 | Parent branch | Canonical CompactSize count<=30, then count raw 32-byte siblings. |
| 6 | Parent index | LE32, must equal0. |
| 7 | Auxiliary branch | Canonical CompactSize count<=30, then count raw 32-byte siblings. |
| 8 | Auxiliary index | LE32, must be less than `2^auxiliary_count`. |
| 9 | Synthetic parent header | Exactly80 opaque bytes. |
| End | Consumption | No truncation or surplus, including bytes after the parent header. |

CompactSize is one byte for 0..252; `fd` plus LE16 for 253..65535; `fe`
plus LE32 for 65536..4294967295; `ff` plus LE64 above that. Nonminimal
forms reject before the field's profile bound is applied. Huge canonical
lengths also reject at the field bound before payload reads or iteration.

Input must be exact Python `bytes`, at most 16384 bytes, before either decoder
constructs its traversal object. The caller has already supplied those bytes;
this is **not** a P2P preallocation defense. An integrated transport would need
its own framing/buffering controls. Per-field limits imply an accepted R0
container cannot exceed **6226 bytes**; the 16384-byte input ceiling is a
looser early study guard. No compression, recursion or open-ended scanning is
performed. These bounds are not measured production recommendations.

## 4. Coinbase subset and canonicality

The payload is a restricted nonwitness transaction-shaped record:

1. Four opaque version bytes.
2. Canonical CompactSize input count **exactly 1**. Zero rejects immediately,
   so Bitcoin witness marker/flag encoding cannot enter this profile.
3. A 32-byte zero previous hash and LE32 index `ffffffff`.
4. Canonical input script length **2..100**, that many script bytes, then
   four opaque sequence bytes.
5. Canonical output count **1..16**. Each output contains an eight-byte
   value field, canonical script length **0..1024**, and those script bytes.
6. Four opaque locktime bytes, followed by exact transaction EOF.

Values are retained as **unsigned64-bit field representations**, not validated
signed monetary amounts. BIP34 height encoding, MoneyRange, total value,
subsidy, scripts, standardness, parent network policy and block validity are
not checked. The parsers' exact-one-null-input shape is not a claim that
Namecoin's isolated proof checker enforces every one of these subset rules.

The minimal parsed record is62 bytes; a semantically linked fixed vector in
section 7 is106 bytes. Canonical253-byte and1024-byte output scripts,16
outputs and100-byte input script cases are covered. A 4096-byte payload at
both branch-depth bounds yields6226 bytes; a 4097-byte payload rejects.
Large encoded counts never directly control allocation or a loop before
their field limit is checked.

## 5. Synthetic linkage model, separate from parsing

The committed [research test](../test/functional/feature_andaluz_auxpow_serialization.py)
has two independent parsing implementations: cursor/slicing A and
BytesIO/struct B. They share **no parsing or CompactSize decoder helpers**.
They normalize to `(domain, child, transaction, outputs, parent_branch,
parent_index, auxiliary_branch, auxiliary_index, parent_header)`, with tuples
of raw sibling hashes and `(value, script)` output pairs.
Independent implementations were written from the same grammar; this is
agent-assisted reference work, not two independent production security audits.

A separate common mathematical model consumes only tuples returned by a
successful R0 parser. It does not revalidate arbitrary fabricated tuples as
an untrusted-input interface. It checks only these R0 predicates:

- Domain equals the caller's exact32-byte expected synthetic domain.
- Let `H(x)=SHA256(SHA256(x))`, retaining raw digest-byte order. Auxiliary leaf
  is `H(label || domain || H(child80))`, where label is ASCII
  `ALUZ-AUXPOW-R0` followed by NUL (**15 bytes**). Its preimage is79 bytes.
- At each auxiliary sibling, if index low bit is1 hash `sibling || current`;
  otherwise hash `current || sibling`; shift index right. Both branches are
  already bounded by parsing. Reverse the final auxiliary root's32 bytes for
  its commitment representation.
- Exactly one `fabe6d6d` marker occurs anywhere in the raw transaction, and
  exactly one output script contains it. That output must have value0 and
  script **exactly 44 bytes**: marker4 + reversed auxiliary root32 + sizeLE32
  + nonceLE32. No script prefix/suffix, markerless alternative or extra marker
  is accepted by this profile. This output-script placement deliberately
  differs from the source's scriptSig placement.
- Size must equal `2^auxiliary_count`. For an external illustrative ID in
  0..32767 and the commitment nonce, auxiliary index must equal the
  [previously researched slot function](andaluzcoin-auxpow-candidate-specification.md#5-exact-namecoin-slot-arithmetic).
  ID7 in fixtures is a synthetic input, not an ALUZ ID proposal. At depth0,
  changing nonce cannot change the only slot; the nonce-mutation rejection
  test uses depth1.
- Parent branch starts at `H(nonwitness_transaction)`, index0, and must equal
  bytes `[36,68)` of the parent header (raw Merkle root). No witness txid is
  silently substituted.

Shared hash/linkage helpers are intentionally separate from the independent
decoders. Parser agreement does not independently corroborate the linkage
model. Fixed hashes were independently derived with OpenSSL; branch/slot
precedent remains pinned in section 2 and existing research tests.
The container/domain/commitment choices are not a security or replay-resistance
proof: an attacker can rewrite synthetic headers when no actual work/context
validator is present.

Neither child nor parent header version/chain ID is decoded or checked;
strict parent-child ID policy and parent AuxPoW-flag rejection are not modeled.
The fixture's raw child version would extract ID770 under Namecoin-style
signed division, while illustrative ID7 is a separate external slot input.
The model authenticates no relationship between those values. Merkle-tree
mutation and complete parent-block semantics are also outside its checks.

Two explicit noncoverage tests guard the evidence boundary:

- A synthetic parent with **zero nBits** still passes parsing and linkage.
  Thus successful linkage is not valid PoW or target acceptance.
- An extra output with raw value `ffffffffffffffff` still passes the same
  layers. That is not a valid signed monetary amount; no full transaction
  validation or monetary-consensus claim follows.

## 6. Parameterized activation specification

This is a decision-table model, **not node activation code**. Inputs are
candidate-block branch height `h`, hypothetical boundary `H`, post-boundary
policy, explicit mode, proof flag, proof presence and context-known predicate.
Heights must be uint32 study inputs; flag/presence/context must be booleans.
No actual boundary, header bit, time, signaling deployment or fork is selected.

| Context and policy | Before H | At H | After H |
| --- | --- | --- | --- |
| Context unknown, unknown policy or unknown mode | Reject | Reject | Reject |
| Legacy policy | Legacy only | Legacy only | Legacy only |
| Hybrid policy | Legacy only | Legacy or auxiliary | Legacy or auxiliary |
| Auxiliary-only policy | Legacy only | Auxiliary only | Auxiliary only |

All cells also require consistent predicates: legacy mode has no proof flag
and no proof; auxiliary mode has both. Any mismatch rejects. A true table
result means **mode is permitted by these hypothetical inputs**, not that a
proof, child target, block, signaling state or chainwork is valid.
Tests use illustrative `H=10` and h=9,10,11; no ALUZ activation at10 is implied.
Re-evaluation at branch-specific heights can change the result across a
synthetic reorg boundary; the test does not create a fork or exercise node
caches, rollback, persistence, chain selection or old-node compatibility.

A real design must separately specify state derivation from the candidate
block's ancestry, cache invalidation, buried/version signaling, unknown-mode
handling, downgrade paths, transition proofs, old-node splits and recovery.
Parent work must be compared to child target and child chainwork credited
once under a separately reviewed design; R0 does not implement those rules.

## 7. Independent fixed fixture and malformed corpus

The fixed zero-branch fixture was independently assembled outside the
repository using OpenSSL 1.1.1k for every double-SHA256, without the test's
builder or hashlib. All literals below are digest bytes, not reversed display.

| Component | Literal / bytes |
| --- | --- |
| Domain | Raw bytes00..1f |
| Child header | Raw bytes00..4f, exactly 80 |
| Input script / sequence | `0101` / `ffffffff` |
| Output | Value0, exact44-byte commitment from section 5 |
| Parent header | Version 4 as LE32, previous hash `33` repeated 32, raw coinbase txid as Merkle root, then 12 zero time/bits/nonce bytes |
| Child H(header) | `852c98044fb00507122ff63bda7b529566348fc204f72b00dff1afd7b40501e4` |
| Synthetic auxiliary leaf/root | `a16523acc3578eef2892e54a69b410378bfffa29a079b926b015d5d27c94d77a` |
| Coinbase txid | `351b305a551698238ec6de2203a256911d5bf87f3d99ad6d01e80d8a4a1b234f` |
| Parent H(header) | `b26fc616776149ef456ae89800c5934a05395f615ab4fa8b7ce1b9cc2036ed0f` |
| H(entire314-byte container) | `3bc6dcddc5c6fac2435387a39bde62dedc135775b5b9bbd72177ec5eb6fabfe0` |

For this fixture, tx length at offset117 is106; tx is `[118,224)`, parent
count224, parent index `[225,229)`, auxiliary count229, auxiliary index
`[230,234)`, parent header `[234,314)`, commitment `[176,220)`, parent root
`[270,302)`. The commitment size is1 and nonce0. A second independently
assembled minimal parsing-only fixture has tx 62/container 270 bytes and no
commitment; it parses but is not semantically linked.

The nonzero-branch reference was also independently assembled with OpenSSL,
without the test's shared branch/slot helpers. Parent siblings are `50` and
`51` each repeated 32 bytes; auxiliary siblings are `78`, `79`, `7a` each
repeated 32. Nonce1 and illustrative ID7 at depth3 give slot2, directions
**0,1,0**, exercising both concatenation orders. Its tx is106 bytes and
container 474 bytes. Literal results pinned by the committed test:

| Component | Raw digest bytes |
| --- | --- |
| Auxiliary step0 | `7a3d1e0367914a8ed1a6d83c05a0cae73f2c58575427622576ebcd4c859339f5` |
| Auxiliary step1 | `d06c5c92076aecc60830852fd8f597e0cd76ff766f517d0725e1329950d15e6f` |
| Auxiliary root | `df23f4b7fb2199275459196c7140e341095e2bb24475204bdcde7d7dccbd346b` |
| Coinbase txid | `24c99cd69a98a0e98a5c48518635b0f63c891038d05da86c8cbfbd8ddc60dc75` |
| Parent step0 | `59aaf40411d3442293c9e76511eaf295aec0780098f248ee545c44eafd7d5823` |
| Parent Merkle root | `03f924df1ba7dc5b31f6164e566f92c74e9a9ddab2f1725ee137654cac4e18f3` |
| H(container) | `5710dab227cd9ebf2e429830873afb47cafff39dc82bcba06abbb44eee9a96de` |

The checked-in test constructs a deterministic corpus, with the independently
fixed full-container digest guarding the positive fixture's exact bytes.
Expected valid/invalid classes are explicit rather than inferred merely from
parser agreement. It includes depth0/1/2/4/30 cases, every strict truncation
of a 474-byte branched fixture, trailing/concatenated data, unknown profile,
wrong input type, nonminimal fd/fe/ff lengths/counts, huge encoded values,
count/length mismatches, oversized fields, witness/unsupported input forms,
null-prevout/index failures, wrong tree indices, marker duplication, root/size
byte-order errors, changed nonce/domain/child/branches and parent Merkle root.
An all-prefix truncation test is finite bounded coverage, not fuzzing or a
proof that every malformed input has been considered.

To reproduce an independent digest, convert the exact constructed input to
hex, then run outside the committed test:

```sh
printf %s "$inputhex" | xxd -r -p | openssl dgst -sha256 -binary | openssl dgst -sha256
```

The external execution report retains the independent builder and full fixed
fixture hex; the committed test pins expected component/container hashes and
field offsets. No network, miner, node or live parent-chain data was used.

## 8. Resource analysis and limitations

See the follow-up [adversarial corpus and resource-bound study](andaluzcoin-auxpow-adversarial-resources.md).

| Dimension | R0 bound and rejection point | What this does not prove |
| --- | --- | --- |
| Supplied buffer | Exact bytes and length<=16384 before traversal object | Caller/network buffering already occurred; integrated framing still needs a budget. |
| Transaction | Length<=4096 before payload slice/read and inner decoder | Not a production tx weight, fee, subsidy or full validity rule. |
| Input script | Length2..100 before read | Not script execution/BIP34 correctness. |
| Output iteration | Count1..16 checked before loop | Not MoneyRange or accounting. |
| Output script | Length<=1024 before read | Not spendability or standardness. |
| Each branch | Count<=30 before iteration; each sibling exactly 32 | Not an interoperable branch-depth recommendation or a production DoS audit. |
| Linkage hashing | At most60 Merkle folding steps plus bounded child/leaf/transaction hashes | No target check, nonce search, contextual work, cache or reorg safety. |
| Trailing data | Exact transaction and container consumption | No complete consensus canonicality claim. |

Accepted maximum is `117 + 3 + 4096 + 1 + 960 + 4 + 1 + 960 + 4 + 80 = 6226`
bytes. There are no recursive structures, attacker-controlled unbounded loops,
file/socket/network operations or subprocesses in the committed test. BytesIO
is an in-memory traversal choice. The fixed marker scan is over a bounded
transaction. Analytical bounds and small malformed-corpus timings are not a
production CPU/memory benchmark, adversarial resource proof or independent
security certification.

## 9. Reproduction and reporting

From a configured checkout (regenerate generated test links with
`cmake -S . -B build` if the new script is missing):

```sh
python3 test/functional/feature_andaluz_auxpow_serialization.py
build/test/functional/test_runner.py --jobs=1 feature_andaluz_auxpow_serialization.py
build/test/functional/test_runner.py --jobs=1 --timeout-factor=40 feature_andaluz_auxpow_serialization.py
build/test/functional/test_runner.py --jobs=1 --timeout-factor=40 --v2transport --usecli feature_andaluz_auxpow_serialization.py
build/test/functional/test_runner.py --jobs=1 --timeout-factor=40 --previous-releases feature_andaluz_auxpow_serialization.py
build/test/functional/test_runner.py --jobs=1 feature_andaluz_auxpow_serialization.py feature_andaluz_auxpow_chainid_domain.py feature_andaluz_auxpow_chainid_spec.py feature_andaluz_auxpow_feasibility.py
build/bin/test_bitcoin --run_test=pow_tests --log_level=test_suite
```

Only explicit runner metadata is accepted, including coverage paths without
opening them. Unknown/abbreviated options, invalid timeout and optimized Python
reject; test mismatch exits nonzero. Successful child output is stdout.
The issue/PR report records fresh direct/runner/negative/injected-failure
results, independent vectors, skipped/unavailable checks, timing and CI at the
exact revision. Commands here are reproduction instructions, not a claim
that any environment passed them. Upstream parsers/tests were read, not run.

## 10. Decision log and production gates

See the follow-up [mixed-mode work and pool-exit recovery research](andaluzcoin-auxpow-work-recovery.md).

| Unselected decision | Experimental choice / alternative | Required next evidence |
| --- | --- | --- |
| Official proof serialization and attachment | Detached R0 vs source-compatible layouts; no selection | Approved full grammar, all serialization/hash/P2P/disk/cache contexts and independent real-proof corpus. |
| Witness policy | R0 excludes witness; precedent can carry witness | txid/wtxid and witness-commitment specification, malformed/witness interoperability corpus. |
| Commitment location/canonicality | R0 exact output commitment; precedent uses scriptSig and historical alternatives | Compatibility, ambiguity/malleability and miner/pool review before any choice. |
| Domain and ID encoding | R0 synthetic domain-bound leaf plus external illustrative ID | Real network binding, signed/version signaling design, expanded ID audit, no allocation inferred. |
| Resource limits | R0 arbitrary small budgets | Adversarial preallocation, transport and validation budgets, fuzzing and independent DoS review. |
| Parent/child work and transaction validity | Unimplemented by R0 | Complete contextual work/target/transaction validation and independently reproduced negative proofs. |
| Activation, legacy policy and recovery | Parameterized truth table only | Owner-selected mechanism and independent forks/transition/reorg/old-node/rollback tests. |

Issue #93 requires reproducible evidence, review and successful CI before any
release completion; owner release approval remains a separate gate.
This research advances a candidate specification and conformance method; it
does not close the roadmap's production-parser, activation or security gates.
Mixed-mode difficulty, chainwork, pool-exit recovery and separately authorized
operational evidence remain later work. No actual ALUZ ID/format/bit/height,
production integration, deployment, live mining or external outreach follows.
