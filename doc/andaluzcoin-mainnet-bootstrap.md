# Andaluzcoin mainnet bootstrap operations

This is a prelaunch guide. Mainnet `vSeeds` and `vFixedSeeds` are empty.
No public bootstrap service or addresses have been approved or deployed.
The local functional test proves manual daemon connections and recovery on
loopback; it does not prove public reachability, DNS discovery, mining security,
or a reliable public network.

## Configure a known peer

Obtain a peer endpoint from its operator through a verified out-of-band channel.
Confirm operator ownership, network/genesis and intended availability. All
`PEER_IP`, `OTHER_PEER_IP`, `PEER_HOST` and `/ABS/PATH/ALUZ_DATA` values below
are placeholders; replace them before use. There is no approved live endpoint.

Use the actual binaries `build/bin/bitcoind` and `build/bin/bitcoin-cli`.
Create a private data directory first, restrict its access to the service owner,
and put a reviewed `bitcoin.conf` there. Mainnet is `-chain=main` (the default),
not `-mainnet`. Example config:

```ini
chain=main
server=1
disablewallet=1
dnsseed=0
fixedseeds=0
natpmp=0
[main]
addnode=PEER_IP:29444
# Repeat addnode for independently verified operators when available.
# addnode=OTHER_PEER_IP:29444
rpcbind=127.0.0.1
rpcallowip=127.0.0.1
```

This deliberately permits RPC only on IPv4 loopback. Cookie authentication is
available by default; keep the cookie private. Do not put custody keys, wallet
seeds or reusable plaintext passwords in configuration. No wallet is needed
for a validating node. `rpcbind` requires `rpcallowip` to take effect; never
broaden either to a public interface/network. Default RPC without overrides
binds to localhost (IPv4 and IPv6). Mainnet RPC port is **29443**; **29444** is
P2P, used by peers for protocol messages, not administrative RPC.

```sh
build/bin/bitcoind -datadir=/ABS/PATH/ALUZ_DATA -chain=main -daemon
```

Alternatively pass `-addnode=PEER_IP:29444` on the daemon launch command.
A launch argument persists operationally only if the same service/launch
command supplies it again. A saved config entry is reread after restart;
editing it while running does not immediately change connections.

| Mechanism | Behavior in this version |
| --- | --- |
| `-addnode=PEER_HOST:29444` / config `addnode=` | Maintain a manual connection; repeat for multiple peers. Separate limit of eight concurrent addnode connections. Does not disable ordinary discovery. |
| `-connect=PEER_HOST:29444` | Restrict automatic outgoing connections to specified manual destinations; repeat for multiple peers. Soft-disables listening and DNS seeds unless explicitly overridden. Specified connect destinations supersede seednode fetching. |
| `-connect=0` / `-noconnect` | Disable automatic addrman outgoing connections; the separate addnode worker still runs. |
| `-seednode=PEER_HOST:29444` | Fetch addresses through a temporary connection, then disconnect; not a maintained relationship. Tried before DNS seeds. |
| RPC `addnode ENDPOINT add` | Add to the running process's maintained list; lost on restart. |
| RPC `addnode ENDPOINT remove` | Remove from that runtime list; does not itself disconnect an existing peer. Saved launch config remains effective on next restart. |
| RPC `addnode ENDPOINT onetry` | Try once; no maintained list entry or persistence. RPC success is not handshake confirmation. |

`-dnsseed=0` disables seed queries, not DNS resolution of manual hostnames.
`-dns=0` disables hostname lookup for manual options; use numeric addresses
if selecting that policy. Keep transport defaults; dedicated encrypted transport
identity validation is a later milestone. A user-agent string identifies claimed
software, not an authenticated operator or trustworthy chain.

## Verify connections and identity

Run locally as the data directory owner (the CLI reads the same config/cookie):

```sh
build/bin/bitcoin-cli -datadir=/ABS/PATH/ALUZ_DATA -chain=main -rpcwait getnetworkinfo
build/bin/bitcoin-cli -datadir=/ABS/PATH/ALUZ_DATA -chain=main getpeerinfo
build/bin/bitcoin-cli -datadir=/ABS/PATH/ALUZ_DATA -chain=main getaddednodeinfo
build/bin/bitcoin-cli -datadir=/ABS/PATH/ALUZ_DATA -chain=main getblockchaininfo
build/bin/bitcoin-cli -datadir=/ABS/PATH/ALUZ_DATA -chain=main getblockhash 0
build/bin/bitcoin-cli -datadir=/ABS/PATH/ALUZ_DATA -chain=main getnodeaddresses 20
```

