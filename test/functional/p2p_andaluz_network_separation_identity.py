#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Verify Andaluzcoin mainnet P2P network separation identity."""

from test_framework.messages import (
    MAGIC_BYTES,
    msg_ping,
)
from test_framework.p2p import P2PDataStore
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


ANDALUZ_MAINNET_MAGIC = b"\xb6\xa9\x64\x58"
BITCOIN_MAINNET_MAGIC = b"\xf9\xbe\xb4\xd9"
INVALID_MAGIC = b"\xff\xff\xff\xff"

ANDALUZ_GENESIS_HASH = (
    "000000f7dca7651a1397fd0bc99b2a456dbb2d23470834b6290aadec4b46d15c"
)


class AndaluzMainnetP2PNetworkSeparationIdentityTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True
        self.chain = ""
        self.extra_args = [[
            "-dnsseed=0",
            "-fixedseeds=0",
            "-connect=0",
            "-listen=1",
            "-v2transport=0",
        ]]

    def assert_mainnet_identity(self):
        node = self.nodes[0]

        blockchain_info = node.getblockchaininfo()

        assert_equal(
            blockchain_info["chain"],
            "main",
        )

        assert_equal(
            blockchain_info["blocks"],
            0,
        )

        assert_equal(
            blockchain_info["headers"],
            0,
        )

        assert_equal(
            blockchain_info["bestblockhash"],
            ANDALUZ_GENESIS_HASH,
        )

        assert_equal(
            node.getblockhash(0),
            ANDALUZ_GENESIS_HASH,
        )

        subversion = node.getnetworkinfo()["subversion"]

        assert subversion.startswith(
            "/AndaluzcoinCore:"
        ), subversion

        assert "Satoshi" not in subversion, subversion
        assert "Bitcoin" not in subversion, subversion

    def connect_framework_peer(self):
        node = self.nodes[0]

        peer = node.add_p2p_connection(
            P2PDataStore(),
        )

        assert_equal(
            peer.magic_bytes,
            ANDALUZ_MAINNET_MAGIC,
        )

        self.wait_until(
            lambda: node.getconnectioncount() == 1,
            timeout=30,
        )

        assert_equal(
            len(node.getpeerinfo()),
            1,
        )

        return peer

    def send_wrong_magic_and_expect_disconnect(
        self,
        peer,
        wrong_magic,
        expected_log,
        nonce,
    ):
        node = self.nodes[0]

        valid_message = peer.build_message(
            msg_ping(nonce=nonce)
        )

        assert_equal(
            valid_message[:4],
            ANDALUZ_MAINNET_MAGIC,
        )

        wrong_message = (
            wrong_magic
            + valid_message[4:]
        )

        with node.assert_debug_log([
            expected_log,
        ]):
            peer.send_raw_message(
                wrong_message,
            )

            peer.wait_for_disconnect(
                timeout=5,
            )

        self.wait_until(
            lambda: node.getconnectioncount() == 0,
            timeout=30,
        )

        node.disconnect_p2ps()

    def run_test(self):
        node = self.nodes[0]

        self.log.info(
            "Checking Andaluzcoin functional framework mainnet magic"
        )

        assert_equal(
            MAGIC_BYTES[""],
            ANDALUZ_MAINNET_MAGIC,
        )

        assert_equal(
            MAGIC_BYTES["mainnet"],
            ANDALUZ_MAINNET_MAGIC,
        )

        assert_equal(
            MAGIC_BYTES[""],
            MAGIC_BYTES["mainnet"],
        )

        assert (
            MAGIC_BYTES["mainnet"]
            != BITCOIN_MAINNET_MAGIC
        )

        self.log.info(
            "Checking initial Andaluzcoin mainnet identity"
        )

        self.assert_mainnet_identity()

        self.log.info(
            "Connecting functional P2P peer using Andaluzcoin mainnet magic"
        )

        peer = self.connect_framework_peer()

        self.assert_mainnet_identity()

        self.log.info(
            "Rejecting Bitcoin mainnet P2P message magic"
        )

        self.send_wrong_magic_and_expect_disconnect(
            peer=peer,
            wrong_magic=BITCOIN_MAINNET_MAGIC,
            expected_log=(
                "Header error: Wrong MessageStart "
                "f9beb4d9 received"
            ),
            nonce=1,
        )

        self.log.info(
            "Checking chain remained unchanged after Bitcoin-magic rejection"
        )

        self.assert_mainnet_identity()

        self.log.info(
            "Reconnecting valid Andaluzcoin mainnet functional P2P peer"
        )

        peer = self.connect_framework_peer()

        self.assert_mainnet_identity()

        self.log.info(
            "Rejecting arbitrary invalid P2P message magic"
        )

        self.send_wrong_magic_and_expect_disconnect(
            peer=peer,
            wrong_magic=INVALID_MAGIC,
            expected_log=(
                "Header error: Wrong MessageStart "
                "ffffffff received"
            ),
            nonce=2,
        )

        self.log.info(
            "Checking final Andaluzcoin mainnet identity"
        )

        self.assert_mainnet_identity()

        assert_equal(
            node.getconnectioncount(),
            0,
        )

        assert_equal(
            node.getblockcount(),
            0,
        )

        assert_equal(
            node.getbestblockhash(),
            ANDALUZ_GENESIS_HASH,
        )


if __name__ == "__main__":
    AndaluzMainnetP2PNetworkSeparationIdentityTest(__file__).main()
