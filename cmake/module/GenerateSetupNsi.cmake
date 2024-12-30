# Copyright (c) 2023-present The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

function(generate_setup_nsi)
  set(abs_top_srcdir ${PROJECT_SOURCE_DIR})
  set(abs_top_builddir ${PROJECT_BINARY_DIR})
  set(CLIENT_URL ${PROJECT_HOMEPAGE_URL})
  set(CLIENT_TARNAME "andaluzcoin")
  set(ANDALUZCOIN_GUI_NAME "andaluzcoin-qt")
  set(ANDALUZCOIN_DAEMON_NAME "andaluzcoind")
  set(ANDALUZCOIN_CLI_NAME "andaluzcoin-cli")
  set(ANDALUZCOIN_TX_NAME "andaluzcoin-tx")
  set(ANDALUZCOIN_WALLET_TOOL_NAME "andaluzcoin-wallet")
  set(ANDALUZCOIN_TEST_NAME "test_andaluzcoin")
  set(EXEEXT ${CMAKE_EXECUTABLE_SUFFIX})
  configure_file(${PROJECT_SOURCE_DIR}/share/setup.nsi.in ${PROJECT_BINARY_DIR}/andaluzcoin-win64-setup.nsi USE_SOURCE_PERMISSIONS @ONLY)
endfunction()
