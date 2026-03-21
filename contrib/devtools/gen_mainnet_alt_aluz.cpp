#include <array>
#include <atomic>
#include <chrono>
#include <cctype>
#include <cstdint>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

#include <openssl/sha.h>
#include <boost/multiprecision/cpp_int.hpp>

namespace fs = std::filesystem;
using boost::multiprecision::cpp_int;

static constexpr const char* INPUT_CADENCE_PATH = "test/functional/data/mainnet_alt.json";
static constexpr const char* TEMP_OUTPUT_PATH   = "test/functional/data/mainnet_alt.aluz.tmp.json";
static constexpr const char* FINAL_OUTPUT_PATH  = "test/functional/data/mainnet_alt.json";

static constexpr const char* GENESIS_HASH_HEX =
    "000000cd6370144985ca6e987bedcf8abb4234ed6631f0011bd04b382a448c83";

static constexpr uint32_t GENESIS_TIME  = 1769731200;
static constexpr uint32_t GENESIS_NBITS = 0x1e0377ae;

static constexpr const char* POW_LIMIT_HEX =
    "0000ffff00000000000000000000000000000000000000000000000000000000";

static constexpr int32_t BLOCK_VERSION = 0x20000000;

static constexpr uint64_t COIN          = 100000000ULL;
static constexpr uint64_t BLOCK_SUBSIDY = 50ULL * COIN;

static constexpr uint32_t HALVING_INTERVAL        = 210000;
static constexpr uint32_t TARGET_TIMESPAN         = 14 * 24 * 60 * 60;
static constexpr uint32_t TARGET_SPACING          = 10 * 60;
static constexpr uint32_t FIRST_BLOCK_GAP         = 126;
static constexpr uint32_t TOTAL_BLOCKS            = 2016;
static constexpr uint32_t PROGRESS_INTERVAL_SECONDS = 60;

static constexpr const char* COINBASE_SCRIPT_PUBKEY_HEX =
    "76a914eadbac7f36c37e39361168b7aaee3cb24a25312d88ac";

using Hash32 = std::array<uint8_t, 32>;

struct ResumeState {
    uint32_t completed{0};
    std::string prev_hash_hex{GENESIS_HASH_HEX};
    std::vector<uint32_t> nonces;
    std::vector<uint32_t> timestamps;
};

struct Options {
    uint32_t threads{0};
    bool fresh{false};
};

// ------------------------------------------------------------
// Hex helpers
// ------------------------------------------------------------

static int HexDigit(char c)
{
    if (c >= '0' && c <= '9') return c - '0';
    c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    if (c >= 'a' && c <= 'f') return 10 + (c - 'a');
    throw std::runtime_error("Invalid hex digit");
}

static std::vector<uint8_t> HexToBytes(std::string hex)
{
    if (hex.size() % 2 != 0)
        throw std::runtime_error("Hex string must have even length");

    std::vector<uint8_t> out;
    out.reserve(hex.size() / 2);

    for (size_t i = 0; i < hex.size(); i += 2) {
        out.push_back(static_cast<uint8_t>(
            (HexDigit(hex[i]) << 4) | HexDigit(hex[i + 1])
        ));
    }
    return out;
}

static std::string BytesToHex(const uint8_t* data, size_t len)
{
    std::ostringstream oss;
    oss << std::hex << std::setfill('0');

    for (size_t i = 0; i < len; ++i)
        oss << std::setw(2) << static_cast<unsigned>(data[i]);

    return oss.str();
}

static std::string ReverseHex(const Hash32& h)
{
    std::ostringstream oss;
    oss << std::hex << std::setfill('0');

    for (auto it = h.rbegin(); it != h.rend(); ++it)
        oss << std::setw(2) << static_cast<unsigned>(*it);

    return oss.str();
}

// ------------------------------------------------------------
// Hashing
// ------------------------------------------------------------

