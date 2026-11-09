# Candidate topology evidence expectations

This is the independent static expectation derivation for the v0.2.92 packet candidate. It describes future record acceptance, with synthetic inputs and outcomes for source review. PIDs, birth times, counter values, observations, runtime artifacts and execution receipts remain absent. The diagnostic is BLOCKED and measurements are HOLD. The operator environment and budgets are UNSELECTED. Mainnet is NO-GO.

## Review inputs and sequence conventions

The v0.2.91 event vocabulary, common envelope and outcome rules are pinned at the completed research merge. The laboratory candidate supplies resource and encoding ceilings. Review of the final controls, source and receipt schema must reconcile this derivation with the same immutable packet. [v0.2.91 event rules](https://github.com/andaluzcoin/andaluzcoin/blob/1e40b1507ab2ffbd03a2d47d89bf009b9edd07a0/doc/andaluzcoin-auxpow-b-diagnostic-packet.md#L106-L214) · [Candidate lab quotas](quotas.json)

- The broker is the sole durable event sequencer. It binds the packet, detached approval and fresh attempt identity. Each record declares its attempt or case scope. Every required earlier event reference names the expected prior sequence, case, role and lifetime. A later record can describe earlier transport arrival with its own observation provenance.
- The proposed transport uses local named-pipe endpoints in exactly three inherited standard handle slots. Commands and acknowledgments go to stdin, bounded assertions arrive on stdout, and stderr is retained only as capped failure data. A transport message carries a role/launch binding. Its process identity requires independent verification through an owned handle.
- Canonical frames on the pipes have the fixed four-byte little-endian length prefix from the controls candidate. The prefix is counted in the writer allocation. The durable event file has canonical payloads and a charged LF framing byte. The packet must bind schemas and frame limits before trusted decoding.
- The two case jobs are exclusive. The aggregate includes the broker and associated cases. Validate the permitted creator, owned case job and aggregate membership, exact image identity, PID and creation FILETIME. The nonreused generation joins these checks to an attempt lifetime. Preserve actor and observer provenance separately.
- The sequences below specify mandatory causal constraints. Repeated accounting, evidence and owned-handle closure records need distinct sequences and bounded capacity. The source and receipt review must demonstrate that the complete scheduled record and ownership inventory fits the quotas, including transport copies and terminal work.

## Admission and successful record pattern

Before reservation, a missing or invalid required input produces a source-shaped `PREFLIGHT_REFUSAL` with explicit input states and `no_attempt_reserved=true`. It has no invented packet/approval/attempt digest. All nine mandatory categories must reconcile before execution. After real independent review and actual detached approval of one attempt, `PACKET_CHECK` would bind the new reservation. `CONTROL_SNAPSHOT` would establish the relevant jobs, caps, ownership, transport, clock and coverage before the first committed creation call.

### L0 direct leaf

| Ordered constraint | Evidence required at review |
| --- | --- |
| `LAUNCH_INTENT` → `LAUNCH_AUTHORIZED` → `LAUNCH_ATTEMPT` | The broker records the exact direct leaf image, command, cwd, environment, role, startup flags and owned standard handle recipe. Authorization and the call-boundary commitment are durable before the call. |
| `LAUNCH_RESULT` → `PRE_RESUME_BOUND` → `RESUME_RESULT` | One created result binds the held process/thread handles. Read back the exact suspended process identity, aggregate and case membership and controls before resume. The resume result records the actual API evidence. |
| `RESUME_RESULT` → transport `BOOT` → `CLIENT_READY` → `IDENTITY_BOUND` → `RELEASE_ACK` | Send the exact BOOT frame only after recording the resume result. Bind the subsequent client assertion to a fresh query of the same owned process, birth, image and job memberships. Bind the ACK to the READY and identity sequences and allow one consumption. |
| `CLIENT_TERMINAL` → `PROCESS_EXIT` → `HANDLE_CLOSE` → case reconciliation | Retain the terminal outcome and separately verify process exit. Complete the owned close ledger and reconcile active lifetime and case job accounting. L1 can begin only after L0 reconciliation. |

The requested direct mask is `12` and its effective pinned-wrapper mask is `525324` in receipt decimal strings. These correspond to `0x0000000c` and `0x0008040c` in the launch specification. Both direct clients require suspended readback before resume. [Pinned direct and delegated recipe](https://github.com/andaluzcoin/andaluzcoin/blob/63e92f435bf236848a083f9b98114f13a6603581/doc/andaluzcoin-auxpow-b-preparation-controls.md#L87-L127)

### L1 direct root and one delegated child

| Ordered constraint | Evidence required at review |
| --- | --- |
| Direct L1 root launch through `RELEASE_ACK` | Repeat the direct sequence with a distinct launch and generation in the L1 case job. The root READY is corroborated and acknowledged before it requests child creation. |
| Delegated `LAUNCH_INTENT` → `LAUNCH_AUTHORIZED` | The root proposes its sole child under its existing authenticated transport binding. The broker durably records the exact declared intent and then authorization before the first authorization frame. |
| Transport `LAUNCH_ENTER` → durable `LAUNCH_ATTEMPT` → call permit → actual call | An enter message binds the prior authorization. The broker commits the one attempt record before issuing the exact permit. ENTER and permit are transport facts tied to these records. The creator's subsequent call is the only delegated creation entry permitted. |
| Delegated `LAUNCH_RESULT` → transport child `BOOT` → child `CLIENT_READY` → `IDENTITY_BOUND` → `RELEASE_ACK` | Preserve creator-side result, actual attempted/admission status and source provenance. Duplicate the held child process handle from the bound root and corroborate birth/image/memberships before sending BOOT. A compliant child waits for BOOT before emitting READY. Require a fresh corroboration of the held identity after READY and before ACK. |
| Child `CLIENT_TERMINAL` → `PROCESS_EXIT` → `HANDLE_CLOSE` → child reconciliation | The child exits under observation, required handle and pipe evidence reconciles, and the root remains alive through this barrier. Send the exact child-reconciled grant to the root after reconciliation. |
| Child-reconciled grant → root `CLIENT_TERMINAL` → `PROCESS_EXIT` → `HANDLE_CLOSE` → L1 reconciliation | Root terminal binds the child-reconciled grant. Verify root exit and all close obligations, then reconcile case accounting and active descendants. |

The delegated child has requested mask `0` and effective mask `525312`, corresponding to `0x00080400`. Its normal startup requires explicit approval for the inherited containment and unsuspended launch exception. There is no suspended-before-resume evidence for the child. L0 has two application roles including the broker. L1 has three, with the same broker. There are three successful nonbroker lifetimes in a complete successful pattern. These are logical expectations. Native association and active/total counter values need independent reconciliation, especially when admission fails or termination references persist. Console-handle and attached-client outcomes are future API evidence with explicit validity and error state. [v0.2.91 role and identity rules](https://github.com/andaluzcoin/andaluzcoin/blob/1e40b1507ab2ffbd03a2d47d89bf009b9edd07a0/doc/andaluzcoin-auxpow-b-diagnostic-packet.md#L78-L149)

### Whole attempt and postterminal evidence

Both cases must reconcile. `ACCOUNTING_SNAPSHOT` binds the last completed-write cuts, aggregate job counters and distinct nested counters. Preserve the identity, observation and admission ledgers. `COVERAGE_END` names the last observer/time/metric scope and any unresolved tail. The one `ATTEMPT_TERMINAL` binds the immediately prior event digest and completed immutable artifacts. The complete event file digest belongs in a detached, bounded inventory. Its write and subsequent resource/network obligations still count. Approval and final packet review artifacts likewise remain detached from the manifest they name.

The successful case sequence is necessary for `PASS_FOR_DECLARED_TOPOLOGY`. Evidence for the actual supported host, independently verified whole required network coverage, required quota/control readbacks, output accounting and reconciled observation limitations is also necessary. A broker's final record cannot directly observe its own exit. A declared topology window and persistent network coverage are separate claims.

## Synthetic refusal and stop cases

These cases are review vectors with required dispositions. They contain no actual receipt or recorded runtime result.

| ID | Input or causal fault | Expected disposition and preserved evidence |
| --- | --- | --- |
| R01 | Missing artifact, actual detached approval or L1 exception. Another release's successful CI and an owner instruction to prepare the packet are present. | BLOCKED before reservation. Name missing evidence/approval. CI and preparation authorization cannot fill either row. |
| R02 | Manifest includes its own digest or the future review/approval digest. A digest, frozen byte length or review identity differs. | BLOCKED before reservation. Name the mismatched artifact or cyclic edge. |
| R03 | Exact host identity, runtime closure, effective network boundary or required control capability has no evidence. | BLOCKED. Preserve explicit missing/unknown state, with no topology/API trial to fill the gap. |
| R04 | `LAUNCH_INTENT` and `LAUNCH_AUTHORIZED` exist, no committed call or prior case attempt exists, and evidence establishes that no call occurred. | BLOCKED is eligible. Preserve the aborted intent and proof boundary without inventing a result or treating an authorization as a call. |
| R05 | First call-boundary record is durable and the permit/actual call entry becomes uncertain. | STOPPED. Retain known commitment and UNKNOWN entry evidence. No next case or second call. |
| R06 | `CreateProcess` fails, admission is rejected, or a created suspended client has a mismatched handle/image/job binding. | STOPPED. Preserve attempted creation and available API result/admission evidence. A mismatched direct client is never resumed. |
| R07 | A direct client's resume precedes readback, or a delegated child is labeled suspended to fit the direct pattern. | STOPPED. Exclude PASS from reordered or fabricated evidence. |
| R08 | ACK names stale READY, wrong case, prior generation, wrong birth time or a previously used release. | STOPPED. Preserve the mismatched binding. No client proceeds using that ACK. |
| R09 | Root tries to create before both durable approvals, makes a second create call or begins L1 before L0 reconciliation. | STOPPED after first commitment or attempted launch. Preserve the actual call/intent boundary. No later valid record repairs the order. |
| R10 | Direct or delegated child emits READY before its bound BOOT. The root later supplies a matching creator result. | STOPPED. Preserve the early assertion within its bounded failure reservation. A later valid creator result cannot repair the sequencing failure. |
| R11 | A correctly bound frame arrives in partial I/O results and reassembles within its exact length, byte reservation and stage deadline. | Eligible to continue. Preserve arrival provenance. Commit trusted identity/release records only after corroboration. |
| R12 | Unknown helper appears, including a console host arising from the exact delegated console-subsystem startup. A PID can also be reused, or counters can match while a short-lived process identity remains unresolved. | STOPPED. No helper exemption follows from matching counts, current images or empty completion messages. The expected three live application roles are insufficient proof of effective OS helper ownership. |
| R13 | Prefix exceeds 4096-byte payload, EOF/deadline truncates a frame, canonical bytes differ, a key repeats, or a required field is UNKNOWN/ERROR. | Refuse trusted decoding or record use. Before the first commitment this is BLOCKED when absence of launch is established. After commitment this is STOPPED. Retain only the allowed bounded failure evidence. |
| R14 | Poll/scan gap exceeds 250 ms, a stage deadline expires, or observed CPU, wall, scratch, memory sample, thread or handle limits fail. | STOPPED after commitment. Preserve observed sample, gap, stop request and cleanup overshoot. Never recast a monitored threshold as a hard cap. |
| R15 | Broker normal/client allocation is exhausted or a partial write would require using terminal reserve for normal output. | STOPPED after commitment. Decline the next normal write, keep its reservation disposition and preserve the valid prefix. Cleanup/failure handling uses only its reserved allocation. |
| R16 | A rewritten checkpoint is treated as an output refund, or terminal accounting includes its own future write or digest. | Reject accounting. STOPPED after commitment. Preserve earlier completed-write cuts and the separate reservation. |
| R17 | Terminal or detached inventory write fails, handle closes without exit proof, or cleanup ends without required tail coverage. | STOPPED with incomplete retained evidence. A short write cannot establish a terminal outcome. No second attempt, terminal rewrite or hidden observer. |
| R18 | A connection is denied, transmitted bytes are absent, or collection produced an empty log, but the attempt violates the frozen call policy or required coverage is unknown. | Preserve denial, observed traffic and attempted operation separately. BLOCKED if required boundary evidence was missing before any commitment. STOPPED if coverage or allowed-call behavior fails after commitment. |
| R19 | L0 succeeds, then L1 admission or later readiness fails. | STOPPED for the whole attempt. Preserve L0's reconciled result and distinct L1 disposition. L0 success cannot qualify the whole attempt. |
| R20 | All three clients return cleanly but a required process/receipt/clock/source relationship cannot reconcile. | STOPPED with preserved evidence. Process exit status is one observation and cannot certify the required relationships. |
| R21 | An alternate executable subsystem, creation mask, helper role or observation component is inserted to bypass the L1 admission blocker. | BLOCKED for any preparation against this manifest. Review a separately amended scope and new artifact digests before considering execution. |

## Review disposition

The tables establish a candidate expected structure and explicit refusal rules. The final independent source, control, artifact and network review must bind exact implemented schemas, paths, source/API/handle inventories, host identities, effective enforcement, output capacity and evidence boundaries. The executable packet, actual receipts and fresh attempt-bound approval are separate required inputs. [v0.2.91 readiness workflow](https://github.com/andaluzcoin/andaluzcoin/blob/1e40b1507ab2ffbd03a2d47d89bf009b9edd07a0/doc/andaluzcoin-auxpow-b-diagnostic-packet.md#L376-L433)
