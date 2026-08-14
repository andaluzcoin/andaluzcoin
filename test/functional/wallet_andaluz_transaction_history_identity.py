#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet transaction history identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletTransactionHistoryIdentityTest(BitcoinTestFramework):
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

    def find_wallet_tx(self, wallet, txid, category):
        matches = [
            entry for entry in wallet.listtransactions("*", 100)
            if entry.get("txid") == txid and entry.get("category") == category
        ]

        assert_equal(len(matches), 1)
        return matches[0]

    def run_test(self):
        sender_wallet_name = "andaluz_history_sender"
        receiver_wallet_name = "andaluz_history_receiver"
        amount = Decimal("1.00000000")

        self.log.info("Checking initial Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()

        self.log.info("Creating Andaluzcoin sender and receiver wallets")
        self.nodes[0].createwallet(wallet_name=sender_wallet_name)
        self.nodes[0].createwallet(wallet_name=receiver_wallet_name)

        sender = self.nodes[0].get_wallet_rpc(sender_wallet_name)
        receiver = self.nodes[0].get_wallet_rpc(receiver_wallet_name)

        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Mining spendable Andaluzcoin balance")
        mining_address = sender.getnewaddress("", "bech32")
        self.assert_valid_wallet_address(sender, mining_address)

        mined_blocks = self.nodes[0].generatetoaddress(
            101,
            mining_address,
            called_by_framework=True,
        )
        assert_equal(len(mined_blocks), 101)
        assert sender.getbalance() >= amount, sender.getbalance()

        self.log.info("Sending Andaluzcoin between wallets")
        receiver_address = receiver.getnewaddress("", "bech32")
        self.assert_valid_wallet_address(receiver, receiver_address)

        txid = sender.sendtoaddress(receiver_address, amount)
        assert txid in self.nodes[0].getrawmempool(), self.nodes[0].getrawmempool()

        self.log.info("Confirming wallet transaction")
        confirm_block_hash = self.nodes[0].generatetoaddress(
            1,
            mining_address,
            called_by_framework=True,
        )[0]

        assert_equal(self.nodes[0].getbestblockhash(), confirm_block_hash)
        assert_equal(self.nodes[0].getmempoolinfo()["size"], 0)

        self.log.info("Checking sender transaction history")
        sender_tx = sender.gettransaction(txid)
        assert_equal(sender_tx["amount"], -amount)
        assert sender_tx["fee"] < Decimal("0"), sender_tx
        assert_equal(sender_tx["confirmations"], 1)
        assert_equal(sender_tx["blockhash"], confirm_block_hash)

        sender_list_entry = self.find_wallet_tx(sender, txid, "send")
        assert_equal(sender_list_entry["amount"], -amount)
        assert sender_list_entry["fee"] < Decimal("0"), sender_list_entry
        assert_equal(sender_list_entry["confirmations"], 1)

        self.log.info("Checking receiver transaction history")
        receiver_tx = receiver.gettransaction(txid)
        assert_equal(receiver_tx["amount"], amount)
        assert_equal(receiver_tx["confirmations"], 1)
        assert_equal(receiver_tx["blockhash"], confirm_block_hash)

        receiver_list_entry = self.find_wallet_tx(receiver, txid, "receive")
        assert_equal(receiver_list_entry["amount"], amount)
        assert_equal(receiver_list_entry["confirmations"], 1)

        self.log.info("Checking confirmed receiver UTXO")
        receiver_utxos = receiver.listunspent(1, 9999999, [receiver_address])
        matching_utxos = [
            utxo for utxo in receiver_utxos
            if utxo["txid"] == txid and utxo["address"] == receiver_address
        ]

        assert_equal(len(matching_utxos), 1)
        assert_equal(matching_utxos[0]["amount"], amount)
        assert_equal(matching_utxos[0]["confirmations"], 1)

        self.log.info("Checking final Andaluzcoin wallet identities")
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletTransactionHistoryIdentityTest(__file__).main()