static Hash32 DoubleSHA256(const uint8_t* data, size_t len)
{
    Hash32 first{};
    Hash32 second{};

    SHA256(data, len, first.data());
    SHA256(first.data(), first.size(), second.data());

    return second;
}

// ------------------------------------------------------------
// Serialization helpers
// ------------------------------------------------------------

static void AppendLE32(std::vector<uint8_t>& out, uint32_t v)
{
    out.push_back(static_cast<uint8_t>(v));
    out.push_back(static_cast<uint8_t>(v >> 8));
    out.push_back(static_cast<uint8_t>(v >> 16));
    out.push_back(static_cast<uint8_t>(v >> 24));
}

static void AppendLE64(std::vector<uint8_t>& out, uint64_t v)
{
    for (int i = 0; i < 8; ++i)
        out.push_back(static_cast<uint8_t>(v >> (8 * i)));
}

static void AppendVarInt(std::vector<uint8_t>& out, uint64_t v)
{
    if (v < 0xfd) {
        out.push_back(static_cast<uint8_t>(v));
    } else if (v <= 0xffff) {
        out.push_back(0xfd);
        out.push_back(static_cast<uint8_t>(v));
        out.push_back(static_cast<uint8_t>(v >> 8));
    } else if (v <= 0xffffffffULL) {
        out.push_back(0xfe);
        AppendLE32(out, static_cast<uint32_t>(v));
    } else {
        out.push_back(0xff);
        AppendLE64(out, v);
    }
}

static std::vector<uint8_t> SerializeScriptNum(int64_t value)
{
    if (value == 0) return {};

    std::vector<uint8_t> result;
    bool neg = value < 0;
    uint64_t absvalue = neg ? static_cast<uint64_t>(-value)
                            : static_cast<uint64_t>(value);

    while (absvalue) {
        result.push_back(static_cast<uint8_t>(absvalue & 0xff));
        absvalue >>= 8;
    }

    if (result.back() & 0x80) {
        result.push_back(neg ? 0x80 : 0x00);
    } else if (neg) {
        result.back() |= 0x80;
    }

    return result;
}

static std::vector<uint8_t> ScriptBIP34CoinbaseHeight(uint32_t height)
{
    std::vector<uint8_t> script;

    if (height <= 16) {
        script.push_back(static_cast<uint8_t>(0x50 + height)); // OP_N
        script.push_back(0x00);                                 // OP_0 padding
        return script;
    }

    const auto num = SerializeScriptNum(height);
    script.push_back(static_cast<uint8_t>(num.size()));
    script.insert(script.end(), num.begin(), num.end());

    return script;
}

static uint64_t CoinbaseValue(uint32_t height)
{
    uint64_t reward = BLOCK_SUBSIDY;
    const uint32_t halvings = height / HALVING_INTERVAL;
    reward >>= halvings;
    return reward;
}

static std::vector<uint8_t> SerializeCoinbaseTx(
    uint32_t height,
    const std::vector<uint8_t>& script_pubkey
)
{
    std::vector<uint8_t> tx;
    tx.reserve(128);

    // version
    AppendLE32(tx, 2);

    // vin
    AppendVarInt(tx, 1);
    tx.insert(tx.end(), 32, 0x00);       // null prevout hash
    AppendLE32(tx, 0xffffffffU);        // null prevout index

    const auto script_sig = ScriptBIP34CoinbaseHeight(height);
    AppendVarInt(tx, script_sig.size());
    tx.insert(tx.end(), script_sig.begin(), script_sig.end());

    AppendLE32(tx, 0xffffffffU);        // sequence

    // vout
    AppendVarInt(tx, 1);
    AppendLE64(tx, CoinbaseValue(height));
    AppendVarInt(tx, script_pubkey.size());
    tx.insert(tx.end(), script_pubkey.begin(), script_pubkey.end());

    AppendLE32(tx, 0);                  // nLockTime

    return tx;
}

// ------------------------------------------------------------
// File helpers
// ------------------------------------------------------------

