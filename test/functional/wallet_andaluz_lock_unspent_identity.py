#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet lockunspent identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal, assert_raises_rpc_error


class AndaluzWalletLockUnspentIdentityTest(BitcoinTestFramework):
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
        miner_wallet_name = "andaluz_lock_unspent_miner"
        sender_wallet_name = "andaluz_lock_unspent_sender"
        receiver_wallet_name = "andaluz_lock_unspent_receiver"

        send_amount = Decimal("1.00000000")

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

        self.log.info("Mining one spendable Andaluzcoin UTXO to sender")
        sender_mining_address = sender.getnewaddress("", "bech32")
        miner_mining_address = miner.getnewaddress("", "bech32")

        self.assert_valid_wallet_address(sender, sender_mining_address)
        self.assert_valid_wallet_address(miner, miner_mining_address)

        sender_blocks = self.nodes[0].generatetoaddress(
            1,
            sender_mining_address,
            called_by_framework=True,
        )
        assert_equal(len(sender_blocks), 1)

        maturity_blocks = self.nodes[0].generatetoaddress(
            100,
            miner_mining_address,
            called_by_framework=True,
        )
        assert_equal(len(maturity_blocks), 100)

        self.nodes[0].syncwithvalidationinterfacequeue()

        assert sender.getbalance() >= send_amount, sender.getbalance()

        self.log.info("Selecting sender UTXO for lockunspent")
        sender_utxos = sender.listunspent(1, 9999999, [sender_mining_address])
        assert_equal(len(sender_utxos), 1)

        locked_output = {
            "txid": sender_utxos[0]["txid"],
            "vout": sender_utxos[0]["vout"],
        }

        assert_equal(sender_utxos[0]["amount"], Decimal("50.00000000"))
        assert_equal(sender_utxos[0]["confirmations"], 101)

        receiver_address = receiver.getnewaddress("andaluz-lock-unspent-receiver", "bech32")
        self.assert_valid_wallet_address(receiver, receiver_address)

        self.log.info("Locking sender UTXO")
        assert_equal(sender.lockunspent(False, [locked_output]), True)
        assert locked_output in sender.listlockunspent(), sender.listlockunspent()

        self.log.info("Checking locked UTXO cannot be automatically spent")
        assert_raises_rpc_error(
            -6,
            "Insufficient funds",
            sender.sendtoaddress,
            receiver_address,
            send_amount,
        )

        assert_equal(self.nodes[0].getmempoolinfo()["size"], 0)

        self.log.info("Unlocking sender UTXO")
        assert_equal(sender.lockunspent(True, [locked_output]), True)
        assert_equal(sender.listlockunspent(), [])

        self.log.info("Checking unlocked UTXO can be spent")
        spend_txid = sender.sendtoaddress(receiver_address, send_amount)
        assert spend_txid in self.nodes[0].getrawmempool(), self.nodes[0].getrawmempool()

        spend_block_hash = self.nodes[0].generatetoaddress(
            1,
            miner_mining_address,
            called_by_framework=True,
        )[0]

        assert_equal(self.nodes[0].getbestblockhash(), spend_block_hash)
        assert_equal(self.nodes[0].getmempoolinfo()["size"], 0)
        self.nodes[0].syncwithvalidationinterfacequeue()

        self.log.info("Checking receiver got confirmed Andaluzcoin after unlock")
        self.wait_until(
            lambda: receiver.getbalances()["mine"]["trusted"] == send_amount,
            timeout=60,
        )

        receiver_tx = receiver.gettransaction(spend_txid)
        assert_equal(receiver_tx["amount"], send_amount)
        assert_equal(receiver_tx["confirmations"], 1)
        assert_equal(receiver_tx["blockhash"], spend_block_hash)

        receiver_list_entry = self.find_wallet_tx(receiver, spend_txid, "receive")
        assert_equal(receiver_list_entry["amount"], send_amount)
        assert_equal(receiver_list_entry["confirmations"], 1)

        self.log.info("Checking final Andaluzcoin wallet identities")
        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletLockUnspentIdentityTest(__file__).main()
