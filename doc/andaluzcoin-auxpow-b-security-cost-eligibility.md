# B1 security/cost eligibility and successor-contract decisions

## 1. Scope and present decision

**v0.2.88 is research/calibration and decision preparation. Real-world B1 cost
qualification remains INELIGIBLE on the evidence currently supplied.**
[Tracker #111](https://github.com/andaluzcoin/andaluzcoin/issues/111) follows the
owner's instruction to proceed with the finite package recommended by
[completed v0.2.87](https://github.com/andaluzcoin/andaluzcoin/issues/109#issuecomment-6704556029)
and [presync F1-F5](andaluzcoin-auxpow-b-presync-design.md#9-actual-evidence-and-finite-next-qualification).
This dossier supplies new exact count/cost comparisons, a resource/input
register and concrete successor decisions. It neither adopts those decisions
nor supplies the independent native/executable evidence needed for qualification.

Frozen baseline B is **dfc3aecf66245b6544eddcc134cdfa51bc31e4b2**, tree
**3ddc5f6d963a32b4b71b2be150f1f5e4502b5e18**. Verified annotated tag
v0.2.87-auxpow-b-presync-design-research has object
b1f40b652b258d2e399d964000215e26c9be8ef5. All immutable source links below pin B.
The complete previous documents, original revision2 manifest/P and all
production/source/runtime/tests/workflows/readiness remain unchanged except
appended navigation. No new manifest bytes, P, p, lookahead, T, budget, official
network mapping, activation or executable B1 scope is allocated.

**Recommended current disposition:** retain S1 as conditional; use the new
equations as model filters, not production settings. Prepare one immutable
successor interpretation with all required qualified literals, preserve native
modular ledger arithmetic, and state the initial security/progress claim only
over an explicitly qualified nonwrapping domain. These are proposals for critical
review. Do not silently add a runtime wrap rejection, reinterpret old P, or
substitute an undocumented local policy object for an exact contract.

All D01-D08 remain OPEN, all21 [mainnet gates](andaluzcoin-mainnet-readiness.md)
unchecked, mainnet **NO-GO**. Operational R02, complete exact freeze,
executable/adoption/integration/activation/migration/operations remain HOLD.
Mainnet genesis/PoW/DAA/subsidy/identity/network parameters and
descriptor-wallet-only policy are preserved.

## 2. Input and evidence register

Repository/GitHub recovery found no selected operator hardware, native RAM,
CPU/service, bandwidth or permanent-growth budget. This is a statement about
recovered evidence, not proof that no private deployment plan exists. The
[candidate limits](https://github.com/andaluzcoin/andaluzcoin/blob/dfc3aecf66245b6544eddcc134cdfa51bc31e4b2/doc/andaluzcoin-auxpow-b-candidate-specification.md#L468-L500)
are provisional logical caps, and the
[operator launch requirements](https://github.com/andaluzcoin/andaluzcoin/blob/dfc3aecf66245b6544eddcc134cdfa51bc31e4b2/doc/andaluzcoin-mainnet-readiness.md#L152-L167)
require later measurable evidence. Unknown is neither zero nor unlimited.

| Input | Recovered status / evidence needed |
| --- | --- |
| Platform and node baseline | UNKNOWN: OS/architecture/compiler/allocator, CPU/SHA acceleration, storage/filesystem, native baseline peak and simultaneous workloads. |
| Temporary capacity | UNSELECTED: total native/RSS objective and residual presync budget after ordinary pools; every allocated-capacity and alias/copy lifetime. |
| CPU/network/service | UNSELECTED: interval/burst budgets, bounded per-operation service, admitted-peer set, honest share, response/drain/cancel bounds and completion objective. |
| Permanent resources | UNSELECTED: separate index RAM, canonical archive, filesystem/inodes/write amplification, total headroom/horizon and excess-growth budgets/reference. |
| Anchor/threshold/domain | UNALLOCATED actual CFG1/T and supported anchor/work/route/clock/no-wrap histories; immutable evidence closure and terminal rules. |
| Adversary costs | UNQUALIFIED aggregate capacity and uniform attempt-cost lower bound in identical units over allowed adaptive/restart/bypass/anchor histories. |
| p/lookahead/reservations | Native641/15,218 are explicitly provisional comparison inputs; S1 K/Q classes are proposed, not implemented allocations. |
| Empirical/executable evidence | NOT SUPPLIED: candidate verifier/proof/body corpus, native allocator/RSS/CPU, race/crash/repair, independent security/service evidence. |

Each selected input must record accountable owner, exact value/units, scope,
status, immutable provenance, platform/configuration, method/workload/horizon,
uncertainty/omissions, independent reviewer and pass criterion. A target supplied
by an owner is a policy input, not a measured native or adversary-cost result.
The inherited script's6Gbit/s,938,343 headers,600seconds and0.2 fraction remain
[source-model assumptions](https://github.com/andaluzcoin/andaluzcoin/blob/dfc3aecf66245b6544eddcc134cdfa51bc31e4b2/contrib/devtools/headerssync-params.py#L14-L46),
not automatically chosen ALUZ budgets or a mapping from arbitrary uint256 T.

## 3. A new exact envelope for the modeled leakage

Use the v0.2.87 source-style below-threshold divergent-C80 model only: uniform
hidden offset, independent unpredictable sampled bits for distinct divergent
C80s, divergence propagation under the stated hash/prevhash/route assumptions,
no threshold-flush shortcut and no unmodeled secret/feedback leakage.
For F forged arrivals and period p>0, the offset-averaged survival probability is

`s(F)=2^(-floor(F/p))*(1-(F mod p)/(2p))`.

For any fixed grouping of that modeled path, forged header j cannot be released
before at least ell+j forged arrivals: it still needs ell later positions in
the lookahead. Whole-batch checks can delay release further. Since s is
nonincreasing, linearity of expectation gives the conservative count envelope

`E_group <= U(p,ell) = sum_(j>=1) s(ell+j)`.

This proves a comparison about the stated random-bit model, not full B1
security. Actual B1 continued full batches are16; a short below-T redownload can
return a ready prefix and then finalize. Repeated one-record continued wire
batches are not a demonstrated attack. Adaptive transcript/batch/abandonment
strategies need a justified conditional survival bound under their observations;
this fixed-path calculation supplies no such independent cryptographic proof.

Writing ell=q*p+r,0<=r<p, summing the first partial period and geometric tail gives

`U(p,ell)=2^(-q)*((3p-1)/2-r+r*(r+1)/(4p))`.

Root independently started at N=ell+1=qN*p+rN and obtained
`2^(-qN)*((p-rN)*(1-(rN+p-1)/(4p))+(3p+1)/4)`.
A separate secret-phase sum uses first sample distance d=1..p: at N let m be
the checked-sample count and d_next the next sampled height; its tail is
`(d_next-N+p)*2^(-m)`, averaged over d. Exact rational comparisons and finite
series/tail decompositions agree. Also `U(ell)-U(ell+1)=s(ell+1)>0`.

| p=641 comparison | Exact U where shown | Approximate U |
| --- | --- | --- |
| ell15,218 | 368051/5377097728 | 0.00006844789115203524 |
| ell15,864 | 366041/10754195456 | 0.00003403704177570789 |
| ell15,870 | 727291/21508390912 | 0.00003381429150026414 |
| ell15,871 | 22703/672137216 | 0.00003377732918154617 |

The old source count allowance is8445087/250000000000=0.000033780348.
For this conservative envelope,15,871 is the first integer ell certifying
that old allowance;15,870 fails the bound test. This does not contradict the
v0.2.87 fixed-batch16 comparison at15,864: they certify different bounds.
Neither value is an adopted or proven-safe B1 setting. An upper bound above a
budget is failure of this certificate, not proof that an attack exceeds it.

## 4. Consistent cost units and byte-frontier sensitivity

For resource j, a conditional modeled excess-growth certificate has the form

`U(p,ell)*D_j,max*A_max/C_attempt,min <= G_j`.

Here D is incremental resource per modeled newly admitted divergent header;
A and C must use the SAME cost unit, and G uses that resource/time. A defender
operation-count upper bound or one slow measured attacker does not establish
a universal attacker cost lower bound. A joint strategy model may be tighter
than a rectangular product, but requires an actual eligible strategy domain.

For sensitivity ONLY, assume n=938,343 mandatory prefix records, A=6Gbit/s
incoming application-wire capacity (not qualified B1 processing throughput),
tau=600seconds, Dmax=10,438 canonical sidecar bytes, and hypothetical
G=(1/5)*464/600 bytes/s. Use application wire bits C=8*n*w. Packed16-record
responses have minimum average w=159.0625 bytes for DIRECT or392.0625 for AUX;
maximum-record average is10,366.0625. These include u32 lengths and one count
byte per16, but exclude transport, requests, retransmits and other service.

| Hypothetical mandatory prefix-cost domain | Last ell whose U does not certify G | First ell certifying this bound | Canonical (ell+16)*10,362 bytes |
| --- | --- | --- | --- |
| Every cost-prefix record AUX, use minimum AUX wire | 17,292 | 17,293 | 179,355,858 |
| Universal minimum DIRECT wire, max AUX increment: rectangular envelope | 18,130 | 18,131 | 188,039,214 |

Root also checked the distinct DIRECT231-byte reference comparison: its
rectangular frontier is18,776 rather than18,131. Reference choice is a policy
input. The all-AUX row requires a justified mandatory AUX cost prefix; the
universal-minimum row is only conservative if its n-record lower cost applies
to EVERY eligible attempt. Joint attainability of minimum input and maximum
increment is not shown or needed to label an upper bound conservative; it IS
needed to claim an actual attack. There is no such proof/corpus here.

At ell15,864 the all-AUX comparison's count-growth fraction is about0.0416339,
but its max-sidecar growth relative to a464-byte reference is about0.936584.
Certifying the illustrative0.2 byte fraction at that ell would require at least
4,394,185 mandatory minimum-AUX cost-prefix records in this model, not assumed
938,343. This is sensitivity of a certificate; it is neither an actual prefix
requirement for safety nor an attainable proof attack nor an official target.

### Coverage the inequality does not supply

1. **Threshold/direct/real-work paths.** First-batch direct admission and
   REDOWNLOAD threshold flush skip the lookahead defense. Real qualifying
   work/context/cost must justify those paths separately, including T=0.
2. **Evolving anchors and restarts.** Accepted below-T prefixes can become
   future anchors, changing T-anchorWork and mandatory replay cost. A fixed
   n lower bound must hold over all allowed anchor/history/route/restart and
   abandonment choices. Fresh salt alone does not cap attempt rate or CPU.
3. **Same Hc, different FIRST attachment.** A larger independently valid A2
   for unchanged C80 passes all C80 samples. FIRST may choose that attachment
   before an alternative. While selected FIRST evidence remains intact, do not
   replace it for size optimization. Lost/corrupt evidence follows the separate
   independently verified, atomically persisted A2 repair rule with no second
   work increment; repair may also change stored proof length.
   Cheap alternatives or attacker-first arrival are not proved. Nevertheless
   U*Dmax covers modeled novel divergent Hc, not all extra proof-size choices
   on otherwise honest headers. Choosing464 as normal proof-byte reference
   therefore needs its own distribution/cost argument, or a conservative
   maximum-size reference and separately reviewed baseline budget.
4. **Other resource growth.** Repair/orphan durable writes, logs/filesystem,
   native index and body/undo, replayed proof CPU and normal qualifying chain
   growth need their own categories. FIRST idempotence is not a lifetime cap
   on distinct forks. Temporary Q and height M bound neither total archive
   across sessions nor all accepted forks nor expected growth per time.

The [candidate FIRST/sidecar rule](https://github.com/andaluzcoin/andaluzcoin/blob/dfc3aecf66245b6544eddcc134cdfa51bc31e4b2/doc/andaluzcoin-auxpow-b-candidate-specification.md#L526-L565)
and [C80/attachment separation](https://github.com/andaluzcoin/andaluzcoin/blob/dfc3aecf66245b6544eddcc134cdfa51bc31e4b2/doc/andaluzcoin-auxpow-b-candidate-specification.md#L389-L409)
must not be replaced by a claim that samples authenticate excluded proof bytes.

## 5. Joint reservation and workload feasibility

For anchor height a, M=2,147,483,647, K=ceil((M-a)/p), Q=ell+16 and R=10,362,
define B_session as the residual native budget AFTER the baseline node and
DISJOINT ordinary-pool charges. Assign each shared physical input owner to
exactly one bucket. The requirement is

`Q*R+A_bits(K)+A_descriptors+ A_receipts+A_input+A_parse/verify+A_session/peers+A_durable_overlap <= B_session`.

Every A is an allocated-capacity maximum not already deducted on the right,
including alignment, native containers,
jobs/stacks/scratch, allocator caches, aliases that pin a larger buffer and
simultaneous writer copies. Count a physically shared input once, but charge
all independent descriptors/jobs/copies. Unknown terms prohibit native RAM/RSS
qualification. A canonical-arena budget B_arena alone implies the NECESSARY
condition `ell<=floor(B_arena/R)-16`. A model's certifying ell_min must intersect
that upper bound, bit capacity and every other qualified dimension. A nonempty
logical intersection is not sufficient evidence of actual memory/security.

The following bounded grid uses only the OLD conditional count allowance and
U, a=0, one165,857-byte input and IDEAL packed bits. It is not an optimizer,
platform measurement, general minimum or a recommendation to select a row.

| p | First model-certifying ell | K logical bits | Q arena bytes | Arena+one input+ideal packed bits |
| --- | --- | --- | --- | --- |
| 16 | 311 | 134,217,728 | 3,388,374 | 20,331,447 |
| 32 | 654 | 67,108,864 | 6,942,540 | 15,497,005 |
| 64 | 1,372 | 33,554,432 | 14,382,456 | 18,742,617 |
| 128 | 2,873 | 16,777,216 | 29,935,818 | 32,198,827 |
| 256 | 6,001 | 8,388,608 | 62,348,154 | 63,562,587 |
| 641 | 15,871 | 3,350,209 | 164,621,094 | 165,205,728 |
| 1024 | 26,053 | 2,097,152 | 270,126,978 | 270,554,979 |

This makes joint p/ell/reservation selection reviewable; inheriting641 or
optimizing only bit payload is not justified. The
[S1 resource classes](andaluzcoin-auxpow-b-presync-design.md#4-logical-payload-accounting-not-a-ram-cap)
still require whole-window output/drain and actual durable destination.
Q ready owners can transfer through one shared arena; a64-element copied
output queue cannot stand in for Q capacity. Stop new progress input until
released owners drain; keep bytes through reviewed FIRST durability.
Reserving a Q flush does not reserve cumulative storage for a complete suffix.
Either qualify that space/headroom/write amplification or explicitly condition
progress on eventual storage availability and scoped out-of-space behavior.

### Hash-call counts are not uniform CPU costs

[B1 primitives](https://github.com/andaluzcoin/andaluzcoin/blob/dfc3aecf66245b6544eddcc134cdfa51bc31e4b2/doc/andaluzcoin-auxpow-b-candidate-specification.md#L54-L60)
define H2 and TH2. The
[SHA256 padding implementation](https://github.com/andaluzcoin/andaluzcoin/blob/dfc3aecf66245b6544eddcc134cdfa51bc31e4b2/src/crypto/sha256.cpp#L725-L739)
gives `H2(n)` raw compression blocks `ceil((n+9)/64)+1`; TH2 adds a64-byte
constant prefix. Applying only message-length arithmetic to the
[proof predicates](https://github.com/andaluzcoin/andaluzcoin/blob/dfc3aecf66245b6544eddcc134cdfa51bc31e4b2/doc/andaluzcoin-auxpow-b-candidate-specification.md#L223-L318)
and [required E](https://github.com/andaluzcoin/andaluzcoin/blob/dfc3aecf66245b6544eddcc134cdfa51bc31e4b2/doc/andaluzcoin-auxpow-b-candidate-specification.md#L482-L498):

| Per-screening transcript geometry | DIRECT | AUX minimum | AUX maximum |
| --- | --- | --- | --- |
| Core raw compression blocks | 3 | 17 | 353 |
| Required E raw blocks | 5 | 9 | 165 |
| Total raw blocks | 8 | 26 | 518 |
| With constant tag-prefix midstates, excluding setup | 7 | 23 | 485 |

Maximum core353=Hc3+leaf4+slot3+txid130+auxiliary30*4+parent30*3+P80work3.
E hashes64+10,362 bytes then32. Min AUX has142-byte coinbase/depth0/record388;
max has8192-byte coinbase/depth30+30/record10,362. Constant tag-prefix caching
saves one block per TH2 occurrence, not all message work. These are length
calculations, not B1 proof hashing, proof validity, a CPU/cycle bound or benchmark.
Parsing, context,
commitment PRF, setup/caches/parallelism, scheduling and I/O remain separate.
Do not automatically multiply by three unless the exact selected path actually
performs all three independently charged traversals.

At a=0,n=M, one mathematical packed max-record pass has
22,260,949,702,530 application bytes; two have44,521,899,405,060. One n-record
screening's analytical call ceiling is66*n=141,733,920,702, not measured CPU.
n new distinct maximum sidecars total22,415,434,307,386 bytes before binding,
index/filesystem/body/undo. These NEW scalar products are not a valid chain,
feasible attack or service promise. Full-height K is finite per session; it
does not make the session affordable or bound repeated sessions or forks.

## 6. Service and exact threshold-domain decisions

One global owner bounds simultaneous windows. An incomplete-payload timer
does not bound total responsive-owner tenure. A finite lease can repeatedly
cancel every honest session requiring more service than that lease, discarding
its salted transcript. Rotation alone proves neither anti-starvation nor
anti-Sybil/no-eclipse. Bounded honest wait additionally needs a bounded admitted
set, bounded selections ahead, bounded cancel/drain overhead and sufficient
uninterrupted or separately reviewed resumable honest service. No numerical
lease or throughput promise is selected here.

A finite observation-horizon resource policy must charge initial screen,
bypass, abandoned/restarted sessions, redownload/final verification, RPC/import,
repair and restart revalidation. A proposed envelope
`charged_j(I)<=burst_j+rate_j*length(I)` needs exact units/paths and a separate
honest minimum-share/completion argument. Safe capacity refusal is not universal
liveness. A defender CPU ceiling is not an attacker cost lower bound.

### Three distinct modular predicates

The frozen candidate preserves
[native modular accumulation](https://github.com/andaluzcoin/andaluzcoin/blob/dfc3aecf66245b6544eddcc134cdfa51bc31e4b2/doc/andaluzcoin-auxpow-b-candidate-specification.md#L368-L371).
Let W_end=(W_anchor+sum_i w_i) mod2^256. Native source supplies the modular
ordering; full16, complete proof and durable admission below are proposed B1/S1
adaptations. Native caller batching uses its configured maximum and is not a
B1 proof/durability implementation. Source inspection and the adaptation yield:

| Decision point | Source ordering and proposed B1 consequence |
| --- | --- |
| First nonempty batch | [Caller](https://github.com/andaluzcoin/andaluzcoin/blob/dfc3aecf66245b6544eddcc134cdfa51bc31e4b2/src/net_processing.cpp#L2767-L2806) compares modular W_end>=T. If true, full ordered contextual/proof admission; otherwise short input stops and full16 starts PRESYNC. W_anchor>=T alone is insufficient if this incoming batch wraps belowT. T=0 always meets the end predicate. |
| PRESYNC | [Process batch](https://github.com/andaluzcoin/andaluzcoin/blob/dfc3aecf66245b6544eddcc134cdfa51bc31e4b2/src/headerssync.cpp#L139-L174) compares only after the complete batch. A crossing erased by later modular wrap need not transition. |
| REDOWNLOAD | [Per-record loop](https://github.com/andaluzcoin/andaluzcoin/blob/dfc3aecf66245b6544eddcc134cdfa51bc31e4b2/src/headerssync.cpp#L215-L292) adds modular work, latches threshold BEFORE the current sample, and keeps the flag even if later additions wrap belowT. Whole-batch success is required before newly ready output. |

These source facts do not establish an admissible concrete work/chain trace.
Do not turn mathematical positive increments into unbounded-integer ledger
credit or silently add a first-batch anchor shortcut. Recommended initial claim
domain excludes wrapping sync traces; preserve processing semantics unless a
separate critical decision chooses scoped local unsupported-domain refusal.
That refusal, if selected, must occur before new transcript/output publication
and must not label an intrinsically valid child INVALID_CHILD.
An alternative is independently qualified modular-trace analysis. No such
oracle/proof/corpus or runtime policy is supplied here.

## 7. Concrete successor decision register

Every disposition below is **PROPOSED / NOT ADOPTED**. Frozen candidate text is
a research baseline, not deployed consensus. A new revision is required for
semantic changes; no silent old-P interpretation is permitted.

| ID / subject | Recommended exact disposition and required decision |
| --- | --- |
| C1 policy identity | Prefer one complete immutable profile interpretation with every qualified literal fixed. [CFG1](https://github.com/andaluzcoin/andaluzcoin/blob/dfc3aecf66245b6544eddcc134cdfa51bc31e4b2/doc/andaluzcoin-auxpow-b-candidate-specification.md#L151-L171) contains P/H/masks/T, not p/ell/typed reservations/scheduler/support-domain identity. Alternative: define a NEW canonical trusted policy schema/PolicyID, session/receipt binding and size/ConfigID/view impacts. Unspecified mutable local S1 under unchanged P/ConfigID is not an exact freeze. |
| C2 objectives/domain | Select actual platform, native/permanent/CPU/network/service objectives and allowed anchor/T/H/route/restart domain; establish uniform cost bounds, same-Hc/repair coverage and reference growth. Then jointly certify p/ell/K/Q and native limits. Current numeric comparison rows allocate nothing. |
| C3 arithmetic/entry | Preserve modular ledger work and all three predicates above; initially qualify only a reviewed nonwrapping claim domain. Runtime refusal or broader modular claims need their own exact decision/evidence. |
| C4 phase lifetime | Ratify compute-E-while-owned then discard complete PRESYNC proof/per-record screen receipt after successful batch; retain sampled bits and bounded cursor/work only. REDOWNLOAD reacquires and independently screens complete A2 and owns exact bytes/E through final verification and durability. This explicitly amends [revision2 receipt references](https://github.com/andaluzcoin/andaluzcoin/blob/dfc3aecf66245b6544eddcc134cdfa51bc31e4b2/doc/andaluzcoin-auxpow-b-candidate-specification.md#L439-L466), not a missing-proof trust shortcut. |
| C5 typed capacities | Replace old scalar sync units by K bits/Q complete owners and all native/job classes. If pending8/peer64/global and active2/peer8/global are retained, explicitly amend their job meaning: screen/copy at most available pending capacity from charged input, never create16 uncharged unscreened canonical jobs. Screened retained/context-awaiting Q owners form an explicit charged class. Final reverification jobs still charge counts/scratch; byte copies cost extra. Numeric adequacy remains unqualified. |
| C6 transitions/failure | Freeze whole-batch screen/transcript atomicity; threshold-before-sample/sticky flag; short ready-prefix-then-stop versus completion; empty caller cancellation; late failure yields no new ready output from that call even after a threshold crossing. Ordered final-context/drain failure preserves independently committed prior prefix. No target-Hc equality test, unseen evidence or permanent attachment poison. |
| C7 ownership/publication/service | Atomically reserve complete K/Q/input/receipt/scratch/durable vector and one global progress owner. Q-sharing ordered drain gates new input; generation fences late jobs; mutable ancestry/evidence closure must be protected/revalidated at evidence-ready/work-eligibility publication. Durable FIRST selection, once-only historical credit and recurring current-eligibility restoration are distinct; restoration never increments work again. FIRST lock alone is insufficient. Preserve historical prefix and nonauthoritative orphan recovery distinction. Keep honest progress conditional until service policy/evidence is qualified. |
| C8 corrections/adoption | Incorporate [R01/R03/Q01/Q02](andaluzcoin-auxpow-b-specification-corrections.md) coherently: route-fixed child-vector C across views; full terminal caller safety; exact supplied P80 bytes; dedicated trusted DIRECT genesis numeric/base-work/durable procedure. All remain proposed/unimplemented. Official mappings/H, old/new-profile coexistence, storage migration/recovery and deployment require separate decisions even after a future research freeze. |

Unchanged context/evidence/genesis/availability scopes remain explicit. Bind
sessions to trusted profile/configuration, fixed anchor and policy interpretation
plus fresh generation; a permitted compatible threshold/config change cancels
and restarts rather than mutating transcript. Incompatible ledger/genesis/H
binding stops for separate review, not automatic reset. Height checks precede
addition/conversion and complete last-batch processing; keep M+1 a wide count,
not an int32 height. Replacing the frozen-clock bit cap does not remove current
clock/context checks or erase historical accepted work.

### Complete manifest and every-view impact

P hashes manifest bytes, not all prose/source/configuration. A revision token
or `presync=S1` label alone cannot bind unresolved policy semantics. Freeze exact
manifest bytes/LF/hash/P together with the entire immutable document hash/commit,
source/ruleset interpretation and independent evidence mapping. Cover C1-C8,
p/ell/K/Q, support domain, entry/order/failure, receipt lifetimes, typed job/owner
limits, all maxima/deadlines/waiters, drain/durability/cancel and R01/R03/Q01/Q02.
No placeholder counts as a complete exact freeze. C8 contributes the corrected
research semantics and explicit compatibility/mapping/migration HOLD
dispositions; a research freeze does not require or authorize selecting official
network H/mapping, coexistence or deployment.

| View/state | Required successor reconciliation |
| --- | --- |
| ND1/LedgerKey/genesis identity | Preserve same-ledger identity; P is not slot/ledger identity. Production mapping stays unallocated. Dedicated new-profile genesis storage procedure needs explicit review; historical work is not reset/recredited. |
| CFG1/ConfigID/receipts/session | New P changes CFG1/ConfigID. Resolve policy schema, ruleset fingerprint and fresh-generation cancellation; ConfigID alone does not fingerprint every contextual rule. |
| HeaderRecord/single/batch | Exact new P in every HeaderRecord; recompute E from its exact canonical bytes (E is not a serialized REC1 field). Proof/route/numeric checks and batch16/payload165857; no known-Hc decode/proof waiver. |
| AUX/DIRECT proof | AUX leaf=TH2(K\|\|P\|\|Hc), so new P changes the required commitment/proof. DIRECT Hc work identity remains; framing is independently checked. No old record rewrap or coacceptance permission. |
| Full/proposal/fallback/RPC/import | Uniform route-fixed child-vector C plus independent complete-view/hex/input caps. Proposal is nonadmitting; trusted ingress bypasses only P2P minimum-work gate, never proof/context/cap/durability. |
| Compact/selector/blocktxn/template | Hold checked complete record before reconstruction; blocktxn cannot replace missing proof. C applies to completed vector/fallback; template153-byte prefix/route-reserved C and terminal no-successor stay explicit. No template receipt/accepted work. |
| Sidecar/export/restart/durable index | New P/record/E and exact corrected full view; old index flags contain no inferred proof. Preserve FIRST selected DIRECT/AUX evidence, closure to explicit genesis, owner release and durable acknowledgement ordering. Compatibility/migration is separately HOLD. |

## 8. Finite eligibility result and evidence handoff

| Claim | Present disposition |
| --- | --- |
| Exact U/count frontiers and logical geometry | CHECKED within the stated scalar/random-bit model; not native measurements or adaptive security certification. |
| Actual F3 security/cost calibration | INELIGIBLE: objectives/inputs/cost coverage and independent actual evidence are missing; same-Hc, threshold/bypass, evolving anchors, CPU/service and permanent categories remain separate. |
| F1 complete successor exact semantics | Concrete C1-C8 register/cross-view mapping supplied; critical choices and qualified literals remain unadopted. Complete freeze HOLD. |
| F2 native envelope / F4 executable / F5 operational service | NOT SUPPLIED; separately authorized frozen scope and independent evidence required. |

Actual new work: three parallel source/design streams and root reconciliation;
root2,886 exact phase/period/recurrence comparisons and99 finite-series/tail
decompositions, separate cost-stream2,698 recurrence checks and exact adjacent
frontier brackets; root/stream message-length and full-height scalar checks.
The execution report records private program/receipt hashes, document/link/hash/
scope audit, immutable-head reviews and required CI. This is one assisted
workflow, not external organizational security certification or independent
candidate verifier implementations.

No candidate parser/verifier/numeric-work oracle, native optimizer import/run,
actual proof/body corpus, node/miner experiment, allocator/RSS/CPU benchmark,
candidate fuzz/race/crash/historical replay or interoperability evidence was
executed/supplied. Ordinary repository CI is separate from this absent evidence.

The next handoff is finite: select the I/O/resource/domain inputs in section2
and critically review C1-C8, preserving the separate official-compatibility and
deployment holds; then assemble the complete immutable successor
interpretation and evidence-specific authorization. If inputs remain undecided,
this research package can complete with an explicit negative eligibility result;
it cannot honestly claim real cost qualification, complete freeze or GO.

Research publication follows issue -> isolated docs branch -> execution report/
PR -> independent exact-head review/CI -> permitted regular merge -> successful
actual-master CI -> independently verified annotated research tag -> final
report/closure. All earlier retry approvals are consumed; failed/cancelled
checks need their own disposition. Mainnet/identity/network/descriptor-only
invariants and all D/21GO holds remain unchanged.