static std::string ReadTextFile(const fs::path& path)
{
    std::ifstream in(path);
    if (!in)
        throw std::runtime_error("Failed to open file: " + path.string());

    std::ostringstream ss;
    ss << in.rdbuf();
    return ss.str();
}

static void AtomicWriteFile(const fs::path& path, const std::string& contents)
{
    const fs::path tmp = path.string() + ".writing";

    {
        std::ofstream out(tmp, std::ios::binary | std::ios::trunc);
        if (!out)
            throw std::runtime_error("Failed to open temp file: " + tmp.string());

        out << contents;
        out.flush();

        if (!out)
            throw std::runtime_error("Failed while writing temp file: " + tmp.string());
    }

    fs::rename(tmp, path);
}

// ------------------------------------------------------------
// JSON parsing helpers (minimal, manual)
// ------------------------------------------------------------

static std::vector<uint32_t> ParseJsonArrayU32(
    const std::string& text,
    const std::string& key
)
{
    const std::string needle = "\"" + key + "\"";
    const size_t key_pos = text.find(needle);

    if (key_pos == std::string::npos)
        throw std::runtime_error("Key not found: " + key);

    const size_t open  = text.find('[', key_pos);
    const size_t close = text.find(']', open);

    if (open == std::string::npos || close == std::string::npos || close < open)
        throw std::runtime_error("Invalid JSON array for key: " + key);

    std::vector<uint32_t> values;
    uint64_t current = 0;
    bool in_number = false;

    for (size_t i = open + 1; i < close; ++i) {
        const char c = text[i];

        if (std::isdigit(static_cast<unsigned char>(c))) {
            current = current * 10 + static_cast<uint64_t>(c - '0');
            in_number = true;
        } else {
            if (in_number) {
                values.push_back(static_cast<uint32_t>(current));
                current = 0;
                in_number = false;
            }
        }
    }

    if (in_number)
        values.push_back(static_cast<uint32_t>(current));

    return values;
}

static std::optional<uint32_t> ParseJsonU32(
    const std::string& text,
    const std::string& key
)
{
    const std::string needle = "\"" + key + "\"";
    const size_t key_pos = text.find(needle);

    if (key_pos == std::string::npos)
        return std::nullopt;

    const size_t colon = text.find(':', key_pos);
    if (colon == std::string::npos)
        return std::nullopt;

    size_t i = colon + 1;
    while (i < text.size() && std::isspace(static_cast<unsigned char>(text[i])))
        ++i;

    uint64_t value = 0;
    bool found = false;

    while (i < text.size() && std::isdigit(static_cast<unsigned char>(text[i]))) {
        found = true;
        value = value * 10 + static_cast<uint64_t>(text[i] - '0');
        ++i;
    }

    if (!found)
        return std::nullopt;

    return static_cast<uint32_t>(value);
}

static std::optional<std::string> ParseJsonString(
    const std::string& text,
    const std::string& key
)
{
    const std::string needle = "\"" + key + "\"";
    const size_t key_pos = text.find(needle);

    if (key_pos == std::string::npos)
        return std::nullopt;

    const size_t colon = text.find(':', key_pos);
    const size_t first_quote = text.find('"', colon + 1);

    if (colon == std::string::npos || first_quote == std::string::npos)
        return std::nullopt;

    const size_t second_quote = text.find('"', first_quote + 1);
    if (second_quote == std::string::npos)
        return std::nullopt;

    return text.substr(first_quote + 1, second_quote - first_quote - 1);
}

// ------------------------------------------------------------
// Cadence loading
// ------------------------------------------------------------

static std::vector<uint32_t> LoadCadenceTemplate()
{
    const std::string text = ReadTextFile(INPUT_CADENCE_PATH);
    const auto timestamps = ParseJsonArrayU32(text, "timestamps");

    if (timestamps.size() != TOTAL_BLOCKS)
        throw std::runtime_error("Expected 2016 timestamps in source cadence file");

    return timestamps;
}

