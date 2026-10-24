# Building Andaluzcoin Core (ALUZ)

Follow the [Ubuntu/Linux source build and optional tests](README.md#build-on-ubuntulinux).
That path lists dependencies, uses CMake with a normal `build/` directory and
builds with `-j 1` for constrained builders. Additional platform and dependency
information is inherited Bitcoin Core material in the
[Unix build notes](doc/build-unix.md) and [dependency reference](doc/dependencies.md).
These references do not establish Andaluzcoin binary distribution or platform
release support.

Current executable names remain `build/bin/bitcoind` and
`build/bin/bitcoin-cli`; the config filename remains `bitcoin.conf`.
Always pass a separate explicit `-datadir` to daemon and CLI; the inherited
Linux default is `~/.bitcoin`. Start with the
[private local inspection example](README.md#private-local-inspection), which
creates a fresh directory, disables peers and uses private cookie-authenticated
RPC without a wallet.

Mainnet code support is not public launch approval. Read the
[readiness checklist](doc/andaluzcoin-mainnet-readiness.md),
[bootstrap guide](doc/andaluzcoin-mainnet-bootstrap.md) and
[documentation index](doc/README.md) before planning operation.
See [COPYING](COPYING) for the MIT license and upstream provenance.
