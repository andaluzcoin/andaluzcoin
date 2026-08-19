#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet abandon transaction identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletAbandonTransactionIdentityTest(BitcoinTestFramework):
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

    def get_wallet(self, wallet_name):
        if wallet_name not in self.nodes[0].listwallets():
            self.nodes[0].loadwallet(wallet_name)
        return self.nodes[0].get_wallet_rpc(wallet_name)

    def run_test(self):
        miner_wallet_name = "andaluz_abandon_miner"
        sender_wallet_name = "andaluz_abandon_sender"
        receiver_wallet_name = "andaluz_abandon_receiver"

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
        receiver_address = receiver.getnewaddress("andaluz-abandon-receiver", "bech32")
        self.assert_valid_wallet_address(receiver, receiver_address)

        self.log.info("Sending unconfirmed Andaluzcoin transaction")
        txid = sender.sendtoaddress(receiver_address, amount)

        assert txid in self.nodes[0].getrawmempool(), self.nodes[0].getrawmempool()
        self.nodes[0].syncwithvalidationinterfacequeue()

        sender_tx = sender.gettransaction(txid)
        assert_equal(sender_tx["amount"], -amount)
        assert sender_tx["fee"] < Decimal("0"), sender_tx

        self.wait_until(
            lambda: receiver.getbalances()["mine"]["untrusted_pending"] == amount,
            timeout=60,
        )

        self.log.info("Restarting without mempool persistence or wallet rebroadcast")
        self.restart_node(
            0,
            extra_args=self.extra_args[0] + [
                "-persistmempool=0",
                "-walletbroadcast=0",
            ],
        )

        miner = self.get_wallet(miner_wallet_name)
        sender = self.get_wallet(sender_wallet_name)
        receiver = self.get_wallet(receiver_wallet_name)

        self.assert_andaluz_runtime_identity()
        assert_equal(self.nodes[0].getmempoolinfo()["size"], 0)
        assert txid not in self.nodes[0].getrawmempool(), self.nodes[0].getrawmempool()

        self.log.info("Abandoning Andaluzcoin transaction")
        sender.abandontransaction(txid)
        self.nodes[0].syncwithvalidationinterfacequeue()

        abandoned_tx = sender.gettransaction(txid)
        assert_equal(abandoned_tx["confirmations"], 0)

        sender_entries = [
            entry for entry in sender.listtransactions("*", 100)
            if entry.get("txid") == txid and entry.get("category") == "send"
        ]
        assert_equal(len(sender_entries), 1)

        if "abandoned" in sender_entries[0]:
            assert_equal(sender_entries[0]["abandoned"], True)

        self.log.info("Checking sender balance is spendable again")
        self.wait_until(
            lambda: sender.getbalances()["mine"]["trusted"] == initial_sender_trusted,
            timeout=60,
        )
        assert_equal(sender.getbalance(), initial_sender_trusted)

        self.log.info("Checking receiver did not receive confirmed Andaluzcoin")
        receiver_balances = receiver.getbalances()["mine"]
        assert_equal(receiver_balances["trusted"], Decimal("0E-8"))
        assert_equal(receiver_balances["untrusted_pending"], Decimal("0E-8"))
        assert_equal(receiver.getbalance(), Decimal("0E-8"))

        self.log.info("Checking final Andaluzcoin wallet identities")
        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletAbandonTransactionIdentityTest(__file__).main()
