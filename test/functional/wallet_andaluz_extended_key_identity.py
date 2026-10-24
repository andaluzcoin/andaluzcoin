#!/usr/bin/env python3
# Copyright (c) 2026 The Andaluzcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

"""Characterize mainnet extended-key identity without changing wallet formats."""

import logging

from test_framework.address import base58_to_byte, byte_to_base58
from test_framework.authproxy import JSONRPCException
from test_framework.descriptors import descsum_check, descsum_create
from test_framework.key import ECKey
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal, assert_raises_rpc_error


PUBLIC_VERSION = bytes.fromhex("04b24746")
PRIVATE_VERSION = bytes.fromhex("04b2430c")
BITCOIN_PUBLIC_VERSION = bytes.fromhex("0488b21e")


def decode_extended_key(encoded):
    """The framework checks the checksum but removes only ONE version byte.

    Return the full 78-byte serialization. Bare assertions avoid printing
    secret bytes on failure when this helper processes a private export.
    """
    remainder, first = base58_to_byte(encoded)
    serialized = bytes([first]) + remainder
    assert len(serialized) == 78, "Unexpected extended-key length"
    return serialized


def replace_version(serialized, version):
    """Preserve all 74 non-version bytes and recompute Base58Check."""
    return byte_to_base58(version[1:] + serialized[4:], version[0])


