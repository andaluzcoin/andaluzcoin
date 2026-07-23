#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin post-v31 runtime identity."""

import subprocess
from pathlib import Path

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzIdentityTest(BitcoinTestFramework):
    def find_binary(self, binary_name, *, required=True):
        build_dir = Path(self.config["environment"]["BUILDDIR"])
        exeext = self.config["environment"].get("EXEEXT", "")
        executable_name = f"{binary_name}{exeext}"

        candidates = [
            build_dir / "bin" / executable_name,
            build_dir / "bin" / "Debug" / executable_name,
            build_dir / "bin" / "Release" / executable_name,
            build_dir / "bin" / "RelWithDebInfo" / executable_name,
        ]
        candidates.extend(sorted((build_dir / "bin").glob(f"**/{executable_name}")))

        binary_path = next((candidate for candidate in candidates if candidate.exists()), None)
        if required:
            assert binary_path is not None, candidates
        return binary_path

    def assert_andaluz_version_output(self, binary_path, datadir):
        result = subprocess.run(
            [binary_path, f"-datadir={datadir}", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        version_text = result.stdout + result.stderr
        version_lines = [line for line in version_text.splitlines() if line.strip()]
        assert version_lines, version_text

        product_line = version_lines[0]
        assert "Andaluzcoin Core" in product_line, version_text
        assert "Bitcoin Core" not in product_line, version_text

    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True
        self.chain = ""
        self.extra_args = [[
            "-dnsseed=0",
            "-fixedseeds=0",
            "-connect=0",
        ]]

    def run_test(self):
        expected_genesis_hash = "000000f7dca7651a1397fd0bc99b2a456dbb2d23470834b6290aadec4b46d15c"

        self.log.info("Checking Andaluzcoin mainnet startup chain identity")
        blockchain_info = self.nodes[0].getblockchaininfo()
        assert_equal(blockchain_info["chain"], "main")
        assert_equal(blockchain_info["blocks"], 0)
        assert_equal(blockchain_info["headers"], 0)
        assert_equal(blockchain_info["bestblockhash"], expected_genesis_hash)

        self.log.info("Checking Andaluzcoin mainnet genesis hash")
        assert_equal(self.nodes[0].getblockhash(0), expected_genesis_hash)

        self.log.info("Checking Andaluzcoin P2P runtime identity")
        network_info = self.nodes[0].getnetworkinfo()
        subversion = network_info["subversion"]
        assert subversion.startswith("/AndaluzcoinCore:"), subversion
        assert "Satoshi" not in subversion, subversion
        assert "Bitcoin" not in subversion, subversion
        assert_equal(network_info["connections"], 0)

        self.log.info("Checking Andaluzcoin CLI identity")
        cli_blockchain_info = self.nodes[0].cli.getblockchaininfo()
        assert_equal(cli_blockchain_info["chain"], "main")
        assert_equal(cli_blockchain_info["bestblockhash"], expected_genesis_hash)
        assert_equal(self.nodes[0].cli.getblockhash(0), expected_genesis_hash)

        cli_network_info = self.nodes[0].cli.getnetworkinfo()
        cli_subversion = cli_network_info["subversion"]
        assert cli_subversion.startswith("/AndaluzcoinCore:"), cli_subversion
        assert "Satoshi" not in cli_subversion, cli_subversion
        assert "Bitcoin" not in cli_subversion, cli_subversion

        self.log.info("Checking Andaluzcoin binary version identity")
        bitcoind_path = self.find_binary("bitcoind")
        bitcoin_cli_path = self.find_binary("bitcoin-cli")
        bitcoin_wallet_path = self.find_binary("bitcoin-wallet", required=False)

        version_datadir = Path(self.options.tmpdir) / "andaluz_version_datadir"
        version_datadir.mkdir(parents=True, exist_ok=True)

        self.assert_andaluz_version_output(bitcoind_path, version_datadir)
        self.assert_andaluz_version_output(bitcoin_cli_path, version_datadir)
        if bitcoin_wallet_path is not None:
            self.assert_andaluz_version_output(bitcoin_wallet_path, version_datadir)

        self.log.info("Checking Andaluzcoin RPC config/help identity")
        help_datadir = Path(self.options.tmpdir) / "andaluz_help_datadir"
        help_datadir.mkdir(parents=True, exist_ok=True)
        help_result = subprocess.run(
            [bitcoind_path, f"-datadir={help_datadir}", "-help"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        help_text = help_result.stdout + help_result.stderr
        assert "default: 29443" in help_text, help_text
        assert "default: 8332" not in help_text, help_text


if __name__ == "__main__":
    AndaluzIdentityTest(__file__).main()