static std::vector<uint32_t> ShiftCadenceToGenesis(
    const std::vector<uint32_t>& old_ts
)
{
    std::vector<uint32_t> out;
    out.reserve(old_ts.size());

    out.push_back(GENESIS_TIME + FIRST_BLOCK_GAP);

    for (size_t i = 1; i < old_ts.size(); ++i) {
        const uint32_t delta = old_ts[i] - old_ts[i - 1];
        out.push_back(out.back() + delta);
    }

    return out;
}

// ------------------------------------------------------------
// Difficulty / target math
// ------------------------------------------------------------

static cpp_int HexToCppInt(const std::string& hex)
{
    cpp_int x = 0;

    for (char c : hex) {
        if (std::isspace(static_cast<unsigned char>(c)))
            continue;

        x <<= 4;
        x += HexDigit(c);
    }

    return x;
}

static cpp_int CompactToTarget(uint32_t nbits)
{
    const uint32_t exponent = nbits >> 24;
    const uint32_t mantissa = nbits & 0x007fffff;

    if (nbits & 0x00800000U)
        throw std::runtime_error("Negative compact target unsupported");

    cpp_int target = mantissa;

    if (exponent <= 3) {
        target >>= 8 * (3 - exponent);
    } else {
        target <<= 8 * (exponent - 3);
    }

    return target;
}

static uint32_t TargetToCompact(const cpp_int& target)
{
    if (target == 0)
        return 0;

    cpp_int tmp = target;
    size_t size = 0;

    while (tmp > 0) {
        ++size;
        tmp >>= 8;
    }

    uint32_t compact = 0;

    if (size <= 3) {
        compact = static_cast<uint32_t>(
            target.convert_to<uint64_t>() << (8 * (3 - size))
        );
    } else {
        compact = static_cast<uint32_t>(
            (target >> (8 * (size - 3))).convert_to<uint64_t>()
        );
    }

    if (compact & 0x00800000U) {
        compact >>= 8;
        ++size;
    }

    compact |= static_cast<uint32_t>(size) << 24;
    return compact;
}

static Hash32 TargetToBigEndianBytes(const cpp_int& target)
{
    Hash32 out{};
    cpp_int value = target;

    for (int i = 31; i >= 0 && value > 0; --i) {
        out[i] = static_cast<uint8_t>((value & 0xff).convert_to<uint32_t>());
        value >>= 8;
    }

    return out;
}

static bool HashMeetsTarget(const Hash32& hash_raw, const Hash32& target_be)
{
    for (size_t i = 0; i < 32; ++i) {
        const uint8_t hb = hash_raw[31 - i]; // convert to big-endian

        if (hb < target_be[i]) return true;
        if (hb > target_be[i]) return false;
    }
    return true;
}

static uint32_t CalculateRetargetBits(
    uint32_t last_time,
    uint32_t first_time,
    uint32_t old_nbits
)
{
    int64_t actual_timespan =
        static_cast<int64_t>(last_time) - static_cast<int64_t>(first_time);

    if (actual_timespan < static_cast<int64_t>(TARGET_TIMESPAN / 4))
        actual_timespan = TARGET_TIMESPAN / 4;

    if (actual_timespan > static_cast<int64_t>(TARGET_TIMESPAN * 4))
        actual_timespan = TARGET_TIMESPAN * 4;

    const cpp_int pow_limit = HexToCppInt(POW_LIMIT_HEX);

    cpp_int new_target = CompactToTarget(old_nbits);
    new_target *= actual_timespan;
    new_target /= TARGET_TIMESPAN;

    if (new_target > pow_limit)
        new_target = pow_limit;

    return TargetToCompact(new_target);
}

// ------------------------------------------------------------
// Block header builder
// ------------------------------------------------------------

