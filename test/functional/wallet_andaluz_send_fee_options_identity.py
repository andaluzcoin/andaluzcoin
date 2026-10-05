#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet send fee-options identity."""

from decimal import Decimal

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import (
    assert_equal,
    assert_fee_amount,
    assert_raises_rpc_error,
)


class AndaluzWalletSendFeeOptionsIdentityTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True
        self.chain = "regtest"
        self.wallet_names = []
        self.extra_args = [[
            "-dnsseed=0",
            "-fixedseeds=0",
            "-connect=0",
            "-fallbackfee=0.00010000",
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

    def assert_wallet_identity(self, wallet, wallet_name):
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

    def assert_nonbroadcast_result(self, result):
        assert_equal(
            result["complete"],
            True,
        )

        assert "txid" in result, result
        assert "hex" in result, result
        assert "psbt" in result, result

        assert_equal(
            len(result["txid"]),
            64,
        )

    def run_test(self):
        miner_wallet_name = "andaluz_send_fee_options_miner"
        sender_wallet_name = "andaluz_send_fee_options_sender"
        receiver_wallet_name = "andaluz_send_fee_options_receiver"

        send_amount = Decimal("1.00000000")

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
            wallet_name=receiver_wallet_name,
        )

        miner = self.nodes[0].get_wallet_rpc(
            miner_wallet_name,
        )

        sender = self.nodes[0].get_wallet_rpc(
            sender_wallet_name,
        )

        receiver = self.nodes[0].get_wallet_rpc(
            receiver_wallet_name,
        )

        self.assert_wallet_identity(
            miner,
            miner_wallet_name,
        )

        self.assert_wallet_identity(
            sender,
            sender_wallet_name,
        )

        self.assert_wallet_identity(
            receiver,
            receiver_wallet_name,
        )

        self.log.info(
            "Mining spendable ALUZ to fee-options sender"
        )

        sender_mining_address = sender.getnewaddress(
            "",
            "bech32",
        )

        miner_mining_address = miner.getnewaddress(
            "",
            "bech32",
        )

        self.nodes[0].generatetoaddress(
            1,
            sender_mining_address,
            called_by_framework=True,
        )

        self.nodes[0].generatetoaddress(
            100,
            miner_mining_address,
            called_by_framework=True,
        )

        self.nodes[0].syncwithvalidationinterfacequeue()

        initial_sender_balance = sender.getbalance()

        assert_equal(
            initial_sender_balance,
            Decimal("50.00000000"),
        )

        destination = receiver.getnewaddress(
            "andaluz-fee-options",
            "bech32",
        )

        outputs = {
            destination: send_amount,
        }

        self.log.info(
            "Checking conf_target and estimate_mode as RPC arguments"
        )

        argument_estimate = sender.send(
            outputs=outputs,
            conf_target=1,
            estimate_mode="economical",
            options={
                "add_to_wallet": False,
            },
        )

        self.assert_nonbroadcast_result(
            argument_estimate,
        )

        self.log.info(
            "Checking conf_target and estimate_mode in options object"
        )

        option_estimate = sender.send(
            outputs=outputs,
            options={
                "conf_target": 1,
                "estimate_mode": "economical",
                "add_to_wallet": False,
            },
        )

        self.assert_nonbroadcast_result(
            option_estimate,
        )

        argument_estimate_fee = self.nodes[0].decodepsbt(
            argument_estimate["psbt"]
        )["fee"]

        option_estimate_fee = self.nodes[0].decodepsbt(
            option_estimate["psbt"]
        )["fee"]

        assert_equal(
            argument_estimate_fee,
            option_estimate_fee,
        )

        self.log.info(
            "Rejecting duplicate conf_target / estimate_mode specification"
        )

        for option_mode in [
            "unset",
            "economical",
            "conservative",
        ]:
            assert_raises_rpc_error(
                -8,
                (
                    "Pass conf_target and estimate_mode either as "
                    "arguments or in the options object, but not both"
                ),
                sender.send,
                outputs=outputs,
                conf_target=1,
                estimate_mode="economical",
                options={
                    "conf_target": 1,
                    "estimate_mode": option_mode,
                    "add_to_wallet": False,
                },
            )

        self.log.info(
            "Checking explicit fee_rate as RPC argument"
        )

        argument_fee_rate = sender.send(
            outputs=outputs,
            fee_rate="1",
            options={
                "add_to_wallet": False,
            },
        )

        self.assert_nonbroadcast_result(
            argument_fee_rate,
        )

        self.log.info(
            "Checking explicit fee_rate in options object"
        )

        option_fee_rate = sender.send(
            outputs=outputs,
            options={
                "fee_rate": "1",
                "add_to_wallet": False,
            },
        )

        self.assert_nonbroadcast_result(
            option_fee_rate,
        )

        argument_fee = self.nodes[0].decodepsbt(
            argument_fee_rate["psbt"]
        )["fee"]

        option_fee = self.nodes[0].decodepsbt(
            option_fee_rate["psbt"]
        )["fee"]

        assert_equal(
            argument_fee,
            option_fee,
        )

        self.log.info(
            "Checking explicit 7 sat/vB fee rate"
        )

        seven_sat_result = sender.send(
            outputs=outputs,
            options={
                "fee_rate": 7,
                "add_to_wallet": False,
            },
        )

        self.assert_nonbroadcast_result(
            seven_sat_result,
        )

        seven_sat_fee = self.nodes[0].decodepsbt(
            seven_sat_result["psbt"]
        )["fee"]

        seven_sat_vsize = self.nodes[0].decoderawtransaction(
            seven_sat_result["hex"]
        )["vsize"]

        assert_fee_amount(
            seven_sat_fee,
            seven_sat_vsize,
            Decimal("0.00007"),
        )

        self.log.info(
            "Checking estimate_mode unset with explicit fee rate"
        )

        unset_result = sender.send(
            outputs=outputs,
            options={
                "fee_rate": 2,
                "estimate_mode": "unset",
                "add_to_wallet": False,
            },
        )

        self.assert_nonbroadcast_result(
            unset_result,
        )

        unset_fee = self.nodes[0].decodepsbt(
            unset_result["psbt"]
        )["fee"]

        unset_vsize = self.nodes[0].decoderawtransaction(
            unset_result["hex"]
        )["vsize"]

        assert_fee_amount(
            unset_fee,
            unset_vsize,
            Decimal("0.00002"),
        )

        self.log.info(
            "Rejecting duplicate fee_rate specification"
        )

        assert_raises_rpc_error(
            -8,
            (
                "Pass the fee_rate either as an argument, "
                "or in the options object, but not both"
            ),
            sender.send,
            outputs=outputs,
            fee_rate=1,
            options={
                "fee_rate": 1,
                "add_to_wallet": False,
            },
        )

        self.log.info(
            "Rejecting deprecated feeRate option"
        )

        assert_raises_rpc_error(
            -8,
            "Use fee_rate (sat/vB) instead of feeRate",
            sender.send,
            outputs,
            6,
            "conservative",
            1,
            {
                "feeRate": 0.01,
            },
        )

        self.log.info(
            "Rejecting unsupported totalFee option"
        )

        assert_raises_rpc_error(
            -3,
            "Unexpected key totalFee",
            sender.send,
            outputs,
            6,
            "conservative",
            1,
            {
                "totalFee": 0.01,
            },
        )

        self.log.info(
            "Rejecting invalid conf_target values"
        )

        for invalid_target in [
            -1,
            0,
            1009,
        ]:
            assert_raises_rpc_error(
                -8,
                "Invalid conf_target, must be between 1 and 1008",
                sender.send,
                outputs=outputs,
                options={
                    "conf_target": invalid_target,
                    "estimate_mode": "economical",
                    "add_to_wallet": False,
                },
            )

        self.log.info(
            "Rejecting invalid estimate_mode values"
        )

        invalid_estimate_mode_message = (
            'Invalid estimate_mode parameter, must be one of: '
            '"unset", "economical", "conservative"'
        )

        for invalid_mode in [
            "",
            "foo",
            "sat/b",
            "btc/kb",
        ]:
            assert_raises_rpc_error(
                -8,
                invalid_estimate_mode_message,
                sender.send,
                outputs=outputs,
                options={
                    "estimate_mode": invalid_mode,
                    "add_to_wallet": False,
                },
            )

        self.log.info(
            "Rejecting incorrect conf_target JSON type"
        )

        assert_raises_rpc_error(
            -3,
            (
                "JSON value of type bool for field conf_target "
                "is not of expected type number"
            ),
            sender.send,
            outputs=outputs,
            options={
                "conf_target": True,
                "estimate_mode": "economical",
                "add_to_wallet": False,
            },
        )

        self.log.info(
            "Rejecting fee rate below minimum"
        )

        minimum_fee_message = (
            "Fee rate (0.999 sat/vB) is lower than "
            "the minimum fee rate setting (1.000 sat/vB)"
        )

        assert_raises_rpc_error(
            -4,
            minimum_fee_message,
            sender.send,
            outputs=outputs,
            options={
                "fee_rate": Decimal("0.999"),
                "add_to_wallet": False,
            },
        )

        assert_raises_rpc_error(
            -4,
            minimum_fee_message,
            sender.send,
            outputs=outputs,
            fee_rate=Decimal("0.999"),
            options={
                "add_to_wallet": False,
            },
        )

        self.log.info(
            "Rejecting zero fee rate"
        )

        zero_fee_message = (
            "Fee rate (0.000 sat/vB) is lower than "
            "the minimum fee rate setting (1.000 sat/vB)"
        )

        assert_raises_rpc_error(
            -4,
            zero_fee_message,
            sender.send,
            outputs=outputs,
            options={
                "fee_rate": 0,
                "add_to_wallet": False,
            },
        )

        self.log.info(
            "Rejecting excessive fee-rate precision"
        )

        assert_raises_rpc_error(
            -3,
            "Invalid amount",
            sender.send,
            outputs=outputs,
            options={
                "fee_rate": "1.111111111",
                "add_to_wallet": False,
            },
        )

        self.log.info(
            "Rejecting negative fee rate"
        )

        assert_raises_rpc_error(
            -3,
            "Amount out of range",
            sender.send,
            outputs=outputs,
            options={
                "fee_rate": -1,
                "add_to_wallet": False,
            },
        )

        self.log.info(
            "Rejecting invalid fee-rate JSON type"
        )

        assert_raises_rpc_error(
            -3,
            "Amount is not a number or string",
            sender.send,
            outputs=outputs,
            options={
                "fee_rate": True,
                "add_to_wallet": False,
            },
        )

        self.log.info(
            "Checking successful and rejected nonbroadcast sends changed no state"
        )

        assert_equal(
            sender.getbalance(),
            initial_sender_balance,
        )

        assert_equal(
            self.nodes[0].getmempoolinfo()["size"],
            0,
        )

        assert_equal(
            sender.listlockunspent(),
            [],
        )

        assert_equal(
            receiver.getbalances()["mine"]["trusted"],
            Decimal("0E-8"),
        )

        assert_equal(
            receiver.getbalances()["mine"]["untrusted_pending"],
            Decimal("0E-8"),
        )

        self.log.info(
            "Checking final Andaluzcoin wallet identities"
        )

        self.assert_wallet_identity(
            miner,
            miner_wallet_name,
        )

        self.assert_wallet_identity(
            sender,
            sender_wallet_name,
        )

        self.assert_wallet_identity(
            receiver,
            receiver_wallet_name,
        )

        self.log.info(
            "Checking final Andaluzcoin runtime identity"
        )

        self.assert_andaluz_runtime_identity()


if __name__ == "__main__":
    AndaluzWalletSendFeeOptionsIdentityTest(__file__).main()
