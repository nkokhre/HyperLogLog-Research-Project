# HyperLogLog accuracy project (Ibrahim & Nika)

Advanced Algorithms & Data Structures, Fall 2026. Full plan: `proposal.pdf` (final version).

We implement HyperLogLog (HLL) from scratch and measure how accurate it is and where it stops being accurate.

Research questions:
1. How does the error change with the true count n, and does linear counting (LC, the small-count fix from HyperLogLog++) remove the error for small counts?
2. How does the number of registers (2^p) change the error, compared with the theory value 1.04/sqrt(m)?

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
- `exp/`          experiment 1 (done), plot script
- `third_party/xxHash`    xxHash v0.8.3 (header-only)
- `proposal.pdf`  final project proposal

## Decisions (all former TBDs are decided in the proposal)
| Item | Decision | Why |
|---|---|---|
| Language | C++ | We both know it; `clz` bit tricks are direct |
| Hash | XXH3-64 (xxHash) | Passes chi-square / rho / bit-balance on 10^6 random AND sequential keys |
| Benchmark tool | Own small harness | Google Benchmark is not installed. Warm-up, repeated runs (median + spread), keys built outside timing, every result used (sink) |
| Real dataset | Optional extra | One public word list (e.g. a Project Gutenberg book), true count from a hash set. First thing dropped if we are late |
| Seeds | 20 | Smoke run: sd at large n = 0.79% vs theory 0.81%. Add seeds only if final intervals are too wide |
| Registers | p = 14 default, p = 4..16 in exp. 2 | 16,384 registers: theory error 0.81% |

## Experiments (from the proposal)
All points: 20 seeds, same seeds and inputs for all versions. Report mean with 95% CI (say on the plot what the bars show).

| # | x-axis | Curves | Fixed | Plot | Status |
|---|---|---|---|---|---|
| 1 | true count n (10 .. 10^7, log) | Basic HLL, HLL + LC | p = 14 | mean relative error and spread, empty-register share | done (smoke run, `results/exp1_p14.*`) |
| 2 | p (4 .. 16) | measured error vs theory 1.04/sqrt(m) | n = 10^6 | spread of error, memory | to do |
| 3 | true count n | Basic HLL, HLL + LC, hash set | p = 14 | time per item, memory | to do |

Metric: relative error (estimate - n) / n. Inputs: random 64-bit IDs with repeats. Exact answer: hash set (`std::unordered_set`).

## Status
Done: HLL code, generator, tests, hash decision and check, experiment 1 run and plot.

Still to do:
- Experiment 2 (p = 4..16) and experiment 3 (time, memory, hash set), incl. the hash set baseline and timing harness.
- Explain the handover region (about 40k-80k items at p=14): both estimators show about +2.4% error at n = 2.5m, because the raw estimate is biased upward near 2.5m and crosses the LC threshold early.
- Slide 10 example: test has a `TODO` placeholder; we need the slides to copy the exact numbers.
- Memory: we STORE 1 byte per register (16 KB at p=14); the 12 KB figure assumes packed 6-bit registers (`bytes_packed_6bit()`). Report both, and correct the slides (1.5 KB vs 12 KB, "about 2%" error vs 0.81%).
- Optional: real dataset (week 4, only if on time).
- Report and slides.

## Schedule (4 weeks)
| Week | Ibrahim | Nika | Result |
|---|---|---|---|
| 1 | Hash set baseline, input generator | HLL code and tests | Working code, TBDs decided |
| 2 | Timing setup for exp. 3 | Experiments 1 and 2 | First plots |
| 3 | Experiment 3, memory | Compare results with predictions | All main plots, list of surprises |
| 4 | Real dataset if on time | Report and slides together | Ready for the defense |
