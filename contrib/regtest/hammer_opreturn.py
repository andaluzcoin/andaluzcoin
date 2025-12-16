#!/usr/bin/env python3
import subprocess, json, os, sys, binascii

CLI = ["build/src/andaluzcoin-cli", "-regtest", "-datadir=/tmp/andaluz_regtest"]

def cli(*args, wallet=None, parse=True):
    cmd = CLI[:]
    if wallet:
        cmd += [f"-rpcwallet={wallet}"]
    cmd += list(args)
    out = subprocess.check_output(cmd)
    s = out.decode().strip()
    if not parse:
        return s
    return json.loads(s) if s and s[0] in "[{" else json.loads(f'"{s}"')

def randhex(nbytes):
    return binascii.hexlify(os.urandom(nbytes)).decode()

# Ensure wallet 'mine' is loaded
wallets = cli("listwallets")
if "mine" not in wallets:
    cli("loadwallet", "mine")

# Get a fresh address for change/mining
addr = cli("getnewaddress", wallet="mine", parse=False).strip()

# Ensure spendable funds (mature coinbase)
height = int(cli("getblockcount"))
if height < 101:
    cli("generatetoaddress", str(101 - height), addr, parse=False)

# Workload knobs (override via env: TXS, BYTES)
TXS   = int(os.environ.get("TXS", "40"))     # number of transactions
BYTES = int(os.environ.get("BYTES", "20000"))# OP_RETURN payload bytes (~20 KB each)

print(f"Sending {TXS} txs with ~{BYTES}B OP_RETURN each…")
for i in range(1, TXS + 1):
    datahex = randhex(BYTES)
    raw = cli("createrawtransaction", "[]", f'[{{"data":"{datahex}"}}]', wallet="mine", parse=False)
    funded = cli("fundrawtransaction", raw, '{"replaceable":false}')
    signed = cli("signrawtransactionwithwallet", funded["hex"])
    txid = cli("sendrawtransaction", signed["hex"], parse=False).strip()
    print(f"[{i}/{TXS}] {txid}")

print("Mining a block to pack them…")
blk = cli("generatetoaddress", "1", addr)[0]
info = cli("getblock", blk, "2")
print(f"Mined block {blk}")
print(f"  txs in block: {len(info['tx'])}")
print(f"  block size:   {info['size']} bytes")
print(f"  block weight: {info['weight']}")