Expect `chain` = `main` and genesis
`000000f7dca7651a1397fd0bc99b2a456dbb2d23470834b6290aadec4b46d15c`.
Mainnet message magic is `b6a96458` (source parameter, not an RPC identity field).
Check `networkactive`, local `/AndaluzcoinCore:` subversion, and each peer's
positive protocol `version`, `subver`, `inbound`, `addr`, `addrbind` and
`connection_type`. A joining client should have a manual outbound peer at the
verified endpoint; the server should observe an inbound connection. Inspect
ping responses and continued message activity after handshake. Added-node
`connected` and `addresses` report the maintained relationship; `onetry` peers
are absent from that list. `getnodeaddresses` reports addrman records, not live
connections or proof of public discovery. Empty results can be expected here.
Loopback addresses are subject to routability/storage/relay filtering; the
local test makes no public address gossip assertions.

## Outages and operating policy

Monitor peer availability, handshake failures, block/header progress, restart
success, disk space and logs. Alert on loss of independent peers and stalled
chain progress; compare tips with independently controlled operators. Keep
reviewed config/operational backups and test restoration; protect any separate
wallet backups and secrets. Use patched systems and SSH keys with restricted
administrative access. Expose only intended P2P ingress through a default-deny
firewall; keep RPC nonpublic and use SSH access for administration. This guide
does not authorize firewall changes or deployment.

Outbound-only nodes can join without inbound public reachability. Inbound
operators must later verify routing, NAT and firewall behavior separately for
IPv4 and IPv6; use `[IPv6_ADDRESS]:29444` syntax. DNS records and working IPv4
do not establish working IPv6 or vice versa. Do not advertise untested routes.

The addnode worker retries after 60 seconds when it attempted a connection,
otherwise after two seconds; scheduling and network failures add delay. Avoid
assuming instant recovery. Check status/logs after restoration. For an explicit
manual retry, after verifying the endpoint is restored:

```sh
build/bin/bitcoin-cli -datadir=/ABS/PATH/ALUZ_DATA -chain=main addnode PEER_IP:29444 onetry
```

Then verify the real handshake with `getpeerinfo`. To add a fallback, use
`addnode OTHER_PEER_IP:29444 add`, verify connection, and save a corresponding
`[main]` addnode entry for later restarts. Do not continually issue retries
without checking existing connections. The test permits 90 seconds for one
local automatic reconnect; it supplies no WAN service-level guarantee.

Plan at least three independently controlled bootstrap operators across distinct
providers, networks and failure domains, with multiple verified endpoints per
participant and tested downtime procedures. Avoid a single trusted endpoint:
manual peers receive special disconnection protections, so malicious selection
can increase eclipse risk. Hardcoding several IPs alone does not establish
independence or decentralization. Full nodes validate the same PoW rules;
miners additionally supply work and produce blocks. Additional validating peers
do not create blocks without miners or provide sufficient attack resistance.

## Pre-public launch gates (all TO DO; not established by this milestone)

- [ ] TO DO: Record at least three independent operators and distinct provider,
  administrative and failure domains, with authenticated endpoint exchange.
- [ ] TO DO: Demonstrate independent remote mainnet node joins and handshakes
  on every advertised IPv4/IPv6 path; record results and observation duration.
- [ ] TO DO: Agree measurable uptime/alert response targets, monitor peers and
  chain progress, and complete bootstrap outage, restart and backup restore drills.
- [ ] TO DO: Review host hardening, SSH access, private RPC binding/authentication,
  firewall policy and operational ownership for every proposed public node.
- [ ] TO DO: Publish accessible operator instructions and verified fallback
  contacts; independently review any future DNS/fixed-seed service design,
  ownership, diversity, monitoring and update policy before adding endpoints.
- [ ] TO DO: Confirm sustained independent mining participation with measured
  block production and difficulty behavior; perform a PoW/eclipsing attack review.

Connectivity tests alone cannot satisfy these gates. Mining sustainability and
alternative difficulty/AuxPoW research remain separate work.
