"""Plot experiment 2. Usage: python3 plot_exp2.py results/exp2_n1e6.csv out.png"""
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

df = pd.read_csv(sys.argv[1]); out = sys.argv[2]
n = int(df.n.iloc[0])
df["err_basic"] = (df.est_basic - n) / n
df["err_lc"] = (df.est_lc - n) / n
g = df.groupby("p")
seeds = g.seed.nunique().iloc[0]
ps = g.m.first().index.values
m = g.m.first().values
theory = 1.04 / np.sqrt(m)
sd = g.err_lc.std(ddof=1).values
mean = g.err_lc.mean().values
rms = np.sqrt(g.err_lc.apply(lambda x: (x ** 2).mean())).values  # RMS error (includes bias)
# 95% CI of the std (chi-square)
lo = sd * np.sqrt((seeds - 1) / stats.chi2.ppf(0.975, seeds - 1))
hi = sd * np.sqrt((seeds - 1) / stats.chi2.ppf(0.025, seeds - 1))

fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
ax[0].errorbar(ps, sd * 100, [(sd - lo) * 100, (hi - sd) * 100], fmt="o-", capsize=3,
               label=f"measured std of rel. error ({seeds} seeds)")
ax[0].plot(ps, theory * 100, "k--", label="theory 1.04/√m")
ax[0].set_yscale("log"); ax[0].set_xlabel("p  (m = 2^p registers)")
ax[0].set_ylabel("std. dev. of relative error (%)")
ax[0].set_title(f"(a) Error vs registers, n = {n:,}; bars = 95% CI of the std")
ax[0].legend()
ax[1].plot(ps, g.bytes_packed6.first() / 1024, "s-", label="packed 6-bit (theory)")
ax[1].plot(ps, g.bytes_stored.first() / 1024, "o-", label="stored (1 byte/register)")
ax[1].set_yscale("log"); ax[1].set_xlabel("p"); ax[1].set_ylabel("memory (KB)")
ax[1].set_title("(b) Memory of the sketch"); ax[1].legend()
plt.tight_layout(); plt.savefig(out, dpi=140)

pd.set_option("display.width", 200)
tab = pd.DataFrame({"m": m, "sd%": sd * 100, "ci_lo%": lo * 100, "ci_hi%": hi * 100,
                    "theory%": theory * 100, "ratio": sd / theory,
                    "mean%": mean * 100, "rms%": rms * 100,
                    "packedKB": g.bytes_packed6.first().values / 1024}, index=ps)
print(tab.round(3).to_string())
# basic vs lc identical at n=1e6?
print("max |basic-lc| diff:", (df.est_basic - df.est_lc).abs().max())
