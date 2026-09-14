#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet send replaceable identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletSendReplaceableIdentityTest(BitcoinTestFramework):
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
            if entry.get("txid") == txid
            and entry.get("category") == category
        ]

        assert_equal(len(matches), 1)
        return matches[0]

    def run_test(self):
        miner_wallet_name = "andaluz_send_replaceable_miner"
        sender_wallet_name = "andaluz_send_replaceable_sender"
        receiver_wallet_name = "andaluz_send_replaceable_receiver"

        coinbase_amount = Decimal("50.00000000")
        initial_sender_balance = coinbase_amount * 2

        fee_rate_sat_vb = 10

        send_cases = [
            {
                "name": "replaceable",
                "amount": Decimal("1.00000000"),
                "replaceable": True,
                "expected_bip125": "yes",
            },
            {
                "name": "nonreplaceable",
                "amount": Decimal("2.00000000"),
                "replaceable": False,
                "expected_bip125": "no",
            },
        ]

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

        self.log.info("Mining two spendable Andaluzcoin UTXOs to sender")
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

        assert_equal(
            sender.getbalances()["mine"]["trusted"],
            initial_sender_balance,
        )
        assert_equal(
            receiver.getbalances()["mine"]["trusted"],
            Decimal("0E-8"),
        )

        expected_sender_balance = initial_sender_balance
        expected_receiver_balance = Decimal("0E-8")

        for case in send_cases:
            case_name = case["name"]
            amount = case["amount"]
            replaceable = case["replaceable"]
            expected_bip125 = case["expected_bip125"]

            self.log.info(
                f"Creating {case_name} Andaluzcoin transaction with send RPC"
            )

            receiver_address = receiver.getnewaddress(
                f"andaluz-send-{case_name}",
                "bech32",
            )
            self.assert_valid_wallet_address(
                receiver,
                receiver_address,
            )

            send_result = sender.send(
                outputs={
                    receiver_address: amount,
                },
                fee_rate=fee_rate_sat_vb,
                options={
                    "replaceable": replaceable,
                },
            )

            assert_equal(send_result["complete"], True)
            assert "txid" in send_result, send_result

            txid = send_result["txid"]
            assert_equal(len(txid), 64)

            self.log.info(
                f"Checking {case_name} transaction entered mempool"
            )

            assert txid in self.nodes[0].getrawmempool(), (
                txid,
                self.nodes[0].getrawmempool(),
            )

            self.nodes[0].syncwithvalidationinterfacequeue()

            self.log.info(
                f"Checking {case_name} BIP125 identity"
            )

            sender_pending_tx = sender.gettransaction(
                txid=txid,
                verbose=True,
            )

            assert_equal(
                sender_pending_tx["amount"],
                -amount,
            )
            assert sender_pending_tx["fee"] < Decimal("0"), sender_pending_tx
            assert_equal(
                sender_pending_tx["confirmations"],
                0,
            )
            assert_equal(
                sender_pending_tx["bip125-replaceable"],
                expected_bip125,
            )

            fee = -sender_pending_tx["fee"]
            assert fee > Decimal("0"), fee

            decoded_tx = sender_pending_tx["decoded"]

            recipient_outputs = [
                output
                for output in decoded_tx["vout"]
                if output["scriptPubKey"].get("address")
                == receiver_address
            ]

            assert_equal(len(recipient_outputs), 1)
            assert_equal(
                recipient_outputs[0]["value"],
                amount,
            )

            self.log.info(
                f"Checking sender history for {case_name} transaction"
            )

            sender_list_entry = self.find_wallet_tx(
                sender,
                txid,
                "send",
            )

            assert_equal(
                sender_list_entry["amount"],
                -amount,
            )
            assert_equal(
                sender_list_entry["confirmations"],
                0,
            )

            self.log.info(
                f"Checking receiver pending accounting for {case_name} transaction"
            )

            self.wait_until(
                lambda: receiver.getbalances()["mine"]["untrusted_pending"]
                == amount,
                timeout=60,
            )

            receiver_pending_tx = receiver.gettransaction(txid)

            assert_equal(
                receiver_pending_tx["amount"],
                amount,
            )
            assert_equal(
                receiver_pending_tx["confirmations"],
                0,
            )

            receiver_list_entry = self.find_wallet_tx(
                receiver,
                txid,
                "receive",
            )

            assert_equal(
                receiver_list_entry["amount"],
                amount,
            )
            assert_equal(
                receiver_list_entry["confirmations"],
                0,
            )

            self.log.info(
                f"Confirming {case_name} Andaluzcoin transaction"
            )

            confirm_block_hash = self.nodes[0].generatetoaddress(
                1,
                miner_mining_address,
                called_by_framework=True,
            )[0]

            assert_equal(
                self.nodes[0].getbestblockhash(),
                confirm_block_hash,
            )
            assert_equal(
                self.nodes[0].getmempoolinfo()["size"],
                0,
            )

            self.nodes[0].syncwithvalidationinterfacequeue()

            expected_sender_balance -= amount + fee
            expected_receiver_balance += amount

            self.wait_until(
                lambda: sender.getbalances()["mine"]["trusted"]
                == expected_sender_balance,
                timeout=60,
            )

            self.wait_until(
                lambda: receiver.getbalances()["mine"]["trusted"]
                == expected_receiver_balance,
                timeout=60,
            )

            self.log.info(
                f"Checking confirmed {case_name} sender accounting"
            )

            sender_confirmed_tx = sender.gettransaction(txid)

            assert_equal(
                sender_confirmed_tx["amount"],
                -amount,
            )
            assert_equal(
                sender_confirmed_tx["fee"],
                -fee,
            )
            assert_equal(
                sender_confirmed_tx["confirmations"],
                1,
            )
            assert_equal(
                sender_confirmed_tx["blockhash"],
                confirm_block_hash,
            )

            assert_equal(
                sender.getbalance(),
                expected_sender_balance,
            )

            self.log.info(
                f"Checking confirmed {case_name} receiver accounting"
            )

            receiver_confirmed_tx = receiver.gettransaction(txid)

            assert_equal(
                receiver_confirmed_tx["amount"],
                amount,
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
                expected_receiver_balance,
            )

        self.log.info("Checking both replaceability cases affected balances correctly")

        total_sent = sum(
            (case["amount"] for case in send_cases),
            Decimal("0E-8"),
        )

        assert_equal(
            receiver.getbalance(),
            total_sent,
        )

        assert sender.getbalance() < (
            initial_sender_balance - total_sent
        ), sender.getbalance()

        self.log.info("Checking final Andaluzcoin wallet identities")
        self.assert_wallet_identity(miner, miner_wallet_name)
        self.assert_wallet_identity(sender, sender_wallet_name)
        self.assert_wallet_identity(receiver, receiver_wallet_name)

        self.log.info("Checking final Andaluzcoin runtime identity")
        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletSendReplaceableIdentityTest(__file__).main()
