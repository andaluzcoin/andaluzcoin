# Andaluzcoin Chain Spec (Frozen)

## Identity
- Name: Andaluzcoin
- Ticker: ALUZ
- Unit denominations: ALUZ / mALUZ / µALUZ

## Supported networks (v0.1)
- Mainnet: YES (frozen)
- Regtest: YES (keep Bitcoin regtest params for now to avoid test cascade)
- Testnet/Testnet4/Signet: NOT shipping in v0.1 (re-spec later)

## Networks
### Mainnet (frozen)
- P2P port: 29444
- RPC port: 29443
- Message start (pchMessageStart): 0xb6 0xa9 0x64 0x58
- Bech32 HRP: aluz
- Base58 prefixes:
  - P2PKH: 55
  - P2SH: 117
  - WIF: 183
  - EXT_PUBLIC_KEY: 04 B2 47 46
  - EXT_SECRET_KEY: 04 B2 43 0C

## Consensus (mainnet)
- PoW algorithm: SHA256d
- Target block time: 10 minutes
- Difficulty adjustment: Bitcoin retarget (2016 blocks / 14 days)
- Min difficulty rules: false
- powLimit: 0000ffff00000000000000000000000000000000000000000000000000000000
- Max block weight: 4,000,000
- Coinbase maturity: 100

## Economics (mainnet)
- Initial block reward: 50 ALUZ
- Halving interval: 210,000 blocks
- Supply: ~21,000,000 ALUZ
- Premine/dev fund: none

## Softfork/BIP Policy (mainnet)
- Buried deployments active from height 1 (BIP34/65/66/CSV/Segwit)
- Taproot: ALWAYS_ACTIVE
- Everything else: default

## Genesis (mainnet)
- pszTimestamp: "Andaluzcoin 30/Jan/2026 Viva Al-Andalus"
- nTime: 1769731200
- nBits: 0x1f00ffff
- Nonce: 104982
- Merkle root: 14a3ed7e9a74a76a935c96b7101d9e5cd4c974534838d77c48bdadb15e103e2a
- Genesis hash: 00003b994550808d4803a2248b519e7f28646f45b45d68d1a947833dc290661a
