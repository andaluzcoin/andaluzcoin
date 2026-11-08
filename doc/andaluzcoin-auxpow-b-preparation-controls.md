# B1 preparation controls and qualification contract

## 1. Authority, finite deliverable and evidence boundary

**v0.2.90 is design research; no diagnostic is approved or executed.**
[Tracker #115](https://github.com/andaluzcoin/andaluzcoin/issues/115) continues
the completed v0.2.89 handoff at frozen baseline B
**03be3d29466ba509de94abbd7e212ffe1fa94f3b**, tree
**1a7e2eaa175240a177ce6a9c2551f780162399c3**.

This milestone drafts and reviews a launch/console/containment contract.
It does not execute that contract, reopen M01, qualify costs or adopt budgets.
The owner's general instruction to proceed retains mainnet NO-GO.
The [v0.2.89 completion](https://github.com/andaluzcoin/andaluzcoin/issues/113#issuecomment-6721769262)
requires a separately reviewed native launch/console/containment scope before another campaign.
All previous experiment and CI retry allowances are consumed; old markers and runs remain permanent.
The positive deliverable is a source-backed model, explicit unknowns and a finite future diagnostic protocol.
No compiler, linker, oracle, worker, native API trial or benchmark is authorized by this document.
No node/B1 parser/proof/sync code, network operation, deployment or parameter change is included.
All mainnet consensus/genesis/PoW/DAA/subsidy/identity/network parameters and
descriptor-wallet-only policy remain unchanged. D01-D08 remain OPEN,
all 21 mainnet gates unchecked, mainnet **NO-GO**.

## 2. Observed/inferred/unestablished ledger

| Item | Established evidence | Boundary |
| --- | --- | --- |
| Original run-001 | MSVC linking produced an executable/IR/assembly and a private VCTIP telemetry queue. | The executable was not approved or measured. |
| Original queue | Records identify VCTIP 14.38.33133.0, collection and failed noncached configuration-download records. | Neither outbound packets nor zero traffic are established. |
| Original hold | Compiler-stage artifacts persisted; an external stop ended the controller with -1. | A lingering VCTIP job member is an inference; complete final resource totals are unavailable. |
| Corrected run-002 | Exact image refusal rejected Windows System32 conhost.exe; supervisor exited 2. | Normal Windows filename/location is not proof of exclusive ownership or harmlessness. |
| Corrected cleanup | Compiler root exit 90, nested active 0, cleanup_errors empty; final parent active 1. | Parent active 1 was the controller before its normal exit, not independent postexit accounting. |
| Corrected work boundary | Seven diagnostic JSON files, no generated binary/IR/assembly, oracle fixtures or measured receipts. | LLD execution and conhost creation provenance are not established. |
| Corrected controls | Aggregate job cap/membership read back; final job commit peak 14,356,480 bytes. | Prior controller startup is separately observed; no retroactive enforcement claim. |
| Corrected observations | Last wall 0.454s; raw job CPU 2.484375 core-seconds; conservative startup-plus-job 4.875s; output 31,389 bytes. | These are stopped-preparation observations, not a performance PASS; startup may overlap CPU totals. |
| Corrected polling | Requested 10ms; observed maximum gap 0.344s retained. | A requested interval is not a hard scheduling/deadline guarantee. |

Original run ID: `ef074dc5fafe28325de73c73cd949c667f5087f5054081b56492e13a55923de2`.
Corrected run ID: `2bdd25e214b3a86d75828441b64c7bc1a45d289115d8123ec1eefb6e1b5f52be`.
Original freeze: 8c2eec566691cffd03fc9cb3d8226c03e7b975f8af576fa8cbd9491740f717d4.
Corrected controller: 7746958258990b8575c24643747e6fc539345e238ae4b1a899222da3fd38cb52.
Corrected activated manifest: 669279a8eea98c3289d6c083005c30fcd63b0b812c48a0c7c5873441c8f5dd2c.
Corrected final receipt: eab04468509fbe43b030689f8b171f7f46a9fb766f5dc529be993f3fc2c82391.
See [first incident](https://github.com/andaluzcoin/andaluzcoin/issues/113#issuecomment-6719088539),
[second incident](https://github.com/andaluzcoin/andaluzcoin/issues/113#issuecomment-6719568545)
and [owner disposition](https://github.com/andaluzcoin/andaluzcoin/issues/113#issuecomment-6719590464).

## 3. Exact mixed-runtime launch trace

The corrected controller supplies _winapi.CreateProcess an absolute executable, quoted arguments,
an explicit environment/cwd, inherit_handles=True and CREATE_SUSPENDED | CREATE_NO_WINDOW.
STARTUPINFO requests redirected stdin/stdout/stderr and SW_HIDE.
Its handle_list contains only the NUL input and the two owned output-pipe write handles.
Job/completion/process handles are not deliberately made inheritable.
The child inherits the already established aggregate job; nested assignment/readback precedes ResumeThread.
CREATE_SUSPENDED describes the child's primary thread, not a promise about every OS helper.

[Pinned CPython 3.9.0 Modules/_winapi.c](https://github.com/python/cpython/blob/v3.9.0/Modules/_winapi.c#L972-L1023) reads handle_list and constructs
PROC_THREAD_ATTRIBUTE_HANDLE_LIST; [lines 1129-1139](https://github.com/python/cpython/blob/v3.9.0/Modules/_winapi.c#L1129-L1139) calls CreateProcessW with the supplied mask
OR EXTENDED_STARTUPINFO_PRESENT OR CREATE_UNICODE_ENVIRONMENT.
It passes the caller's inheritance Boolean and copied standard-handle fields.
It does not silently replace CREATE_NO_WINDOW with DETACHED_PROCESS.
This pinned wrapper supplies only handle_list attributes; inventing a job-list dictionary key is not atomic job assignment.
Any creation-time job-list extension would require separately reviewed native plumbing and explicit scope.
The local controller bypasses Popen._execute_child, so Popen-only filtering/validation is not assumed.
[CPython 3.9.0 Lib/subprocess.py](https://github.com/python/cpython/blob/v3.9.0/Lib/subprocess.py#L1377-L1401) explains why a nonempty handle list uses
handle inheritance while restricting inheritance to listed handles.
This restriction controls handles; console association is a separate Windows property.

[Rust 1.74.1 compiler back/command.rs](https://github.com/rust-lang/rust/blob/1.74.1/compiler/rustc_codegen_ssa/src/back/command.rs#L93-L112) constructs std::process::Command for LLD,
adds "-flavor link", arguments and environment, but supplies no Windows creation_flags.
Its [std sys/windows/process.rs](https://github.com/rust-lang/rust/blob/1.74.1/library/std/src/sys/windows/process.rs#L192-L202) initializes flags=0 and detach=false.
The spawn implementation uses self.flags | CREATE_UNICODE_ENVIRONMENT and its own standard-handle setup.
Thus the controller's creation-mask bits are not automatically applied at Rustc -> LLD.
A root DETACHED_PROCESS change would not prove the entire delegated native chain console-free.
Rust 1.74.1's explicit linker path/flavor selects Rust LLD; it does not wrap every descendant launch.

[Microsoft process-creation flags](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags) distinguish a windowless console application from a detached process.
CREATE_NO_WINDOW is ignored when combined with DETACHED_PROCESS or CREATE_NEW_CONSOLE.
DETACHED_PROCESS avoids inherited console association; a process can still call AllocConsole later.
No cited contract promises zero console-host processes or zero network traffic for either mask.
The two incidents therefore support replacing an assumed process model, not merely changing a flag.

## 4. Preferred model and bounded alternative

Preferred direct-launch design: one contained broker owns each application launch
in the direct case. The separately declared delegated case below is an explicit
exception requiring fresh review; it does not inherit the direct-case guarantee.
Every broker-created application starts suspended with DETACHED_PROCESS, explicit Unicode environment,
explicit absolute cwd/image, explicit pipe/NUL standard handles and a minimal inherited handle list.
The CPython wrapper's added EXTENDED_STARTUPINFO_PRESENT/CREATE_UNICODE_ENVIRONMENT remain recorded.
For this proposed direct recipe, the requested creation mask is 0x0000000c
(CREATE_SUSPENDED | DETACHED_PROCESS); this wrapper makes the effective mask
0x0008040c. CREATE_NO_WINDOW, CREATE_NEW_CONSOLE and breakaway bits are absent.
STARTUPINFO uses STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW and SW_HIDE;
all other fields are zero except the required size and exact owned std handles.
This is a proposed diagnostic recipe, not an adopted fix or a runtime result.
No shell, PATH-selected executable, parent console handle, console attachment or breakaway flag is used.
Before ResumeThread, verify aggregate/nested membership, queried limits and exact process image.
After verified membership, bind each observed PID to an open handle, creation FILETIME and image path.
A PID alone, parent PID alone or matching image basename is insufficient identity.
Verify disk hashes of compiler/runtime/probe dependencies before their approved phase.
Console/window handles and process handles retain their different meanings in receipts.

All observers, brokers, diagnostic clients and admitted helpers must be charged to the aggregate model.
Preserve observed startup/private/commit/WS definitions and hard-after-establishment coverage separately.
No uncharged external watchdog, shared console host or OS helper may be silently omitted.
[Ordinary implicit children inherit the no-breakaway job chain](https://learn.microsoft.com/en-us/windows/win32/procthread/nested-jobs); parent job accounting aggregates children.
That rule alone does not identify or account every OS console broker/helper.
Before enabling termination, document the exclusive workload ownership and cleanup boundary.
An unexplained or unchargeable component blocks readiness; its name is not added to an allowlist.
Preserve stop evidence, bounded queued output, exited counters and cleanup uncertainty.

Bounded alternative: model a normal-running delegated launch as an explicitly
different diagnostic case. Its child starts normally in the inherited job.
The proposed Python-only surrogate uses _winapi.CreateProcess with requested
mask 0, hence effective 0x00080400 under the pinned CPython wrapper, an exact
three-handle list and explicit std handles. It is neither suspended nor detached.
Actual Rust starts from a different wrapper/stdio implementation; its default
mask is CREATE_UNICODE_ENVIRONMENT, with EXTENDED_STARTUPINFO_PRESENT only
when process-thread attributes are supplied. The surrogate deliberately differs.
This is not the broker's suspended-before-resume guarantee and requires explicit separate scope approval.
A Python reproduction must state every departure from Rust's actual STARTUPINFO/handle behavior.
It cannot be relabelled an exact Rust compiler test.
Actual Rustc -> LLD remains unqualified until its complete frozen command/dependency/process recipe is reviewed.
Controller-mediated object generation and separate linking is another design option, not an existing recipe:
it requires a fully derived/frozen link command, not guessed CRT/rlib arguments or a hidden bootstrap compile.

## 5. Future topology-only diagnostic protocol: proposal, not permission

The minimum pilot uses reviewed standard-library-only control probes with pinned Python -I -S -B.
It avoids compiler bootstrap, M01 source import, oracle generation, payload loops and throughput sampling.
The probe emits bounded control records, performs no network/filesystem workload and never attaches a console.
Its allowed control APIs, exact source hashes and all expected record fields must be reviewed before approval.
GetConsoleWindow/GetConsoleProcessList/GetStdHandle/GetFileType would themselves be NEW controlled API trials.
No such call is permitted now merely to fill an unknown in this dossier.
The exact literal quota vector, output allocations, deadlines and allowed process graph remain approval inputs.
Historic M01 ceilings are a reference option, not newly adopted diagnostic or operator budgets.
If a complete bounded ownership/graph contract cannot be frozen, the pilot remains BLOCKED without launching.

Freeze exactly two nonadaptive cases, each once, serially, in one new permanent attempt directory:

- L0: the broker creates one receipt-only leaf with the preferred suspended/detached/explicit-handle recipe.
- L1: the same broker creates one reviewed root, which makes exactly one receipt-only child
  using the separately declared Python-only normal-running surrogate recipe.

The direct and delegated recipes are fixed above; absolute paths, dependency
hashes, source/receipt grammar and numeric quota vector still require the
complete future packet. Until supplied, eligibility is **BLOCKED**, not ready to run.

| Case | Expected application roles including the one broker | Expected application lifetimes |
| --- | --- | --- |
| L0 | broker + one leaf, at most two live | one leaf launch |
| L1 | same broker + one root + one child, at most three live | one root and one child launch |

Cases are serial, so there are three nonbroker application lifetimes total.
These are logical role expectations, not a newly adopted process-limit setting.
No console host/helper is implicitly exempted or admitted; an additional role
stops the attempt. Local case/run IDs are not production P, CFG1, T, K or Q.
Each receipt-only process follows a bounded ready/acknowledge/terminal protocol.
It reports startup identity/stdio/console observations, then remains alive within
a frozen deadline until the broker confirms its OS handle/creation-time/image
and job membership and acknowledges release. L1 root is acknowledged before
its one delegated spawn; its child uses the same identity/release barrier.
Missing or late acknowledgments stop the attempt with partial evidence.
This cooperation keeps known clients observable; it does not explain or exempt
any short-lived helper, nor prove a delegated client was suspended before startup.
One terminal record follows release; waits, records and cleanup stay charged.
L1 requires an explicit approval exception for that inherited-contained, unsuspended descendant.
No AllocConsole, AttachConsole, FreeConsole, pseudoconsole creation, shell or additional application spawn is allowed.
Neither case is a rerun of run-001/run-002; no old marker, source freeze or compiled artifact is reused.
An unexpected process, ownership ambiguity or quota/control failure stops the attempt before the next case.
A no-window comparison would be an additional diagnostic requiring an explicitly amended frozen scope.

Before the single approved invocation, freeze probe/controller sources, interpreter/dependencies,
API/handle/console recipes, exact allowed topology and quotas, observation coverage and reviewer provenance.
Bind new approval to those immutable inputs, the prior incidents and a new attempt identity.
A general "proceed", elapsed time or old comment cannot satisfy that gate.
The future implementation must establish/read back containment before clients
and save an immutable controls snapshot. It has not been implemented or qualified.
The controller must remain charged while alive; no parent/child job CPU totals
are added together, because parent counters already include nested jobs.
Charge startup separately with stated overlap/conservative treatment.
Each case records full application_name/command_line, effective flag mask, startup flags and inherited handles.
Record child-side std-handle types and console API returns with API errors/definitions.
Do not infer server ownership from a NULL/non-NULL console HWND or screen visibility.
[GetConsoleProcessList](https://learn.microsoft.com/en-us/windows/console/getconsoleprocesslist) lists attached clients, not a documented complete console-server inventory.
[Pseudoconsole GetConsoleWindow results](https://learn.microsoft.com/en-us/windows/console/getconsolewindow) need not represent a locally visible window.
Collect contained process identities, association/creation observations and exited-job totals separately.
Classify missing short-lived observations and unresolved OS attribution explicitly; do not manufacture a graph.
[TotalProcesses](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_accounting_information) is not a complete successful-admission/image history: Microsoft also counts some failed
associations when limits are exceeded; ActiveProcesses can include processes pending termination/reference release.
Reconcile attempted/failed admissions, lifetime identities, exits and limit events with queried counters.
An unresolved short-lived PID, admission discrepancy or missing identity blocks topology qualification.
Exact count equality plus sampled image membership cannot prove a closed process/image history.
Record raw job user/kernel CPU, job commit, sampled private/WS, logical scratch and cumulative output.
[Aggregate JOB_OBJECT_LIMIT_JOB_MEMORY](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information) is an enforced commit cap after
establishment. CPU/wall/scratch scans are monitored stops; output is a
cumulative prewrite-mediated cap. None is inferred from another metric.
The literal vector, controller/child/startup/cleanup scope, output allocations
and diagnostic maximum runtime remain unselected until the packet is reviewed.
Keep output prewrite reservations, checkpoint rewrite charges, stop requests and terminal-receipt reserve.
Record actual poll/scan gaps and stop/cleanup overshoot; never describe polled limits as hard ceilings.
Check graceful exit plus zero active descendants, drain bounded pipes, then preserve final queried counters.
Document the last observation boundary and any unobserved final observer/self-exit tail.
[Completion-port messages](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects#job-limits-and-notifications) supplement queries; ordinary notification delivery is not guaranteed.
Never infer no quota event, no process or no network activity solely from absent messages/files.
The frozen receipt must record one outcome with its exact case and coverage:

| Outcome | Required disposition |
| --- | --- |
| BLOCKED | Before the first diagnostic client: missing packet, approval, required metadata or established control; no launch to fill the gap. |
| STOPPED | Once a diagnostic launch is attempted, including failed/rejected admission: unexpected role, identity/ownership/accounting discrepancy, missing record/acknowledgment, failed fixed check or stopping condition; preserve partial records and do not continue or repeat. |
| PASS for this topology scope | Both L0 and L1 complete and independently reconcile to the exact approved packet, role/lifetime records, controls and network-assurance evidence. One successful case alone is not a pilot PASS. |

A topology PASS covers only the declared recipe/host and observed client-lifetime
window. The last controller snapshot cannot establish its subsequent self-exit
tail. If a whole-family lifetime or cleanup bound needs evidence beyond that
window, it remains unqualified until the approved packet independently observes
or conservatively justifies it. No silent external uncharged monitor is allowed.
A topology PASS cannot upgrade an unobserved tail to a resource guarantee.

The future pilot also needs a concrete reviewed network-assurance/evidence implementation before approval.
Job, image and console controls are not network isolation; neither absent packet observations nor
source-level absence of networking calls proves universal zero application traffic, especially after VCTIP.
Do not weaken the charter's zero application traffic requirement to "no deliberate networking".
WFP/firewall rules, VM/container isolation, new privileges, installations and host policy changes are NOT
authorized by this design or old M01 decisions; any need for them requires its own concrete scoped decision.
If the zero-application-traffic scope cannot be established within the reviewed existing boundary, BLOCKED.

## 6. Stop gates, assurance limits and later separation

A source-only review may clear a recipe; it cannot clear unobserved runtime behavior.
A topology pilot PASS would cover its exact Python/control recipe and host only.
It would not establish actual Rust compiler/linker behavior, a native allocator envelope or M01 correctness.
A later separately scoped empty-crate Rustc/Rust LLD preparation must reconcile the real descendant graph.
Only after that control qualification may a NEW complete M01 proposal be reviewed and authorized.
Its sources, binaries/generated code, independent expected fixtures and quotas still need the two freezes.
Clock/review wait, failures and cleanup remain charged; no automatic repeat, higher limit or waiver follows.
No deliberate OOM/quota pressure, global registry/privacy/firewall change, privilege change or download is proposed.
This design does not create run-003, modify old programs/freezes or grant a
compiler/linker/version/capability probe. An executed qualification would need
its own new immutable attempt, independent controls/source review and critical approval.
Required unknown metadata or incomplete ownership/accounting produces BLOCKED, not a presumption of zero.
The present milestone can finish with this contract and open gates; measurements and mainnet stay HOLD/NO-GO.

## 7. Resource decisions, independence and qualification handoff

This handoff prepares decisions; it selects no operator target or new experiment.
The source baseline is M `03be3d29466ba509de94abbd7e212ffe1fa94f3b`.
The [completed v0.2.89 record](https://github.com/andaluzcoin/andaluzcoin/issues/113#issuecomment-6721769262)
preserves both stopped preparations and confirms that their allowances are consumed.
The [owner disposition](https://github.com/andaluzcoin/andaluzcoin/issues/113#issuecomment-6719590464)
keeps measurements HOLD. A controls design, ordinary CI or elapsed time supplies no retry approval.

### Operator decision card

Complete this card for one named intended operating environment, not an inferred desktop minimum.
Each row needs a proposed value, units, accountable owner, status and immutable evidence reference.
Record the observation horizon, simultaneous workload, uncertainty, omissions and pass/fail rule.
Every value below remains **TO BE DECIDED**; unknown means neither zero nor unlimited.
Observed laboratory inventory and prior campaign ceilings are not operator acceptance budgets.
This follows the [resource-input requirements at M](https://github.com/andaluzcoin/andaluzcoin/blob/03be3d29466ba509de94abbd7e212ffe1fa94f3b/doc/andaluzcoin-auxpow-b-measurement-charter.md#L74-L90).

| Decision to fill | Required units and coverage |
| --- | --- |
| Supported platform and baseline | OS/build, architecture, compiler/ABI, allocator, CPU/SHA implementation path, RAM, storage/filesystem, simultaneous node workloads and baseline peak. |
| Whole-node and residual temporary memory | Separate allocated capacity, committed bytes, private bytes and working-set objectives; exact residual session allowance after disjoint ordinary pools. |
| CPU and burst service | User+kernel core-seconds per interval, burst allowance, concurrency, operation boundary and termination/cleanup accounting. |
| Network | Separate application/transport ingress and egress bytes per interval, burst allowance, request/response/retry overhead and minimum honest delivery assumptions. |
| Permanent resources | Separate canonical bytes, physical allocation/writes, inodes, index RAM, journals/logs and orphan/repair retention; absolute headroom and horizon. |
| Growth reference and excess allowance | Honest route/proof-size reference, reference rate and permitted excess in each resource per time; distinguish expectation from hard total capacity. |
| Honest progress and waiting | Bounded admitted-peer/domain assumptions, selection/preemption/resume rules, minimum honest share, response/drain/cancel bounds and completion objective. |
| Threshold and supported histories | Trusted anchor/evidence closure, height/work, CFG1/T provenance, route/profile histories, clock and nonwrapping claim domain, bypass/restart/repair cases. |
| Adversary cost and capacity | Eligible adaptive strategies, aggregate capacity and uniform mandatory per-attempt lower cost in identical units; include replay and abandonment. |

### Charging and support-domain rules

Assign every physical input/arena owner to exactly one memory bucket; charge its full pinned capacity.
Charge independent copies, handles, descriptors, receipts, threads/stacks, scratch and writer overlap separately.
Distinguish pending/active jobs from already-screened retained owners without creating a class exemption.
A whole Q-sized release must keep every owner charged until ordered drain/durability releases it.
Temporary occupancy, cumulative accepted archive growth and repeated CPU service are different budgets.
Keep filesystem/index/body/undo and same-Hc FIRST/repair/orphan costs separate from divergent-header leakage.
No count objective or canonical-byte product establishes physical storage, native RAM or CPU cost.
The [joint reservation and service requirements](https://github.com/andaluzcoin/andaluzcoin/blob/03be3d29466ba509de94abbd7e212ffe1fa94f3b/doc/andaluzcoin-auxpow-b-security-cost-eligibility.md#L186-L227)
remain necessary even if a future launch-control experiment succeeds.

Freeze a supported history/domain before relating T to record count or attacker effort.
Reusable proof-generation work is not a fresh attempt cost unless its necessity is established.
An empirical defender throughput result is not a universal attacker lower bound.
Use a joint eligible strategy model or justify every factor of a conservative envelope.
One global owner and safe refusal do not establish anti-starvation, anti-Sybil or no-eclipse service.
Claims outside the supported domain remain explicitly unsupported; do not silently replace native work arithmetic.

### Evidence responsibilities

Assign the following roles before the corresponding future work; this table assigns no people or authority.
Each artifact needs immutable source/input/platform identity, method, scope, omissions and reviewer disposition.

| Responsibility | Required separation and evidence |
| --- | --- |
| Operator/decision owner | Select the target environment, budget bundle and support domain; a preference is a policy input, not measurement or security evidence. |
| Controls designer | Specify launch roles, containment, hard limits versus monitored stops, accounting and failure records; preserved incidents are observations, not capability certification. |
| Implementation author | Implement only the separately authorized frozen component; identify actual runtime/allocator/layout and all resource owners. |
| Fixture/oracle author | Derive expected bytes, verdicts and counts independently of implementation outputs; disclose shared helpers and provide actual proof/context provenance when that scope requires it. |
| Artifact/control reviewer | Independently check sources, inputs, binaries, manifests, containment/accounting boundaries and stop conditions before the authorized execution gate. |
| Security/service reviewer | Review strategy/domain costs, adaptive/restart/bypass coverage, durability and honest-service claims under their own scopes. |

Separate assisted authorship and cross-runtime agreement do not establish independent B1 implementations or an external organizational audit.
Synthetic Rust/System byte operations cannot establish the node's C++ allocation envelope or actual proof/context cost.
Neither stopped preparation reached fixtures, an approved executable freeze or measured worker cases.
These distinctions follow the [charter's evidence boundary](https://github.com/andaluzcoin/andaluzcoin/blob/03be3d29466ba509de94abbd7e212ffe1fa94f3b/doc/andaluzcoin-auxpow-b-measurement-charter.md#L219-L246).

### Gates carried into the next decision

| Gate | Evidence still required; a controls dossier closes none of these gates |
| --- | --- |
| F2 native envelope | Matching node C++ platform/layout/allocator and allocated-capacity maxima; all input/job/K/Q/receipt/scratch/writer overlap, failure ownership, release and durability paths. |
| F3 security/cost | Selected objectives/domain plus eligible uniform costs and independent actual evidence; jointly qualify p/ell/reservations and the separate permanent/service categories. |
| F4 executable evidence | Fresh scoped authorization and complete applicable experiment freeze; corresponding B1 verification/sync/integration still requires the complete production semantic freeze. Consumed M01 allowances cannot be reused. |
| F5 operational service | Reviewed scheduling/long-session/fairness assumptions and corresponding operational evidence. Storage/repair/compatibility and C8 deployment holds remain separate; no deployment or launch approval follows from research CI. |

The [F2-F5 requirements at M](https://github.com/andaluzcoin/andaluzcoin/blob/03be3d29466ba509de94abbd7e212ffe1fa94f3b/doc/andaluzcoin-auxpow-b-presync-design.md#L449-L455)
and [C1-C8 register](https://github.com/andaluzcoin/andaluzcoin/blob/03be3d29466ba509de94abbd7e212ffe1fa94f3b/doc/andaluzcoin-auxpow-b-security-cost-eligibility.md#L314-L323) remain the handoff contract.
C1's one-fixed-profile drafting direction is recorded; do not ask that same direction question again.
C2 still needs the card above. C3 preserves modular work and distinct entry/phase predicates.
C4-C7 still need exact receipt lifetimes, typed owners/jobs, batch/failure ordering, generation/ancestry protection, durable FIRST, historical credit and eligibility restoration.
C8 still needs coherent corrected views/genesis/terminal semantics; official mapping, compatibility, migration and deployment stay HOLD.

### What can be asked only after the concrete plan exists

First publish/review one exact preferred launch/console/containment design and its finite diagnostic protocol.
Pin purpose, calls, tool/source identities, permitted process roles/counts, inputs, hard/monitored controls, receipts, cleanup and refusal outcomes.
State explicitly which question that diagnostic can answer, what remains unknown and which later executable gates it cannot unlock.
Then request a fresh decision on that exact immutable scope: approve one bounded attempt, retain HOLD, or revise a named choice.
Approval must bind the reviewed revision, controls, limits and attempt identity; no probe, allowlist widening or new run is implied while waiting.
Actual operator-budget adoption remains a separate decision after its concrete card and consequences are reviewable.
All D01-D08 remain OPEN, all 21 mainnet gates unchecked and mainnet NO-GO; consensus/identity/network/descriptor-only invariants remain unchanged.

## 8. Primary source register

- [CPython 3.9.0 _winapi.c](https://github.com/python/cpython/blob/v3.9.0/Modules/_winapi.c): blob e1672c478522e874e4560fed10828a8b4a4212db.
- [CPython 3.9.0 subprocess.py](https://github.com/python/cpython/blob/v3.9.0/Lib/subprocess.py): blob 13600c28cf71170b216ab5df055aa1402df60b32.
- [Rust 1.74.1 linker launcher](https://github.com/rust-lang/rust/blob/1.74.1/compiler/rustc_codegen_ssa/src/back/command.rs).
- [Rust 1.74.1 Windows process implementation](https://github.com/rust-lang/rust/blob/1.74.1/library/std/src/sys/windows/process.rs): blob cd5bf7f1538cad7c8fe00a45f58785155b3c1d0f.
- [Rust 1.74.1 linker/flavor selection](https://github.com/rust-lang/rust/blob/1.74.1/src/doc/rustc/src/codegen-options/index.md).
- [Microsoft process creation flags](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags).
- [Microsoft console creation](https://learn.microsoft.com/en-us/windows/console/creation-of-a-console) and [console handles](https://learn.microsoft.com/en-us/windows/console/console-handles).
- [Microsoft nested jobs](https://learn.microsoft.com/en-us/windows/win32/procthread/nested-jobs) and [completion-port guarantees/limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_associate_completion_port).
- [Microsoft basic job accounting](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_accounting_information): admission/active-counter definitions, not a complete process-image ledger.
- [Microsoft console-client list](https://learn.microsoft.com/en-us/windows/console/getconsoleprocesslist) and [console HWND/pseudoconsole semantics](https://learn.microsoft.com/en-us/windows/console/getconsolewindow).
- [Microsoft job memory limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information).
- [Microsoft handle-list attribute](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute) and [STARTUPINFO](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/ns-processthreadsapi-startupinfow).

## Diagnostic packet continuation

See [the proposed evidence-packet and readiness specification](andaluzcoin-auxpow-b-diagnostic-packet.md); diagnostic execution remains BLOCKED and measurements HOLD.
