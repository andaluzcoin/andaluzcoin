# v0.2.92 diagnostic packet review candidate

This candidate advances the L0 and L1 diagnostic from the v0.2.91 requirements to concrete review inputs. The candidate is **BLOCKED**. The execution manifest depends on a selected lab, effective control evidence, and source that matches those controls. [v0.2.91 handoff](https://github.com/andaluzcoin/andaluzcoin/issues/117#issuecomment-6730372055) · [Tracker #119](https://github.com/andaluzcoin/andaluzcoin/issues/119)

| Review input | Artifact |
| --- | --- |
| Proposed launch, IPC, process identity and cleanup contract | [Controls](controls.md) |
| Proposed isolated lab and evidence required for effective network denial | [Network assurance](network.md) |
| Proposed laboratory limits and observation boundaries | [Quota vector](quotas.json) |
| Expected event order and refusal cases | [Review fixtures](expectations.md) |
| Pure receipt encoding and complete pipe framing source | [Receipt codec](receipt_encoding.py) |
| Canonical UTF-8 and digest test vector | [Encoding vector](encoding-vector.json) |
| Static file identity reference from the preparation workstation | [Runtime reference](runtime-reference.json) |
| Bound inventory and outstanding gates | [Review index](review-index.json) |

The question for the eventual diagnostic is whether two specified CPython launch recipes can be admitted, observed, released and reconciled within their declared Windows boundary. The review uses the inherited L0 suspended direct launch and L1 normally started delegated child. The proposed control transport uses local pipes and a durable broker acknowledgement before each creation call.

A dedicated Hyper-V guest is the proposed laboratory route for review. A named guest, its effective isolation policy, its runtime and loader closure, and the evidence custodian are required. An offline adapter configuration covers only part of the network boundary. Loopback, service-mediated actions and host integration paths need explicit coverage through startup and the last observer exit. [Network assurance](network.md)

The existing L1 recipe has a concrete ownership problem. Its console-subsystem child starts with requested flags zero from a detached root. Windows documents console initialization for console applications. The packet needs evidence for ownership, isolation, accounting and cleanup of any console helper involved in that path. Preserve L1 and block until that evidence is supplied or a separately reviewed amendment changes the recipe. [Controls](controls.md) · [Microsoft console initialization](https://learn.microsoft.com/en-us/windows/console/allocconsole)

The proposed limits identify the hard job limits separately from sampled counters and stop policies. Exact live aggregate commit, complete startup and fatal-output coverage, and final observer-tail coverage still need a supported measurement boundary or an explicit, separately reviewed revision of the claim. The hard job commit limit and peak are distinct from current commit. [Quota vector](quotas.json) · [Microsoft job object query classes](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-queryinformationjobobject)

The receipt codec supplies canonical bytes, bounded complete-frame serialization and parsing, and SHA-256 event digest input. The controller still needs the event-specific field schema, causal checks, bounded I/O and the platform controls. The writer must enforce the final journal envelope size, including its digest and line feed, and account for encoding temporaries in its buffer budget.

For review, compare the bytes and SHA-256 digests in the index with the files at the draft commit. The index lists draft artifacts separately from the mandatory execution inputs. A missing row has no digest or byte length. The final execution manifest will bind the selected host, effective controls, source bytes, limits, bounded receipt format and expected evidence. The independent review then binds that manifest's digest in a separate record. Fresh approval must bind both records and a new attempt identity, including the L1 exception. [v0.2.91 manifest rules](https://github.com/andaluzcoin/andaluzcoin/blob/1e40b1507ab2ffbd03a2d47d89bf009b9edd07a0/doc/andaluzcoin-auxpow-b-diagnostic-packet.md#L16-L49)

Mainnet is **NO-GO**. Measurements are **HOLD**. Operator environment and budgets are **UNSELECTED**. Diagnostic execution is **BLOCKED** pending the outstanding evidence, final source and review, and fresh execution approval.
