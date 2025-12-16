# Regtest Hammer Tools

Helpers to stress block storage & rotation on regtest.

## Files
- `hammer_opreturn.py` – crafts large OP_RETURN txs and mines a block to pack them.
- `hammer_until_rotate.sh` – loops `hammer_opreturn.py` until blk file rotation or size growth thresholds.

## Usage
```bash
export PATH="$HOME/workspace/andaluzcoin/contrib/regtest:$PATH"   # or add to ~/.bashrc

# mine big blocks until a new blk file appears
STOP_WHEN=files TARGET_NEW_FILES=1 hammer_until_rotate.sh

# or stop after +50 MB growth
STOP_WHEN=any TARGET_MB_GROWTH=50 hammer_until_rotate.sh