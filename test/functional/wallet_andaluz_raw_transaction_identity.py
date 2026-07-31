#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin raw transaction identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzRawTransactionIdentityTest(BitcoinTestFramework):
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

        self.log.info("Creating sender and receiver wallets")
        self.nodes[0].createwallet(wallet_name="sender")
        self.nodes[0].createwallet(wallet_name="receiver")

        sender = self.nodes[0].get_wallet_rpc("sender")
        receiver = self.nodes[0].get_wallet_rpc("receiver")

        mining_addr = sender.getnewaddress("", "bech32")
        receiver_addr = receiver.getnewaddress("", "bech32")

        assert_equal(self.nodes[0].validateaddress(mining_addr)["isvalid"], True)
        assert_equal(self.nodes[0].validateaddress(receiver_addr)["isvalid"], True)

        self.log.info("Mining spendable Andaluzcoin")
        mined_blocks = self.nodes[0].generatetoaddress(
            101,
            mining_addr,
            called_by_framework=True,
        )
        assert_equal(len(mined_blocks), 101)
        assert_equal(sender.getbalance(), Decimal("50.00000000"))

        self.log.info("Creating raw transaction")
        raw_tx = self.nodes[0].createrawtransaction(
            [],
            [{receiver_addr: Decimal("1.00000000")}],
        )

        self.log.info("Funding raw transaction with sender wallet")
        funded_tx = sender.fundrawtransaction(raw_tx)
        assert "hex" in funded_tx, funded_tx
        assert "fee" in funded_tx, funded_tx
        assert funded_tx["fee"] > Decimal("0"), funded_tx

        fee_paid = funded_tx["fee"]

        self.log.info("Signing raw transaction with sender wallet")
        signed_tx = sender.signrawtransactionwithwallet(funded_tx["hex"])
        assert_equal(signed_tx["complete"], True)

        self.log.info("Broadcasting raw transaction")
        txid = self.nodes[0].sendrawtransaction(signed_tx["hex"])
        assert txid in self.nodes[0].getrawmempool()

        self.log.info("Checking sender wallet fee accounting")
        sender_tx = sender.gettransaction(txid)
        assert_equal(sender_tx["amount"], Decimal("-1.00000000"))
        assert_equal(sender_tx["fee"], -fee_paid)

        self.log.info("Confirming raw transaction")
        confirm_blocks = self.nodes[0].generatetoaddress(
            1,
            mining_addr,
            called_by_framework=True,
        )
        assert_equal(len(confirm_blocks), 1)

        block = self.nodes[0].getblock(confirm_blocks[0])
        assert txid in block["tx"], block["tx"]
        assert txid not in self.nodes[0].getrawmempool()

        self.log.info("Checking confirmed raw transaction result")
        assert_equal(receiver.getbalance(), Decimal("1.00000000"))

        confirmed_sender_tx = sender.gettransaction(txid)
        assert_equal(confirmed_sender_tx["amount"], Decimal("-1.00000000"))
        assert_equal(confirmed_sender_tx["fee"], -fee_paid)
        assert_equal(confirmed_sender_tx["confirmations"], 1)

        confirmed_receiver_tx = receiver.gettransaction(txid)
        assert_equal(confirmed_receiver_tx["amount"], Decimal("1.00000000"))
        assert_equal(confirmed_receiver_tx["confirmations"], 1)

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzRawTransactionIdentityTest(__file__).main()
