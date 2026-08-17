#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet sendmany accounting identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletSendManyAccountingIdentityTest(BitcoinTestFramework):
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

    def find_received_by_address(self, wallet, address):
        matches = [
            entry for entry in wallet.listreceivedbyaddress(1)
            if entry["address"] == address
        ]

        assert_equal(len(matches), 1)
        return matches[0]

    def run_test(self):
        miner_wallet_name = "andaluz_sendmany_miner"
        sender_wallet_name = "andaluz_sendmany_sender"
        receiver_one_wallet_name = "andaluz_sendmany_receiver_one"
        receiver_two_wallet_name = "andaluz_sendmany_receiver_two"

        amount_one = Decimal("1.25000000")
        amount_two = Decimal("2.50000000")
        total_amount = amount_one + amount_two

        self.log.info("Checking initial Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()

        self.log.info("Creating Andaluzcoin miner, sender, and receiver wallets")
        self.nodes[0].createwallet(wallet_name=miner_wallet_name)
        self.nodes[0].createwallet(wallet_name=sender_wallet_name)
        self.nodes[0].createwallet(wallet_name=receiver_one_wallet_name)
        self.nodes[0].createwallet(wallet_name=receiver_two_wallet_name)

        miner = self.nodes[0].get_wallet_rpc(miner_wallet_name)
        sender = self.nodes[0].get_wallet_rpc(sender_wallet_name)
        receiver_one = self.nodes[0].get_wallet_rpc(receiver_one_wallet_name)
        receiver_two = self.nodes[0].get_wallet_rpc(receiver_two_wallet_name)

        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver_one, receiver_one_wallet_name)
        self.assert_wallet_identity(receiver_two, receiver_two_wallet_name)

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

        assert sender.getbalance() >= total_amount, sender.getbalance()
        initial_sender_trusted = sender.getbalances()["mine"]["trusted"]

        self.log.info("Creating Andaluzcoin receiver addresses")
        receiver_one_address = receiver_one.getnewaddress("andaluz-sendmany-one", "bech32")
        receiver_two_address = receiver_two.getnewaddress("andaluz-sendmany-two", "bech32")

        self.assert_valid_wallet_address(receiver_one, receiver_one_address)
        self.assert_valid_wallet_address(receiver_two, receiver_two_address)

        self.log.info("Sending one Andaluzcoin transaction to multiple recipients")
        txid = sender.sendmany("", {
            receiver_one_address: amount_one,
            receiver_two_address: amount_two,
        })

        assert txid in self.nodes[0].getrawmempool(), self.nodes[0].getrawmempool()
        self.nodes[0].syncwithvalidationinterfacequeue()

        sender_tx = sender.gettransaction(txid)
        assert_equal(sender_tx["amount"], -total_amount)
        assert sender_tx["fee"] < Decimal("0"), sender_tx

        fee = -sender_tx["fee"]
        assert fee > Decimal("0"), sender_tx

        self.log.info("Checking unconfirmed receiver accounting")
        self.wait_until(
            lambda: receiver_one.getbalances()["mine"]["untrusted_pending"] == amount_one,
            timeout=60,
        )
        self.wait_until(
            lambda: receiver_two.getbalances()["mine"]["untrusted_pending"] == amount_two,
            timeout=60,
        )

        assert_equal(receiver_one.getbalances()["mine"]["trusted"], Decimal("0E-8"))
        assert_equal(receiver_two.getbalances()["mine"]["trusted"], Decimal("0E-8"))

        self.log.info("Confirming sendmany transaction")
        confirm_block_hash = self.nodes[0].generatetoaddress(
            1,
            miner_mining_address,
            called_by_framework=True,
        )[0]

        assert_equal(self.nodes[0].getbestblockhash(), confirm_block_hash)
        assert_equal(self.nodes[0].getmempoolinfo()["size"], 0)
        self.nodes[0].syncwithvalidationinterfacequeue()

        expected_sender_trusted = initial_sender_trusted - total_amount - fee

        self.wait_until(
            lambda: sender.getbalances()["mine"]["trusted"] == expected_sender_trusted,
            timeout=60,
        )
        self.wait_until(
            lambda: receiver_one.getbalances()["mine"]["trusted"] == amount_one,
            timeout=60,
        )
        self.wait_until(
            lambda: receiver_two.getbalances()["mine"]["trusted"] == amount_two,
            timeout=60,
        )

        self.log.info("Checking confirmed sender accounting")
        confirmed_sender_tx = sender.gettransaction(txid)
        assert_equal(confirmed_sender_tx["amount"], -total_amount)
        assert_equal(confirmed_sender_tx["fee"], -fee)
        assert_equal(confirmed_sender_tx["confirmations"], 1)
        assert_equal(confirmed_sender_tx["blockhash"], confirm_block_hash)

        self.log.info("Checking confirmed receiver accounting")
        receiver_one_tx = receiver_one.gettransaction(txid)
        receiver_two_tx = receiver_two.gettransaction(txid)

        assert_equal(receiver_one_tx["amount"], amount_one)
        assert_equal(receiver_two_tx["amount"], amount_two)
        assert_equal(receiver_one_tx["confirmations"], 1)
        assert_equal(receiver_two_tx["confirmations"], 1)
        assert_equal(receiver_one_tx["blockhash"], confirm_block_hash)
        assert_equal(receiver_two_tx["blockhash"], confirm_block_hash)

        self.log.info("Checking listreceivedbyaddress entries")
        receiver_one_received = self.find_received_by_address(receiver_one, receiver_one_address)
        receiver_two_received = self.find_received_by_address(receiver_two, receiver_two_address)

        assert_equal(receiver_one_received["amount"], amount_one)
        assert_equal(receiver_two_received["amount"], amount_two)
        assert_equal(receiver_one_received["confirmations"], 1)
        assert_equal(receiver_two_received["confirmations"], 1)

        self.log.info("Checking final Andaluzcoin wallet identities")
        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver_one, receiver_one_wallet_name)
        self.assert_wallet_identity(receiver_two, receiver_two_wallet_name)

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletSendManyAccountingIdentityTest(__file__).main()
