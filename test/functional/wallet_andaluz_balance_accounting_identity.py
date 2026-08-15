#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet balance accounting identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletBalanceAccountingIdentityTest(BitcoinTestFramework):
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

    def assert_mine_balances(self, wallet, trusted, untrusted_pending, immature):
        balances = wallet.getbalances()["mine"]
        assert_equal(balances["trusted"], trusted)
        assert_equal(balances["untrusted_pending"], untrusted_pending)
        assert_equal(balances["immature"], immature)
        assert_equal(wallet.getbalance(), trusted)

    def run_test(self):
        miner_wallet_name = "andaluz_balance_miner"
        sender_wallet_name = "andaluz_balance_sender"
        receiver_wallet_name = "andaluz_balance_receiver"

        block_reward = Decimal("50.00000000")
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

        self.log.info("Mining one spendable Andaluzcoin coinbase to sender")
        sender_mining_address = sender.getnewaddress("", "bech32")
        miner_mining_address = miner.getnewaddress("", "bech32")

        self.assert_valid_wallet_address(sender, sender_mining_address)
        self.assert_valid_wallet_address(miner, miner_mining_address)

        sender_block = self.nodes[0].generatetoaddress(
            1,
            sender_mining_address,
            called_by_framework=True,
        )
        assert_equal(len(sender_block), 1)

        maturity_blocks = self.nodes[0].generatetoaddress(
            100,
            miner_mining_address,
            called_by_framework=True,
        )
        assert_equal(len(maturity_blocks), 100)

        self.log.info("Checking initial wallet balance accounting")
        self.assert_mine_balances(
            sender,
            trusted=block_reward,
            untrusted_pending=Decimal("0E-8"),
            immature=Decimal("0E-8"),
        )
        self.assert_mine_balances(
            receiver,
            trusted=Decimal("0E-8"),
            untrusted_pending=Decimal("0E-8"),
            immature=Decimal("0E-8"),
        )

        initial_sender_trusted = sender.getbalances()["mine"]["trusted"]

        self.log.info("Sending Andaluzcoin from sender to receiver")
        receiver_address = receiver.getnewaddress("", "bech32")
        self.assert_valid_wallet_address(receiver, receiver_address)

        txid = sender.sendtoaddress(receiver_address, amount)
        assert txid in self.nodes[0].getrawmempool(), self.nodes[0].getrawmempool()

        sender_tx = sender.gettransaction(txid)
        assert_equal(sender_tx["amount"], -amount)
        assert sender_tx["fee"] < Decimal("0"), sender_tx

        fee = -sender_tx["fee"]
        assert fee > Decimal("0"), sender_tx

        self.log.info("Checking unconfirmed receiver balance accounting")
        receiver_pending = receiver.getbalances()["mine"]
        assert_equal(receiver_pending["trusted"], Decimal("0E-8"))
        assert_equal(receiver_pending["untrusted_pending"], amount)

        self.log.info("Confirming transaction without maturing extra sender coinbase")
        confirm_block_hash = self.nodes[0].generatetoaddress(
            1,
            miner_mining_address,
            called_by_framework=True,
        )[0]

        assert_equal(self.nodes[0].getbestblockhash(), confirm_block_hash)
        assert_equal(self.nodes[0].getmempoolinfo()["size"], 0)

        expected_sender_trusted = initial_sender_trusted - amount - fee

        self.log.info("Checking confirmed sender balance accounting")
        self.assert_mine_balances(
            sender,
            trusted=expected_sender_trusted,
            untrusted_pending=Decimal("0E-8"),
            immature=Decimal("0E-8"),
        )

        confirmed_sender_tx = sender.gettransaction(txid)
        assert_equal(confirmed_sender_tx["amount"], -amount)
        assert_equal(confirmed_sender_tx["fee"], -fee)
        assert_equal(confirmed_sender_tx["confirmations"], 1)
        assert_equal(confirmed_sender_tx["blockhash"], confirm_block_hash)

        self.log.info("Checking confirmed receiver balance accounting")
        self.assert_mine_balances(
            receiver,
            trusted=amount,
            untrusted_pending=Decimal("0E-8"),
            immature=Decimal("0E-8"),
        )

        receiver_tx = receiver.gettransaction(txid)
        assert_equal(receiver_tx["amount"], amount)
        assert_equal(receiver_tx["confirmations"], 1)
        assert_equal(receiver_tx["blockhash"], confirm_block_hash)

        self.log.info("Checking final Andaluzcoin wallet identities")
        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletBalanceAccountingIdentityTest(__file__).main()
