# Andaluzcoin Developer Notes

## Build directory rule

Use separate build directories for normal functional tests and fuzz testing.

### Normal build

Use `build/` only for normal daemon, CLI, wallet, unit, and functional tests.

```bash
cmake -B build -S . \
  -DBUILD_FOR_FUZZING=OFF \
  -DBUILD_FUZZ_BINARY=OFF \
  -DBUILD_DAEMON=ON \
  -DBUILD_CLI=ON \
  -DENABLE_WALLET=ON \
  -DBUILD_WALLET_TOOL=ON \
  -DBUILD_TESTS=ON

cmake --build build -j 1
