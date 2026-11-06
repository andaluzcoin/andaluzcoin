# Explicit network-bound AuxPoW candidate B1 and evidence plan

## 1. Status, authorization and scope

**PROPOSED CANDIDATE ONLY. No production rule or value is adopted.**
[Issue #103](https://github.com/andaluzcoin/andaluzcoin/issues/103) scopes this new
v0.2.84 research milestone. The owner
[approved B](https://github.com/andaluzcoin/andaluzcoin/issues/101#issuecomment-6652354993)
for the isolated specification/evidence phase in
[direction package section 11](andaluzcoin-auxpow-design-direction.md#11-finite-next-phase-if-the-owner-chooses-a-direction).
That approval permits exact candidate proposals for separate review, not a
real ALUZ parser, consensus/network/storage implementation or activation.

Frozen ALUZ baseline: **4c98bfa88c4c45014677c7e9b2fec53459b000aa**,
tree **03027e0bdd4fb6f0c50707cc1e8041ac20ef36ae**.
Namecoin precedent remains pinned to
**942b14038f3ae704b6c2d50355de835d3ee92288**.
Current ALUZ still validates ordinary SHA256d work with its existing 80-byte
header and descriptor-wallet-only policy. Production genesis/PoW/DAA/subsidy,
identity/network settings, runtime tests and CI are unchanged.

This document fixes **one reviewable B1 candidate**, including provisional
literal limits and a parameterized trusted configuration. Every B1 MUST below
defines this proposal, not today's node behavior. All D01-D08 production/evidence
gates remain OPEN; all 21 [launch gates](andaluzcoin-mainnet-readiness.md) remain
unchecked and public economic mainnet remains **NO-GO**.
No upstream oracle, candidate parser, performance experiment or historical
mined-proof replay is implemented/executed by this document.

## 2. Source facts and deliberate departures

| Immutable source | Fact used / candidate departure |
| --- | --- |
| ALUZ [block/header](https://github.com/andaluzcoin/andaluzcoin/blob/4c98bfa88c4c45014677c7e9b2fec53459b000aa/src/primitives/block.h#L26-L107), [GetHash](https://github.com/andaluzcoin/andaluzcoin/blob/4c98bfa88c4c45014677c7e9b2fec53459b000aa/src/primitives/block.cpp#L15-L18) | C80 has six fields; proof exclusion is compatible with that hash starting point, not with unchanged future wire views. |
| ALUZ [HashWriter](https://github.com/andaluzcoin/andaluzcoin/blob/4c98bfa88c4c45014677c7e9b2fec53459b000aa/src/hash.h#L100-L129), [TaggedHash](https://github.com/andaluzcoin/andaluzcoin/blob/4c98bfa88c4c45014677c7e9b2fec53459b000aa/src/hash.h#L213-L219) | HashWriter has double/single finalizers; TaggedHash primes SHA256(tag) twice. B1 requires the double finalizer, not the usual BIP340 single-SHA result. |
| ALUZ [context](https://github.com/andaluzcoin/andaluzcoin/blob/4c98bfa88c4c45014677c7e9b2fec53459b000aa/src/validation.cpp#L4112-L4152), [admission](https://github.com/andaluzcoin/andaluzcoin/blob/4c98bfa88c4c45014677c7e9b2fec53459b000aa/src/validation.cpp#L4218-L4290), [work/index](https://github.com/andaluzcoin/andaluzcoin/blob/4c98bfa88c4c45014677c7e9b2fec53459b000aa/src/node/blockstorage.cpp#L224-L255) | Expected bits/ancestry, work verification and index credit are separate. Existing known-header/min-work shortcuts do not authenticate new evidence. |
| ALUZ [native index height](https://github.com/andaluzcoin/andaluzcoin/blob/4c98bfa88c4c45014677c7e9b2fec53459b000aa/src/chain.h#L105-L106) | CBlockIndex stores int nHeight; B1 bounds admitted/configured heights to the nonnegative signed32 range before native conversion/addition. |
| ALUZ [transaction shape](https://github.com/andaluzcoin/andaluzcoin/blob/4c98bfa88c4c45014677c7e9b2fec53459b000aa/src/primitives/transaction.h#L341-L344), [basic checks](https://github.com/andaluzcoin/andaluzcoin/blob/4c98bfa88c4c45014677c7e9b2fec53459b000aa/src/consensus/tx_check.cpp#L19-L59), [txid](https://github.com/andaluzcoin/andaluzcoin/blob/4c98bfa88c4c45014677c7e9b2fec53459b000aa/src/primitives/transaction.cpp#L69-L96) | Coinbase shape, amount rules and stripped txid are distinct from full parent validity. B1 proposes the precise proof-only subset below. |
| Namecoin [proof](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/auxpow.cpp#L41-L139), [slot/fold](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/auxpow.cpp#L143-L185), [serializer](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/auxpow.h#L88-L114) | Historical scriptSig/markerless and ignored-field semantics are not B1. B1 uses a unique exact output record, tagged auxiliary nodes and a ledger-key slot. |
| Namecoin [work route](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/validation.cpp#L1886-L1940), [numeric path](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/pow.cpp#L153-L186) | Parent work is tested against child bits; linkage is not full parent consensus. Future numeric evidence must exclude the fuzz-determinism shortcut. |

B1 is not Namecoin-compatible or the old AP79/R0 profile. Reusing SHA256d,
a binary branch or the pure-header concept establishes no pool interoperability.
The [direction package predicate/fixture ledger](andaluzcoin-auxpow-design-direction.md#8-predicate-ledger-decode-is-not-acceptance)
retains the source-generated/regtest and unavailable-historical-evidence limits.

## 3. Byte and hash conventions

All strings named ASCII below mean exactly those bytes, case-sensitive, with
**no implicit NUL**. Integers are unsigned little-endian unless stated otherwise.
C80 is the current 80-byte six-field header serialization, beginning with
signed-int32 version. A digest D is the raw 32 bytes returned by SHA256d; its display
hex is reversed only for a display explicitly labelled as such.
PoW compares the little-endian uint256 value of D, never its display string.

H2(x) = SHA256(SHA256(x)).
For an exact ASCII tag t, let q = SHA256(ASCII(t)).
TH2(t,x) = H2(q || q || x). The existing TaggedHash primed writer can be
finalized differently: B1 requires the double-hash GetHash result, not the usual
BIP340 GetSHA256 single-SHA result. The exact transcript above is normative.

| Purpose | Exact tag |
| --- | --- |
| Ledger key | ALUZ-B-CANDIDATE/ledger/1 |
| Profile ID | ALUZ-B-CANDIDATE/profile/1 |
| Child leaf | ALUZ-B-CANDIDATE/leaf/1 |
| Auxiliary internal node | ALUZ-B-CANDIDATE/node/1 |
| Slot | ALUZ-B-CANDIDATE/slot/1 |
| Evidence seal | ALUZ-B-CANDIDATE/evidence/1 |

CS(n) is minimal Bitcoin CompactSize: 00..fc; fd+LE16; fe+LE32; ff+LE64,
with the appropriate lowest representable range. Reject nonminimal encodings
and values beyond a field bound before payload reads, allocation or loops.
Unframed variable concatenation is forbidden. Every complete view and inner
length-delimited object below has exact EOF: truncation and surplus reject.

## 4. Exact profile manifest and provisional limits

ProfileID P = TH2(profile tag, the following ASCII manifest bytes).
The first byte is A of ALUZ-B1; every displayed line ends in LF, including the
last. Code-fence bytes, indentation and CR are not part of the manifest.

```text
ALUZ-B1
revision=2
hash=TH2-SHA256TAG
network=ND1
config=CFG1
mode=MONOTONE-DIRECT-AUX1
storage=BIND1-SIDECAR1-CURRENTINDEX
frame=REC1
parent=STRIPPED-TXID-P80
family=ALUZBMM!
aux-node=TAGGED-NODE1
slot=LEDGER-NONCE-HEIGHT1
tx-max=8192
outputs-max=64
output-script-max=4096
coinbase-script-min=2
coinbase-script-max=100
parent-depth-max=30
aux-depth-max=30
proof-max=10205
record-max=10362
block-and-compact-max=4000000
template=RESERVE-RECORD-MAX1
child-tx-count-max=100000
headers-count-max=16
headers-payload-max=165857
```

The manifest excludes its derived P, LedgerKey/configuration values, child,
proof/root/parent data and fixture seals. It identifies this document's B1
interpretation. After this candidate's review freeze, any normative acceptance change requires
a new revision and manifest/P; reusing P for a different interpretation is forbidden.
Ledger/configuration values are excluded so different ledgers can use the same P.

These are proposed study/review limits with no operational adequacy claim.
8192 bounds proof transaction work; 64 outputs and 4096-byte scripts bound loops.
Depth 30 bounds index arithmetic and each branch. The total proof/record maxima
are derived below. The 4,000,000-byte complete-view ceiling conservatively keeps
one finite transport budget; it is not an unchanged future block-capacity claim.
R0's smaller caps are not evidence that these limits are safe or sufficient.

## 5. Trusted network/configuration and immutable mode contract

ND1 = ASCII(ALUZNET1)[8] || class:u8 || GenesisHash[32] ||
LedgerNamespace[32] || CS(originLen) || Origin[1..4096] ||
CS(challengeLen) || Challenge[0..4096].
Classes are MAIN=0, TEST=1, SIGNET=2, REGTEST=3; other values reject.
GenesisHash = H2(the configured GenesisC80). Non-SIGNET requires empty Challenge;
SIGNET requires the exact configured nonempty challenge bytes.
Canonical maximum ND1 length is8+1+32+32+3+4096+3+4096=8271.

LedgerNamespace is an explicitly configured nonzero 32-byte lineage identifier.
Origin is the exact immutable origin-descriptor byte string supplied in the
trusted local network manifest. They are not read from a prover or synthesized
from a network label. Custom networks/overrides without an explicit manifest
are unsupported and reject; they must not inherit a leftover default label.
A distinct intended ledger must have a distinct descriptor/namespace.
Intentionally identical descriptors define the same ledger for B1; no global
registry or uniqueness proof is asserted. Origin must not be regenerated from
current profile, activation state or active tip when the same ledger upgrades.

LedgerKey K = TH2(ledger tag, ND1). K is ONE trusted constant for the same ledger
across all accepted routes/profiles. The profile never becomes a second slot key.
The actual production network-to-manifest mapping and all official K values
remain unallocated; this is a complete parameterized rule for supplied trusted
configuration, not authentication of self-declared genesis/domain labels.

CFG1 is trusted local input, not an untrusted network view:
ASCII(ALUZBCF1)[8] || GenesisC80[80] || CS(ND1len) || ND1 ||
P[32] || H:u32 || BeforeMask:u8 || AfterMask:u8 ||
MinAdmissionWork:uint256-LE || EOF.
ND1len must equal its canonical parsing and be<=8271; maximum CFG1 length8432.
P must equal the manifest-derived B1 P; unsupported profiles/configuration reject.
**BeforeMask MUST be1 (DIRECT); AfterMask MUST be2 (AUX).**
Zero, BOTH=3, reverse or any other masks reject configuration.
H is encoded u32 but MUST be in1..INT32_MAX (2147483647); larger values reject
before native conversion. H is immutable for this ledger history; no literal
production H is chosen. MinAdmissionWork is a local admission threshold only.
ConfigID = H2(exact canonical CFG1 bytes).

The trusted node confirms ND1 genesis/class/challenge against its intended
network. Missing, ambiguous or mismatched trusted configuration rejects all B1
inputs. The persistent ledger binding in section12 freezes K, H, genesis and
mode ordering. A profile change cannot supply another H or re-enable DIRECT
after AUX. Replacing incompatible CFG1 while retaining old index/work is not
permitted cache invalidation; stop for separately reviewed migration/full
revalidation, never automatically restore DIRECT descendants.
A local admission-threshold change can change ConfigID/receipts but not that
immutable ledger binding. No production configuration/migration is adopted.

For a non-genesis C80: require a known same-ledger previous child matching
hashPrevBlock. Require pprev.height in0..INT32_MAX-1; reject invalid or
INT32_MAX parent heights before addition. Compute h=pprev.height+1 using checked
wider arithmetic, require h in1..INT32_MAX, then convert to native height.
No signed overflow/unsigned wrap is permitted; genesis height is0.
At h<H only DIRECT is legal; at h>=H only AUX is legal.
This is the exact proposed monotone fixed-height mechanism.
Expected bits, MTP, future-time and full signed-version rules use that fixed
ancestry and current ALUZ consensus parameters/clock, not the active tip.
Unknown ancestry or missing required evidence is UNAVAILABLE, not presumed valid.
Admission/eligible work preserves current native exclusions for a child properly
marked consensus-invalid and a failed parent/ancestor. Intrinsic evidence success
cannot revive either; an attachment-only failure must not create such a permanent
child-invalid mark. Header admission does not require the previous child's full
body/scripts merely to know its ancestry; native header/context and required
proof-availability checks still apply.
Genesis requires exact configured GenesisC80 and DIRECT regardless of H;
it does not allocate a new genesis or auxiliary genesis work route.

Mode is proposed outside the child version: no Namecoin high-word ID equality/
dispatch, no new child version bit, no masking away current ALUZ versionbits.
Different same-height children get the same height-only route, while expected
bits/MTP can differ with ancestry. A fixed child does not change height when
another branch becomes active. CFG1 values are not an approved deployment.

## 6. Exact candidate HeaderRecord and proof bytes

Hc = H2(C80). Hc is the only child header/block identity; the new record, route,
K/P and proof are excluded from that identity. Current child transaction
identity/merkle/witness validation remains separately required.
For DIRECT, K/P are checked framing/context metadata, NOT part of its PoW
preimage. The same otherwise-valid C80 can be re-enveloped for another trusted
ledger sharing its genesis/history/rules without new direct PoW. AUX binds K/P
in its committed leaf. Neither statement establishes general replay prevention
or alleges a current ALUZ-network exploit.

REC1 HeaderRecord, in order:

| Field | Exact rule |
| --- | --- |
| Magic | ASCII ALUZBSP1, 8 bytes |
| Route | u8: 0=DIRECT, 1=AUX; all others reject |
| Reserved | u8 zero |
| Ledger/profile | K[32], P[32], both exactly equal trusted values |
| Child | C80[80] |
| Proof | CS(proofLen), then exactly proofLen bytes |
| End | Exact view EOF unless this record is the defined prefix of another view |

DIRECT requires proofLen=0, record length 155, and direct numeric Hc work.
AUX requires the nonempty proof grammar below. There is no malformed-AUX,
unknown-profile or missing-proof fallback to DIRECT. A separately submitted evidence record must satisfy the same immutable mode;
there is no DIRECT repair route at/after H.

AUX Proof, in order:
CS(txLen) || StrippedCoinbase[txLen] ||
CS(parentDepth) || parentDepth*Sibling[32] ||
CS(auxDepth) || auxDepth*Sibling[32] ||
auxIndex:u32 || nonce:u32 || P80[80] || EOF.
txLen is 142..8192 and explicitly greater than 64; both depths are 0..30.
Reject count/length overflow or bound violation before traversal.
Parent index is literal zero and is not serialized; historical hashBlock and
unused parent-index bytes are not part of B1.
auxIndex < 2^auxDepth, including index=0 at depth zero.

Minimum AUX proof = 1+142+1+1+4+4+80 =233 bytes; HeaderRecord minimum388.
Maximum proof =3+8192 +2*(1+30*32)+4+4+80 =10205 bytes.
The fixed record prefix is154 bytes; maximum record154+3+10205=10362.
The length envelope must be checked before retaining/buffering a full record.
These are byte-arithmetic bounds, not measurements or an executed parser oracle.

## 7. Stripped parent transaction and sole commitment

The proof carries ONLY canonical nonwitness transaction serialization:
version:i32, CS(vin=1), null previous hash[32], previous index=ffffffff,
CS(scriptSigLen=2..100), scriptSig, sequence:u32,
CS(voutCount=1..64), outputs, locktime:u32, exact transaction EOF.
Each output is signed int64 little-endian value, CS(scriptLen=0..4096), script.
Require nonnegative values and a cumulative sum <=INT64_MAX using checked
arithmetic. This is a proposed proof-sanity range, not a parent's MAX_MONEY,
subsidy, script, UTXO or complete transaction consensus validation.
Reject a witness marker/flag serialization and all nonminimal/ambiguous forms.
Txid = H2(these exact stripped bytes).

An actually witness-bearing parent transaction can have these same stripped
bytes/txid. B1 proves neither witness absence nor validity of the parent's
witness commitment, reserved value, scripts or transaction set.

Common family marker F = ASCII ALUZBMM!, exactly8 bytes.
Count raw byte occurrences of F over the ENTIRE canonical stripped coinbase,
including scripts, values, versions and all other fields, across ALL profiles.
Exactly one occurrence is required. A malformed/non-designated occurrence rejects,
not just a second well-formed record. Witness bytes are outside this txid-bound
scope and cannot carry the recognized B1 commitment.

The sole occurrence must start at offset3 of exactly one output script:
6a 4c 4d || F[8] || P[32] || AuxRoot[32] || auxHeight:u8 || nonce:u32.
Thus payload77, script80 bytes; the output value must be zero.
6a=OP_RETURN, 4c=OP_PUSHDATA1, 4d=77. Alternative push forms, script lengths,
trailing script bytes and unknown/mismatched P reject.
Record auxHeight must equal auxDepth (tree height, not child height); both nonces agree.
This intentionally uses one ProfileID for the entire parent carrier: different
ledgers with the same P can co-mine; ledgers requiring different P cannot share
one B1 carrier. That restriction is a review tradeoff, not pool compatibility.
An accidental extra F in another field also rejects; this is a deliberate strict
family-recognition restriction, not a claim about parent-network consensus.

Canonical one-input/one-output size is60+scriptSigLen+outputScriptLen:
minimum60+2+80=142, never64. This excludes parent coinbase leaf preimages from
the exact64-byte internal-node preimage domain. Require txLen>64 explicitly.
An 8192-byte maximum is attainable with scriptSig2 and three scripts of lengths
80,4096,3932: 142+4107+3943=8192. Output values can be zero.
No fixture or upstream execution result is inferred from those arithmetic facts.

## 8. Exact leaf, slot, branches and parent work

Leaf = TH2(leaf tag, K[32] || P[32] || Hc[32]).
The auxiliary internal function is Node(a,b)=TH2(node tag,a[32]||b[32]).
It is common to all leaves in one tree, not keyed separately by each ledger.
At depth j from zero, combine running value on the right iff bit j of auxIndex
is one; otherwise on the left. The resulting raw root must equal AuxRoot.
No reversed display hash, implicit hex string or Namecoin raw-Hc leaf is accepted.

S = TH2(slot tag, K[32] || nonce:u32 || auxDepth:u8).
expectedIndex = LE32(S[0..3]) & (2^auxDepth-1), with expectedIndex=0 at depth zero.
auxIndex must equal expectedIndex. Slot does NOT depend on Hc, P, route, height
of the child, active tip or prover labels. K/slot interpretation, common family marker, parent index zero/plain txid fold,
canonical parent coinbase length>64, tagged auxiliary node function and exact
record/tree geometry are stable across simultaneously accepted profiles.
A future profile changing these invariants cannot be coaccepted without a
separate anti-reuse design/review. Nonce trials do not guarantee collision-free multi-ledger packing.

ParentRoot starts at Txid and folds each parent sibling using plain H2(a||b),
always at literal index zero: H2(running||sibling). It must equal P80's raw
hashMerkleRoot. Branch length does not prove the parent's total transaction count.
One path cannot establish global no-duplicates or full Merkle mutation-freedom:
a hidden duplicated subtree can be invisible to that path.
No global mutation-free-parent claim is made, even if equal-node checks are added.

For actual acceptance, derive T from the child's EXPECTED nBits with current
ALUZ powLimit; reject negative, zero, overflow and above-limit targets.
C80.nBits must equal that ancestry-derived value.
DIRECT requires LE256(Hc)<=T.
AUX requires LE256(H2(P80))<=T plus every proof/commitment predicate above.
Parent nBits, version, time and previous hash are opaque work-header bytes;
parent nBits is NOT the target used here. No parent/child numeric-ID comparison
or recursive work delegation is evaluated. B1 does not interpret Namecoin parent
ID bits or bit8, validate a parent chain's DAA/history/membership or carry a
recursive parent proof. P80 being80 bytes does not prove its originating network
has no extension/flag/AuxPoW. Extra proof bytes still reject at EOF.
All work claims require the ordinary numeric path, not fuzz determinism.

### Conditional non-amplification within one accepted ancestry

For two AUX children using fixed P80, its Merkle root is fixed. With parent
index zero, canonical stripped CB length>64 and H2 collision resistance,
distinct CB/path witnesses at different depths cannot alias a CB leaf with
a 64-byte internal preimage. Equal parent roots bind the same CB unless an H2
collision is found. The single common-family record fixes P, AuxRoot, depth
and nonce; one K fixes one slot. Exact power-of-two geometry fixes depth/index.
Different accepted leaf/Hc values there require a hash collision.

This proves no DIRECT/AUX hybrid claim. The rejected hybrid counterexample is:
make AUX child C1; use a valid child C2 as P80, with C2.prev=Hc1 and C2's
coinbase carrying C1's sole commitment; mine C2/P80 once. A BOTH policy would
credit C1 as AUX and then C2 as DIRECT in the SAME ancestry.
A parent.prev filter blocks only the immediate example; a body-only marker ban
does not protect bare-header credit without extra authenticated DIRECT evidence.

B1 therefore forbids BOTH and every AUX→DIRECT transition:
DIRECT→DIRECT is header-identity deduplication; AUX→AUX uses the argument above.
An earlier DIRECT ancestor reused as a later AUX parent's P80 would commit a
descendant Hc through that ancestor's coinbase/root while descendant ancestry
commits the ancestor Hc. Excluding such a construction requires explicit
preimage/second-preimage/fixed-point hardness and acyclic-construction assumptions,
not collision resistance alone. This is conditional reasoning, not executed
cryptographic evidence or a comprehensive mining-security proof.

The scope is ONE accepted ancestry/history. Incomparable forks straddling H
can still reuse P80 as DIRECT on one fork and AUX on another; their work is not
summed into one history. Do not make validity depend on whether a parent hash
happens to be present elsewhere in the node's known-header index.
The argument does not prove unique full child bodies/witness, global no-duplicate
tree contents, full parent validity, economics, concentration or reorg security.
Mixed-mode recovery remains blocked pending a different exact design/review.

## 9. Verification, context and once-only state

A candidate verifier is side-effect-free over an immutable canonical record.
It checks trusted configuration/record grammar, known-child ancestry and route,
current expected bits/time/full-version rules, then applicable work/proof.
Full child transactions, witness commitment, UTXO/scripts and current monetary
consensus remain separate full-block checks. No min_pow_checked, known-header,
HAVE_DATA or fChecked result substitutes for an omitted proof predicate.

For valid expected target T, accepted work increment is floor(2^256/(T+1)),
matching current GetBitsProof(nBits)/GetBlockProof(header), once per Hc regardless
of proof alternatives or submissions. Accumulation uses current uint256 addition
semantics, not the earlier synthetic model's overflow-refusal rule.
Provisional screening work for presync is NOT accepted ledger/index work.
AUX parent hash size/parent difficulty or multiple valid proofs add no second
increment. Conflicting claimed child bits/context cannot repair the same child.
No extra work is obtained from the parent header's nBits or origin claims.

Candidate outcomes distinguish MALFORMED_RECORD, INVALID_EVIDENCE,
INVALID_CHILD_CONTEXT, UNAVAILABLE_CONTEXT/DATA, RETRY_TIME and VALID_EVIDENCE.
These are proposed abstract verifier outcomes, not allocated node reject codes,
peer penalties or BLOCK_VALID/FAILED/HAVE flag meanings.
Future-time retry and absent parent/data must not permanently poison Hc.
A valid A1 remains stored if A2 fails; valid A2 gets no inherited proof trust
from A1 or Hc. A DIRECT high-hash result is a failure of that work route/evidence, not an
intrinsic statement that no evidence could certify C80 under any hypothetical
policy. Under B1's actual immutable mode, a disallowed alternative route rejects;
there is no fallback within a failed AUX request.

Separate intrinsic evidence checks from contextual acceptance. A successful
context receipt binds Hc,K,P,route, E=TH2(evidence tag, exact HeaderRecord),
ConfigID, fixed pprev identity, derived height/expected bits/MTP, applicable
route, the frozen ALUZ ruleset/consensus-parameter bundle, and clock/data
preconditions. The ruleset reference here is the stated immutable ALUZ baseline;
an arbitrary new binary/ruleset cannot reuse its contextual verdict.
Lookup/use must reference the SAME immutable bytes; no post-check swap.
Concurrent successful A1/A2 commit is idempotent for Hc/work. Reorg alone does
not change fixed ancestry. Current route, actual-ancestry expected bits/MTP,
full-version and relevant time/configuration checks are ALWAYS reevaluated for
a new admission/eligibility decision. ConfigID alone is not a fingerprint of all
binary/consensus overrides. Cache hits may reuse only immutable byte/hash facts
with identical function/input/profile preconditions, never a cached context-pass
as authority. E is a public collision-resistant seal, not a MAC/signature or
permission token: recompute it from the actual canonical bytes.
Incompatible immutable ledger binding changes stop, not automatic mode reset.

Local MinAdmissionWork changes neither historical validity nor credited work;
no historical prefix must independently exceed today's threshold at restart.
A behind local clock producing RETRY_TIME must not erase stored evidence/work
or permanently invalidate an accepted Hc. Keep persistent proof/work facts
separate from temporarily unavailable/current eligibility and reevaluate time
preconditions without a second credit when eligibility returns.

## 10. Every candidate representation and admission view

All names below are logical PROPOSED views, not allocated live P2P commands/RPCs.
No native legacy decoding fallback is permitted inside a B1 view.
A preserved Hc does not preserve deployed wire/disk/mining compatibility.
All request lengths are capped before variable buffering/resize.

| View | Exact bytes/presence and acceptance contract |
| --- | --- |
| Single header / submitheader / getblockheader B1 | Exactly one HeaderRecord. Bare C80 is diagnostic/template material only, never accepted evidence for AUX. Retrieval needs the retained validated record; it must not reconstruct proof trust from six index fields. |
| Headers batch | CS(N=0..16), then N repetitions of u32(recordLen)\|\|HeaderRecord; exact payload EOF, total<=165857. Each length<=10362. Continuity is checked between C80s; all record evidence is screened before provisional work. |
| Full block / submitblock B1 | HeaderRecord followed by canonical child transaction vector CS(N=1..100000)\|\|transactions with current TX_WITH_WITNESS grammar, exact EOF. Entire view<=4000000 bytes; current child weight/transactions/UTXO/scripts also apply to C80+child vector. Proof bytes consume the separate total-view budget and can reduce available child payload capacity. |
| Compact block B1 | HeaderRecord\|\|nonce:u64\|\|CS(shortCount)\|\|shortIDs[6*shortCount]\|\|CS(prefillCount)\|\|prefilled entries, exact EOF<=4000000. Total transactions=shortCount+prefillCount in1..100000; prefillCount>=1. Each prefilled entry is CS(deltaIndex)\|\|child TX_WITH_WITNESS. First absolute index=deltaIndex=0 and contains coinbase; later absolute=previous+delta+1 with checked range/strict increase. |
| Compact selector / reconstruction | k=SHA256(C80\|\|nonce:u64); SipHash-2-4 uses first two little-endian u64s of k over raw child wtxid bytes; short ID is low48 bits serializedLE6. No legacy txid-mode fallback. Header evidence is verified before body reconstruction. Missing/colliding IDs trigger bounded transaction/full-block acquisition, not child invalidity or proof reuse. blocktxn supplies transactions only and cannot fill missing HeaderRecord evidence. |
| blocktxn request/response B1 | Request=Hc[32]\|\|CS(N=1..100000)\|\|N repetitions of CS(deltaIndex), exact EOF<=500037 bytes; first absolute=first delta, later absolute=previous+delta+1, all unique/in-range for the held compact block. Response=Hc[32]\|\|CS(N)\|\|N child TX_WITH_WITNESS objects, exact EOF<=4000000. Hc/count/order and each reconstructed wtxid/short-ID position must match the one bounded outstanding request; no proof is supplied. Reuse only the already-held immutable validated HeaderRecord. A full fallback with A2 verifies its new record independently. |
| RPC hex | One applicable complete binary view as lowercase even-length hex, no whitespace/prefix/trailing bytes. Submitheader<=20724 chars; submitblock/proposal<=8000000. JSON/body front ends must bound input before decoding/buffering; an already buffered string is not preallocation protection. |
| Proposal | Exactly the Full-block B1 view; structural/linkage/current child context checks apply, numeric work may be disabled solely for this non-admitting proposal operation. Return a labelled proposal-only result; never create VALID_EVIDENCE, index work or durable proof status from it. |
| Mining template | ASCII ALUZBTM1[8]\|\|K[32]\|\|P[32]\|\|Route:u8\|\|C80[80]\|\|canonical child vector. The prefix is153 bytes. DIRECT child-vector bytes<=3999845 (4000000-155); AUX<=3989638 (4000000-10362), reserving the complete maximum HeaderRecord before mining. These bounds include the vector count; template EOF<=4000000. Use the sole route permitted at derived height; no proof is present. This is NOT a HeaderRecord/submitted block. Fill current child expected bits/time/coinbase; C80 changes require rebuilding leaf/commitment/parent work. |
| Disk block / raw export / import | ASCII ALUZBDS1[8]\|\|u32(payloadLen)\|\|Full-block B1 view, EOF; payloadLen<=4000000. Network/ledger binding remains inside HeaderRecord. Imported records are fully decoded/validated; a C80-first skip may not authenticate unseen attached bytes. No implicit recognition as the current flat-file format. |
| Evidence sidecar / restart | ASCII ALUZBEV1[8]\|\|Hc[32]\|\|E[32]\|\|u32(recordLen)\|\|HeaderRecord, EOF. Identity/seal/length must agree, recordLen<=10362. This is separate evidence storage, not a new inferred meaning for current index flags. |

The compact selector is a precise candidate choice based on the current
[short-ID machinery](https://github.com/andaluzcoin/andaluzcoin/blob/4c98bfa88c4c45014677c7e9b2fec53459b000aa/src/blockencodings.cpp#L34-L70)
and [serialization](https://github.com/andaluzcoin/andaluzcoin/blob/4c98bfa88c4c45014677c7e9b2fec53459b000aa/src/blockencodings.h#L104-L130),
not claimed compatibility. Future independent vectors must verify keys, wtxid,
delta bounds, proof presence and reconstruction behavior.

Presync uses the immutable
[screening/redownload state machine](https://github.com/andaluzcoin/andaluzcoin/blob/4c98bfa88c4c45014677c7e9b2fec53459b000aa/src/headerssync.cpp#L177-L279)
as the candidate anti-DoS reference, with these explicit modifications/requirements:
decode full HeaderRecords instead of assuming bare six-field headers; apply
route/profile/known-anchor-height and linkage/numeric screening to EACH record
before its claimed-bit work enters provisional totals; retain bounded branch
state/claimed targets, not accepted index credit. PermittedDifficultyTransition
is screening, not exact contextual acceptance.
Compressed retention stores only C80-derived fields plus K/P/route/E receipt
references, not an authenticated replacement proof. Existing GetHash-based
commitments do not authenticate excluded proof bytes.
Redownload requires a complete HeaderRecord and independently redoes proof and
actual ancestry/context before index admission; different A2 must be checked,
not promoted by A1's transcript. Invalid/missing replacement aborts/restarts
local synchronization without permanently poisoning an otherwise valid child.
For screening only, valid-range C80.nBits is the claimed target; full expected-bit
and ancestry-context equality is mandatory before accepted index work. No screen
receipt is a full contextual verdict. MinAdmissionWork is CFG1's exact threshold.
Retained synchronization units (compressed headers or commitment entries) are
capped at4096 per peer and32768 globally; exceeding a cap aborts local admission,
not child consensus validity. General initial-sync liveness is not established.

Trusted ingress is the node-selected enum P2P, AUTHENTICATED_RPC or LOCAL_IMPORT,
never a field supplied in HeaderRecord. P2P header admission uses the stated
presync/minimum-work reference. Authenticated local RPC/import may bypass only
that P2P minimum-work gate, not byte caps, route, proof or actual child context.
No peer NoBan/min_pow_checked/known-header permission waives those checks.
Unknown anchor/configuration is unavailable; active-tip guesses are forbidden.

## 11. D04 resource/admission proposal

These are explicit provisional local policies, not measured performance facts
or adopted consensus/peer-ban rules. Local overload/timeouts are availability
outcomes, not proof that a child is consensus-invalid.

| Boundary | Candidate cap / behavior |
| --- | --- |
| Header/proof buffering | HeaderRecord<=10362; proof<=10205; tx<=8192; all CS bounds before loops/payload reads. Batch16, payload165857 =1+16*(4+10362). |
| Complete full/compact/disk payload | <=4000000 before variable buffering. A disk outer prefix is12 additional bytes; child current weight/full validation remains independent. blocktxn requests<=500037 and responses<=4000000 use the same bounded body-payload pool. |
| Binary in-flight payloads | Shared global pool: at most16 payloads<=4000000 each for full/compact, blocktxn request/response, fallback full blocks, decoded RPC/proposal/template views and disk/import frames. At most2 slots per peer; local import at most2 globally and decoded RPC at most2 globally, all debited from the SAME16 slots. Header batches use a separate pool: at most2 per peer/32 globally. No unbounded partial-message queue or uncharged copy. |
| Proof validation concurrency | At most2 active validations per peer and8 globally; pending canonical records at most8 per peer and64 globally. Pending record bytes<=663168 globally, active bytes<=82896; shared ownership/copies must be charged, not hidden outside pools. Reject/defer on exhaustion. |
| Local receive deadline | 60 seconds per incomplete candidate payload; cancellation releases its bounded buffers and gives no validity/credit. It is not a block-time or consensus rule. |
| RPC front end | Header hex bound20724; full/proposal hex8000000. Separate ENCODED body pool: at most1 per authenticated connection and2 globally, each<=8001024 before JSON/hex accumulation (total16002048 bytes). Decoded binary views consume the shared16-slot pool. JSON/native structures remain additional unmeasured costs; no unbounded RPC batch queue. |
| Hash work per AUX proof | Core predicates<=65 H2/TH2: Hc1, leaf1, slot1, txid1, auxiliary30, parent branch30, parent header1. A stored/admitting/synchronization receipt REQUIRES E, one additional TH2 (total66). A non-admitting call that emits no receipt may omit E. Excludes constant tag/profile/config setup; no CPU/RSS/allocator claim. |

The shared binary receive pool accounts for at most64000000 bytes and the
separate header-batch pool5307424 bytes. These are NOT a total peak estimate.
The separate encoded-RPC pool adds<=16002048 bytes; pending/active canonical
record pools add<=663168/82896 bytes when copied. Decoded RPC/import/fallback
buffers already debit the shared binary pool, not an unbounded extra pool.
Referenced larger owner buffers remain charged until released; duplicate copies
cannot escape a cap. Parser/native/JSON/interpreter structures and retained
presync units are additional costs for future allocator review. These are
accounting assumptions, not peak-memory proof.
For the65 core hashes, first H2 preimages total14373 bytes and second passes
2080 bytes. Required E adds a64+10362=10426-byte first preimage plus32 bytes;
combined admitting total26911 across both passes, excluding SHA padding and
constant setup. These analytical counts are not timing/native allocation proof.
Every presync/redownload/RPC/import path shares the same record/proof caps;
none may bypass them through trusted/min-work/known-header flags.
Unbounded archive growth and restart revalidation are separate operational costs,
not solved by those in-memory limits.

## 12. D05/D07 exact index association, persistence and recovery

Keep the pinned
[CDiskBlockIndex encoding](https://github.com/andaluzcoin/andaluzcoin/blob/4c98bfa88c4c45014677c7e9b2fec53459b000aa/src/chain.h#L340-L371)
byte-for-byte: no appended evidence pointer/flag, and no proof meaning inferred
from native validity/HAVE_DATA bits. The deterministic association is:
under the trusted ledger data root, b1/binding.bin stores BIND1;
b1/<rawhex(K)>/<rawhex(Hc)>.bev stores the exact evidence sidecar from section10.
rawhex is64 lowercase raw-digest hex characters with NO display reversal.
Unknown/missing sidecar means evidence unavailable, not an authenticated AUX
header reconstructed from the index. The stored sidecar Hc/E/record and filename
must all match; reverify the complete record and current applicable context
before in-memory evidence-ready/candidate-work eligibility.

BIND1 = ASCII(ALUZBLD1)[8]||K[32]||H:u32||GenesisHash[32]||
BeforeMask:u8(1)||AfterMask:u8(2)||EOF, exactly78 bytes.
It is durably initialized only for a reviewed empty/migrated B1 ledger store.
An existing index with missing binding requires explicit migration/recovery
review; never silently initialize it from another CFG1.
K, H, genesis and monotone route ordering must match on every startup/profile.
A conflicting config cannot retain old index/work and restore DIRECT after AUX.
The local admission threshold is not part of this immutable binding.
Migration of today's data/network representation is not implemented or adopted.

Selection policy: keep the FIRST fully checked, durably committed valid record
for Hc. Independently valid A2 is an alternative receipt without extra work;
invalid A2 leaves A1/child validity intact. Lost/corrupt evidence can be repaired
by fully checking and atomically persisting A2, with no second work increment.
A separately submitted permitted DIRECT repair is checked independently;
startup never invents that route merely because proof data is missing.

Required proposed storage state machine:
1. Decode/verify one immutable record/context with no authoritative side effects.
2. Write/seal the complete sidecar at its deterministic Hc key and obtain durable
   file-and-directory acknowledgement before publishing evidence-ready/work.
   Concurrent first-writer selection is serialized per Hc; losing valid writers
   recheck the selected immutable sidecar instead of changing accepted work.
3. Durably write the unchanged index encoding and then publish in-memory
   evidence-ready/once-only work eligibility. If index already exists, proof
   repair is still independently checked and durable before eligibility.
4. On crash/restart, reconcile orphan sidecars/index entries. Reverify evidence
   and applicable ancestry/context before restoring candidate-work eligibility;
   missing/corrupt data remains unavailable/reacquire, never implicit DIRECT
   work or permanent child invalidity. Current-clock RETRY_TIME or a new local
   admission threshold cannot erase historical proof/work facts. Storage failures
   never waive checks.

Current
[flush/index code](https://github.com/andaluzcoin/andaluzcoin/blob/4c98bfa88c4c45014677c7e9b2fec53459b000aa/src/validation.cpp#L2778-L2799)
does not establish these guarantees: one flush failure is logged before index
writing continues. B1's required state machine needs independent crash/error
tests; no existing atomic proof-storage guarantee is claimed.

Retain ALL selected HeaderRecord sidecars, AUX and DIRECT, when pruning child
body/undo data. Missing DIRECT evidence can be repaired only by independently
checked explicit resubmission; it is not assumed from six index fields.
Archive cost is up to10362+76 bytes per header plus binding78 per ledger.
This disk/revalidation/liveness cost needs independent analysis before adoption.
Pruned child bodies remain separately unavailable for connection/reorg; retained
validity/work is not body or proof availability.

Full/raw reads, restart, import, reindex and reindex-chainstate must use the
appropriate exact B1 views and evidence association; no C80-first skip or index
load's current direct-PoW assumption can authenticate AUX work.
[Current connection warnings](https://github.com/andaluzcoin/andaluzcoin/blob/4c98bfa88c4c45014677c7e9b2fec53459b000aa/src/validation.cpp#L2292-L2317)
require that audit. UTXO/script assumevalid is no B1 proof shortcut.
Current source code does not implement any of this proposal.

## 13. D06 monotone modes, compatibility and withdrawal

B1 permits ONLY the immutable ledger-wide DIRECT→AUX boundary in section5.
H is an unallocated trusted parameter. BOTH, AUX→DIRECT and profile-dependent
mode/slot resets are rejected configurations, including during recovery.
This restricts the earlier exploratory hybrid scenarios because of section8's
concrete one-solve/two-sequential-child counterexample; it is not evidence that
a general hybrid policy is safe. A body-only marker ban or immediate-parent
filter is insufficient for bare-header credit. Larger authenticated DIRECT
evidence or work-domain-separation alternatives need a different exact review.

AUX permits Hc above its own target when parent work meets that target.
Old nodes require direct Hc work; adopting such a block is a consensus hard fork.
New wrappers/storage require a migration/compatibility design even when an Hc
happens to meet direct PoW. Rolling back to an old binary after the first
parent-only-work accepted child is unsafe without separate chain/data recovery.
No old-binary downgrade, automatic mode reset, signaling mechanism, real H,
official hard-fork deployment or operational rollback command is selected.

Pool withdrawal changes neither route nor target because time passes.
Before H, miners must produce valid DIRECT work. At/after H, AUX disappearance
does not enable DIRECT, a recovery block or a wall-time difficulty escape.
This knowingly sacrifices hybrid fallback; liveness/participation remains a
critical open operational/economic gate. The
[work/recovery limits](andaluzcoin-auxpow-work-recovery.md#10-decision-log-and-remaining-production-gates)
remain. No actual hashrate, pool commitment or security budget is claimed.

## 14. D01-D08 consequences and rejected alternatives

| Choice | Proposed rationale / cost / alternative |
| --- | --- |
| Pure C80 identity, proof excluded | Avoid direct feedback cycles; requires immutable evidence receipts and every new view. Including the completed parent proof in Hc is not a free cache fix. |
| Stable trusted ND1/K | Separates intended ledger context outside child-version IDs; needs authoritative origin/namespace configuration. Genesis/name alone and unchecked prover labels are rejected substitutes. |
| Tagged leaf/nodes; ledger-only hash slot | Exact framing and stable same-ledger slot across profiles; new non-Namecoin rules need independent review. Legacy LCG/ID reuse is rejected for B1, not declared universally unsafe. |
| One common-family record | Prevents two accepted roots/profiles within one parent carrier; raw whole-stripped-byte scanning can reject accidental marker occurrences and restrict tooling. |
| Stripped proof transaction/P80 only | Limits carried unused witness/parent policy ambiguity; proves neither actual witness absence nor full parent consensus. Witness-carry and named-parent validation require separately specified evidence. |
| Strict limits, proof-bearing views and retained sidecars | Bound local work and preserve proof availability; reduce payload flexibility and increase relay/storage/restart costs. No adequate pool support or performance is demonstrated. |
| Immutable monotone fixed-height mode | Removes the demonstrated same-history AUX→DIRECT amplification path; loses hybrid fallback and still depends on explicit cryptographic/ancestry assumptions. Does not settle signaling, governance or withdrawal incentives. |
| Current D08 | Owner review of this exact candidate, independent security/implementation/economic/operational evidence and explicit adoption remain required. |

No D01-D08 production gate is closed by choosing provisional text.
Return this package for separate exact-spec review before any dependent real
ALUZ parser, consensus, networking or storage implementation.
Routine research publication may follow #103's standing all-green workflow;
it does not adopt B1 or authorize operational evidence gathering.

## 15. Independent evidence plan: planned, not executed

All V rows below are **UNIMPLEMENTED/UNEXECUTED acceptance requirements**.
Future reference builders/decoders must be independent of the candidate
implementation and each other's encoder/oracle where independence is claimed.
Pin source/build/configuration, raw bytes/seals/offsets, trusted ND1/CFG1,
verdict layer and expected versus actual results.
Source-generated regtest, historical mined, malformed and hypothetical schedule
fixtures are distinct provenance classes. No historical corpus is promised.

| Dossier V | Exact future acceptance examples / evidence |
| --- | --- |
| V01 | Canonical manifest/tag/ND1<=8271/CFG1<=8432/BIND1=78/record/view literals and offsets; DIRECT155, AUX388 minimum, AUX10362 maximum; truncation/suffix/nonminimal CS, unknown magic/reserved/route/profile; exact roundtrips/seals. |
| V02 | Wrong expected K/P/Hc leaf, absent/malformed commitment, extra raw marker in ANY stripped field, marker at wrong parsed location, wrong output value/push/length; no unchecked domain labels or circular preimages. |
| V03 | Numeric negative/zero/overflow/above-limit target; hash exactlyT andT+1, incorrect expected bits before accepted credit, parent nBits deliberately different/ignored, wrong endian/display hash. |
| V04 | Repeated Hc/proof and concurrent A1/A2 add work once; different parent-branch depths/siblings and sequential AUX/profile hypotheses; demonstrate rejected hybrid AUX C1→DIRECT C2=P80 amplification, monotone restrictions and explicit fixed-point assumptions. Do not claim fork-global uniqueness. |
| V05 | Unknown/failed parent/ancestor and properly invalid child, exact genesis, known-header/data and trusted-min-work shortcuts; each applicable path still needs correct evidence; no malformed-AUX→DIRECT fallback. |
| V06 | Every length/count cap at cap±1, huge prefix before allocation/loop, batch16/17 and payload bound, presync/redownload proof screening vs provisional/accepted work, per-peer/global queues/timeouts and explicit release of cancelled buffers. |
| V07 | Full/compact record and SHA256(C80\|\|nonce) wtxid short IDs; prefill/request delta overflow/duplicates/range, response Hc/count/order/wtxid binding, missing proof not supplied by blocktxn, independently checked full A2 fallback without poisoning Hc. |
| V08 | Canonical142-byte CB and explicit64-byte exclusion; input/null-outpoint/output/script/value-sum failures; changed witness with same stripped txid is NOT detected by this proof; hidden duplicated Merkle subtree cannot be globally certified by one branch. |
| V09 | Bad A1 then valid A2 and reverse; retained valid A1 survives invalid A2; valid alternative repairs unavailable evidence only after full verification; invalid child expected bits remain invalid. |
| V10 | Immutable bytes versus swapped A2 and attacker-recomputed E; idempotent commit; ConfigID is not a full ruleset fingerprint and current context is reevaluated. K/H/BIND1 conflicts stop; behind-clock/local-threshold changes do not erase historical work. Retry/reconnect/assumevalid never promote unseen evidence. |
| V11 | Different trusted namespaces/origins/challenges with shared genesis; missing custom manifest; unchanged wrong-K record rejects, but re-enveloped DIRECT C80 may pass in two otherwise equivalent contexts without new work. AUX leaf binds K/P. Stable K/slot across profiles, index i+2^h rejects; collisions acknowledged. |
| V12 | Unchanged native index bytes plus exact BIND1/sidecar/path association; wrong filename/K/Hc/E, missing/conflicting binding, interrupted writes/flush errors/crash cuts, orphan reconciliation and startup/import/reindex/reindex-chainstate evidence revalidation. |
| V13 | Pruned child body with retained AUX proof, missing/corrupt sidecar/reacquisition and eligible-work accounting; unavailable proof/body must not become invalid child or implicit direct work. |
| V14 | Proposal/template never become accepted evidence; submit views require work. Template child-vector cap/cap+1 reserves155 DIRECT or10362 AUX and includes its153-byte prefix; a maximum valid completed proof still fits. RPC/body/EOF bounds at every view. |
| V15 | Parent-derived h; H-1/H/H+1 within the native range; H=0/H>INT32_MAX reject; invalid/negative/INT32_MAX parent heights reject before addition/conversion; pprev=INT32_MAX-1 permits h=INT32_MAX and its next child rejects; exact genesis height0/DIRECT exception; fixed child across active-tip changes, same-height branches, unknown parent/clock retry without active-tip dispatch. |
| V16 | Only DIRECT→AUX allowed; reject BOTH/reverse/profile-reset configurations, persisted-H changes and unknown profiles; old/new-node disagreement/rollback after parent-only work; no pool-exit DIRECT fallback or wall-time target change. |
| V17 | Byte-identical current genesis/PoW/DAA/subsidy/identity/network/descriptor-only behavior before any authorized later implementation; no adoption inferred from this research. |
| V18 | Independent exact-contract reviewer/implementations, resource/fuzz/concurrency/security and economic/operational evidence by layer; all omissions named, no general mining/security certification. |

A numeric-work oracle must exclude the simplified fuzz-determinism route and
record the actual numeric result plus expected verdict per EXACT fixture and
applicable build/configuration/parameters. Merely executing or covering a named
function is insufficient. A Namecoin assertion is not a B1 verdict.
No test solely mirroring this documentation is introduced.

## 16. Completion versus adoption

This milestone completes a proposed contract/evidence-plan artifact only.
Its report must state actual document/source/link/hash/byte-arithmetic/scope
checks and CI obtained; this list is not a runtime/performance/security pass.
All literal B1 choices, official mappings and the exact specification return
for separate critical review. No parser/integration is authorized by publication.

Issue → isolated documentation branch → report/PR → independent technical review
and exact-head CI → permitted regular merge → successful actual-merge master CI
→ verified annotated research tag → final report/closure remains the workflow.
Failed checks or actual adoption require separate owner disposition.
Mainnet remains **NO-GO** with 21 unchecked launch gates and D01-D08 OPEN.

See the [B1 specification review](andaluzcoin-auxpow-b-specification-review.md)
for unresolved findings and next-phase eligibility; no production rule is adopted.
