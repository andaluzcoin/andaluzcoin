# B1 resource decisions and isolated measurement charter

## 1. Status and finite objective

**v0.2.89 is a proposal awaiting critical scope approval, not cost
qualification.** [Tracker #113](https://github.com/andaluzcoin/andaluzcoin/issues/113)
continues the [v0.2.88 handoff](https://github.com/andaluzcoin/andaluzcoin/issues/111#issuecomment-6711774059).
It provides a bounded first experiment and the evidence path to selecting
real resource budgets. No experiment described here has been implemented or run.

Frozen baseline B is **b91ad859ccec3362eaedf27e158273907817566a**, tree
**5170f14ee1b49f3b24849495e4757746b127fc0f**. The
[eligibility input register](https://github.com/andaluzcoin/andaluzcoin/blob/b91ad859ccec3362eaedf27e158273907817566a/doc/andaluzcoin-auxpow-b-security-cost-eligibility.md#2-input-and-evidence-register)
and C1-C8 remain the requirements. The owner's
[one-fixed-profile decision](https://github.com/andaluzcoin/andaluzcoin/issues/111#issuecomment-6708955217)
approves future drafting direction only. It supplies no operator budget,
executable permission, production profile, new P or network mapping.

Repository/GitHub recovery still finds no chosen deployment host, operator
RAM/CPU/network/storage/service budget or independent B1 implementation.
Build-machine advice and hosted CI runners are not node capacity evidence.
Rather than require already-qualified production literals before collecting
any measurements, section 3 proposes a narrow, explicitly approved component
experiment gate. The production freeze requirement stays in force.

All D01-D08 remain OPEN, all 21 mainnet gates unchecked, mainnet **NO-GO**.
Mainnet consensus/genesis/PoW/DAA/subsidy/identity/network parameters and the
descriptor-wallet-only policy remain unchanged. Operational R02, complete
production freeze, integration, activation, migration and deployment stay HOLD.

## 2. Concrete resource proposal and outstanding operator decisions

The recommended immediate choice is **local component measurement first**,
followed by actual operator targets and integrated qualification. The following
NEW limits are proposed campaign guardrails, not recovered project requirements,
minimum node hardware or qualified B1 policy values. Their purpose is to bound
one small experiment without buying infrastructure or contacting a network.

| First-campaign item | Proposed exact limit and meaning |
| --- | --- |
| Host | Existing authorized local Windows x86_64 desktop only; no remote host, rented service, toolchain download, node or miner. Record its exact OS/build, CPU/features, physical/available RAM, storage/filesystem, compiler/target/allocator and background-load observations before measurement. Unavailable required metadata is a preflight failure, not permission to infer it. |
| Execution | One native worker process at a time; independently authored Python oracle runs separately. No worker child process, network operation, listening port, GPU or parallel campaign. Compilation is a separate sequential phase under the same aggregate limits. |
| Memory | Enforced aggregate process-tree committed-memory ceiling 1 GiB, including supervisor/compiler/oracle/worker; no assumption that private bytes, working set and committed bytes coincide. Record all available metrics with their API definitions. If enforcement or measurement is unavailable, do not start measured work. |
| CPU/time | Stop thresholds: 600 aggregate process-tree user+kernel core-seconds; 1,800 campaign wall seconds from first compilation/oracle action; 30 wall seconds per measured worker-case. A supervisor polls at a requested interval no greater than 10 ms; record actual gaps and termination/cleanup overshoot. These are stopping policies, not hard CPU/wall ceilings. Any threshold overrun prevents PASS. Include warmups, failures and cleanup; no automatic repeat of a failed/stopped campaign. |
| Files | Monitored stopping threshold 2 GiB of live logical scratch-file lengths, including compiler/temp outputs and failed runs, in one fresh workspace subdirectory. This is not a hard filesystem quota; record actual scan gaps, observed peak and overshoot. Independently cap all mediated worker/oracle/supervisor/compiler-console output at 64 MiB cumulatively, checking BEFORE each write. No export of sources, secrets, wallet/datadir material or user files. |
| Network/storage scope | Zero application network traffic. Synthetic volatile buffers only; no chain archive, filesystem durability/repair benchmark, mining, actual proof acquisition or public service. Pin compiler output/TMP/TEMP/cache paths to the scratch directory; disable incremental/external caches and downloads. Ordinary compilation/output writes are observed; no claim that file lengths measure cumulative writes or physical storage. |
| Measurement scope | Exact synthetic byte operations and native allocation lifetimes in section 4; no candidate parser, proof/context/work verifier, synchronization state machine, optimizer or node code import/run. |

Here 1 MiB=2^20 bytes and 1 GiB=2^30 bytes. A polled watchdog is not hard
memory enforcement. A reviewed supervisor must establish an aggregate Windows
Job Object commit limit, child containment and monotonic stopping policies
before launching descendants; stop before exceeding the mediated-output
allocation. Unmediated compiler files use the explicit monitored scratch policy,
not a claimed bounded writer or new filesystem quota. Windows
[job user-time limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information)
do not directly cap aggregate user+kernel core-seconds. The
[job memory limit](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)
constrains job-wide committed memory. Report
actual complete-tree totals and any overshoot rather than asserting a hard
CPU/wall bound. Failure to establish the specified controls blocks execution.
Do not deliberately consume the limits. No priority, operating-system security
or authentication changes.

The reviewed containment design must use JOB_OBJECT_LIMIT_JOB_MEMORY with
JobMemoryLimit=2^30, verify queried limits/membership, prohibit breakaway and
account for the dedicated supervisor plus compiler/linker/oracle/worker. Create
descendants suspended and assign them before resuming. Account for controller
startup and pre-assignment allocations; do not silently omit an external
monitor. Review nested-job compatibility, kill-on-close and final exited-process
accounting. No benchmark starts merely because an API name exists. Win32 FFI
needed for reviewed control/measurement plumbing is within the proposed scope;
unsafe payload manipulation in the native worker is excluded.

An eventual operator budget must separately choose the following; **none is
selected by approving this first-campaign proposal**. A later proposal should
use measurements to make these choices concrete rather than treating the
campaign's 1 GiB limit as a node or synchronization allowance.

| Actual qualification input | Required decision and evidence |
| --- | --- |
| Supported operator environment | Intended OS/architecture/compiler/allocator, CPU/SHA path, RAM/storage, simultaneous node workloads and measured baseline peak. This Windows experiment establishes no Linux or other-platform support. |
| Temporary memory | Total allocated/committed/RSS objectives and disjoint residual session budget after ordinary peers, block/RPC/import pools and baseline; input, retained owners, metadata, receipts, scratch and writer overlap all charged. |
| CPU/network/service | Sustained/burst CPU and application/transport bandwidth, admitted-peer/domain limits, deadlines and honest minimum share/completion objective. Bounded memory alone does not qualify responsive-peer service. |
| Permanent growth | Separate index RAM, logical/canonical archive bytes, physical writes/inodes, retained orphan/repair data, absolute headroom, observation horizon, honest route/proof-size reference and permitted excess-growth rate in each resource. |
| Cost/security domain | Actual trusted anchor/evidence closure/T/route/restart/bypass histories, nonwrapping claim scope, adversary capacity and mandatory per-attempt cost in identical units. Reusable prior mining is not automatically a fresh attempt cost. |

Each adopted target needs accountable owner, exact units/status/provenance,
platform/domain/horizon, omissions/uncertainty, independent reviewer and pass
criterion. Unknown is neither zero nor unlimited. p/ell/K/Q must ultimately be
selected jointly against these inputs; no experimental size below selects them.

## 3. Proposed scoped exception and two freezes

[Presync F4](https://github.com/andaluzcoin/andaluzcoin/blob/b91ad859ccec3362eaedf27e158273907817566a/doc/andaluzcoin-auxpow-b-presync-design.md#9-actual-evidence-and-finite-next-qualification)
requires separate approval and complete freeze before executable evidence.
**Proposed amendment M01:** after explicit owner approval of this charter's
scope, allow one standalone, nonadmitting component campaign under a complete
experiment freeze, before the complete production successor profile exists.
This is a new proposed exception, not an interpretation of prior approval.

The experiment freeze comprises this exact document commit/hash, reviewed
supervisor/native/oracle/generator sources and binaries with SHA256, offline
compiler/library versions and flags, exact platform/allocator/CPU feature path,
fixture manifest/expected outputs, quotas and immutable case/run identifiers.
First freeze/review source, build recipe, fixture-generation rules and controls;
after controlled preparation freeze/review binaries and expected fixture outputs
before executing measurement. The campaign clock includes this review wait; it
is not paused or reset. Prepare reviewers in advance; a missed deadline stops
the campaign rather than permitting unfrozen execution or an automatic retry.
No hash, platform fact or expected output may be filled retrospectively after
looking at timing results. Preflight may read metadata and compile only after
the scope decision; compilation and oracle work count against the campaign.
If the complete pre-run freeze cannot be established, report BLOCKED.

A case/run ID identifies an experiment, not B1 P, CFG1/ConfigID, LedgerKey,
network H or accepted evidence. It must never be placed on a live wire or store.
No revision2 record is reinterpreted, and no new profile manifest/P is allocated.
Native worker operations are exactly section 4; importing native repository
code or changing semantic scope requires a new reviewed authorization.

**Production freeze remains separate:** all qualified literals, exact C1-C8
semantics, manifest/P/full-document/source mapping, every-view reconciliation
and the independent evidence plan must be complete before corresponding B1
verification/sync/integration experiments. M01 grants none of those permissions.
Actual cost qualification is still INELIGIBLE until its full evidence exists.

## 4. M1: exact first component campaign

### Independent authorship and fixed bytes

Use a standalone native Rust worker with the system allocator and no external
package downloads, and an independently authored Python standard-library oracle.
These choices match command availability recovered on the local host; usable
versions/linker/limits still require preflight. They measure those runtimes,
**not the node's C++ allocator or proof verifier**. A later matching C++ node
allocator campaign is required for any claim about its native envelope.

One author specifies/generates fixtures and expected byte/digest results; a
different author implements the native operations from this charter without
copying the oracle's algorithm. A third review, or root independent of both
authors, checks the freeze and reconciles all outputs. Assistance in one workflow
is not an external organizational audit or independent B1 implementation.

For case index c starting at zero and byte index i starting at zero, synthetic
buffer byte b[i]=(i+17*c) mod 256. Indices use checked nonnegative integer
arithmetic. These are arbitrary byte strings, **not valid HeaderRecords,
proofs, chain headers or PoW**. Do not serialize candidate magic/K/P or claim
acceptance. Generate/check each case separately; never retain a hidden corpus.

### Operation cases and repetitions

| Cases | Exact operation |
| --- | --- |
| H00-H15 | Lengths, in order: 0,1,55,56,63,64,65,80,96,101,154,155,388,8192,10362,10426. Compute SHA256(x), then H2(x)=SHA256(SHA256(x)), with raw 32-byte digests. Hash arbitrary bytes only; no claimed proof validation. |
| T00-T02 | Lengths 155,388,10362; q=SHA256(ASCII ALUZ-B-CANDIDATE/evidence/1), no NUL/LF; compute H2(q concatenated q concatenated x). Compute q once per worker before sampling; report that single setup duration/output separately and charge it to the case. No cached-midstate or accepted-E performance claim. |
| A00-A02 | Q=16,15887,18147 respectively; R=10362 bytes. Allocate/touch, in this order, one contiguous Q*R arena, a 418777-byte bit buffer, a 165857-byte input buffer, a 64*R scratch buffer and an 8*R scratch buffer; observe the simultaneous live peak, then release in reverse order. The bit-buffer size is the earlier illustrative a=0,p=641 payload, not an adopted K or native bound. |
| L00-L02 | Establish the corresponding A buffers; create 16 immutable views with offsets j*R and length R, j=0..15, without payload copies. Allocate/copy arena[0:R] into an R-byte writer, then allocate/copy the entire arena into a second Q*R writer while every prior buffer remains live. Verify both copies; release large writer, R-byte writer, views, then A buffers in reverse allocation order. |
| F00-F02 | Establish the corresponding A buffers and the 16 L views, then deny the R-byte writer allocation through a deterministic test allocator shim BEFORE allocation. Release views then A buffers in reverse order, once each. No subsequent large writer is attempted. This is synthetic denial/cleanup, not real OS OOM or node cancellation. |
| C00-C02 | Establish the corresponding A buffers/views and successful R-byte writer as in L, then inject a local cancellation branch immediately after the writer copy/check. Do not attempt the large writer; release R-byte writer, views, then A buffers in reverse order, once each. No generation, synchronization or durable-store semantics are exercised. |

Payload seed c is 0..15 for H00..H15, 16..18 for T00..T02 and 19..21 for
A00..A02. Each L/F/C case reuses its corresponding A seed. Each separately
allocated A buffer starts at byte index i=0 with that seed; views/copies inherit
the selected arena bytes, with no reseeding. Verify every live payload/copy by
streaming SHA256 before its release; report requested bytes and actual exposed
capacity separately. All checking is included in the measured lifecycle. Oracle
supplies expected logical lengths/digests/lifetime events; it need not duplicate
native allocation and cannot certify its RSS.

The arena sizes reuse [v0.2.88 illustrative frontiers](https://github.com/andaluzcoin/andaluzcoin/blob/b91ad859ccec3362eaedf27e158273907817566a/doc/andaluzcoin-auxpow-b-security-cost-eligibility.md#4-consistent-cost-units-and-byte-frontier-sensitivity)
and its count frontier: 15887=15871+16 and 18147=18131+16. R/input sizes come
from the [candidate grammar](https://github.com/andaluzcoin/andaluzcoin/blob/b91ad859ccec3362eaedf27e158273907817566a/doc/andaluzcoin-auxpow-b-candidate-specification.md#6-exact-candidate-headerrecord-and-proof-bytes);
418777 is the [presync packed-bit example](https://github.com/andaluzcoin/andaluzcoin/blob/b91ad859ccec3362eaedf27e158273907817566a/doc/andaluzcoin-auxpow-b-presync-design.md#typed-reservation-and-full-height-commitment-envelope).
They are diagnostic fixture dimensions, not approved profile parameters.

For every H/T case: correctness once, then 3 warmup samples and 15 recorded
samples, exactly 4096 complete operations per sample. SHA256 and H2 in each H
case are separately labelled operations and sampled separately. Do not fold
digest outputs into later inputs. Apply a reviewed per-operation input/output
optimization barrier in the native loop (for example, pinned Rust black_box
treatment) and check every digest. Checking identical results alone does not
prevent loop hoisting; a barrier is a best-effort aid, not a guarantee.
Independently review the generated artifact or instrumentation to establish the
4096 intended complete operations and actual allocation/copy overlap. Record
barrier/check overhead as included. For every A/L/F/C case: correctness once, then
1 warmup and 5 recorded samples, exactly one lifecycle per sample. Separate
worker process per case/operation, sequential only; the 30-second worker-case
deadline covers correctness, warmup and recorded samples together.

Generate H/T inputs and expected outputs before the sample timers. Start the
wall/process-CPU sample interval immediately before its operation loop and stop
immediately after its last checked result; include barriers/checks, exclude
receipt formatting/output. For A/L/F/C, include the entire allocate/fill/view/
copy/digest/check/release lifecycle between the sample timers; exclude receipt
formatting/output. Process/campaign totals still include everything. The frozen
implementation must identify its clocks/resolution and compiler treatment;
[Rust's optimization-barrier documentation](https://doc.rust-lang.org/std/hint/fn.black_box.html)
explains why source-loop counts alone are insufficient.

The allocator shim is a deterministic local branch with explicit logical
accounting; it never pressures the host to actual OOM. No write outside owned
buffers, unsafe payload manipulation, random proof search or filesystem fault
injection is permitted. Bounds/cleanup correctness must pass before timing.
Record every sample, failure and stop; no adaptive repetition, outlier deletion,
background tuning, unreported warmup or selecting a faster platform.

### Evidence and exit criteria

The receipt records the complete frozen manifest, author/reviewer provenance,
correctness outputs, per-operation/sample wall and process CPU durations,
timer definitions/resolution, every requested/capacity/overlap byte count,
process-tree committed/private bytes and working-set peak with collection
method/coverage, and retained capacity after release. Record whether peaks
come from OS counters, allocator instrumentation or sampling; do not relabel
a sampled observation as a proven supremum. Report compiler/SHA implementation
and feature path, load, elapsed/CPU/scratch totals and all omissions. Never
infer a hardware-accelerated path solely from available CPU features.

PASS means all expected digests/lengths/lifetime/cleanup outputs agree, no
quota/control failure, no missing sample and a reconciled independently reviewed
receipt. Timing has no preselected throughput pass target: first M1 characterizes
its exact components. A timeout, unavailable metadata/toolchain/control, output
mismatch, unexpected allocation or quota event is FAILED/BLOCKED as appropriate;
preserve diagnostics and stop. No automatic rerun, limit increase or waiver.
Compile/oracle/supervisor problems count; failed measurements are evidence too.

Positive deliverable: reproducible native synthetic allocation/copy/hash
observations and a checked measurement method, contributing to an F2 component
slice. This does not complete F2, supply B1 proof/context cost, establish a
uniform adversary lower bound, select p/ell, qualify F3 or demonstrate service.
Cross-runtime agreement concerns bytes/operations only; timings/allocator peaks
need not agree. CI duration and symbolic byte arithmetic are separate evidence.

## 5. Subsequent qualification contracts and parallel work

The following streams can be specified/reviewed in parallel. Each executable
campaign needs its own complete semantic/input/platform/code/fixture freeze and
appropriate scoped authorization; M01 does not allow implementing/running them.

| Stream | Required next evidence and limiting dependency |
| --- | --- |
| Native B1 verification | Independently authored canonical grammar/numeric/context/proof implementations and independent expected fixtures; exact valid min/max DIRECT/AUX, late-invalid/E cases, parent/route/clock/work domains. Complete semantic freeze first; no synthetic length is a valid proof or cheap mining permission. |
| S1 native envelope | Matching node C++ allocator/layout; disjoint ordinary/input/pending/active/Q/receipt/scratch/writer charges, Q-full flush, shared/copy ownership, phase lifetimes, cancellation/generation and blocked-drain cleanup. Actual independent ownership implementation and platform evidence are required. |
| Security and repeated costs | Adaptive leakage/strategy analysis and eligible uniform cost across evolving anchors, threshold/direct/known-Hc/import/RPC bypass, restarts, same-Hc FIRST size choices, repair and orphan I/O. Defender throughput upper bounds do not establish mandatory attacker cost. |
| Permanent storage | Logical sidecar/index and physical filesystem/inode/write/fsync/journal growth; independently valid fixture provenance, FIRST/durable acknowledgment, lost/corrupt repair, restart/recovery and orphan retention. Qualified reference growth/horizon and absolute budget needed. |
| Service | Bounded admitted-peer/domain model, responsive below-T sessions, lease/rotation/cancel/drain and honest service/completion. Safe refusal and one global owner are not universal liveness. |

Do not claim a valid Q-sized ALUZ-work chain exists without reviewed acquisition
provenance; no public mining/network experiment or upload follows. Replay may
reuse a valid prefix, so previously expended proof-generation work is not a
per-attempt cost unless its necessity is justified. The scalar U certificate is
only its stated below-threshold fixed-path model; failed bounds are not attacks.

## 6. C1-C8 and the approval record

| Decision | Carried-forward disposition |
| --- | --- |
| C1 | One immutable production profile drafting direction recorded. M1 run/case IDs are separate; no PolicyID, new P or unchanged-P mutable S1 object. |
| C2 | Actual operator targets and uniform domains still require owner decisions plus independent evidence. M1 quotas and Q fixture sizes allocate no production budget/parameter. |
| C3 | Preserve modular ledger work and the distinct first-entry/PRESYNC end-of-batch versus REDOWNLOAD sticky per-record predicates. Initial nonwrap claim recommendation remains proposed; M1 performs no chainwork or threshold operation. |
| C4-C7 | Receipt/phase lifetime, typed pending/active/Q owners, batch/failure ordering, generation/ancestry-protected eligibility, historical credit/restoration and service must be resolved in the full successor. Synthetic view/copy/cleanup cases do not adopt or test those semantics. |
| C8 | R01/R03/Q01/Q02 and all every-view/genesis corrections remain proposed/unimplemented; compatibility, official H/mapping, migration and deployment stay HOLD. |

**Pending critical decision:** approve M01's narrow exception and the exact
section 2/4 first-campaign scope, permitting later implementation, independent
pre-run artifact review/freeze and one bounded local campaign only if those
gates pass; or retain the original complete-production-freeze prerequisite.
No answer or elapsed time supplies approval. Scope approval would select these
lab guardrails only; actual operator budgets remain a separate decision.

Current status is **PROPOSED / NOT APPROVED / NOT EXECUTED**. The tracker/PR
must record the exact reviewed document revision and actual answer before
dependent work. Material operation/platform/quota changes require review and
new scoped approval. This charter's documentation/CI review cannot substitute
for the critical decision or for later executable correctness/resource evidence.

Research publication still follows issue -> isolated branch -> execution report
and PR -> exact-head technical/owner review and required CI -> permitted regular
merge -> successful actual-master CI -> independently verified annotated
research tag -> final report/closure. No old CI retry/waiver permission remains;
no milestone completion, merge or tag is claimed while the required gates wait.

Preparation follow-up: [v0.2.90 controls contract](andaluzcoin-auxpow-b-preparation-controls.md).
Both preparation attempts stopped; the contract is design only and grants no new execution or qualification.

## Diagnostic packet continuation

See [the proposed evidence-packet and readiness specification](andaluzcoin-auxpow-b-diagnostic-packet.md); diagnostic execution remains BLOCKED and measurements HOLD.
