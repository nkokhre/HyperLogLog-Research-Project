"""Plots A-E for experiment 5 (crossover). Run after exp/analyze_exp5.py.
Usage (from project root):  python3 exp/plot_exp5.py

Colour code used in EVERY plot and slide:
  Plain (raw) HLL = blue, linear counting (LC) = orange, textbook 2.5m rule = purple, best rule = green.
Plain-language axis labels, direct curve labels (no legends), zones/crossover marked on the plot.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
RAW, LC, TEXT, BEST, INK, GRAYC = "#1f77b4", "#ff7f0e", "#8e44ad", "#2e7d32", "#222222", "#777777"
plt.rcParams.update({"font.size": 15, "axes.labelsize": 16, "axes.titlesize": 17, "xtick.labelsize": 15,
                     "ytick.labelsize": 15, "axes.spines.top": False, "axes.spines.right": False,
                     "lines.linewidth": 3.2, "figure.dpi": 100, "savefig.dpi": 200})

cur = pd.read_csv(os.path.join(RES, "exp5_curves.csv"))
cross = pd.read_csv(os.path.join(RES, "exp5_crossover.csv")).set_index("p")
scan = pd.read_csv(os.path.join(RES, "exp5_scan.csv"))
rules = pd.read_csv(os.path.join(RES, "exp5_rules.csv"))
bestc = pd.read_csv(os.path.join(RES, "exp5_best_threshold.csv")).set_index("p")
P0 = 14
M0 = 2 ** P0
SEEDS = int(cur.seeds.iloc[0])
XT = [0.25, 0.5, 1, 2, 4, 8]


def xaxis_nm(ax, label="Items per register  (n / m, log scale)"):
    ax.set_xscale("log"); ax.set_xlim(0.25, 8)
    ax.xaxis.set_major_locator(FixedLocator(XT)); ax.xaxis.set_major_formatter(FixedFormatter([str(x) for x in XT]))
    ax.xaxis.set_minor_locator(NullLocator()); ax.set_xlabel(label)


def yaxis_err(ax, lo=0.2, hi=400):
    ax.set_yscale("log"); ax.set_ylim(lo, hi)
    ticks = [t for t in (0.1, 1, 10, 100) if lo <= t <= hi]
    ax.yaxis.set_major_locator(FixedLocator(ticks)); ax.yaxis.set_major_formatter(FixedFormatter([f"{t:g}%" for t in ticks]))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_ylabel("Typical error of the estimate\n(log scale: each gridline = 10×)")


def top_axis_n(ax, m=M0):
    sec = ax.secondary_xaxis("top", functions=(lambda t: t * m, lambda n: n / m))
    ns = [m // 4, m // 2, m, 2 * m, 4 * m, 8 * m]
    sec.xaxis.set_major_locator(FixedLocator(ns)); sec.xaxis.set_major_formatter(FixedFormatter([f"{n:,}" for n in ns]))
    sec.xaxis.set_minor_locator(NullLocator())
    sec.set_xlabel(f"Number of distinct items n  (for p = {int(np.log2(m))}: m = {m:,} registers)", fontsize=14)
    sec.tick_params(labelsize=13)
    return sec


def curves_p(p):
    d = cur[cur.p == p].sort_values("n_over_m")
    return d


def plot_a_p14(annotated, fname):
    d = curves_p(P0)
    t = d.n_over_m.values
    fig, ax = plt.subplots(figsize=(12.5, 6.4))
    cs = cross.loc[P0, "c_star"]
    if annotated:
        ax.axvspan(0.25, cs, color=LC, alpha=0.09, lw=0)
        ax.axvspan(cs, 8, color=RAW, alpha=0.09, lw=0)
    ax.fill_between(t, d.rmse_raw_ci_lo * 100, d.rmse_raw_ci_hi * 100, color=RAW, alpha=0.25, lw=0)
    ax.fill_between(t, d.rmse_lc_ci_lo * 100, d.rmse_lc_ci_hi * 100, color=LC, alpha=0.25, lw=0)
    ax.plot(t, d.rmse_raw * 100, color=RAW)
    ax.plot(t, d.rmse_lc * 100, color=LC)
    xaxis_nm(ax); yaxis_err(ax)
    ax.text(0.31, 60, "Plain HLL", color=RAW, fontsize=19, fontweight="bold", ha="left")
    ax.text(4.2, 3.6, "Linear\ncounting", color=LC, fontsize=19, fontweight="bold", ha="left", va="bottom")
    if annotated:
        ax.axvline(cs, color=INK, lw=2.4, ls="--")
        lo, hi = cross.loc[P0, "ci_lo"], cross.loc[P0, "ci_hi"]
        ax.axvspan(lo, hi, color=INK, alpha=0.25, lw=0)
        ax.text(0.27, 0.27, "Linear counting\nis better", color="#b35a00", fontsize=17, fontweight="bold", va="bottom")
        ax.text(6.9, 0.27, "Plain HLL\nis better", color="#124e78", fontsize=17, fontweight="bold", ha="right", va="bottom")
        ax.annotate(f"Crossover: {cs:.2f} items per register\n≈ {cs * M0:,.0f} items  (95% CI {lo:.2f} to {hi:.2f})",
                    xy=(cs, 1.5), xytext=(0.28, 9), fontsize=16, color=INK, fontweight="bold",
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.2))
    top_axis_n(ax)
    ax.text(0.995, -0.2, f"shaded bands around the lines = 95% confidence interval over {SEEDS} runs",
            transform=ax.transAxes, ha="right", fontsize=12.5, color=GRAYC)
    plt.tight_layout(); plt.savefig(os.path.join(RES, fname)); plt.close()


def plot_a_allp(fname):
    ps = sorted(cross.index)
    shade = np.linspace(1.0, 0.45, len(ps))
    fig, ax = plt.subplots(1, 2, figsize=(14.5, 6.2), sharey=True)
    for k, a in enumerate(ax):
        for i, p in enumerate(ps):
            d = curves_p(p); m = 2 ** p
            x = d.n.values if k == 0 else d.n_over_m.values
            a.plot(x, d.rmse_raw * 100, color=RAW, lw=1.9, alpha=0.45 + 0.55 * (i / (len(ps) - 1)))
            a.plot(x, d.rmse_lc * 100, color=LC, lw=1.9, alpha=0.45 + 0.55 * (i / (len(ps) - 1)))
            cs = cross.loc[p, "c_star"]
            xc = cs * m if k == 0 else cs
            yc = np.interp(cs, d.n_over_m.values, d.rmse_raw.values) * 100
            a.plot([xc], [yc], "o", color=INK, ms=9, zorder=5)
            a.annotate(f"p={p}", (xc, yc), xytext=(4, -22 if k == 0 else 12), textcoords="offset points", fontsize=13, fontweight="bold")
        a.set_yscale("log"); a.set_ylim(0.15, 400)
        a.xaxis.set_minor_locator(NullLocator()); a.yaxis.set_minor_locator(NullLocator())
    ax[0].set_xscale("log"); ax[0].set_xlabel("Number of distinct items  n  (log scale)")
    ax[0].xaxis.set_major_locator(FixedLocator([100, 1000, 1e4, 1e5, 1e6])); ax[0].xaxis.set_major_formatter(FixedFormatter(["100", "1,000", "10,000", "100,000", "1,000,000"]))
    ax[0].set_xlim(60, 6e5)
    xaxis_nm(ax[1])
    ax[0].yaxis.set_major_locator(FixedLocator([1, 10, 100])); ax[0].yaxis.set_major_formatter(FixedFormatter(["1%", "10%", "100%"]))
    ax[0].set_ylabel("Typical error of the estimate\n(log scale: each gridline = 10×)")
    lo_n, hi_n = cross.n_star.min(), cross.n_star.max(); lo_c, hi_c = cross.c_star.min(), cross.c_star.max()
    ax[0].set_title(f"x-axis = number of items n:\ncrossovers (dots) range from {lo_n:,.0f} to {hi_n:,.0f}", fontsize=16)
    ax[1].set_title(f"x-axis = items per register n/m:\ncrossovers (dots) stay between {lo_c:.1f} and {hi_c:.1f}", fontsize=16)
    ax[1].text(0.3, 90, "blue = plain HLL, orange = linear counting\n(one thin line per sketch size, p = 8 … 16)", fontsize=13.5, color=INK)
    plt.tight_layout(); plt.savefig(os.path.join(RES, fname)); plt.close()


def plot_b(fname):
    ps = sorted(cross.index)
    fig, ax = plt.subplots(figsize=(11.5, 6.2))
    x = np.arange(len(ps))
    c = cross.loc[ps, "c_star"].values; lo = cross.loc[ps, "ci_lo"].values; hi = cross.loc[ps, "ci_hi"].values
    ax.axhline(2.5, color=TEXT, lw=3, ls="--")
    ax.text(len(ps) - 0.55, 2.5 - 0.06, "textbook rule: 2.5", color=TEXT, fontsize=17, fontweight="bold", ha="right", va="top")
    ax.errorbar(x, c, yerr=[c - lo, hi - c], fmt="o", color=INK, ms=14, capsize=8, elinewidth=3, capthick=3, zorder=5)
    for xi, ci in zip(x, c):
        ax.text(xi, ci + 0.2, f"{ci:.2f}", ha="center", fontsize=17, fontweight="bold")
    ax.plot(x, c, color=INK, lw=1.5, alpha=0.4, zorder=1)
    ax.set_xticks(x); ax.set_xticklabels([f"p = {p}\n{2 ** p:,} registers" for p in ps], fontsize=14)
    ax.set_ylim(1.5, 4.2); ax.set_xlim(-0.5, len(ps) - 0.5)
    ax.set_xlabel("Sketch size")
    ax.set_ylabel("Crossover  c*  (items per register)")
    ax.text(0.02, 0.97, "Each dot = one sketch size, bars = 95% CI.\nThe dots climb, so no single threshold fits every size.",
            transform=ax.transAxes, fontsize=15, va="top", color=INK)
    plt.tight_layout(); plt.savefig(os.path.join(RES, fname)); plt.close()


def _rule(p, name):
    return rules[(rules.p == p) & (rules.rule == name)].iloc[0]


def plot_c(fname, p=P0):
    names = [("raw_only", "Plain HLL\nonly", RAW), ("textbook_2.5m", "Textbook\n(2.5)", TEXT),
             ("best_c_per_p", f"Best\n({bestc.loc[p, 'best_c']:.2f})", BEST)]
    fig, ax = plt.subplots(figsize=(12.5, 6.4))
    cap = 3.4
    groups = [("wc", "Worst case\n(largest typical error anywhere)"), ("bump", "Hand-over bump\n(largest average error)")]
    w = 0.26
    for gi, (key, gl) in enumerate(groups):
        for bi, (nm, lab, col) in enumerate(names):
            r = _rule(p, nm); v = r[key] * 100; lo = r[f"{key}_ci_lo"] * 100; hi = r[f"{key}_ci_hi"] * 100
            x = gi + (bi - 1) * (w + 0.04)
            if v > cap:
                ax.bar(x, cap, w, color=col)
                ax.plot([x - w / 2 - 0.01, x + w / 2 + 0.01], [cap * 0.78, cap * 0.84], color="white", lw=6)
                ax.text(x, cap * 0.5, f"{v:.0f}%", ha="center", va="center", color="white", fontsize=20, fontweight="bold", rotation=90)
                ax.text(x, cap + 0.06, "off the\nchart", ha="center", va="bottom", fontsize=12.5, color=col)
            else:
                ax.bar(x, v, w, color=col, yerr=[[v - lo], [hi - v]], error_kw=dict(ecolor=INK, capsize=6, elinewidth=2.5))
                ax.text(x, hi + 0.07, f"{v:.2f}%", ha="center", va="bottom", fontsize=18, fontweight="bold", color=col)
            ax.text(x, -0.02, lab, ha="center", va="top", fontsize=14, color=col, fontweight="bold", transform=ax.get_xaxis_transform())
    ax.set_xticks([0, 1]); ax.set_xticklabels([g[1] for g in groups], fontsize=16)
    ax.tick_params(axis="x", pad=58)
    ax.set_ylim(0, 4.3); ax.set_xlim(-0.55, 1.55)
    ax.set_ylabel("Error (%)"); ax.set_xlabel("")
    fig.text(0.5, 0.005, f"p = {p}, lower is better. Black bars = 95% CI. Measured on {SEEDS // 2} runs that were not used to choose the switch point.",
             ha="center", fontsize=13, color=GRAYC)
    plt.tight_layout(rect=(0, 0.03, 1, 1)); plt.savefig(os.path.join(RES, fname)); plt.close()


def plot_c_by_p(fname):
    ps = sorted(cross.index)
    fig, ax = plt.subplots(figsize=(11.5, 6))
    x = np.arange(len(ps)); w = 0.36
    for off, nm, col, lab in ((-w / 2, "textbook_2.5m", TEXT, "Textbook rule (2.5)"), (w / 2, "best_c_per_p", BEST, "Best rule")):
        v = np.array([_rule(p, nm).wc * 100 for p in ps])
        lo = np.array([_rule(p, nm).wc_ci_lo * 100 for p in ps]); hi = np.array([_rule(p, nm).wc_ci_hi * 100 for p in ps])
        ax.bar(x + off, v, w, color=col, yerr=[v - lo, hi - v], error_kw=dict(ecolor=INK, capsize=5, elinewidth=2.2))
        for xi, vi, hi_i in zip(x + off, v, hi):
            ax.text(xi, hi_i + 0.15, f"{vi:.1f}%", ha="center", fontsize=14, fontweight="bold", color=col)
    ax.text(0.2, 7.9, "Textbook rule (2.5)", color=TEXT, fontsize=17, fontweight="bold")
    ax.text(0.2, 7.2, "Best rule", color=BEST, fontsize=17, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels([f"p = {p}\n{2 ** p:,} registers" for p in ps], fontsize=14)
    ax.set_ylabel("Worst-case typical error (%)"); ax.set_xlabel("Sketch size"); ax.set_ylim(0, 8.8)
    plt.tight_layout(); plt.savefig(os.path.join(RES, fname)); plt.close()


def plot_d(fname, p=P0):
    s = scan[(scan.p == p) & (scan.family == "raw_estimate_threshold")].sort_values("param")
    fig, ax = plt.subplots(figsize=(12, 6.2))
    ax.plot(s.param, s.wc_train * 100, color=INK, lw=3.4)
    ax.plot(s.param, s.wc_train * 100, "o", color=INK, ms=6)
    ymax = 6
    ax.set_ylim(0, ymax); ax.set_xlim(1.45, 5.05)
    cb = bestc.loc[p, "best_c"]
    t25 = s[np.isclose(s.param, 2.5)].wc_train.iloc[0] * 100
    tb = s[np.isclose(s.param, cb)].wc_train.iloc[0] * 100
    ax.plot([2.5], [t25], "o", color=TEXT, ms=19, zorder=6); ax.plot([cb], [tb], "o", color=BEST, ms=19, zorder=6)
    ax.annotate("Textbook rule:\nswitch at 2.5", xy=(2.5, t25), xytext=(2.85, 4.3), fontsize=18, color=TEXT, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color=TEXT, lw=2.4))
    ax.annotate(f"Lowest point:\nswitch at {cb:.2f}", xy=(cb, tb), xytext=(3.7, 3.0), fontsize=18, color=BEST, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color=BEST, lw=2.4))
    ax.text(1.5, 0.15, "off the chart on the far left: switching very early\nleaves the large error of plain HLL", fontsize=12.5, color=GRAYC)
    ax.set_xlabel("Where we switch from linear counting to plain HLL  (items per register, n/m)")
    ax.set_ylabel("Worst-case typical error (%)")
    ax.text(0.99, 0.97, f"p = {p}. Each point = a different switch place; lower is better.\nMeasured on half of the runs ({SEEDS // 2}).",
            transform=ax.transAxes, ha="right", va="top", fontsize=13.5, color=GRAYC)
    plt.tight_layout(); plt.savefig(os.path.join(RES, fname)); plt.close()


def plot_e(fname):
    d = curves_p(P0)
    t = d.n_over_m.values
    fig, ax = plt.subplots(figsize=(12, 6.2))
    tt = np.linspace(0.25, 8, 400)
    ax.plot(t, d.empty_frac * 100, "o", color=INK, ms=7, label="measured")
    ax.plot(tt, np.exp(-tt) * 100, color=GRAYC, lw=2, ls="--")
    xaxis_nm(ax)
    ax.set_ylim(0, 85)
    ax.set_ylabel("Registers still empty (%)")
    ax.text(0.28, 24, "Measured (dots) and the simple\nformula e^(−n/m) (dashed line)\nagree.", fontsize=14.5, color=INK, va="top")
    cs = cross.loc[P0, "c_star"]
    ax.axvline(cs, color=INK, lw=2.4, ls="--")
    ax.annotate(f"At the crossover ({cs:.2f}):\nonly {np.exp(-cs) * 100:.1f}% of the registers\nare still empty", xy=(cs, np.exp(-cs) * 100),
                xytext=(0.95, 58), fontsize=16.5, fontweight="bold", color=INK, arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.2))
    ax.text(4.1, 22, "Linear counting needs empty\nregisters. When they run out,\nit has nothing to work with.", fontsize=15, color=LC, fontweight="bold")
    plt.tight_layout(); plt.savefig(os.path.join(RES, fname)); plt.close()


def plot_sanity(fname):
    """left: large-n typical error vs theory; right: real-text crossover vs synthetic crossover"""
    ps = sorted(cross.index)
    real = pd.read_csv(os.path.join(RES, "exp6_real_crossover.csv"))
    fig, ax = plt.subplots(1, 2, figsize=(14.5, 6.2))
    a = ax[0]
    meas = [curves_p(p).iloc[-1].rmse_raw * 100 for p in ps]
    th = [104 / np.sqrt(2 ** p) for p in ps]
    xs = np.arange(len(ps))
    a.bar(xs - 0.2, meas, 0.38, color=RAW)
    a.bar(xs + 0.2, th, 0.38, color="#bbbbbb")
    for xi, v, t in zip(xs, meas, th):
        a.text(xi - 0.2, v + 0.15, f"{v:.2f}", ha="center", fontsize=12.5, color=RAW, fontweight="bold")
        a.text(xi + 0.2, t + 0.15, f"{t:.2f}", ha="center", fontsize=12.5, color="#555555", fontweight="bold")
    a.set_xticks(xs); a.set_xticklabels([f"p = {p}" for p in ps])
    a.set_ylabel("Typical error of plain HLL (%)"); a.set_xlabel("Sketch size")
    a.set_title("Large counts (8 items per register):\nmeasured vs theory 1.04/√m", fontsize=16)
    a.text(0.97, 0.9, "blue = measured\ngray = theory", transform=a.transAxes, ha="right", va="top", fontsize=15, fontweight="bold", color=INK)
    b = ax[1]
    rp = list(real.p)
    xs2 = np.arange(len(rp))
    syn = real.c_star_synthetic.values
    b.plot(xs2, syn, "s", ms=15, color=INK, label="synthetic")
    b.errorbar(xs2 + 0.12, real.c_star_real, yerr=[real.c_star_real - real.ci_lo, real.ci_hi - real.c_star_real], fmt="o", ms=14,
               color=LC, ecolor=LC, capsize=7, elinewidth=3, capthick=3)
    for xi, v in zip(xs2, syn):
        b.text(xi - 0.1, v, f"{v:.2f}", ha="right", va="center", fontsize=14, fontweight="bold", color=INK)
    for xi, v in zip(xs2, real.c_star_real):
        b.text(xi + 0.2, v - 0.12, f"{v:.2f}", ha="left", va="top", fontsize=14, fontweight="bold", color="#b35a00")
    b.set_xticks(xs2); b.set_xticklabels([f"p = {p}" for p in rp]); b.set_xlim(-0.5, len(rp) - 0.5)
    b.set_ylim(1.5, 5.9)
    b.text(0.03, 0.80, "p = 8: wide interval (a small sketch on one fixed text is noisy)", transform=b.transAxes, fontsize=12.5, color=GRAYC)
    b.set_ylabel("Crossover (items per register)"); b.set_xlabel("Sketch size")
    b.set_title("Crossover on real text vs synthetic data", fontsize=16)
    b.text(0.03, 0.98, "black squares = synthetic random IDs\norange dots = War and Peace (bars = 95% CI)", transform=b.transAxes, va="top", fontsize=14, color=INK)
    plt.tight_layout(); plt.savefig(os.path.join(RES, fname)); plt.close()


def plot_bump_real(fname):
    d = curves_p(P0)
    t = d.n_over_m.values
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(t, d.rmse_textbook * 100, color=TEXT, lw=3.6)
    ax.plot(t, np.abs(d.bias_textbook) * 100, color=TEXT, lw=2.6, ls=":")
    xaxis_nm(ax); ax.set_ylim(0, 3.6)
    ax.set_ylabel("Error of the textbook rule (%)")
    j = int(np.argmax(d.rmse_textbook.values))
    ax.plot([t[j]], [d.rmse_textbook.values[j] * 100], "o", color=INK, ms=16, zorder=6)
    ax.annotate("WORST CASE = the tallest point of the\nsolid line (typical error)", xy=(t[j], d.rmse_textbook.values[j] * 100),
                xytext=(0.3, 3.0), fontsize=16, fontweight="bold", color=INK, arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.4))
    k = int(np.argmax(np.abs(d.bias_textbook.values)))
    ax.plot([t[k]], [abs(d.bias_textbook.values[k]) * 100], "o", color=TEXT, ms=14, zorder=6, mfc="white", mew=3)
    ax.annotate("HAND-OVER BUMP = the tallest point\nof the dotted line (average error),\nright where the rule switches", xy=(t[k], abs(d.bias_textbook.values[k]) * 100),
                xytext=(3.0, 1.45), fontsize=16, fontweight="bold", color=TEXT, arrowprops=dict(arrowstyle="-|>", color=TEXT, lw=2.4))
    ax.axvline(2.5, color=GRAYC, ls="--", lw=2); ax.text(2.55, 3.45, "switch at 2.5", color=GRAYC, fontsize=14)
    ax.text(0.02, 0.5, "solid line = typical error\ndotted line = average error\n(real data, p = 14, textbook rule)", transform=ax.transAxes, ha="left", fontsize=14.5, color=GRAYC)
    plt.tight_layout(); plt.savefig(os.path.join(RES, fname)); plt.close()


def plot_backup_theory(fname):
    """typical error of plain HLL vs number of registers (exp2 data) against the theory line"""
    e2 = pd.read_csv(os.path.join(RES, "exp2_n1e6.csv"))
    n = e2.n.iloc[0]
    e2["err"] = (e2.est_basic - n) / n
    g = e2.groupby("p")
    ps = np.array(sorted(g.groups)); m = 2.0 ** ps
    sd = np.array([g.get_group(p).err.std(ddof=1) * 100 for p in ps])
    fig, ax = plt.subplots(figsize=(11.5, 6))
    ax.plot(ps, 104 / np.sqrt(m), color=GRAYC, lw=3, ls="--")
    ax.plot(ps, sd, "o-", color=RAW, ms=11)
    ax.set_yscale("log"); ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_locator(FixedLocator([0.3, 1, 3, 10, 30])); ax.yaxis.set_major_formatter(FixedFormatter(["0.3%", "1%", "3%", "10%", "30%"]))
    ax.set_xticks(ps); ax.set_xticklabels([f"{p}" for p in ps])
    ax.set_xlabel("p  (number of registers m = 2^p; each +1 doubles the memory)")
    ax.set_ylabel("Typical error of plain HLL\n(log scale)")
    ax.text(4.3, 0.75, "Plain HLL, measured", color=RAW, fontsize=18, fontweight="bold")
    ax.text(10.2, 6.5, "Theory 1.04/√m", color=GRAYC, fontsize=18, fontweight="bold")
    ax.text(0.99, 0.97, f"n = {n:,} items, 20 runs per point (20 runs: values are uncertain by about ±16%)", transform=ax.transAxes, ha="right", va="top", fontsize=12.5, color=GRAYC)
    plt.tight_layout(); plt.savefig(os.path.join(RES, fname)); plt.close()


def plot_small_multiples(fname):
    ps = sorted(cross.index)
    fig, axs = plt.subplots(1, len(ps), figsize=(17, 4.6), sharey=True)
    for a, p in zip(axs, ps):
        d = curves_p(p)
        a.plot(d.n_over_m, d.rmse_raw * 100, color=RAW, lw=2.6); a.plot(d.n_over_m, d.rmse_lc * 100, color=LC, lw=2.6)
        cs = cross.loc[p, "c_star"]; a.axvline(cs, color=INK, ls="--", lw=2)
        a.set_xscale("log"); a.set_yscale("log"); a.set_xlim(0.25, 8); a.set_ylim(0.15, 400)
        a.xaxis.set_major_locator(FixedLocator([0.5, 1, 2, 4, 8])); a.xaxis.set_major_formatter(FixedFormatter(["0.5", "1", "2", "4", "8"]))
        a.xaxis.set_minor_locator(NullLocator()); a.yaxis.set_minor_locator(NullLocator())
        a.set_title(f"p = {p}\ncrossover {cs:.2f}", fontsize=15)
        a.tick_params(labelsize=12)
    axs[0].yaxis.set_major_locator(FixedLocator([1, 10, 100])); axs[0].yaxis.set_major_formatter(FixedFormatter(["1%", "10%", "100%"]))
    axs[0].set_ylabel("Typical error", fontsize=14)
    fig.supxlabel("Items per register (n/m, log scale)   blue = plain HLL, orange = linear counting, dashed line = crossover", fontsize=14)
    plt.tight_layout(); plt.savefig(os.path.join(RES, fname)); plt.close()


if __name__ == "__main__":
    plot_a_p14(False, "exp5_plotA_p14_plain.png")
    plot_a_p14(True, "exp5_plotA_p14_crossover.png")
    plot_a_allp("exp5_plotA_all_p.png")
    plot_b("exp5_plotB_crossover_vs_p.png")
    plot_c("exp5_plotC_rules.png")
    plot_c_by_p("exp5_plotC_by_p.png")
    plot_d("exp5_plotD_threshold_scan.png")
    plot_e("exp5_plotE_empty_share.png")
    plot_sanity("exp5_sanity.png")
    plot_bump_real("exp5_bump_definition.png")
    plot_backup_theory("exp5_backup_theory.png")
    plot_small_multiples("exp5_backup_small_multiples.png")
    print("exp5 plots written")
