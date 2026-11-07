# B1 correction proposals and exact-freeze disposition

## 1. Decision, authorization and immutable inputs

**v0.2.86 publishes proposed corrections, not a corrected executable freeze.**
[Tracker #107](https://github.com/andaluzcoin/andaluzcoin/issues/107) follows the
owner's instruction to proceed with the three integration findings and two
clarifications in the [completed v0.2.85 report](https://github.com/andaluzcoin/andaluzcoin/issues/105#issuecomment-6682099167).
The exact requirements are [review R01-R03/Q01-Q02](andaluzcoin-auxpow-b-specification-review.md#3-findings-and-publication-versus-adoption)
and its [finite correction-phase recommendation](andaluzcoin-auxpow-b-specification-review.md#7-next-phase-eligibility-and-completion-boundary).
This addendum supplies concrete replacement proposals, alternatives and the
remaining freeze conditions. It does not claim that the five findings have
implementation/security passes or that documentation CI resolves engineering
choices. **Exact-contract freeze, executable B1 work and adoption remain HOLD.**

Frozen master is **d68c9a2e386cda9878efaa86ff64ddc2a05e96f0**, tree
**bb1e28688cb7b5e75a3196147d19b658678b4bfd**, annotated research tag
v0.2.85-auxpow-b-specification-review-research, object
c47ab9abaf475ac876fbd01627ae29502de3b779. Source links below use this immutable
master; its production source equals the earlier B1 source baseline.

The original [B1 revision 2](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/doc/andaluzcoin-auxpow-b-candidate-specification.md)
prefix remains exactly 51,803 UTF-8 bytes / 665 LF lines, SHA256
`abc2689cd5f0e460a7ff0a6fc08a26d7f9db9fa6f8554a583edb0358ea5ca892`.
Its 523-byte manifest SHA256 is
`33cf3ee36c366a0559473e051423a36f09807d46942521c14e32ad0dd107fbb6`;
raw proposed P is
`a6bf3a4212ae085d505322b78bfd06ebe1566146836b218ba33ff35ea99c251c`.
The frozen review SHA256 is
`3bd4cde7d0ca0512d031228527b88a4cdd7303c7e738d694ba80ead56724865a`.
Append-only navigation links do not alter those frozen interpretations.
**This document does not amend revision 2 under its old P.** No successor P,
official network mapping, activation height or migration is allocated.

All D01-D08 production/evidence gates remain **OPEN**, all 21
[mainnet launch gates](andaluzcoin-mainnet-readiness.md) remain unchecked and
public economic mainnet remains **NO-GO**. Mainnet genesis/PoW/DAA/subsidy,
identity/network settings, descriptor-wallet-only policy, runtime tests and
workflows are unchanged. No real parser, node/miner trial or operation is
authorized by this research publication.

## 2. Parallel method and disposition ledger

Three separately assigned agent-assisted streams examined capacity/presync,
terminal height/genesis, and contract identity/parent offsets. Root read source
bodies, challenged the slot bound and failure classifications, and reconciled
the proposed clauses below. This is one assisted workflow, not independent
organizations, executable verifier implementations or an external security audit.

| Finding | Proposed correction / disposition | Remaining dependency |
| --- | --- | --- |
| R01 | Route-fixed worst-record reservation for every admitted child-vector view; retain FIRST evidence and distinguish reconstruction/admission failure. | Review acceptance-domain change in a new exact contract; actual all-view/serving/recovery evidence. |
| R02 | Exclude the unqualified cap/lookahead combination from implementation-ready claims; specify whole-window reservation and supported-domain obligations. | Select and independently qualify an exact retention/security/resource design. Operational R02 remains OPEN. |
| R03 | Retain the declared height domain with explicit terminal-safe caller/count semantics, not an incidental lower cutoff. | Exhaustive native caller inventory, safe implementation and boundary/resource evidence. |
| Q01 | Explicit conventional six-field P80 offsets and raw-byte/hash semantics. | Confirm intended nonsemantic clarification in the next exact review. |
| Q02 | Explicit trusted-genesis expected-bits/numeric/base-work/evidence procedure. | Review the chosen base case and configured-network fixtures; distinguish it from native admission's bypass. |

Every MUST in sections 3-7 is **proposed successor-contract text only**. No
clause is an instruction to modify today's node. A drafting disposition can be
complete while its operational/evidence obligation remains open.

## 3. R01: uniform child capacity and retained evidence

### Proposed replacement clauses

Let W=4,000,000 be the complete full-view ceiling. Let R(DIRECT)=155 and
R(AUX)=10,362 be the maximum complete HeaderRecord lengths for the sole route
selected by trusted configuration and the child's fixed actual ancestry/height.
These reuse the B1 geometry for this proposal; they are not measurements.

1. The canonical child vector includes minimal CS(transaction count) and every
   serialized TX_WITH_WITNESS byte. Its exact serialized length MUST be at most
   C(route)=W-R(route): **3,999,845 DIRECT; 3,989,638 AUX**. The allowance MUST
   NOT depend on a particular valid attachment's length, arrival order or
   retained FIRST status. Count, current child weight, witness, UTXO, script
   and monetary checks remain separate and mandatory as applicable.
2. Apply the SAME vector limit to full/submitblock, completed compact/blocktxn
   reconstruction, full fallback, proposal, template, disk payload, raw export
   and import. HeaderRecord plus vector MUST still meet the complete W ceiling
   and exact EOF. Disk's 12-byte outer prefix remains outside its payload cap.
   The template's 153-byte prefix and its own complete-view limit also apply;
   these vector limits already reserve a maximum valid completed record.
3. Compact wire and blocktxn request/response limits remain independent. A
   small compact wire view does not establish reconstructed-vector eligibility.
   Enforce incremental serialized-byte/count bounds before allocation/copy and
   the exact completed vector length. Object size, stripped bytes and weight
   are not substitutes. No transaction response or proof alternative enlarges C.
4. Keep FIRST fully checked, durably committed record selection for Hc. A body
   admitted under C then fits with EVERY valid allowed record for that Hc/route:
   recordLen+vectorLen <= R+C = W. Header/full/raw serving uses the retained
   independently valid record and available body. Repair/restart cannot invent
   record validity from six index fields. Missing proof and missing body are
   distinct availability states. No smaller-proof replacement policy is needed
   merely to serve the admitted body.
5. This proposed cap defines **profile-view/body admission and serving**, not
   a new meaning for native consensus-invalid flags. A tentative reconstruction
   that exceeds C, collides, lacks transactions or mismatches a response MUST
   trigger bounded independently verified full acquisition or an availability
   outcome. It MUST NOT permanently poison Hc. Even an independently obtained
   body over C fails this profile's admission; that fact alone is not proof of
   intrinsic current child-consensus invalidity. Genuine child-context/body
   failures require the applicable independent consensus verdict and mutation
   checks. A malformed/invalid A2 never erases valid retained A1.

This selects a simple preferred drafting alternative. The B1
[full/compact/template views](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/doc/andaluzcoin-auxpow-b-candidate-specification.md#L419-L431)
and [FIRST/durability policy](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/doc/andaluzcoin-auxpow-b-candidate-specification.md#L526-L555)
motivate the correction. Native [reconstruction results](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/blockencodings.cpp#L191-L222),
[fallback](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/net_processing.cpp#L3484-L3504)
and [witness/weight mutation ordering](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/validation.cpp#L4195-L4215)
show why transport/reconstruction failures must remain scoped.

The cost is up to **9,974 bytes** less AUX vector capacity than B1 permits
with its minimum 388-byte proof record. The prior conditional 3,995,000-byte
witness-heavy vector would exceed the new AUX allowance by 5,362 regardless
of attachment; no valid mined body/proof fixture is claimed. An alternative
attachment-aware design would need proof replacement/multiple-proof indexing,
serving/import/repair/crash/garbage-collection rules and resource qualification.
Merely accepting A2/body while retaining size-incompatible A1 leaves R01 open.
Increasing W instead changes the wire/resource contract. Neither alternative
is silently included. This admission-domain change requires new revision/P.

## 4. R02: synchronization compatibility and the unresolved design gate

### Proposed replacement clauses

The [B1 presync contract](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/doc/andaluzcoin-auxpow-b-candidate-specification.md#L438-L465)
does not establish that 4,096 per-peer units and 32,768 global units are
compatible with all permitted thresholds. Do not describe that combination as
an implementation-ready inheritance of native progress/security.

1. Retain native commitment/lookahead behavior as the pinned research security
   reference. MAIN's provisional period=641 and lookahead L=15,218 are source
   facts, not newly selected safe B1 parameters. No implicit early release,
   smaller lookahead, substituted threshold, dropped evidence or local-import
   bypass repairs the mismatch.
2. A future exact P2P configuration MUST state its supported anchor/height/time/
   threshold domain, commitment bound, batch-processing order, complete progress
   reservation and proof-receipt lifetime. Trusted CFG1 MinAdmissionWork is the
   stated threshold; a peer cannot choose it. Do not silently replace it with
   native near-tip policy. Zero/already-met thresholds do not demonstrate
   positive-threshold liveness or an adequate general mainnet anti-DoS policy.
3. For inherited whole-batch append-then-pop ordering, B<=16, a conservative
   redownload slot reservation is **L+B+C_outstanding**, where C_outstanding is
   a reviewed bound on remaining sampled commitment entries. Reserve the
   separate complete PRESYNC commitment requirement too. MAIN's header-only
   component is **15,234**, not merely the single-record first release count
   15,219. Include every additional retained/transient receipt, owning buffer
   and copy in explicit slot/byte accounting; compressed C80 is not a proof.
   The formula is a sufficient queue-slot compatibility condition for that
   processing order, NOT a security, RAM-peak or arbitrary-chain progress proof.
4. Global admission MUST reserve a supported peer's entire qualified progress
   window, charge concurrent peers/transients and define scheduling under a
   stated available-capacity assumption. Exhaustion means bounded refusal/
   defer/cancel with released resources, not invalid-child evidence or work.
   Before starting an unqualified combination, report unsupported local sync
   configuration; do not claim consensus failure from the resource limit.
5. Each complete record still undergoes route/linkage/numeric screening before
   provisional claimed-bit work. Redownload independently verifies its full
   record and actual ancestry/expected bits before accepted ledger work.
   A C80 hash commitment or A1 receipt does not authenticate absent proof bytes
   or a substituted A2. Cancellation/restart releases charged state and cannot
   promote unseen evidence, erase historical work or credit it twice.

Inspected [whole-batch processing](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/headerssync.cpp#L98-L136)
appends before [release](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/headerssync.cpp#L241-L292).
[Maximum commitments](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/headerssync.cpp#L33-L43)
depend on current time and anchor MTP; the prior 10,000-equal-work example's
at-most-16 commitments are not a universal maximum. The source
[MAIN parameters](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/kernel/chainparams.cpp#L175-L179),
[security rationale](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/headerssync.h#L63-L98)
and [native threshold provenance](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/net_processing.cpp#L2635-L2645)
must not be conflated with the proposed trusted CFG1 policy.

**Operational R02 and complete exact freeze remain OPEN/HOLD.** The preferred
next investigation preserves the reference defense and qualifies a revised
retention/reservation policy; this is a research recommendation, not a cap
allocation. A separately analyzed new algorithm/parameter set or deliberately
restricted supported domain are alternatives requiring explicit review.
An unmeasured larger cap removes no resource/security obligation; reducing L
can weaken the commitment defense. No numeric repair or synchronization
experiment is supplied here. The finite correction artifact is complete only
as an explicit unsupported-combination disposition with these dependencies.

## 5. R03: a total terminal-height operational contract

### Proposed replacement clauses

Retain B1's proposed height domain 0..M, M=2,147,483,647, and H in1..M.
Do not conceal native overflow with a new incidental consensus cutoff.

1. Distinguish height, successor, entry count, depth/confirmation count and
   native index. Validate disk/external values before arithmetic/conversion.
   For a non-genesis child, its parent height MUST be in0..M-1; compute the
   child in checked wider arithmetic before conversion. A parent at M has no supported descendant:
   refuse before native +1, with no wrap/saturation/height invention or route
   fallback. A block at M remains eligible subject to all other predicates.
2. Its chain entry count is M+1=**2,147,483,648**, a count rather than a signed32
   height. Bounds comparisons MUST NOT narrow the count. Empty Height is -1;
   nonempty Height subtracts one in the count domain before safe conversion.
   Terminal Next returns no successor before addition. Check container maximum,
   count multiplication and allocation; failure is local resource unavailability,
   not intrinsic invalidity, and cannot publish partially authoritative state.
3. At an active terminal tip, every successor-dependent operation MUST return
   a defined no-supported-successor outcome before old native calls: mining/
   templates/proposals, next-height fee/finality/sequence-lock/mempool admission
   or revalidation, and RPCs promising a mineable next block. No fabricated
   successful template or overflowed context is permitted. No production RPC
   code or peer penalty is allocated by these abstract outcomes.
4. Historical/status/locator reads, traversal, proof serving/export, persistence,
   pruning/recovery, restart/import/reindex, invalidation and rollback/reorg to
   an allowed lower branch MUST remain safe. Tip confirmations=1; genesis depth
   at terminal tip can be M+1 and uses a checked wide output representation.
   Equal-height terminal forks must load without computing an invalid successor.
   A safe rollback restores successor-dependent operations after current-context
   checks; terminal state is not a permanent process-wide refusal.
5. Preserve fixed ancestry, historical evidence/work and publication/ancestor
   closure requirements. An exhaustive affected-caller inventory plus actual
   arithmetic/resource/error tests is required before integration. Supporting a
   representable height is not proof that a machine can retain a real M+1 chain.

The original [SetTip resize](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/chain.cpp#L16-L24)
is only one issue. [Index comparison, Next and Height](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/chain.h#L402-L427)
also narrow counts or add one; fixing resize alone is insufficient.
[Mining time/template creation](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/node/miner.cpp#L36-L46),
[assembly](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/node/miner.cpp#L131-L140),
[mempool finality](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/validation.cpp#L146-L167),
[lock points](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/validation.cpp#L211-L223),
[RPC depth](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/rpc/blockchain.cpp#L116-L123)
and [sorted-index restart continuity](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/node/blockstorage.cpp#L454-L467)
give further inspected examples, not an exhaustive audit. Today's code does
not meet this proposed terminal contract. No terminal node/crash/exploit was
constructed. A lower admitted domain is a distinct, separately reviewed chain
termination choice; no such choice is adopted here.

## 6. Q01: exact P80 layout and hash transcript

### Proposed clarification clauses

P80 MUST be exactly the 80 supplied octets. Offsets are zero-based half-open
intervals, without padding, omission, reordering or normalization.

| Interval | Width | Conventional field encoding |
| --- | --- | --- |
| [0,4) | 4 | version: signed-int32 bit pattern, little-endian |
| [4,36) | 32 | previous-header hash: raw serialized digest bytes |
| [36,68) | 32 | Merkle root: raw serialized digest bytes |
| [68,72) | 4 | time: unsigned LE32 |
| [72,76) | 4 | bits: unsigned LE32 |
| [76,80) | 4 | nonce: unsigned LE32 |

The parent branch's raw root MUST equal P80[36:68] byte-for-byte. Parent work
hash is **H2(P80[0:80])**, all and only the supplied bytes. Compare the raw
digest's little-endian uint256 with the child's expected target; display-hex
reversal is not applied to the root, hash input or stored raw digest. Named
parent version/prevhash/time/bits remain opaque work-header fields: do not
decode parent bits as the work target, impose parent consensus/Namecoin flags,
validate parent membership or normalize/re-serialize supplied work bytes.

This is intended nonsemantic precision consistent with the conventional
[field order](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/primitives/block.h#L26-L43),
[hashing](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/primitives/block.cpp#L15-L18),
[double finalizer](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/hash.h#L111-L121)
and [raw/display distinction](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/uint256.h#L74-L120).
No second accepted interpretation or exploit was demonstrated. The next review
must confirm that classification; any changed acceptance needs new revision/P.

## 7. Q02: explicit genesis verifier and durable base case

### Proposed replacement clauses

1. Obtain exact GenesisC80=G and intended ledger parameters from trusted
   configuration. Expected genesis bits MUST be the LE32 at G[72:76], not
   GetNextWorkRequired(null,...). Decode the target with the real numeric rule;
   reject negative/zero/overflow/above-powLimit T_G. Require LE256(H2(G))<=T_G.
   Inconsistent trusted inputs fail configuration initialization. This retains
   B1's general DIRECT numeric predicate as an explicit base case; it is NOT a
   claim that native genesis admission currently performs those checks.
2. Genesis input MUST have byte-identical G, trusted K/P, DIRECT route, zero
   reserved byte, canonical zero proof length and exact EOF: a 155-byte DIRECT
   record. Height is0, pprev is absent as a designated GENESIS case. Reject AUX
   genesis, altered C80, wrong K/P or noncanonical framing. Do not invent a
   predecessor, ancestor receipt, MTP/expected-bits dispatch or descendant
   version/time rule. No current-clock genesis retry applies to this trusted
   fixed anchor. Current native genesis-body/UTXO semantics stay separate;
   header bootstrap does not authorize an arbitrary body.
3. Initial cumulative work MUST be **floor(2^256/(T_G+1))**, added to zero
   once under the stated native uint256 convention. Admission bypass does not
   mean zero genesis credit. Duplicate bootstrap/import/restart/repair adds no
   second increment. A local threshold or clock change cannot erase this
   historical base or require mining a new genesis.
4. For an explicitly reviewed empty successor-profile store, deterministically
   construct the DIRECT genesis record from trusted G/K/P, fully validate this
   dedicated path, compute E, and use reviewed binding/sidecar/index durability
   ordering before evidence-ready/work publication. Its receipt states GENESIS,
   height0 and expected bits; it never claims a validated predecessor. This
   explicit initialization is not generic evidence synthesis for other headers.
5. Restart/reviewed migration MUST check binding, deterministic K/Hc path,
   exact record/E and trusted G again. Missing/conflicting/corrupt binding or
   sidecar requires unavailable/recovery disposition, not automatic legacy-store
   binding, a new genesis or another work credit. A separately specified genesis
   recovery procedure may regenerate its explicit record only after validating
   trusted inputs/durability; it cannot repair arbitrary AUX records from C80.

Native [genesis admission](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/validation.cpp#L4218-L4265)
skips ordinary PoW/context checks; its later min_pow_checked gate is separate.
[GetNextWorkRequired](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/pow.cpp#L14-L16)
requires a nonnull parent. [Real numeric checks and fuzz shortcut](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/pow.cpp#L140-L171)
must be distinguished in future evidence. [Work arithmetic](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/chain.cpp#L120-L133)
and [index initialization](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/node/blockstorage.cpp#L241-L251)
include one genesis increment, despite the ordinary admission bypass.
[LoadGenesisBlock](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/validation.cpp#L4958-L4985)
implements no B1 sidecar. [Current MAIN genesis](https://github.com/andaluzcoin/andaluzcoin/blob/d68c9a2e386cda9878efaa86ff64ddc2a05e96f0/src/kernel/chainparams.cpp#L134-L151)
is preserved exactly; no invalid current genesis is alleged.

A trust-anchor numeric bypass could instead be a named new-contract exception,
but must not coexist with an unqualified DIRECT numeric requirement. Zero-work
genesis contradicts native index initialization. The recommended numeric base
case requires independent configured-network/target fixtures before adoption;
not every imaginable trusted custom configuration is asserted to satisfy it.
No numeric verifier or genesis node experiment was executed here.

## 8. Cross-cutting evidence, publication and failure states

These proposed state requirements complete the correction dependencies; they
do not establish a particular lock, transaction or crash-safety implementation.

| Situation | Required successor-contract disposition |
| --- | --- |
| Genesis-to-tip ancestry includes A with missing sidecar; descendant B has intact evidence. | B cannot regain current candidate eligibility merely from B's record or native nChainWork. Revalidate evidence closure to the explicit genesis base. No arbitrary new trusted anchor/checkpoint is introduced. Historical work facts are not erased; repair A/dependencies without second credit or permanent invalid-child marks. |
| Parent becomes properly invalid while verified child's sidecar I/O is pending. | At the eligibility-publication linearization point protect the relevant mutable context or revalidate it. A per-Hc FIRST lock and immutable E do not protect ancestry. An orphan durable sidecar is not authority to publish work; startup revalidates dependencies. Specify invalidation propagation and crash ordering before integration. |
| Valid A1 plus colliding/mutated/over-cap tentative compact body; later full A2/body. | Keep A1's independent evidence fact. Use bounded full fallback; verify A2 and the actual body independently. No Hc invalidity from reconstruction, alternative-proof failure or local capacity. Separate current intrinsic child-consensus failure and witness/mutation checks. |
| Restart with retained proof but pruned/missing body, or a changed clock/threshold. | Proof availability, historical work, body availability and current eligibility remain separate. No missing-body proof erasure, implicit DIRECT work, unseen evidence promotion or duplicate increment. |

See the review's [integration obligations](andaluzcoin-auxpow-b-specification-review.md#5-critical-decisions-and-evidence-still-required)
and the existing [integration boundary audit](andaluzcoin-auxpow-integration-readiness.md).
Operational resource failure must not become a hidden new chain-validity rule.

## 9. Revision, manifest and immutable interpretation

The combined proposals change acceptance/admission/context requirements.
They MUST enter a **new reviewed revision, changed manifest bytes and distinct
derived P**, never revision2/P with patched prose. Q01 alone is intended
nonsemantic precision; that does not excuse reusing old P for the combined
R01/R02/Q02 contract changes. Retaining R03's domain avoids a new cutoff but
does not remove its native integration requirements.

P hashes the manifest, not all prose, source, configuration or security evidence.
The next freeze MUST bind revision/manifest/P to immutable complete document
bytes/commit/SHA256 and its source/ruleset interpretation. An incremented revision
can identify new semantics; explicit policy labels should make capacity,
presync/support, terminal and genesis choices reviewable. No unresolved labels,
placeholder values or guessed P may masquerade as an exact profile.

Do not incidentally change K/ND1, family marker, slot/branch geometry, stable
ledger binding, immutable H or DIRECT-to-AUX monotonicity. A new P does not
authorize profile coacceptance, store migration, reactivation of DIRECT, an
operational mapping or network deployment. Such compatibility/adoption decisions
remain separately critical. This addendum creates no successor manifest/P.

## 10. Finite acceptance plan and actual evidence boundary

Every C row below is **future UNIMPLEMENTED/UNEXECUTED acceptance evidence**,
mapped to the original V requirements. A document check is not one of these
runtime passes. Allegedly independent implementations must not share their
encoder/expected-result oracle and then claim independent agreement.

| Case | Future independent evidence required | Mapping |
| --- | --- | --- |
| C01 | Exact vector C-1/C/C+1, min/max valid AUX records, both arrival orders; full/compact/blocktxn/fallback/proposal/template/disk/export/import; FIRST serving/repair/restart/crash. Separate profile cap from intrinsic consensus verdict. | R01; V01/V07/V09/V12/V13/V14 |
| C02 | Zero/already-met/positive thresholds, long honest/competing chains; batch1/16, period/offset, cap boundaries, complete commitment/proof reservations; global saturation/fair resumed progress, cancel/restart, allocation/CPU/security bounds. | R02; V05/V06/V07/V18 |
| C03 | Bounded synthetic index/allocator fixtures at M-2/M-1/M, invalid successor, M+1 count/maximum depth, empty chain, all inventoried callers, equal-height terminal forks at restart, rollback recovery, malformed disk heights and allocation/crash failures. Instrument overflow; do not claim a real M-length chain. | R03; V15/V17/V18 |
| C04 | Independent nonsymmetric P80 bytes in all intervals; boundary mutations, raw/display negatives, parent bits not child target, length79/80/81 and exact EOF. | Q01; V01/V02/V03/V08 |
| C05 | Every supported trusted network's exact G/record/E/target/base work, absent-pprev path, changed G/K/P/AUX negatives, bad trusted target, duplicate/repair/restart/clock/threshold, missing binding and durability cuts. Exclude fuzz numeric bypass; record expected and actual numeric verdict. | Q02; V01/V03/V05/V12/V15 |
| C06 | Missing interior ancestor then repair; invalidation during pending I/O; compact bad body then valid full A2 and reverse; retain historical facts with no Hc poison/double work. | Cross-cutting; V07/V09/V10/V12/V13 |
| C07 | New exact manifest known-answer bytes/hash/P and immutable document mapping; old-P/new-semantics rejection; unchanged mainnet/identity/network/descriptor-only invariants and explicit compatibility review. | Revision boundary; V11/V16/V17/V18 |

Actual new evidence in this milestone is source/document inspection, parallel
proposal reconciliation, frozen-prefix/manifest/hash/ProfileID verification,
local/immutable link checks, exact changed-file scope and inert byte/count
arithmetic. The execution report records the results actually obtained and CI.
No candidate parser/verifier, numeric oracle, valid body/proof/UTXO/mined fixture,
sync/native terminal experiment, allocator/performance measurement, fuzz/race/
crash campaign, historical replay, pool interoperability or external security
certificate was supplied. Existing CI tests today's repository, not these
unimplemented clauses. V01-V18 remain future requirements at their stated scope.

## 11. Next exact-freeze gate and research completion

Before presenting a complete successor exact contract: select/review R02's
supported domain and retention/security design; reconcile the proposed R01,
R03 and Q01/Q02 clauses with every view/state; fix all exact literals and error
layers; publish a new complete revision/manifest/P with immutable mapping; and
obtain exact-contract critical review. **Do not infer that decision from green
research CI.** Then separately scope/authorize isolated executable evidence;
only qualified independent results and further critical decisions can support
production integration, activation or operational evidence.

Review-only fixture planning, native caller inventory and relay/storage resource
design can run in parallel without inventing missing normative answers.
The immediate recommendation is the finite **presync retention/security design
and supported-domain investigation**, followed by exact-contract reconciliation;
it is not automatic approval of a smaller lookahead, new cap or implementation.
No fixed milestone count, launch date or GO commitment follows.

Research completion means all five proposed dispositions, tradeoffs, blockers,
revision impact and actual validation are published. Follow issue -> isolated
branch -> GitHub report/PR -> independent exact-head review/CI -> permitted
regular merge -> successful actual-merge master CI -> independently verified
annotated research tag -> final report/closure. Failed/cancelled checks require
their own disposition; older retry approvals do not carry forward.
Completion closes no D gate, future C/V evidence case or mainnet checkbox.

See the [presync design investigation](andaluzcoin-auxpow-b-presync-design.md)
for typed memory, security-model and supported-domain proposals; exact freeze remains HOLD.
