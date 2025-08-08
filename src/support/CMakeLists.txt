# Copyright (c) 2023-present The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

add_library(andaluzcoin_support STATIC
    ${CMAKE_CURRENT_SOURCE_DIR}/lockedpool.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/cleanse.cpp
)

target_include_directories(andaluzcoin_support PUBLIC
    ${CMAKE_SOURCE_DIR}/src
)

