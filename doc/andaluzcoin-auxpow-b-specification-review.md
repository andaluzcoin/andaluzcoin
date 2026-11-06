# B1 exact-specification review and parallel evidence disposition

## 1. Decision and frozen input

**v0.2.85 is an agent-assisted review, not adoption or a security certificate.**
[Tracker #105](https://github.com/andaluzcoin/andaluzcoin/issues/105) follows the
owner's instruction to review the exact B1 package and use parallel work.
The authority is [B1 sections 14-16](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/doc/andaluzcoin-auxpow-b-candidate-specification.md#14-d01-d08-consequences-and-rejected-alternatives)
and the [completed v0.2.84 report](https://github.com/andaluzcoin/andaluzcoin/issues/103#issuecomment-6674661739),
not a previously agreed numbered roadmap. The 12-18 milestone estimate is a
conditional planning range, not an acceptance rule or authorization.

Frozen master is **5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1**, tree
**b7cd016d787c02f9ec04fb23f8e0d3d6b1ddde59**, annotated research tag
v0.2.84-auxpow-b-candidate-specification-research, tag object
cc8fe74b504527cbbae4a559511896dd855bbf51.
The reviewed [B1 revision 2 document](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/doc/andaluzcoin-auxpow-b-candidate-specification.md)
has 51,803 UTF-8 bytes and 665 LF lines, SHA256
`abc2689cd5f0e460a7ff0a6fc08a26d7f9db9fa6f8554a583edb0358ea5ca892`,
Git blob `c8439343d7ce92d3d4dec3e23b72a1068520e4b1`.
Its 523-byte manifest and raw proposed ProfileID
`a6bf3a4212ae085d505322b78bfd06ebe1566146836b218ba33ff35ea99c251c`
are not official allocations. A backlink appended by this milestone does not
change that frozen normative input, manifest or interpretation.

**Disposition: publish the review; HOLD exact-spec adoption and executable B1
implementation.** R01 needs an explicit cross-view rule; R02 needs compatible
presync parameters and security/liveness analysis; R03 needs terminal-node
behavior beyond header admission. Q01/Q02 request parent-layout and genesis
initialization precision before an independent verifier freeze.
None is silently fixed by this dossier. No real ALUZ parser, consensus,
networking, storage, activation or operational work is authorized here.

All D01-D08 production/evidence gates remain **OPEN**. All 21
[mainnet launch gates](andaluzcoin-mainnet-readiness.md) remain unchecked;
public economic mainnet remains **NO-GO**. Production source, runtime behavior,
genesis/PoW/DAA/subsidy, identity/network settings and descriptor-wallet-only
policy are unchanged.

## 2. Parallel review method and limits

Three separately assigned agent-assisted workstreams read the frozen candidate:

| Workstream | Review responsibility | Root reconciliation |
| --- | --- | --- |
| A: D01-D03 | Exact bytes/hashes, trusted ledger/profile, parent transaction/Merkle proof, child target and once-only work reasoning. | Challenge inferred layout, same-history versus cross-fork claims and proof/body identity. |
| B: D04/D05/D07 | Every ingress/relay/RPC/compact/presync/storage view, resource accounting, failure/cache/concurrency and durable recovery. | Challenge cross-view size dependence and the cited native presync state machine against the new cap. |
| C: D06/D08 | Monotone route, height/context, migration/rollback, participation and adoption/release boundaries. | Trace terminal-height successors outside header admission; separate local binding from network agreement. |

The root inspected cited source bodies and reconciled findings across streams;
the integration findings were challenged by a second stream. These are parallel
reviews by agents in one assisted workflow, not independent organizations,
independent executable verifier implementations or an external security audit.
Search hits were followed into the relevant bodies; the cited examples are not
an exhaustive audit of every successor-height or serialization call path.

Actual new evidence is document/source inspection, immutable file/link/hash
verification and inert integer arithmetic supporting the findings below.
The prior manifest/hash/geometry results remain prior v0.2.84 evidence at their
stated scope. No candidate decoder, node, miner, valid block/proof corpus,
numeric-work oracle, fuzz/concurrency/crash campaign, performance measurement,
historical replay, pool interoperability or operational trial was executed.
GitHub CI tests the existing repository; it cannot execute the unimplemented B1
contract merely because this review passes CI.

## 3. Findings and publication versus adoption

Priorities describe what must be resolved before the affected later phase,
not a demonstrated vulnerability in today's unchanged ALUZ implementation.

| ID | Classification | Required disposition |
| --- | --- | --- |
| R01 | High: cross-view acceptance/storage ambiguity; D01/D04/D05/D07. | Specify proof-size-independent child capacity or an equally complete attachment-aware alternative before all-view verifier/integration eligibility. |
| R02 | High: conditional native-presync parameter incompatibility/liveness gap; D04/D07. | Specify compatible retention, lookahead, commitment and threshold behavior with independently reviewed security/liveness bounds. |
| R03 | Medium: terminal native-height integration gap; D05/D06/D07. | Specify safe terminal-tip behavior for every affected caller, not only next-header rejection. |
| Q01 | Low: exact parent-field layout clarification; D01/D03. | Restate byte offsets and hashing in the next exact review freeze; do not let implementers invent them. |
| Q02 | Medium: genesis verifier/initial-state base case; D01/D03/D05/D07. | State target/numeric verdict, initial work and evidence bootstrap explicitly without inventing a previous block. |

These block an unconditional implementation/adoption recommendation, not honest
publication of findings in a research document. Known open production decisions
and missing evidence are recorded separately in sections 5-7.

### R01. Full-view capacity, compact reconstruction and FIRST evidence

[B1's full/compact/template views](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/doc/andaluzcoin-auxpow-b-candidate-specification.md#L422-L431)
cap the complete full view at 4,000,000 bytes; its available child capacity
depends on the attached HeaderRecord. The compact row caps its own wire view.
Only the template row expressly reserves the maximum 10,362-byte AUX record.
[FIRST selected evidence](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/doc/andaluzcoin-auxpow-b-candidate-specification.md#L526-L555)
can differ from a later independently valid alternative for the same Hc.

Conditional geometry: assume an otherwise valid witness-heavy child vector of
3,995,000 serialized bytes, and two independently valid AUX records for its Hc:
A1 is 10,362 bytes and A2 is 388 bytes. Then A2 plus body is 3,995,388 bytes,
within the full-view cap, while A1 plus the same body is 4,005,362, beyond it.
This must not be presented as a large nonwitness block: for illustrative stripped
child-vector length 1,000, the current child block weight would be
`3*(80+1000)+(80+3995000)=3998320`, below 4,000,000 under the
[current weight formula](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/consensus/validation.h#L127-L139).
This is conditional arithmetic, not a constructed valid transaction/UTXO,
Merkle, proof or mined-block fixture.

A compact view containing A1 and short transaction IDs can be much smaller
than its reconstructed body. If it reconstructs the same child vector, the text
does not explicitly choose between enforcing an A1-dependent reconstructed full
size, a proof-independent body bound, or only compact-wire/current-child bounds.
If A1 remains the FIRST sidecar while a full A2/body is accepted, a complete rule
is also needed for retrieval/export/reindex and retention of a size-compatible
record. The existing availability distinction does not select this policy.

For a later reviewed revision, possible designs include a uniform worst-record
child-vector budget across full/compact/reconstructed/disk views, or explicit
attachment-scoped capacity with corresponding serving, alternative retention,
replacement and failure rules. The first reduces usable payload; the second
needs a complete state machine. Neither is adopted here. Extending the template
reserve to consensus/admission views without review would be a normative change.
Future V01/V07/V09/V12/V13/V14 must cover both proof sizes, both arrival orders,
compact reconstruction, serving and restart; oversized attachment failure must
not silently become permanent Hc invalidity.

### R02. A retention cap does not preserve native presync liveness

[B1 presync](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/doc/andaluzcoin-auxpow-b-candidate-specification.md#L438-L465)
references the native screening/redownload state machine but caps retained
synchronization units at 4,096 per peer and 32,768 globally. Native MAIN's
[provisional parameters](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/kernel/chainparams.cpp#L175-L179)
use commitment period 641 and redownload lookahead 15,218. Native
[commitment collection](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/headerssync.cpp#L177-L208)
is sparse, while [redownload release](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/headerssync.cpp#L241-L292)
waits for sufficient work or more than the configured lookahead.

Consider a permitted positive CFG1 MinAdmissionWork requiring 10,000 remaining
equal-work headers from a known anchor. At most 16 sampled commitments suffice
in presync. Redownload, however, exceeds 4,096 retained headers before reaching
either that threshold or the native 15,219-header release point. Counting the
remaining commitments against the same unit pool only tightens the obstruction.
Thus that combination cannot inherit native progress merely by adding a cap.
The threshold, chain and outcome are a conditional paper/arithmetic case, not
an executed synchronization experiment or evidence about actual participation.

This is not a universal claim that 4,096 units make synchronization impossible.
B1's exact CFG1 threshold may be zero or already reached; a different compatible
algorithm/parameter set may work. Current source nMinimumChainWork=0 alone is
also not the whole native threshold policy: [GetAntiDoSWorkThreshold](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/net_processing.cpp#L2635-L2645)
can include near-tip work. B1 explicitly chooses CFG1's threshold, and must not
silently inherit a different native threshold while claiming that contract.

A later design must specify compatible lookahead/commitment/retention behavior,
proof-receipt retention and threshold provenance, then establish anti-DoS
security and valid-chain progress for its supported domain. Simply lowering a
buffer or releasing earlier can weaken the commitment defense. Exceeding a
local cap remains availability/admission failure, not invalid-child evidence.
Future V05/V06/V07/V18 need long-chain, competing-peer, restart and cap-boundary
cases plus allocation/work measurements. B1 already disclaims general IBD
liveness; this review identifies one concrete dependency behind that disclaimer.

### R03. Representable height is not an operational native range

[B1 height admission](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/doc/andaluzcoin-auxpow-b-candidate-specification.md#L159-L178)
and [V15](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/doc/andaluzcoin-auxpow-b-candidate-specification.md#L642)
permit a child at 2,147,483,647 and reject another header whose parent is at
that height before adding one. This correctly bounds that admission operation.
It does not protect every native caller that installs or uses that terminal tip.

[CChain::SetTip](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/chain.cpp#L16-L24)
resizes its vector using signed `nHeight+1`; even installing the allowed terminal
height needs a safe representation/allocation policy. The
[Next helper](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/chain.h#L415-L422)
also adds one before indexing. Merely rejecting a later submitted header does
not guard either operation.

Unchanged examples calculate signed `tip.nHeight+1` in
[GetMinimumTime](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/node/miner.cpp#L36-L46),
[template assembly](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/node/miner.cpp#L131-L140),
[mempool finality](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/validation.cpp#L146-L167),
[lock-point calculation](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/validation.cpp#L211-L223),
and [mining RPC output](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/rpc/mining.cpp#L1030-L1038).
The mathematical successor 2,147,483,648 exceeds signed32 representation.
No terminal-height node was constructed or run, and no present practical ALUZ
exploit is claimed. The concern is completeness of the proposed native boundary.

Before integration, inventory and guard every relevant successor calculation,
including proposal/template/mempool/restart and supporting call paths, and
define consistent safe terminal behavior before addition/conversion. Retaining
the admitted range with checked fail-closed callers differs from changing the
accepted height domain; a changed domain requires separate exact review and a
new manifest/ProfileID as applicable. No bound or source is changed here; large
chain-vector allocation and retention also need resource qualification, not just
an arithmetic conversion fix.
Expand future V15/V17/V18 beyond next-header acceptance and use actual native
boundary/error tests only in a separately authorized phase.

### Q01. Restate the parent-header byte layout

B1 explicitly defines C80 as current six-field serialization, while
[P80 framing](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/doc/andaluzcoin-auxpow-b-candidate-specification.md#L227-L237)
and [root/work predicates](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/doc/andaluzcoin-auxpow-b-candidate-specification.md#L305-L323)
describe an 80-byte parent header with hashMerkleRoot and opaque work
fields. The conventional layout can be inferred from the pinned precedent;
this is not a demonstrated second valid interpretation or exploit.
Before an independent exact-byte verifier freeze, explicitly state parent
version[0:4], prevhash[4:36], Merkle root[36:68], time[68:72], bits[72:76],
nonce[76:80], and H2 over exactly all 80 supplied bytes. Field opacity does not
mean the verifier may choose its own Merkle-root offset. Record whether the
clarification is nonsemantic or requires a revision; never silently reuse P
for changed acceptance semantics.

### Q02. Specify genesis verification and initial evidence/work

[B1's genesis exception](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/doc/andaluzcoin-auxpow-b-candidate-specification.md#L174-L197)
requires exact configured GenesisC80 and DIRECT at height zero. The general
DIRECT rule also requires numeric work, while the target rule derives expected
bits from ancestry. There is no genesis pprev. The
[native admission exception](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/validation.cpp#L4218-L4260)
skips ordinary PoW/context checks for the configured genesis, and
[GetNextWorkRequired](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/pow.cpp#L14-L16)
requires a nonnull predecessor. A verifier must not invent an ancestor or call
that function on null to complete the base case.

The next exact specification should state genesis expected-bits/target-range
and numeric-check behavior and how the first explicit DIRECT evidence sidecar
is initialized/revalidated. Native
[index creation](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/node/blockstorage.cpp#L241-L251)
starts from zero and adds GetBlockProof for genesis; the future B1 contract must
state its initial work/receipt convention rather than infer zero credit from
the ordinary admission bypass. Preserve exact configured genesis identity;
never manufacture AUX genesis or a new chain. No invalid current MAIN genesis
or executed startup failure is alleged. This makes the bootstrap verdict and
durable base state independently reproducible, without permission to change
today's parameters. Future V01/V03/V05/V12/V15 must distinguish exact genesis,
altered genesis and ordinary descendants.

## 4. D01-D03 reasoning retained with qualifications

No additional concrete counterexample was found in this bounded review to the
specified same-history AUX reuse argument. This is an inspection result only.
[B1's argument](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/doc/andaluzcoin-auxpow-b-candidate-specification.md#L327-L357)
depends on literal parent index zero, canonical coinbase length greater than
64, one marker across the entire stripped transaction, fixed carrier
P/root/depth/nonce, common tagged node geometry and one K-only slot independent
of Hc/P. Collision and preimage/second-preimage/fixed-point assumptions are not
interchangeable. The immutable DIRECT-to-AUX restriction excludes the documented
AUX-to-DIRECT promotion counterexample; it does not prove a general hybrid safe.

The claim is scoped to one accepted ancestry. Incomparable forks may reuse work;
DIRECT framing K/P is not cryptographic work binding; a stripped txid does not
certify witness absence/validity; one Merkle path does not establish full-tree
mutation freedom; parent numeric work does not certify a parent chain's rules
or membership. None of these disclosures is removed by this review, a green CI
result or the unchanged candidate ProfileID.

## 5. Critical decisions and evidence still required

| Decision / evidence | Why it remains open |
| --- | --- |
| Exact candidate and revisions | Resolve R01-R03/Q01/Q02, review any normative change with a new revision/P, and freeze the independently implementable contract. No official literal or approval is supplied here. |
| Network manifest and activation agreement | CFG1/BIND1 protects one store. Identical K/P/genesis with different H can select conflicting routes between the two heights. One reviewed network mapping, H, distribution/governance and upgrade-readiness procedure is needed; local immutability is not inter-node agreement. |
| Mode and recovery policy | Retain or replace the monotone policy only by critical review. BOTH, reversal, profile reset and automatic pool-exit DIRECT recovery remain forbidden in B1, including emergencies. |
| Migration and old-node behavior | New wrappers affect even pre-H DIRECT wire/disk/mining views. Hc preservation does not establish compatibility. First parent-only accepted work creates the stated hard fork; old-binary downgrade and profile-history/revalidation need a separate migration/recovery plan. |
| Real production and security budget | No miners, hash rate, concentration or participation commitments are demonstrated. P80 is opaque work: a B1-compatible standalone producer could mine a synthetic parent header; actual Bitcoin-parent membership is not required. Withdrawal removes neither the need for valid B1 work nor the need to measure replacement production. |
| Difficulty and incentives | Existing MAIN 2016-block retarget, limit saturation and no wall-time escape remain. AuxPoW does not produce miners, fix current difficulty economics or import a parent's attack resistance. See the separate mining study. |
| Independent implementation/security/operations | No numeric verifier agreement, malformed-proof corpus, allocator/race/crash evidence, organizational security review, signed release qualification or independent WAN/mining trial is supplied by this dossier. |
| Launch scope and accountability | Whether AuxPoW is a launch prerequisite is not settled. Accountable operators/reviewers and every applicable mainnet gate still need evidence and separate decisions; no person/service is assigned by this review. |

The [mode/withdrawal text](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/doc/andaluzcoin-auxpow-b-candidate-specification.md#L570-L595)
and [mining sustainability study](andaluzcoin-mining-sustainability.md#1-executive-summary)
make these costs material. Pool withdrawal does not logically force a stall if
other B1-compatible producers supply adequate work; that replacement and its
security are unproved. Zero mining produces no blocks under either route.

Three concrete integration obligations also need explicit future state tables;
these are not additional demonstrated intrinsic-proof grammar contradictions:

- **Ancestor evidence closure:** for indexed A-to-B, with A's sidecar missing
  and B's intact, specify the evidence/anchor closure needed for B eligibility
  and how repair restores it without double credit. Native
  [index loading](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/node/blockstorage.cpp#L454-L499)
  rebuilds nChainWork from parent work/bits; that alone cannot authenticate a
  future missing sidecar. Historical facts, temporary availability and eligible
  work must remain distinct, without permanent invalidity from data loss.
- **Publication freshness:** consider successful child verification, then a
  properly invalidated parent while sidecar I/O is pending, then publication.
  Immutable child bytes and a per-Hc first-writer lock do not alone protect
  mutable ancestry conditions. Specify a protected snapshot or revalidation at
  the publication linearization point, consistent with native
  [admission exclusions](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/validation.cpp#L4218-L4265).
  No particular lock design or crash/race result is supplied here.
- **Compact body failure scope:** a correct proof with a bad reconstructed body
  must preserve fallback/attachment versus intrinsic-child failure distinctions.
  Inspect the native [reconstruction result](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/blockencodings.cpp#L191-L222),
  [full-block fallback](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/net_processing.cpp#L3484-L3504),
  [mutation exclusion](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/validation.cpp#L1985-L1993)
  and [pre-admission body check](https://github.com/andaluzcoin/andaluzcoin/blob/5f49d6a08ba3a4ac44f8db54f3a71a07a19583d1/src/validation.cpp#L4439-L4451)
  in future V07/V09/V10/V12/V13 tests. Proof success is not body success, and a
  potentially mutated/colliding reconstruction must not permanently poison Hc.

## 6. Evidence mapping and safe parallel packages

All V01-V18 are still **UNIMPLEMENTED/UNEXECUTED** candidate acceptance
requirements. The mapping below is a dependency plan, not a pass report.

| Gates / V cases | Required later evidence | Dependency |
| --- | --- | --- |
| D01/D02/D03; V01/V02/V03/V04/V08/V11 | Exact bytes/offsets, trusted domain/profile, actual numeric target boundaries, independent parent/proof predicates and conditional work-reuse negatives. | Resolve affected exactness findings and freeze input; separately authorize isolated implementations. |
| D04/D05; V05/V06/V09/V10/V15 | Ingress/known-header/context, compatible presync, admission bounds, attachment failure/replacement, immutable cache/race receipts and terminal-tip operations. | R02/R03 plus context/failure contract; actual native tests are later work. |
| D01/D04/D05/D07; V07/V12/V13/V14 | Cross-view capacity, compact/transaction fallback, proposal/template versus submission, selected sidecar/serving, import/reindex/prune/crash durability. | Resolve R01 and storage/availability design before integrated verdict claims. |
| D06; V15/V16 | Fixed ancestry H-1/H/H+1, mismatched configuration, mode/upgrade/old-node/reorg/reconnect/rollback behavior. | Symbolic review may proceed now; real mappings/activation and node trials need separate decisions. |
| D08; V17/V18 | Frozen mainnet/descriptor-only invariants, independent security/resource review and qualified operational/release evidence. | No integration or launch approval follows from source inspection or research CI. |

Useful parallel packages, each with its own finite scope and report:

| Package | Can proceed as review-only planning | Executable/operational gate |
| --- | --- | --- |
| P0: exactness correction options | Resolve R01/R02/R03/Q01/Q02 alternatives, rejection classifications and revision impact in a separately scoped drafting phase. | Freeze a reviewed exact contract; do not amend revision2/P implicitly. |
| P1: independent verifier/fixture design | Define provenance, raw bytes/seals/offsets, verdict layers and independence protocol. | Separate approval for real B1 executable work after freeze; independently authored implementations must not share an encoder/oracle while claiming independence. |
| P2: context/mode/native-boundary matrix | Inventory fixed ancestry, mismatched-H, unknown context, successor and compatibility cases. | Actual context/node/activation tests require the selected specification and separately authorized implementation. |
| P3: relay/storage/resource plan | Trace per-route buffers, complete payload capacity, first-writer/repair, crash cuts, pruning and reacquisition. | Integrated measurements/fuzz/race/crash tests require reviewed code and accepted protocols. |
| P4: launch-evidence planning | Draft current-rule mining/withdrawal and operator/WAN/wallet/reproducible-distribution/recovery evidence protocols, thresholds and accountability requirements. | No outreach, endpoints, mining, hardware/service claims, deployment or jurisdiction-specific professional disposition is authorized by planning. |

P1 planning, P2 inventory, P3 planning and P4 desk research can run alongside
P0 once separately scoped; they cannot supply missing normative answers by
independent guesswork. After the contract and executable scope are approved,
two independent verifier implementations can run in parallel against frozen
public fixtures, with separately derived expected results and cross-checks.
Production integration, adversarial/recovery qualification and authorized
real-world evidence remain dependent later stages. Some wallets/distribution
planning is independent of AuxPoW; real launch evidence still needs accountable
participants. No fixed milestone count or launch date is promised.

## 7. Next-phase eligibility and completion boundary

The next recommendation is a finite **specification-disposition/correction
phase**, returning concrete revised options and their manifest/profile impact
for exact review. Eligibility for an unconditional all-view B1 verifier or
production patch is HOLD. Narrow scalar/hash fixture planning does not waive
R01-R03, and this review does not authorize implementing even a subset parser.
Do not treat a protocol engineering choice as automatically owner-approved
because a documentation PR has all-green CI.

The later order is: resolve/freeze contract and critical scope decisions;
separately authorize isolated executable evidence; obtain independent results
and security disposition; separately authorize production integration; qualify
compatibility/recovery/resources; obtain separately authorized operational
evidence; record the release/GO decision for the specific revision.

Research completion means review findings, limitations, actual checks and
dependencies are published under #105's all-green workflow. It closes no D gate,
V requirement or mainnet checkbox. The execution report records the final PR
head/tree, review/CI, any permitted regular merge and actual-master CI, and the
independently verified annotated research tag before tracker closure.
No automatic retry or failed-check waiver is implied by earlier milestones.

See the [separate correction proposals](andaluzcoin-auxpow-b-specification-corrections.md)
for concrete drafting dispositions and the unresolved exact-freeze conditions.
