#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet message signing identity."""

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletMessageSigningIdentityTest(BitcoinTestFramework):
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

    def run_test(self):
        wallet_name = "andaluz_message_signing_wallet"
        message = "Andaluzcoin wallet message signing identity"
        changed_message = "Andaluzcoin wallet message signing identity changed"

        self.log.info("Checking initial Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()

        self.log.info("Creating Andaluzcoin wallet")
        create_result = self.nodes[0].createwallet(wallet_name=wallet_name)
        assert_equal(create_result["name"], wallet_name)

        wallet = self.nodes[0].get_wallet_rpc(wallet_name)

        self.log.info("Checking Andaluzcoin wallet identity")
        self.assert_andaluz_wallet_identity(wallet, wallet_name)

        self.log.info("Creating Andaluzcoin legacy signing address")
        signing_address = wallet.getnewaddress("", "legacy")
        assert signing_address.startswith("P"), signing_address
        assert not signing_address.startswith("1"), signing_address

        address_info = self.nodes[0].validateaddress(signing_address)
        assert_equal(address_info["isvalid"], True)

        wallet_address_info = wallet.getaddressinfo(signing_address)
        assert_equal(wallet_address_info["ismine"], True)
        assert_equal(wallet_address_info["solvable"], True)

        self.log.info("Signing message with Andaluzcoin wallet")
        signature = wallet.signmessage(signing_address, message)
        assert len(signature) > 0, signature

        self.log.info("Verifying Andaluzcoin message signature")
        assert_equal(
            self.nodes[0].verifymessage(signing_address, signature, message),
            True,
        )

        self.log.info("Verifying changed message fails signature check")
        assert_equal(
            self.nodes[0].verifymessage(signing_address, signature, changed_message),
            False,
        )

        self.log.info("Checking final Andaluzcoin wallet identity")
        self.assert_andaluz_wallet_identity(wallet, wallet_name)

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletMessageSigningIdentityTest(__file__).main()
