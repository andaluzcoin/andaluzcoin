# Andaluzcoin mainnet readiness

**Status: PRELAUNCH / NOT APPROVED FOR PUBLIC ECONOMIC MAINNET.**
This is a documentation checklist, not a completed security audit or launch
approval. No speculative launch date is assigned. All gates below remain open;
owners/operators are **TO BE ASSIGNED**. Unknown evidence is a NO-GO.

Mainnet code defines which chain a node validates. It does not create public
bootstrap infrastructure, independent hash security, an operator SLA or an
economic ecosystem. More validating nodes do not produce blocks or supply hash
power. Engineering CI and local functional tests do not establish live mainnet
operation. No public seeds/bootstrap network has been approved here.

## Evidence boundary

| Area | Verified in repository / local automated coverage | Not yet established (UNKNOWN / TO DO) |
| --- | --- | --- |
| Chain identity | [Source parameters](../src/kernel/chainparams.cpp), [chain specification](chain-spec.md), [runtime identity test](../test/functional/feature_andaluz_identity.py): custom genesis, magic, ports and branding | Independently operated public chain and stable public release approval |
| Manual bootstrap | v0.2.71 [loopback test](../test/functional/p2p_andaluz_mainnet_bootstrap_identity.py): three daemons, addnode, restart, outage/reconnect | Public WAN reachability, geographic/provider diversity, address discovery, long-running IBD and uptime |
| Encrypted transport | v0.2.72 [local mainnet test](../test/functional/p2p_andaluz_mainnet_v2_transport_identity.py): v2 session/fixture relay, v1 interoperability, wrong-magic v1 prefix rejection | Authenticated operators, all encrypted cross-network rejection cases, public WAN exercises |
| Mining/validation | [Two precomputed mainnet blocks](../test/functional/mining_andaluz_mainnet_block_validation.py), rejection paths and relay | Sustained real independent hash rate, pool participation, viable economics and attack resistance |
| Wallets | [Address identity](../test/functional/wallet_andaluz_identity.py), [backup/restore](../test/functional/wallet_andaluz_backup_restore.py), v0.2.73 [extended keys/descriptors/watch-only/reload](../test/functional/wallet_andaluz_extended_key_identity.py) | Funded recovery qualification, independent external/hardware wallet compatibility and provenance guarantees |
| Operations and economics | [Manual operator guidance](andaluzcoin-mainnet-bootstrap.md); code/test review artifacts | Security audit, signed/reproducible distribution, measured incident response, legal/listing diligence |

These links identify implemented checks and their scope, not a promise that
every environment passes or that any public service exists. Local observations,
public WAN observations and economic-security measurements must be recorded
separately with revision, configuration, duration, methodology and reviewer.

## Bootstrap diversity and eclipse resistance

Owner/operator: **TO BE ASSIGNED** (bootstrap coordinator and independent operators).
Use the [bootstrap guide](andaluzcoin-mainnet-bootstrap.md).

- [ ] Obtain commitments from at least three independently controlled operators
  separated by geography, provider, network, administration and failure domain.
  Evidence: reviewed diversity/ownership inventory and fallback contacts;
  outreach and participation are TO DO, not current infrastructure claims.
- [ ] Exchange endpoints through signed or otherwise verified out-of-band
  channels; confirm operator ownership and intended chain/genesis. Evidence:
  independently reviewed verification records without publishing secrets.
- [ ] Review eclipse exposure and peer-selection policy, including malicious
  manual peers, shared hosting dependencies and single-operator outages.
  Evidence: threat model, independent review and loss-of-peer recovery exercises.
  Several hardcoded addresses alone do not prove decentralization.
- [ ] Review any prospective DNS/fixed seed design, ownership, update and
  monitoring policy before approval. Mainnet `vSeeds` and `vFixedSeeds` are
  currently empty; no functioning public discovery is inferred.

## Public WAN connectivity and durability

