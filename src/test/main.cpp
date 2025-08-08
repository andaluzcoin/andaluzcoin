// Copyright (c) 2011-2022 The Andaluzcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

/**
 * See https://www.boost.org/doc/libs/1_78_0/libs/test/doc/html/boost_test/adv_scenarios/single_header_customizations/multiple_translation_units.html
 */
#undef BOOST_TEST_MODULE
#define BOOST_TEST_MODULE Andaluzcoin Core Test Suite

#include <boost/test/included/unit_test.hpp>

#include <test/util/setup_common.h>

#include <functional>
#include <iostream>
#include <vector>
#include <string>

/** Assign values to the already-declared inline variables */
// Correct assignments to inline variables (declared in setup_common.h)
struct SetupGTestVariables {
    SetupGTestVariables() {
        G_TEST_LOG_FUN = [](const std::string& s) {
            std::cerr << "[TEST LOG] " << s;
        };

        G_TEST_COMMAND_LINE_ARGUMENTS = []() {
            return std::vector<const char*>{};
        };

        G_TEST_GET_FULL_NAME = []() {
            return std::string("andaluzcoin_tests");
        };
    }
};

// Static instance to run during startup
static SetupGTestVariables setup_gtest_vars;

