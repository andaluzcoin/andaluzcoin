#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet RBF/bumpfee identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletRbfBumpfeeIdentityTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True
        self.chain = "regtest"
        self.wallet_names = []
        self.extra_args = [[
            "-dnsseed=0",
            "-fixedseeds=0",
            "-connect=0",
        ]]

    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    def assert_andaluz_runtime_identity(self):
        assert_equal(self.nodes[0].getblockchaininfo()["chain"], "regtest")

        subversion = self.nodes[0].getnetworkinfo()["subversion"]
        assert subversion.startswith("/AndaluzcoinCore:"), subversion
        assert "Satoshi" not in subversion, subversion
        assert "Bitcoin" not in subversion, subversion

    def assert_wallet_identity(self, wallet, wallet_name):
        wallet_info = wallet.getwalletinfo()
        assert_equal(wallet_info["walletname"], wallet_name)
        assert_equal(wallet_info["private_keys_enabled"], True)
        assert_equal(wallet_info["descriptors"], True)
        assert_equal(wallet_info["format"], "sqlite")

    def assert_valid_wallet_address(self, wallet, address):
        address_info = self.nodes[0].validateaddress(address)
        assert_equal(address_info["isvalid"], True)

        wallet_address_info = wallet.getaddressinfo(address)
        assert_equal(wallet_address_info["ismine"], True)
        assert_equal(wallet_address_info["solvable"], True)

    def run_test(self):
        miner_wallet_name = "andaluz_rbf_miner"
        sender_wallet_name = "andaluz_rbf_sender"
        receiver_wallet_name = "andaluz_rbf_receiver"

        amount = Decimal("1.00000000")

        self.log.info("Checking initial Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()

        self.log.info("Creating Andaluzcoin miner, sender, and receiver wallets")
        self.nodes[0].createwallet(wallet_name=miner_wallet_name)
        self.nodes[0].createwallet(wallet_name=sender_wallet_name)
        self.nodes[0].createwallet(wallet_name=receiver_wallet_name)

        miner = self.nodes[0].get_wallet_rpc(miner_wallet_name)
        sender = self.nodes[0].get_wallet_rpc(sender_wallet_name)
        receiver = self.nodes[0].get_wallet_rpc(receiver_wallet_name)

        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Mining spendable Andaluzcoin balance to sender")
        sender_mining_address = sender.getnewaddress("", "bech32")
        miner_mining_address = miner.getnewaddress("", "bech32")

        self.assert_valid_wallet_address(sender, sender_mining_address)
        self.assert_valid_wallet_address(miner, miner_mining_address)

        sender_blocks = self.nodes[0].generatetoaddress(
            2,
            sender_mining_address,
            called_by_framework=True,
        )
        assert_equal(len(sender_blocks), 2)

        maturity_blocks = self.nodes[0].generatetoaddress(
            100,
            miner_mining_address,
            called_by_framework=True,
        )
        assert_equal(len(maturity_blocks), 100)

        assert sender.getbalance() >= amount, sender.getbalance()
        initial_sender_trusted = sender.getbalances()["mine"]["trusted"]

        self.log.info("Creating Andaluzcoin receiver address")
        receiver_address = receiver.getnewaddress("andaluz-rbf-receiver", "bech32")
        self.assert_valid_wallet_address(receiver, receiver_address)

        self.log.info("Sending replaceable Andaluzcoin transaction")
        original_txid = sender.sendtoaddress(
            receiver_address,
            amount,
            "",
            "",
            False,
            True,
        )

        assert original_txid in self.nodes[0].getrawmempool(), self.nodes[0].getrawmempool()
        self.nodes[0].syncwithvalidationinterfacequeue()

        original_sender_tx = sender.gettransaction(original_txid)
        assert_equal(original_sender_tx["amount"], -amount)
        assert original_sender_tx["fee"] < Decimal("0"), original_sender_tx
        original_fee = -original_sender_tx["fee"]
        assert original_fee > Decimal("0"), original_sender_tx

        self.log.info("Checking receiver sees unconfirmed replaceable transaction")
        self.wait_until(
            lambda: receiver.getbalances()["mine"]["untrusted_pending"] == amount,
            timeout=60,
        )

        self.log.info("Bumping Andaluzcoin transaction fee")
        bump_result = sender.bumpfee(original_txid)
        assert "txid" in bump_result, bump_result
        assert "origfee" in bump_result, bump_result
        assert "fee" in bump_result, bump_result

        bumped_txid = bump_result["txid"]
        assert bumped_txid != original_txid, bump_result
        assert bump_result["fee"] > bump_result["origfee"], bump_result

        mempool = self.nodes[0].getrawmempool()
        assert original_txid not in mempool, mempool
        assert bumped_txid in mempool, mempool

        self.nodes[0].syncwithvalidationinterfacequeue()

        self.log.info("Checking bumped sender transaction accounting")
        bumped_sender_tx = sender.gettransaction(bumped_txid)
        assert_equal(bumped_sender_tx["amount"], -amount)
        assert bumped_sender_tx["fee"] < -original_fee, bumped_sender_tx

        bumped_fee = -bumped_sender_tx["fee"]
        assert bumped_fee > original_fee, bumped_sender_tx

        self.log.info("Confirming bumped transaction")
        confirm_block_hash = self.nodes[0].generatetoaddress(
            1,
            miner_mining_address,
            called_by_framework=True,
        )[0]

        assert_equal(self.nodes[0].getbestblockhash(), confirm_block_hash)
        assert_equal(self.nodes[0].getmempoolinfo()["size"], 0)
        self.nodes[0].syncwithvalidationinterfacequeue()

        expected_sender_trusted = initial_sender_trusted - amount - bumped_fee

        self.wait_until(
            lambda: sender.getbalances()["mine"]["trusted"] == expected_sender_trusted,
            timeout=60,
        )
        self.wait_until(
            lambda: receiver.getbalances()["mine"]["trusted"] == amount,
            timeout=60,
        )

        self.log.info("Checking confirmed bumped sender transaction")
        confirmed_sender_tx = sender.gettransaction(bumped_txid)
        assert_equal(confirmed_sender_tx["amount"], -amount)
        assert_equal(confirmed_sender_tx["fee"], -bumped_fee)
        assert_equal(confirmed_sender_tx["confirmations"], 1)
        assert_equal(confirmed_sender_tx["blockhash"], confirm_block_hash)

        self.log.info("Checking confirmed receiver transaction")
        receiver_tx = receiver.gettransaction(bumped_txid)
        assert_equal(receiver_tx["amount"], amount)
        assert_equal(receiver_tx["confirmations"], 1)
        assert_equal(receiver_tx["blockhash"], confirm_block_hash)

        self.log.info("Checking original transaction is marked replaced/conflicted")
        original_sender_tx_after_bump = sender.gettransaction(original_txid)
        assert_equal(original_sender_tx_after_bump["confirmations"], -1)
        assert bumped_txid in original_sender_tx_after_bump["walletconflicts"]

        self.log.info("Checking final Andaluzcoin wallet identities")
        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletRbfBumpfeeIdentityTest(__file__).main()
