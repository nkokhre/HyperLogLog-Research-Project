# Findings so far (p=14 unless noted; 20 seeds; numbers from results/*.csv)

## Exp 1 - error vs n (results/exp1_p14.*)
- Basic HLL at n=1000: +1130% (12.3x too big), as predicted. LC: -0.05% mean, sd 0.56% (prediction "about 1%": confirmed).
- Large n (>= 10^6): mean error ~0 (|mean| < 0.25%), sd 0.64-0.93% around theory 0.81%. Independent of n: confirmed.
- Empty-register share follows e^(-n/m) almost exactly.
- SURPRISE (handover): for n/m in [2.5, ~4.5] (n = 41k..74k) both estimators have a positive bias:
  +2.4% at n=2.5m, +1.0% at 3.1m, +0.3% at 3.75m, ~0 from ~4.5m (n ~ 74k).
  Cause: the raw formula is biased upward in this range. The LC switch tests the *raw estimate* <= 2.5m, and because
  the raw estimate is biased up, it already exceeds 2.5m when the true n is about 2.5m, so LC is switched off while the
  bias is still there (lc_used_share drops from 1.00 at n/m=2.19 to 0.00 at n/m=2.50). Just below, LC is unbiased
  (-0.13% at 2.19m). A jump of about +2.4% appears at the switch, roughly 3 standard deviations of the 0.8% noise.
  HyperLogLog++ fixes this range with an empirical bias-correction table; we do not.

## Exp 2 - error vs p, n=10^6 (results/exp2_n1e6.*)
- Measured sd follows 1.04/sqrt(m): ratio measured/theory is 0.64-1.12 for p=4..16 (p=14: 0.865% vs 0.812%, ratio 1.07);
  theory lies inside the 95% CI of the std for every p.
- For tiny sketches (m <= 64) there is a negative bias (-3.5% .. -5.6%) in addition to the spread; theory 1.04/sqrt(m) is asymptotic.
- LC and basic are identical here (n=10^6 >> 2.5m for all p).
- Memory (packed 6-bit): 12 B at p=4 ... 12 KB at p=14 ... 48 KB at p=16. Stored (1 byte/register): 16 KB at p=14.

## Exp 3 - time and memory (results/exp3_p14.*; 21 runs, median)
- Update cost per item: HLL 1.2-3.7 ns, hash set 23-208 ns (grows with n: cache misses).
  HLL is 8-17x faster at n=1000..100k, 57x at 10^6 and ~170x at 10^7.
- HLL per-item time FALLS for large n (3.6 ns at 1e5 -> 1.2 ns at 1e7): late in the stream almost no register
  changes, so the update branch is predictable.
- Linear counting does not slow the update (same add()). The estimate step costs ~28 us per call for both versions;
  LC adds ~1 us at n=1000 (counting empties) and 0 at larger n. Per-item numbers for LC in the plot include one estimate,
  which is why they are higher at small n (fixed 28 us / few items).
- Memory: HLL 16 KB stored / 12 KB packed at every n. Hash set (exact bytes requested from allocator):
  36 KB (n=1e3), 3.2 MB (1e5), 37 MB (1e6), 345 MB (1e7) -> 2x..21,000x larger than the stored sketch.

## Exp 4 - real data: distinct words in War and Peace (results/exp4_real.csv)
583,368 words, 17,445 distinct. p=14 (n/m=1.06): basic +27.85%, LC -0.18% (sd 0.72%, theory 0.81%);
p=13 (n/m=2.13): basic +4.21%, LC -0.50%; p<=12 (n/m>=4): both ~0 with sd close to 1.04/sqrt(m). Same picture as synthetic data.

## Caveats
- Exp 1 snapshots of one seed share a stream (correlated across n).
- Timing: single machine run; keep it plugged in / other programs closed when re-running for the final report.
- Timings: final run plugged in, other programs closed (an earlier run on battery agreed closely). One machine only.
