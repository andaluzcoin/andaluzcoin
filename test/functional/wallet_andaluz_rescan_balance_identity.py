#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet rescan balance identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletRescanBalanceIdentityTest(BitcoinTestFramework):
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
        miner_wallet_name = "andaluz_rescan_miner"
        sender_wallet_name = "andaluz_rescan_sender"
        receiver_wallet_name = "andaluz_rescan_receiver"

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

        self.log.info("Creating Andaluzcoin receiver address")
        receiver_address = receiver.getnewaddress("andaluz-rescan-receiver", "bech32")
        self.assert_valid_wallet_address(receiver, receiver_address)

        self.log.info("Unloading receiver wallet before payment")
        self.nodes[0].unloadwallet(receiver_wallet_name)
        assert receiver_wallet_name not in self.nodes[0].listwallets()

        self.log.info("Sending confirmed Andaluzcoin payment while receiver wallet is offline")
        txid = sender.sendtoaddress(receiver_address, amount)
        assert txid in self.nodes[0].getrawmempool(), self.nodes[0].getrawmempool()
        self.nodes[0].syncwithvalidationinterfacequeue()

        confirm_block_hash = self.nodes[0].generatetoaddress(
            1,
            miner_mining_address,
            called_by_framework=True,
        )[0]

        assert_equal(self.nodes[0].getbestblockhash(), confirm_block_hash)
        assert_equal(self.nodes[0].getmempoolinfo()["size"], 0)
        self.nodes[0].syncwithvalidationinterfacequeue()

        self.log.info("Reloading receiver wallet")
        load_result = self.nodes[0].loadwallet(receiver_wallet_name)
        assert_equal(load_result["name"], receiver_wallet_name)

        receiver = self.nodes[0].get_wallet_rpc(receiver_wallet_name)
        self.assert_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Rescanning receiver wallet blockchain")
        rescan_result = receiver.rescanblockchain(0)
        assert "start_height" in rescan_result, rescan_result
        assert "stop_height" in rescan_result, rescan_result
        assert_equal(rescan_result["start_height"], 0)
        assert rescan_result["stop_height"] >= 103, rescan_result

        self.nodes[0].syncwithvalidationinterfacequeue()

        self.wait_until(
            lambda: receiver.getbalances()["mine"]["trusted"] == amount,
            timeout=60,
        )

        self.log.info("Checking recovered receiver balance")
        assert_equal(receiver.getbalance(), amount)
        assert_equal(receiver.getbalances()["mine"]["trusted"], amount)
        assert_equal(receiver.getbalances()["mine"]["untrusted_pending"], Decimal("0E-8"))

        self.log.info("Checking recovered receiver transaction history")
        receiver_tx = receiver.gettransaction(txid)
        assert_equal(receiver_tx["amount"], amount)
        assert_equal(receiver_tx["confirmations"], 1)
        assert_equal(receiver_tx["blockhash"], confirm_block_hash)

        receiver_list_entry = self.find_wallet_tx(receiver, txid, "receive")
        assert_equal(receiver_list_entry["amount"], amount)
        assert_equal(receiver_list_entry["confirmations"], 1)

        self.log.info("Checking recovered receiver UTXO")
        receiver_utxos = receiver.listunspent(1, 9999999, [receiver_address])
        matching_utxos = [
            utxo for utxo in receiver_utxos
            if utxo["txid"] == txid and utxo["address"] == receiver_address
        ]

        assert_equal(len(matching_utxos), 1)
        assert_equal(matching_utxos[0]["amount"], amount)
        assert_equal(matching_utxos[0]["confirmations"], 1)

        self.log.info("Checking final Andaluzcoin wallet identities")
        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletRescanBalanceIdentityTest(__file__).main()
