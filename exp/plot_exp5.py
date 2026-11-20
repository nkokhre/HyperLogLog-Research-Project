"""Plots for experiment 5 (crossover) and experiment 6 (real text). Run after exp/analyze_exp5.py.
Usage (from project root):  python3 exp/plot_exp5.py

Colour code used in EVERY plot and slide:
  plain HLL = blue, linear counting (LC) = orange, textbook 2.5 rule = purple, best rule = green.
Rules: plain-language axis labels, curves labelled directly (no legend lookups), the key point annotated,
error bands explained on the figure. Figures are sized for a 16:9 slide (side layout 10 x 5.5 in,
full-width layout 14 x 5.45 in) so the text stays readable when projected.
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
LCDARK, RAWDARK = "#b35a00", "#124e78"
plt.rcParams.update({"font.size": 18, "axes.labelsize": 18, "axes.titlesize": 19, "xtick.labelsize": 16,
                     "ytick.labelsize": 16, "axes.spines.top": False, "axes.spines.right": False,
                     "lines.linewidth": 3.6, "savefig.dpi": 200})
SIDE = (10, 5.5)
WIDE = (14, 5.45)

cur = pd.read_csv(os.path.join(RES, "exp5_curves.csv"))
cross = pd.read_csv(os.path.join(RES, "exp5_crossover.csv")).set_index("p")
scan = pd.read_csv(os.path.join(RES, "exp5_scan.csv"))
rules = pd.read_csv(os.path.join(RES, "exp5_rules.csv"))
bestc = pd.read_csv(os.path.join(RES, "exp5_best_threshold.csv")).set_index("p")
P0 = 14
M0 = 2 ** P0
SEEDS = int(cur.seeds.iloc[0])
XT = [0.25, 0.5, 1, 2, 4, 8]


def save(fig, fname):
    fig.savefig(os.path.join(RES, fname), bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def xaxis_nm(ax, label="Items per register  (n / m, log scale)"):
    ax.set_xscale("log"); ax.set_xlim(0.25, 8)
    ax.xaxis.set_major_locator(FixedLocator(XT)); ax.xaxis.set_major_formatter(FixedFormatter([str(x) for x in XT]))
    ax.xaxis.set_minor_locator(NullLocator()); ax.set_xlabel(label)


def yaxis_err(ax, lo=0.2, hi=400, label="Typical error  (log scale)"):
    ax.set_yscale("log"); ax.set_ylim(lo, hi)
    ticks = [t for t in (0.1, 1, 10, 100) if lo <= t <= hi]
    ax.yaxis.set_major_locator(FixedLocator(ticks)); ax.yaxis.set_major_formatter(FixedFormatter([f"{t:g}%" for t in ticks]))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_ylabel(label)


def top_axis_n(ax, m=M0):
    sec = ax.secondary_xaxis("top", functions=(lambda t: t * m, lambda n: n / m))
    ns = [m // 4, m, 4 * m, 8 * m]
    sec.xaxis.set_major_locator(FixedLocator(ns)); sec.xaxis.set_major_formatter(FixedFormatter([f"{n:,}" for n in ns]))
    sec.xaxis.set_minor_locator(NullLocator())
    sec.set_xlabel(f"same position in items n  (p = {int(np.log2(m))}, m = {m:,} registers)", fontsize=15, color=GRAYC)
    sec.tick_params(labelsize=14, colors=GRAYC)


def curves_p(p):
    return cur[cur.p == p].sort_values("n_over_m")


# ---------------------------------------------------------------- plot A (p = 14)
def plot_a_p14(annotated, fname):
    d = curves_p(P0); t = d.n_over_m.values
    fig, ax = plt.subplots(figsize=SIDE)
    c = cross.loc[P0, "c_star"]; lo, hi = cross.loc[P0, "ci_lo"], cross.loc[P0, "ci_hi"]
    if annotated:
        ax.axvspan(0.25, c, color=LC, alpha=0.10, lw=0); ax.axvspan(c, 8, color=RAW, alpha=0.10, lw=0)
    ax.fill_between(t, d.rmse_raw_ci_lo * 100, d.rmse_raw_ci_hi * 100, color=RAW, alpha=0.3, lw=0)
    ax.fill_between(t, d.rmse_lc_ci_lo * 100, d.rmse_lc_ci_hi * 100, color=LC, alpha=0.3, lw=0)
    ax.plot(t, d.rmse_raw * 100, color=RAW); ax.plot(t, d.rmse_lc * 100, color=LC)
    xaxis_nm(ax); yaxis_err(ax)
    ax.text(0.3, 45, "Plain HLL", color=RAW, fontsize=22, fontweight="bold")
    ax.text(4.3, 9.5, "Linear\ncounting", color=LC, fontsize=22, fontweight="bold", va="bottom")
    if annotated:
        ax.axvspan(lo, hi, color=INK, alpha=0.3, lw=0)
        ax.axvline(c, color=INK, lw=2.6, ls="--")
        ax.text(1.05, 330, "Linear counting\nis better here", color=LCDARK, fontsize=19, fontweight="bold", va="top")
        ax.text(7.8, 330, "Plain HLL is\nbetter here", color=RAWDARK, fontsize=19, fontweight="bold", va="top", ha="right")
        ax.annotate(f"Crossover = {c:.2f}\nitems per register\n(≈ {c * M0:,.0f} items)", xy=(c, 1.15), xytext=(0.3, 1.25),
                    fontsize=18, color=INK, fontweight="bold", arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.4))
    top_axis_n(ax)
    ax.text(0.0, -0.25, f"shaded bands = 95% confidence interval over {SEEDS} runs", transform=ax.transAxes, fontsize=14, color=GRAYC)
    save(fig, fname)


# ---------------------------------------------------------------- plot A (all p)
def plot_a_allp(fname):
    ps = sorted(cross.index)
    fig, ax = plt.subplots(1, 2, figsize=WIDE, sharey=True)
    for k, a in enumerate(ax):
        for i, p in enumerate(ps):
            d = curves_p(p); m = 2 ** p
            x = d.n.values if k == 0 else d.n_over_m.values
            al = 0.4 + 0.6 * i / (len(ps) - 1)
            a.plot(x, d.rmse_raw * 100, color=RAW, lw=2.2, alpha=al)
            a.plot(x, d.rmse_lc * 100, color=LC, lw=2.2, alpha=al)
            c = cross.loc[p, "c_star"]
            xc = c * m if k == 0 else c
            yc = np.interp(c, d.n_over_m.values, d.rmse_raw.values) * 100
            a.plot([xc], [yc], "o", color=INK, ms=10, zorder=5)
            if k == 0:
                a.annotate(f"p={p}", (xc, yc), xytext=(6, -24), textcoords="offset points", fontsize=15, fontweight="bold")
            else:
                a.annotate(f"p={p}", (xc, yc), xytext=(14, 0), textcoords="offset points", fontsize=15, fontweight="bold", va="center")
        a.set_yscale("log"); a.set_ylim(0.15, 400)
        a.xaxis.set_minor_locator(NullLocator()); a.yaxis.set_minor_locator(NullLocator())
    ax[0].set_xscale("log"); ax[0].set_xlabel("Number of distinct items  n  (log scale)")
    ax[0].xaxis.set_major_locator(FixedLocator([100, 1e3, 1e4, 1e5])); ax[0].xaxis.set_major_formatter(FixedFormatter(["100", "1,000", "10,000", "100,000"]))
    ax[0].set_xlim(60, 6e5)
    xaxis_nm(ax[1])
    ax[0].yaxis.set_major_locator(FixedLocator([1, 10, 100])); ax[0].yaxis.set_major_formatter(FixedFormatter(["1%", "10%", "100%"]))
    ax[0].set_ylabel("Typical error  (log scale)")
    lo_n, hi_n = cross.n_star.min(), cross.n_star.max(); lo_c, hi_c = cross.c_star.min(), cross.c_star.max()
    ax[0].set_title(f"x-axis = items n:  dots from {lo_n:,.0f} to {hi_n:,.0f}", fontsize=18, fontweight="bold")
    ax[1].set_title(f"x-axis = items per register:  dots from {lo_c:.1f} to {hi_c:.1f}", fontsize=18, fontweight="bold")
    ax[0].text(70, 0.2, "orange = linear counting", color=LC, fontsize=16, fontweight="bold")
    ax[0].text(70, 0.36, "blue = plain HLL", color=RAW, fontsize=16, fontweight="bold")
    fig.tight_layout(w_pad=3)
    save(fig, fname)


# ---------------------------------------------------------------- plot B
def plot_b(fname):
    ps = sorted(cross.index)
    fig, ax = plt.subplots(figsize=SIDE)
    x = np.arange(len(ps))
    c = cross.loc[ps, "c_star"].values; lo = cross.loc[ps, "ci_lo"].values; hi = cross.loc[ps, "ci_hi"].values
    ax.axhline(2.5, color=TEXT, lw=3, ls="--")
    ax.text(len(ps) - 0.5, 2.44, "textbook rule: 2.5", color=TEXT, fontsize=19, fontweight="bold", ha="right", va="top")
    ax.plot(x, c, color=INK, lw=1.6, alpha=0.35, zorder=1)
    ax.errorbar(x, c, yerr=[c - lo, hi - c], fmt="o", color=INK, ms=15, capsize=9, elinewidth=3, capthick=3, zorder=5)
    for xi, v in zip(x, c):
        ax.text(xi, v + 0.17, f"{v:.2f}", ha="center", fontsize=20, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels([f"p = {p}\n{2 ** p:,}" for p in ps])
    ax.set_ylim(1.6, 4.0); ax.set_xlim(-0.5, len(ps) - 0.5)
    ax.set_xlabel("Sketch size  (p, and number of registers m)")
    ax.set_ylabel("Crossover  (items per register)")
    ax.text(-0.4, 3.9, "Each dot = one sketch size, bars = 95% CI.\nThe dots climb: no single threshold fits every size.", fontsize=16, va="top")
    save(fig, fname)


def _rule(p, name):
    return rules[(rules.p == p) & (rules.rule == name)].iloc[0]


# ---------------------------------------------------------------- plot C (p = 14)
def plot_c(fname, p=P0):
    names = [("raw_only", "Plain HLL\nonly", RAW), ("textbook_2.5m", "Textbook\nrule 2.5", TEXT),
             ("best_c_per_p", f"Best rule\n{bestc.loc[p, 'best_c']:.2f}", BEST)]
    fig, ax = plt.subplots(figsize=SIDE)
    cap = 3.4; w = 0.27
    groups = [("wc", "Worst case"), ("bump", "Hand-over bump")]
    for gi, (key, gl) in enumerate(groups):
        for bi, (nm, lab, col) in enumerate(names):
            r = _rule(p, nm); v = r[key] * 100; lo = r[f"{key}_ci_lo"] * 100; hi = r[f"{key}_ci_hi"] * 100
            x = gi + (bi - 1) * (w + 0.04)
            if v > cap:
                ax.bar(x, cap, w, color=col)
                ax.plot([x - w / 2 - 0.01, x + w / 2 + 0.01], [cap * 0.76, cap * 0.83], color="white", lw=7)
                ax.text(x, cap * 0.42, f"{v:.0f}%", ha="center", va="center", color="white", fontsize=22, fontweight="bold", rotation=90)
                ax.text(x, cap + 0.06, "off the\nchart", ha="center", va="bottom", fontsize=14, color=col)
            else:
                ax.bar(x, v, w, color=col, yerr=[[v - lo], [hi - v]], error_kw=dict(ecolor=INK, capsize=6, elinewidth=2.5))
                ax.text(x, hi + 0.07, f"{v:.2f}%", ha="center", va="bottom", fontsize=20, fontweight="bold", color=col)
            ax.text(x, -0.03, lab, ha="center", va="top", fontsize=15, color=col, fontweight="bold", transform=ax.get_xaxis_transform())
    ax.set_xticks([0, 1]); ax.set_xticklabels([g[1] for g in groups], fontsize=19, fontweight="bold")
    ax.tick_params(axis="x", pad=58, length=0)
    ax.set_ylim(0, 4.9); ax.set_xlim(-0.52, 1.52)
    ax.set_ylabel("Error (%)  — lower is better")
    ax.text(0.55, 4.88, f"p = {p} · black bars = 95% CI\nmeasured on {SEEDS // 2} runs NOT used to choose the switch place",
            ha="center", va="top", fontsize=13.5, color=GRAYC)
    save(fig, fname)


def plot_c_by_p(fname):
    ps = sorted(cross.index)
    fig, ax = plt.subplots(figsize=SIDE)
    x = np.arange(len(ps)); w = 0.36
    for off, nm, col in ((-w / 2, "textbook_2.5m", TEXT), (w / 2, "best_c_per_p", BEST)):
        v = np.array([_rule(p, nm).wc * 100 for p in ps])
        lo = np.array([_rule(p, nm).wc_ci_lo * 100 for p in ps]); hi = np.array([_rule(p, nm).wc_ci_hi * 100 for p in ps])
        ax.bar(x + off, v, w, color=col, yerr=[v - lo, hi - v], error_kw=dict(ecolor=INK, capsize=5, elinewidth=2.2))
        for xi, vi, hi_i in zip(x + off, v, hi):
            ax.text(xi, hi_i + 0.15, f"{vi:.1f}", ha="center", fontsize=16, fontweight="bold", color=col)
    ax.text(4.45, 7.6, "Textbook rule 2.5", color=TEXT, fontsize=20, fontweight="bold", ha="right")
    ax.text(4.45, 6.7, "Best rule", color=BEST, fontsize=20, fontweight="bold", ha="right")
    ax.set_xticks(x); ax.set_xticklabels([f"p = {p}" for p in ps])
    ax.set_ylabel("Worst-case error (%)"); ax.set_xlabel("Sketch size"); ax.set_ylim(0, 8.6)
    ax.text(4.45, 5.9, "black bars = 95% CI", color=GRAYC, fontsize=14, ha="right")
    save(fig, fname)


# ---------------------------------------------------------------- plot D
def plot_d(fname, p=P0):
    s = scan[(scan.p == p) & (scan.family == "raw_estimate_threshold")].sort_values("param")
    fig, ax = plt.subplots(figsize=SIDE)
    ax.plot(s.param, s.wc_train * 100, color=INK, lw=3.6)
    ax.plot(s.param, s.wc_train * 100, "o", color=INK, ms=6)
    ax.set_ylim(0, 6); ax.set_xlim(1.45, 5.05)
    cb = bestc.loc[p, "best_c"]
    t25 = s[np.isclose(s.param, 2.5)].wc_train.iloc[0] * 100
    tb = s[np.isclose(s.param, cb)].wc_train.iloc[0] * 100
    ax.plot([2.5], [t25], "o", color=TEXT, ms=20, zorder=6); ax.plot([cb], [tb], "o", color=BEST, ms=20, zorder=6)
    ax.annotate("Textbook rule:\nswitch at 2.5", xy=(2.5, t25), xytext=(2.8, 4.4), fontsize=20, color=TEXT, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color=TEXT, lw=2.6))
    ax.annotate(f"Lowest point:\nswitch at {cb:.2f}", xy=(cb, tb), xytext=(3.75, 2.9), fontsize=20, color=BEST, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color=BEST, lw=2.6))
    ax.text(1.5, 0.2, "far left: off the chart\n(switching too early)", fontsize=14, color=GRAYC)
    ax.set_xlabel("Switch place c  (switch when the estimate passes c · m)")
    ax.set_ylabel("Worst-case error (%)")
    ax.text(5.0, 5.9, f"p = {p}; lower is better", ha="right", va="top", fontsize=15, color=GRAYC)
    save(fig, fname)


# ---------------------------------------------------------------- plot E
def plot_e(fname):
    d = curves_p(P0); t = d.n_over_m.values
    fig, ax = plt.subplots(figsize=SIDE)
    tt = np.linspace(0.25, 8, 400)
    ax.plot(tt, np.exp(-tt) * 100, color=GRAYC, lw=2.4, ls="--")
    ax.plot(t, d.empty_frac * 100, "o", color=INK, ms=8)
    xaxis_nm(ax); ax.set_ylim(0, 85)
    ax.set_ylabel("Registers still empty (%)")
    c = cross.loc[P0, "c_star"]
    ax.axvline(c, color=INK, lw=2.6, ls="--")
    ax.text(3.35, 83, "dots = measured\ndashed = formula e^(−n/m)", fontsize=15, color=GRAYC, va="top")
    ax.text(3.35, 60, "Linear counting needs\nempty registers. When\nthey run out, it has\nnothing to work with.", fontsize=17, color=LCDARK, fontweight="bold", va="top")
    ax.annotate(f"At the crossover ({c:.2f}):\nonly {np.exp(-c) * 100:.1f}% of registers\nare still empty", xy=(c, np.exp(-c) * 100),
                xytext=(0.27, 3), fontsize=18, fontweight="bold", color=INK, arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.4))
    save(fig, fname)


# ---------------------------------------------------------------- worst case / hand-over bump definition
def plot_bump_definition(fname):
    d = curves_p(P0); t = d.n_over_m.values
    fig, ax = plt.subplots(figsize=SIDE)
    ax.plot(t, d.rmse_textbook * 100, color=TEXT, lw=3.8)
    ax.plot(t, np.abs(d.bias_textbook) * 100, color=TEXT, lw=2.8, ls=":")
    xaxis_nm(ax); ax.set_ylim(0, 3.7)
    ax.set_ylabel("Error of the textbook rule (%)")
    j = int(np.argmax(d.rmse_textbook.values)); k = int(np.argmax(np.abs(d.bias_textbook.values)))
    ax.plot([t[j]], [d.rmse_textbook.values[j] * 100], "o", color=INK, ms=16, zorder=6)
    ax.plot([t[k]], [abs(d.bias_textbook.values[k]) * 100], "o", color=TEXT, ms=14, zorder=6, mfc="white", mew=3)
    ax.annotate("WORST CASE =\ntallest point of the\nsolid line", xy=(t[j], d.rmse_textbook.values[j] * 100),
                xytext=(0.6, 2.4), fontsize=18, fontweight="bold", color=INK, arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.4))
    ax.annotate("HAND-OVER BUMP =\ntallest point of the\ndotted line", xy=(t[k], abs(d.bias_textbook.values[k]) * 100),
                xytext=(3.6, 1.6), fontsize=18, fontweight="bold", color=TEXT, arrowprops=dict(arrowstyle="-|>", color=TEXT, lw=2.4))
    ax.text(0.27, 1.15, "solid = typical error\ndotted = average error", fontsize=15, color=GRAYC)
    ax.text(2.62, 3.6, "switch at 2.5", color=GRAYC, fontsize=15, va="top")
    ax.axvline(2.5, color=GRAYC, ls="--", lw=2)
    save(fig, fname)


# ---------------------------------------------------------------- sanity checks
def plot_sanity(fname):
    ps = sorted(cross.index)
    real = pd.read_csv(os.path.join(RES, "exp6_real_crossover.csv"))
    fig, ax = plt.subplots(1, 2, figsize=WIDE, gridspec_kw={"width_ratios": [1.25, 1]})
    a = ax[0]
    meas = [curves_p(p).iloc[-1].rmse_raw * 100 for p in ps]
    th = [104 / np.sqrt(2 ** p) for p in ps]
    xs = np.arange(len(ps))
    a.bar(xs - 0.2, meas, 0.38, color=RAW); a.bar(xs + 0.2, th, 0.38, color="#bbbbbb")
    for xi, v, t in zip(xs, meas, th):
        a.text(xi - 0.2, v + 0.12, f"{v:.2f}", ha="center", fontsize=13.5, color=RAWDARK, fontweight="bold", rotation=90, va="bottom")
        a.text(xi + 0.2, t + 0.12, f"{t:.2f}", ha="center", fontsize=13.5, color="#555555", fontweight="bold", rotation=90, va="bottom")
    a.set_xticks(xs); a.set_xticklabels([f"p={p}" for p in ps])
    a.set_ylim(0, 8.2)
    a.set_ylabel("Typical error of plain HLL (%)"); a.set_xlabel("Sketch size")
    a.set_title("Large counts: measured vs theory", fontsize=18, fontweight="bold")
    a.text(4.4, 7.9, "blue = measured\ngray = theory 1.04/√m", ha="right", va="top", fontsize=16, fontweight="bold")
    b = ax[1]
    rp = list(real.p); xs2 = np.arange(len(rp))
    syn = real.c_star_synthetic.values; rv = real.c_star_real.values
    lo = real.ci_lo.values; hi = real.ci_hi.values
    top = 3.6
    b.plot(xs2 - 0.12, syn, "s", ms=15, color=INK)
    for xi, v, l, h in zip(xs2 + 0.12, rv, lo, hi):
        b.plot([xi, xi], [l, min(h, top)], color=LC, lw=3.2)
        b.plot([xi - 0.06, xi + 0.06], [l, l], color=LC, lw=3.2)
        if h <= top:
            b.plot([xi - 0.06, xi + 0.06], [h, h], color=LC, lw=3.2)
        else:
            b.annotate("", xy=(xi, top), xytext=(xi, top - 0.18), arrowprops=dict(arrowstyle="-|>", color=LC, lw=3))
            b.text(xi + 0.1, top - 0.03, f"CI up to {h:.1f}\n(small sketch,\nnoisy)", fontsize=13, color=LCDARK, va="top")
        b.plot([xi], [v], "o", ms=15, color=LC)
    for xi, v in zip(xs2, syn):
        b.text(xi - 0.25, v, f"{v:.2f}", ha="right", va="center", fontsize=15, fontweight="bold", color=INK)
    for xi, v in zip(xs2, rv):
        b.text(xi + 0.25, v - 0.06, f"{v:.2f}", ha="left", va="top", fontsize=15, fontweight="bold", color=LCDARK)
    b.set_xticks(xs2); b.set_xticklabels([f"p={p}" for p in rp]); b.set_xlim(-0.6, len(rp) - 0.4)
    b.set_ylim(1.6, top)
    b.set_ylabel("Crossover (items per register)"); b.set_xlabel("Sketch size")
    b.set_title("Crossover: random IDs vs real text", fontsize=18, fontweight="bold")
    b.text(0.75, 2.12, "■ random IDs", fontsize=16, fontweight="bold", color=INK, va="top")
    b.text(0.75, 1.97, "● War and Peace\n   (bars = 95% CI)", fontsize=16, fontweight="bold", color=LCDARK, va="top")
    fig.tight_layout(w_pad=3)
    save(fig, fname)


# ---------------------------------------------------------------- supporting plot (used in the report)
def plot_theory_check(fname):
    """typical error of plain HLL vs number of registers (exp2 data) against the theory line"""
    e2 = pd.read_csv(os.path.join(RES, "exp2_n1e6.csv"))
    n = e2.n.iloc[0]
    e2["err"] = (e2.est_basic - n) / n
    g = e2.groupby("p")
    ps = np.array(sorted(g.groups)); m = 2.0 ** ps
    sd = np.array([g.get_group(p).err.std(ddof=1) * 100 for p in ps])
    fig, ax = plt.subplots(figsize=SIDE)
    ax.plot(ps, 104 / np.sqrt(m), color=GRAYC, lw=3, ls="--")
    ax.plot(ps, sd, "o-", color=RAW, ms=11)
    ax.set_yscale("log"); ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_locator(FixedLocator([0.3, 1, 3, 10, 30])); ax.yaxis.set_major_formatter(FixedFormatter(["0.3%", "1%", "3%", "10%", "30%"]))
    ax.set_xticks(ps[::2]); ax.set_xticklabels([f"{p}" for p in ps[::2]])
    ax.set_xlabel("p   (m = 2^p registers; +1 doubles the memory)")
    ax.set_ylabel("Typical error of plain HLL (log scale)")
    ax.text(4.2, 0.6, "Plain HLL, measured", color=RAW, fontsize=20, fontweight="bold")
    ax.text(10.3, 6.0, "Theory 1.04/√m", color=GRAYC, fontsize=20, fontweight="bold")
    ax.text(16, 35, f"n = {n:,} items, 20 runs per point", ha="right", va="top", fontsize=14, color=GRAYC)
    save(fig, fname)


if __name__ == "__main__":
    plot_a_p14(False, "exp5_plotA_p14_plain.png")
    plot_a_p14(True, "exp5_plotA_p14_crossover.png")
    plot_a_allp("exp5_plotA_all_p.png")
    plot_b("exp5_plotB_crossover_vs_p.png")
    plot_c("exp5_plotC_rules.png")
    plot_c_by_p("exp5_plotC_by_p.png")
    plot_d("exp5_plotD_threshold_scan.png")
    plot_e("exp5_plotE_empty_share.png")
    plot_bump_definition("exp5_bump_definition.png")
    plot_sanity("exp5_sanity.png")
    plot_theory_check("exp5_theory_check.png")
    print("exp5 plots written")
