#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet restore validation identity."""

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import (
    assert_equal,
    assert_raises_rpc_error,
)


class AndaluzWalletRestoreValidationIdentityTest(BitcoinTestFramework):
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
        subversion = self.nodes[0].getnetworkinfo()["subversion"]

        assert subversion.startswith("/AndaluzcoinCore:"), subversion
        assert "Satoshi" not in subversion, subversion
        assert "Bitcoin" not in subversion, subversion

    def assert_wallet_identity(
        self,
        wallet,
        wallet_name,
    ):
        wallet_info = wallet.getwalletinfo()

        assert_equal(
            wallet_info["walletname"],
            wallet_name,
        )

        assert_equal(
            wallet_info["private_keys_enabled"],
            True,
        )

        assert_equal(
            wallet_info["descriptors"],
            True,
        )

        assert_equal(
            wallet_info["format"],
            "sqlite",
        )

    def assert_andaluz_address(
        self,
        wallet,
        address,
    ):
        assert address.startswith("aluz1"), address
        assert not address.startswith("bc1"), address

        validate_result = self.nodes[0].validateaddress(
            address,
        )

        assert_equal(
            validate_result["isvalid"],
            True,
        )

        address_info = wallet.getaddressinfo(
            address,
        )

        assert_equal(
            address_info["ismine"],
            True,
        )

        assert_equal(
            address_info["iswatchonly"],
            False,
        )

    def run_test(self):
        node = self.nodes[0]

        source_wallet_name = "andaluz_restore_validation_source"
        existing_wallet_name = "andaluz_restore_validation_existing"
        invalid_restore_name = "andaluz_restore_invalid"
        missing_restore_name = "andaluz_restore_missing"
        restored_wallet_name = "andaluz_restore_validation_restored"

        self.log.info(
            "Checking initial Andaluzcoin runtime identity"
        )

        self.assert_andaluz_runtime_identity()

        self.log.info(
            "Creating source Andaluzcoin wallet"
        )

        create_source = node.createwallet(
            wallet_name=source_wallet_name,
        )

        assert_equal(
            create_source["name"],
            source_wallet_name,
        )

        source_wallet = node.get_wallet_rpc(
            source_wallet_name,
        )

        self.assert_wallet_identity(
            source_wallet,
            source_wallet_name,
        )

        source_address = source_wallet.getnewaddress(
            "andaluz-restore-source",
            "bech32",
        )

        self.assert_andaluz_address(
            source_wallet,
            source_address,
        )

        self.log.info(
            "Creating valid Andaluzcoin wallet backup"
        )

        backup_file = (
            node.datadir_path
            / "andaluz_restore_validation_backup.bak"
        )

        source_wallet.backupwallet(
            backup_file,
        )

        assert backup_file.exists()
        assert backup_file.stat().st_size > 0

        self.log.info(
            "Rejecting invalid wallet backup"
        )

        invalid_backup_file = (
            node.datadir_path
            / "andaluz_invalid_wallet_backup.bak"
        )

        invalid_backup_file.write_text(
            "invalid_wallet_content",
            encoding="utf-8",
        )

        invalid_target_dir = (
            node.wallets_path
            / invalid_restore_name
        )

        assert not invalid_target_dir.exists()

        assert_raises_rpc_error(
            -18,
            "Wallet file verification failed.",
            node.restorewallet,
            invalid_restore_name,
            invalid_backup_file,
        )

        assert not invalid_target_dir.exists()

        assert invalid_restore_name not in node.listwallets()

        self.log.info(
            "Checking source wallet remains intact after invalid restore"
        )

        self.assert_wallet_identity(
            source_wallet,
            source_wallet_name,
        )

        self.assert_andaluz_address(
            source_wallet,
            source_address,
        )

        self.log.info(
            "Rejecting nonexistent backup"
        )

        nonexistent_backup_file = (
            node.datadir_path
            / "andaluz_nonexistent_backup.bak"
        )

        assert not nonexistent_backup_file.exists()

        missing_target_dir = (
            node.wallets_path
            / missing_restore_name
        )

        assert not missing_target_dir.exists()

        assert_raises_rpc_error(
            -8,
            "Backup file does not exist",
            node.restorewallet,
            missing_restore_name,
            nonexistent_backup_file,
        )

        assert not missing_target_dir.exists()

        assert missing_restore_name not in node.listwallets()

        self.log.info(
            "Rejecting empty restored wallet name"
        )

        assert_raises_rpc_error(
            -8,
            "Wallet name cannot be empty",
            node.restorewallet,
            "",
            backup_file,
        )

        self.log.info(
            "Creating existing destination wallet"
        )

        create_existing = node.createwallet(
            wallet_name=existing_wallet_name,
        )

        assert_equal(
            create_existing["name"],
            existing_wallet_name,
        )

        existing_wallet = node.get_wallet_rpc(
            existing_wallet_name,
        )

        self.assert_wallet_identity(
            existing_wallet,
            existing_wallet_name,
        )

        existing_address = existing_wallet.getnewaddress(
            "andaluz-existing-wallet",
            "bech32",
        )

        self.assert_andaluz_address(
            existing_wallet,
            existing_address,
        )

        self.log.info(
            "Recording existing wallet state before rejected overwrite"
        )

        existing_descriptors_before = (
            existing_wallet.listdescriptors(False)["descriptors"]
        )

        existing_balance_before = existing_wallet.getbalance()

        existing_transactions_before = (
            existing_wallet.listtransactions(
                "*",
                100,
                0,
                True,
            )
        )

        self.log.info(
            "Rejecting restore over existing wallet database"
        )

        assert_raises_rpc_error(
            -36,
            "Failed to restore wallet. Database file exists",
            node.restorewallet,
            existing_wallet_name,
            backup_file,
        )

        self.log.info(
            "Checking existing wallet remained loaded and unchanged"
        )

        assert existing_wallet_name in node.listwallets()

        existing_wallet = node.get_wallet_rpc(
            existing_wallet_name,
        )

        self.assert_wallet_identity(
            existing_wallet,
            existing_wallet_name,
        )

        self.assert_andaluz_address(
            existing_wallet,
            existing_address,
        )

        assert_equal(
            existing_wallet.listdescriptors(False)["descriptors"],
            existing_descriptors_before,
        )

        assert_equal(
            existing_wallet.getbalance(),
            existing_balance_before,
        )

        assert_equal(
            existing_wallet.listtransactions(
                "*",
                100,
                0,
                True,
            ),
            existing_transactions_before,
        )

        existing_source_address_info = (
            existing_wallet.getaddressinfo(
                source_address,
            )
        )

        assert_equal(
            existing_source_address_info["ismine"],
            False,
        )

        self.log.info(
            "Checking source wallet remains intact after all failed restores"
        )

        self.assert_wallet_identity(
            source_wallet,
            source_wallet_name,
        )

        self.assert_andaluz_address(
            source_wallet,
            source_address,
        )

        self.log.info(
            "Unloading source before final valid restore"
        )

        node.unloadwallet(
            source_wallet_name,
        )

        self.log.info(
            "Restoring valid backup after validation failures"
        )

        restore_result = node.restorewallet(
            restored_wallet_name,
            backup_file,
        )

        assert_equal(
            restore_result["name"],
            restored_wallet_name,
        )

        restored_wallet = node.get_wallet_rpc(
            restored_wallet_name,
        )

        self.assert_wallet_identity(
            restored_wallet,
            restored_wallet_name,
        )

        restored_source_address_info = (
            restored_wallet.getaddressinfo(
                source_address,
            )
        )

        assert_equal(
            restored_source_address_info["ismine"],
            True,
        )

        assert_equal(
            restored_source_address_info["iswatchonly"],
            False,
        )

        restored_new_address = restored_wallet.getnewaddress(
            "andaluz-restored-wallet",
            "bech32",
        )

        self.assert_andaluz_address(
            restored_wallet,
            restored_new_address,
        )

        self.log.info(
            "Checking failed restore targets were never created"
        )

        assert not invalid_target_dir.exists()
        assert not missing_target_dir.exists()

        self.log.info(
            "Checking final Andaluzcoin runtime identity"
        )

        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletRestoreValidationIdentityTest(__file__).main()
