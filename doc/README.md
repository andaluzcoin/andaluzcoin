# Andaluzcoin Core (ALUZ) documentation

Andaluzcoin is a Bitcoin-derived culture/community SHA256d proof-of-work chain.
Mainnet and regtest code support does not establish a reliable public economic
network. **PRELAUNCH / NOT APPROVED FOR PUBLIC ECONOMIC MAINNET.**
Start with the [readiness checklist](andaluzcoin-mainnet-readiness.md) and
[manual bootstrap operations](andaluzcoin-mainnet-bootstrap.md).

## Operators

- [Current chain specification](chain-spec.md): network identity and consensus parameters; source is authoritative.
- [Mainnet readiness checklist](andaluzcoin-mainnet-readiness.md): unfulfilled launch gates and required evidence.
- [Manual mainnet bootstrap guide](andaluzcoin-mainnet-bootstrap.md): private RPC, verified peer selection and recovery; no approved public endpoints.
- [Private local inspection](../README.md#private-local-inspection): fresh isolated datadir with no peers or wallet.

## Developers

- [Project overview and Ubuntu/Linux build](../README.md#build-on-ubuntulinux)
- [Installation entry point](../INSTALL.md)
- [Andaluzcoin developer notes](andaluzcoin-dev-notes.md): normal versus fuzz build directories.
- [Runtime identity test](../test/functional/feature_andaluz_identity.py)
- [Local mainnet bootstrap test](../test/functional/p2p_andaluz_mainnet_bootstrap_identity.py)
- [Local mainnet v2 transport test](../test/functional/p2p_andaluz_mainnet_v2_transport_identity.py)
- [Precomputed mainnet block validation test](../test/functional/mining_andaluz_mainnet_block_validation.py)
- [Project source and issues](https://github.com/andaluzcoin/andaluzcoin)

## Wallet users and integrators

Current local coverage uses SQLite descriptor wallets. External wallet and
hardware integration remain TO DO; extended-key bytes overlap Bitcoin's
SLIP-0132 zpub/zprv convention. The descriptor wrapper determines script type,
not the textual key prefix. Read the [wallet readiness gate](andaluzcoin-mainnet-readiness.md#wallet-recovery-and-integration)
before attempting integration.

- [Address and wallet identity test](../test/functional/wallet_andaluz_identity.py)
- [Extended key, descriptor and watch-only test](../test/functional/wallet_andaluz_extended_key_identity.py)
- [Backup/restore identity test](../test/functional/wallet_andaluz_backup_restore.py)

## Inherited Bitcoin Core technical references

The following documents describe upstream mechanics and may contain Bitcoin
network addresses, wallet examples, defaults, downloads or support channels.
Those are not Andaluzcoin resources. Check network-specific values against the
[ALUZ chain specification](chain-spec.md) and source, retain `bitcoin.conf`
and current executable names, and always specify a private ALUZ `-datadir`.
Upstream release procedures are reference material, not a claim of ALUZ releases.

- [Unix build notes](build-unix.md) and [dependencies](dependencies.md)
- [Configuration file syntax](bitcoin-conf.md)
- [JSON-RPC interface](JSON-RPC-interface.md)
- [Managing wallets](managing-wallets.md)
- [Descriptor language](descriptors.md)
- [PSBT reference](psbt.md)
- [Developer notes](developer-notes.md)
- [Fuzz testing](fuzzing.md)
- [Release process reference](release-process.md)
- [Assets attribution](assets-attribution.md)

Andaluzcoin acknowledges Bitcoin Core contributors and Satoshi Nakamoto.
Distributed under the [MIT software license](../COPYING), preserving upstream
copyright and license provenance.
