# Libraries

| Name                     | Description |
|--------------------------|-------------|
| *libandaluzcoin_cli*         | RPC client functionality used by *andaluzcoin-cli* executable |
| *libandaluzcoin_common*      | Home for common functionality shared by different executables and libraries. Similar to *libandaluzcoin_util*, but higher-level (see [Dependencies](#dependencies)). |
| *libandaluzcoin_consensus*   | Consensus functionality used by *libandaluzcoin_node* and *libandaluzcoin_wallet*. |
| *libandaluzcoin_crypto*      | Hardware-optimized functions for data encryption, hashing, message authentication, and key derivation. |
| *libandaluzcoin_kernel*      | Consensus engine and support library used for validation by *libandaluzcoin_node*. |
| *libandaluzcoinqt*           | GUI functionality used by *andaluzcoin-qt* and *andaluzcoin-gui* executables. |
| *libandaluzcoin_ipc*         | IPC functionality used by *andaluzcoin-node*, *andaluzcoin-wallet*, *andaluzcoin-gui* executables to communicate when [`-DWITH_MULTIPROCESS=ON`](multiprocess.md) is used. |
| *libandaluzcoin_node*        | P2P and RPC server functionality used by *andaluzcoind* and *andaluzcoin-qt* executables. |
| *libandaluzcoin_util*        | Home for common functionality shared by different executables and libraries. Similar to *libandaluzcoin_common*, but lower-level (see [Dependencies](#dependencies)). |
| *libandaluzcoin_wallet*      | Wallet functionality used by *andaluzcoind* and *andaluzcoin-wallet* executables. |
| *libandaluzcoin_wallet_tool* | Lower-level wallet functionality used by *andaluzcoin-wallet* executable. |
| *libandaluzcoin_zmq*         | [ZeroMQ](../zmq.md) functionality used by *andaluzcoind* and *andaluzcoin-qt* executables. |

## Conventions

- Most libraries are internal libraries and have APIs which are completely unstable! There are few or no restrictions on backwards compatibility or rules about external dependencies. An exception is *libandaluzcoin_kernel*, which, at some future point, will have a documented external interface.

- Generally each library should have a corresponding source directory and namespace. Source code organization is a work in progress, so it is true that some namespaces are applied inconsistently, and if you look at [`add_library(andaluzcoin_* ...)`](../../src/CMakeLists.txt) lists you can see that many libraries pull in files from outside their source directory. But when working with libraries, it is good to follow a consistent pattern like:

  - *libandaluzcoin_node* code lives in `src/node/` in the `node::` namespace
  - *libandaluzcoin_wallet* code lives in `src/wallet/` in the `wallet::` namespace
  - *libandaluzcoin_ipc* code lives in `src/ipc/` in the `ipc::` namespace
  - *libandaluzcoin_util* code lives in `src/util/` in the `util::` namespace
  - *libandaluzcoin_consensus* code lives in `src/consensus/` in the `Consensus::` namespace

## Dependencies

- Libraries should minimize what other libraries they depend on, and only reference symbols following the arrows shown in the dependency graph below:

<table><tr><td>

```mermaid

%%{ init : { "flowchart" : { "curve" : "basis" }}}%%

graph TD;

andaluzcoin-cli[andaluzcoin-cli]-->libandaluzcoin_cli;

andaluzcoind[andaluzcoind]-->libandaluzcoin_node;
andaluzcoind[andaluzcoind]-->libandaluzcoin_wallet;

andaluzcoin-qt[andaluzcoin-qt]-->libandaluzcoin_node;
andaluzcoin-qt[andaluzcoin-qt]-->libandaluzcoinqt;
andaluzcoin-qt[andaluzcoin-qt]-->libandaluzcoin_wallet;

andaluzcoin-wallet[andaluzcoin-wallet]-->libandaluzcoin_wallet;
andaluzcoin-wallet[andaluzcoin-wallet]-->libandaluzcoin_wallet_tool;

libandaluzcoin_cli-->libandaluzcoin_util;
libandaluzcoin_cli-->libandaluzcoin_common;

libandaluzcoin_consensus-->libandaluzcoin_crypto;

libandaluzcoin_common-->libandaluzcoin_consensus;
libandaluzcoin_common-->libandaluzcoin_crypto;
libandaluzcoin_common-->libandaluzcoin_util;

libandaluzcoin_kernel-->libandaluzcoin_consensus;
libandaluzcoin_kernel-->libandaluzcoin_crypto;
libandaluzcoin_kernel-->libandaluzcoin_util;

libandaluzcoin_node-->libandaluzcoin_consensus;
libandaluzcoin_node-->libandaluzcoin_crypto;
libandaluzcoin_node-->libandaluzcoin_kernel;
libandaluzcoin_node-->libandaluzcoin_common;
libandaluzcoin_node-->libandaluzcoin_util;

libandaluzcoinqt-->libandaluzcoin_common;
libandaluzcoinqt-->libandaluzcoin_util;

libandaluzcoin_util-->libandaluzcoin_crypto;

libandaluzcoin_wallet-->libandaluzcoin_common;
libandaluzcoin_wallet-->libandaluzcoin_crypto;
libandaluzcoin_wallet-->libandaluzcoin_util;

libandaluzcoin_wallet_tool-->libandaluzcoin_wallet;
libandaluzcoin_wallet_tool-->libandaluzcoin_util;

classDef bold stroke-width:2px, font-weight:bold, font-size: smaller;
class andaluzcoin-qt,andaluzcoind,andaluzcoin-cli,andaluzcoin-wallet bold
```
</td></tr><tr><td>

**Dependency graph**. Arrows show linker symbol dependencies. *Crypto* lib depends on nothing. *Util* lib is depended on by everything. *Kernel* lib depends only on consensus, crypto, and util.

</td></tr></table>

- The graph shows what _linker symbols_ (functions and variables) from each library other libraries can call and reference directly, but it is not a call graph. For example, there is no arrow connecting *libandaluzcoin_wallet* and *libandaluzcoin_node* libraries, because these libraries are intended to be modular and not depend on each other's internal implementation details. But wallet code is still able to call node code indirectly through the `interfaces::Chain` abstract class in [`interfaces/chain.h`](../../src/interfaces/chain.h) and node code calls wallet code through the `interfaces::ChainClient` and `interfaces::Chain::Notifications` abstract classes in the same file. In general, defining abstract classes in [`src/interfaces/`](../../src/interfaces/) can be a convenient way of avoiding unwanted direct dependencies or circular dependencies between libraries.

- *libandaluzcoin_crypto* should be a standalone dependency that any library can depend on, and it should not depend on any other libraries itself.

- *libandaluzcoin_consensus* should only depend on *libandaluzcoin_crypto*, and all other libraries besides *libandaluzcoin_crypto* should be allowed to depend on it.

- *libandaluzcoin_util* should be a standalone dependency that any library can depend on, and it should not depend on other libraries except *libandaluzcoin_crypto*. It provides basic utilities that fill in gaps in the C++ standard library and provide lightweight abstractions over platform-specific features. Since the util library is distributed with the kernel and is usable by kernel applications, it shouldn't contain functions that external code shouldn't call, like higher level code targeted at the node or wallet. (*libandaluzcoin_common* is a better place for higher level code, or code that is meant to be used by internal applications only.)

- *libandaluzcoin_common* is a home for miscellaneous shared code used by different Andaluzcoin Core applications. It should not depend on anything other than *libandaluzcoin_util*, *libandaluzcoin_consensus*, and *libandaluzcoin_crypto*.

- *libandaluzcoin_kernel* should only depend on *libandaluzcoin_util*, *libandaluzcoin_consensus*, and *libandaluzcoin_crypto*.

- The only thing that should depend on *libandaluzcoin_kernel* internally should be *libandaluzcoin_node*. GUI and wallet libraries *libandaluzcoinqt* and *libandaluzcoin_wallet* in particular should not depend on *libandaluzcoin_kernel* and the unneeded functionality it would pull in, like block validation. To the extent that GUI and wallet code need scripting and signing functionality, they should be get able it from *libandaluzcoin_consensus*, *libandaluzcoin_common*, *libandaluzcoin_crypto*, and *libandaluzcoin_util*, instead of *libandaluzcoin_kernel*.

- GUI, node, and wallet code internal implementations should all be independent of each other, and the *libandaluzcoinqt*, *libandaluzcoin_node*, *libandaluzcoin_wallet* libraries should never reference each other's symbols. They should only call each other through [`src/interfaces/`](../../src/interfaces/) abstract interfaces.

## Work in progress

- Validation code is moving from *libandaluzcoin_node* to *libandaluzcoin_kernel* as part of [The libandaluzcoinkernel Project #27587](https://github.com/andaluzcoin/andaluzcoin/issues/27587)
