# Findings

All numbers come from files in `results/`. Section 1 is the main result of the project; section 2 is background
from the first phase (still correct, but it answers the earlier, broader questions).

## 1. MAIN: the crossover between linear counting and plain HLL (experiments 5 and 6)

**Goal.** At what number of distinct items n does plain HyperLogLog become accurate enough that linear counting no
longer helps, and below which is HLL + linear counting better? We express the border as c* = n*/m (m = 2^p registers).

**Definitions** (identical in README, report and slides; implemented in `exp/analyze_exp5.py`):
- error of one estimate = (estimate − n) / n; **typical error** = root-mean-square of that error over the runs.
- **plain HLL** = `estimate_basic()`; **linear counting (LC)** = `estimate_lc_only()` = m·ln(m/V), V clamped to ≥ 1.
- **crossover c\*** = smallest n/m after which plain HLL's typical error stays ≤ LC's for every larger n/m
  (linear interpolation between grid points); 95% CI by bootstrap over runs (1,000 resamples).
- **switch rule with threshold c** = `estimate_switch(c)`: LC if the raw estimate E ≤ c·m and V > 0, else E.
  **Textbook 2.5m rule** = c = 2.5 = `estimate_lc()` (unchanged default).
- **worst case** = largest typical error anywhere on n/m = 0.25 … 8.
- **hand-over bump** = largest |average error| (bias) anywhere on n/m = 0.25 … 8; for the switch rules it sits at the switch.
- **best rule** = threshold c with the lowest worst case on half of the runs (odd seeds); all comparisons below are
  measured on the other half (even seeds, 250 runs), CIs by bootstrap over those runs.

**Setup.** p = 8, 10, 12, 14, 16; 93 values of n/m from 0.25 to 8 (step 0.125 up to 1.5, 0.05 from 1.5 to 5,
0.25 from 5 to 8); 500 runs per point; the same sketches feed every method. Raw data: `results/exp5_raw.csv.gz`
(`build/exp5_crossover 500 8,10,12,14,16`), aggregates: `results/exp5_*.csv` (`python3 exp/analyze_exp5.py`).

### 1.1 The crossover grows with the sketch size (`exp5_crossover.csv`, `exp5_best_threshold.csv`)

| p | m | c* | 95% CI | n* (items) | simple model c* | best switch c (train half) | 95% CI | best empty-share f |
|---|---|---|---|---|---|---|---|---|
| 8 | 256 | 2.09 | 2.00–2.17 | 535 | 2.33 | 2.50 | 2.25–2.90 | 0.075 |
| 10 | 1,024 | 2.45 | 2.39–2.50 | 2,512 | 2.54 | 2.90 | 2.55–2.95 | 0.065 |
| 12 | 4,096 | 2.80 | 2.74–2.85 | 11,459 | 2.89 | 3.20 | 3.05–3.28 | 0.050 |
| 14 | 16,384 | 3.12 | 3.08–3.18 | 51,200 | 3.18 | 3.45 | 3.15–3.55 | 0.035 |
| 16 | 65,536 | 3.46 | 3.40–3.51 | 226,521 | 3.46 | 3.55 | 3.50–3.65 | 0.030 |

- **Hypothesis "one fixed c\* ≈ 2.5 works for every p": rejected.** The intervals do not overlap; c\* rises by about
  0.17 per extra bit of p. Measuring in n/m still removes most of the size dependence (n\* spans 535 to 226,521 items,
  a factor of ~420, while c\* only spans 2.09 to 3.46).
- Why: plain HLL's average over-estimate at a given n/m is (almost) the same for every m (e.g. +5.5% at n/m = 2 and
  +2.4% at n/m = 2.5 for p ≥ 10, `exp5_curves.csv` column bias_raw), while the random error of LC shrinks like 1/√m.
  A bigger sketch therefore keeps LC better for longer. A simple model — raw typical error² = bias(n/m)² + (raw noise)²,
  LC typical error² = (e^t − t − 1)/(t² m) — reproduces c\* within 0.09 for p ≥ 10 (column c_star_model; 0.24 off at p = 8).
- At the crossover only e^(−c\*) of the registers are still empty (4.4% at p = 14, `exp5_curves.csv` empty_frac),
  which is why LC loses: it has almost no empty registers left to read.
