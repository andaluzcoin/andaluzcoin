import os
import sys

# ✅ Make sure test_framework is resolvable regardless of working directory
current_dir = os.path.dirname(os.path.abspath(__file__))
functional_dir = os.path.abspath(os.path.join(current_dir, ".."))
if functional_dir not in sys.path:
    sys.path.insert(0, functional_dir)

import json
import subprocess
import hashlib
from io import BytesIO

from test_framework.blocktools import create_block
from test_framework.messages import CBlockHeader
from time import time
from test_framework.messages import uint256_from_str


print("🔍 sys.path[0]:", sys.path[0])
print("🔍 Current file:", __file__)
print("📁 Adding to sys.path:", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from test_framework.messages import CBlockHeader, uint256_from_str, from_hex

RPC_USER = "rpc"
RPC_PASSWORD = "rpc2headers"
RPC_PORT = "18443"
RPC_HOST = "127.0.0.1"

def bits_to_target(bits):
    exponent = bits >> 24
    mantissa = bits & 0xffffff
    if exponent <= 3:
        target = mantissa >> (8 * (3 - exponent))
    else:
        target = mantissa << (8 * (exponent - 3))
    return target

def check_pow(header):
    hash_int = int.from_bytes(header.sha256[::-1], "big")
    target = bits_to_target(header.nBits)
    return hash_int <= target

def bitcoin_cli(command, *args, **kwargs):
    raw = kwargs.pop("raw", False)
    print(f"🧪 bitcoin_cli: command={command}, args={args}, raw={raw}")

    cmd = ["bitcoin-cli", "-regtest", f"-rpcuser={RPC_USER}", f"-rpcpassword={RPC_PASSWORD}", command] + list(map(str, args))
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"❌ bitcoin-cli {command} failed:\n{result.stderr.strip()}")
    return result.stdout.strip() if raw else json.loads(result.stdout)

def reconstruct_header_from_hex(header_hex):
    try:
        header = CBlockHeader()
        header_bytes = bytes.fromhex(header_hex)
        header.deserialize(BytesIO(header_bytes))

        # 🔒 Manually compute double SHA256 since .sha256 is not set
        hash_bytes = hashlib.sha256(hashlib.sha256(header_bytes).digest()).digest()
        header.sha256 = hash_bytes[::-1]  # Reverse for display format (LE)

        return header
    except Exception as e:
        print(f"❌ reconstruct_header_from_hex failed: {e}")
        return None

def main():
    print("🔧 Connecting to regtest node RPC...")
    try:

        tip_height = int(bitcoin_cli("getblockcount", raw=True))
        print(f"📦 Tip height = {tip_height}")
    except Exception as e:
        print(f"❌ Failed to get tip height: {e}")
        return

    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "headers_regtest.dat"))

     # 🧹 Optional: Clear existing file before appending
    open(out_path, "wb").close()

    try:
        with open(out_path, "ab") as f:
            for height in range(tip_height + 1):
                try:
                    block_hash = bitcoin_cli("getblockhash", height, raw=True).strip().lower()
                    header_hex = bitcoin_cli("getblockheader", block_hash, "false", raw=True).strip()

                    if not header_hex or not isinstance(header_hex, str):
                        print(f"⚠️ Skipping height {height}: empty or non-string header_hex = {repr(header_hex)}")
                        continue

                    if not all(c in "0123456789abcdefABCDEF" for c in header_hex.strip()):
                        print(f"❌ Invalid hex at height {height}: {repr(header_hex)}")
                        continue

                    header = reconstruct_header_from_hex(header_hex)
                    
                    if header is None:
                        print(f"⚠️ Skipping height {height}: failed to parse header")
                        continue

                    header.calc_sha256()  # ✅ Make sure sha256 is populated
                    computed_hash = header.sha256.hex()

                    if computed_hash != block_hash:
                        print(f"❌ MISMATCH at height {height}")
                        print(f"   Computed hash: {computed_hash}")
                        print(f"   RPC     hash: {block_hash}")
                        continue

                    if not check_pow(header):
                        print(f"❌ Header {height}: Fails regtest POW — not writing to file.")
                        print(f"   hash  = {computed_hash}")
                        print(f"   nBits = 0x{header.nBits:08x}")
                        continue

                    # ✅ Write valid header
                    f.write(b"main:" + header.serialize())
                    print(f"✅ Header {height}: POW valid, hash={computed_hash}")

                except Exception as inner_e:
                    print(f"❌ Exception at height {height}: {inner_e}")
        
        print(f"✅ Dumped headers 0 through {tip_height} to {out_path}")

        # Assume the last main header is still in `header`
        append_fork_headers(header, count=2)

        self.log.info("🎯 Test completed successfully — headers sent and peer disconnected.")

    except Exception as e:
        print(f"❌ Failed to write headers file: {e}")

def hash_to_hex_le(hash_int):
    return hash_int.to_bytes(32, byteorder="big")[::-1].hex()


def append_fork_headers(base_header: CBlockHeader, count: int = 2):
    fork_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "headers_regtest.dat"))

    with open(fork_path, "ab") as f:
        prev_hash = uint256_from_str(base_header.sha256)  # correct LE parent hash

        for i in range(count):
            fork_header = CBlockHeader()
            fork_header.nVersion = 0x20000000

            # ✅ Assign correctly typed and formatted fields
            fork_header.hashPrevBlock = prev_hash                             # must be uint256
            fork_header.hashMerkleRoot = uint256_from_str(b'\x00' * 32)      # must also be uint256
            fork_header.nTime = base_header.nTime + (i + 1)
            fork_header.nBits = base_header.nBits
            fork_header.nNonce = 0

            fork_header.calc_sha256()
            print(f"🌿 Appending fork header {i}, hash={hash_to_hex_le(fork_header.sha256)}")

            f.write(b"fork:" + fork_header.serialize())

            # set prev_hash for next header (as uint256)
            prev_hash = uint256_from_str(fork_header.sha256.to_bytes(32, "little"))


if __name__ == "__main__":
    main()
