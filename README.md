# HyperLogLog accuracy project (Ibrahim & Nika)

Advanced Algorithms & Data Structures, Fall 2026. Full plan: `proposal.pdf` (final version).

We implement HyperLogLog (HLL) from scratch and measure how accurate it is and where it stops being accurate.

Research questions:
1. How does the error change with the true count n, and does linear counting (LC, the small-count fix from HyperLogLog++) remove the error for small counts?
2. How does the number of registers (2^p) change the error, compared with the theory value 1.04/sqrt(m)?

## Build / run
    make check                         # tests + hash uniformity check
    make coverage                      # line/branch coverage of the tests (100% of src/)
    make build/exp1 build/exp2 build/exp3
    build/exp1 14 20 10000000 > results/exp1_p14.csv
    python3 exp/plot_exp1.py results/exp1_p14.csv results/exp1_p14.png
    build/exp2 20 1000000 > results/exp2_n1e6.csv && python3 exp/plot_exp2.py results/exp2_n1e6.csv results/exp2_n1e6.png
    build/exp4_real data/war_and_peace.txt 20 > results/exp4_real.csv
    python3 exp/plot_extra.py          # extra figures (how HLL works, hand-over zoom, real data, summary)
    build/exp3 21 > results/exp3_p14.csv && python3 exp/plot_exp3.py results/exp3_p14.csv results/exp3_p14.png

## Layout
- `src/hll.hpp`   HyperLogLog: `estimate_basic()`, `estimate_lc()`, `merge()`, `empty_fraction()`
- `src/gen.hpp`   input generator (random 64-bit IDs + repeats, true count known by construction)
- `tests/`        0/1/2 items, register edge cases, merge, switch rules, worked example, hand-over bias, generator vs real hash set (100% line/branch coverage of `src/`)
- `tools/hash_check.cpp`  uniformity check for the hash
- `exp/`          experiments 1-3 and their plot scripts
- `results/`      CSVs, plots, `FINDINGS.md`
- `data/`         real dataset (War and Peace, Project Gutenberg) + `SOURCE.txt`
- `report/`       HTML source of `report.pdf`, script that builds `slides.pptx`
- `report.pdf`, `slides.pptx`  final report and defense slides (`report/make_slides.py` builds the slides)
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
| 2 | p (4 .. 16) | measured error vs theory 1.04/sqrt(m) | n = 10^6 | spread of error, memory | done, `results/exp2_n1e6.*` |
| 3 | true count n | Basic HLL, HLL + LC, hash set | p = 14 | time per item, memory | done, `results/exp3_p14.*` |
| 4 (optional) | p = 8..14 | Basic HLL, HLL + LC | real text | error on distinct words of War and Peace | done, `results/exp4_real.csv` |

Metric: relative error (estimate - n) / n. Inputs: random 64-bit IDs with repeats. Exact answer: hash set (`std::unordered_set`).

## Status
Everything in the proposal is done: HLL code, generator, tests (incl. a hand-computed worked example in place of the slide-10 example, whose numbers we do not have), hash check, experiments 1-3, the optional real dataset (exp. 4), `results/FINDINGS.md`, `report.pdf` and `slides.pptx` (with the slide corrections: 12 KB not 1.5 KB; 0.81% not about 2%).

Known limits / optional follow-ups:
- Timings: final run plugged in, other programs closed (an earlier battery run agreed closely).
- If the original slide 10 differs from our worked example, change the numbers in `test_worked_example()`.

Memory note: we STORE 1 byte per register (16 KB at p=14); the 12 KB figure assumes packed 6-bit registers (`bytes_packed_6bit()`). Both are reported.

## Schedule (4 weeks)
| Week | Ibrahim | Nika | Result |
|---|---|---|---|
| 1 | Hash set baseline, input generator | HLL code and tests | Working code, TBDs decided |
| 2 | Timing setup for exp. 3 | Experiments 1 and 2 | First plots |
| 3 | Experiment 3, memory | Compare results with predictions | All main plots, list of surprises |
| 4 | Real dataset if on time | Report and slides together | Ready for the defense |
