# Copyright (c) 2023-present The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

include(GNUInstallDirs)
include(AddWindowsResources)

configure_file(${PROJECT_SOURCE_DIR}/cmake/andaluzcoin-build-config.h.in andaluzcoin-build-config.h USE_SOURCE_PERMISSIONS @ONLY)
include_directories(${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_CURRENT_SOURCE_DIR})

add_custom_target(generate_build_info
  BYPRODUCTS ${PROJECT_BINARY_DIR}/src/andaluzcoin-build-info.h
  COMMAND ${CMAKE_COMMAND} -DBUILD_INFO_HEADER_PATH=${PROJECT_BINARY_DIR}/src/andaluzcoin-build-info.h -DSOURCE_DIR=${PROJECT_SOURCE_DIR} -P ${PROJECT_SOURCE_DIR}/cmake/script/GenerateBuildInfo.cmake
  COMMENT "Generating andaluzcoin-build-info.h"
  VERBATIM
)
add_library(andaluzcoin_clientversion OBJECT EXCLUDE_FROM_ALL
  clientversion.cpp
)
target_link_libraries(andaluzcoin_clientversion
  PRIVATE
    core_interface
)
add_dependencies(andaluzcoin_clientversion generate_build_info)

add_subdirectory(crypto)
add_subdirectory(univalue)
add_subdirectory(util)
if(WITH_MULTIPROCESS)
  add_subdirectory(ipc)
endif()

#=============================
# secp256k1 subtree
#=============================
message("")
message("Configuring secp256k1 subtree...")
set(SECP256K1_DISABLE_SHARED ON CACHE BOOL "" FORCE)
set(SECP256K1_ENABLE_MODULE_ECDH OFF CACHE BOOL "" FORCE)
set(SECP256K1_ENABLE_MODULE_RECOVERY ON CACHE BOOL "" FORCE)
set(SECP256K1_ENABLE_MODULE_MUSIG OFF CACHE BOOL "" FORCE)
set(SECP256K1_BUILD_BENCHMARK OFF CACHE BOOL "" FORCE)
set(SECP256K1_BUILD_TESTS ${BUILD_TESTS} CACHE BOOL "" FORCE)
set(SECP256K1_BUILD_EXHAUSTIVE_TESTS ${BUILD_TESTS} CACHE BOOL "" FORCE)
if(NOT BUILD_TESTS)
  # Always skip the ctime tests, if we are building no other tests.
  # Otherwise, they are built if Valgrind is available. See SECP256K1_VALGRIND.
  set(SECP256K1_BUILD_CTIME_TESTS ${BUILD_TESTS} CACHE BOOL "" FORCE)
