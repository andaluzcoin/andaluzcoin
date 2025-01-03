// Copyright (c) 2024-present The Andaluzcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef ANDALUZCOIN_TEST_FUZZ_UTIL_CHECK_GLOBALS_H
#define ANDALUZCOIN_TEST_FUZZ_UTIL_CHECK_GLOBALS_H

#include <memory>
#include <optional>
#include <string>

struct CheckGlobalsImpl;
struct CheckGlobals {
    CheckGlobals();
    ~CheckGlobals();
    std::unique_ptr<CheckGlobalsImpl> m_impl;
};

#endif // ANDALUZCOIN_TEST_FUZZ_UTIL_CHECK_GLOBALS_H
