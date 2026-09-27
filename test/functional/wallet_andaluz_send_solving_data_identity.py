#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet send solving-data identity."""

from decimal import Decimal

from test_framework.descriptors import descsum_create
from test_framework.wallet_util import generate_keypair
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal, assert_raises_rpc_error


class AndaluzWalletSendSolvingDataIdentityTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 2
        self.setup_clean_chain = True
        self.chain = "regtest"
        self.wallet_names = []
        self.extra_args = [
            [
                "-dnsseed=0",
                "-fixedseeds=0",
            ],
            [
                "-dnsseed=0",
                "-fixedseeds=0",
            ],
        ]

    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    def assert_andaluz_runtime_identity(self, node):
        assert_equal(
            node.getblockchaininfo()["chain"],
            "regtest",
        )

        subversion = node.getnetworkinfo()["subversion"]

        assert subversion.startswith("/AndaluzcoinCore:"), subversion
        assert "Satoshi" not in subversion, subversion
        assert "Bitcoin" not in subversion, subversion

    def assert_wallet_identity(self, wallet, wallet_name):
        wallet_info = wallet.getwalletinfo()

        assert_equal(wallet_info["walletname"], wallet_name)
        assert_equal(wallet_info["private_keys_enabled"], True)
        assert_equal(wallet_info["descriptors"], True)
        assert_equal(wallet_info["format"], "sqlite")

    def assert_valid_wallet_address(self, node, wallet, address):
        address_info = node.validateaddress(address)
        assert_equal(address_info["isvalid"], True)

        wallet_address_info = wallet.getaddressinfo(address)
        assert_equal(wallet_address_info["ismine"], True)
        assert_equal(wallet_address_info["solvable"], True)

    def find_wallet_tx(self, wallet, txid, category):
        matches = [
            entry
            for entry in wallet.listtransactions("*", 100)
            if entry.get("txid") == txid
            and entry.get("category") == category
        ]

        assert_equal(len(matches), 1)
        return matches[0]

    def sign_external_psbt(self, spending_wallet, external_wallet, psbt):
        first_pass = spending_wallet.walletprocesspsbt(
            psbt,
        )

        final_pass = external_wallet.walletprocesspsbt(
            first_pass["psbt"],
        )

        assert_equal(
            final_pass["complete"],
            True,
        )

        return final_pass

    def run_test(self):
        miner_wallet_name = "andaluz_send_solving_data_miner"
        source_wallet_name = "andaluz_send_solving_data_source"
        spending_wallet_name = "andaluz_send_solving_data_spender"
        external_wallet_name = "andaluz_send_solving_data_external"
        receiver_wallet_name = "andaluz_send_solving_data_receiver"

        coinbase_amount = Decimal("50.00000000")
        external_amount = Decimal("10.00000000")
        wallet_amount = Decimal("10.00000000")
        payment_amount = Decimal("15.00000000")

        self.log.info("Checking initial Andaluzcoin runtime identity")

        self.assert_andaluz_runtime_identity(self.nodes[0])
        self.assert_andaluz_runtime_identity(self.nodes[1])

        self.log.info("Creating Andaluzcoin wallets")

        self.nodes[0].createwallet(
            wallet_name=miner_wallet_name,
        )

        self.nodes[0].createwallet(
            wallet_name=source_wallet_name,
        )

        self.nodes[0].createwallet(
            wallet_name=receiver_wallet_name,
        )

        self.nodes[1].createwallet(
            wallet_name=spending_wallet_name,
        )

        self.nodes[1].createwallet(
            wallet_name=external_wallet_name,
        )

        miner = self.nodes[0].get_wallet_rpc(
            miner_wallet_name,
        )

        source = self.nodes[0].get_wallet_rpc(
            source_wallet_name,
        )

        receiver = self.nodes[0].get_wallet_rpc(
            receiver_wallet_name,
        )

        spending_wallet = self.nodes[1].get_wallet_rpc(
            spending_wallet_name,
        )

        external_wallet = self.nodes[1].get_wallet_rpc(
            external_wallet_name,
        )

        self.assert_wallet_identity(
            miner,
            miner_wallet_name,
        )

        self.assert_wallet_identity(
            source,
            source_wallet_name,
        )

        self.assert_wallet_identity(
            spending_wallet,
            spending_wallet_name,
        )

        self.assert_wallet_identity(
            external_wallet,
            external_wallet_name,
        )

        self.assert_wallet_identity(
            receiver,
            receiver_wallet_name,
        )

        self.log.info("Mining spendable ALUZ to source wallet")

        source_mining_address = source.getnewaddress(
            "",
            "bech32",
        )

        miner_mining_address = miner.getnewaddress(
            "",
            "bech32",
        )

        self.assert_valid_wallet_address(
            self.nodes[0],
            source,
            source_mining_address,
        )

        self.assert_valid_wallet_address(
            self.nodes[0],
            miner,
            miner_mining_address,
        )

        source_blocks = self.nodes[0].generatetoaddress(
            1,
            source_mining_address,
            called_by_framework=True,
        )

        assert_equal(
            len(source_blocks),
            1,
        )

        maturity_blocks = self.nodes[0].generatetoaddress(
            100,
            miner_mining_address,
            called_by_framework=True,
        )

        assert_equal(
            len(maturity_blocks),
            100,
        )

        self.sync_all()

        assert_equal(
            source.getbalances()["mine"]["trusted"],
            coinbase_amount,
        )

        self.log.info(
            "Creating externally controlled Andaluzcoin descriptor"
        )

        private_key, _ = generate_keypair(
            wif=True,
        )

        external_descriptor = descsum_create(
            f"sh(wsh(pkh({private_key})))"
        )

        import_result = external_wallet.importdescriptors([
            {
                "desc": external_descriptor,
                "timestamp": "now",
            }
        ])

        assert_equal(
            len(import_result),
            1,
        )

        assert_equal(
            import_result[0]["success"],
            True,
        )

        external_address = self.nodes[0].deriveaddresses(
            external_descriptor,
        )[0]

        external_address_info = external_wallet.getaddressinfo(
            external_address,
        )

        assert_equal(
            external_address_info["ismine"],
            True,
        )

        assert_equal(
            external_address_info["solvable"],
            True,
        )

        self.log.info(
            "Funding external descriptor and spending wallet"
        )

        external_funding_txid = source.sendtoaddress(
            external_address,
            external_amount,
        )

        spending_address = spending_wallet.getnewaddress(
            "andaluz-solving-data-wallet",
            "bech32",
        )

        self.assert_valid_wallet_address(
            self.nodes[1],
            spending_wallet,
            spending_address,
        )

        wallet_funding_txid = source.sendtoaddress(
            spending_address,
            wallet_amount,
        )

        assert_equal(
            len(external_funding_txid),
            64,
        )

        assert_equal(
            len(wallet_funding_txid),
            64,
        )

        self.sync_all()

        self.log.info(
            "Confirming external and wallet-owned funding outputs"
        )

        confirmation_blocks = self.nodes[0].generatetoaddress(
            6,
            miner_mining_address,
            called_by_framework=True,
        )

        assert_equal(
            len(confirmation_blocks),
            6,
        )

        self.sync_all()

        self.nodes[0].syncwithvalidationinterfacequeue()
        self.nodes[1].syncwithvalidationinterfacequeue()

        external_utxos = external_wallet.listunspent(
            addresses=[external_address],
        )

        assert_equal(
            len(external_utxos),
            1,
        )

        external_utxo = external_utxos[0]

        assert_equal(
            external_utxo["amount"],
            external_amount,
        )

        assert external_utxo["confirmations"] >= 6, external_utxo

        spending_utxos = spending_wallet.listunspent()

        assert_equal(
            len(spending_utxos),
            1,
        )

        spending_utxo = spending_utxos[0]

        assert_equal(
            spending_utxo["amount"],
            wallet_amount,
        )

        assert spending_utxo["confirmations"] >= 6, spending_utxo

        assert_equal(
            spending_wallet.getbalance(),
            wallet_amount,
        )

        assert_equal(
            external_wallet.getbalance(),
            external_amount,
        )

        receiver_address = receiver.getnewaddress(
            "andaluz-send-solving-data-receiver",
            "bech32",
        )

        self.assert_valid_wallet_address(
            self.nodes[0],
            receiver,
            receiver_address,
        )

        mempool_before = set(
            self.nodes[0].getrawmempool()
        )

        assert_equal(
            mempool_before,
            set(),
        )

        expected_error = (
            "Not solvable pre-selected input COutPoint("
            f"{external_utxo['txid'][0:10]}, {external_utxo['vout']})"
        )

        self.log.info(
            "Checking external preset input fails without solving data"
        )

        assert_raises_rpc_error(
            -4,
            expected_error,
            spending_wallet.send,
            outputs={
                receiver_address: payment_amount,
            },
            options={
                "inputs": [
                    external_utxo,
                ],
                "add_inputs": True,
                "psbt": True,
                "add_to_wallet": False,
            },
        )

        self.log.info(
            "Checking rejected external-input attempt changed no state"
        )

        assert_equal(
            set(self.nodes[0].getrawmempool()),
            set(),
        )

        assert_equal(
            set(self.nodes[1].getrawmempool()),
            set(),
        )

        assert_equal(
            spending_wallet.getbalance(),
            wallet_amount,
        )

        assert_equal(
            external_wallet.getbalance(),
            external_amount,
        )

        assert_equal(
            receiver.getbalance(),
            Decimal("0E-8"),
        )

        self.log.info(
            "Creating PSBT with pubkey/script solving data"
        )

        script_solving_result = spending_wallet.send(
            outputs={
                receiver_address: payment_amount,
            },
            options={
                "inputs": [
                    external_utxo,
                ],
                "add_inputs": True,
                "psbt": True,
                "add_to_wallet": False,
                "solving_data": {
                    "pubkeys": [
                        external_address_info["pubkey"],
                    ],
                    "scripts": [
                        external_address_info["embedded"]["scriptPubKey"],
                        external_address_info["embedded"]["embedded"]["scriptPubKey"],
                    ],
                },
            },
        )

        assert_equal(
            script_solving_result["complete"],
            False,
        )

        assert "psbt" in script_solving_result, script_solving_result

        script_signed = self.sign_external_psbt(
            spending_wallet,
            external_wallet,
            script_solving_result["psbt"],
        )

        assert "psbt" in script_signed, script_signed

        self.log.info(
            "Checking pubkey/script solving data produces completable PSBT"
        )

        script_finalized = self.nodes[0].finalizepsbt(
            script_signed["psbt"],
        )

        assert_equal(
            script_finalized["complete"],
            True,
        )

        assert "hex" in script_finalized, script_finalized

        script_accept = self.nodes[0].testmempoolaccept([
            script_finalized["hex"],
        ])

        assert_equal(
            len(script_accept),
            1,
        )

        assert_equal(
            script_accept[0]["allowed"],
            True,
        )

        self.log.info(
            "Creating PSBT with descriptor solving data"
        )

        descriptor_solving_result = spending_wallet.send(
            outputs={
                receiver_address: payment_amount,
            },
            options={
                "inputs": [
                    external_utxo,
                ],
                "add_inputs": True,
                "psbt": True,
                "add_to_wallet": False,
                "solving_data": {
                    "descriptors": [
                        external_descriptor,
                    ],
                },
            },
        )

        assert_equal(
            descriptor_solving_result["complete"],
            False,
        )

        assert "psbt" in descriptor_solving_result, (
            descriptor_solving_result
        )

        descriptor_signed = self.sign_external_psbt(
            spending_wallet,
            external_wallet,
            descriptor_solving_result["psbt"],
        )

        assert "psbt" in descriptor_signed, descriptor_signed

        self.log.info(
            "Checking descriptor solving data contains expected inputs"
        )

        decoded_psbt = self.nodes[0].decodepsbt(
            descriptor_signed["psbt"],
        )

        decoded_inputs = {
            (
                vin["txid"],
                vin["vout"],
            )
            for vin in decoded_psbt["tx"]["vin"]
        }

        expected_inputs = {
            (
                external_utxo["txid"],
                external_utxo["vout"],
            ),
            (
                spending_utxo["txid"],
                spending_utxo["vout"],
            ),
        }

        assert_equal(
            decoded_inputs,
            expected_inputs,
        )

        assert_equal(
            len(decoded_psbt["tx"]["vin"]),
            2,
        )

        external_input_index = None

        for index, vin in enumerate(
            decoded_psbt["tx"]["vin"]
        ):
            if (
                vin["txid"] == external_utxo["txid"]
                and vin["vout"] == external_utxo["vout"]
            ):
                external_input_index = index
                break

        assert external_input_index is not None, decoded_psbt

        external_psbt_input = decoded_psbt["inputs"][
            external_input_index
        ]

        assert (
            "final_scriptSig" in external_psbt_input
            or "final_scriptwitness" in external_psbt_input
        ), external_psbt_input

        self.log.info(
            "Finalizing descriptor-solving-data PSBT"
        )

        finalized = self.nodes[0].finalizepsbt(
            descriptor_signed["psbt"],
        )

        assert_equal(
            finalized["complete"],
            True,
        )

        assert "hex" in finalized, finalized

        raw_hex = finalized["hex"]

        decoded_tx = self.nodes[0].decoderawtransaction(
            raw_hex,
        )

        spend_txid = decoded_tx["txid"]

        assert_equal(
            len(spend_txid),
            64,
        )

        recipient_outputs = [
            output
            for output in decoded_tx["vout"]
            if output["scriptPubKey"].get("address")
            == receiver_address
        ]

        assert_equal(
            len(recipient_outputs),
            1,
        )

        assert_equal(
            recipient_outputs[0]["value"],
            payment_amount,
        )

        total_input_amount = (
            external_amount
            + wallet_amount
        )

        total_output_amount = sum(
            (
                output["value"]
                for output in decoded_tx["vout"]
            ),
            Decimal("0E-8"),
        )

        actual_fee = (
            total_input_amount
            - total_output_amount
        )

        assert actual_fee > Decimal("0"), actual_fee
        assert actual_fee < payment_amount, actual_fee

        self.log.info(
            "Checking descriptor-solving transaction is mempool-valid"
        )

        accept_result = self.nodes[0].testmempoolaccept([
            raw_hex,
        ])

        assert_equal(
            len(accept_result),
            1,
        )

        assert_equal(
            accept_result[0]["txid"],
            spend_txid,
        )

        assert_equal(
            accept_result[0]["allowed"],
            True,
        )

        self.log.info(
            "Checking PSBT construction did not automatically broadcast"
        )

        assert_equal(
            set(self.nodes[0].getrawmempool()),
            set(),
        )

        assert_equal(
            set(self.nodes[1].getrawmempool()),
            set(),
        )

        assert_equal(
            receiver.getbalance(),
            Decimal("0E-8"),
        )

        self.log.info(
            "Broadcasting solving-data Andaluzcoin transaction"
        )

        broadcast_txid = self.nodes[0].sendrawtransaction(
            raw_hex,
        )

        assert_equal(
            broadcast_txid,
            spend_txid,
        )

        self.sync_all()

        assert spend_txid in self.nodes[0].getrawmempool(), (
            self.nodes[0].getrawmempool()
        )

        assert spend_txid in self.nodes[1].getrawmempool(), (
            self.nodes[1].getrawmempool()
        )

        self.nodes[0].syncwithvalidationinterfacequeue()
        self.nodes[1].syncwithvalidationinterfacequeue()

        self.log.info(
            "Checking receiver sees pending 15 ALUZ payment"
        )

        self.wait_until(
            lambda:
                receiver.getbalances()["mine"]["untrusted_pending"]
                == payment_amount,
            timeout=60,
        )

        receiver_pending_tx = receiver.gettransaction(
            spend_txid,
        )

        assert_equal(
            receiver_pending_tx["amount"],
            payment_amount,
        )

        assert_equal(
            receiver_pending_tx["confirmations"],
            0,
        )

        receiver_pending_entry = self.find_wallet_tx(
            receiver,
            spend_txid,
            "receive",
        )

        assert_equal(
            receiver_pending_entry["amount"],
            payment_amount,
        )

        assert_equal(
            receiver_pending_entry["confirmations"],
            0,
        )

        self.log.info(
            "Confirming solving-data Andaluzcoin transaction"
        )

        confirm_block_hash = self.nodes[0].generatetoaddress(
            1,
            miner_mining_address,
            called_by_framework=True,
        )[0]

        self.sync_all()

        assert_equal(
            self.nodes[0].getbestblockhash(),
            confirm_block_hash,
        )

        assert_equal(
            self.nodes[1].getbestblockhash(),
            confirm_block_hash,
        )

        assert_equal(
            self.nodes[0].getmempoolinfo()["size"],
            0,
        )

        assert_equal(
            self.nodes[1].getmempoolinfo()["size"],
            0,
        )

        self.nodes[0].syncwithvalidationinterfacequeue()
        self.nodes[1].syncwithvalidationinterfacequeue()

        expected_spending_balance = (
            total_input_amount
            - payment_amount
            - actual_fee
        )

        self.wait_until(
            lambda:
                receiver.getbalances()["mine"]["trusted"]
                == payment_amount,
            timeout=60,
        )

        self.wait_until(
            lambda:
                external_wallet.getbalance()
                == Decimal("0E-8"),
            timeout=60,
        )

        self.wait_until(
            lambda:
                spending_wallet.getbalance()
                == expected_spending_balance,
            timeout=60,
        )

        self.log.info(
            "Checking confirmed receiver accounting"
        )

        receiver_confirmed_tx = receiver.gettransaction(
            spend_txid,
        )

        assert_equal(
            receiver_confirmed_tx["amount"],
            payment_amount,
        )

        assert_equal(
            receiver_confirmed_tx["confirmations"],
            1,
        )

        assert_equal(
            receiver_confirmed_tx["blockhash"],
            confirm_block_hash,
        )

        assert_equal(
            receiver.getbalance(),
            payment_amount,
        )

        receiver_confirmed_entry = self.find_wallet_tx(
            receiver,
            spend_txid,
            "receive",
        )

        assert_equal(
            receiver_confirmed_entry["amount"],
            payment_amount,
        )

        assert_equal(
            receiver_confirmed_entry["confirmations"],
            1,
        )

        self.log.info(
            "Checking external input is fully spent"
        )

        remaining_external_utxos = [
            utxo
            for utxo in external_wallet.listunspent()
            if (
                utxo["txid"] == external_utxo["txid"]
                and utxo["vout"] == external_utxo["vout"]
            )
        ]

        assert_equal(
            remaining_external_utxos,
            [],
        )

        assert_equal(
            external_wallet.getbalance(),
            Decimal("0E-8"),
        )

        assert_equal(
            spending_wallet.getbalance(),
            expected_spending_balance,
        )

        self.log.info(
            "Checking final Andaluzcoin wallet identities"
        )

        self.assert_wallet_identity(
            miner,
            miner_wallet_name,
        )

        self.assert_wallet_identity(
            source,
            source_wallet_name,
        )

        self.assert_wallet_identity(
            spending_wallet,
            spending_wallet_name,
        )

        self.assert_wallet_identity(
            external_wallet,
            external_wallet_name,
        )

        self.assert_wallet_identity(
            receiver,
            receiver_wallet_name,
        )

        self.log.info(
            "Checking final Andaluzcoin runtime identity"
        )

        self.assert_andaluz_runtime_identity(
            self.nodes[0],
        )

        self.assert_andaluz_runtime_identity(
            self.nodes[1],
        )


if __name__ == "__main__":
    AndaluzWalletSendSolvingDataIdentityTest(__file__).main()