- The textbook 2.5 is close to c\* only for small sketches (p = 10: 2.45).
- The best observable switch place is a bit later than c\* (for p ≥ 10). Fitted line (train half only):
  **c(p) = 1.53 + 0.1325·p** (`exp5_formula.csv`). The empty-share rule (LC while V/m > f) performs about as well.

### 1.2 Impact: worst case and hand-over bump (`exp5_rules.csv`, test half, 250 runs, 95% CIs)

| p | rule | switch | worst case % | hand-over bump % | worst case ÷ textbook | bump ÷ textbook |
|---|---|---|---|---|---|---|
| 8 | textbook 2.5 | 2.50 | 7.21 (6.80–7.77) | 1.84 (1.24–2.54) | – | – |
| 8 | best c | 2.50 | 7.21 (6.80–7.77) | 1.84 (1.24–2.54) | 1.00 | 1.00 |
| 8 | formula c(p) | 2.59 | 7.05 (6.69–7.65) | 1.72 (1.10–2.40) | 0.98 (0.96–1.01) | 0.93 (0.83–1.04) |
| 10 | textbook 2.5 | 2.50 | 4.11 (3.88–4.36) | 2.18 (1.83–2.50) | – | – |
| 10 | best c | 2.90 | 3.89 (3.62–4.21) | 0.94 (0.60–1.33) | 0.96 (0.89–1.02) | 0.44 (0.31–0.55) |
| 10 | formula c(p) | 2.86 | 3.92 (3.58–4.26) | 1.02 (0.70–1.41) | 0.96 (0.88–1.03) | 0.48 (0.36–0.59) |
| 12 | textbook 2.5 | 2.50 | 2.93 (2.77–3.07) | 2.30 (2.12–2.47) | – | – |
| 12 | best c | 3.20 | 2.12 (1.98–2.29) | 0.61 (0.43–0.80) | 0.73 (0.67–0.79) | 0.27 (0.20–0.33) |
| 12 | formula c(p) | 3.12 | 2.16 (1.98–2.33) | 0.71 (0.54–0.87) | 0.74 (0.68–0.79) | 0.31 (0.24–0.36) |
| 14 | textbook 2.5 | 2.50 | 2.71 (2.61–2.79) | 2.48 (2.39–2.55) | – | – |
| 14 | best c | 3.45 | 1.26 (1.16–1.36) | 0.50 (0.41–0.59) | 0.47 (0.43–0.50) | 0.20 (0.17–0.23) |
| 14 | formula c(p) | 3.38 | 1.21 (1.13–1.34) | 0.56 (0.46–0.66) | 0.45 (0.42–0.49) | 0.23 (0.19–0.26) |
| 16 | textbook 2.5 | 2.50 | 2.65 (2.61–2.69) | 2.60 (2.53–2.66) | – | – |
| 16 | best c | 3.55 | 0.60 (0.57–0.66) | 0.34 (0.30–0.38) | 0.23 (0.21–0.25) | 0.13 (0.12–0.15) |
| 16 | formula c(p) | 3.65 | 0.62 (0.58–0.68) | 0.28 (0.23–0.32) | 0.24 (0.22–0.26) | 0.11 (0.09–0.12) |

- Plain HLL alone has a worst case of 238–239% for every p (at n/m = 0.25), so any switch rule is a huge improvement
  over it; the interesting comparison is textbook vs best.
- p = 8: the textbook rule is already the best threshold on the grid; no gain.
- p = 10: the worst case does not improve significantly (ratio CI includes 1), but the hand-over bump halves.
- p = 12–16: the best switch place cuts the worst case by 27% to 77% and the hand-over bump by 73% to 87%; all CIs exclude 1.
  At p = 14 the worst case drops from 2.71% to 1.26% and the bump from 2.48% to 0.50%.
- The one-line formula c(p) is as good as the per-p best choice (overlapping CIs at every p).

### 1.3 Sanity checks
- **Theory at large counts** (`exp5_curves.csv`, n/m = 8): plain HLL's typical error / (1.04/√m) = 0.96, 0.91, 0.98,
  0.97, 0.91 for p = 8 … 16 — close to theory (slightly below it at n/m = 8).
