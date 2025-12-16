#!/usr/bin/env bash
set -euo pipefail

# --- Config (override via env) ---
DATADIR="${DATADIR:-/tmp/andaluz_regtest}"
CLI="${CLI:-build/src/andaluzcoin-cli}"
PY="${PY:-python3}"
HAMMER="${HAMMER:-hammer_opreturn.py}"

TXS="${TXS:-40}"          # txs per block for hammer_opreturn.py
BYTES="${BYTES:-20000}"   # OP_RETURN bytes per tx
FEE="${FEE:-0.000001}"    # BTC/kB feerate

TARGET_NEW_FILES="${TARGET_NEW_FILES:-1}"   # stop after this many new blk files (0 to disable)
TARGET_MB_GROWTH="${TARGET_MB_GROWTH:-0}"  # stop after this many MB growth in size_on_disk (0 to disable)
STOP_WHEN="${STOP_WHEN:-any}"              # "any", "both", "files", or "mb"

blocksdir="$DATADIR/regtest/blocks"
mkdir -p "$blocksdir"

# Validate STOP_WHEN and add simple guardrails
case "$STOP_WHEN" in
  any|both|files|mb) ;;
  *)
    echo "error: STOP_WHEN must be 'any', 'both', 'files', or 'mb'" >&2
    exit 1
    ;;
esac
if [[ "$STOP_WHEN" == "files" && ${TARGET_NEW_FILES:-0} -le 0 ]]; then
  echo "error: STOP_WHEN=files requires TARGET_NEW_FILES > 0" >&2
  exit 1
fi
if [[ "$STOP_WHEN" == "mb" && ${TARGET_MB_GROWTH:-0} -le 0 ]]; then
  echo "error: STOP_WHEN=mb requires TARGET_MB_GROWTH > 0" >&2
  exit 1
fi

# --- Helpers ---
find_blk_count () {
  find "$blocksdir" -maxdepth 1 -type f -name 'blk*.dat' 2>/dev/null | wc -l | tr -d ' '
}
get_size_on_disk () {
  "$CLI" -regtest -datadir="$DATADIR" getblockchaininfo \
    | "$PY" -c 'import sys,json; print(json.load(sys.stdin)["size_on_disk"])'
}
get_height () {
  "$CLI" -regtest -datadir="$DATADIR" getblockcount
}
bytes_to_mb () {
  awk -v b="$1" 'BEGIN{printf "%.2f", b/1024/1024}'
}

# spinner state
_frames='|/-\'
_frame_idx=0
spin () {
  local i=$((_frame_idx % ${#_frames}))
  printf "%s" "${_frames:$i:1}"
  _frame_idx=$((_frame_idx + 1))
}

# pretty target strings
target_desc_files () {
  if (( TARGET_NEW_FILES > 0 )); then
    printf "+%d files" "$TARGET_NEW_FILES"
  else
    printf "∞ files"
  fi
}
target_desc_mb () {
  if (( TARGET_MB_GROWTH > 0 )); then
    printf "+%d MB" "$TARGET_MB_GROWTH"
  else
    printf "∞ MB"
  fi
}

# progress line
print_progress () {
  local h="$1" files="$2" size_bytes="$3" start_files="$4" start_size="$5"
  local d_files=$((files - start_files))
  local d_bytes=$((size_bytes - start_size))
  local now
  now="$(date '+%H:%M:%S')"
  printf "\r[%s] height=%-8s files=%-4s (Δ %2d) size=%7s MB (Δ %6s MB)  target: %s, %s  %s" \
    "$now" \
    "$h" \
    "$files" \
    "$d_files" \
    "$(bytes_to_mb "$size_bytes")" \
    "$(bytes_to_mb "$d_bytes")" \
    "$(target_desc_files)" \
    "$(target_desc_mb)" \
    "$(spin)"
}

# ensure final newline on exit
cleanup() { printf "\n"; }
trap cleanup EXIT

# --- Pre-flight ---
if ! "$CLI" -regtest -datadir="$DATADIR" getblockcount >/dev/null 2>&1; then
  echo "error: CLI cannot reach node at DATADIR=$DATADIR" >&2
  exit 1
fi

start_height=$(get_height || echo 0)
start_files=$(find_blk_count)
start_size=$(get_size_on_disk || echo 0)

# compute targets
target_files=$start_files
if (( TARGET_NEW_FILES > 0 )); then
  target_files=$((start_files + TARGET_NEW_FILES))
fi
target_size_bytes=$start_size
if (( TARGET_MB_GROWTH > 0 )); then
  target_size_bytes=$((start_size + TARGET_MB_GROWTH*1024*1024))
fi

echo "Starting… blk_files=$start_files, size_on_disk=$(bytes_to_mb "$start_size") MB, height=$start_height"
echo "Targets: new_files=${TARGET_NEW_FILES}, +MB=${TARGET_MB_GROWTH}, mode=${STOP_WHEN}"

# initial progress line
print_progress "$start_height" "$start_files" "$start_size" "$start_files" "$start_size"

# --- Loop until condition(s) met ---
while :; do
  # fire one hammer round (mine a fat block packing jumbo OP_RETURN txs)
  TXS="$TXS" BYTES="$BYTES" FEE="$FEE" "$PY" "$HAMMER" >/dev/null

  current_files=$(find_blk_count)
  current_size=$(get_size_on_disk || echo "$start_size")
  height=$(get_height || echo "$start_height")

  # update progress line
  print_progress "$height" "$current_files" "$current_size" "$start_files" "$start_size"

  files_ok=false
  size_ok=false
  if (( TARGET_NEW_FILES > 0 )) && (( current_files >= target_files )); then files_ok=true; fi
  if (( TARGET_MB_GROWTH > 0 )) && (( current_size >= target_size_bytes )); then size_ok=true; fi

  case "$STOP_WHEN" in
    both)  [[ "$files_ok" == true && "$size_ok" == true ]] && break ;;
    files) [[ "$files_ok" == true ]] && break ;;
    mb)    [[ "$size_ok" == true ]] && break ;;
    any)   { [[ "$files_ok" == true ]] || [[ "$size_ok" == true ]]; } && break ;;
  esac
done

# newline for clean report
printf "\n"

# --- Report ---
end_files=$(find_blk_count)
end_size=$(get_size_on_disk || echo "$start_size")
growth=$(( end_size - start_size ))
echo "=== Report ==="
echo "blk files: $start_files -> $end_files"
echo "size_on_disk: $(bytes_to_mb "$start_size") MB -> $(bytes_to_mb "$end_size") MB (Δ $(bytes_to_mb "$growth") MB)"
echo -n "tip height: "
get_height || true
ls -lh "$blocksdir"/blk*.dat "$blocksdir"/rev*.dat 2>/dev/null || true
