#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin encrypted wallet send identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal, assert_raises_rpc_error


class AndaluzEncryptedWalletSendIdentityTest(BitcoinTestFramework):
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

    def assert_andaluz_wallet_identity(self, wallet, wallet_name):
        wallet_info = wallet.getwalletinfo()
        assert_equal(wallet_info["walletname"], wallet_name)
        assert_equal(wallet_info["private_keys_enabled"], True)
        assert_equal(wallet_info["descriptors"], True)
        assert_equal(wallet_info["format"], "sqlite")

    def run_test(self):
        miner_wallet_name = "andaluz_encrypted_sender"
        receiver_wallet_name = "andaluz_receiver"
        passphrase = "andaluz encrypted wallet send passphrase"

        self.log.info("Checking initial Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()

        self.log.info("Creating Andaluzcoin miner and receiver wallets")
        self.nodes[0].createwallet(wallet_name=miner_wallet_name)
        self.nodes[0].createwallet(wallet_name=receiver_wallet_name)

        miner = self.nodes[0].get_wallet_rpc(miner_wallet_name)
        receiver = self.nodes[0].get_wallet_rpc(receiver_wallet_name)

        self.assert_andaluz_wallet_identity(miner, miner_wallet_name)
        self.assert_andaluz_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Mining spendable Andaluzcoin balance")
        mining_addr = miner.getnewaddress("", "bech32")
        mined_blocks = self.nodes[0].generatetoaddress(
            101,
            mining_addr,
            called_by_framework=True,
        )
        assert_equal(len(mined_blocks), 101)

        assert_equal(miner.getbalance(), Decimal("50.00000000"))
        assert_equal(receiver.getbalance(), Decimal("0.00000000"))

        self.log.info("Encrypting Andaluzcoin miner wallet")
        encrypt_result = miner.encryptwallet(passphrase)
        assert "wallet encrypted" in encrypt_result.lower(), encrypt_result
        assert_equal(miner.getwalletinfo()["unlocked_until"], 0)

        self.log.info("Verifying locked encrypted wallet cannot send")
        receiver_addr = receiver.getnewaddress("", "bech32")
        assert_raises_rpc_error(
            -13,
            "wallet passphrase",
            miner.sendtoaddress,
            receiver_addr,
            Decimal("1.00000000"),
        )
        assert_equal(miner.getwalletinfo()["unlocked_until"], 0)

        self.log.info("Unlocking encrypted Andaluzcoin miner wallet")
        miner.walletpassphrase(passphrase, 60)
        assert miner.getwalletinfo()["unlocked_until"] > 0

        self.log.info("Sending ALUZ from encrypted wallet")
        txid = miner.sendtoaddress(receiver_addr, Decimal("1.00000000"))
        assert len(txid) == 64, txid

        self.log.info("Confirming encrypted wallet send")
        confirm_addr = miner.getnewaddress("", "bech32")
        confirmed_blocks = self.nodes[0].generatetoaddress(
            1,
            confirm_addr,
            called_by_framework=True,
        )
        assert_equal(len(confirmed_blocks), 1)

        self.sync_all()

        assert_equal(receiver.getbalance(), Decimal("1.00000000"))
        assert miner.getbalance() < Decimal("99.00000000"), miner.getbalance()

        self.log.info("Locking Andaluzcoin miner wallet again")
        miner.walletlock()
        assert_equal(miner.getwalletinfo()["unlocked_until"], 0)

        self.log.info("Checking final wallet identities")
        self.assert_andaluz_wallet_identity(miner, miner_wallet_name)
        self.assert_andaluz_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzEncryptedWalletSendIdentityTest(__file__).main()
