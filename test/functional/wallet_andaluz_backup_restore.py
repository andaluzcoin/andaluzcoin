#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet backup and restore identity."""

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletBackupRestoreTest(BitcoinTestFramework):
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

    def assert_andaluz_wallet_identity(self, wallet, wallet_name):
        wallet_info = wallet.getwalletinfo()
        assert_equal(wallet_info["walletname"], wallet_name)
        assert_equal(wallet_info["private_keys_enabled"], True)
        assert_equal(wallet_info["descriptors"], True)
        assert_equal(wallet_info["format"], "sqlite")

        bech32_addr = wallet.getnewaddress("", "bech32")
        assert bech32_addr.startswith("aluz1"), bech32_addr
        assert not bech32_addr.startswith("bc1"), bech32_addr

        address_info = self.nodes[0].validateaddress(bech32_addr)
        assert_equal(address_info["isvalid"], True)

        return bech32_addr

    def run_test(self):
        wallet_name = "andaluz_backup_source"
        restored_wallet_name = "andaluz_backup_restored"

        self.log.info("Creating Andaluzcoin source wallet")
        create_result = self.nodes[0].createwallet(wallet_name=wallet_name)
        assert_equal(create_result["name"], wallet_name)

        source_wallet = self.nodes[0].get_wallet_rpc(wallet_name)

        self.log.info("Checking source wallet identity")
        source_addr = self.assert_andaluz_wallet_identity(source_wallet, wallet_name)

        self.log.info("Backing up Andaluzcoin wallet")
        backup_file = self.nodes[0].datadir_path / "andaluz_wallet_backup.bak"
        source_wallet.backupwallet(backup_file)
        assert backup_file.exists()

        self.log.info("Unloading source wallet")
        self.nodes[0].unloadwallet(wallet_name)

        self.log.info("Restoring Andaluzcoin wallet from backup")
        restore_result = self.nodes[0].restorewallet(restored_wallet_name, backup_file)
        assert_equal(restore_result["name"], restored_wallet_name)

        restored_wallet = self.nodes[0].get_wallet_rpc(restored_wallet_name)

        self.log.info("Checking restored wallet identity")
        self.assert_andaluz_wallet_identity(restored_wallet, restored_wallet_name)

        self.log.info("Checking restored wallet owns backed-up address")
        restored_source_address_info = restored_wallet.getaddressinfo(source_addr)
        assert_equal(restored_source_address_info["ismine"], True)
        assert_equal(restored_source_address_info["iswatchonly"], False)


if __name__ == "__main__":
    AndaluzWalletBackupRestoreTest(__file__).main()
