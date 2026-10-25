# Andaluzcoin Core (ALUZ)

Andaluzcoin is an independent Bitcoin-derived cultural/community coin with
functional decentralized consensus, peer-to-peer transactions and SHA256d
proof-of-work mining. Its purpose is community participation and peer-to-peer
money; it is not a utility-first token or a Bitcoin competitor by design.
There are no guarantees of value, profit or mining returns.

**PRELAUNCH: NOT APPROVED FOR PUBLIC ECONOMIC MAINNET.** Mainnet consensus
and regtest are supported in code. That does not establish public launch
readiness: there is no approved public seeds/bootstrap network, and repository
tests alone establish no verified security, uptime or mining ecosystem.
See the [mainnet readiness checklist](doc/andaluzcoin-mainnet-readiness.md)
for the outstanding gates and evidence required.

## Network identity

These mainnet values come from [chain parameters](src/kernel/chainparams.cpp)
and [RPC base parameters](src/chainparamsbase.cpp); source remains authoritative.

| Parameter | Implemented mainnet value |
| --- | --- |
| Genesis | `000000f7dca7651a1397fd0bc99b2a456dbb2d23470834b6290aadec4b46d15c` |
| P2P magic | `b6 a9 64 58` |
| P2P / RPC port | `29444` / `29443` |
| Bech32 HRP | `aluz` |
| P2PKH / P2SH / WIF version byte (decimal) | `55` / `117` / `183` |
| Intended block spacing | 10 minutes |
| Difficulty retarget | 2016 blocks / 14-day target timespan; no mainnet minimum-difficulty exception |
| Subsidy halving interval | 210000 blocks |
| DNS / fixed seeds | Empty |

The [chain specification](doc/chain-spec.md) records further parameters.
Mining sustainability, hash-rate shocks and reorg risk still require review;
ASERT and AuxPoW are research concepts, not implemented features.

## Build on Ubuntu/Linux

From this repository checkout, use a normal build directory separate from fuzz
builds. The current requirements include CMake >= 3.22, a C++20 compiler
(GCC >= 12.1 or Clang >= 17), Boost >= 1.74, libevent >= 2.1.8,
SQLite >= 3.7.17 for wallets, and Python >= 3.10 for test scripts.
The package list follows the inherited [Unix build notes](doc/build-unix.md)
and [dependency reference](doc/dependencies.md); older distributions may need
newer compiler packages.

```sh
sudo apt-get install build-essential cmake pkgconf python3 libevent-dev libboost-dev libsqlite3-dev
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_GUI=OFF -DENABLE_IPC=OFF -DWITH_USDT=OFF \
  -DBUILD_FOR_FUZZING=OFF -DBUILD_FUZZ_BINARY=OFF \
  -DBUILD_DAEMON=ON -DBUILD_CLI=ON -DENABLE_WALLET=ON -DBUILD_TESTS=ON
cmake --build build -j 1
```

`-j 1` limits parallel compiler memory use on constrained ARM64/Linux builders;
a successful build still requires sufficient memory and disk. IPC is disabled
here so Cap'n Proto is not required. The current executables retain upstream
names: **`build/bin/bitcoind`** and **`build/bin/bitcoin-cli`**. These names do
not mean this checkout connects to Bitcoin mainnet. This is a source build path,
not a claim that GUI packages or Windows/macOS releases are distributed.

Optional local validation after building:

```sh
ctest --test-dir build --output-on-failure
python3 build/test/functional/test_runner.py -j 1 feature_andaluz_identity.py p2p_andaluz_mainnet_bootstrap_identity.py
```

The targeted functional tests create isolated temporary data directories and
exercise local mainnet identity/manual connections. They do not contact a
public ALUZ bootstrap network or demonstrate economic security.

## Private local inspection

For a non-public mainnet inspection, create a fresh directory with `mktemp`;
do not reuse an existing Bitcoin or Andaluzcoin wallet/data directory.
Run these commands from the checkout after building:

```sh
ALUZ_LOCAL_DATA=$(mktemp -d /tmp/aluz-local.XXXXXX)
chmod 700 "$ALUZ_LOCAL_DATA"
build/bin/bitcoind -datadir="$ALUZ_LOCAL_DATA" -chain=main \
  -disablewallet=1 -connect=0 -listen=0 -dns=0 -dnsseed=0 -fixedseeds=0 \
  -natpmp=0 -discover=0 -rpcbind=127.0.0.1 -rpcallowip=127.0.0.1 -daemon
build/bin/bitcoin-cli -datadir="$ALUZ_LOCAL_DATA" -chain=main -rpcwait getblockchaininfo
build/bin/bitcoin-cli -datadir="$ALUZ_LOCAL_DATA" -chain=main getblockhash 0
build/bin/bitcoin-cli -datadir="$ALUZ_LOCAL_DATA" -chain=main stop
```

This disables peer discovery, outgoing automatic connections and P2P listening;
it does not automatically sync or mine. RPC uses the local authentication cookie;
keep it private. The config filename remains **`bitcoin.conf`**. Use an explicit
`-datadir` for both daemon and CLI: inherited defaults still use Bitcoin paths
(`~/.bitcoin` on Linux). `chain=main` selects mainnet; `[main]` scopes config
settings and does not itself select a chain. Explicit RPC binding requires
both `rpcbind` and `rpcallowip`; keep both private. See the
[manual bootstrap guide](doc/andaluzcoin-mainnet-bootstrap.md) for future
operator planning with verified peers; no live endpoints are provided.

## Documentation and development

- [Installation entry point](INSTALL.md)
- [Andaluzcoin documentation index](doc/README.md)
- [Chain specification](doc/chain-spec.md)
- [Mainnet readiness gates](doc/andaluzcoin-mainnet-readiness.md)
- [Manual mainnet bootstrap operations](doc/andaluzcoin-mainnet-bootstrap.md)
- [Andaluzcoin developer notes](doc/andaluzcoin-dev-notes.md)
- [Project repository](https://github.com/andaluzcoin/andaluzcoin)
- [Contribution workflow](CONTRIBUTING.md) and [inherited developer reference](doc/developer-notes.md)

Andaluzcoin derives from Bitcoin Core and acknowledges its contributors and
Satoshi Nakamoto. Much technical documentation, executable naming and command
syntax remain inherited Bitcoin Core material. Bitcoin addresses, services,
downloads and support channels in those references are not Andaluzcoin services;
use the Andaluzcoin chain specification and tests for network-specific facts.
Automated engineering tests are not evidence of a deployed global network.

Andaluzcoin Core is distributed under the [MIT license](COPYING), preserving
upstream copyright and license provenance.