Owner/operator: **TO BE ASSIGNED** (network operators and independent validators).
The [local bootstrap test](../test/functional/p2p_andaluz_mainnet_bootstrap_identity.py)
is the starting point, not WAN evidence.

- [ ] Verify inbound public P2P reachability and outbound joins on every
  advertised IPv4/IPv6 route from independently operated remote nodes.
  Evidence: dated topology, chain/genesis/handshake checks and per-route results.
- [ ] Exercise reconnection, restart, bootstrap outages, multiple independent
  peers and fallback selection. Evidence: failure-injection results, logs and
  measured recovery times against thresholds agreed before the exercise.
- [ ] Complete long-running peer, IBD, block propagation and tip-comparison
  exercises across independent nodes. Evidence: predeclared observation window,
  latency/progress/error thresholds, measurements and independent sign-off.
  No universal duration or service guarantee is established by this checklist.

[BIP324 v2](https://bips.dev/324/) provides opportunistic transport encryption,
not authenticated peer/operator identity, proof of a remote chain, or
post-quantum protection. V1 remains possible and unencrypted. The local v2
wrong-magic probe covers a Bitcoin **v1 prefix** on a v2-capable listener;
it does not prove all encrypted cross-network rejection behavior. Verify chain
and operator identity separately; a user-agent or session ID alone is not trust.

## Mining security and difficulty viability

See the [offline mining sustainability study](andaluzcoin-mining-sustainability.md).
See the [SHA256d AuxPoW feasibility study](andaluzcoin-sha256d-auxpow-feasibility.md).

Owner/operator: **TO BE ASSIGNED** (consensus reviewers, independent miners and monitoring operators).
See [chain parameters](../src/kernel/chainparams.cpp),
[PoW implementation](../src/pow.cpp) and [chain specification](chain-spec.md).

Implemented mining is **SHA256d**, with a **2016-block / 14-day target timespan
Bitcoin-style retarget**, intended **10-minute** spacing and **no mainnet
minimum-difficulty fallback**. `powLimit` is
`000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff`;
the subsidy halves every **210000 blocks**. These are consensus parameters,
not forecasts of observed production or revenue. If hash power falls, blocks
can stagnate before the next retarget; elapsed wall time alone does not trigger
a minimum-difficulty escape.

**ASERT and SHA256d AuxPoW merged mining are research concepts only: neither is
implemented or activated.** Difficulty-change research requires a separate
consensus design, simulations, review and activation decision. Dogecoin/Litecoin
Scrypt auxiliary mining is not a ready-made implementation for this SHA256d
fork, nor evidence of available ALUZ mining participants.

- [ ] Measure real independent hash rate, ownership/concentration and pool
  participation with sustained block production. Evidence: methodology,
  observation period, block intervals, difficulty and operating cost/revenue
  assumptions; operator outreach and measurements remain TO DO.
- [ ] Evaluate hash-rate shocks, retarget viability and stagnation scenarios.
  Evidence: reproducible modeling and reviewed acceptance bounds under current
  rules; proposed future algorithms must be evaluated separately.
- [ ] Review 51% attacks, reorgs, rented/concentrated hash power and eclipse
  interactions. Evidence: documented threat model, security-budget assumptions,
  confirmation policy and independent review; no attack-resistance guarantee.
- [ ] Establish monitoring and incident response for stalled blocks, peer loss,
  hash-rate shifts and reorgs. Evidence: numerical alert/response thresholds,
  assigned on-call roles, runbooks and successful recorded drills.

## Consensus, monetary parameters and release review

Owner/operator: **TO BE ASSIGNED** (consensus auditors and release maintainers).

- [ ] Audit genesis, PoW/retarget, subsidy/halving, monetary limits, activation
  rules and chain assumptions against source and tests. Evidence: signed review
  findings, reproducible checks and resolved blocking issues. The
  [chain specification](chain-spec.md) is a reference, not an audit certificate.
- [ ] Complete independent security review and stable release review of a
  specific revision, including upstream security fixes and known limitations.
  Evidence: reviewer identities/roles, scope, results and disposition of findings.
  Green CI alone does not satisfy either review.

## Wallet recovery and integration

Owner/operator: **TO BE ASSIGNED** (wallet reviewers and independent integrators).
Use the [local wallet evidence](README.md#wallet-users-and-integrators);
[managing wallets](managing-wallets.md) and [descriptors](descriptors.md) are
inherited Bitcoin Core references whose network examples need ALUZ verification.

Mainnet extended-key bytes `04 B2 47 46` / `04 B2 43 0C` overlap Bitcoin's
[SLIP-0132 zpub/zprv convention](https://github.com/satoshilabs/slips/blob/master/slip-0132.md).
External wallets may assume a different chain or script policy. In this code,
the descriptor wrapper determines the output script type. Version bytes,
checksums and key origin metadata do not authenticate provenance; relabeling a
key does not prove it originated on ALUZ or make an external wallet compatible.

- [ ] Qualify backup, restore and recovery in isolated environments, including
  encrypted wallets, receive/change recovery and retained ownership/metadata.
  Evidence: reviewed recovery cases and results beyond the existing local
  identity test; keep all secrets out of reports.
- [ ] Qualify descriptor import/export, checksums, ranges, watch-only derivation
  and signing boundaries. Evidence: independent reproducible cases with
  non-custodial test material and expected scripts/addresses.
- [ ] Test third-party and hardware assumptions explicitly: version collisions,
  chain/coin-type derivation, script wrappers, address display, signing and
  recovery. Evidence: per-product/version results and reviewed limitations.
  No third-party/hardware support is established by repository tests alone.

## Node security, recovery and distribution

Owner/operator: **TO BE ASSIGNED** (host administrators and release/security maintainers).
See [bootstrap RPC guidance](andaluzcoin-mainnet-bootstrap.md) and the
[inherited release process](release-process.md) as reference only.

- [ ] Review private RPC binding and authentication, cookie permissions,
  explicit separate datadirs, host patching, administrative access and firewall
  policy. Evidence: per-host review and authorization checks; never expose RPC
  publicly. The inherited filename remains `bitcoin.conf`.
- [ ] Establish log retention/redaction, disk/peer/chain alerts, infrastructure
  backup/restoration and incident ownership. Evidence: measured recovery drills,
  escalation contacts and documented recovery/response targets.
- [ ] Produce independently reproducible builds and review release signing,
  key custody, artifact verification and distribution procedures. Evidence:
  matching build attestations, verified signatures and an approved release
  inventory. GUI packages, downloads and cross-platform releases are not implied.

## Economic, legal and listing diligence

Owner/operator: **TO BE ASSIGNED** (project governance and qualified advisers).

- [ ] Complete prospective economic and jurisdiction-specific legal diligence
  for the intended activities. Evidence: scoped professional review and
  documented decisions; no legal conclusion is supplied by this checklist.
- [ ] If pursuing listings, evaluate each venue's technical, custody, compliance
  and disclosure requirements. Evidence: verified requirements and explicit
  approvals. No exchange listing, liquidity, price or investment return is
  promised; no service participation has been verified here.

## GO / NO-GO decision

**Current decision: NO-GO for public economic mainnet.** Local development and
isolated tests do not close launch gates.

GO requires every applicable gate above to have an assigned accountable owner,
reviewable evidence for a specific revision/configuration, predeclared measurable
acceptance thresholds met over an agreed observation period, independent review,
and explicit recorded owner/release approval. There must be no unresolved
blocking audit, security, recovery or difficulty-viability findings. Independent
bootstrap participation, public WAN results and mining/security measurements
must each exist; none can substitute for the others.

Missing/UNKNOWN evidence, unassigned ownership, failed thresholds or unresolved
blocking findings mean NO-GO. Record the decision and evidence references before
any separate deployment authorization. This document authorizes no deployment,
endpoint publication, network changes, real mining or third-party services.
