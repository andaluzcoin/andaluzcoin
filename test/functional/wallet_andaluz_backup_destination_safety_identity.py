#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet backup destination safety identity."""

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import (
    assert_equal,
    assert_raises_rpc_error,
)


class AndaluzWalletBackupDestinationSafetyIdentityTest(BitcoinTestFramework):
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

        source_wallet_name = "andaluz_backup_safety_source"
        restored_wallet_name = "andaluz_backup_safety_restored"

        self.log.info(
            "Checking initial Andaluzcoin runtime identity"
        )

        self.assert_andaluz_runtime_identity()

        self.log.info(
            "Creating Andaluzcoin source wallet at explicit wallet path"
        )

        source_wallet_path = (
            node.datadir_path
            / source_wallet_name
        )

        assert not source_wallet_path.exists()

        create_result = node.createwallet(
            wallet_name=source_wallet_path,
        )

        source_wallet_name = create_result["name"]

        source_wallet = node.get_wallet_rpc(
            source_wallet_name,
        )

        self.assert_wallet_identity(
            source_wallet,
            source_wallet_name,
        )

        assert source_wallet_path.exists()

        source_address = source_wallet.getnewaddress(
            "andaluz-backup-safety",
            "bech32",
        )

        self.assert_andaluz_address(
            source_wallet,
            source_address,
        )

        self.log.info(
            "Recording source wallet state"
        )

        descriptors_before = source_wallet.listdescriptors(
            False,
        )["descriptors"]

        balance_before = source_wallet.getbalance()

        transactions_before = source_wallet.listtransactions(
            "*",
            100,
            0,
            True,
        )

        wallet_path = source_wallet_path
        wallet_parent = source_wallet_path.parent

        assert wallet_path.exists()
        assert wallet_parent.exists()

        self.log.info(
            "Rejecting backup directly onto active wallet path"
        )

        assert_raises_rpc_error(
            -4,
            "backup failed",
            source_wallet.backupwallet,
            wallet_path,
        )

        self.log.info(
            "Rejecting backup directly onto wallet parent directory"
        )

        assert_raises_rpc_error(
            -4,
            "backup failed",
            source_wallet.backupwallet,
            wallet_parent,
        )

        self.log.info(
            "Checking failed backup attempts did not mutate source wallet"
        )

        assert source_wallet_name in node.listwallets()

        self.assert_wallet_identity(
            source_wallet,
            source_wallet_name,
        )

        self.assert_andaluz_address(
            source_wallet,
            source_address,
        )

        assert_equal(
            source_wallet.listdescriptors(False)["descriptors"],
            descriptors_before,
        )

        assert_equal(
            source_wallet.getbalance(),
            balance_before,
        )

        assert_equal(
            source_wallet.listtransactions(
                "*",
                100,
                0,
                True,
            ),
            transactions_before,
        )

        self.log.info(
            "Creating valid backup after rejected unsafe destinations"
        )

        valid_backup = (
            node.datadir_path
            / "andaluz_backup_destination_safety.bak"
        )

        source_wallet.backupwallet(
            valid_backup,
        )

        assert valid_backup.exists()
        assert valid_backup.stat().st_size > 0

        self.log.info(
            "Unloading source wallet"
        )

        node.unloadwallet(
            source_wallet_name,
        )

        assert source_wallet_name not in node.listwallets()

        self.log.info(
            "Restoring valid backup after rejected unsafe backup attempts"
        )

        restore_result = node.restorewallet(
            restored_wallet_name,
            valid_backup,
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

        self.log.info(
            "Checking restored wallet retains original Andaluzcoin address"
        )

        restored_address_info = restored_wallet.getaddressinfo(
            source_address,
        )

        assert_equal(
            restored_address_info["ismine"],
            True,
        )

        assert_equal(
            restored_address_info["iswatchonly"],
            False,
        )

        restored_new_address = restored_wallet.getnewaddress(
            "andaluz-backup-safety-restored",
            "bech32",
        )

        self.assert_andaluz_address(
            restored_wallet,
            restored_new_address,
        )

        self.log.info(
            "Checking final Andaluzcoin runtime identity"
        )

        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletBackupDestinationSafetyIdentityTest(__file__).main()
