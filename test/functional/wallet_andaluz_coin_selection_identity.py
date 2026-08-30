#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet coin selection identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletCoinSelectionIdentityTest(BitcoinTestFramework):
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

    def find_wallet_tx(self, wallet, txid, category):
        matches = [
            entry for entry in wallet.listtransactions("*", 100)
            if entry.get("txid") == txid and entry.get("category") == category
        ]

        assert_equal(len(matches), 1)
        return matches[0]

    def has_utxo(self, utxos, txid, vout):
        return any(
            utxo["txid"] == txid and utxo["vout"] == vout
            for utxo in utxos
        )

    def run_test(self):
        miner_wallet_name = "andaluz_coin_selection_miner"
        sender_wallet_name = "andaluz_coin_selection_sender"
        receiver_wallet_name = "andaluz_coin_selection_receiver"

        receiver_amount = Decimal("1.00000000")
        change_amount = Decimal("48.99900000")
        expected_fee = Decimal("0.00100000")

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

        self.log.info("Mining multiple spendable Andaluzcoin UTXOs to sender")
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

        self.nodes[0].syncwithvalidationinterfacequeue()

        sender_utxos = sender.listunspent(101, 9999999, [sender_mining_address])
        assert_equal(len(sender_utxos), 2)

        for utxo in sender_utxos:
            assert_equal(utxo["amount"], Decimal("50.00000000"))

        sorted_utxos = sorted(sender_utxos, key=lambda utxo: (utxo["txid"], utxo["vout"]))
        selected_utxo = sorted_utxos[0]
        untouched_utxo = sorted_utxos[1]

        selected_outpoint = {
            "txid": selected_utxo["txid"],
            "vout": selected_utxo["vout"],
        }

        untouched_txid = untouched_utxo["txid"]
        untouched_vout = untouched_utxo["vout"]

        self.log.info("Creating manual Andaluzcoin coin-selection PSBT")
        receiver_address = receiver.getnewaddress("andaluz-coin-selection-receiver", "bech32")
        sender_change_address = sender.getrawchangeaddress("bech32")

        self.assert_valid_wallet_address(receiver, receiver_address)
        self.assert_valid_wallet_address(sender, sender_change_address)

        unsigned_psbt = self.nodes[0].createpsbt(
            [selected_outpoint],
            [
                {receiver_address: receiver_amount},
                {sender_change_address: change_amount},
            ],
        )

        self.log.info("Signing manual coin-selection PSBT with sender wallet")
        signed_psbt = sender.walletprocesspsbt(unsigned_psbt)
        assert_equal(signed_psbt["complete"], True)

        finalized = self.nodes[0].finalizepsbt(signed_psbt["psbt"])
        assert_equal(finalized["complete"], True)

        decoded_tx = self.nodes[0].decoderawtransaction(finalized["hex"])
        decoded_inputs = [
            {
                "txid": vin["txid"],
                "vout": vin["vout"],
            }
            for vin in decoded_tx["vin"]
        ]

        assert_equal(decoded_inputs, [selected_outpoint])

        decoded_outputs = {
            output["scriptPubKey"]["address"]: output["value"]
            for output in decoded_tx["vout"]
            if "address" in output["scriptPubKey"]
        }

        assert_equal(decoded_outputs[receiver_address], receiver_amount)
        assert_equal(decoded_outputs[sender_change_address], change_amount)

        selected_input_amount = selected_utxo["amount"]
        decoded_output_total = sum(decoded_outputs.values(), Decimal("0E-8"))
        assert_equal(selected_input_amount - decoded_output_total, expected_fee)

        self.log.info("Broadcasting manual Andaluzcoin coin-selection transaction")
        spend_txid = self.nodes[0].sendrawtransaction(finalized["hex"])
        assert spend_txid in self.nodes[0].getrawmempool(), self.nodes[0].getrawmempool()

        spend_block_hash = self.nodes[0].generatetoaddress(
            1,
            miner_mining_address,
            called_by_framework=True,
        )[0]

        assert_equal(self.nodes[0].getbestblockhash(), spend_block_hash)
        assert_equal(self.nodes[0].getmempoolinfo()["size"], 0)
        self.nodes[0].syncwithvalidationinterfacequeue()

        self.log.info("Checking selected UTXO was spent and other UTXO remains unspent")
        remaining_sender_utxos = sender.listunspent(1, 9999999)

        assert not self.has_utxo(
            remaining_sender_utxos,
            selected_utxo["txid"],
            selected_utxo["vout"],
        ), remaining_sender_utxos

        assert self.has_utxo(
            remaining_sender_utxos,
            untouched_txid,
            untouched_vout,
        ), remaining_sender_utxos

        matching_change_utxos = [
            utxo for utxo in remaining_sender_utxos
            if utxo["txid"] == spend_txid and utxo["address"] == sender_change_address
        ]

        assert_equal(len(matching_change_utxos), 1)
        assert_equal(matching_change_utxos[0]["amount"], change_amount)
        assert_equal(matching_change_utxos[0]["confirmations"], 1)

        self.log.info("Checking receiver got confirmed Andaluzcoin")
        self.wait_until(
            lambda: receiver.getbalances()["mine"]["trusted"] == receiver_amount,
            timeout=60,
        )

        receiver_tx = receiver.gettransaction(spend_txid)
        assert_equal(receiver_tx["amount"], receiver_amount)
        assert_equal(receiver_tx["confirmations"], 1)
        assert_equal(receiver_tx["blockhash"], spend_block_hash)

        receiver_list_entry = self.find_wallet_tx(receiver, spend_txid, "receive")
        assert_equal(receiver_list_entry["amount"], receiver_amount)
        assert_equal(receiver_list_entry["confirmations"], 1)

        self.log.info("Checking final Andaluzcoin wallet identities")
        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletCoinSelectionIdentityTest(__file__).main()
