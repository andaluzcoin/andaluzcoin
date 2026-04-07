// Copyright (c) 2023-present The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <bip324.h>
#include <chainparams.h>
#include <key.h>
#include <pubkey.h>
#include <span.h>
#include <test/util/random.h>
#include <test/util/setup_common.h>
#include <util/strencodings.h>

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <vector>

#include <cstdlib>
#include <climits>

#include <boost/test/unit_test.hpp>

#ifdef GENERATE_BIP324_PACKET_VECTORS
#include <iostream>
#endif


#ifndef GENERATE_BIP324_PACKET_VECTORS
    static int GetEnvInt(const char* name, int def)
    {
        const char* v = std::getenv(name);
        if (!v || !*v) return def;

        char* end = nullptr;
        long x = std::strtol(v, &end, 10);
        if (end == v) return def;                 // not a number
        if (x < INT_MIN) return INT_MIN;
        if (x > INT_MAX) return INT_MAX;
        return (int)x;
    }
#endif

namespace {

struct BIP324Test : BasicTestingSetup {

void TestBIP324PacketVector(
    uint32_t in_idx,
    const std::string& in_priv_ours_hex,
    const std::string& in_ellswift_ours_hex,
    const std::string& in_ellswift_theirs_hex,
    bool in_initiating,
    const std::string& in_contents_hex,
    uint32_t in_multiply,
    const std::string& in_aad_hex,
    bool in_ignore,
    const std::string& mid_send_garbage_hex,
    const std::string& mid_recv_garbage_hex,
    const std::string& out_session_id_hex,
    const std::string& out_ciphertext_hex,
    const std::string& out_ciphertext_endswith_hex)
{
    // ---- vec id + optional filtering FIRST (no parsing overhead on skipped vectors) ----
    static uint32_t vec_id = 0;
    const uint32_t this_vec = vec_id++;

#ifndef GENERATE_BIP324_PACKET_VECTORS
    static const int ONLY_VEC = GetEnvInt("BIP324_ONLY_VEC", -1);
    if (ONLY_VEC >= 0 && this_vec != static_cast<uint32_t>(ONLY_VEC)) return;
#endif

#ifndef GENERATE_BIP324_PACKET_VECTORS
    const auto msgstart = Params().MessageStart();

    BOOST_TEST_CONTEXT("vec=" << this_vec
                      << " in_idx=" << in_idx
                      << " initiating=" << in_initiating
                      << " msgstart=" << HexStr(msgstart))
    {
#endif

        // ---- Parse inputs (always needed) ----
        const auto in_priv_ours = ParseHex(in_priv_ours_hex);
        const auto in_ellswift_ours = ParseHex<std::byte>(in_ellswift_ours_hex);
        const auto in_ellswift_theirs = ParseHex<std::byte>(in_ellswift_theirs_hex);
        const auto in_contents = ParseHex<std::byte>(in_contents_hex);
        const auto in_aad = ParseHex<std::byte>(in_aad_hex);

#ifndef GENERATE_BIP324_PACKET_VECTORS
        // ---- Parse expected outputs only in test mode ----
        const auto mid_send_garbage = ParseHex<std::byte>(mid_send_garbage_hex);
        const auto mid_recv_garbage = ParseHex<std::byte>(mid_recv_garbage_hex);
        const auto out_session_id = ParseHex<std::byte>(out_session_id_hex);
        const auto out_ciphertext = ParseHex<std::byte>(out_ciphertext_hex);
        const auto out_ciphertext_endswith = ParseHex<std::byte>(out_ciphertext_endswith_hex);
#endif

        // ---- Load keys ----
        CKey key;
        key.Set(in_priv_ours.begin(), in_priv_ours.end(), true);
        EllSwiftPubKey ellswift_ours(in_ellswift_ours);
        EllSwiftPubKey ellswift_theirs(in_ellswift_theirs);

        // ---- Encrypting cipher ----
        BIP324Cipher cipher(key, ellswift_ours);
        cipher.Initialize(ellswift_theirs, in_initiating);

#ifdef GENERATE_BIP324_PACKET_VECTORS
        if (!cipher) {
            std::cerr << "BIP324 init failed vec=" << this_vec
                      << " in_idx=" << in_idx
                      << " initiating=" << in_initiating << "\n";
            return;
        }
#else
        BOOST_REQUIRE(cipher);
#endif

        // ---- Foundation truths ----
        const auto sid = cipher.GetSessionID();
        const auto send_term = cipher.GetSendGarbageTerminator();
        const auto recv_term = cipher.GetReceiveGarbageTerminator();

#ifndef GENERATE_BIP324_PACKET_VECTORS
        BOOST_REQUIRE(std::ranges::equal(out_session_id, sid));
        BOOST_REQUIRE(std::ranges::equal(mid_send_garbage, send_term));
        BOOST_REQUIRE(std::ranges::equal(mid_recv_garbage, recv_term));
#endif

        // ---- Seek + Encrypt ----
        std::vector<std::vector<std::byte>> dummies(in_idx);
        for (uint32_t i = 0; i < in_idx; ++i) {
            dummies[i].resize(cipher.EXPANSION);
            cipher.Encrypt({}, {}, true, dummies[i]);
        }

        std::vector<std::byte> contents;
        contents.reserve(in_contents.size() * in_multiply);
        for (uint32_t i = 0; i < in_multiply; ++i) {
            contents.insert(contents.end(), in_contents.begin(), in_contents.end());
        }

        std::vector<std::byte> ciphertext(contents.size() + cipher.EXPANSION);
        cipher.Encrypt(contents, in_aad, in_ignore, ciphertext);

#ifdef GENERATE_BIP324_PACKET_VECTORS
        // print msgstart in dump mode *if you really want it per vector*
        std::cout << "// msgstart=" << HexStr(Params().MessageStart()) << "\n";
#endif

#ifdef GENERATE_BIP324_PACKET_VECTORS
        // ---- Dump mode: print vector call, then stop (no assertions/decrypt loop) ----
        constexpr size_t FULL_MAX = 512;
        constexpr size_t TAIL_BYTES = 64;

        std::string out_ciphertext_hex_gen;
        std::string out_ciphertext_endswith_hex_gen;

        if (ciphertext.size() <= FULL_MAX) {
            out_ciphertext_hex_gen = HexStr(ciphertext);
        } else {
            const auto tail = std::span{ciphertext}.last(std::min<size_t>(TAIL_BYTES, ciphertext.size()));
            out_ciphertext_endswith_hex_gen = HexStr(tail);
        }

        std::cout
            << "    TestBIP324PacketVector(\n"
            << "        " << in_idx << ",\n"
            << "        \"" << in_priv_ours_hex << "\",\n"
            << "        \"" << in_ellswift_ours_hex << "\",\n"
            << "        \"" << in_ellswift_theirs_hex << "\",\n"
            << "        " << (in_initiating ? "true" : "false") << ",\n"
            << "        \"" << in_contents_hex << "\",\n"
            << "        " << in_multiply << ",\n"
            << "        \"" << in_aad_hex << "\",\n"
            << "        " << (in_ignore ? "true" : "false") << ",\n"
            << "        \"" << HexStr(send_term) << "\",\n"
            << "        \"" << HexStr(recv_term) << "\",\n"
            << "        \"" << HexStr(sid) << "\",\n"
            << "        \"" << out_ciphertext_hex_gen << "\",\n"
            << "        \"" << out_ciphertext_endswith_hex_gen << "\");\n";
        return;
#else
        // ---- Verify ciphertext ----
        if (!out_ciphertext.empty()) {
            BOOST_REQUIRE(out_ciphertext == ciphertext);
        } else {
            BOOST_REQUIRE(ciphertext.size() >= out_ciphertext_endswith.size());
            BOOST_REQUIRE(std::ranges::equal(
                out_ciphertext_endswith,
                std::span{ciphertext}.last(out_ciphertext_endswith.size())
            ));
        }

        // ---- Decrypt/error loop ----
        for (unsigned error = 0; error <= 12; ++error) {
            BIP324Cipher dec_cipher(key, ellswift_ours);
            dec_cipher.Initialize(ellswift_theirs, (error == 1) ^ in_initiating, /*self_decrypt=*/true);
            BOOST_REQUIRE(dec_cipher);

            const bool expect_match = (error != 1);
            BOOST_CHECK(std::ranges::equal(out_session_id, dec_cipher.GetSessionID()) == expect_match);
            BOOST_CHECK(std::ranges::equal(mid_send_garbage, dec_cipher.GetSendGarbageTerminator()) == expect_match);
            BOOST_CHECK(std::ranges::equal(mid_recv_garbage, dec_cipher.GetReceiveGarbageTerminator()) == expect_match);

            if (in_idx == 0 && error == 12) continue;
            uint32_t dec_idx = in_idx ^ (error == 12 ? (1U << m_rng.randrange(16)) : 0);

            constexpr auto LEN_LEN = BIP324Cipher::LENGTH_LEN;

            for (uint32_t i = 0; i < dec_idx; ++i) {
                unsigned use_idx = i < in_idx ? i : 0;
                bool dec_ignore{false};
                dec_cipher.DecryptLength(std::span{dummies[use_idx]}.first(LEN_LEN));
                dec_cipher.Decrypt(std::span{dummies[use_idx]}.subspan(LEN_LEN), {}, dec_ignore, {});
            }

            auto to_decrypt = ciphertext;
            if (error >= 2 && error <= 9) {
                to_decrypt[m_rng.randrange(to_decrypt.size())] ^= std::byte(1U << (error - 2));
            }

            uint32_t dec_len = dec_cipher.DecryptLength(std::span{to_decrypt}.first(LEN_LEN));
            to_decrypt.resize(dec_len + cipher.EXPANSION);

            auto dec_aad = in_aad;
            if (error == 10) {
                if (in_aad.empty()) continue;
                dec_aad[m_rng.randrange(dec_aad.size())] ^= std::byte(1U << m_rng.randrange(8));
            }
            if (error == 11) dec_aad.push_back({});

            std::vector<std::byte> decrypted(dec_len);
            bool dec_ignore{false};
            bool dec_ok = dec_cipher.Decrypt(std::span{to_decrypt}.subspan(LEN_LEN), dec_aad, dec_ignore, decrypted);

            BOOST_CHECK(dec_ok == (error == 0));
            if (dec_ok) {
                BOOST_CHECK(decrypted == contents);
                BOOST_CHECK(dec_ignore == in_ignore);
            }
        }
#endif

#ifndef GENERATE_BIP324_PACKET_VECTORS
    }
#endif
} // function TestBIP324PacketVector()
}; // struct BIP324Test


BOOST_FIXTURE_TEST_SUITE(bip324_tests, BIP324Test)

BOOST_AUTO_TEST_CASE(packet_test_vectors)
{
    SelectParams(ChainType::MAIN);

    const std::string magic = HexStr(Params().MessageStart());

#ifndef GENERATE_BIP324_PACKET_VECTORS
    BOOST_TEST_CONTEXT("BIP324 packet vectors: msgstart=" << magic)
    {
        BOOST_REQUIRE_MESSAGE(magic == "b6a96458",
            "Andaluzcoin vectors expected. msgstart=" << magic);

        #include <test/data/bip324_packet_vectors_andaluzcoin.inl>
    }
#else
    std::cout << "BEGIN_BIP324_PACKET_VECTORS\n";
    std::cout << "// msgstart=" << magic << "\n";

    #include <test/data/bip324_packet_vectors_andaluzcoin.inl>

    std::cout << "END_BIP324_PACKET_VECTORS\n";
    BOOST_TEST(true);
    return;
#endif
}

BOOST_AUTO_TEST_SUITE_END()

}  // namespace