#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet send data-output identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal, assert_raises_rpc_error


class AndaluzWalletSendDataOutputIdentityTest(BitcoinTestFramework):
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
        assert_equal(
            self.nodes[0].getblockchaininfo()["chain"],
            "regtest",
        )

        subversion = self.nodes[0].getnetworkinfo()["subversion"]

        assert subversion.startswith("/AndaluzcoinCore:"), subversion
        assert "Satoshi" not in subversion, subversion
        assert "Bitcoin" not in subversion, subversion

    def assert_wallet_identity(
        self,
        wallet,
        wallet_name,
        private_keys_enabled,
    ):
        wallet_info = wallet.getwalletinfo()

        assert_equal(
            wallet_info["walletname"],
            wallet_name,
        )

        assert_equal(
            wallet_info["private_keys_enabled"],
            private_keys_enabled,
        )

        assert_equal(
            wallet_info["descriptors"],
            True,
        )

        assert_equal(
            wallet_info["format"],
            "sqlite",
        )

    def assert_valid_wallet_address(
        self,
        wallet,
        address,
    ):
        assert_equal(
            self.nodes[0].validateaddress(address)["isvalid"],
            True,
        )

        address_info = wallet.getaddressinfo(address)

        assert_equal(
            address_info["ismine"],
            True,
        )

        assert_equal(
            address_info["solvable"],
            True,
        )

    def find_data_output(self, decoded_tx):
        data_outputs = [
            output
            for output in decoded_tx["vout"]
            if output["scriptPubKey"].get("type") == "nulldata"
        ]

        assert_equal(
            len(data_outputs),
            1,
        )

        return data_outputs[0]

    def public_wpkh_descriptor_requests(
        self,
        signer,
    ):
        descriptors = signer.listdescriptors(
            False,
        )["descriptors"]

        requests = []

        for descriptor in descriptors:
            if not descriptor.get("active", False):
                continue

            if not descriptor["desc"].startswith("wpkh("):
                continue

            request = {
                "desc": descriptor["desc"],
                "timestamp": "now",
                "active": True,
                "internal": descriptor.get(
                    "internal",
                    False,
                ),
            }

            if "range" in descriptor:
                request["range"] = descriptor["range"]

            requests.append(request)

        assert_equal(
            len(requests),
            2,
        )

        assert_equal(
            {
                request["internal"]
                for request in requests
            },
            {
                False,
                True,
            },
        )

        return requests

    def run_test(self):
        miner_wallet_name = "andaluz_send_data_miner"
        sender_wallet_name = "andaluz_send_data_sender"
        signer_wallet_name = "andaluz_send_data_signer"
        watch_wallet_name = "andaluz_send_data_watch"

        coinbase_amount = Decimal("50.00000000")
        watch_funding_amount = Decimal("10.00000000")
        fee_rate_sat_vb = Decimal("10")

        valid_data_hex = "23"
        expected_data_script_hex = "6a0123"
        expected_data_asm = "OP_RETURN 35"

        self.log.info(
            "Checking initial Andaluzcoin runtime identity"
        )

        self.assert_andaluz_runtime_identity()

        self.log.info(
            "Creating Andaluzcoin wallets"
        )

        self.nodes[0].createwallet(
            wallet_name=miner_wallet_name,
        )

        self.nodes[0].createwallet(
            wallet_name=sender_wallet_name,
        )

        self.nodes[0].createwallet(
            wallet_name=signer_wallet_name,
        )

        self.nodes[0].createwallet(
            wallet_name=watch_wallet_name,
            disable_private_keys=True,
        )

        miner = self.nodes[0].get_wallet_rpc(
            miner_wallet_name,
        )

        sender = self.nodes[0].get_wallet_rpc(
            sender_wallet_name,
        )

        signer = self.nodes[0].get_wallet_rpc(
            signer_wallet_name,
        )

        watch = self.nodes[0].get_wallet_rpc(
            watch_wallet_name,
        )

        self.assert_wallet_identity(
            miner,
            miner_wallet_name,
            True,
        )

        self.assert_wallet_identity(
            sender,
            sender_wallet_name,
            True,
        )

        self.assert_wallet_identity(
            signer,
            signer_wallet_name,
            True,
        )

        self.assert_wallet_identity(
            watch,
            watch_wallet_name,
            False,
        )

        self.log.info(
            "Importing signer public descriptors into watch-only wallet"
        )

        descriptor_requests = (
            self.public_wpkh_descriptor_requests(
                signer,
            )
        )

        import_results = watch.importdescriptors(
            descriptor_requests,
        )

        assert_equal(
            len(import_results),
            2,
        )

        for result in import_results:
            assert_equal(
                result["success"],
                True,
            )

        self.log.info(
            "Mining spendable ALUZ to sender"
        )

        sender_mining_address = sender.getnewaddress(
            "",
            "bech32",
        )

        miner_mining_address = miner.getnewaddress(
            "",
            "bech32",
        )

        self.assert_valid_wallet_address(
            sender,
            sender_mining_address,
        )

        self.assert_valid_wallet_address(
            miner,
            miner_mining_address,
        )

        sender_blocks = self.nodes[0].generatetoaddress(
            1,
            sender_mining_address,
            called_by_framework=True,
        )

        assert_equal(
            len(sender_blocks),
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

        self.nodes[0].syncwithvalidationinterfacequeue()

        assert_equal(
            sender.getbalances()["mine"]["trusted"],
            coinbase_amount,
        )

        self.log.info(
            "Funding signer/watch-only descriptor wallet"
        )

        signer_address = signer.getnewaddress(
            "andaluz-data-watch-funding",
            "bech32",
        )

        self.assert_valid_wallet_address(
            signer,
            signer_address,
        )

        watch_address_info = watch.getaddressinfo(
            signer_address,
        )

        assert_equal(
            watch_address_info["ismine"],
            True,
        )

        assert_equal(
            watch_address_info["solvable"],
            True,
        )

        funding_txid = sender.sendtoaddress(
            signer_address,
            watch_funding_amount,
        )

        assert_equal(
            len(funding_txid),
            64,
        )

        assert funding_txid in self.nodes[0].getrawmempool(), (
            self.nodes[0].getrawmempool()
        )

        funding_block_hash = self.nodes[0].generatetoaddress(
            1,
            miner_mining_address,
            called_by_framework=True,
        )[0]

        assert_equal(
            self.nodes[0].getbestblockhash(),
            funding_block_hash,
        )

        assert_equal(
            self.nodes[0].getmempoolinfo()["size"],
            0,
        )

        self.nodes[0].syncwithvalidationinterfacequeue()

        assert_equal(
            signer.getbalances()["mine"]["trusted"],
            watch_funding_amount,
        )

        assert_equal(
            watch.getbalances()["mine"]["trusted"],
            watch_funding_amount,
        )

        self.log.info(
            "Checking non-hexadecimal data is rejected"
        )

        sender_balance_before_invalid = sender.getbalance()
        mempool_before_invalid = set(
            self.nodes[0].getrawmempool()
        )

        assert_raises_rpc_error(
            -8,
            "Data must be hexadecimal string (not 'Hello World')",
            sender.send,
            outputs={
                "data": "Hello World",
            },
            fee_rate=fee_rate_sat_vb,
        )

        assert_equal(
            set(self.nodes[0].getrawmempool()),
            mempool_before_invalid,
        )

        assert_equal(
            sender.getbalance(),
            sender_balance_before_invalid,
        )

        self.log.info(
            "Creating broadcast OP_RETURN transaction with modern send"
        )

        sender_balance_before_data = sender.getbalance()

        data_result = sender.send(
            outputs={
                "data": valid_data_hex,
            },
            fee_rate=fee_rate_sat_vb,
        )

        assert_equal(
            data_result["complete"],
            True,
        )

        assert "txid" in data_result, data_result

        data_txid = data_result["txid"]

        assert_equal(
            len(data_txid),
            64,
        )

        assert data_txid in self.nodes[0].getrawmempool(), (
            self.nodes[0].getrawmempool()
        )

        self.nodes[0].syncwithvalidationinterfacequeue()

        self.log.info(
            "Checking OP_RETURN output structure"
        )

        sender_pending_tx = sender.gettransaction(
            txid=data_txid,
            verbose=True,
        )

        assert_equal(
            sender_pending_tx["confirmations"],
            0,
        )

        assert_equal(
            sender_pending_tx["amount"],
            Decimal("0E-8"),
        )

        assert sender_pending_tx["fee"] < Decimal("0"), (
            sender_pending_tx
        )

        data_fee = -sender_pending_tx["fee"]

        assert data_fee > Decimal("0"), data_fee

        decoded_data_tx = sender_pending_tx["decoded"]

        data_output = self.find_data_output(
            decoded_data_tx,
        )

        assert_equal(
            data_output["value"],
            Decimal("0E-8"),
        )

        assert_equal(
            data_output["scriptPubKey"]["hex"],
            expected_data_script_hex,
        )

        assert_equal(
            data_output["scriptPubKey"]["asm"],
            expected_data_asm,
        )

        assert_equal(
            sender.getbalance(),
            sender_balance_before_data - data_fee,
        )

        self.log.info(
            "Confirming private-key OP_RETURN transaction"
        )

        direct_confirm_block = self.nodes[0].generatetoaddress(
            1,
            miner_mining_address,
            called_by_framework=True,
        )[0]

        assert_equal(
            self.nodes[0].getbestblockhash(),
            direct_confirm_block,
        )

        assert_equal(
            self.nodes[0].getmempoolinfo()["size"],
            0,
        )

        self.nodes[0].syncwithvalidationinterfacequeue()

        sender_confirmed_tx = sender.gettransaction(
            data_txid,
        )

        assert_equal(
            sender_confirmed_tx["confirmations"],
            1,
        )

        assert_equal(
            sender_confirmed_tx["blockhash"],
            direct_confirm_block,
        )

        assert_equal(
            sender.getbalance(),
            sender_balance_before_data - data_fee,
        )

        self.log.info(
            "Creating OP_RETURN PSBT from watch-only wallet"
        )

        watch_balance_before = (
            watch.getbalances()["mine"]["trusted"]
        )

        assert_equal(
            watch_balance_before,
            watch_funding_amount,
        )

        watch_data_result = watch.send(
            outputs={
                "data": valid_data_hex,
            },
            fee_rate=fee_rate_sat_vb,
        )

        assert_equal(
            watch_data_result["complete"],
            False,
        )

        assert "psbt" in watch_data_result, watch_data_result
        assert "txid" not in watch_data_result, watch_data_result

        assert_equal(
            self.nodes[0].getmempoolinfo()["size"],
            0,
        )

        assert_equal(
            watch.getbalances()["mine"]["trusted"],
            watch_balance_before,
        )

        self.log.info(
            "Signing watch-only OP_RETURN PSBT with private-key wallet"
        )

        signed_result = signer.walletprocesspsbt(
            watch_data_result["psbt"],
        )

        assert_equal(
            signed_result["complete"],
            True,
        )

        assert "hex" in signed_result, signed_result
        assert "psbt" in signed_result, signed_result

        raw_hex = signed_result["hex"]

        decoded_watch_tx = self.nodes[0].decoderawtransaction(
            raw_hex,
        )

        watch_data_txid = decoded_watch_tx["txid"]

        assert_equal(
            len(watch_data_txid),
            64,
        )

        watch_data_output = self.find_data_output(
            decoded_watch_tx,
        )

        assert_equal(
            watch_data_output["value"],
            Decimal("0E-8"),
        )

        assert_equal(
            watch_data_output["scriptPubKey"]["hex"],
            expected_data_script_hex,
        )

        assert_equal(
            watch_data_output["scriptPubKey"]["asm"],
            expected_data_asm,
        )

        self.log.info(
            "Checking signed watch-only transaction is mempool-valid"
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
            watch_data_txid,
        )

        assert_equal(
            accept_result[0]["allowed"],
            True,
        )

        watch_data_fee = accept_result[0]["fees"]["base"]

        assert watch_data_fee > Decimal("0"), watch_data_fee

        assert_equal(
            self.nodes[0].getmempoolinfo()["size"],
            0,
        )

        self.log.info(
            "Broadcasting watch-only OP_RETURN transaction"
        )

        broadcast_txid = self.nodes[0].sendrawtransaction(
            raw_hex,
        )

        assert_equal(
            broadcast_txid,
            watch_data_txid,
        )

        assert watch_data_txid in self.nodes[0].getrawmempool(), (
            self.nodes[0].getrawmempool()
        )

        self.nodes[0].syncwithvalidationinterfacequeue()

        self.log.info(
            "Confirming watch-only OP_RETURN transaction"
        )

        watch_confirm_block = self.nodes[0].generatetoaddress(
            1,
            miner_mining_address,
            called_by_framework=True,
        )[0]

        assert_equal(
            self.nodes[0].getbestblockhash(),
            watch_confirm_block,
        )

        assert_equal(
            self.nodes[0].getmempoolinfo()["size"],
            0,
        )

        self.nodes[0].syncwithvalidationinterfacequeue()

        expected_watch_balance = (
            watch_funding_amount
            - watch_data_fee
        )

        self.wait_until(
            lambda:
                watch.getbalances()["mine"]["trusted"]
                == expected_watch_balance,
            timeout=60,
        )

        self.wait_until(
            lambda:
                signer.getbalances()["mine"]["trusted"]
                == expected_watch_balance,
            timeout=60,
        )

        assert_equal(
            watch.getbalance(),
            expected_watch_balance,
        )

        assert_equal(
            signer.getbalance(),
            expected_watch_balance,
        )

        self.log.info(
            "Checking final Andaluzcoin wallet identities"
        )

        self.assert_wallet_identity(
            miner,
            miner_wallet_name,
            True,
        )

        self.assert_wallet_identity(
            sender,
            sender_wallet_name,
            True,
        )

        self.assert_wallet_identity(
            signer,
            signer_wallet_name,
            True,
        )

        self.assert_wallet_identity(
            watch,
            watch_wallet_name,
            False,
        )

        self.log.info(
            "Checking final Andaluzcoin runtime identity"
        )

        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletSendDataOutputIdentityTest(__file__).main()
