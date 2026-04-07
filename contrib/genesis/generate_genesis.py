#!/usr/bin/env python3
import hashlib
from struct import pack

def sha256d(b: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(b).digest()).digest()

def ser_varint(n: int) -> bytes:
    if n < 0xfd: return pack("<B", n)
    if n <= 0xffff: return b"\xfd" + pack("<H", n)
    if n <= 0xffffffff: return b"\xfe" + pack("<I", n)
    return b"\xff" + pack("<Q", n)

def bits_to_target(bits: int) -> int:
    exp = (bits >> 24) & 0xff
    mant = bits & 0x007fffff
    if bits & 0x00800000:
        raise ValueError("negative/invalid bits")
    if exp <= 3:
        return mant >> (8 * (3 - exp))
    return mant << (8 * (exp - 3))

def pushdata(data: bytes) -> bytes:
    l = len(data)
    if l < 0x4c:
        return bytes([l]) + data
    raise ValueError("timestamp too long for this simple script")

def script_num(n: int) -> bytes:
    # minimal little-endian signed-magnitude, but for positive small ints this is simple
    if n == 0: return b""
    out = bytearray()
    while n:
        out.append(n & 0xff)
        n >>= 8
    if out[-1] & 0x80:
        out.append(0)
    return bytes(out)

def make_genesis(psz: str, pubkey_hex: str, ntime: int, nbits: int, nnonce: int, reward_sats: int, version: int = 1):
    psz_b = psz.encode("utf-8")
    pubkey = bytes.fromhex(pubkey_hex)

    # scriptSig: push(486604799) push(4) push(timestamp)
    scr = b""
    scr += pushdata(script_num(486604799))
    scr += pushdata(script_num(4))
    scr += pushdata(psz_b)

    # scriptPubKey: push(pubkey) OP_CHECKSIG
    scriptpub = pushdata(pubkey) + b"\xac"

    # coinbase tx (legacy)
    tx = b""
    tx += pack("<I", 1)                 # version
    tx += ser_varint(1)                 # vin count
    tx += b"\x00"*32                    # prevout hash
    tx += pack("<I", 0xffffffff)        # prevout n
    tx += ser_varint(len(scr)) + scr    # scriptSig
    tx += pack("<I", 0xffffffff)        # sequence
    tx += ser_varint(1)                 # vout count
    tx += pack("<q", reward_sats)       # value
    tx += ser_varint(len(scriptpub)) + scriptpub
    tx += pack("<I", 0)                 # locktime

    tx_hash = sha256d(tx)               # internal bytes
    mrkl = tx_hash                      # single-tx merkle root

    header = b""
    header += pack("<I", version)
    header += b"\x00"*32
    header += mrkl
    header += pack("<I", ntime)
    header += pack("<I", nbits)
    header += pack("<I", nnonce)

    bhash = sha256d(header)

    return {
        "txid": tx_hash[::-1].hex(),
        "merkle_root": mrkl[::-1].hex(),
        "hash": bhash[::-1].hex(),
        "hash_bytes_le_int": int.from_bytes(bhash, "little"),
    }

if __name__ == "__main__":
    PSZ = "Andaluzcoin 30/Jan/2026 Viva Al-Andalus"
    # You can keep Bitcoin’s genesis pubkey for now; changing it is optional.
    PUBKEY = "04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f"

    NTIME = 1769731200
    NBITS = 0x1f00ffff
    REWARD = 50 * 100_000_000
    target = bits_to_target(NBITS)

    nonce = 0
    while True:
        g = make_genesis(PSZ, PUBKEY, NTIME, NBITS, nonce, REWARD)
        if g["hash_bytes_le_int"] <= target:
            print("FOUND")
            print("nonce:", nonce)
            print("genesis_hash:", g["hash"])
            print("merkle_root:", g["merkle_root"])
            print("txid:", g["txid"])
            break
        nonce += 1
