#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet encryption identity."""

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletEncryptionIdentityTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True
        self.chain = ""
        self.wallet_names = []
        self.extra_args = [[
            "-dnsseed=0",
            "-fixedseeds=0",
            "-connect=0",
        ]]

    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    def assert_andaluz_runtime_identity(self):
        assert_equal(self.nodes[0].getblockchaininfo()["chain"], "main")

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

        address = wallet.getnewaddress("", "bech32")
        assert address.startswith("aluz1"), address
        assert not address.startswith("bc1"), address

        address_info = self.nodes[0].validateaddress(address)
        assert_equal(address_info["isvalid"], True)

        return address

    def run_test(self):
        wallet_name = "andaluz_encrypted_wallet"
        passphrase = "andaluz wallet encryption test passphrase"

        self.log.info("Checking initial Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()

        self.log.info("Creating Andaluzcoin wallet")
        create_result = self.nodes[0].createwallet(wallet_name=wallet_name)
        assert_equal(create_result["name"], wallet_name)

        wallet = self.nodes[0].get_wallet_rpc(wallet_name)

        self.log.info("Checking unencrypted wallet identity")
        self.assert_andaluz_wallet_identity(wallet, wallet_name)
        assert "unlocked_until" not in wallet.getwalletinfo()

        self.log.info("Encrypting Andaluzcoin wallet")
        encrypt_result = wallet.encryptwallet(passphrase)
        assert "wallet encrypted" in encrypt_result.lower(), encrypt_result

        encrypted_info = wallet.getwalletinfo()
        assert_equal(encrypted_info["walletname"], wallet_name)
        assert_equal(encrypted_info["private_keys_enabled"], True)
        assert_equal(encrypted_info["descriptors"], True)
        assert_equal(encrypted_info["format"], "sqlite")
        assert_equal(encrypted_info["unlocked_until"], 0)

        self.log.info("Unlocking Andaluzcoin wallet")
        wallet.walletpassphrase(passphrase, 60)
        unlocked_info = wallet.getwalletinfo()
        assert unlocked_info["unlocked_until"] > 0, unlocked_info

        self.log.info("Checking unlocked wallet address identity")
        self.assert_andaluz_wallet_identity(wallet, wallet_name)

        self.log.info("Locking Andaluzcoin wallet again")
        wallet.walletlock()
        locked_info = wallet.getwalletinfo()
        assert_equal(locked_info["unlocked_until"], 0)
        assert_equal(locked_info["descriptors"], True)
        assert_equal(locked_info["format"], "sqlite")

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletEncryptionIdentityTest(__file__).main()
