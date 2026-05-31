# Andaluzcoin Chain Specification

Status: v0.1 baseline
Project: Andaluzcoin
Ticker: ALUZ
Base codebase: Bitcoin Core-derived fork

This document records the current Andaluzcoin network, consensus, wallet, and launch parameters. It is intended to be a stable technical reference for developers, testers, contributors, and future release planning.

Andaluzcoin is a Bitcoin-derived proof-of-work cryptocurrency created as a culture/community coin. It inherits core blockchain functionality such as peer-to-peer transactions, mining, decentralized consensus, and operation without a central authority.

Andaluzcoin is not intended to compete with Bitcoin as digital gold. It is designed as a meme/community coin that can still function as peer-to-peer money.

---

## 1. Identity

| Field           | Value                                                                |
| --------------- | -------------------------------------------------------------------- |
| Name            | Andaluzcoin                                                          |
| Ticker          | ALUZ                                                                 |
| Main unit       | ALUZ                                                                 |
| Milli unit      | mALUZ                                                                |
| Micro unit      | µALUZ                                                                |
| Base codebase   | Bitcoin Core-derived                                                 |
| Consensus model | Proof of Work                                                        |
| Primary purpose | Culture/community coin with working peer-to-peer money functionality |

---

## 2. Supported Networks

For the v0.1 baseline, Andaluzcoin focuses on mainnet and regtest.

| Network  | Status                      | Notes                                             |
| -------- | --------------------------- | ------------------------------------------------- |
| Mainnet  | Enabled                     | Primary custom Andaluzcoin network                |
| Regtest  | Enabled                     | Used for local development and functional testing |
| Testnet  | Present but not productized | Deferred for v0.1                                 |
| Testnet4 | Present but not productized | Deferred for v0.1                                 |
| Signet   | Present but not productized | Deferred for v0.1                                 |

Regtest is intentionally kept close to Bitcoin behavior where practical. This reduces unnecessary test breakage and keeps the functional test framework stable.

---

## 3. Mainnet Network Parameters

| Parameter                   | Value               |
| --------------------------- | ------------------- |
| Network name                | main                |
| Default P2P port            | 29444               |
| Default RPC port            | 29443               |
| Message start / magic bytes | 0xb6 0xa9 0x64 0x58 |
| Bech32 HRP                  | aluz                |

---

## 4. Mainnet Address Encoding

| Encoding                    | Value       |
| --------------------------- | ----------- |
| P2PKH prefix                | 55          |
| P2SH prefix                 | 117         |
| WIF / secret key prefix     | 183         |
| Extended public key prefix  | 04 B2 47 46 |
| Extended private key prefix | 04 B2 43 0C |
| Bech32 HRP                  | aluz        |

These values are defined in:

src/kernel/chainparams.cpp

---

## 5. Mainnet Consensus Parameters

| Parameter                      | Value                                                            |
| ------------------------------ | ---------------------------------------------------------------- |
| PoW algorithm                  | SHA256d                                                          |
| Subsidy halving interval       | 210,000 blocks                                                   |
| Target block spacing           | 10 minutes                                                       |
| Difficulty adjustment interval | 2016 blocks                                                      |
| Difficulty adjustment timespan | 14 days                                                          |
| Minimum difficulty blocks      | false                                                            |
| No retargeting                 | false                                                            |
| BIP94 enforcement              | false                                                            |
| PoW limit                      | 000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff |
| Coinbase maturity              | 100 blocks                                                       |
| Initial block reward           | 50 ALUZ                                                          |
| Approximate max supply         | 21,000,000 ALUZ                                                  |
| Premine / dev fund             | none                                                             |

Andaluzcoin mainnet uses a Litecoin/Dogecoin-style maximum proof-of-work target to support practical early community mining while retaining Bitcoin-derived proof-of-work consensus behavior.

---

## 6. Genesis Block

Current Andaluzcoin mainnet genesis parameters:

| Field             | Value                                                            |
| ----------------- | ---------------------------------------------------------------- |
| Timestamp message | Andaluzcoin 30/Jan/2026 Viva Al-Andalus                          |
| nTime             | 1769731200                                                       |
| nBits             | 0x1e00ffff                                                       |
| nNonce            | 549347                                                           |
| Version           | 1                                                                |
| Genesis reward    | 50 ALUZ                                                          |
| Merkle root       | 14a3ed7e9a74a76a935c96b7101d9e5cd4c974534838d77c48bdadb15e103e2a |
| Genesis hash      | 000000f7dca7651a1397fd0bc99b2a456dbb2d23470834b6290aadec4b46d15c |

The genesis block is asserted directly in the chain parameters source file.

Important note: if the genesis values in this document ever differ from src/kernel/chainparams.cpp, the source code is the authority.

---

## 7. Buried Deployments and Softfork Policy

For Andaluzcoin mainnet v0.1, buried deployments are treated as active from height 1.

| Deployment              | Mainnet value |
| ----------------------- | ------------- |
| BIP34 height            | 1             |
| BIP65 height            | 1             |
| BIP66 height            | 1             |
| CSV height              | 1             |
| Segwit height           | 1             |
| Min BIP9 warning height | 1             |

Taproot is configured as always active for Andaluzcoin mainnet v0.1.

| Taproot field             | Value         |
| ------------------------- | ------------- |
| Bit                       | 2             |
| Start time                | ALWAYS_ACTIVE |
| Timeout                   | NO_TIMEOUT    |
| Minimum activation height | 0             |
| Threshold                 | 1815          |
| Period                    | 2016          |

The test dummy deployment is configured as never active.

---

## 8. Chain Assumptions

Because Andaluzcoin is a new chain, mainnet does not currently use historical Bitcoin chain assumptions.

| Field                       | Value        |
| --------------------------- | ------------ |
| Minimum chain work          | empty / zero |
| Default assume valid        | empty / zero |
| AssumeUTXO data             | empty        |
| Chain transaction data time | 0            |
| Chain transaction count     | 0            |
| Chain transaction rate      | 0.0          |
| Assumed blockchain size     | 0            |
| Assumed chain state size    | 0            |

---

## 9. Seeds and Peer Discovery

For the current v0.1 baseline:

| Field       | Status  |
| ----------- | ------- |
| DNS seeds   | cleared |
| Fixed seeds | cleared |

This means mainnet seed infrastructure is not yet productized. Public peer discovery should be added later when reliable Andaluzcoin seed nodes are available.

Future seed-node work should be handled in a separate pull request.

---

## 10. Wallet Direction

Current Andaluzcoin wallet direction:

| Wallet type               | Status                               |
| ------------------------- | ------------------------------------ |
| Descriptor wallet         | Preferred                            |
| SQLite wallet backend     | Preferred                            |
| Legacy wallet             | Not preferred for future development |
| Berkeley DB legacy wallet | Deprecated direction                 |

The project direction is to prefer modern descriptor wallets backed by SQLite and avoid long-term dependency on legacy Berkeley DB wallets.

Legacy wallet support may exist temporarily during development or compatibility work, but it should not be the preferred long-term wallet direction.

---

## 11. Development and Testing Policy

The current v0.1 baseline was created after a green CI and green test-each-commit milestone.

Important validation areas include:

* Mainnet chain parameters
* Genesis block validation
* Proof-of-work behavior
* Regtest compatibility
* Functional test framework behavior
* Wallet configuration behavior
* CI build stability

Documentation-only pull requests should not change runtime behavior.

Consensus, network, wallet, or launch parameter changes must be reviewed carefully and validated with targeted tests.

---

## 12. Maintenance Policy

For future development:

* Keep one theme per pull request.
* Avoid mixing upstream Bitcoin sync work with Andaluzcoin-specific cleanup.
* Tag stable milestones after large green PRs.
* Merge Bitcoin security fixes in isolated PRs.
* Batch non-critical upstream updates separately.
* Keep this document synchronized with src/kernel/chainparams.cpp.
* Treat source code and tests as the final authority.

---

## 13. Source of Truth

This document is a human-readable technical reference.

For actual consensus and network behavior, the source code remains the final authority.

Primary files:

src/kernel/chainparams.cpp
src/chainparams.cpp
src/chainparams.h
src/consensus/params.h
src/test/
test/functional/

If this document conflicts with the source code, update this document or fix the source code intentionally in a separate reviewed pull request.
