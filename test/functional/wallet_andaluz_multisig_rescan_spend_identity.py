#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet multisig rescan spend identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletMultisigRescanSpendIdentityTest(BitcoinTestFramework):
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

    def find_wallet_tx(self, wallet, txid, category, include_watchonly=False):
        matches = [
            entry for entry in wallet.listtransactions("*", 100, 0, include_watchonly)
            if entry.get("txid") == txid and entry.get("category") == category
        ]

        assert_equal(len(matches), 1)
        return matches[0]

    def run_test(self):
        miner_wallet_name = "andaluz_multisig_rescan_miner"
        sender_wallet_name = "andaluz_multisig_rescan_sender"
        signer_one_wallet_name = "andaluz_multisig_rescan_signer_one"
        signer_two_wallet_name = "andaluz_multisig_rescan_signer_two"
        multisig_wallet_name = "andaluz_multisig_rescan_coordinator"
        receiver_wallet_name = "andaluz_multisig_rescan_receiver"

        multisig_amount = Decimal("1.00000000")
        spend_amount = Decimal("0.99900000")

        self.log.info("Checking initial Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()

        self.log.info("Creating Andaluzcoin miner, sender, signer, multisig, and receiver wallets")
        self.nodes[0].createwallet(wallet_name=miner_wallet_name)
        self.nodes[0].createwallet(wallet_name=sender_wallet_name)
        self.nodes[0].createwallet(wallet_name=signer_one_wallet_name)
        self.nodes[0].createwallet(wallet_name=signer_two_wallet_name)
        self.nodes[0].createwallet(
            wallet_name=multisig_wallet_name,
            disable_private_keys=True,
            blank=True,
        )
        self.nodes[0].createwallet(wallet_name=receiver_wallet_name)

        miner = self.nodes[0].get_wallet_rpc(miner_wallet_name)
        sender = self.nodes[0].get_wallet_rpc(sender_wallet_name)
        signer_one = self.nodes[0].get_wallet_rpc(signer_one_wallet_name)
        signer_two = self.nodes[0].get_wallet_rpc(signer_two_wallet_name)
        multisig_wallet = self.nodes[0].get_wallet_rpc(multisig_wallet_name)
        receiver = self.nodes[0].get_wallet_rpc(receiver_wallet_name)

        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(signer_one, signer_one_wallet_name)
        self.assert_wallet_identity(signer_two, signer_two_wallet_name)
        self.assert_wallet_identity(multisig_wallet, multisig_wallet_name, private_keys_enabled=False)
        self.assert_wallet_identity(receiver, receiver_wallet_name)

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

        assert sender.getbalance() >= multisig_amount, sender.getbalance()

        self.log.info("Creating Andaluzcoin multisig signer public keys")
        signer_one_address = signer_one.getnewaddress("andaluz-multisig-rescan-signer-one", "bech32")
        signer_two_address = signer_two.getnewaddress("andaluz-multisig-rescan-signer-two", "bech32")

        self.assert_valid_wallet_address(signer_one, signer_one_address)
        self.assert_valid_wallet_address(signer_two, signer_two_address)

        signer_one_pubkey = signer_one.getaddressinfo(signer_one_address)["pubkey"]
        signer_two_pubkey = signer_two.getaddressinfo(signer_two_address)["pubkey"]

        self.log.info("Creating Andaluzcoin 2-of-2 multisig descriptor")
        multisig_result = self.nodes[0].createmultisig(
            2,
            [signer_one_pubkey, signer_two_pubkey],
            "bech32",
        )

        multisig_address = multisig_result["address"]
        multisig_descriptor = multisig_result["descriptor"]

        assert_equal(self.nodes[0].validateaddress(multisig_address)["isvalid"], True)
        assert multisig_address.startswith("bcrt1"), multisig_address

        self.log.info("Importing multisig descriptor into watch-only coordinator wallet")
        import_result = multisig_wallet.importdescriptors([{
            "desc": multisig_descriptor,
            "timestamp": 0,
            "label": "andaluz-2-of-2-multisig-rescan",
        }])

        assert_equal(import_result[0]["success"], True)
        assert_equal(multisig_wallet.getwalletinfo()["private_keys_enabled"], False)

        multisig_address_info = multisig_wallet.getaddressinfo(multisig_address)
        assert (
            multisig_address_info.get("iswatchonly", False)
            or multisig_address_info.get("ismine", False)
        ), multisig_address_info
        assert_equal(multisig_address_info["solvable"], True)

        self.log.info("Unloading multisig coordinator wallet before funding")
        self.nodes[0].unloadwallet(multisig_wallet_name)
        assert multisig_wallet_name not in self.nodes[0].listwallets()

        self.log.info("Sending confirmed Andaluzcoin payment to multisig address while coordinator is offline")
        funding_txid = sender.sendtoaddress(multisig_address, multisig_amount)
        assert funding_txid in self.nodes[0].getrawmempool(), self.nodes[0].getrawmempool()
        self.nodes[0].syncwithvalidationinterfacequeue()

        funding_block_hash = self.nodes[0].generatetoaddress(
            1,
            miner_mining_address,
            called_by_framework=True,
        )[0]

        assert_equal(self.nodes[0].getbestblockhash(), funding_block_hash)
        assert_equal(self.nodes[0].getmempoolinfo()["size"], 0)
        self.nodes[0].syncwithvalidationinterfacequeue()

        self.log.info("Reloading multisig coordinator wallet")
        load_result = self.nodes[0].loadwallet(multisig_wallet_name)
        assert_equal(load_result["name"], multisig_wallet_name)

        multisig_wallet = self.nodes[0].get_wallet_rpc(multisig_wallet_name)
        self.assert_wallet_identity(multisig_wallet, multisig_wallet_name, private_keys_enabled=False)

        self.log.info("Rescanning multisig coordinator wallet blockchain")
        rescan_result = multisig_wallet.rescanblockchain(0)
        assert "start_height" in rescan_result, rescan_result
        assert "stop_height" in rescan_result, rescan_result
        assert_equal(rescan_result["start_height"], 0)
        assert rescan_result["stop_height"] >= 103, rescan_result

        self.nodes[0].syncwithvalidationinterfacequeue()

        self.wait_until(
            lambda: self.trusted_balance_total(multisig_wallet) == multisig_amount,
            timeout=60,
        )

        self.log.info("Checking recovered multisig wallet balance, history, and UTXO")
        assert_equal(self.trusted_balance_total(multisig_wallet), multisig_amount)

        funding_tx = multisig_wallet.gettransaction(funding_txid, True)
        assert_equal(funding_tx["amount"], multisig_amount)
        assert_equal(funding_tx["confirmations"], 1)
        assert_equal(funding_tx["blockhash"], funding_block_hash)

        funding_list_entry = self.find_wallet_tx(
            multisig_wallet,
            funding_txid,
            "receive",
            include_watchonly=True,
        )
        assert_equal(funding_list_entry["amount"], multisig_amount)
        assert_equal(funding_list_entry["confirmations"], 1)

        multisig_utxos = multisig_wallet.listunspent(1, 9999999, [multisig_address])
        matching_multisig_utxos = [
            utxo for utxo in multisig_utxos
            if utxo["txid"] == funding_txid and utxo["address"] == multisig_address
        ]

        assert_equal(len(matching_multisig_utxos), 1)
        assert_equal(matching_multisig_utxos[0]["amount"], multisig_amount)
        assert_equal(matching_multisig_utxos[0]["confirmations"], 1)

        self.log.info("Creating PSBT spend from recovered multisig UTXO")
        receiver_address = receiver.getnewaddress("andaluz-multisig-rescan-receiver", "bech32")
        self.assert_valid_wallet_address(receiver, receiver_address)

        unsigned_psbt = self.nodes[0].createpsbt(
            [{
                "txid": matching_multisig_utxos[0]["txid"],
                "vout": matching_multisig_utxos[0]["vout"],
            }],
            [{receiver_address: spend_amount}],
        )

        updated_psbt = multisig_wallet.walletprocesspsbt(
            unsigned_psbt,
            False,
            "ALL",
            True,
        )["psbt"]

        self.log.info("Signing recovered multisig PSBT with signer one")
        signer_one_result = signer_one.walletprocesspsbt(updated_psbt)
        assert_equal(signer_one_result["complete"], False)

        self.log.info("Signing recovered multisig PSBT with signer two")
        signer_two_result = signer_two.walletprocesspsbt(signer_one_result["psbt"])

        finalized = self.nodes[0].finalizepsbt(signer_two_result["psbt"])
        assert_equal(finalized["complete"], True)

        self.log.info("Broadcasting finalized Andaluzcoin multisig rescan spend")
        spend_txid = self.nodes[0].sendrawtransaction(finalized["hex"])
        assert spend_txid in self.nodes[0].getrawmempool(), self.nodes[0].getrawmempool()

        spend_block_hash = self.nodes[0].generatetoaddress(
            1,
            miner_mining_address,
            called_by_framework=True,
        )[0]

        assert_equal(self.nodes[0].getbestblockhash(), spend_block_hash)
        self.nodes[0].syncwithvalidationinterfacequeue()

        self.log.info("Checking receiver got confirmed Andaluzcoin from recovered multisig spend")
        self.wait_until(
            lambda: receiver.getbalances()["mine"]["trusted"] == spend_amount,
            timeout=60,
        )

        receiver_tx = receiver.gettransaction(spend_txid)
        assert_equal(receiver_tx["amount"], spend_amount)
        assert_equal(receiver_tx["confirmations"], 1)
        assert_equal(receiver_tx["blockhash"], spend_block_hash)

        receiver_list_entry = self.find_wallet_tx(receiver, spend_txid, "receive")
        assert_equal(receiver_list_entry["amount"], spend_amount)
        assert_equal(receiver_list_entry["confirmations"], 1)

        self.log.info("Checking final Andaluzcoin wallet identities")
        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(signer_one, signer_one_wallet_name)
        self.assert_wallet_identity(signer_two, signer_two_wallet_name)
        self.assert_wallet_identity(multisig_wallet, multisig_wallet_name, private_keys_enabled=False)
        self.assert_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletMultisigRescanSpendIdentityTest(__file__).main()
