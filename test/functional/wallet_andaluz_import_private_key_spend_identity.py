#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet imported private-key spend identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletImportPrivateKeySpendIdentityTest(BitcoinTestFramework):
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

    def assert_wallet_identity(self, wallet, wallet_name, private_keys_enabled=True):
        wallet_info = wallet.getwalletinfo()
        assert_equal(wallet_info["walletname"], wallet_name)
        assert_equal(wallet_info["private_keys_enabled"], private_keys_enabled)
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

    def private_descriptor_import_requests(self, source_wallet):
        requests = []

        for descriptor in source_wallet.listdescriptors(True)["descriptors"]:
            if not descriptor.get("active", False):
                continue

            request = {
                "desc": descriptor["desc"],
                "timestamp": 0,
                "active": True,
            }

            if descriptor.get("internal", False):
                request["internal"] = True

            if "range" in descriptor:
                request["range"] = descriptor["range"]

            if "next_index" in descriptor:
                request["next_index"] = descriptor["next_index"]

            requests.append(request)

        assert requests, source_wallet.listdescriptors(True)
        return requests

    def run_test(self):
        miner_wallet_name = "andaluz_import_privkey_miner"
        sender_wallet_name = "andaluz_import_privkey_sender"
        source_wallet_name = "andaluz_import_privkey_source"
        import_wallet_name = "andaluz_import_privkey_imported"

        amount = Decimal("1.00000000")
        spend_amount = Decimal("0.25000000")

        self.log.info("Checking initial Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()

        self.log.info("Creating Andaluzcoin miner, sender, source, and import wallets")
        self.nodes[0].createwallet(wallet_name=miner_wallet_name)
        self.nodes[0].createwallet(wallet_name=sender_wallet_name)
        self.nodes[0].createwallet(wallet_name=source_wallet_name)
        self.nodes[0].createwallet(
            wallet_name=import_wallet_name,
            blank=True,
        )

        miner = self.nodes[0].get_wallet_rpc(miner_wallet_name)
        sender = self.nodes[0].get_wallet_rpc(sender_wallet_name)
        source = self.nodes[0].get_wallet_rpc(source_wallet_name)
        imported = self.nodes[0].get_wallet_rpc(import_wallet_name)

        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(source, source_wallet_name)
        self.assert_wallet_identity(imported, import_wallet_name)

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

        self.log.info("Creating Andaluzcoin source private-key address")
        source_address = source.getnewaddress("andaluz-import-private-key-source", "bech32")
        self.assert_valid_wallet_address(source, source_address)

        self.log.info("Sending confirmed Andaluzcoin payment to source address")
        txid = sender.sendtoaddress(source_address, amount)
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

        self.log.info("Checking source wallet owns the ALUZ")
        self.wait_until(
            lambda: source.getbalances()["mine"]["trusted"] == amount,
            timeout=60,
        )

        source_tx = source.gettransaction(txid)
        assert_equal(source_tx["amount"], amount)
        assert_equal(source_tx["confirmations"], 1)
        assert_equal(source_tx["blockhash"], confirm_block_hash)

        self.log.info("Importing source private descriptors into second wallet")
        import_requests = self.private_descriptor_import_requests(source)
        import_results = imported.importdescriptors(import_requests)

        assert_equal(len(import_results), len(import_requests))
        for result in import_results:
            assert_equal(result["success"], True)

        imported_address_info = imported.getaddressinfo(source_address)
        assert_equal(imported_address_info["ismine"], True)
        assert_equal(imported_address_info["solvable"], True)

        self.log.info("Rescanning imported private-key wallet blockchain")
        rescan_result = imported.rescanblockchain(0)
        assert "start_height" in rescan_result, rescan_result
        assert "stop_height" in rescan_result, rescan_result
        assert_equal(rescan_result["start_height"], 0)
        assert rescan_result["stop_height"] >= 103, rescan_result

        self.nodes[0].syncwithvalidationinterfacequeue()

        self.wait_until(
            lambda: imported.getbalances()["mine"]["trusted"] == amount,
            timeout=60,
        )

        self.log.info("Checking imported private-key wallet balance recovery")
        assert_equal(imported.getbalance(), amount)
        assert_equal(imported.getbalances()["mine"]["trusted"], amount)
        assert_equal(imported.getbalances()["mine"]["untrusted_pending"], Decimal("0E-8"))

        self.log.info("Checking imported private-key wallet transaction history")
        imported_tx = imported.gettransaction(txid)
        assert_equal(imported_tx["amount"], amount)
        assert_equal(imported_tx["confirmations"], 1)
        assert_equal(imported_tx["blockhash"], confirm_block_hash)

        imported_list_entry = self.find_wallet_tx(imported, txid, "receive")
        assert_equal(imported_list_entry["amount"], amount)
        assert_equal(imported_list_entry["confirmations"], 1)

        self.log.info("Checking imported private-key wallet UTXO recovery")
        imported_utxos = imported.listunspent(1, 9999999, [source_address])
        matching_imported_utxos = [
            utxo for utxo in imported_utxos
            if utxo["txid"] == txid and utxo["address"] == source_address
        ]

        assert_equal(len(matching_imported_utxos), 1)
        assert_equal(matching_imported_utxos[0]["amount"], amount)
        assert_equal(matching_imported_utxos[0]["confirmations"], 1)
        assert_equal(matching_imported_utxos[0].get("spendable", True), True)

        self.log.info("Checking imported private-key wallet can spend the ALUZ")
        sender_return_address = sender.getnewaddress("andaluz-import-private-key-return", "bech32")
        self.assert_valid_wallet_address(sender, sender_return_address)

        spend_txid = imported.sendtoaddress(sender_return_address, spend_amount)
        assert spend_txid in self.nodes[0].getrawmempool(), self.nodes[0].getrawmempool()

        spend_block_hash = self.nodes[0].generatetoaddress(
            1,
            miner_mining_address,
            called_by_framework=True,
        )[0]

        assert_equal(self.nodes[0].getbestblockhash(), spend_block_hash)
        self.nodes[0].syncwithvalidationinterfacequeue()

        imported_spend_tx = imported.gettransaction(spend_txid)
        assert_equal(imported_spend_tx["confirmations"], 1)
        assert_equal(imported_spend_tx["blockhash"], spend_block_hash)

        self.log.info("Checking final Andaluzcoin wallet identities")
        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(source, source_wallet_name)
        self.assert_wallet_identity(imported, import_wallet_name)

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletImportPrivateKeySpendIdentityTest(__file__).main()