static std::array<uint8_t, 80> BuildHeader(
    int32_t version,
    const std::string& prev_hash_hex,
    const Hash32& merkle_raw,
    uint32_t ntime,
    uint32_t nbits,
    uint32_t nonce
)
{
    std::array<uint8_t, 80> header{};
    std::vector<uint8_t> tmp;
    tmp.reserve(80);

    AppendLE32(tmp, static_cast<uint32_t>(version));

    auto prev_be = HexToBytes(prev_hash_hex);
    if (prev_be.size() != 32)
        throw std::runtime_error("prev_hash hex must be 32 bytes");

    tmp.insert(tmp.end(), prev_be.rbegin(), prev_be.rend());
    tmp.insert(tmp.end(), merkle_raw.begin(), merkle_raw.end());

    AppendLE32(tmp, ntime);
    AppendLE32(tmp, nbits);
    AppendLE32(tmp, nonce);

    if (tmp.size() != 80)
        throw std::runtime_error("header serialization size mismatch");

    std::copy(tmp.begin(), tmp.end(), header.begin());
    return header;
}

// ------------------------------------------------------------
// Checkpoint JSON builders
// ------------------------------------------------------------

static std::string BuildCheckpointJson(
    uint32_t completed,
    const std::string& prev_hash_hex,
    uint32_t retarget_bits,
    const std::vector<uint32_t>& timestamps,
    const std::vector<uint32_t>& nonces
)
{
    std::ostringstream oss;
    oss << "{\n";
    oss << "  \"completed\": " << completed << ",\n";
    oss << "  \"prev_hash\": \"" << prev_hash_hex << "\",\n";
    oss << "  \"retarget_nbits\": " << retarget_bits << ",\n";
    oss << "  \"timestamps\": [\n";

    for (size_t i = 0; i < timestamps.size(); ++i) {
        oss << "    " << timestamps[i];
        if (i + 1 != timestamps.size()) oss << ",";
        oss << "\n";
    }

    oss << "  ],\n";
    oss << "  \"nonces\": [\n";

    for (size_t i = 0; i < nonces.size(); ++i) {
        oss << "    " << nonces[i];
        if (i + 1 != nonces.size()) oss << ",";
        oss << "\n";
    }

    oss << "  ]\n";
    oss << "}\n";
    return oss.str();
}

static std::string BuildFinalJson(
    const std::vector<uint32_t>& timestamps,
    const std::vector<uint32_t>& nonces
)
{
    std::ostringstream oss;
    oss << "{\n";
    oss << "  \"timestamps\": [\n";

    for (size_t i = 0; i < timestamps.size(); ++i) {
        oss << "    " << timestamps[i];
        if (i + 1 != timestamps.size()) oss << ",";
        oss << "\n";
    }

    oss << "  ],\n";
    oss << "  \"nonces\": [\n";

    for (size_t i = 0; i < nonces.size(); ++i) {
        oss << "    " << nonces[i];
        if (i + 1 != nonces.size()) oss << ",";
        oss << "\n";
    }

    oss << "  ]\n";
    oss << "}\n";
    return oss.str();
}

// ------------------------------------------------------------
// Resume state loader
// ------------------------------------------------------------

static std::optional<ResumeState> LoadResumeState(
    const std::vector<uint32_t>& expected_timestamps
)
{
    if (!fs::exists(TEMP_OUTPUT_PATH))
        return std::nullopt;

    const std::string text = ReadTextFile(TEMP_OUTPUT_PATH);

    ResumeState state;
    state.timestamps = ParseJsonArrayU32(text, "timestamps");
    state.nonces     = ParseJsonArrayU32(text, "nonces");

    const auto completed = ParseJsonU32(text, "completed");
    const auto prev_hash = ParseJsonString(text, "prev_hash");

    if (!completed || !prev_hash)
        throw std::runtime_error("Resume file missing completed or prev_hash");

    state.completed     = *completed;
    state.prev_hash_hex = *prev_hash;

    if (state.timestamps != expected_timestamps)
        throw std::runtime_error("Resume file timestamps do not match cadence");

    if (state.completed != state.nonces.size())
        throw std::runtime_error("Resume file completed count mismatch");

    if (state.completed > TOTAL_BLOCKS)
        throw std::runtime_error("Resume file completed count invalid");

    return state;
}