class AndaluzWalletExtendedKeyIdentityTest(BitcoinTestFramework):
    def set_test_params(self):
        self.chain = ""
        self.setup_clean_chain = True
        self.num_nodes = 1
        self.wallet_names = []
        self.bind_to_localhost_only = True
        self.extra_args = [["-dnsseed=0", "-fixedseeds=0", "-dns=0", "-connect=0"]]

    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    def check_private_export(self, wallet, public):
        # Authproxy DEBUG tracing includes RPC responses. Suppress it even if
        # the test is invoked with --tracerpc; never send secrets to parsers.
        rpc_logger = logging.getLogger("BitcoinRPC")
        previous_level = rpc_logger.level
        rpc_logger.setLevel(logging.CRITICAL + 1)
        try:
            try:
                private_entries = wallet.gethdkeys(private=True)
            except JSONRPCException:
                raise AssertionError("Private HD export failed (details suppressed)") from None
            assert len(private_entries) == 1, "Unexpected private HD key count"
            entry = private_entries[0]
            assert entry["xpub"] == public["xpub"], "Public export mismatch"
            assert entry["has_private"], "Missing private HD key"
            private = decode_extended_key(entry["xprv"])
            pub = decode_extended_key(public["xpub"])
            assert private[:4] == PRIVATE_VERSION, "Unexpected private version"
            assert private[4:45] == pub[4:45], "Extended-key metadata mismatch"
            assert private[45] == 0, "Missing private key marker"
            key = ECKey()
            key.set(private[46:], compressed=True)
            assert key.get_pubkey().get_bytes() == pub[45:], "Neutering mismatch"
        finally:
            rpc_logger.setLevel(previous_level)

    def run_test(self):
        node = self.nodes[0]
        self.log.info("Checking isolated mainnet and descriptor wallet identity")
        assert_equal(node.getblockchaininfo()["chain"], "main")
        assert_equal(node.getblockcount(), 0)
        assert_equal(node.getblockhash(0), "000000f7dca7651a1397fd0bc99b2a456dbb2d23470834b6290aadec4b46d15c")
        assert node.getnetworkinfo()["subversion"].startswith("/AndaluzcoinCore:")
        assert_equal(node.getconnectioncount(), 0)
        assert_equal(node.getpeerinfo(), [])
        name = "extended_identity"
        node.createwallet(wallet_name=name)
        wallet = node.get_wallet_rpc(name)
        info = wallet.getwalletinfo()
        assert_equal(info["descriptors"], True)
        assert_equal(info["format"], "sqlite")
        assert_equal(info["private_keys_enabled"], True)

        entries = wallet.gethdkeys()
        assert_equal(len(entries), 1)
        public = entries[0]
        assert_equal(public["has_private"], True)
        assert "xprv" not in public
        serialized = decode_extended_key(public["xpub"])
        assert_equal(serialized[:4], PUBLIC_VERSION)
        assert serialized[45] in (2, 3)
        self.check_private_export(wallet, public)

        self.log.info("Checking coherent public descriptor exports and checksums")
        exported = wallet.listdescriptors()
        assert_equal({d["desc"] for d in exported["descriptors"]}, {d["desc"] for d in public["descriptors"]})
        assert exported["descriptors"]
        for item in exported["descriptors"]:
            desc = item["desc"]
            assert descsum_check(desc)
            normalized = node.getdescriptorinfo(desc)
            assert_equal(normalized["descriptor"], desc)
            assert_equal(normalized["hasprivatekeys"], False)
            assert_equal(normalized["checksum"], desc[-8:])

        self.log.info("Checking explicit wrappers using the same public HD key")
        key = public["xpub"] + "/0/*"
        bodies = [f"wpkh({key})", f"sh(wpkh({key}))", f"pkh({key})", f"tr({key})"]
        scripts = set()
        addresses = []
        for body, prefix in zip(bodies, ["aluz1q", "p", "P", "aluz1p"]):
            desc = descsum_create(body)
            result = node.getdescriptorinfo(body)
            assert_equal(result["descriptor"], desc)
            assert_equal(result["isrange"], True)
            assert_equal(result["issolvable"], True)
            assert_equal(result["hasprivatekeys"], False)
            address = node.deriveaddresses(desc, [0, 0])[0]
            assert address.startswith(prefix)
            validation = node.validateaddress(address)
            assert_equal(validation["isvalid"], True)
            scripts.add(validation["scriptPubKey"])
            addresses.append(address)
        assert_equal(len(scripts), 4)
        assert_equal(len(set(addresses)), 4)
        descriptor = descsum_create(bodies[0])

        self.log.info("Checking watch-only import and deterministic receiving address")
        node.createwallet(wallet_name="extended_watch", disable_private_keys=True, blank=True)
        watch = node.get_wallet_rpc("extended_watch")
        assert_equal(watch.getwalletinfo()["private_keys_enabled"], False)
        request = {"desc": descriptor, "timestamp": "now", "active": True, "range": [0, 2], "next_index": 0}
        assert_equal(watch.importdescriptors([request])[0]["success"], True)
        assert_equal(watch.getnewaddress("", "bech32"), addresses[0])
        ownership = watch.getaddressinfo(addresses[0])
        assert_equal(ownership["ismine"], True)
        assert_equal(ownership["solvable"], True)
        assert_equal(ownership["iswatchonly"], False)  # Deprecated: always false.
        assert_equal(watch.gethdkeys()[0]["has_private"], False)

        self.log.info("Checking wrong-version and checksum rejection with public material")
        bitcoin_key = replace_version(serialized, BITCOIN_PUBLIC_VERSION)
        rewritten = decode_extended_key(bitcoin_key)
        assert_equal(rewritten[:4], BITCOIN_PUBLIC_VERSION)
        assert_equal(rewritten[4:], serialized[4:])
        corrupt = public["xpub"][:-1] + ("1" if public["xpub"][-1] != "1" else "2")
        for rejected_key in (bitcoin_key, corrupt):
            rejected = descsum_create(f"wpkh({rejected_key}/0/*)")
            assert_raises_rpc_error(-5, "is not valid", node.getdescriptorinfo, rejected)
            failure = watch.importdescriptors([{"desc": rejected, "timestamp": "now", "range": [0, 2]}])[0]
            assert_equal(failure["success"], False)
            assert_equal(failure["error"]["code"], -5)
            assert "is not valid" in failure["error"]["message"]
        bad_checksum = descriptor[:-1] + ("q" if descriptor[-1] != "q" else "p")
        assert not descsum_check(bad_checksum)
        assert_raises_rpc_error(-5, "checksum", node.getdescriptorinfo, bad_checksum)

        self.log.info("Checking public identity preservation across wallet reload")
        node.unloadwallet(name)
        node.loadwallet(name)
        wallet = node.get_wallet_rpc(name)
        assert_equal(wallet.gethdkeys(), entries)
        assert_equal(wallet.listdescriptors(), exported)
        assert_equal(node.deriveaddresses(descriptor, [0, 0])[0], addresses[0])
        node.unloadwallet("extended_watch")
        node.loadwallet("extended_watch")
        watch = node.get_wallet_rpc("extended_watch")
        assert_equal(watch.getaddressinfo(addresses[0])["ismine"], True)
        assert_equal(watch.getnewaddress("", "bech32"), node.deriveaddresses(descriptor, [1, 1])[0])
        assert_equal(node.getblockcount(), 0)
        assert_equal(node.getconnectioncount(), 0)


if __name__ == "__main__":
    AndaluzWalletExtendedKeyIdentityTest(__file__).main()
