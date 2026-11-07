# HyperLogLog accuracy project (Ibrahim & Nika)

## Build / run
    make check                         # tests + hash uniformity check
    make build/exp1
    build/exp1 14 20 10000000 > results/exp1_p14.csv
    python3 exp/plot_exp1.py results/exp1_p14.csv results/exp1_p14.png

## Layout
- `src/hll.hpp`   HyperLogLog: `estimate_basic()`, `estimate_lc()`, `merge()`, `empty_fraction()`
- `src/gen.hpp`   input generator (random 64-bit IDs + repeats, true count known by construction)
- `tests/`        0/1/2 items, register edge cases, merge, generator vs real hash set
- `tools/hash_check.cpp`  uniformity check for the hash
- `exp/`          experiment 1 (done as smoke run), plot script
- `third_party/xxHash`    xxHash v0.8.3 (header-only)

## TBD decisions (Week 1)
| Item | Decision | Why |
|---|---|---|
| Language | C++ | g++/clang available, bit tricks (clz) are direct |
| Hash | XXH3-64 (xxHash) | passes chi-square / rho / bit-balance on 10^6 random AND sequential keys |
| Benchmark tool | **open**: Google Benchmark is not installed; either fetch it from GitHub or write a small harness (warm-up, keys built outside timing, result sink) | decide before experiment 3 |
| Real dataset | **open**: not searched yet | drop first if late |
| Seeds | 20 | smoke run: sd at large n = 0.79% vs theory 0.81%, fine |

## Still to do
- Slide 10 example: test has a `TODO` placeholder; we need the slides to copy the exact numbers.
- Experiment 2 (p = 4..16), experiment 3 (time, memory, hash set).
- Memory: we STORE 1 byte per register (16 KB at p=14); the 12 KB figure assumes packed 6-bit registers
  (`bytes_packed_6bit()`). Report both.
