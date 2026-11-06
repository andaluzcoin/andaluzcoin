# AuxPoW validation boundaries and implementation-readiness research

## 1. Decision, baseline and scope

**v0.2.82 is a documentation-only research checkpoint.**
Public economic mainnet remains **NO-GO**; all 21
[mainnet readiness gates](andaluzcoin-mainnet-readiness.md) remain unchecked.
This dossier does not approve production integration or establish a security audit.

[Issue #99](https://github.com/andaluzcoin/andaluzcoin/issues/99) defines this finite
follow-up. No pre-agreed numbered v0.2.82 scope was found before that tracker.
The frozen ALUZ baseline is **d470a2b166a0e300f88b654564e6177439118ffa**,
tree **5764e09c2351f6dafa04abbb6693a155c650645d**, published as
v0.2.81-auxpow-adversarial-resources-research.

Current ALUZ validates ordinary SHA256d child work and has no attached AuxPoW
proof. No production format, parent chain, chain ID, domain, version bit, height,
budget, strictness or activation policy is selected here. Consensus parameters,
identity/network settings and the descriptor-wallet-only policy are preserved.

This advances unfinished requirements in the
[candidate specification](andaluzcoin-auxpow-candidate-specification.md#14-decision-log-and-independent-acceptance-gates),
[proof/activation study](andaluzcoin-auxpow-proof-serialization-activation.md#10-decision-log-and-production-gates),
[work/recovery study](andaluzcoin-auxpow-work-recovery.md#10-decision-log-and-remaining-production-gates)
and [adversarial study](andaluzcoin-auxpow-adversarial-resources.md#10-remaining-real-integration-gates).
Those studies remain evidence with their original limits, rather than implemented
production proof, activation, replay or operational behavior.

## 2. Audit method and traceability

Immutable source links below all name the frozen baseline. The audit read the
actual function bodies, nearby branches and relevant callers, including duplicate,
genesis, trusted-input, reduced-check and availability paths; signature searches
alone were not treated as validation evidence. Separate agent-assisted source
reviews corroborated header/cache and relay/storage/mining observations.
This is a bounded engineering source audit, not an independent organizational
security review or an exhaustive audit of every call path and historical upgrade.

Evidence labels have deliberately different meanings:

- **CURRENT**: behavior directly observed in the pinned source.
- **CONDITIONAL**: an obligation if an eventual owner-selected design introduces
  auxiliary proof handling; it is not a description of current ALUZ.
- **FUTURE VECTOR**: a required test class, not an implemented or executed test.
- **OWNER GATE**: a choice and acceptance criterion that remain unresolved.

Surface IDs S01-S13 connect the source ledger to future vector IDs V01-V18 and
decision IDs D01-D08. These are document identifiers, not new runtime tests.
Research completion means the dossier is reviewable, not that the owner gates
or any mainnet launch gate have passed.

## 3. Current source surfaces and conditional integration obligations

### S01. Header identity and full-block serialization

**CURRENT:** [CBlockHeader fields/serializer](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/primitives/block.h#L26-L70)
contain six fields totaling 80 bytes. [GetHash](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/primitives/block.cpp#L15-L18)
hashes that header serialization using
[HashWriter's double SHA256](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/hash.h#L100-L144).
[CBlock](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/primitives/block.h#L73-L107) inherits header identity and
serializes the header plus transactions; its identity is not a digest of every
byte of that full serialized payload. Its validation caches are memory-only.

**CONDITIONAL:** Specify child identity, proof binding and every serialized view
before attaching data. An identity that excludes a proof and one that commits to
it have different replacement, circular-commitment and compatibility obligations.
Neither is chosen. Trace V01/V02/V09 to D01/D05.

### S02. Numeric work, expected bits and once-only index credit

**CURRENT:** [PoW functions](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/pow.cpp#L14-L170) implement ordinary
retargeting, numeric target rejection and direct hash comparison.
[ContextualCheckBlockHeader](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/validation.cpp#L4112-L4152) additionally
requires exact expected bits, MTP, future-time and buried full-version checks.
[GetBitsProof](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/chain.cpp#L121-L134) computes target-based work;
it is not itself a mainnet powLimit/context validator.
[AddToBlockIndex](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/node/blockstorage.cpp#L224-L255) deduplicates
by child GetHash, derives height from pprev and adds the child's work once.

**CONDITIONAL:** A future auxiliary work route needs actual proof/hash binding,
the child target and its ancestry-derived expected bits before accepted credit.
Parent difficulty, a lower hash or extra submissions must not silently create
additional credit for one child. Trace V03/V04 to D02/D03/D06.

### S03. Header admission, known entries and minimum-work trust

**CURRENT:** [AcceptBlockHeader/ProcessNewBlockHeaders](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/validation.cpp#L4218-L4290)
accept header objects, not a detached proof payload. A known nonfailed index
returns before fresh header/context/minimum-work checks. A new non-genesis header
takes direct PoW, known/nonfailed parent and contextual checks before insertion;
genesis is a distinct branch. The final min_pow_checked gate concerns anti-DoS
work admission, not permission to skip the preceding new-header PoW check.

**CONDITIONAL:** Define where proof availability and validity are established,
including known-header, genesis and trusted-caller paths. A previous header result
cannot by itself authenticate newly supplied bytes excluded from that identity.
Trace V02/V05/V09 to D01/D04/D05.

### S04. P2P header screening and low-work presync

**CURRENT:** [CheckHeadersPoW](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/net_processing.cpp#L2619-L2633) calls
HasValidProofOfWork and continuity checks.
[ProcessHeadersMessage](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/net_processing.cpp#L2983-L3085) performs
that screening before HeadersSyncState. Known-header/NoBan shortcuts occur later
in anti-DoS work handling; they do not bypass that initial direct PoW screening.
[Presync/redownload](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/headerssync.cpp#L177-L279) use permitted
difficulty transitions, keyed one-bit GetHash commitments and accumulated work.
[CompressedHeader](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/headerssync.h#L20-L54) retains the five
non-prevhash fields and reconstructs a header from a supplied previous hash.

**CONDITIONAL:** Establish proof delivery, verification cost and retention before
work-based admission. Under a proof-excluded identity, a GetHash commitment does
not also commit to separate attachment bytes. Presync is not a full contextual
validator. Trace V05/V06 to D01/D04/D05.

### S05. Full and compact P2P framing and reconstruction

**CURRENT:** [HEADERS decoding](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/net_processing.cpp#L4816-L4839)
checks the header count against the configured result limit before resizing,
then deserializes headers and reads/ignores each transaction count, assuming zero;
this excerpt does not strictly check that count equals zero.
[Full BLOCK handling](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/net_processing.cpp#L4857-L4902) decodes
TX_WITH_WITNESS and applies mutation/work-admission handling before processing.
[Compact serialization](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/blockencodings.h#L104-L130) carries a
CBlockHeader, nonce, short transaction IDs and prefilled transactions.
[Compact admission](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/net_processing.cpp#L4554-L4628) processes the
header before body reconstruction; [FillBlock](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/blockencodings.cpp#L191-L236)
copies that header, reconstructs transactions and checks possible mutation.

**CONDITIONAL:** Specify the representation and availability of proof bytes for
each message/reconstruction route, including partial data and existing-block
shortcuts. A full-block extension does not automatically solve header or compact
relay. Trace V01/V06/V07 to D01/D04/D07.

### S06. Status, data availability and block acceptance shortcuts

**CURRENT:** [BlockStatus](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/chain.h#L42-L85) distinguishes validity
levels from HAVE_DATA/HAVE_UNDO and FAILED_VALID. Value 1 is reserved, formerly
HEADER; there is no active BLOCK_VALID_HEADER stage. TREE, TRANSACTIONS, CHAIN
and SCRIPTS have distinct meanings.
[ReceivedBlockTransactions](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/validation.cpp#L3797-L3821) records
transaction/data information and raises TRANSACTIONS, not full script validity.
[AcceptBlock](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/validation.cpp#L4330-L4411) admits the header, but
can return early for existing data or selected unrequested/pruned/low-work cases.

**CONDITIONAL:** Define whether proof bytes are present, checked and retained at
each stage. Existing data/validity flags do not acquire a new attachment meaning
by inference. Trace V07/V09/V13 to D04/D05/D07.

### S07. Success caches, failure scope and concurrency

**CURRENT:** [CheckBlock](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/validation.cpp#L3950-L4014) returns early
on fChecked and sets that cache only after its PoW and Merkle checks are enabled
and pass. Separate [Merkle/witness caches](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/validation.cpp#L3869-L3935)
cover other checks; fChecked does not certify contextual witness/UTXO/scripts.
[ProcessNewBlock](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/validation.cpp#L4430-L4452) locks cs_main around
CheckBlock because of its mutable cache and prechecks before AcceptBlock to avoid
permanently poisoning a header through a malleated-body failure.
[InvalidBlockFound](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/validation.cpp#L1985-L1993) excludes
BLOCK_MUTATED from permanent FAILED_VALID marking.

**CONDITIONAL:** Classify proof-specific, child-specific, contextual and
availability failures before deciding cache/status scope. Do not infer that all
proof errors should become BLOCK_MUTATED or that all caches should be cleared
on every reorg. These current paths are not a claimed ALUZ exploit.
Trace V08/V09/V10 to D03/D05/D06.

### S08. Connection, reconnect and dry-run semantics

**CURRENT:** [ConnectBlock](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/validation.cpp#L2292-L2317) explicitly
does not rerun the two contextual checkers; comments warn about upgrade/reconnect
rules placed only there. Contextual checker comments also identify
[-reindex-chainstate limits](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/validation.cpp#L4098-L4111).
[Assumevalid decisions](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/validation.cpp#L2343-L2378) feed
[ConnectBlock's later path](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/validation.cpp#L2491-L2647), including
conditional script checking and an fJustCheck return before
normal undo/status/view updates; normal processing can raise SCRIPTS directly.
That status is not proof that every historical signature was freshly evaluated.
[TestBlockValidity](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/validation.cpp#L4495-L4550) uses selected
checks and a temporary view instead of normal index admission.

**CONDITIONAL:** Review initial acceptance, reconnect, assumed/trusted history
and reduced-check callers separately. Trace V10/V12/V14 to D05/D06/D07.

### S09. Child transactions, witness and hypothetical parent evidence

**CURRENT:** [Transaction hash computation](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/primitives/transaction.cpp#L69-L96)
distinguishes txid without witness from witness hash.
[Transaction deserialization](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/primitives/transaction.h#L184-L238)
has witness/unknown-flag rules.
[CheckTransaction](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/consensus/tx_check.cpp#L11-L59) includes
monetary, input and coinbase-shape checks, and
[CheckBlock](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/validation.cpp#L3978-L3999) applies it to child
transactions. No AuxPoW parent coinbase is currently passed through this route.

**CONDITIONAL:** Specify parent transaction/proof validity, hash conventions,
mutation handling and the extent of parent-network validation. An inclusion
proof and a numeric hash check do not establish all parent-network consensus.
R0's output commitment and unsigned amount fields select none of these rules.
Trace V02/V08/V11 to D01/D03/D04.

### S10. Disk index, full-block storage, restart and pruning

**CURRENT:** [CDiskBlockIndex](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/chain.h#L340-L371) stores status,
height, transaction/position metadata and six header fields, reconstructing the
header hash. [LoadBlockIndexGuts](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/node/blockstorage.cpp#L120-L165)
rebuilds that data and checks direct hash PoW.
[ReadBlock](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/node/blockstorage.cpp#L1036-L1081) resets the object,
decodes TX_WITH_WITNESS, checks direct PoW/signet/expected hash as applicable;
it is not all contextual validation.
[WriteBlock](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/node/blockstorage.cpp#L1134-L1165) writes message
start, serialized size and witness-capable block payload.
[PruneOneBlockFile](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/node/blockstorage.cpp#L258-L283) clears data/
undo availability and positions, retaining index validity/header information.

**CONDITIONAL:** Specify durable/reconstructible proof data, migrations and
pruned-node behavior for every representation. Retained index work is not retained
proof availability. Trace V12/V13 to D01/D04/D05/D07.

### S11. Raw reads, import and reindex are distinct paths

**CURRENT:** [ReadRawBlock](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/node/blockstorage.cpp#L1083-L1131)
checks stored message start and a MAX_SIZE ceiling before allocating the payload.
[ImportBlocks](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/node/blockstorage.cpp#L1261-L1308) invokes
LoadExternalBlockFile differently for reindex and explicit loadblock.
[LoadExternalBlockFile](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/validation.cpp#L4988-L5080) scans magic
and size 80..MAX_BLOCK_SERIALIZED_SIZE, parses the header/hash first, handles
unknown-parent records, and fully deserializes/accepts needed bodies.
Its size bound differs from the raw-read bound; known data can skip processing.

**CONDITIONAL:** Specify bounded framing and revalidation for each path rather
than treating one successful disk roundtrip as import/reindex coverage.
Generic [CompactSize guards](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/serialize.h#L330-L359)
and [bounded vector-read chunks](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/serialize.h#L666-L675)
are not an approved total AuxPoW budget. Trace V06/V12/V13 to D01/D04/D07.

### S12. RPC submission, proposal and template distinctions

**CURRENT:** [submitblock/submitheader](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/rpc/mining.cpp#L1086-L1155)
take different representations and processing routes; submitheader supplies
min_pow_checked=true after decode/previous-header lookup, not an auxiliary proof.
[DecodeHexBlockHeader/DecodeHexBlk](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/core_io.cpp#L237-L264) return
after deserialization with no explicit reader-exhaustion check in those helpers.
R0's exact-EOF rule must not be attributed to these existing RPC decoders.
[GBT proposal](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/rpc/mining.cpp#L748-L769) has duplicate shortcuts
and calls TestBlockValidity with PoW disabled/Merkle enabled.
[Template assembly](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/node/miner.cpp#L215-L229) fills the current
parent, time, expected bits and nonce zero; its optional dry run disables both
PoW and Merkle checks. These are not proof-production or mined-block guarantees.

**CONDITIONAL:** Define proposed-versus-submitted checks, framing and proof
availability deliberately; proposal/template success must not be promoted into
accepted auxiliary work. Trace V01/V05/V14 to D01/D03/D04.

### S13. Ancestry, signaling and active-chain selection

**CURRENT:** [CBlockIndex::GetBlockHeader](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/chain.h#L185-L195)
reconstructs the parent from pprev; AddToBlockIndex derives height from that parent.
[Contextual checks](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/validation.cpp#L4112-L4152) use that ancestry.
[Version computation](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/versionbits.cpp#L265-L284) and
[existing versionbits constants](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/versionbits.h#L18-L33) belong
to today's header layout, not an auxiliary ID/discriminator allocation.
[FindMostWorkChain](https://github.com/andaluzcoin/andaluzcoin/blob/d470a2b166a0e300f88b654564e6177439118ffa/src/validation.cpp#L3145-L3201) excludes invalid
or unavailable candidate paths before activation; work alone is insufficient.

**CONDITIONAL:** Define activation state, old-node behavior and recovery against
the selected ancestry and rules, without using active-tip state as a substitute.
Trace V03/V10/V15/V16 to D02/D05/D06/D07.

## 4. Identity, availability and failure dependencies

Let C be a child header and P its previous block on the child chain.
An auxiliary parent-work header Q is a different object from P.
A fixed C binds P through hashPrevBlock. Once P's ancestry is known, C's derived
height/ancestry do not change merely because another branch becomes active.

Under the **unselected hypothesis** that an attachment A is excluded from C's
identity, C with A1 and C with A2 can share a child hash while differing in proof
availability or validity. That is a design dependency, not present ALUZ behavior.

- Missing bytes are not automatically an objectively invalid child header.
- An invalid A1 followed by valid A2 requires a reasoned failure/cache scope;
  the dossier selects neither the taxonomy nor a cache key implementation.
- A previous header/data/cache success cannot authenticate unseen A2.
- Proof presence, proof checking, child contextual validity and retained data
  must be separately evidenced wherever the eventual design needs them.
- Different child headers may share parent work only under their independently
  valid commitments/contexts; no parent hash alone grants child acceptance.
- Actual caller flags, locks and shortcut invariants must survive the chosen
  design; no new proof-state flag is allocated by these statements.

If the chosen identity instead binds proof data, document the resulting identity,
replacement and serialization consequences; do not silently reuse the hypothesis.
Bad attachment, corrupted body and invalid child context need not share a failure
scope. Neither automatic permanent invalidity nor universal retry is selected.

## 5. Context and activation counterexamples

All rows are **future reasoning requirements**, not a selected activation plan.

| Case | Required distinction | Trace |
| --- | --- | --- |
| Same fixed C, active tip changes | C keeps P and its derived height; active-chain membership can change. | S03/S13; V15; D05/D06 |
| Different children at the same height, hypothetical fixed-height H | Height-only mode permission is the same at that height; expected bits/MTP may differ with ancestry. | S02/S13; V15; D06 |
| Hypothetical ancestry-dependent signaling | Same-height branches may have different signaling state only if the eventual mechanism derives that result from their histories. | S13; V16; D02/D06 |
| Unknown P | Context cannot be invented from the active tip. Current new-header admission reports missing previous block; future unavailable-proof handling remains open. | S03; V05/V15; D04/D06 |
| Same C, future-time rejection | Runtime clock can later make C timely without changing its ancestry or any reorg; not every acceptance input is immutable. | S02; V10/V15; D05/D06 |
| Higher-work branch lacks data | Current fork handling distinguishes missing data from invalidity; retained work does not manufacture proof/body availability. | S10/S13; V13; D05/D07 |

The [earlier truth tables](andaluzcoin-auxpow-proof-serialization-activation.md#6-parameterized-activation-specification)
use symbolic candidate heights. They are not evidence that a fixed child's height
changes during a reorg, or that actual node/cache/reconnect behavior was exercised.

## 6. Future acceptance-vector catalogue

**None of V01-V18 is implemented or executed by this dossier.**
These classes become concrete independent bytes, expected outcomes and node tests
only after the associated choices are specified. Existing toy coverage does not
silently satisfy them.

| ID | Future cases and required evidence | Surfaces / gates |
| --- | --- | --- |
| V01 | Header/full/compact/RPC/disk roundtrips, suffix/unknown-mode handling, identity consistency and every selected proof representation. | S01/S05/S10/S12; D01/D04/D07 |
| V02 | Missing, malformed, alternative and child/domain-mismatched proofs under the chosen grammar; identity/commitment binding without circular hashing. | S01/S03/S09; D01/D02/D03 |
| V03 | Child expected bits and numeric target boundaries, parent-versus-child work semantics, invalid context before credit. | S02/S13; D02/D03/D06 |
| V04 | Duplicate submissions and alternative attachments add work once per accepted child; independent valid branch totals and ties. | S02/S06; D03/D05 |
| V05 | Unknown, failed and valid parents, genesis/known-header shortcuts, trusted caller flags and minimum-work admission; no assumed proof validity from a flag. | S03/S04/S12; D03/D04/D05 |
| V06 | Header batches, presync/redownload commitments, compressed reconstruction, per-peer/concurrent costs and bounded retention. | S04/S05/S11; D01/D04/D05 |
| V07 | Full/compact reconstruction, partial proofs, known-data shortcuts, missing bodies and equivalent representations. | S05/S06; D01/D04/D07 |
| V08 | Parent transaction/coinbase/witness/txid/Merkle/mutation negatives; separate parent validity claims from child transaction checks. | S07/S09; D01/D03 |
| V09 | Bad A1 then good A2 and the reverse under a proof-excluded identity; repeated known-header/data/cache paths with correctly scoped failure. | S01/S03/S06/S07; D01/D05 |
| V10 | Concurrent reuse, positive/negative cache dependencies, future-time retry and reconnect/reduced-check callers under specified assumptions. | S07/S08/S13; D05/D06 |
| V11 | Network domain, signed ID/version encoding, parent-child policy and signaling conflicts under actual selected rules; no toy constants promoted. | S01/S09/S13; D02/D03 |
| V12 | Restart, index load, raw/block read, import and reindex retain/recover the selected proof evidence with defined upgrade behavior. | S08/S10/S11; D01/D04/D07 |
| V13 | Pruning, missing side-branch data, reacquisition and candidate eligibility distinguish availability from invalidity. | S06/S10/S11/S13; D04/D05/D07 |
| V14 | Proposal/template versus submitheader/submitblock outcomes; disabled-check results cannot count as accepted work or stored validation. | S08/S12; D01/D03/D05 |
| V15 | Same fixed child across active-tip changes; different same-height children around symbolic H; unknown ancestry and clocks remain distinct. | S02/S03/S13; D05/D06 |
| V16 | If selected: ancestry-derived signaling, boundary transition, old/new-node disagreement, reconnect and rollback; no real mechanism chosen here. | S08/S13; D02/D06/D07 |
| V17 | Preserve genesis/PoW/DAA/subsidy/identity/network and descriptor-only wallet behavior across every authorized later patch. | S01/S02/S12/S13; D08 |
| V18 | Independent implementations, adversarial resource/fuzz review, reproducible fixtures and independent security disposition before integration. | S01-S13; D01-D08 |

## 7. Unresolved owner/reviewer decisions

**Every D01-D08 gate remains OPEN.** Roles are proposed accountability categories,
not named assignees or completed approvals. Candidate alternatives below are not
production recommendations selected by this milestone.

See the [design-direction review package](andaluzcoin-auxpow-design-direction.md)
for concrete PROPOSED alternatives and an owner decision form; these gates remain OPEN.

| ID / accountable roles | Decision requiring explicit review | Evidence needed before implementation/integration |
| --- | --- | --- |
| D01 / owner, consensus, networking | Child identity, proof attachment, complete grammar, canonical framing and all serialization views. | Approved exact format; independent V01/V02/V07/V12 corpora and compatibility rationale. |
| D02 / owner, consensus, ecosystem | Parent family, algorithm/domain/ID encoding, version/signaling coexistence and cross-network separation. | Expanded pinned evidence and a specified network/encoding threat model; V03/V11/V16. |
| D03 / consensus, transaction/security reviewers | Proof validity, txid/witness, coinbase/Merkle rules, parent validity extent and child work semantics. | Independent real-verifier agreement, precise negative corpus and V02/V03/V04/V08/V14. |
| D04 / networking, storage, security | Input/batch/per-peer/concurrent budgets, proof availability, missing-data behavior and peer/RPC error treatment. | Measured/adversarial allocation and work budgets at each actual route; V01/V05/V06/V07/V12/V13. |
| D05 / consensus, validation/cache maintainers | Success/failure identity, cache/status dependencies, alternative proof replacement, concurrency and trusted assumptions. | Explicit invariants and negative/positive/race cases V04/V05/V09/V10/V13/V14/V15. |
| D06 / owner, consensus, release | Actual mode/activation state derivation, legacy coexistence, old-node behavior and recovery. | Selected mechanism and independent ancestry/boundary/reorg/reconnect/rollback evidence V03/V10/V15/V16. |
| D07 / storage, networking, operators | Durable proof representation, migration, pruned-node recovery and compatible relay/submission behavior. | Restart/import/reindex/pruning/reconstruction plans and V01/V07/V12/V13/V16. |
| D08 / owner, independent security/release reviewers | Scope of a later integration, independent audit, invariant preservation and operational authorization. | Reviewed code/evidence inventory, V17/V18 and separately authorized operational/launch gates. |

A source-level shortcut is a place to specify an invariant, not evidence that a
new implementation should simply delete the shortcut. No taxonomy, cache design,
network budget, parent-chain policy or activation parameter is inferred from R0.

## 8. Dependency order and implementation-readiness evidence

See the [proposed B1 candidate contract](andaluzcoin-auxpow-b-candidate-specification.md)
for exact reviewable bytes, view/policy contracts and planned evidence; it adopts no production rule.

1. **Freeze the research input.** Record revision, surfaces, source facts and
   missing evidence. This dossier supplies that map; issue #99 records review.
2. **Resolve the specification choices.** D01-D03 establish actual identity,
   formats, network/domain and proof/work semantics. D04-D07 must be analyzed
   alongside them; storage, cost and compatibility constraints can require
   revisiting earlier choices. This is not a one-way approval checklist.
3. **Specify verifiers and integration invariants.** Publish independent positive/
   negative real-proof corpora, failure/cache scope, per-path budgets and the
   activation/recovery design. Refine V01-V18 into exact acceptance criteria.
4. **Independently review isolated implementations.** Parser agreement, resource/
   fuzz evidence and security review must use the selected specification.
   Existing R0 decoders and synthetic work labels are not replacements.
5. **Authorize a separate production patch.** Only a later explicitly scoped
   change can implement consensus/network/storage behavior. Audit every
   identified surface and omitted call path, including upgrade/reindex and
   assumevalid/trusted-input implications; preserve D08 invariants.
6. **Qualify integration and operations separately.** Actual node transition,
   old-node, reorg, recovery and distribution evidence, and independently
   participating operators/miners, remain later requirements. No pool outreach,
   service deployment or live mining is authorized by this source audit.

There is no authorization to skip from a complete research dossier to step 5.
A future readiness decision must identify revision, reviewers, selected choices,
results and unresolved limitations; all relevant dependencies must be evidenced.

## 9. Evidence boundary and verification reporting

The present artifact is documentation: no new runtime driver, prototype parser,
activation simulation or live node exercise is introduced. The issue/PR execution
report must distinguish source/link/whitespace/scope checks and any CI results
actually obtained from this catalogue of **unexecuted** future requirements.
No fresh test pass, performance measurement or security certification is claimed
merely by listing a function, future vector or reproduction link.

Source locations are baseline-specific. A future production branch must refresh
the audit against its own immutable revision and check callers, serialization
parameters, locking, flags, assumed history and failure behavior again.
The existing research suite may provide regression evidence within its declared
limits; no runtime test should be added solely to mirror this documentation.

The expected #99 change surface is this document plus concise backlinks in the
candidate and adversarial studies. Production source, runtime tests, wallets,
network settings and the readiness checklist remain outside this milestone.

## 10. Research completion and remaining gates

Issue #99 follows the established branch → evidence/PR → technical review/CI →
routine research release process under standing owner approval. Research tagging
still requires the successful exact-merge master CI and verified annotated tag
before final report/closure. Critical production decisions remain separate.

This dossier makes the unfinished integration work traceable and reviewable.
It does not select or deploy AuxPoW, prove real proof acceptance, provide an
independent security certification, or close implementation/operational gates.
The [mainnet checklist](andaluzcoin-mainnet-readiness.md) remains unchanged:
all 21 gates unchecked, public economic mainnet **NO-GO**.

See the [B1 specification review](andaluzcoin-auxpow-b-specification-review.md)
for cross-view, synchronization and native-boundary findings; production gates remain OPEN.

See the [separate correction proposals](andaluzcoin-auxpow-b-specification-corrections.md)
for capacity, sync, terminal-height and genesis requirements; no integration is authorized.
