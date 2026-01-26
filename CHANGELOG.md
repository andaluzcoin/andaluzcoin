# Andaluzcoin Core Changelog

Andaluzcoin Core is based on Bitcoin Core.
This changelog tracks *Andaluzcoin-specific* changes and upstream sync milestones.

Versioning convention (recommended):
- v<bitcoin-version>-andaluzcoin<N>
  Example: v30.2-andaluzcoin1, v30.2-andaluzcoin2, ...

## [Unreleased]

### Upstream sync
- Sync with Bitcoin Core `30.x` up to `v30.2`. (#3)

### Documentation
- Add CHANGELOG to track Andaluzcoin-specific changes.

## [andaluzcoin-v0.0.1] - 2026-01-25

### Tests
- Fix MiniWallet fee/feerate normalization for TRUC mempool tests; avoid 0-fee txs under minrelay changes. (#2)

### Build/CI
- CI: free disk and prune docker/build cache for the CentOS depends+gui job. (#2)
- CI: test-each-commit workflow improvements (unshallow checkout; only test PR commits). (#2)

### Repo hygiene
- Keep libmultiprocess subtree unmodified to satisfy subtree lint. (#2)
- Lint fixes (whitespace, doc args, etc.). (#2)
