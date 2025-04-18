# Copyright (c) 2023-present The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

# Wallet functionality used by andaluzcoind and andaluzcoin-wallet executables.
add_library(andaluzcoin_wallet STATIC EXCLUDE_FROM_ALL
  coincontrol.cpp
  coinselection.cpp
  context.cpp
  crypter.cpp
  db.cpp
  dump.cpp
  external_signer_scriptpubkeyman.cpp
  feebumper.cpp
  fees.cpp
  interfaces.cpp
  load.cpp
  migrate.cpp
  receive.cpp
  rpc/addresses.cpp
  rpc/backup.cpp
  rpc/coins.cpp
  rpc/encrypt.cpp
  rpc/signmessage.cpp
  rpc/spend.cpp
  rpc/transactions.cpp
  rpc/util.cpp
  rpc/wallet.cpp
  scriptpubkeyman.cpp
  spend.cpp
  transaction.cpp
  wallet.cpp
  walletdb.cpp
  walletutil.cpp
)
target_link_libraries(andaluzcoin_wallet
  PRIVATE
    core_interface
    andaluzcoin_common
    univalue
    Boost::headers
    $<TARGET_NAME_IF_EXISTS:USDT::headers>
)

if(NOT USE_SQLITE AND NOT USE_BDB)
  message(FATAL_ERROR "Wallet functionality requested but no BDB or SQLite support available.")
endif()

if(USE_SQLITE)
  target_sources(andaluzcoin_wallet PRIVATE sqlite.cpp)
  target_link_libraries(andaluzcoin_wallet
    PRIVATE
      $<TARGET_NAME_IF_EXISTS:unofficial::sqlite3::sqlite3>
      $<TARGET_NAME_IF_EXISTS:SQLite::SQLite3>
  )
endif()


if(USE_BDB)
  # Ensure that the Berkeley DB variables are defined.
  if(NOT DEFINED DBerkeleyDB_INCLUDE_DIR OR NOT DEFINED DBerkeleyDB_LIBRARY_RELEASE)
    message(FATAL_ERROR "USE_BDB is enabled but DBerkeleyDB_INCLUDE_DIR or DBerkeleyDB_LIBRARY_RELEASE are not defined.")
  endif()

  # Define an imported target for Berkeley DB if not already defined.
  if(NOT TARGET BerkeleyDB::BerkeleyDB)
    add_library(BerkeleyDB::BerkeleyDB STATIC IMPORTED)
    set_target_properties(BerkeleyDB::BerkeleyDB PROPERTIES
      IMPORTED_LOCATION "${DBerkeleyDB_LIBRARY_RELEASE}"
      INTERFACE_INCLUDE_DIRECTORIES "${DBerkeleyDB_INCLUDE_DIR}"
    )
  endif()

  target_sources(andaluzcoin_wallet PRIVATE bdb.cpp salvage.cpp)
  target_link_libraries(andaluzcoin_wallet PUBLIC BerkeleyDB::BerkeleyDB)
endif()


# if(USE_BDB)
#  target_sources(andaluzcoin_wallet PRIVATE bdb.cpp salvage.cpp)
#  target_link_libraries(andaluzcoin_wallet PUBLIC BerkeleyDB::BerkeleyDB)
# endif()
