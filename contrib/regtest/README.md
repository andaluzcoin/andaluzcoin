# Regtest hammer tools

- `hammer_opreturn.py` – crafts jumbo OP_RETURN txs and mines a block to pack them.
- `hammer_until_rotate.sh` – loops hammering until blk file rotation or size-on-disk target.

Examples:
  DATADIR=/tmp/andaluz_regtest ./hammer_opreturn.py
  STOP_WHEN=files TARGET_NEW_FILES=1 ./hammer_until_rotate.sh
