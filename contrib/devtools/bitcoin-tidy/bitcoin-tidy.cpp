// Copyright (c) 2023 Andaluzcoin Developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include "nontrivial-threadlocal.h"

#include <clang-tidy/ClangTidyModule.h>
#include <clang-tidy/ClangTidyModuleRegistry.h>

class AndaluzcoinModule final : public clang::tidy::ClangTidyModule
{
public:
    void addCheckFactories(clang::tidy::ClangTidyCheckFactories& CheckFactories) override
    {
        CheckFactories.registerCheck<andaluzcoin::NonTrivialThreadLocal>("andaluzcoin-nontrivial-threadlocal");
    }
};

static clang::tidy::ClangTidyModuleRegistry::Add<AndaluzcoinModule>
    X("andaluzcoin-module", "Adds andaluzcoin checks.");

volatile int AndaluzcoinModuleAnchorSource = 0;
