#!/usr/bin/env python3
# Copyright (c) 2022-present The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import subprocess

from test_framework.blocktools import create_block, create_coinbase
from test_framework.test_framework import BitcoinTestFramework

class BitcoinChainstateTest(BitcoinTestFramework):
    def skip_test_if_missing_module(self):
        self.skip_if_no_bitcoin_chainstate()

    def set_test_params(self):
        self.setup_clean_chain = True
        self.chain = ""
        self.num_nodes = 1
        # Set prune to avoid disk space warning.
        self.extra_args = [["-prune=550"]]

    def add_block(self, datadir, input, expected_stderr):
        proc = subprocess.Popen(
            self.get_binaries().chainstate_argv() + [datadir],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate(input=input + "\n", timeout=5)
        self.log.debug("STDOUT: {0}".format(stdout.strip("\n")))
        self.log.info("STDERR: {0}".format(stderr.strip("\n")))

        if expected_stderr not in stderr:
            raise AssertionError(f"Expected stderr output {expected_stderr} does not partially match stderr:\n{stderr}")

    def run_test(self):
        node = self.nodes[0]
        datadir = node.cli.datadir

        # Build a synthetic child block on top of the actual chain genesis.
        genesis_hash = node.getblockhash(0)
        genesis_header = node.getblockheader(genesis_hash)

        block = create_block(
            hashprev=int(genesis_hash, 16),
            coinbase=create_coinbase(height=1),
            ntime=genesis_header["time"] + 1,
        )
        block.nBits = int(genesis_header["bits"], 16)
        block.solve()
        block_one = block.serialize().hex()

        node.stop_node()

        self.log.info(f"Testing bitcoin-chainstate {self.get_binaries().chainstate_argv()} with datadir: {datadir}")
        self.add_block(datadir, block_one, "Block has not yet been rejected")
        self.add_block(datadir, block_one, "duplicate")
        self.add_block(datadir, "00", "Block decode failed")
        self.add_block(datadir, "", "Empty line found")

if __name__ == "__main__":
    BitcoinChainstateTest(__file__).main()