// ------------------------------------------------------------
// Mining loop
// ------------------------------------------------------------

static uint32_t MineNonce(
    uint32_t height,
    const std::array<uint8_t, 80>& header_template,
    const Hash32& target_be,
    uint32_t threads
)
{
    std::atomic<bool> found{false};
    std::atomic<uint32_t> found_nonce{0};

    std::vector<std::atomic<uint32_t>> cursors(threads);
    for (uint32_t i = 0; i < threads; ++i)
        cursors[i].store(i, std::memory_order_relaxed);

    auto worker = [&](uint32_t tid) {
        std::array<uint8_t, 80> header = header_template;
        uint64_t nonce = tid;
        uint64_t iter  = 0;

        while (nonce <= 0xffffffffULL && !found.load(std::memory_order_relaxed)) {
            header[76] = static_cast<uint8_t>(nonce);
            header[77] = static_cast<uint8_t>(nonce >> 8);
            header[78] = static_cast<uint8_t>(nonce >> 16);
            header[79] = static_cast<uint8_t>(nonce >> 24);

            const auto h = DoubleSHA256(header.data(), header.size());
            if (HashMeetsTarget(h, target_be)) {
                const bool already = found.exchange(true, std::memory_order_relaxed);
                if (!already)
                    found_nonce.store(static_cast<uint32_t>(nonce), std::memory_order_relaxed);
                return;
            }

            nonce += threads;
            ++iter;

            if ((iter & ((1u << 20) - 1)) == 0) {
                cursors[tid].store(
                    static_cast<uint32_t>(nonce > 0xffffffffULL ? 0xffffffffU : nonce),
                    std::memory_order_relaxed
                );
            }
        }
    };

    std::vector<std::thread> pool;
    pool.reserve(threads);

    for (uint32_t i = 0; i < threads; ++i)
        pool.emplace_back(worker, i);

    const auto start = std::chrono::steady_clock::now();

    while (!found.load(std::memory_order_relaxed)) {
        std::this_thread::sleep_for(std::chrono::seconds(PROGRESS_INTERVAL_SECONDS));

        if (found.load(std::memory_order_relaxed))
            break;

        const auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::steady_clock::now() - start
        ).count();

        uint32_t max_nonce = 0;
        for (uint32_t i = 0; i < threads; ++i)
            max_nonce = std::max(max_nonce, cursors[i].load(std::memory_order_relaxed));

        std::cout << "[progress] height=" << height
                  << " elapsed=" << elapsed << "s"
                  << " highest_nonce_seen~" << max_nonce
                  << std::endl;
    }

    for (auto& t : pool)
        t.join();

    if (!found.load(std::memory_order_relaxed))
        throw std::runtime_error("Failed to find valid nonce for height " + std::to_string(height));

    return found_nonce.load(std::memory_order_relaxed);
}

// ------------------------------------------------------------
// CLI options
// ------------------------------------------------------------

static Options ParseOptions(int argc, char** argv)
{
    Options opts;
    opts.threads = std::max(1u, std::thread::hardware_concurrency());

    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];

        if (arg == "--fresh") {
            opts.fresh = true;
        } else if (arg == "--threads") {
            if (i + 1 >= argc)
                throw std::runtime_error("--threads requires a value");

            opts.threads = static_cast<uint32_t>(std::stoul(argv[++i]));
            if (opts.threads == 0)
                throw std::runtime_error("--threads must be >= 1");
        } else {
            throw std::runtime_error("Unknown argument: " + arg);
        }
    }

    return opts;
}

// ------------------------------------------------------------
// Main
// ------------------------------------------------------------

