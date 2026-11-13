"""Plot experiment 1. Usage: python3 plot_exp1.py results/exp1_p14.csv out.png"""
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

df = pd.read_csv(sys.argv[1])
out = sys.argv[2]
m = int(df.m.iloc[0])
theory = 1.04 / np.sqrt(m)
df["err_basic"] = (df.est_basic - df.n) / df.n
df["err_lc"] = (df.est_lc - df.n) / df.n

g = df.groupby("n")
seeds = g.seed.nunique().iloc[0]
tcrit = stats.t.ppf(0.975, seeds - 1)
def mean_ci(col):
    mu, sd = g[col].mean(), g[col].std(ddof=1)
    return mu, tcrit * sd / np.sqrt(seeds), sd
mb, cb, sb = mean_ci("err_basic")
ml, cl, sl = mean_ci("err_lc")
ns = mb.index.values
hand = 2.5 * m

fig, ax = plt.subplots(1, 3, figsize=(17, 4.8))
ax[0].errorbar(ns, mb * 100, cb * 100, fmt="o-", ms=3, capsize=2, label="Basic HLL")
ax[0].errorbar(ns, ml * 100, cl * 100, fmt="s-", ms=3, capsize=2, label="HLL + linear counting")
ax[0].set_xscale("log"); ax[0].set_yscale("symlog", linthresh=1)
ax[0].axvline(hand, ls=":", c="gray", label=f"switch point 2.5m = {int(hand):,}")
ax[0].set_xlabel("true count n"); ax[0].set_ylabel("mean relative error (%)")
ax[0].set_title(f"(a) Mean error, p={int(np.log2(m))}; bars = 95% CI of mean ({seeds} seeds)")
ax[0].legend()

ax[1].plot(ns, sb * 100, "o-", ms=3, label="Basic HLL")
ax[1].plot(ns, sl * 100, "s-", ms=3, label="HLL + linear counting")
ax[1].axhline(theory * 100, c="k", ls="--", label=f"theory 1.04/√m = {theory*100:.2f}%")
ax[1].set_xscale("log"); ax[1].set_yscale("log")
ax[1].axvline(hand, ls=":", c="gray", label="switch point 2.5m")
ax[1].set_xlabel("true count n"); ax[1].set_ylabel("std. dev. of relative error (%)")
ax[1].set_title("(b) Spread of the error (std over seeds)"); ax[1].legend()

ax[2].plot(ns, g.empty_frac.mean(), "o-", ms=3, label="measured")
ax[2].plot(ns, np.exp(-ns / m), "k--", label="theory e^(-n/m)")
ax[2].set_xscale("log"); ax[2].set_yscale("log"); ax[2].set_ylim(1e-5, 1.5)
ax[2].axvline(hand, ls=":", c="gray", label="switch point 2.5m")
ax[2].set_xlabel("true count n"); ax[2].set_ylabel("share of empty registers")
ax[2].set_title("(c) Empty registers"); ax[2].legend()
plt.tight_layout(); plt.savefig(out, dpi=140)

# numbers for the report
pd.set_option("display.width", 200)
tab = pd.DataFrame({"mean_basic%": mb * 100, "mean_lc%": ml * 100,
                    "sd_basic%": sb * 100, "sd_lc%": sl * 100,
                    "empty": g.empty_frac.mean()})
print(f"theory sigma = {theory*100:.3f}%, 2.5m = {hand:.0f}")
print(tab.round(3).to_string())
big = ns >= 4 * hand
print(f"\nn >= 4*2.5m: pooled sd basic {np.sqrt((sb[big]**2).mean())*100:.3f}%, "
      f"lc {np.sqrt((sl[big]**2).mean())*100:.3f}%")
