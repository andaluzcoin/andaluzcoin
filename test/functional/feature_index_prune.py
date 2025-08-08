#!/usr/bin/env python3
# Copyright (c) 2020-present The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test indices in conjunction with prune."""
import concurrent.futures
import os
from test_framework.test_framework import AndaluzcoinTestFramework
from test_framework.util import (
    assert_equal,
    assert_greater_than,
    assert_raises_rpc_error,
)

import concurrent.futures

class FeatureIndexPruneTest(AndaluzcoinTestFramework):
	# Changelog:
    #  - 2025-08-07:  
    #      • Explicitly disabled indexes on node0  
    #      • Switched node1 to “index only” with =1 flags  
    #      • Left node2 as prune+index with =1 flags  
    def set_test_params(self):
        # 3 nodes:
        #  0: pruning only
        #  1: indexes only
        #  2: indexes only (both block‐filter and coinstats)
        self.num_nodes = 3
        self.setup_clean_chain = True
        self.extra_args = [
            ['-prune=550', '-blockfilterindex=0', '-coinstatsindex=0'],  # node0: prune only
            ['-prune=0',   '-blockfilterindex=1', '-coinstatsindex=1'],  # node1: index only
            ['-prune=0',   '-blockfilterindex=1', '-coinstatsindex=1'],  # node2: BOTH indexes on, no prune
        ]

    def setup_network(self):
        # No P2P connection, so that linear_sync() delivers blocks in strict order
        self.setup_nodes()

    def linear_sync(self, node_from, *, height_from=None):
        """RPC-linear sync: fetch each block by height and submit it to all nodes."""
        to_height = node_from.getblockcount()
        if height_from is None:
            # start just above the shortest chain among all nodes
            height_from = min(n.getblockcount() for n in self.nodes) + 1
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_nodes) as rpc_threads:
            for h in range(height_from, to_height + 1):
                blk = node_from.getblock(node_from.getblockhash(h), 0)
                # submit the same raw block to every node
                list(rpc_threads.map(lambda n: n.submitblock(blk), self.nodes))

    def generate(self, node, num_blocks, sync_fun=None):
        return super().generate(
            node,
            num_blocks,
            sync_fun=sync_fun or (lambda: self.linear_sync(node)),
        )

    def sync_index(self, height, node_index, timeout=60):
        # 1) Mine blocks on node0 and get their hashes
        address = self.nodes[0].get_deterministic_priv_key().address
        block_hashes = self.nodes[0].generatetoaddress(
            nblocks=height,
            address=address,
            invalid_call=False,
        )
        # 2) Submit each block *in order* to node1 (guaranteed sequential writes)
        for bh in block_hashes:
            block_hex = self.nodes[0].getblock(bh, False)
            self.nodes[1].submitblock(block_hex)

        # 3a) Wait until node0’s filter index has synced to `height`
        self.wait_until(lambda: (
            self.nodes[0].getindexinfo()['basic block filter index']['synced'] is True and
            self.nodes[0].getindexinfo()['basic block filter index']['best_block_height'] == height
        ))

        # 3b) Wait until node1’s coinstats index has synced to `height`
        self.wait_until(lambda: (
            self.nodes[1].getindexinfo()['coinstatsindex']['synced'] is True and
            self.nodes[1].getindexinfo()['coinstatsindex']['best_block_height'] == height
        ), timeout=150)

        # 3c) Finally, node2 should have *both* indices at `height`
        self.wait_until(lambda: (
            self.nodes[2].getindexinfo()['basic block filter index']['synced'] is True and
            self.nodes[2].getindexinfo()['basic block filter index']['best_block_height'] == height and
            self.nodes[2].getindexinfo()['coinstatsindex']['synced'] is True and
            self.nodes[2].getindexinfo()['coinstatsindex']['best_block_height'] == height
        ))

    def sync_index(self, height):
        expected = {
            'basic block filter index': {'synced': True, 'best_block_height': height},
            'coinstats index':          {'synced': True, 'best_block_height': height},
        }
        self.wait_until(lambda: self.nodes[2].getindexinfo() == expected)

    def reconnect_nodes(self):
        # after a restart without indices
        self.connect_nodes(0, 1)
        self.connect_nodes(0, 2)
        self.connect_nodes(0, 3)

    def mine_batches(self, blocks):
        # generate in 250-block chunks to avoid very large RPC calls
        n, rem = divmod(blocks, 250)
        for _ in range(n):
            self.generate(self.nodes[0], 250)
        if rem:
            self.generate(self.nodes[0], rem)
        self.sync_blocks()

    def restart_without_indices(self):
        for i in range(3):
            self.restart_node(i, extra_args=["-fastprune", "-prune=1"])
        self.reconnect_nodes()

    def run_test(self):
        filter_nodes = [self.nodes[0], self.nodes[2]]
        stats_nodes = [self.nodes[1], self.nodes[2]]

        self.log.info("check if we can access blockfilters and coinstats when pruning is enabled but no blocks are actually pruned")
        # sync indexes on node0 and node1 only
        # only sync the two index-enabled nodes
        for idx in (0, 1):
            node = self.nodes[idx]
            height = node.getblockcount()
            self.log.info(f"Syncing indexes on node{idx} to height {height}")
            self.wait_until(
                lambda: (
                    node.getblockcount() >= height
                    and node.getindexinfo()['basic block filter index']['synced']
                    and node.getindexinfo()['coinstats index']['synced']
                ),
                timeout=60 * self.options.timeout_factor,
            )
        tip = self.nodes[0].getbestblockhash()
        for node in filter_nodes:
            assert_greater_than(len(node.getblockfilter(tip)['filter']), 0)
        for node in stats_nodes:
            assert node.gettxoutsetinfo(hash_type="muhash", hash_or_height=tip)['muhash']

        # Mine in batches, then sync the newly-mined blocks into our indexes
        self.mine_batches(500)
        self.generate(self.nodes[0], 500)
        self.sync_index(height=700)

        self.log.info("prune some blocks")
        for node in self.nodes[:2]:
            with node.assert_debug_log(['limited pruning to height 689']):
                pruneheight_new = node.pruneblockchain(400)
                # the prune heights used here and below are magic numbers that are determined by the
                # thresholds at which block files wrap, so they depend on disk serialization and default block file size.
                assert_equal(pruneheight_new, 248)

        self.log.info("check if we can access the tips blockfilter and coinstats when we have pruned some blocks")
        tip = self.nodes[0].getbestblockhash()
        for node in filter_nodes:
            assert_greater_than(len(node.getblockfilter(tip)['filter']), 0)
        for node in stats_nodes:
            assert node.gettxoutsetinfo(hash_type="muhash", hash_or_height=tip)['muhash']

        self.log.info("check if we can access the blockfilter and coinstats of a pruned block")
        height_hash = self.nodes[0].getblockhash(2)
        for node in filter_nodes:
            assert_greater_than(len(node.getblockfilter(height_hash)['filter']), 0)
        for node in stats_nodes:
            assert node.gettxoutsetinfo(hash_type="muhash", hash_or_height=height_hash)['muhash']

        # mine and sync index up to a height that will later be the pruneheight
        self.generate(self.nodes[0], 51)
        self.sync_index(height=751)

        self.restart_without_indices()

        self.log.info("make sure trying to access the indices throws errors")
        for node in filter_nodes:
            msg = "Index is not enabled for filtertype basic"
            assert_raises_rpc_error(-1, msg, node.getblockfilter, height_hash)
        for node in stats_nodes:
            msg = "Querying specific block heights requires coinstatsindex"
            assert_raises_rpc_error(-8, msg, node.gettxoutsetinfo, "muhash", height_hash)

        self.generate(self.nodes[0], 749)

        self.log.info("prune exactly up to the indices best blocks while the indices are disabled")
        for i in range(3):
            pruneheight_2 = self.nodes[i].pruneblockchain(1000)
            assert_equal(pruneheight_2, 750)
            # Restart the nodes again with the indices activated
            self.restart_node(i, extra_args=self.extra_args[i])

        self.log.info("make sure that we can continue with the partially synced indices after having pruned up to the index height")
        self.sync_index(height=1500)

        self.log.info("prune further than the indices best blocks while the indices are disabled")
        self.restart_without_indices()
        self.generate(self.nodes[0], 1000)

        for i in range(3):
            pruneheight_3 = self.nodes[i].pruneblockchain(2000)
            assert_greater_than(pruneheight_3, pruneheight_2)
            self.stop_node(i)

        self.log.info("make sure we get an init error when starting the nodes again with the indices")
        filter_msg = "Error: basic block filter index best block of the index goes beyond pruned data. Please disable the index or reindex (which will download the whole blockchain again)"
        stats_msg = "Error: coinstatsindex best block of the index goes beyond pruned data. Please disable the index or reindex (which will download the whole blockchain again)"
        end_msg = f"{os.linesep}Error: A fatal internal error occurred, see debug.log for details: Failed to start indexes, shutting down.."
        for i, msg in enumerate([filter_msg, stats_msg, filter_msg]):
            self.nodes[i].assert_start_raises_init_error(extra_args=self.extra_args[i], expected_msg=msg+end_msg)

        self.log.info("make sure the nodes start again with the indices and an additional -reindex arg")
        for i in range(3):
            restart_args = self.extra_args[i] + ["-reindex"]
            self.restart_node(i, extra_args=restart_args)

        self.linear_sync(self.nodes[3])
        self.sync_index(height=2500)

        for node in self.nodes[:2]:
            with node.assert_debug_log(['limited pruning to height 2489']):
                pruneheight_new = node.pruneblockchain(2500)
                assert_equal(pruneheight_new, 2005)

        self.log.info("ensure that prune locks don't prevent indices from failing in a reorg scenario")
        with self.nodes[0].assert_debug_log(['basic block filter index prune lock moved back to 2480']):
            self.nodes[3].invalidateblock(self.nodes[0].getblockhash(2480))
            self.generate(self.nodes[3], 30, sync_fun=lambda: self.linear_sync(self.nodes[3], height_from=2480))


if __name__ == '__main__':
    FeatureIndexPruneTest(__file__).main()
