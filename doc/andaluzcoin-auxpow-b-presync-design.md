# B1 presync memory, security and supported-domain investigation

## 1. Decision and frozen inputs

**v0.2.87 is a research design, not implementation or parameter adoption.**
[Tracker #109](https://github.com/andaluzcoin/andaluzcoin/issues/109) follows the
owner's instruction to investigate synchronization memory/security after the
[v0.2.86 completion report](https://github.com/andaluzcoin/andaluzcoin/issues/107#issuecomment-6701399793).
Exact scope comes from [correction R02](andaluzcoin-auxpow-b-specification-corrections.md#4-r02-synchronization-compatibility-and-the-unresolved-design-gate),
[C02](andaluzcoin-auxpow-b-specification-corrections.md#10-finite-acceptance-plan-and-actual-evidence-boundary)
and its [next exact-freeze gate](andaluzcoin-auxpow-b-specification-corrections.md#11-next-exact-freeze-gate-and-research-completion).

Frozen master B is **261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a**, tree
**704972911f6f7737bd9227c7ed6b90239e337731**. Its verified annotated research
tag v0.2.86-auxpow-b-specification-corrections-research has object
dedbc6b16e40478a4942ef5cd9981a3f7d8bc151. All source links below pin B.
The 32,090-byte / 412-LF correction document SHA256 is
`fcf7f6c749e9fa18d5c38d9e8dd821caafcdf1ff59515f7e638f43175c684195`.
The original B1 normative prefix remains 51,803 bytes / 665 LF, SHA256
`abc2689cd5f0e460a7ff0a6fc08a26d7f9db9fa6f8554a583edb0358ea5ca892`;
its 523-byte revision2 manifest and raw proposed P
`a6bf3a4212ae085d505322b78bfd06ebe1566146836b218ba33ff35ea99c251c`
are unchanged. Navigation additions never amend that interpretation.

**Decision:** recommend conditional design **S1**, with typed whole-session
reservations, complete immutable redownload records and an ordered drain.
This removes the paper 4,096/window contradiction within an explicit supported
domain. It does **not** establish acceptable native RAM, CPU, global service or
permanent-storage security. New analysis also shows that changing batch size
invalidates automatic inheritance of the native tuning result. Operational
R02 and a complete successor exact freeze remain **OPEN/HOLD**.

All D01-D08 production/evidence gates remain OPEN, all 21
[mainnet launch gates](andaluzcoin-mainnet-readiness.md) unchecked, mainnet
**NO-GO**. Mainnet genesis/PoW/DAA/subsidy/identity/network parameters,
descriptor-wallet-only policy, runtime tests and workflows are unchanged.
No new cap, lookahead, threshold, manifest/P, mapping, activation or executable
B1 work is authorized by this dossier.

## 2. Method and source facts

Three parallel agent-assisted streams examined memory/ownership, security/cost
and supported-domain/progress. Root read source bodies and reconciled their
cross-cutting claims. Scalar results were cross-checked through separately
organized calculations: an offset loop and algebraic offset averaging; exact
rational sums bracket the comparison points. This is one assisted workflow,
not independent verifier implementations or an external security audit.

| Pinned source | Fact and consequence |
| --- | --- |
| [MAIN parameters](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/src/kernel/chainparams.cpp#L175-L179) | Period p=641/lookahead L0=15,218 are explicitly provisional pending a nonzero chainwork checkpoint. They are comparison inputs, not qualified B1 settings. |
| [Constructor/finalization](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/src/headerssync.cpp#L17-L62) | Native commitment maximum is frozen from local start time and anchor MTP, with fresh salt/offset. A chain growing after that snapshot can need a restart. |
| [Batch processing](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/src/headerssync.cpp#L68-L174) | PRESYNC tests threshold after the whole batch. REDOWNLOAD appends the whole batch before popping; a result can outlive finalization. |
| [Sampling](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/src/headerssync.cpp#L177-L208) | Native push occurs before the maximum check; failure may temporarily own K+1 entries. A successor must charge it or refuse before insertion. |
| [Redownload/release](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/src/headerssync.cpp#L215-L292) | Work threshold sets the flush flag before that header's sample check. Subsequent samples are skipped after the flag. The code tests work, not equality with a stored target blockhash, despite comments. |
| [Caller entry](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/src/net_processing.cpp#L2767-L2810) | A first screened batch already meeting threshold goes to full validation directly. Only a full below-threshold batch starts two-pass sync. Positive threshold alone does not imply two passes. |
| [Native threshold](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/src/net_processing.cpp#L2635-L2645) | Native policy includes near-tip work. B1 explicitly selects trusted CFG1 MinAdmissionWork; substituting native policy silently is forbidden. |
| [Caller result handling](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/src/net_processing.cpp#L2685-L2760) | Returned headers replace the caller vector; per-peer state can be destroyed first. Full proof owners cannot disappear with the sync object. |

Current [screening/caller shortcuts](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/src/net_processing.cpp#L2960-L3085)
are not B1 proof permissions. B1 requires complete numeric/route/proof screening
before provisional work, then actual ancestry/expected-bits/context before
accepted evidence/work. A sampled C80 hash excludes attachment bytes; matching
it cannot authenticate a replacement proof, missing sidecar or reused receipt.

## 3. Preferred S1 contract to qualify

Every requirement here is proposed successor text, not today's behavior.
Let M=2,147,483,647, a be a trusted anchor height, p>0 the sampled period,
ell>0 the lookahead and Bmax=16 the maximum complete header batch. S1 keeps
the two-pass salted C80-bit mechanism and append-then-pop/check ordering as its
research reference. **ell must later satisfy a qualified security/cost model**;
L0 is used for examples only.

### Typed reservation and full-height commitment envelope

For n new heights and secret offset o in0..p-1, the exact sample count is

`C(a,n,o)=floor((a+n-o)/p)-floor((a-o)/p)`.

These are mathematical floors; negative intermediates are possible and native
truncation toward zero would undercount. Equivalently, find the first positive
distance d to the next sampled height, then use zero for n<d or
`1+floor((n-d)/p)` otherwise. For every offset, C<=ceil(n/p).

S1 reserves **K=ceil((M-a)/p)** logical commitment bits before starting a session.
Use checked division/remainder rather than overflowing `N+p-1`. Check current
height<M before adding one, then check the reserved bit capacity BEFORE writing.
This avoids a K+1 failure allocation. At a=0,p=641, K=3,350,209 bits and an
ideal packed-array payload is **418,777 bytes**. At a=M there is no new child.

This deliberately **replaces the native frozen-clock commitment cap** with a
full remaining-height envelope. It is a proposed local admission-policy change,
requiring new exact semantics/revision; it is not unchanged native inheritance.
It removes that particular growing-chain/snapshot-length obstruction, while
allowing a responsive low-work peer up to M-a screened records in one session.
That CPU/service exposure is a serious unresolved qualification, not solved by
the small packed-bit payload. Current clock/MTP/context rules still apply.

The native-clock-cap alternative remains possible only with an explicit frozen
horizon/domain and checked nonnegative time arithmetic. Its nominal
`floor(6*(t0-anchorMTP+7200)/p)` needs the complete last PRESYNC batch and offset
count to fit. It cannot claim arbitrary growing-chain progress or accept a
negative signed result converted to a huge unsigned capacity.

### One owner for every retained record

1. Acquire one complete session resource vector atomically: K commitment bits,
   **Q=ell+Bmax** canonical record positions, input/staging/receipt/native
   scratch allowance and downstream drain/durability capacity. Refuse/defer
   before starting if any dimension is unqualified/unavailable. Reserving only
   PRESYNC bits and hoping to acquire the redownload window later can deadlock.
2. Screen every PRESYNC record in bounded input/validation owners, including
   exact bytes, route/height/linkage, claimed-target numeric work and proof.
   Complete the entire batch's screening before committing its provisional
   transcript/work updates; a later bad record cannot publish a screened prefix.
   Compute required E while the record is owned. Afterwards discard that proof
   and per-record screen receipt; retain only sampled C80 bits, bounded cursor
   state and provisional work. No hidden per-header receipt archive. This
   explicit lifetime must be ratified in successor text, not inferred under frozen revision2/P.
3. REDOWNLOAD supplies a fresh complete HeaderRecord for every position. Copy
   it into a reserved canonical slot, freeze bytes and independently screen it;
   finish whole-batch proof screening before provisional state updates. Then
   preserve the reference per-record threshold/sample order described below;
   an A2 attachment inherits no authentication from A1 or a C80 commitment.
   Retain complete canonical bytes and the exact associated E/typed receipt
   through staging, lookahead and release. Hash/receipt-only proof retention
   or a third acquisition at release is not selected by S1.
4. Whole-batch append reaches at most Q positions. Before threshold, pop while
   queue size>ell; at threshold the entire Q window can become release-ready.
   Transfer immutable owners to an **ordered drain cursor**, without copying
   proofs into an uncharged result vector. Staging+lookahead+released-but-not-
   finished owners share the same Q-position reservation.
5. Do not request/process another progress batch until the released cursor has
   drained. Each record undergoes full actual-header-context/evidence admission
   from the fixed parent, including expected bits/MTP/version/time/route and
   the actual retained proof, before once-only work/index publication. Full
   body/UTXO/script checks remain separate. Conservative independent screening
   and final verification may traverse a proof three times across the phases;
   no unqualified cached context-pass substitutes for this work.
6. Keep the canonical owner until the reviewed FIRST sidecar/durability handoff
   releases it. Charge any simultaneous writer copy, job, buffer and owner.
   Persistent accepted index/archive growth is not bounded by temporary Q.
   At publication, revalidate/protect mutable ancestry and evidence closure;
   a per-Hc FIRST lock or public E alone supplies neither guarantee.
7. Cancellation, timeout, bad proof/commitment, disconnect and late completion
   release/fence all generation-bound owners exactly once. Restart uses fresh
   salt/offset. Never promote unseen evidence, restore proof from six fields,
   erase historical work due to data/clock loss or credit duplicate Hc twice.

Old [resource pools](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/doc/andaluzcoin-auxpow-b-candidate-specification.md#L474-L499)
do not silently accommodate this design. If pending means every record awaiting
actual context, a Q-sized window exceeds the old per-peer8/global64 limits.
Successor text must explicitly distinguish and reserve fully screened retained
owners from pending first proof-validation jobs, or change those caps. Merely
renaming entries cannot create a memory exemption. Pending/active jobs, ordinary
block/RPC/import pools and unsolicited messages remain independently charged.

### Conservative global scheduler

S1 admits **one active progress owner globally**, with its entire reservation
held across phases/drain. Other peers get only bounded connection/control and
waiting metadata, no second retained window or uncharged queued message. Bound
and deduplicate waiting requests; exhausted capacity is defer/refuse, not proof
that a child is invalid. A rotation can select peers, but completion requires
an honest cooperative peer eventually obtaining and retaining enough service.

Idle receive deadlines are not a proof against a responsive attacker occupying
the owner for a very long below-threshold stream. A preemption quantum can also
starve every honest session if each restarts before reaching threshold. No
anti-Sybil, no-eclipse, global fairness, acceptable CPU or wall-time result is
claimed. Concurrent sessions are a separate option needing separately reserved
whole windows and a reviewed scheduling/security policy.

## 4. Logical payload accounting, not a RAM cap

R=10,362 is the current candidate maximum complete record, including C80.
The preferred fixed canonical arena reserves Q*R payload capacity, not merely
the sum of currently short record lengths. Separately charge the maximum
165,857-byte input batch when it overlaps canonical copies.

| Comparison input | Q | Canonical arena bytes | Plus one input and worst logical packed bits |
| --- | --- | --- | --- |
| Reference ell=15,218,p=641 | 15,234 | 157,854,708 | 158,439,342 |
| Conditional count-model example ell=15,864,p=641 | 15,880 | 164,548,560 | 165,133,194 |

Neither row allocates a production setting. The second only illustrates why a
security-model change must also update every reservation. With all32 old global
header input slots still available, their raw pool is5,307,424 bytes INCLUDING
the selected session's input; the first arena+that pool+packed bits totals
163,580,909 before overhead. Do not add the selected batch twice, or subtract a
larger wire owner while a slice still pins it. Other declared pools are extra.

A complete native bound must qualify at least

`Q*R + A_bits(K) + A_descriptors(Q) + A_input + A_receipts + A_parse/verify + A_session/peers + A_durable_overlap`.

Each A denotes **allocated capacity**, not serialized length. Unqualified terms
include alignment/control blocks, arenas/handles and growth, parser transaction/
script/branch objects, hash scratch, threads/stacks/jobs, queues/mutexes,
locators/stats/wait metadata, allocator caches/fragmentation and storage overlap.
If retaining native compressed fields too, their48-byte element payload adds
731,232 at Q=15,234, before deque/container costs. Deriving C80 directly from
the full record can avoid that redundant payload only with reviewed ownership.

The [native48-byte assertion](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/src/headerssync.cpp#L13-L15)
does not measure an enlarged proof-bearing queue. The
[bitdeque block/padding design](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/src/util/bitdeque.h#L15-L27)
uses32,768-bit logical blocks by default: append-only PRESYNC at Kmax needs103
such block payloads (421,888 bytes), rather than ideal packed418,777. Object
layout, deque maps/padding/allocator overhead remain additional. REDOWNLOAD's
pop-only front padding can retain capacity despite fewer live bits; it does not
add blocks beyond the preceding append-only peak in this two-phase lifetime.
S1's proposed
packed arena is not a claim that this native allocation already exists.

The receiver must handle a threshold flush of Q owners; a64-record destination
or16-record input bound does not bound that output. Without the drain gate,
the next batch can overlap Q+B=15,250 owners at the reference input. Ownership
transfer avoids a second full proof vector, not native/metadata allocations.
Allocation failure, lost context and storage delay remain layered availability
outcomes, not evidence of intrinsic invalidity or permission to drop proofs.

## 5. Entry, transitions, finish and conditional progress

### Supported-domain predicates

Preflight must freeze trusted ND1/CFG1/profile/immutable binding and exact
T=CFG1.MinAdmissionWork. A peer supplies neither T nor an ingress class. The
anchor is a known same-ledger child with actual context and evidence closure
to the explicit genesis base; CBlockIndex membership or a descendant's intact
sidecar alone is insufficient. A threshold/config change cancels/restarts the
session rather than mutating its transcript. Current-time eligibility does not
erase historical accepted work. Height/count/length arithmetic is checked
before conversion, allocation and loops; the R03 terminal contract is still a
prerequisite for eventual native integration.

| Event | Proposed result, following the stated reference where applicable |
| --- | --- |
| First screened batch already reaches T, including zero/already-met threshold | Reserve its complete validation/durable destination and perform ordered actual-context/proof admission without a two-pass object. No trusted/min-work/prover shortcut waives B1 proof checks. |
| First batch below T and short | No new admission; do not start two-pass sync. |
| First batch full and below T | Acquire complete S1 reservation, create fresh session and process it in PRESYNC. Wire full means exactly16 records; count1/full=true is an internal-model case, not a real full B1 response. |
| PRESYNC full below T | Continue, with no accepted work/index output. |
| PRESYNC reaches T after its whole batch | Retain commitment bits, reset redownload cursor/work to the same anchor and request complete records again. |
| PRESYNC short below T | Terminate with no new output. |
| Empty response in either phase | Caller cancels the session, not a call to the nonempty-span state-machine operation; no unseen evidence is promoted. |
| REDOWNLOAD below T, full | Screen/check samples, append whole batch, transfer only owners beyond ell; drain before requesting more. |
| REDOWNLOAD reaches T | Preserve the reference threshold-before-current-sample ordering; remaining samples are skipped after flag. Transfer the entire ready window, validate/drain and then finish. Do not invent a target-hash equality test. |
| REDOWNLOAD short below T | An already lookahead-ready prefix may be returned, but the unreleased tail is discarded on finalization. Success is not completion; retain only independently admitted prefix facts. |
| Invalid proof/sample, missing context, resource refusal, clock retry, disconnect | Use the applicable scoped failure/availability/cancellation result; fence late jobs. No permanent Hc poison or implicit DIRECT fallback from missing data. |

Screening/sample/continuity processing is atomic with respect to ready output:
a later failure in that batch returns no newly ready owners from that call,
even if an earlier record set the threshold flag. Prior admitted calls remain
historical facts. After a successful batch transfers owners, actual-context or
durability failure has its independently scoped ordered-drain result; do not
erase or double-credit the already admitted valid prefix.

The caller's [empty/known-header paths](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/src/net_processing.cpp#L2960-L3085)
and [actual contextual checks](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/src/validation.cpp#L4112-L4152)
must be audited again in an authorized implementation. Proposal/template and
trusted ingress remain distinct from accepted evidence.

### Conditional progress statement

For an admitted owner serving a stable fully valid threshold-reaching prefix,
all complete PRESYNC batches fit within M-a; full responses continue while
needed, all redownload records/proofs are available, current context remains
eligible, network/CPU/durable receiver eventually serve every charged item,
and the owner is not perpetually canceled/preempted. Assume no obstructing
uint256 work wrap: the candidate explicitly retains native modular addition,
not mathematical unbounded cumulative work. Under these conditions:

1. C(a,n,o)<=K prevents a commitment-cap abort throughout the supported prefix.
2. Whole-batch staging owns at most ell+B records; the input is separately
   charged. A threshold flush transfers owners instead of allocating Q new ones.
3. Ordered draining supplies each next actual parent/context; no next batch
   consumes its slots until ready ownership/durability has drained.
4. A finite threshold-reaching PRESYNC prefix transitions after its complete
   batch. Finite redownload plus eventual drain reaches normal completion.

This is a conditional abstract progress argument, not a native execution or
universal liveness theorem. Terminal chains below T, work-wrap traces that do
not reach T, short/refusing/reorganizing peers, unavailable proof/ancestry,
clock ineligibility, undraining storage and an honest peer never getting service
fall outside the claim. Do not replace modular ledger arithmetic merely to make
the argument monotone. A stricter local unsupported-domain predicate or a
separate modular analysis needs its own exact-contract disposition.

## 6. Security objective and new batch-size finding

The [native rationale](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/src/headerssync.h#L52-L98)
uses secret salted one-bit C80 samples to detect a peer replaying an honest
high-work prefix in pass1 and diverging into cheaply generated headers in pass2.
The [pinned tuning model](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/contrib/devtools/headerssync-params.py#L14-L146)
targets expected extra permanent header-count growth, not zero failure chance:

| Source input | Pinned value / limit |
| --- | --- |
| Normal block interval | 600 seconds |
| Honest prefix corresponding to minimum work | 938,343 headers |
| Aggregate attacker processing bandwidth | 6,000,000,000 bits/second, a source modeling assumption |
| Extra growth fraction | 0.2 of normal header growth |
| Wire/temporary element sizes | 81 bytes /48 bytes |
| Batch and offset | 2,000 headers; random secret offset |
| Length horizon | Bitcoin genesis2009 and study date2028-10-10 |

These are not a B1 threshold/cost mapping, a benchmark measured here or current
official ALUZ settings. ALUZ MAIN also currently targets600-second spacing,
but its [minimum chainwork is zero](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/src/kernel/chainparams.cpp#L97-L121),
its genesis differs and CFG1 is unallocated. The tuning script's
[memory function](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/contrib/devtools/headerssync-params.py#L217-L226)
counts compact payload/commitment bits, not full proofs, native allocations,
CPU or durable proof archives. The optimizer was **not run** for this milestone.

### Reproducible inert expectation calculation

In the source-style model, h is the honest prefix0..B-1 of the first divergent
batch; F=B-h+kB forged headers have arrived at batch boundary k. With uniformly
hidden offset, average probability of matching all checked forged samples is

`p(F)=2^(-floor(F/p)) * (1-(F mod p)/(2p))`.

This follows by counting p-r offsets with q checks and r offsets with q+1,
where F=qp+r. The new forged release count at that boundary is
`d(F)=min(B,max(F-ell,0))`. Compute
`Emax=max_h sum_k d(F)*p(F)` for the lookahead-release attack model. Whole-batch
checks before popping matter: smaller batches can release earlier with fewer
checked bits. Merely preserving ell/p does not preserve this expectation.

Root integrated offsets algebraically, separately from the source-style
offset loop used by another stream. Exact integer/common-denominator sums of
the same positive series were checked through q<96, with omitted tail bounded
by **2(p+B)*2^-96**. That rational interval supports the comparisons below
without relying on floating-point roundoff. The model's independence/secrecy/
attack assumptions remain conditional; exact arithmetic does not validate them.

| p,ell,batch | Expected forged admissions per modeled attack, approximately | Worst h |
| --- | --- | --- |
| 641,15,218,2,000 | 0.00003376987444977211 | 200 |
| 641,15,218,16 | 0.00006788982988032735 | 3 |
| 641,15,218,1 | 0.00006844789115203524 | 0 |
| 641,15,863,16 | 0.00003379714121693509 | 0 |
| 641,15,864,16 | 0.00003376026897929544 | 15 |

The old source allowance is exactly8445087/250000000000 =0.000033780348
headers/attack. Its native-batch point is below that allowance; B1batch16 is
above, about2.00974 times the allowance. In this **same conditional count
benchmark**, 15,864 is the minimal integer ell>=15,218 passing the old allowance:
the positive-series expectation is nonincreasing with lookahead, and exact
intervals place15,863 strictly above and15,864 strictly below. This number is
**NOT a safe/allocated B1 parameter or a complete security correction**.

For a sensitivity example ONLY, retain the source's938,343-header attempt cost,
6Gbit/s and600seconds, and change just wire cost. B1's maximum16-record batch
has minimum average complete wire bytes159.0625 for DIRECT or392.0625 for AUX
(record+4-byte length+one shared count byte). At ell15,218 the resulting modeled
count-growth fractions are about0.204686 and0.0830425; at15,864 they are0.101786
and0.0412954. No actual CFG1 threshold or adversary cost lower bound is derived
from that example, and mixed route/proof-size/replay strategies require analysis.

## 7. Proof storage, adversary cost and security eligibility

A source C80 commitment says nothing about excluded attachment bytes. S1
independently screens pass1, redownload and actual admission; an alternative A2
is fully checked and owned. Preserve collision/preimage assumptions, no C80
reconstruction of AUX evidence, no cached context authority, proper branch/
numeric predicates, no duplicate work and scoped attachment failures. The
existing [receipt/context rules](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/doc/andaluzcoin-auxpow-b-candidate-specification.md#L361-L409)
and [durability rules](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/doc/andaluzcoin-auxpow-b-candidate-specification.md#L504-L567)
remain dependencies, not properties established by this model.

The sample model assumes keyed-hash pseudorandomness and hidden salt/offset,
and prevhash collision/second-preimage resistance so divergence propagates.
B1's same-history work-cost premise additionally depends on immutable monotone
routes and its stated fixed-point/acyclic assumptions, not merely a generic
hash-security label; see the [qualified B1 reasoning](https://github.com/andaluzcoin/andaluzcoin/blob/261ff2ab2e9fbcc9a078d5f875c7d1937286ee1a/doc/andaluzcoin-auxpow-b-candidate-specification.md#L325-L357).
No fork-global uniqueness or cryptographic/security proof is established here.

Header count is not permanent bytes. A canonical sidecar adds76 framing bytes:
minimum AUX record388 gives464 bytes; maximum10,362 gives10,438. The geometry
ratio is about22.4957. Even an assumed0.2 extra-header fraction could correspond
to about4.49914 times a minimum-AUX canonical-sidecar reference byte rate under
that hypothetical mix. This is **conditional geometry**, not a valid proof
corpus or a demonstrated attainable attack. Index/filesystem/page-cache/native
RAM costs are excluded and must not be conflated with canonical disk payload.

For each permanent resource j, define a reviewed byte-growth budget G_j and
prove a common model's eligible inequality, for example

`Emax * D_j,max * A_max / C_attempt,min <= G_j`.

D_j,max is incremental accepted bytes/header for the stated resource; A_max
and C_attempt,min must use the SAME attacker cost units. RAM index growth and
disk archive growth need separate terms, as do temporary proof/CPU service.
A fractional normal-growth target can define
`G_j=f_j*D_j,honest_reference/tau`, but none of those B1 budgets is adopted here.
The old0.2 count objective is not an automatically selected proof-byte budget.

Qualify C_attempt,min across allowed anchors, repeated/aborted sessions,
threshold-bypass entry, trusted CFG1 work, actual difficulty/work paths,
DIRECT/AUX/profile history, proof alternatives and time/bandwidth/CPU limits.
An arbitrary positive uint256 T does not imply938,343 headers or a minimum
attempt bandwidth cost; zero/already-met T supplies no general low-work defense.
Do not independently combine impossible best/worst wire and storage cases as an
attainable attack, or treat a pessimistic product as a measured cost bound.

Keep salt/offset secret, regenerate on every fresh attempt and analyze adaptive
responses/restarts rather than assuming arbitrary independent Bernoulli trials.
The model concerns lookahead release before honest-work qualification; the
threshold-flush path and source assumption that an adversary cannot cheaply
produce sufficient real work need their own justified cost/context argument.
Preserving the bit mechanism while changing clock cap, records, scheduler,
batch, costs and threshold domain is not preservation of the old security target.

## 8. Alternatives and explicit design changes

| Option | Tradeoff / disposition |
| --- | --- |
| S1 complete-record owners, height-envelope bits, one active session | Preferred design to qualify: no missing-proof trust or third acquisition, finite typed canonical payloads and explicit drain. Large raw window and responsive-peer CPU/service exposure remain unqualified. |
| Compressed records plus proof fetch at release | Smaller temporary payload but effectively a third acquisition. Needs bounded authenticated fetch, availability/serving/restart rules and a new progress argument. Not selected. |
| Receipt-only retention after discarding proof | A digest is not proof availability or context. Requires a separately exact trust/ownership/durable repair contract; not a free optimization. Not selected. |
| Keep frozen-clock cap or restrict height/threshold/chain domain | Can reduce bit reservation but must refuse outside a proved domain, including whole last batch/offset counts. No general growing-chain claim. |
| Multiple reserved peers or changed sample algorithm/early release | Needs global resource, cost/security and sufficiently-long-service analysis. Lower lookahead can weaken defense; larger cap alone does not establish security. Not selected. |

S1 changes local admission/retention/receipt/pool/scheduling semantics even if
wire geometry remains. The eventual complete contract needs a new reviewed
revision, changed manifest/P and immutable full-document/source mapping. No
old-P reinterpretation, official cap/ell/T, network mapping, store migration,
profile coacceptance or H reset follows. Other correction R01/R03/Q01/Q02
requirements and immutable DIRECT-to-AUX ordering still apply.

## 9. Actual evidence and finite next qualification

Actual new evidence is pinned source inspection, three parallel design reviews
with root challenges, exact formula/owner/count arithmetic and conditional
scalar model comparisons. Root cross-checked the two sample-count formulations
at40,383 boundary/offset placements; a separate progress stream checked41,024
placements. These are count exercises, not candidate decode/context tests.
The execution report records file/link/hash/scope validation and CI obtained.

No B1 executable/parser/verifier, numeric-work oracle, node/miner experiment,
native allocator/RSS/CPU measurement, candidate fuzz/race/crash campaign,
historical replay, valid proof/body corpus, interoperability or external security
certificate was supplied. The native optimizer was not run. Existing CI tests
today's repository, not this proposed architecture. C02/V05/V06/V07/V18 and all
other future C/V requirements remain unimplemented/unexecuted at that scope.

| Qualification gate | Finite required evidence before the affected claim |
| --- | --- |
| F1: exact semantics/domain | Reconcile S1 classes/entry/threshold-before-sample/short/finish/height/clock/work-wrap/cancellation with every candidate view and other corrections; state unsupported traces and revised manifest semantics. |
| F2: resource implementation envelope | Independently specify all allocated-capacity maxima and failure ownership on pinned platforms, including Q flush, input/copy overlap, bit payload/metadata/native allocations, pending caps and durable destination. No scalar bytes-to-RAM inference. |
| F3: security/cost calibration | Select reviewable temporary/permanent-byte/CPU/service objectives and justified actual anchor/CFG1/route/restart cost domains; independently validate/adapt the model and choose p/ell/reservations together. Conditional15,864 is only a comparison point. |
| F4: independent executable evidence | Only after separate approval and complete freeze: independent fixture/oracle authors, all offsets/batches/cap boundaries and threshold outcomes; actual proof/context agreement, concurrency/cancel/durability and resource/security cases. |
| F5: service and deployment disposition | Prove or explicitly limit scheduling/long-session/fairness/eclipsing behavior; qualify storage/repair/compatibility and operational evidence under their own scopes. No launch approval from research CI. |

**Next recommendation:** a finite security/cost calibration and exact-contract
decision package using S1's explicit ownership/domain obligations, then critical
review of a complete successor revision. It must determine real budgets and
eligible inputs, not simply adopt the illustrative lookahead. Actual executable
resource/verification work still needs its separately authorized frozen scope.

## 10. Research completion versus GO

This investigation provides a concrete conditional design, new batch/security
counterexample, exact typed bounds and explicit unresolved decisions. That
research artifact can complete under issue -> isolated branch -> GitHub report/
PR -> independent exact-head review/CI -> permitted regular merge -> successful
actual-merge masterCI -> independently verified annotated research tag -> final
report/closure. A failed/cancelled check needs its own disposition; older retry
approvals are consumed. No workflow or gate is weakened to accelerate release.

Operational R02, full exact freeze, executable B1, adoption/integration,
activation/migration and operations remain HOLD. All D01-D08 and21launch gates
remain OPEN/unchecked, mainnetNO-GO. Mainnet consensus/identity/network settings
and descriptor-wallet-only policy remain unchanged. No fixed remaining milestone
count or GO date is implied by completing a research dossier.

Security/cost eligibility and exact-contract follow-up: [v0.2.88 dossier](andaluzcoin-auxpow-b-security-cost-eligibility.md).
Research/calibration only; no budget/parameter adoption, complete freeze or GO approval.

Proposed component-measurement gate: [v0.2.89 charter](andaluzcoin-auxpow-b-measurement-charter.md).
The scoped F4 exception is unapproved; the production freeze/executable holds remain.
