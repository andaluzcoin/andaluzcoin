# Andaluzcoin AuxPoW candidate specification and chain-ID compatibility

## 1. Executive decision

**Research only; public economic mainnet NO-GO.** No consensus change,
activation, official ALUZ chain ID, parent chain or wire format is selected.
All 21 [readiness gates](andaluzcoin-mainnet-readiness.md) remain unchecked.
This is a candidate decision package, not a BIP, release or complete validator.

Evidence hierarchy and status labels throughout:

- **VERIFIED ALUZ CURRENT**: frozen local source alone determines current consensus.
- **SOURCE-PINNED PRECEDENT**: external immutable code describes that revision.
- **CANDIDATE/PROPOSED**: conditional, non-binding preferences requiring approval.
- **OPEN BLOCKER**: unresolved design or evidence required before implementation.
- **TOY TEST ONLY**: bounded arithmetic/synthetic fields; no real proof acceptance.

## 2. Frozen baseline and present rules

VERIFIED ALUZ CURRENT: branch `research/auxpow-spec-chainid-compatibility`,
HEAD/master/origin/master/peeled `v0.2.76-sha256d-auxpow-feasibility-research`
all `e80901170a1faf7b6fda4ffd3b5f3c1cb9a7651d` before edits.
[Feasibility](andaluzcoin-sha256d-auxpow-feasibility.md) and
[sustainability](andaluzcoin-mining-sustainability.md) remain unchanged.
Their synthetic linkage and normalized rate scenarios are educational evidence.

| Current source | Verified behavior / future impact |
| --- | --- |
| [block.h](../src/primitives/block.h), CBlockHeader serialization:42; [block.cpp](../src/primitives/block.cpp):15; [hash.h](../src/hash.h):115 | Six fields total 80 bytes; SHA256d identity; no auxiliary proof field. Future proof exclusion from identity must be explicit to avoid circular commitments. |
| [chainparams.cpp](../src/kernel/chainparams.cpp):98-103,149; [params.h](../src/consensus/params.h) | 600-second spacing, 1209600-second timespan, 2016-block retarget; no mainnet min-difficulty fallback; genesis bits `0x1e00ffff`. |
| [pow.cpp](../src/pow.cpp):146-170; [pow.h](../src/pow.h) | Reject negative, zero, overflowing or above-limit target; ordinary child hash must be <= target. |
| [arith_uint256.cpp](../src/arith_uint256.cpp):175-220 | Compact representation truncates; configured powLimit compact-encodes to `0x1e00ffff`, so genesis is compact-saturated. |
| [chain.cpp](../src/chain.cpp):121-133 | GetBitsProof computes floor(2^256/(target+1)); accumulated work credits each child once. |
| [validation.cpp](../src/validation.cpp), CheckBlockHeader / ContextualCheckBlockHeader / AcceptBlockHeader | Direct child work, contextual expected bits/time/version, presync and accumulated header work assume present header format; auxiliary mode needs separate review at every entry point. |
| [miner.cpp](../src/node/miner.cpp), CreateNewBlock:122-235 | Ordinary template and coinbase assembly with child nBits; no parent work interface. |
| [transaction.cpp](../src/primitives/transaction.cpp):69-92; [transaction.h](../src/primitives/transaction.h); [uint256.h](../src/uint256.h) | txid excludes witness; wtxid includes witness; raw hash storage and display order differ. |

ASERT and AuxPoW are unimplemented. Old nodes still check the child hash;
a parent proof cannot be assumed acceptable to them. Header presync, P2P/disk
serialization, validation caches, fork choice and template interfaces would
all need an independently reviewed future change.

## 3. Immutable primary-source ledger

SOURCE-PINNED PRECEDENT, independently retrieved/read on 2026-10-29 UTC.
Commit identity API evidence from original research remains in the external
reports; source content was inspected, including the corrected hash paths.
Each link fixes a revision; no moving-master evidence is used here.

