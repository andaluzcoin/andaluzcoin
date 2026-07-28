#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin coinbase maturity and spend identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzCoinbaseMaturitySpendIdentityTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True
        self.chain = "regtest"
        self.wallet_names = []
        self.extra_args = [[
            "-dnsseed=0",
            "-fixedseeds=0",
            "-connect=0",
            "-fallbackfee=0.0001",
        ]]

    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    def assert_andaluz_runtime_identity(self):
        assert_equal(self.nodes[0].getblockchaininfo()["chain"], "regtest")

        subversion = self.nodes[0].getnetworkinfo()["subversion"]
        assert subversion.startswith("/AndaluzcoinCore:"), subversion
        assert "Satoshi" not in subversion, subversion
        assert "Bitcoin" not in subversion, subversion

    def run_test(self):
        self.log.info("Checking initial Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()
        assert_equal(self.nodes[0].getblockcount(), 0)

        self.log.info("Creating miner and receiver wallets")
        self.nodes[0].createwallet(wallet_name="miner")
        self.nodes[0].createwallet(wallet_name="receiver")

        miner = self.nodes[0].get_wallet_rpc("miner")
        receiver = self.nodes[0].get_wallet_rpc("receiver")

        mining_addr = miner.getnewaddress("", "bech32")
        receiver_addr = receiver.getnewaddress("", "bech32")

        assert_equal(self.nodes[0].validateaddress(mining_addr)["isvalid"], True)
        assert_equal(self.nodes[0].validateaddress(receiver_addr)["isvalid"], True)

        self.log.info("Mining one immature Andaluzcoin coinbase block")
        first_blocks = self.nodes[0].generatetoaddress(
            1,
            mining_addr,
            called_by_framework=True,
        )
        assert_equal(len(first_blocks), 1)
        assert_equal(self.nodes[0].getblockcount(), 1)

        balances = miner.getbalances()["mine"]
        assert_equal(balances["trusted"], Decimal("0E-8"))
        assert_equal(balances["immature"], Decimal("50.00000000"))

        self.log.info("Mining 100 more blocks to mature the first coinbase")
        mature_blocks = self.nodes[0].generatetoaddress(
            100,
            mining_addr,
            called_by_framework=True,
        )
        assert_equal(len(mature_blocks), 100)
        assert_equal(self.nodes[0].getblockcount(), 101)

        balances = miner.getbalances()["mine"]
        assert_equal(balances["trusted"], Decimal("50.00000000"))
        assert_equal(balances["immature"], Decimal("5000.00000000"))
        assert miner.getbalance() >= Decimal("50.00000000")

        self.log.info("Spending matured Andaluzcoin coinbase output")
        txid = miner.sendtoaddress(receiver_addr, Decimal("1.00000000"))
        assert txid in self.nodes[0].getrawmempool()

        self.log.info("Confirming matured coinbase spend")
        confirm_blocks = self.nodes[0].generatetoaddress(
            1,
            mining_addr,
            called_by_framework=True,
        )
        assert_equal(len(confirm_blocks), 1)
        assert_equal(self.nodes[0].getblockcount(), 102)

        block = self.nodes[0].getblock(confirm_blocks[0])
        assert txid in block["tx"], block["tx"]
        assert txid not in self.nodes[0].getrawmempool()

        assert_equal(receiver.getbalance(), Decimal("1.00000000"))

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzCoinbaseMaturitySpendIdentityTest(__file__).main()