endif()
set(SECP256K1_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
include(GetTargetInterface)
# -fsanitize and related flags apply to both C++ and C,
# so we can pass them down to libsecp256k1 as CFLAGS and LDFLAGS.
get_target_interface(core_sanitizer_cxx_flags "" sanitize_interface COMPILE_OPTIONS)
set(SECP256K1_APPEND_CFLAGS ${core_sanitizer_cxx_flags} CACHE STRING "" FORCE)
unset(core_sanitizer_cxx_flags)
get_target_interface(core_sanitizer_linker_flags "" sanitize_interface LINK_OPTIONS)
set(SECP256K1_APPEND_LDFLAGS ${core_sanitizer_linker_flags} CACHE STRING "" FORCE)
unset(core_sanitizer_linker_flags)
# We want to build libsecp256k1 with the most tested RelWithDebInfo configuration.
enable_language(C)
foreach(config IN LISTS CMAKE_BUILD_TYPE CMAKE_CONFIGURATION_TYPES)
  if(config STREQUAL "")
    continue()
  endif()
  string(TOUPPER "${config}" config)
  set(CMAKE_C_FLAGS_${config} "${CMAKE_C_FLAGS_RELWITHDEBINFO}")
endforeach()
# If the CFLAGS environment variable is defined during building depends
# and configuring this build system, its content might be duplicated.
if(DEFINED ENV{CFLAGS})
  deduplicate_flags(CMAKE_C_FLAGS)
endif()
set(CMAKE_EXPORT_COMPILE_COMMANDS OFF)
add_subdirectory(secp256k1)
set_target_properties(secp256k1 PROPERTIES
  EXCLUDE_FROM_ALL TRUE
)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
string(APPEND CMAKE_C_COMPILE_OBJECT " ${APPEND_CPPFLAGS} ${APPEND_CFLAGS}")

add_library(andaluzcoin_consensus STATIC EXCLUDE_FROM_ALL
  arith_uint256.cpp
  consensus/merkle.cpp
  consensus/tx_check.cpp
  hash.cpp
  primitives/block.cpp
  primitives/transaction.cpp
  pubkey.cpp
  script/interpreter.cpp
  script/script.cpp
  script/script_error.cpp
  uint256.cpp
)
target_link_libraries(andaluzcoin_consensus
  PRIVATE
    core_interface
    andaluzcoin_crypto
    secp256k1
)

if(WITH_ZMQ)
  add_subdirectory(zmq)
endif()

# Home for common functionality shared by different executables and libraries.
# Similar to `andaluzcoin_util` library, but higher-level.
add_library(andaluzcoin_common STATIC EXCLUDE_FROM_ALL
  addresstype.cpp
  base58.cpp
  bech32.cpp
  chainparams.cpp
  chainparamsbase.cpp
  coins.cpp
  common/args.cpp
  common/bloom.cpp
  common/config.cpp
  common/init.cpp
  common/interfaces.cpp
  common/messages.cpp
  common/netif.cpp
  common/pcp.cpp
  common/run_command.cpp
  common/settings.cpp
  common/signmessage.cpp
  common/system.cpp
  common/url.cpp
  compressor.cpp
  core_read.cpp
  core_write.cpp
  deploymentinfo.cpp
  external_signer.cpp
  init/common.cpp
  kernel/chainparams.cpp
  key.cpp
  key_io.cpp
  merkleblock.cpp
  net_permissions.cpp
  net_types.cpp
  netaddress.cpp
  netbase.cpp
  outputtype.cpp
  policy/feerate.cpp
  policy/policy.cpp
  protocol.cpp
  psbt.cpp
  rpc/external_signer.cpp
  rpc/rawtransaction_util.cpp
  rpc/request.cpp
  rpc/util.cpp
  scheduler.cpp
  script/descriptor.cpp
  script/miniscript.cpp
  script/parsing.cpp
  script/sign.cpp
  script/signingprovider.cpp
  script/solver.cpp
)
target_link_libraries(andaluzcoin_common
  PRIVATE
    core_interface
    andaluzcoin_consensus
    andaluzcoin_util
    univalue
    secp256k1
    Boost::headers
    $<TARGET_NAME_IF_EXISTS:USDT::headers>
    $<$<PLATFORM_ID:Windows>:ws2_32>
)


set(installable_targets)
if(ENABLE_WALLET)
  add_subdirectory(wallet)

  if(BUILD_WALLET_TOOL)
    add_executable(andaluzcoin-wallet
      andaluzcoin-wallet.cpp
      init/andaluzcoin-wallet.cpp
      wallet/wallettool.cpp
    )
    add_windows_resources(andaluzcoin-wallet andaluzcoin-wallet-res.rc)
    target_link_libraries(andaluzcoin-wallet
      core_interface
      andaluzcoin_wallet
      andaluzcoin_common
      andaluzcoin_util
      Boost::headers
    )
    list(APPEND installable_targets andaluzcoin-wallet)
  endif()
endif()


# P2P and RPC server functionality used by `andaluzcoind` and `andaluzcoin-qt` executables.
add_library(andaluzcoin_node STATIC EXCLUDE_FROM_ALL
  addrdb.cpp
  addrman.cpp
  banman.cpp
  bip324.cpp
  blockencodings.cpp
  blockfilter.cpp
  chain.cpp
  consensus/tx_verify.cpp
  dbwrapper.cpp
  deploymentstatus.cpp
  flatfile.cpp
  headerssync.cpp
  httprpc.cpp
  httpserver.cpp
  i2p.cpp
  index/base.cpp
  index/blockfilterindex.cpp
  index/coinstatsindex.cpp
  index/txindex.cpp
  init.cpp
  kernel/chain.cpp
  kernel/checks.cpp
  kernel/coinstats.cpp
  kernel/context.cpp
  kernel/cs_main.cpp
  kernel/disconnected_transactions.cpp
  kernel/mempool_removal_reason.cpp
  mapport.cpp
  net.cpp
  net_processing.cpp
  netgroup.cpp
  node/abort.cpp
  node/blockmanager_args.cpp
  node/blockstorage.cpp
  node/caches.cpp
  node/chainstate.cpp
  node/chainstatemanager_args.cpp
  node/coin.cpp
  node/coins_view_args.cpp
  node/connection_types.cpp
  node/context.cpp
  node/database_args.cpp
  node/eviction.cpp
  node/interface_ui.cpp
  node/interfaces.cpp
  node/kernel_notifications.cpp
  node/mempool_args.cpp
  node/mempool_persist.cpp
  node/mempool_persist_args.cpp
  node/miner.cpp
  node/mini_miner.cpp
  node/minisketchwrapper.cpp
  node/peerman_args.cpp
  node/psbt.cpp
  node/timeoffsets.cpp
  node/transaction.cpp
  node/txdownloadman_impl.cpp
  node/txreconciliation.cpp
  node/utxo_snapshot.cpp
  node/warnings.cpp
  noui.cpp
  policy/ephemeral_policy.cpp
  policy/fees.cpp
  policy/fees_args.cpp
  policy/packages.cpp
  policy/rbf.cpp
  policy/settings.cpp
  policy/truc_policy.cpp
  pow.cpp
  rest.cpp
  rpc/blockchain.cpp
  rpc/fees.cpp
  rpc/mempool.cpp
  rpc/mining.cpp
  rpc/net.cpp
  rpc/node.cpp
  rpc/output_script.cpp
  rpc/rawtransaction.cpp
  rpc/server.cpp
  rpc/server_util.cpp
  rpc/signmessage.cpp
  rpc/txoutproof.cpp
  script/sigcache.cpp
  signet.cpp
  torcontrol.cpp
  txdb.cpp
  txmempool.cpp
  txorphanage.cpp
  txrequest.cpp
  validation.cpp
  validationinterface.cpp
  versionbits.cpp
  $<$<TARGET_EXISTS:andaluzcoin_wallet>:wallet/init.cpp>
  $<$<NOT:$<TARGET_EXISTS:andaluzcoin_wallet>>:dummywallet.cpp>
)
target_link_libraries(andaluzcoin_node
  PRIVATE
    core_interface
    andaluzcoin_common
    andaluzcoin_util
    $<TARGET_NAME_IF_EXISTS:andaluzcoin_zmq>
    leveldb
    minisketch
    univalue
    Boost::headers
    $<TARGET_NAME_IF_EXISTS:libevent::core>
    $<TARGET_NAME_IF_EXISTS:libevent::extra>
    $<TARGET_NAME_IF_EXISTS:libevent::pthreads>
    $<TARGET_NAME_IF_EXISTS:USDT::headers>
)


# Andaluzcoin Core andaluzcoind.
if(BUILD_DAEMON)
  add_executable(andaluzcoind
    andaluzcoind.cpp
    init/andaluzcoind.cpp
  )
  add_windows_resources(andaluzcoind andaluzcoind-res.rc)
  target_link_libraries(andaluzcoind
    core_interface
    andaluzcoin_node
    $<TARGET_NAME_IF_EXISTS:andaluzcoin_wallet>
  )
  list(APPEND installable_targets andaluzcoind)
endif()
if(WITH_MULTIPROCESS)
  add_executable(andaluzcoin-node
    andaluzcoind.cpp
    init/andaluzcoin-node.cpp
  )
  target_link_libraries(andaluzcoin-node
    core_interface
    andaluzcoin_node
    andaluzcoin_ipc
    $<TARGET_NAME_IF_EXISTS:andaluzcoin_wallet>
  )
  list(APPEND installable_targets andaluzcoin-node)

  if(BUILD_TESTS)
    # andaluzcoin_ipc_test library target is defined here in src/CMakeLists.txt
    # instead of src/test/CMakeLists.txt so capnp files in src/test/ are able to
    # reference capnp files in src/ipc/capnp/ by relative path. The Cap'n Proto
    # compiler only allows importing by relative path when the importing and
    # imported files are underneath the same compilation source prefix, so the
    # source prefix must be src/, not src/test/
    add_library(andaluzcoin_ipc_test STATIC EXCLUDE_FROM_ALL
      test/ipc_test.cpp
    )
    target_capnp_sources(andaluzcoin_ipc_test ${PROJECT_SOURCE_DIR}
      test/ipc_test.capnp
    )
    add_dependencies(andaluzcoin_ipc_test andaluzcoin_ipc_headers)
  endif()
endif()


add_library(andaluzcoin_cli STATIC EXCLUDE_FROM_ALL
  compat/stdin.cpp
  rpc/client.cpp
)
target_link_libraries(andaluzcoin_cli
  PUBLIC
    core_interface
    univalue
)


# Andaluzcoin Core RPC client
if(BUILD_CLI)
  add_executable(andaluzcoin-cli andaluzcoin-cli.cpp)
  add_windows_resources(andaluzcoin-cli andaluzcoin-cli-res.rc)
  target_link_libraries(andaluzcoin-cli
    core_interface
    andaluzcoin_cli
    andaluzcoin_common
    andaluzcoin_util
    libevent::core
    libevent::extra
  )
  list(APPEND installable_targets andaluzcoin-cli)
endif()


if(BUILD_TX)
  add_executable(andaluzcoin-tx andaluzcoin-tx.cpp)
  add_windows_resources(andaluzcoin-tx andaluzcoin-tx-res.rc)
  target_link_libraries(andaluzcoin-tx
    core_interface
    andaluzcoin_common
    andaluzcoin_util
    univalue
  )
  list(APPEND installable_targets andaluzcoin-tx)
endif()


if(BUILD_UTIL)
  add_executable(andaluzcoin-util andaluzcoin-util.cpp)
  add_windows_resources(andaluzcoin-util andaluzcoin-util-res.rc)
  target_link_libraries(andaluzcoin-util
    core_interface
    andaluzcoin_common
    andaluzcoin_util
  )
  list(APPEND installable_targets andaluzcoin-util)
endif()


if(BUILD_GUI)
  add_subdirectory(qt)
endif()


if(BUILD_KERNEL_LIB)
  add_subdirectory(kernel)
endif()

if(BUILD_UTIL_CHAINSTATE)
  add_executable(andaluzcoin-chainstate
    andaluzcoin-chainstate.cpp
  )
  # TODO: The `SKIP_BUILD_RPATH` property setting can be deleted
  #       in the future after reordering Guix script commands to
  #       perform binary checks after the installation step.
  # Relevant discussions:
  # - https://github.com/hebasto/andaluzcoin/pull/236#issuecomment-2183120953
  # - https://github.com/andaluzcoin/andaluzcoin/pull/30312#issuecomment-2191235833
  set_target_properties(andaluzcoin-chainstate PROPERTIES
    SKIP_BUILD_RPATH OFF
  )
  target_link_libraries(andaluzcoin-chainstate
    PRIVATE
      core_interface
      andaluzcoinkernel
  )
endif()


add_subdirectory(test/util)
if(BUILD_BENCH)
  add_subdirectory(bench)
endif()

if(BUILD_TESTS)
  add_subdirectory(test)
endif()

if(BUILD_FUZZ_BINARY)
  add_subdirectory(test/fuzz)
endif()


install(TARGETS ${installable_targets}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
unset(installable_targets)

if(INSTALL_MAN)
  # TODO: these stubs are no longer needed. man pages should be generated at install time.
  install(DIRECTORY ../doc/man/
    DESTINATION ${CMAKE_INSTALL_MANDIR}/man1
    FILES_MATCHING PATTERN *.1
  )
endif()