- **Real text** (experiment 6, War and Peace, 583,368 words, 17,445 distinct; words in their real order; 200 hash seeds;
  `exp6_real_crossover.csv`): c\* = 2.48 (2.40–2.58) at p = 10 and 2.77 (2.69–2.85) at p = 12, against 2.45 and 2.80
  on random IDs. At p = 8 c\* = 1.99 with a wide CI (1.92–5.55): one fixed text gives a noisy small sketch. p = 14/16
  are not possible (the text has only 17,445 distinct words, and p = 12 already stops at n/m = 4.25).

### 1.4 Limits
- Random 64-bit IDs and one real text; one hash (XXH3-64); p = 8 … 16 only; n/m grid up to 8.
- Worst case and bump are taken over n/m = 0.25 … 8; other ranges can give other best thresholds.
- Our code stores 1 byte per register (16 KB at p = 14); the 12 KB figure is for packed 6-bit registers.

## 2. BACKGROUND: first-phase experiments (1–4)


### Exp 1 - error vs n (results/exp1_p14.*)
- Basic HLL at n=1000: +1130% (12.3x too big), as predicted. LC: -0.05% mean, sd 0.56% (prediction "about 1%": confirmed).
- Large n (>= 10^6): mean error ~0 (|mean| < 0.25%), sd 0.64-0.93% around theory 0.81%. Independent of n: confirmed.
- Empty-register share follows e^(-n/m) almost exactly.
- SURPRISE (handover): for n/m in [2.5, ~4.5] (n = 41k..74k) both estimators have a positive bias:
  +2.4% at n=2.5m, +1.0% at 3.1m, +0.3% at 3.75m, ~0 from ~4.5m (n ~ 74k).
  Cause: the raw formula is biased upward in this range. The LC switch tests the *raw estimate* <= 2.5m, and because
  the raw estimate is biased up, it already exceeds 2.5m when the true n is about 2.5m, so LC is switched off while the
  bias is still there (lc_used_share drops from 1.00 at n/m=2.19 to 0.00 at n/m=2.50). Just below, LC is unbiased
  (-0.13% at 2.19m). A jump of about +2.4% appears at the switch, roughly 3 standard deviations of the 0.8% noise.
  We describe this effect but do not correct it.

### Exp 2 - error vs p, n=10^6 (results/exp2_n1e6.*)
- Measured sd follows 1.04/sqrt(m): ratio measured/theory is 0.64-1.12 for p=4..16 (p=14: 0.865% vs 0.812%, ratio 1.07);
  theory lies inside the 95% CI of the std for every p.
- For tiny sketches (m <= 64) there is a negative bias (-3.5% .. -5.6%) in addition to the spread; theory 1.04/sqrt(m) is asymptotic.
- LC and basic are identical here (n=10^6 >> 2.5m for all p).
- Memory (packed 6-bit): 12 B at p=4 ... 12 KB at p=14 ... 48 KB at p=16. Stored (1 byte/register): 16 KB at p=14.

### Exp 3 - time and memory (results/exp3_p14.*; 21 runs, median)
- Update cost per item: HLL 1.2-3.7 ns, hash set 23-208 ns (grows with n: cache misses).
  HLL is 8-17x faster at n=1000..100k, 57x at 10^6 and ~170x at 10^7.
- HLL per-item time FALLS for large n (3.6 ns at 1e5 -> 1.2 ns at 1e7): late in the stream almost no register
  changes, so the update branch is predictable.
- Linear counting does not slow the update (same add()). The estimate step costs ~28 us per call for both versions;
  LC adds ~1 us at n=1000 (counting empties) and 0 at larger n. Per-item numbers for LC in the plot include one estimate,
  which is why they are higher at small n (fixed 28 us / few items).
- Memory: HLL 16 KB stored / 12 KB packed at every n. Hash set (exact bytes requested from allocator):
  36 KB (n=1e3), 3.2 MB (1e5), 37 MB (1e6), 345 MB (1e7) -> 2x..21,000x larger than the stored sketch.

### Exp 4 - real data: distinct words in War and Peace (results/exp4_real.csv)
583,368 words, 17,445 distinct. p=14 (n/m=1.06): basic +27.85%, LC -0.18% (sd 0.72%, theory 0.81%);
p=13 (n/m=2.13): basic +4.21%, LC -0.50%; p<=12 (n/m>=4): both ~0 with sd close to 1.04/sqrt(m). Same picture as synthetic data.

### Caveats (experiments 1–4)
- Exp 1 snapshots of one seed share a stream (correlated across n).
- Timings: final run plugged in, other programs closed (an earlier run on battery agreed closely). One machine only.