| Project / immutable commit | Paths, functions, lines and evidence | Confidence / gaps |
| --- | --- | --- |
| Namecoin `942b14038f3ae704b6c2d50355de835d3ee92288` | [auxpow.cpp:41-165](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/auxpow.cpp#L41): CAuxPow::check/getExpectedIndex; [auxpow.h:88-106](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/auxpow.h#L88): serializer | Direct primary code; no full interoperability audit. |
| Same Namecoin revision | [pureheader.h](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/primitives/pureheader.h): version bit 8, signed version division by 65536 for chain ID; [pureheader.cpp:11](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/primitives/pureheader.cpp#L11) and [hash.h](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/hash.h): SHA256d | Signed extraction is not unrestricted unsigned high-bit extraction. |
| Same Namecoin revision | [chainparams.cpp:179](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/kernel/chainparams.cpp#L179); [validation.cpp:1886-1940](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/validation.cpp#L1886) | Main ID and contextual routing confirmed; parent work checked against child bits, not complete parent-network validity. |
| Huntercoin `6aa3da0bbe4a7d16352c02f07369a00ae78fcf59` | [main.cpp:1710](https://github.com/chronokings/huntercoin/blob/6aa3da0bbe4a7d16352c02f07369a00ae78fcf59/src/main.cpp#L1710): GetOurChainID; [main.h:1112-1123](https://github.com/chronokings/huntercoin/blob/6aa3da0bbe4a7d16352c02f07369a00ae78fcf59/src/main.h#L1112): GetHash/GetPoWHash; [util.h:612-621](https://github.com/chronokings/huntercoin/blob/6aa3da0bbe4a7d16352c02f07369a00ae78fcf59/src/util.h#L612): two SHA256 calls | Corrected source path: no src/hash.h at this pin. Original 404 resolved as a path issue, not consensus failure. |
| Same Huntercoin revision | [main.cpp:1764-1804](https://github.com/chronokings/huntercoin/blob/6aa3da0bbe4a7d16352c02f07369a00ae78fcf59/src/main.cpp#L1764); [auxpow.cpp:21](https://github.com/chronokings/huntercoin/blob/6aa3da0bbe4a7d16352c02f07369a00ae78fcf59/src/auxpow.cpp#L21) | [auxpow.h:GetParentBlockHash](https://github.com/chronokings/huntercoin/blob/6aa3da0bbe4a7d16352c02f07369a00ae78fcf59/src/auxpow.h#L42) routes parentBlock.GetPoWHash(algo); main.cpp checks algorithm equality. Historical implementation, not a portable normative model. |
| Myriad `35fa3b702864d9ac9e1fa257403f58b4f452fc3b` | [chainparams.cpp:76-78](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/chainparams.cpp#L76); [validation.cpp:1092-1098](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/validation.cpp#L1092) | ID and SHA256d/Scrypt auxiliary routing confirmed. |
| Same Myriad revision | [pureheader.cpp:17-27](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/primitives/pureheader.cpp#L17); [hash.h](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/hash.h): SerializeHash -> CHashWriter -> CHash256::Finalize | SHA256d routes to GetHash, then serialized double SHA256. Other algorithms are outside this inventory. |

The original engineering reports retain incomplete-check labels as historical
records; this revision supplies the missing path evidence. No source conflict
with the Namecoin model was found. Huntercoin uses a different historical
integer implementation; this study does not substitute it for Namecoin's code.

## 4. Bounded chain-ID inventory

SOURCE-PINNED PRECEDENT, **NON-EXHAUSTIVE**, no reservation registry.

| Project / network at pin | Numeric ID | Algorithm / proof rule | Unknown |
| --- | --- | --- | --- |
| Namecoin main | `0x0001` = 1 | SHA256d; strict parent same-ID rejection; links in section 3 | Current operation and miners |
| Namecoin test | `0x0001` = 1 | SHA256d; strict ID flag false (chainparams:346-347) | Cross-network separation cannot follow from ID alone |
| Huntercoin main | `0x0006` = 6 | ALGO_SHA256D=0 routes GetHash -> Hash in util.h; algorithm-indexed IDs; main rejects parent same ID | End-to-end interoperability and current operation |
| Myriad main | `0x005A` = 90 | SHA256d auxiliary branch accepted; strict ID flag false | Other networks, current operation and parent compatibility |
| ALUZ | UNKNOWN / unselected | Ordinary SHA256d, no AuxPoW ID | All future ID decisions BLOCKED |

Huntercoin's Scrypt ID 2 is outside the SHA256d inventory. Network magic,
genesis identity, BIP9 signaling and pool job configuration are distinct from
auxiliary chain IDs. No mining support, exhaustive ecosystem coverage or
Bitcoin compatibility follows from these four rows.
Repeat investigation: identify repository provenance, pin commit via public
commit API, search that tree for `nAuxpowChainId`, `GetOurChainID`,
`ALGO_SHA256D`, `GetPoWHash` and `CheckProofOfWork`, trace hash helpers and
network parameters, and record gaps. Expand the audit before any ID proposal.

## 5. Exact Namecoin slot arithmetic

SOURCE-PINNED PRECEDENT: auxpow.cpp:143-165 takes uint32 nonce, signed int
chain ID, unsigned h; uint32 modulus `1u << h`; uint64 intermediates, two
multiply/add operations, reduction after each, and ID addition between them.
The checker limits branch height to 30. This model restricts IDs to
0..2147483647, nonce to 0..4294967295, h to 0..30 and rejects bools.
That study domain is not a claim all IDs fit the signed header-version field.
Negative upstream IDs and signed header encoding need separate analysis.

With a=1103515245, c=12345, m=2^h:
`slot = (a * (((a*nonce+c) mod m) + ID) + c) mod m`.
The largest intermediate in this nonnegative domain fits uint64.
For fixed nonce/h, slot difference is `a*(ID2-ID1) mod m`.
Since a is odd, gcd(a,m)=1: equal slots **iff** equal ID residues mod m.
Nonce changes cannot separate congruent IDs. At h=0 every ID uses slot 0.
At h>0, m residue classes map bijectively to m slots; more than m children
force a collision, and distinct numeric IDs alone do not prevent collisions.

## 6. Collision and replay matrix

TOY TEST ONLY: illustrative IDs 1 and 17 are inputs, not ALUZ proposals.
The following fixed nonce=0 rows come from independent C++ arithmetic.

| h | slot ID=0 | slot ID=1 | slot ID=17 | 1 versus 17 |
| --- | --- | --- | --- | --- |
| 0 | 0 | 0 | 0 | Same only slot |
| 1 | 0 | 1 | 1 | Distinct IDs, equal residues |
| 2 | 2 | 3 | 3 | Distinct IDs, equal residues |
| 4 | 14 | 11 | 11 | Distinct IDs, equal residues |
| 8 | 126 | 235 | 187 | Different slots |
| 16 | 5758 | 25835 | 19387 | Different slots |
| 30 | 333190782 | 362964203 | 839338939 | Different slots |

The test repeats heights with nonce 0,1,2147483648,4294967295 and IDs 1,
1+2^h: equality holds at every nonce; ID 0 versus 1 differs whenever h>0.
Equal numeric IDs always collide at equal nonce/h. Distinct IDs can collide.
Changing height may separate residues; changing nonce alone cannot.

| Situation | Consequence / status |
| --- | --- |
| Same ID in two networks | Arithmetic gives no domain separation; explicit network binding OPEN BLOCKER. |
| Two children in one tree | Distinct slots necessary for distinct leaves, insufficient for security or replay resistance. |
| Different nonces | Each proof must bind its own nonce; no modular collision cure. |
| Replay with altered child | Toy decoder rejects changed bytes; real commitment and contextual validation unimplemented. |
| Production ID allocation | BLOCKED pending expanded source audit, encoding and network-domain design, independent review. |

## 7. Candidate envelope and framing decisions

All rows are CANDIDATE/PROPOSED with OPEN BLOCKER details; **byte layout OPEN**.
No lengths below are production allocations.

| Decision | Conditional preference | Alternative / tradeoff / approval needed |
| --- | --- | --- |
| Child identity and proof attachment | Fixed child identity excludes attached proof, avoiding circular hash | New extended identity changes tooling and commitment rules; consensus reviewer must specify every serialized context. |
| Mode/version | Explicit unambiguous discriminator with unknown modes rejected | Reuse version bits risks BIP9/legacy conflicts; release owner must approve bit and dispatch. |
| Chain/domain identity | Network-specific binding for main/test/regtest and strict parent-child separation | Shared numeric ID plus separate domain may aid tooling; actual compatible encoding remains OPEN. |
| Framing | Exact canonical length, reject surplus/ambiguous encodings | Permissive historical formats ease compatibility but increase malleability; no format inherited automatically. |
| Allocation/CPU | Validate CompactSize canonicality and bounds before allocation | Deferred checks risk DoS; total proof/transaction/branch budgets require measurements and review. |
| Tree | Bounded power-of-two size coupled to height, nonce and expected index | Alternate slot functions would break precedent compatibility; ID width/height limits need approval. |
| Witness policy | Explicit txid/nonwitness identity and bounded serialization policy | Reject witness or carry witness: bandwidth and compatibility differ; neither chosen. |

## 8. Coinbase, Merkle and parent evidence obligations

SOURCE-PINNED PRECEDENT: Namecoin check:41-139 computes the auxiliary root
from the child hash and indexed sibling branch, reverses its 32 stored bytes
for script search, checks parent membership using coinbase **txid** at index
zero, and requires at least one input. Left/right sibling order follows index
bits (CheckMerkleBranch:169 onward); root size and nonce are LE32.
The marker, if found, must be unique and adjacent immediately before the
first matched root. With no marker, historical root offset <=20 is allowed.
Eight following bytes are required; size must equal 2^height and index must
match the nonce/ID function. This does not establish universal root uniqueness,
exact trailing length, full coinbase validity or complete parent validity.

Serializer auxpow.h:88-106 carries TX_WITH_WITNESS coinbase, a redundant
hashBlock local, parent branch and index local, auxiliary branch/index and
pure parent header. Parent membership uses txid rather than wtxid; serializing
witness does not make a witness commitment mandatory in this checker. The
redundant fields are not fully canonicalized/verified by `check`.

CANDIDATE/PROPOSED: prefer one mandatory marker with unique root placement
and explicit adjacency, bounded parent branch/index zero, precise txid rules,
coinbase structure and mutation/script constraints. Alternate markerless
precedent eases historical compatibility but permits additional encodings.
OPEN BLOCKER: real transaction parsing, null prevout/coinbase constraints,
witness/txid policy, branch mutation handling, parent hash definition and
accepted parent header semantics. Repeated roots, duplicate markers, ambiguous
search and trailing bytes require independently agreed rejection vectors.

## 9. Header identity, target and chainwork

VERIFIED ALUZ CURRENT: child SHA256d must satisfy child nBits. SOURCE-PINNED
PRECEDENT: Namecoin validation:1886-1940 rejects mismatched proof/mode flags,
checks configured chain ID conditionally, rejects auxiliary-mode parent headers,
and compares parent hash with **child** bits before checking linkage.
Checking parent work against child target does not prove parent network
acceptance, parent transactions, parent target or parent-chain membership.

CANDIDATE/PROPOSED: retain an 80-byte child identity and pure 80-byte parent
header, proof outside child hash; credit child target-derived work once,
independent of parent difficulty and other children. Alternatives (extended
identity or parent-work-derived credit) need separate fork-choice analysis;
parent difficulty credit risks disproportionate child chainwork.
OPEN BLOCKER: all header-only/presync paths, contextual child expected bits,
timestamps, version restrictions, orphan proof availability, cache identity,
reorgs and mixed-mode fork work. No field layout or proof validity is defined.

## 10. Strict rejection and DoS matrix

CANDIDATE/PROPOSED requirements; real implementations and budgets OPEN BLOCKER.

| Input/failure | Required future rejection / evidence | Present coverage |
| --- | --- | --- |
| Missing proof, unknown mode, conflicting version | Reject before mode-dependent interpretation; contextual activation vectors | None |
| Truncation, surplus, noncanonical CompactSize, overflowing count | Reject before dynamic allocation; bound byte/CPU cost | Toy fixed-length fields only |
| Negative/oversized/bool model parameters | Reject invalid domains | Toy arithmetic tests |
| Wrong size, non-power-of-two, height/index/nonce mismatch | Bind size=2^h, index to nonce/ID; bound both branches | Toy height/size/index/changed nonce |
| Duplicate/absent/misplaced marker or repeated root | Single canonical commitment, resolve ambiguity | Toy marker and fixed root positions only |
| Wrong hash order, LE32 swap, altered child/domain | Reject mismatched commitment and network binding | Toy bytes only |
| Bad coinbase, witness ambiguity, mutation | Real bounded tx decoding and reviewed membership rules | Explicitly uncovered |
| Invalid parent work, child target/time/bits | Reject with contextual child rules; no reliance on parent's claimed bits | Explicitly uncovered |
| Same parent-child ID / wrong network | Agreed strict policy and domain binding | OPEN; no real ID parser |
| Oversized proof, huge branch, costly scripts | Preallocation bounds, total size and CPU budgets, fuzzing | OPEN; toy fixed length is no resource benchmark |
| Cross-activation/reorg invalid mode | Height/context-dependent validation, recovery vectors | None |

The toy decoder does not implement CompactSize. Its refusal of short/extended
LE32 inputs is only an illustrative canonical fixed-field boundary.

## 11. Activation and old-node compatibility

All future options OPEN BLOCKER; legacy current behavior remains authoritative.

| Mode | Compatibility consequence | Acceptance evidence required |
| --- | --- | --- |
| Legacy SHA256d only | Present format and direct child work remain | Existing regression tests; operational readiness remains open. |
| Hybrid legacy plus AuxPoW | Upgraded nodes dispatch by reviewed mode; old nodes may reject parent-only work | Mode ambiguity, downgrade, competing branches, activation boundary and reorg vectors. |
| AuxPoW only after activation | Legacy work must be rejected contextually by upgraded nodes | Explicit activation rule, old-node split analysis, pool exit/stall and rollback drills. |

Signaling mechanism, height/time and legacy policy are unselected. An old node
cannot validate a newly attached proof merely because the pure child remains
80 bytes. If child work happens to pass, that still does not imply protocol
compatibility. Rollback after divergent accepted histories can split the
chain; coordinated recovery needs an independent owner-approved plan.

## 12. DAA, saturation and participation

VERIFIED ALUZ CURRENT: legacy DAA and compact-saturated powLimit persist.
AuxPoW does not change difficulty response or rescue a chain with no miners.
ASERT research is separate. Parent hash rate does not automatically become
child security: only miners committing to and submitting child work count.
Operator concentration, censorship, withholding, reorgs, job/payout overhead
and correlated pool withdrawal require evidence. Participation, revenues,
attack costs and economic viability remain UNKNOWN; no outreach occurred.

## 13. Reproducible offline model

TOY TEST ONLY: [research test](../test/functional/feature_andaluz_auxpow_chainid_spec.py),
stdlib only, eight unittest methods with subcases, sixteen literal slot vectors.
Independent reference: GCC 13.3 C++17, uint64 intermediates and explicit modulo,
140 rows across heights 0,1,2,4,8,16,30; four nonce edges and five IDs.
The external execution report contains full reference source and values;
all 16 literals were checked against those rows. It is an arithmetic cross-check,
not an independent consensus implementation or upstream test harness.

Fixed LE32 vectors: 0=`00000000`, 1=`01000000`, 0x12345678=`78563412`,
4294967295=`ffffffff`. Raw bytes 00..1f display as 1f..00.
The 84-byte synthetic marker/domain/child/reversed-child/size/nonce/index
record is deliberately non-transaction data, not a candidate wire allocation.
Truncation, surplus, domains, child bytes, marker placement/duplication, endian,
size and index mutations are rejected. Real coinbase, serialization, witness
validation, parent work and contextual child validation are explicitly absent.

Reproduce from repository root (scratch caches outside repository):

```sh
PYTHONPYCACHEPREFIX=/tmp/aluz-277-pycache python3 -m py_compile test/functional/feature_andaluz_auxpow_chainid_spec.py
python3 test/functional/feature_andaluz_auxpow_chainid_spec.py
build/test/functional/test_runner.py --jobs=1 feature_andaluz_auxpow_chainid_spec.py
build/test/functional/test_runner.py --jobs=1 --timeout-factor=40 feature_andaluz_auxpow_chainid_spec.py
build/test/functional/test_runner.py --jobs=1 --timeout-factor=40 --v2transport --usecli feature_andaluz_auxpow_chainid_spec.py
build/test/functional/test_runner.py --jobs=1 --timeout-factor=40 --previous-releases feature_andaluz_auxpow_chainid_spec.py
```

CLI uses allow_abbrev=False; only specified runner metadata accepted. Paths are
never opened or written by the child. Successful child stderr is empty and
unittest output goes to stdout. Unknown/abbreviated options and optimized Python
exit 2. Injected assertion failure in a scratch copy exits 1. No subprocess,
sockets, downloads, mining or files are used inside the committed script.
Four single-test runner variants and existing compiled pow_tests are local
validation only; no GitHub CI or multi-platform result is claimed.

## 14. Decision log and independent acceptance gates

CANDIDATE/PROPOSED owner roles below are requirements, not assigned people or
completed approvals. No mainnet readiness gate is satisfied by this study.

| Owner gate | Unresolved decision / dissenting alternative | Independent acceptance criterion |
| --- | --- | --- |
| Project owner + ecosystem researcher | Numeric chain ID, encoded range, network binding; shared versus separate domains | Expanded immutable inventory, signed/header encoding analysis, no claim of reservation. |
| Consensus reviewers | Proof envelope, canonical marker versus historical markerless behavior; witness carry versus exclusion | Two independently implemented bounded parsers agree on exact positive/negative corpus. |
| Consensus + networking maintainers | Pure header identity and proof attachment, discriminator and BIP9 overlap | Serialization/hash/presync/P2P/disk/cache vectors; unknown-mode rejection. |
| Security reviewer | Parent-child ID strictness, mutation, allocations and proof budgets | Adversarial/fuzz/resource tests, preallocation proof and reviewed threat assumptions. |
| Consensus + DAA reviewers | Child target, once-only chainwork, legacy/hybrid/AuxPoW mode | Independent integer target/work vectors, fork/reorg/activation tests. |
| Release owner + operators | Signaling, activation, rollback, pool withdrawal | Explicit approval, isolated recovery drills and separately authorized participation evidence. |

Immediate implementation remains BLOCKED. Reviewers must agree on exact status
boundaries and all open choices before any real parser or consensus patch.
No chain ID, limit, bit or activation choice can be inferred from toy constants.

## 15. Conclusions, sources and next milestones

The section 3 immutable source ledger is the external authority for precedent;
section 2 local sources govern ALUZ. These findings establish modular collision
behavior and bounded historical ID evidence. They do not establish mining
security, ecosystem completeness, interoperability or live operation.

Next three separately reviewed research milestones:

1. Expand the pinned SHA256d ID/domain audit and resolve signed version encoding,
   cross-network replay and parent-child policy; owner reviews all choices.
2. Publish a precise bounded proof/serialization and activation specification,
   then obtain independent parser/vector agreement and DoS review in isolation.
3. Study mixed-mode difficulty/chainwork/reorg and pool-exit recovery, followed
   by separately authorized operational evidence gathering and security review.

**NO-GO remains. No production consensus changes.** Owner and ChatGPT review
must precede staging or any publication. No official ALUZ ID is selected.