int main(int argc, char** argv)
{
    try {
        const Options opts = ParseOptions(argc, argv);

        if (opts.fresh && fs::exists(TEMP_OUTPUT_PATH))
            fs::remove(TEMP_OUTPUT_PATH);

        const auto source_timestamps = LoadCadenceTemplate();
        const auto new_timestamps    = ShiftCadenceToGenesis(source_timestamps);

        const uint32_t retarget_bits = CalculateRetargetBits(
            new_timestamps[2014],   // height 2015
            GENESIS_TIME,
            GENESIS_NBITS
        );

        std::cout << "Threads        : " << opts.threads << "\n";
        std::cout << "Initial nBits  : 0x" << std::hex << GENESIS_NBITS << std::dec << "\n";
        std::cout << "Retarget nBits : 0x" << std::hex << retarget_bits << std::dec << "\n";
        std::cout << "First timestamp: " << new_timestamps.front() << "\n";
        std::cout << "Last timestamp : " << new_timestamps.back() << "\n";

        const auto script_pubkey = HexToBytes(COINBASE_SCRIPT_PUBKEY_HEX);

        ResumeState state;

        if (auto resume = LoadResumeState(new_timestamps)) {
            state = *resume;
            std::cout << "Resuming from height "
                      << (state.completed + 1)
                      << " using " << TEMP_OUTPUT_PATH << "\n";
        } else {
            state.timestamps = new_timestamps;
            std::cout << "Starting fresh\n";
        }

        for (uint32_t height = state.completed + 1; height <= TOTAL_BLOCKS; ++height) {
            const uint32_t nbits =
                (height < TOTAL_BLOCKS) ? GENESIS_NBITS : retarget_bits;

            const auto coinbase_tx = SerializeCoinbaseTx(height, script_pubkey);
            const Hash32 txid_raw  = DoubleSHA256(coinbase_tx.data(), coinbase_tx.size());

            const auto header_template = BuildHeader(
                BLOCK_VERSION,
                state.prev_hash_hex,
                txid_raw,                 // merkle root
                state.timestamps[height - 1],
                nbits,
                0
            );

            const auto start = std::chrono::steady_clock::now();

            const cpp_int target_int = CompactToTarget(nbits);
            const Hash32 target_be   = TargetToBigEndianBytes(target_int);

            const uint32_t nonce = MineNonce(
                height,
                header_template,
                target_be,
                opts.threads
            );

            auto solved_header = header_template;
            solved_header[76] = static_cast<uint8_t>(nonce);
            solved_header[77] = static_cast<uint8_t>(nonce >> 8);
            solved_header[78] = static_cast<uint8_t>(nonce >> 16);
            solved_header[79] = static_cast<uint8_t>(nonce >> 24);

            const Hash32 block_hash_raw =
                DoubleSHA256(solved_header.data(), solved_header.size());

            const std::string block_hash_hex = ReverseHex(block_hash_raw);

            const auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(
                std::chrono::steady_clock::now() - start
            ).count();

            state.nonces.push_back(nonce);
            state.completed     = height;
            state.prev_hash_hex = block_hash_hex;

            AtomicWriteFile(
                TEMP_OUTPUT_PATH,
                BuildCheckpointJson(
                    state.completed,
                    state.prev_hash_hex,
                    retarget_bits,
                    state.timestamps,
                    state.nonces
                )
            );

            std::cout << "Solved height "
                      << std::setw(4) << height
                      << " time=" << state.timestamps[height - 1]
                      << " bits=0x" << std::hex << nbits << std::dec
                      << " nonce=" << nonce
                      << " hash=" << block_hash_hex
                      << " elapsed=" << elapsed << "s"
                      << std::endl;
        }

        AtomicWriteFile(
            FINAL_OUTPUT_PATH,
            BuildFinalJson(state.timestamps, state.nonces)
        );

        std::cout << "\nDone.\n";
        std::cout << "Wrote final file : " << FINAL_OUTPUT_PATH << "\n";
        std::cout << "Checkpoint file  : " << TEMP_OUTPUT_PATH << "\n";
        std::cout << "Retarget nBits   : 0x" << std::hex << retarget_bits << std::dec << "\n";

        return 0;
    }
    catch (const std::exception& e) {
        std::cerr << "ERROR: " << e.what() << "\n";
        return 1;
    }
}