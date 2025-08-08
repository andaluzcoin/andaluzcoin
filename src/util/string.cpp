// Copyright (c) 2019-2022 The Andaluzcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <util/string.h>

#include <string>

namespace util {
void ReplaceAll(std::string& in_out, const std::string& search, const std::string& substitute)
{
    if (search.empty()) return;

    size_t pos = 0;
    while ((pos = in_out.find(search, pos)) != std::string::npos) {
        in_out.replace(pos, search.length(), substitute);
        pos += substitute.length();
    }
}
} // namespace util

