#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin wallet address identity."""

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class AndaluzWalletIdentityTest(BitcoinTestFramework):
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

    def run_test(self):
        wallet_name = "andaluz_identity"

        self.log.info("Creating wallet")
        create_result = self.nodes[0].createwallet(wallet_name=wallet_name)
        assert_equal(create_result["name"], wallet_name)

        wallet = self.nodes[0].get_wallet_rpc(wallet_name)

        self.log.info("Checking Andaluzcoin wallet RPC startup identity")
        wallet_info = wallet.getwalletinfo()
        assert_equal(wallet_info["walletname"], wallet_name)
        assert_equal(wallet_info["private_keys_enabled"], True)
        assert_equal(wallet_info["descriptors"], True)
        assert_equal(wallet_info["format"], "sqlite")

        self.log.info("Checking Andaluzcoin bech32 address prefix")
        bech32_addr = wallet.getnewaddress("", "bech32")
        assert bech32_addr.startswith("aluz1"), bech32_addr
        assert not bech32_addr.startswith("bc1"), bech32_addr

        self.log.info("Checking Andaluzcoin legacy P2PKH address prefix")
        legacy_addr = wallet.getnewaddress("", "legacy")
        assert legacy_addr.startswith("P"), legacy_addr
        assert not legacy_addr.startswith("1"), legacy_addr

        self.log.info("Checking Andaluzcoin P2SH address prefix")
        p2sh_addr = wallet.getnewaddress("", "p2sh-segwit")
        assert p2sh_addr.startswith("p"), p2sh_addr
        assert not p2sh_addr.startswith("3"), p2sh_addr

        self.log.info("Checking generated addresses validate")
        for addr in [bech32_addr, legacy_addr, p2sh_addr]:
            info = self.nodes[0].validateaddress(addr)
            assert_equal(info["isvalid"], True)


if __name__ == "__main__":
    AndaluzWalletIdentityTest(__file__).main()
