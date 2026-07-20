#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin mempool transaction relay identity."""

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzMempoolTransactionIdentityTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 2
        self.setup_clean_chain = True
        self.chain = "regtest"
        self.wallet_names = []
        self.extra_args = [
            [
                "-listen=1",
                "-fallbackfee=0.0001",
            ],
            [
                "-listen=1",
                "-fallbackfee=0.0001",
            ],
        ]

    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    def run_test(self):
        self.log.info("Checking both nodes run with Andaluzcoin runtime identity")
        for node in self.nodes:
            assert_equal(node.getblockchaininfo()["chain"], "regtest")

            network_info = node.getnetworkinfo()
            subversion = network_info["subversion"]
            assert subversion.startswith("/AndaluzcoinCore:"), subversion
            assert "Satoshi" not in subversion, subversion
            assert "Bitcoin" not in subversion, subversion

        self.log.info("Connecting Andaluzcoin nodes")
        self.connect_nodes(0, 1)
        self.wait_until(lambda: self.nodes[0].getconnectioncount() >= 1, timeout=30)
        self.wait_until(lambda: self.nodes[1].getconnectioncount() >= 1, timeout=30)

        self.log.info("Creating sender and receiver wallets")
        self.nodes[0].createwallet(wallet_name="sender")
        self.nodes[1].createwallet(wallet_name="receiver")

        sender = self.nodes[0].get_wallet_rpc("sender")
        receiver = self.nodes[1].get_wallet_rpc("receiver")

        mining_addr = sender.getnewaddress("", "bech32")
        receiver_addr = receiver.getnewaddress("", "bech32")

        self.log.info("Mining spendable coins on node 0")
        mined_blocks = self.nodes[0].generatetoaddress(
            101,
            mining_addr,
            called_by_framework=True,
        )
        assert_equal(len(mined_blocks), 101)
        self.sync_blocks()

        assert sender.getbalance() > 0

        self.log.info("Sending transaction from node 0 wallet to node 1 wallet")
        txid = sender.sendtoaddress(receiver_addr, 1)

        self.wait_until(lambda: txid in self.nodes[0].getrawmempool(), timeout=30)
        self.sync_mempools()
        assert txid in self.nodes[1].getrawmempool()

        self.log.info("Confirming transaction in a block")
        confirm_blocks = self.nodes[0].generatetoaddress(
            1,
            mining_addr,
            called_by_framework=True,
        )
        assert_equal(len(confirm_blocks), 1)
        block_hash = confirm_blocks[0]
        self.sync_blocks()

        block = self.nodes[0].getblock(block_hash)
        assert txid in block["tx"], block["tx"]

        assert txid not in self.nodes[0].getrawmempool()
        self.sync_mempools()
        assert txid not in self.nodes[1].getrawmempool()

        self.log.info("Checking final Andaluzcoin runtime identity")
        for node in self.nodes:
            assert_equal(node.getblockchaininfo()["chain"], "regtest")

            subversion = node.getnetworkinfo()["subversion"]
            assert subversion.startswith("/AndaluzcoinCore:"), subversion
            assert "Satoshi" not in subversion, subversion
            assert "Bitcoin" not in subversion, subversion


if __name__ == "__main__":
    AndaluzMempoolTransactionIdentityTest(__file__).main()
