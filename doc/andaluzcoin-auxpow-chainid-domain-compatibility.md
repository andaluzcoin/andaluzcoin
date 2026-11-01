# AuxPoW chain-ID encoding and network-domain compatibility research

## 1. Decision and evidence boundary

**v0.2.78 is research only. Public economic mainnet remains NO-GO.**
No official ALUZ chain ID, version-bit layout, domain format, parent chain,
proof parser, replay policy or activation is selected. All 21
[mainnet readiness gates](andaluzcoin-mainnet-readiness.md) remain unchecked.
The descriptor-wallet-only policy and all production behavior are unchanged.

This follows [issue #91](https://github.com/andaluzcoin/andaluzcoin/issues/91)
and the first follow-up in the
[v0.2.77 decision package](andaluzcoin-auxpow-candidate-specification.md#15-conclusions-sources-and-next-milestones).
Frozen ALUZ baseline: `989ba3cb5fb00d1e145d3a3ee5974839eb8fd442`, annotated
`v0.2.77-auxpow-spec-chainid-compatibility-research`.
External code was inspected at the immutable revisions below on 2026-11-01 UTC.
An immutable observation describes that source, not present operation.

Status vocabulary:

- **ALUZ CURRENT**: unmodified baseline source, not an AuxPoW implementation.
- **PINNED PRECEDENT**: external source at the exact linked revision.
- **DERIVED**: arithmetic or control-flow consequence, not a live observation.
- **SYNTHETIC MODEL**: offline examples, not real block/proof validation.
- **OPEN**: unresolved choice or missing evidence requiring separate review.

## 2. ALUZ baseline and compatibility surface

ALUZ CURRENT: [CBlockHeader](../src/primitives/block.h) has signed `int32_t
nVersion` and the existing six-field, 80-byte serialization. There is no
AuxPoW attachment or auxiliary chain-ID interpretation.
[versionbits.h](../src/versionbits.h) defines top bits `0x20000000`, mask
`0xe0000000`, and **29** available versionbits. In
[versionbits.cpp](../src/versionbits.cpp), `ComputeBlockVersion` starts with
those top bits and adds signaling masks; [miner.cpp](../src/node/miner.cpp)
uses the result. These source facts do not activate an ALUZ auxiliary mode.

Copying another chain's high-word ID or bit-8 flag onto this layout can
reinterpret current fields. Review must cover header identity, unknown-bit
behavior, buried-version rules, signaling, serialization, validation entry
points and old-node compatibility. Existing network magic, genesis, ports,
PoW/DAA, subsidy, seeds and wallets are unchanged. In particular,
[wallet.cpp](../src/wallet/rpc/wallet.cpp) rejects `createwallet` with
`descriptors=false`; this research does not weaken that policy.

## 3. Expanded immutable network inventory

PINNED PRECEDENT; **non-exhaustive**, not an allocation registry or support list.
IDs below are **configured/expected** IDs; section 5 distinguishes effective
header extraction. Strict child checks and strict parent checks are separate.

| Project and network | Configured SHA256d ID | Child-ID comparison | Parent same-ID rejection | Immutable parameter evidence |
| --- | --- | --- | --- | --- |
| Namecoin main | 1 | Strict for nonlegacy headers | Strict | [chainparams.cpp:179](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/kernel/chainparams.cpp#L179) |
| Namecoin testnet | 1 | Disabled by strict=false | Disabled by strict=false | [chainparams.cpp:345](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/kernel/chainparams.cpp#L345) |
| Namecoin signet | 1 | Strict for nonlegacy headers | Strict | [chainparams.cpp:634](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/kernel/chainparams.cpp#L634) |
| Namecoin regtest | 1 | Strict for nonlegacy headers | Strict | [chainparams.cpp:742](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/kernel/chainparams.cpp#L742) |
| Huntercoin main | 6 | At height >=1, except INT_MAX path | Enabled on main | [main.cpp:1701](https://github.com/chronokings/huntercoin/blob/6aa3da0bbe4a7d16352c02f07369a00ae78fcf59/src/main.cpp#L1701) |
| Huntercoin test | 6 | Same height/exception rule | Disabled on test | [same network-independent ID function](https://github.com/chronokings/huntercoin/blob/6aa3da0bbe4a7d16352c02f07369a00ae78fcf59/src/main.cpp#L1710) |
| Myriad main | 90 | Disabled by strict=false | Disabled by strict=false | [chainparams.cpp:76](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/chainparams.cpp#L76) |
| Myriad test | 90 | Disabled by strict=false | Disabled by strict=false | [chainparams.cpp:282](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/chainparams.cpp#L282) |
| Myriad regtest | 90 | Disabled by strict=false | Disabled by strict=false | [chainparams.cpp:451](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/chainparams.cpp#L451) |
| ALUZ networks | Unselected / not implemented | No auxiliary ID rule | No auxiliary proof | Baseline in section 2 |

Unknowns are not filled by analogy: Namecoin's
[testnet4 class](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/kernel/chainparams.cpp#L435)
contains no AuxPoW-field assignments and includes a FIXME. Its auxiliary ID,
strictness and start fields are **not established here**. Huntercoin regtest
was not established in this historical source audit. No inferred row proves
that a network is supported or operational.

SHA256d routing is source-traced, not inferred from project names:
Namecoin's [pureheader.cpp](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/primitives/pureheader.cpp#L11)
uses header serialization hashing;
Huntercoin's [GetPoWHash](https://github.com/chronokings/huntercoin/blob/6aa3da0bbe4a7d16352c02f07369a00ae78fcf59/src/main.h#L1113)
routes SHA256d to `GetHash`, whose
[util.h helper](https://github.com/chronokings/huntercoin/blob/6aa3da0bbe4a7d16352c02f07369a00ae78fcf59/src/util.h#L612)
performs two SHA256 calls; Myriad's
[pureheader.cpp](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/primitives/pureheader.cpp#L17)
routes SHA256d to `GetHash`/`SerializeHash`.
The preceding [source ledger](andaluzcoin-auxpow-candidate-specification.md#3-immutable-primary-source-ledger)
traces their double-SHA256 helpers. Scrypt and other algorithms are outside
this inventory. Mining/pool participation and full interoperability are UNKNOWN.

## 4. Signed version encoding is not an unsigned high-word field

PINNED PRECEDENT: Namecoin
[pureheader.h:87-117](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/primitives/pureheader.h#L87)
uses signed `nVersion / 65536` for ID and signed `%256` for base version.
Huntercoin's [GetChainID](https://github.com/chronokings/huntercoin/blob/6aa3da0bbe4a7d16352c02f07369a00ae78fcf59/src/main.h#L1099)
also divides signed `int`; modeling it as 32 bits is an explicit historical
platform assumption. Myriad's
[GetChainId](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/primitives/pureheader.h#L123)
divides signed `int32_t`, but its base accessor masks low eight bits instead.

DERIVED: C++ division truncates toward zero; Python `//` floors. Neither
unsigned `uint32(version)>>16` nor floor division models negative inputs.
The following literal rows were independently executed with GCC 13.3 C++17:

| Signed version | uint32 hex | Signed /65536 | Unsigned upper16 | Floor /65536 |
| --- | --- | --- | --- | --- |
| -2147483648 | 80000000 | -32768 | 32768 | -32768 |
| -65537 | fffeffff | -1 | 65534 | -2 |
| -65536 | ffff0000 | -1 | 65535 | -1 |
| -65535 | ffff0001 | 0 | 65535 | -1 |
| -1 | ffffffff | 0 | 65535 | -1 |
| 65536 | 00010000 | 1 | 1 | 1 |
| 536870912 | 20000000 | 8192 | 8192 | 8192 |
| 536871168 | 20000100 | 8192 | 8192 | 8192 |
| 2147483647 | 7fffffff | 32767 | 32767 | 32767 |

For `version=-65532` (`ffff0004`), signed extraction gives ID0 and base -252,
whereas a low8 mask gives base4. Combining signed `(-1 * 65536) | 4` therefore
does not round-trip ID -1. A negative remainder also retains sign bits:
`(-1 % 65536) | 65536` in C++ is -1, not a clean high-word replacement.

Namecoin's [SetBaseVersion](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/primitives/pureheader.cpp#L16)
asserts base1..255 and no preexisting AuxPoW flag, then ORs a signed
`chainId * 65536`; its setter is not an ID-range validator. Signed overflow
must not be treated as defined wraparound. The mathematical encoding
`ID*65536 + low16`, with nonnegative ID and low16 in 0..65535, fits int32
for ID0..32767. ID32768 exceeds INT32_MAX even at low16=0. The offline model
rejects it before encoding. This bounded domain is **not** an ID allocation or
claim all such combinations are valid upstream headers. Negative IDs, setters,
platform assumptions and contextual version checks need separate treatment.

## 5. Signaling, flags and configured versus effective IDs

PINNED PRECEDENT: bit8 is the AuxPoW flag in
[Namecoin](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/primitives/pureheader.h#L25)
and [Myriad](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/primitives/pureheader.h#L58).
Huntercoin additionally uses bit9 to select Scrypt
([main.h:985](https://github.com/chronokings/huntercoin/blob/6aa3da0bbe4a7d16352c02f07369a00ae78fcf59/src/main.h#L985));
its `CHAIN_END` constant is not a mask in `GetChainID`.

DERIVED: the BIP9 predicate `(bits & 0xe0000000)==0x20000000` overlaps
nonnegative high-word IDs **8192..16383**. Bits16..28 affect extracted ID;
bits0..15 share base/flag space, including bit8. Example `0x20000100`
has top001, bit8 and extracted ID8192 simultaneously. A reused layout needs
an explicit rule; an independent ID integer alone cannot solve these conflicts.

Namecoin's [miner.cpp:145](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/node/miner.cpp#L145)
uses `SetBaseVersion(4, ID)` and comments out `ComputeBlockVersion`.
Its [versionbits.h](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/versionbits.h#L21)
retains the top pattern and declares `VERSIONBITS_NUM_BITS=5` for warning
enumeration with a BIP323 comment. That constant is not a general rejection
rule for higher configured deployment bits; actual deployment masks must be
traced separately. Do not transplant ALUZ's layout by analogy. Adding `0x20000000` to the
Namecoin-style ID1 example `0x00010104` yields extracted ID8193, not1, and
conflicts with a strict ID1 check. This is a compatibility observation,
not a defect claim or an instruction to change ALUZ signaling.

Myriad's [miner.cpp:119](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/miner.cpp#L119)
passes `ComputeBlockVersion` and configured ID90 to
[SetBaseVersion](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/primitives/pureheader.cpp#L52),
which ORs them. Its [version computation](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/validation.cpp#L1781)
starts with `0x20000000`; its [versionbits.h](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/versionbits.h#L14)
declares eight warning bits and documents an intended low-eight-bit signaling
convention. This is not a general rejection rule for higher deployment bits:
[deployment masks](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/versionbits.cpp#L184)
use configured positions, including
[testdummy bit28](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/chainparams.cpp#L156).
Source-derived example:
`0x20000000 | (90*65536) | 256 = 0x205a0100`, whose signed extraction is
**8282**, not90. The [auxpow RPC](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/rpc/auxpow_miner.cpp#L133)
returns actual `GetChainId()`. Accordingly, the earlier inventory's ID90
denotes configuration, not a guarantee of effective ID90 for every version.
Strict checks are false in the three parameter sets. No live block, pool
configuration or exploit was tested; full historical behavior remains unaudited.

## 6. What the strict checks actually cover

Namecoin [CheckProofOfWork](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/validation.cpp#L1886)
checks configured child ID for nonlegacy headers only when strict=true.
`IsLegacy` means **full version exactly1**, not every direct-work header.
The no-proof route still checks direct child PoW; flag/proof mismatches fail.
An AuxPoW-flagged parent is rejected independently of strictness.
[CAuxPow::check](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/auxpow.cpp#L41)
separately rejects equal parent/child extracted IDs only when strict=true.
Parent work is checked against **child** bits; this is not full parent-network
context validation.

Namecoin's [legacy-before rule](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/consensus/params.h#L266)
and [contextual rejection](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/validation.cpp#L4223)
do not imply AuxPoW-only mode: correctly encoded direct-work headers can
still take the ordinary route. Signed base versions also face buried-version
checks ([validation.cpp:4255](https://github.com/namecoin/namecoin-core/blob/942b14038f3ae704b6c2d50355de835d3ee92288/src/validation.cpp#L4255)).
Genesis and call-context exceptions require their own audit.

Huntercoin [main.cpp:1756](https://github.com/chronokings/huntercoin/blob/6aa3da0bbe4a7d16352c02f07369a00ae78fcf59/src/main.cpp#L1756)
enforces child ID after its start height except `INT_MAX`, rejects parent
AuxPoW/algorithm mismatch, and checks work against child bits. Its
[same-ID check](https://github.com/chronokings/huntercoin/blob/6aa3da0bbe4a7d16352c02f07369a00ae78fcf59/src/auxpow.cpp#L21)
is main-only. Myriad's [child check](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/validation.cpp#L1049)
and [parent-ID check](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/auxpow.cpp#L48)
both depend on strictness. The [early-AuxPoW rejection](https://github.com/myriadteam/myriadcoin/blob/35fa3b702864d9ac9e1fa257403f58b4f452fc3b/src/validation.cpp#L3362)
must not be read as proof of the adjacent comment's claimed post-start legacy
prohibition. These excerpts are not full acceptance specifications.

## 7. Network-domain and replay threat matrix

DERIVED / OPEN: a chain ID, genesis, network magic and commitment have different
roles. Current ALUZ headers commit to previous-block hash and Merkle root;
contextual validation, not a numeric label alone, anchors accepted history.

| Mechanism or case | What it establishes | What remains OPEN |
| --- | --- | --- |
| Numeric ID shared across networks | Inventory proves IDs are reused in these sources | No unique main/test/regtest binding or proof of actual replay. |
| Distinct numeric IDs | Potential namespace separation under a specified extraction rule | Slot collisions, signaling overlap and encoding ambiguity can remain. |
| Namecoin-style slot selection | At fixed height/nonce, IDs congruent mod 2^h collide; nonce cannot separate them | Slot distinction is not network authentication or replay protection. |
| Network magic | Framing distinguishes intended P2P traffic | It is not automatically included in an auxiliary commitment or offline proof. |
| Genesis identifier | Names a particular chain context when actually bound and checked | No binding follows merely from node configuration or a documentation label. |
| Commitment to child hash | Changing committed child bytes changes the expected commitment | Real transaction/Merkle validity, target and contextual child acceptance still required. |
| Strict parent != child ID | Rejects the particular equal-ID relation under the chosen decoder | Does not bind child network or fully validate parent-network consensus. |
| Non-strict historical policy | Omits specified ID checks while retaining other proof rules | Not automatically safe or unsafe for ALUZ; compatibility/security analysis required. |
| Explicit network domain in commitment | Could distinguish networks if canonical, required and checked everywhere | Exact format, migration, downgrade, omission and all entry-point behavior unresolved. |
| Same child bytes under different contexts | Synthetic examples can test an explicit context field's effect | Cannot conclude full-block replay is possible or prevented without real validators. |

Slot arithmetic and existing collision vectors remain in the
[v0.2.77 model](../test/functional/feature_andaluz_auxpow_chainid_spec.py).
No new slot function or network identity is proposed here.

## 8. Offline model and independent evidence

The [new stdlib test](../test/functional/feature_andaluz_auxpow_chainid_domain.py)
has eight methods: literal signed quotient/bit predicates, signed LE32 bytes,
negative remainder differences, bounded positive encoding, invalid domains,
signaling overlap (all 32768 nonnegative high-word IDs), fixed synthetic
domain hashes and field mutations. The test uses exact integer arithmetic,
rejects bools and out-of-domain inputs, and never evaluates signed overflow.

Two synthetic 32-byte genesis values are `00..1f` and `1f..00`; the child is
`42` repeated 32 times. The label is ASCII `ALUZ-AUXPOW-RESEARCH-ONLY` plus
NUL. SHA256d(label + genesis + child) has a fixed **90-byte** input:

| Synthetic genesis | Digest bytes in hex (not reversed display order) |
| --- | --- |
| 00..1f | a076cef2fb01bf1549dd75131fb0ff1777e9581163962b0ecf6b705ffd4ae308 |
| 1f..00 | 225fde6d4d13b73c2724d63320b28846a494654c20899dedd9f7dc3cfb94b4f2 |

These literal values were independently reproduced with OpenSSL 3.0.13,
not the Python test's hash routine. They illustrate the effect of an explicit
synthetic context on two fixed inputs. The label is not an ALUZ ID or wire
allocation. No real genesis, coinbase, proof, parent work, replay acceptance,
activation/reorg, miner or network validator is tested.

Reproduce the digest cross-check in a scratch shell with OpenSSL and xxd:

```sh
label=414c555a2d415558504f572d52455345415243482d4f4e4c5900
ga=000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f
gb=1f1e1d1c1b1a191817161514131211100f0e0d0c0b0a09080706050403020100
child=4242424242424242424242424242424242424242424242424242424242424242
for genesis in "$ga" "$gb"; do
  printf %s "$label$genesis$child" | xxd -r -p | openssl dgst -sha256 -binary | openssl dgst -sha256
done
```

For the signed arithmetic literals, compile this independent reference as
scratch C++17 with `g++ -std=c++17 -Wall -Wextra -Werror -pedantic ref.cpp`:

```cpp
#include <cstdint>
#include <iostream>
#include <limits>
int main()
{
    const int32_t versions[] = {INT32_MIN, -65537, -65536, -65535, -1,
        0, 255, 256, 65535, 65536, 0x20000000, 0x20000100, INT32_MAX};
    for (const auto v : versions) {
        const uint32_t u = static_cast<uint32_t>(v);
        const int32_t q = v / 65536;
        const int32_t floor = q - (v < 0 && v % 65536 != 0);
        std::cout << v << ',' << q << ',' << (u >> 16) << ',' << floor
                  << ',' << bool(u & 256) << ','
                  << ((u & 0xe0000000u) == 0x20000000u) << '\n';
    }
    for (const int64_t id : {0, 1, 8192, 32767, 32768}) {
        for (const int64_t low : {0, 256, 65535}) {
            const int64_t wide = id * 65536 + low;
            const bool fits = wide <= std::numeric_limits<int32_t>::max();
            std::cout << id << ',' << low << ',' << wide << ',' << fits << '\n';
        }
    }
}
```

This prints 13 signed boundary rows and 15 wide-encoding cases without an
out-of-range signed cast. The negative examples and configured/effective-ID
examples in sections 4–5 are also independently corroborated in the execution
report. Source checks, arithmetic references and synthetic hashes are different
kinds of evidence; none is an independent production consensus implementation.

## 9. Reproduction and runner contract

From a configured repository checkout:

```sh
python3 test/functional/feature_andaluz_auxpow_chainid_domain.py
build/test/functional/test_runner.py --jobs=1 feature_andaluz_auxpow_chainid_domain.py
build/test/functional/test_runner.py --jobs=1 --timeout-factor=40 feature_andaluz_auxpow_chainid_domain.py
build/test/functional/test_runner.py --jobs=1 --timeout-factor=40 --v2transport --usecli feature_andaluz_auxpow_chainid_domain.py
build/test/functional/test_runner.py --jobs=1 --timeout-factor=40 --previous-releases feature_andaluz_auxpow_chainid_domain.py
build/test/functional/test_runner.py --jobs=1 feature_andaluz_auxpow_chainid_domain.py feature_andaluz_auxpow_chainid_spec.py feature_andaluz_auxpow_feasibility.py
build/bin/test_bitcoin --run_test=pow_tests --log_level=test_suite
```

Rerun `cmake -S . -B build` if the generated functional-test directory has no
link for the new script. The child uses only stdlib and no node/RPC, sockets,
subprocesses, downloads, file operations, random inputs or mining. It accepts
only enumerated runner metadata and does not open metadata paths. Unknown or
abbreviated arguments, invalid timeout values and optimized Python reject;
test failures return nonzero and successful output is on stdout.
The registered runner still needs a configured build. Environment-specific
results, negative CLI checks, injected-failure check, independent source
review and CI status belong in the linked issue/PR execution report, not
assumed from these commands. Upstream source tests were read, not run.

## 10. Decision log and next gates

| Open choice / alternative | Recommendation for review, not selection | Acceptance gate |
| --- | --- | --- |
| ID width and signed vs unsigned decoder | Specify an exact domain before any allocation; never infer it from a toy constant | Independent encoding corpus including negative, boundary and overflow rejection cases. |
| Shared vs per-network ID | Audit configured and effective IDs and all network domains | Expanded source audit plus an explicit domain and replay threat model. |
| Strict vs permissive parent-child ID policy | Review extraction, parent version compatibility and rejection boundaries together | Exact positive/negative proofs and compatibility evidence, not an arithmetic predicate alone. |
| Version signaling and auxiliary discriminator | Specify coexistence or a reviewed migration; do not simply OR fields | Old/new-node, signaling, serialization, hash and all-entry-point vectors. |
| Genesis/domain bound in commitment vs relying on child context | Analyze canonical binding, downgrade and omission risks | Precise bounded proof specification and independent real-parser agreement. |
| Legacy/hybrid/AuxPoW-only mode | Preserve present rules until separately authorized | Contextual target/work, fork, activation, reorg and recovery review. |

Immediate production implementation remains **BLOCKED** on these choices and
independent security review. Research completion is not resolution of every
design question. Issue #91 requires a PR, reproducible evidence, required CI
and recorded owner/ChatGPT review before milestone closure or merge/tag.
Precise production proof/activation specification, independent parsers, DoS
budgets and mixed-mode chainwork/pool-exit studies remain separate follow-ups.
No outreach, deployment, live mining, activation or mainnet approval follows.
