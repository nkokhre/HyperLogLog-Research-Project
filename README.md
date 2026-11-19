# When does linear counting stop helping HyperLogLog? (Ibrahim & Nika)

Advanced Algorithms & Data Structures, Fall 2026.

**Goal.** At what number of distinct items n does plain HyperLogLog (HLL) become accurate enough that linear counting (LC)
no longer helps, and below which is HLL + linear counting better? With m = 2^p registers we express the border as a ratio
**c\* = n\*/m** (items per register, i.e. how full the sketch is), test whether one value of c\* works for every p,
and compare the best observable switch rule (it may only use the raw estimate E and the empty registers V) with the
textbook rule "use LC when E ≤ 2.5·m and V > 0".

**Result** (`results/FINDINGS.md`, section 1). The crossover is **not** constant: c\* = 2.09, 2.45, 2.80, 3.12, 3.46 for
p = 8, 10, 12, 14, 16 (95% CIs ±0.05 to ±0.09). So the hypothesis "one fixed threshold ≈ 2.5 fits every size" is rejected.
Switching at c(p)·m with c(p) = 1.53 + 0.1325·p instead of 2.5·m gives no gain at p = 8. At p = 14 it cuts the worst-case error
from 2.71% to 1.21% and the hand-over bump from 2.48% to 0.56%. Larger sketches gain more.

Deliverables: `slides.html` (defense deck), `report.pdf` (report), `proposal.pdf` (proposal, updated to this goal).

## Build / run
Needs a C++17 compiler and Python 3 with `numpy pandas scipy matplotlib` (`pip3 install numpy pandas scipy matplotlib`).
The PDFs are printed with Google Chrome.

    make check              # C++ tests + hash uniformity check
    make check-analysis     # tests of the crossover analysis (Python)
    make coverage           # line/branch coverage of src/ (macOS clang; 100%)
    make exp5-run           # MAIN experiment: exp5 + exp6 -> analysis -> plots -> slides.html  (~1 min)
    make slides             # rebuild slides.html from results/*.csv
    make pdfs               # rebuild report.pdf and proposal.pdf from report/*.html

Supporting experiments (background, see FINDINGS section 2):

    make all
    build/exp1 14 20 10000000 > results/exp1_p14.csv && python3 exp/plot_exp1.py results/exp1_p14.csv results/exp1_p14.png
    build/exp2 20 1000000 > results/exp2_n1e6.csv && python3 exp/plot_exp2.py results/exp2_n1e6.csv results/exp2_n1e6.png
    build/exp3 21 > results/exp3_p14.csv && python3 exp/plot_exp3.py results/exp3_p14.csv results/exp3_p14.png   # timing: plug in, close other programs
    build/exp4_real data/war_and_peace.txt 20 > results/exp4_real.csv

**Slides:** open `slides.html` in a browser, or in VS Code right-click it and choose "Open with Live Server".
Keys: → / space next, ← back, **N** speaker notes (with a walkthrough for every graph and the source file of every number), **P** print view.

## Layout
- `src/hll.hpp`: HyperLogLog. It provides `estimate_basic()` (plain HLL) and `estimate_lc()` (textbook rule, unchanged). It also provides `estimate_lc_only()` (pure LC), `estimate_switch(c)` and `estimate_switch_empty(f)` (switch rules), `merge()`, `empty_fraction()` and `bytes_packed_6bit()`.
- `src/gen.hpp`: input generator. It produces random 64-bit IDs with repeats, so the true count is known by construction.
- `tests/`: `test_hll.cpp` gives 100% line and branch coverage of `src/`. `test_analysis.py` tests the crossover finder and the switch rules.
- `tools/hash_check.cpp`: uniformity check for the hash.
- `exp/`
  - `exp5_crossover.cpp` (main experiment), `exp6_real_crossover.cpp` (real text), `analyze_exp5.py` (crossover, CIs, threshold scan, rules), `plot_exp5.py` (plots A–E), `plot_schematics.py` (build-up illustrations).
  - Supporting: `exp1`–`exp4` with their plot scripts, and `plot_extra.py` (memory and speed figure).
- `results/`: CSVs, plots, `FINDINGS.md`. The raw data of exp5 and exp6 is gzipped.
- `data/`: War and Peace (Project Gutenberg #2600, public domain) and `SOURCE.txt`.
- `report/`: `report.html` and `proposal.html` (sources of the PDFs), `make_slides.py` (builds `slides.html`).
- `third_party/xxHash`: `xxhash.h` and the license of xxHash v0.8.3 (header-only).

## Experiments
| # | role | what | output |
|---|---|---|---|
| 5 | **MAIN** | p = 8…16 × 93 values of n/m in 0.25…8 × 500 runs. It measures plain HLL vs LC, the crossover c\* with a bootstrap CI, a scan over switch thresholds, and the best rule vs the textbook rule. The best rule is chosen on half of the runs and evaluated on the other half. | `results/exp5_*.csv`, `exp5_*.png` |
| 6 | main (sanity) | The same crossover on real text: words of War and Peace in their order, 200 hash seeds, p = 8, 10, 12. | `results/exp6_*.csv` |
| 1 | background | Error vs n at p = 14 (basic vs textbook LC), 20 seeds. | `results/exp1_p14.*` |
| 2 | background | Error vs p at n = 10^6 against 1.04/√m, 20 seeds. | `results/exp2_n1e6.*` |
| 3 | background | Time per item and memory: HLL vs `std::unordered_set`. | `results/exp3_p14.*`, `fig_summary.png` |
| 4 | background | Error on the full War and Peace text, p = 8…14. | `results/exp4_real.csv` |

Terms (the same everywhere):
- **Typical error** is the root-mean-square of (estimate − n)/n over the runs.
- **Crossover c\*** is the smallest n/m after which plain HLL's typical error stays ≤ LC's.
- **Worst case** is the largest typical error on n/m = 0.25…8.
- **Hand-over bump** is the largest average error (bias) on that range.
- **Switch threshold c** means: use LC while E ≤ c·m and V > 0.

## Decisions
| Item | Decision |
|---|---|
| Language | C++ (library and experiments), Python only for analysis and plots |
| Hash | XXH3-64, with a different seed per run. It passes chi-square, rho and bit-balance on 10^6 random and sequential keys. |
| Seeds | 500 per point in exp5 (20 is too few to locate a crossover); 200 hash seeds in exp6; 20 in exp1–4 |
| LC when V = 0 | V is clamped to 1, so LC is capped at m·ln m |
| Benchmark | own harness (warm-up, 21 repeats, median, keys built outside the timing) |

## Status
Done: library, tests (100% coverage of `src/`), all experiments, FINDINGS, report, proposal and slides (23 main + 4 backup).
Limits: random IDs and one text, one hash, p = 8…16, and the n/m grid only goes up to 8. Our code stores 1 byte per register (16 KB at p = 14); the 12 KB figure is for packed 6-bit registers.
The slide-10 test (`test_worked_example()`) uses our own hand-computed example, because we do not have the original slide's numbers.
