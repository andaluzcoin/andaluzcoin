# Andaluzcoin Core Changelog

Andaluzcoin Core is based on Bitcoin Core.
This changelog tracks *Andaluzcoin-specific* changes and upstream sync milestones.

Versioning convention (recommended):
- v<bitcoin-version>-andaluzcoin<N>
  Example: v30.2-andaluzcoin1, v30.2-andaluzcoin2, ...

## [Unreleased]

### Upstream sync
- Sync with Bitcoin Core `30.x` (includes 30.2 backports). (#3)

### Tests
- Fix MiniWallet fee/feerate normalization for TRUC mempool tests; avoid 0-fee txs under minrelay changes. (#2)

### Build/CI
- Free disk and prune docker/build cache for the CentOS depends+gui CI job. (#2)
- Keep libmultiprocess subtree unmodified to satisfy subtree lint. (#2)
- Lint fixes (whitespace, doc args, etc.). (#2)

