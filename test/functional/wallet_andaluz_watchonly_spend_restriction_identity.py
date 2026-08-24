#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin watch-only wallet spend restriction identity."""

from decimal import Decimal

from test_framework.authproxy import JSONRPCException
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletWatchonlySpendRestrictionIdentityTest(BitcoinTestFramework):
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

    def trusted_balance_total(self, wallet):
        balances = wallet.getbalances()
        total = balances["mine"]["trusted"]

        if "watchonly" in balances:
            total += balances["watchonly"]["trusted"]

        return total

    def untrusted_pending_total(self, wallet):
        balances = wallet.getbalances()
        total = balances["mine"]["untrusted_pending"]

        if "watchonly" in balances:
            total += balances["watchonly"]["untrusted_pending"]

        return total

    def assert_rpc_fails(self, call):
        try:
            call()
        except JSONRPCException:
            return

        raise AssertionError("Expected watch-only wallet RPC call to fail")

    def find_wallet_tx(self, wallet, txid, category, include_watchonly=False):
        matches = [
            entry for entry in wallet.listtransactions("*", 100, 0, include_watchonly)
            if entry.get("txid") == txid and entry.get("category") == category
        ]

        assert_equal(len(matches), 1)
        return matches[0]

    def run_test(self):
        miner_wallet_name = "andaluz_watchonly_miner"
        sender_wallet_name = "andaluz_watchonly_sender"
        receiver_wallet_name = "andaluz_watchonly_receiver"
        watch_wallet_name = "andaluz_watchonly_restriction"

        amount = Decimal("1.00000000")
        spend_amount = Decimal("0.25000000")

        self.log.info("Checking initial Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()

        self.log.info("Creating Andaluzcoin miner, sender, receiver, and watch-only wallets")
        self.nodes[0].createwallet(wallet_name=miner_wallet_name)
        self.nodes[0].createwallet(wallet_name=sender_wallet_name)
        self.nodes[0].createwallet(wallet_name=receiver_wallet_name)
        self.nodes[0].createwallet(
            wallet_name=watch_wallet_name,
            disable_private_keys=True,
            blank=True,
        )

        miner = self.nodes[0].get_wallet_rpc(miner_wallet_name)
        sender = self.nodes[0].get_wallet_rpc(sender_wallet_name)
        receiver = self.nodes[0].get_wallet_rpc(receiver_wallet_name)
        watch = self.nodes[0].get_wallet_rpc(watch_wallet_name)

        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver, receiver_wallet_name)
        self.assert_wallet_identity(watch, watch_wallet_name, private_keys_enabled=False)

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
        receiver_address = receiver.getnewaddress("andaluz-watchonly-receiver", "bech32")
        self.assert_valid_wallet_address(receiver, receiver_address)

        self.log.info("Importing receiver address descriptor into watch-only wallet")
        watch_descriptor = self.nodes[0].getdescriptorinfo(
            f"addr({receiver_address})"
        )["descriptor"]

        import_result = watch.importdescriptors([{
            "desc": watch_descriptor,
            "timestamp": "now",
            "label": "andaluz-watchonly-restriction",
        }])

        assert_equal(import_result[0]["success"], True)
        assert_equal(watch.getwalletinfo()["private_keys_enabled"], False)

        self.log.info("Sending confirmed Andaluzcoin payment to imported address")
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

        self.log.info("Rescanning watch-only wallet blockchain")
        rescan_result = watch.rescanblockchain(0)
        assert "start_height" in rescan_result, rescan_result
        assert "stop_height" in rescan_result, rescan_result
        assert_equal(rescan_result["start_height"], 0)
        assert rescan_result["stop_height"] >= 103, rescan_result

        self.nodes[0].syncwithvalidationinterfacequeue()

        self.wait_until(
            lambda: self.trusted_balance_total(watch) == amount,
            timeout=60,
        )

        self.log.info("Checking watch-only wallet sees imported ALUZ")
        assert_equal(self.trusted_balance_total(watch), amount)
        assert_equal(self.untrusted_pending_total(watch), Decimal("0E-8"))
        assert_equal(watch.getwalletinfo()["private_keys_enabled"], False)

        watch_tx = watch.gettransaction(txid, True)
        assert_equal(watch_tx["amount"], amount)
        assert_equal(watch_tx["confirmations"], 1)
        assert_equal(watch_tx["blockhash"], confirm_block_hash)

        watch_list_entry = self.find_wallet_tx(
            watch,
            txid,
            "receive",
            include_watchonly=True,
        )
        assert_equal(watch_list_entry["amount"], amount)
        assert_equal(watch_list_entry["confirmations"], 1)

        watch_utxos = watch.listunspent(1, 9999999, [receiver_address])
        matching_watch_utxos = [
            utxo for utxo in watch_utxos
            if utxo["txid"] == txid and utxo["address"] == receiver_address
        ]

        assert_equal(len(matching_watch_utxos), 1)
        assert_equal(matching_watch_utxos[0]["amount"], amount)
        assert_equal(matching_watch_utxos[0]["confirmations"], 1)

        self.log.info("Checking watch-only wallet cannot sign the imported ALUZ")
        sender_return_address = sender.getnewaddress("andaluz-watchonly-return", "bech32")
        self.assert_valid_wallet_address(sender, sender_return_address)

        unsigned_raw_tx = self.nodes[0].createrawtransaction(
            [{
                "txid": matching_watch_utxos[0]["txid"],
                "vout": matching_watch_utxos[0]["vout"],
            }],
            {sender_return_address: spend_amount},
        )

        try:
            watch_signed = watch.signrawtransactionwithwallet(unsigned_raw_tx)
            assert_equal(watch_signed["complete"], False)
        except JSONRPCException:
            pass

        self.log.info("Checking watch-only wallet cannot send the imported ALUZ")
        self.assert_rpc_fails(
            lambda: watch.sendtoaddress(sender_return_address, spend_amount)
        )

        self.log.info("Checking private-key receiver wallet owns and can spend the ALUZ")
        self.wait_until(
            lambda: receiver.getbalances()["mine"]["trusted"] == amount,
            timeout=60,
        )

        receiver_utxos = receiver.listunspent(1, 9999999, [receiver_address])
        matching_receiver_utxos = [
            utxo for utxo in receiver_utxos
            if utxo["txid"] == txid and utxo["address"] == receiver_address
        ]

        assert_equal(len(matching_receiver_utxos), 1)
        assert_equal(matching_receiver_utxos[0]["amount"], amount)
        assert_equal(matching_receiver_utxos[0].get("spendable", True), True)

        spend_txid = receiver.sendtoaddress(sender_return_address, spend_amount)
        assert spend_txid in self.nodes[0].getrawmempool(), self.nodes[0].getrawmempool()

        spend_block_hash = self.nodes[0].generatetoaddress(
            1,
            miner_mining_address,
            called_by_framework=True,
        )[0]

        assert_equal(self.nodes[0].getbestblockhash(), spend_block_hash)
        self.nodes[0].syncwithvalidationinterfacequeue()

        receiver_spend_tx = receiver.gettransaction(spend_txid)
        assert_equal(receiver_spend_tx["confirmations"], 1)
        assert_equal(receiver_spend_tx["blockhash"], spend_block_hash)

        self.log.info("Checking final Andaluzcoin wallet identities")
        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver, receiver_wallet_name)
        self.assert_wallet_identity(watch, watch_wallet_name, private_keys_enabled=False)

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletWatchonlySpendRestrictionIdentityTest(__file__).main()
