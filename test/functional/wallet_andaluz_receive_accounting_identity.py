#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet receive accounting identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletReceiveAccountingIdentityTest(BitcoinTestFramework):
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

    def find_received_by_label(self, wallet, label):
        matches = [
            entry for entry in wallet.listreceivedbylabel(1)
            if entry["label"] == label
        ]

        assert_equal(len(matches), 1)
        return matches[0]

    def run_test(self):
        miner_wallet_name = "andaluz_receive_miner"
        sender_wallet_name = "andaluz_receive_sender"
        receiver_wallet_name = "andaluz_receive_receiver"

        label_one = "andaluz-receive-one"
        label_two = "andaluz-receive-two"

        amount_one = Decimal("1.25000000")
        amount_two = Decimal("2.50000000")
        total_amount = amount_one + amount_two

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

        assert sender.getbalance() >= total_amount, sender.getbalance()

        self.log.info("Creating labeled Andaluzcoin receiver addresses")
        receive_address_one = receiver.getnewaddress(label_one, "bech32")
        receive_address_two = receiver.getnewaddress(label_two, "bech32")

        self.assert_valid_wallet_address(receiver, receive_address_one)
        self.assert_valid_wallet_address(receiver, receive_address_two)

        address_one_info = receiver.getaddressinfo(receive_address_one)
        address_two_info = receiver.getaddressinfo(receive_address_two)
        assert_equal(address_one_info["labels"][0], label_one)
        assert_equal(address_two_info["labels"][0], label_two)

        self.log.info("Sending Andaluzcoin to labeled receiver addresses")
        txid_one = sender.sendtoaddress(receive_address_one, amount_one)
        txid_two = sender.sendtoaddress(receive_address_two, amount_two)

        mempool = self.nodes[0].getrawmempool()
        assert txid_one in mempool, mempool
        assert txid_two in mempool, mempool

        self.nodes[0].syncwithvalidationinterfacequeue()

        self.log.info("Confirming receive transactions")
        confirm_block_hash = self.nodes[0].generatetoaddress(
            1,
            miner_mining_address,
            called_by_framework=True,
        )[0]

        assert_equal(self.nodes[0].getbestblockhash(), confirm_block_hash)
        assert_equal(self.nodes[0].getmempoolinfo()["size"], 0)
        self.nodes[0].syncwithvalidationinterfacequeue()

        self.wait_until(
            lambda: receiver.getbalances()["mine"]["trusted"] == total_amount,
            timeout=10,
        )

        self.log.info("Checking listreceivedbyaddress accounting")
        received_one = self.find_received_by_address(receiver, receive_address_one)
        assert_equal(received_one["amount"], amount_one)
        assert_equal(received_one["confirmations"], 1)
        assert_equal(received_one["label"], label_one)

        received_two = self.find_received_by_address(receiver, receive_address_two)
        assert_equal(received_two["amount"], amount_two)
        assert_equal(received_two["confirmations"], 1)
        assert_equal(received_two["label"], label_two)

        self.log.info("Checking listreceivedbylabel accounting")
        label_one_entry = self.find_received_by_label(receiver, label_one)
        assert_equal(label_one_entry["amount"], amount_one)
        assert_equal(label_one_entry["confirmations"], 1)

        label_two_entry = self.find_received_by_label(receiver, label_two)
        assert_equal(label_two_entry["amount"], amount_two)
        assert_equal(label_two_entry["confirmations"], 1)

        self.log.info("Checking confirmed receiver balance")
        assert_equal(receiver.getbalance(), total_amount)
        assert_equal(receiver.getbalances()["mine"]["trusted"], total_amount)

        self.log.info("Checking final Andaluzcoin wallet identities")
        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletReceiveAccountingIdentityTest(__file__).main()
