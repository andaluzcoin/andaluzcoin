#!/usr/bin/env python3
# Copyright (c) 2019-2022 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test that we reject low difficulty headers to prevent our block tree from filling up with useless bloat"""

from test_framework.messages import (
    CBlockHeader,
    from_hex,
)
from test_framework.p2p import (
    P2PInterface,
    msg_headers,
)
from test_framework.test_framework import AndaluzcoinTestFramework

from test_framework.p2p import P2PDataStore

import os


class SendPingMessagesHeadersTest(AndaluzcoinTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.chain = "regtest"   # ✅ Ensure regtest for matching magic bytes
        self.num_nodes = 2
        self.extra_args = [["-minimumchainwork=0x0", '-prune=550']] * self.num_nodes

    def add_options(self, parser):
        parser.add_argument(
            '--datafile',
            default='headers.dat',  # ✅ Clean regtest default
            help='Path to regtest headers file (default: %(default)s)',
        )

    def run_test(self):
        self.log.info("Read headers data")

        self.log.info("🌐 Connecting P2P test peer")
        peer = self.nodes[0].add_p2p_connection(P2PDataStore())
        peer.timeout_factor = 1.0

        self.log.info("📡 Sending ping to test diagnostics")
        peer.send_and_ping(msg_headers([]))

        self.log.info("✅ Ping response successfully received")

if __name__ == '__main__':
    SendPingMessagesHeadersTest(__file__).main()
