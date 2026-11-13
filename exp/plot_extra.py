"""Extra figures for report and slides. Usage: python3 exp/plot_extra.py  (run from project root)"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from scipy import stats

BLUE, ORANGE, GREEN, RED, GRAY = "#1f77b4", "#ff7f0e", "#2e7d32", "#c0392b", "#666666"
plt.rcParams.update({"font.size": 13, "axes.spines.top": False, "axes.spines.right": False})

# ---------- 1. How HLL works (worked example, p=4) ----------
fig, ax = plt.subplots(figsize=(12, 4.6)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 4.6)
def box(x, y, w, h, t, fc="#eaf1fb", ec=BLUE, fs=13):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04", fc=fc, ec=ec, lw=1.6))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs)
def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=18, lw=1.6, color=GRAY))
box(0.1, 1.7, 1.9, 1.2, "item\n(an ID)")
arrow(2.1, 2.3, 2.9, 2.3)
box(3.0, 1.7, 2.2, 1.2, "hash\n64 random bits")
arrow(5.3, 2.5, 6.0, 3.3); arrow(5.3, 2.1, 6.0, 1.3)
box(6.1, 3.0, 2.8, 1.1, "first p bits →\nwhich register", fc="#fff4e5", ec=ORANGE)
box(6.1, 0.6, 2.8, 1.1, "rest of the bits →\nleading zeros + 1", fc="#fff4e5", ec=ORANGE)
arrow(9.0, 3.5, 9.7, 2.9); arrow(9.0, 1.2, 9.7, 1.9)
box(9.8, 1.7, 2.1, 1.2, "register keeps\nthe maximum", fc="#e8f5e9", ec=GREEN)
ax.text(6.0, 4.4, "Each item updates exactly one of m = 2^p registers", ha="center", fontsize=15, fontweight="bold", color="#1F3864")
ax.text(6.0, 0.1, "Many different items → some register sees a long run of zeros.  Long runs are rare, so the registers tell us how many items we saw.",
        ha="center", fontsize=11, color=GRAY)
plt.savefig("results/fig_how.png", dpi=150, bbox_inches="tight"); plt.close()

# ---------- 2. Worked example: registers and estimate ----------
rho = [1, 1, 2, 1, 3, 1, 1, 2, 1, 1, 1, 2, 1, 4, 0, 0]
fig, ax = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1.6, 1]})
cols = [RED if r == 0 else BLUE for r in rho]
ax[0].bar(range(16), [max(r, 0.12) for r in rho], color=cols)
for i, r in enumerate(rho): ax[0].text(i, r + 0.08, str(r), ha="center", fontsize=11)
ax[0].set_xticks(range(16)); ax[0].set_xlabel("register number"); ax[0].set_ylabel("value in register")
ax[0].set_title("A tiny sketch (m = 16). Red = empty register"); ax[0].set_ylim(0, 5)
ax[1].axis("off")
ax[1].text(0, 0.95, "Basic formula", fontsize=14, fontweight="bold", color="#1F3864", va="top")
ax[1].text(0, 0.80, "sum of 2^(−value) = 7.4375\nestimate = 0.673 · 16² / 7.4375\n               = 23.2", fontsize=13, va="top", family="monospace")
ax[1].text(0, 0.42, "Linear counting", fontsize=14, fontweight="bold", color="#1F3864", va="top")
ax[1].text(0, 0.27, "2 of 16 registers empty\nestimate = 16 · ln(16 / 2)\n               = 33.3", fontsize=13, va="top", family="monospace")
plt.tight_layout(); plt.savefig("results/fig_example.png", dpi=150); plt.close()

# ---------- 3. Small counts: estimate vs perfect answer (2 panels) ----------
d = pd.read_csv("results/exp1_p14.csv")
g = d.groupby("n")[["est_basic", "est_lc"]].mean()
ns = g.index.values
fig, ax = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
for a_, col, c, mk, ttl in [(ax[0], "est_basic", BLUE, "o", "Basic HLL vs perfect answer"),
                            (ax[1], "est_lc", ORANGE, "s", "Linear counting vs perfect answer")]:
    a_.plot(ns, ns, "-", color="black", lw=2.2, label="perfect answer", zorder=1)
    a_.plot(ns, g[col], mk, ms=5, color=c, label=ttl.split(" vs")[0], zorder=2)
    a_.set_xscale("log"); a_.set_yscale("log")
    a_.set_xlabel("real number of different items"); a_.set_title(ttl)
    a_.legend(loc="lower right")
ax[0].set_ylabel("estimate (mean of 20 runs)")
ax[0].annotate("1,000 items:\nbasic says ~12,300", xy=(1000, 12300), xytext=(12, 150000), arrowprops=dict(arrowstyle="->"), fontsize=12)
ax[1].annotate("1,000 items:\nlinear counting says ~1,000", xy=(1000, 1000), xytext=(12, 150000), arrowprops=dict(arrowstyle="->"), fontsize=12)
plt.tight_layout(); plt.savefig("results/fig_small.png", dpi=150); plt.close()

# ---------- 4. Hand-over zoom ----------
m = 16384
d["eb"] = (d.est_basic - d.n) / d.n * 100; d["el"] = (d.est_lc - d.n) / d.n * 100
z = d[(d.n >= 0.8 * m) & (d.n <= 7 * m)]
gz = z.groupby("n"); x = gz.eb.mean().index.values / m
tc = stats.t.ppf(0.975, 19)
fig, ax = plt.subplots(figsize=(10, 5))
ax.axvspan(2.5, 4.5, color=RED, alpha=0.08)
ax.axhline(0, color="k", lw=0.8)
for col, c, mk, lab in [("eb", BLUE, "o", "basic HLL"), ("el", ORANGE, "s", "with linear counting")]:
    mu, ci = gz[col].mean().values, tc * gz[col].std().values / np.sqrt(20)
    ax.errorbar(x + (0.01 if col == "el" else 0), mu, ci, fmt=mk + "-", ms=4, capsize=2, color=c, label=lab)
ax.axvline(2.5, color=GRAY, ls=":"); ax.text(2.52, 18, "switch point\nn = 2.5m", color=GRAY, fontsize=11)
ax.text(3.2, 12, "both versions\ntoo high\n(up to +2.4%)", color=RED, fontsize=12, ha="left")
ax.set_ylim(-3, 22); ax.set_xlim(0.8, 7)
ax.set_xlabel("n / m  (real count divided by number of registers)"); ax.set_ylabel("mean error (%)")
ax.set_title("The hand-over region (p = 14, error bars = 95% CI of the mean)"); ax.legend(loc="upper right")
plt.tight_layout(); plt.savefig("results/fig_handover.png", dpi=150); plt.close()

# ---------- 5. Real data ----------
r = pd.read_csv("results/exp4_real.csv")
t = r.true_distinct.iloc[0]
r["eb"] = (r.est_basic - t) / t * 100; r["el"] = (r.est_lc - t) / t * 100
gr = r.groupby("p"); ps = gr.eb.mean().index.values
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ax[0].plot(ps, gr.eb.mean(), "o-", color=BLUE, label="basic HLL")
ax[0].plot(ps, gr.el.mean(), "s-", color=ORANGE, label="with linear counting")
ax[0].axhline(0, color="k", lw=0.8)
ax[0].set_xlabel("p  (more registers →)"); ax[0].set_ylabel("mean error (%)")
ax[0].set_title("War and Peace: 17,445 different words"); ax[0].legend()
ax[0].annotate("n/m = 1.06:\nbasic is +28%", xy=(14, 27.85), xytext=(11.0, 20), arrowprops=dict(arrowstyle="->"), fontsize=11)
sd = gr.el.std().values; th = 104 / np.sqrt(2.0 ** ps)
ax[1].plot(ps, sd, "o-", color=ORANGE, label="measured spread (linear counting)")
ax[1].plot(ps, th, "k--", label="theory 1.04/√m")
ax[1].set_yscale("log"); ax[1].set_xlabel("p"); ax[1].set_ylabel("spread of error (%)")
ax[1].set_title("Spread follows the theory"); ax[1].legend()
plt.tight_layout(); plt.savefig("results/fig_real.png", dpi=150); plt.close()

# ---------- 6. Summary: HLL vs hash set at n = 10^7 ----------
e = pd.read_csv("results/exp3_p14.csv").iloc[-1]
fig, ax = plt.subplots(1, 2, figsize=(10, 4.2))
ax[0].bar(["HyperLogLog", "hash set"], [e.hll_bytes_packed6 / 1024, e.set_bytes / 1024], color=[GREEN, GRAY])
ax[0].set_yscale("log"); ax[0].set_ylabel("memory (KB, log scale)")
ax[0].set_title("Memory for 10 million items")
ax[0].text(0, e.hll_bytes_packed6 / 1024 * 1.4, "12 KB", ha="center", fontweight="bold")
ax[0].text(1, e.set_bytes / 1024 * 1.4, "345 MB", ha="center", fontweight="bold")
ax[0].set_ylim(1, 3e6)
ax[1].bar(["HyperLogLog", "hash set"], [e.hll_basic_ns, e.set_ns], color=[GREEN, GRAY])
ax[1].set_ylabel("time per item (ns)"); ax[1].set_title("Speed for 10 million items")
ax[1].text(0, e.hll_basic_ns + 4, f"{e.hll_basic_ns:.1f} ns", ha="center", fontweight="bold")
ax[1].text(1, e.set_ns + 4, f"{e.set_ns:.0f} ns", ha="center", fontweight="bold")
ax[1].set_ylim(0, 245)
plt.tight_layout(); plt.savefig("results/fig_summary.png", dpi=150); plt.close()
print("figures written")

# ---------- 7. Experiment 1, simple version for slides ----------
d = pd.read_csv("results/exp1_p14.csv")
d["eb"] = (d.est_basic - d.n) / d.n * 100; d["el"] = (d.est_lc - d.n) / d.n * 100
gg = d.groupby("n"); ns = gg.eb.mean().index.values
sw = 2.5 * 16384
fig, ax = plt.subplots(1, 2, figsize=(13, 5))
for a_ in ax:
    a_.axvline(sw, color=GRAY, ls=":", lw=2); a_.set_xscale("log")
    a_.set_xlabel("real number of different items")
ax[0].axhline(0, color="k", lw=0.8)
ax[0].plot(ns, gg.eb.mean(), "o-", ms=4, color=BLUE, label="basic HLL")
ax[0].plot(ns, gg.el.mean(), "s-", ms=4, color=ORANGE, label="with linear counting")
ax[0].set_ylim(-6, 30); ax[0].set_ylabel("average error (%)")
ax[0].set_title("(a) Average error")
ax[0].annotate("basic HLL is far above the\nchart for small counts\n(+1130% at 1,000 items)", xy=(1.9e4, 24), xytext=(11, 9), arrowprops=dict(arrowstyle="->"), fontsize=12, color=BLUE)
ax[0].text(sw * 1.15, 13, "dotted line = switch point\n(2.5 × registers = 40,960 items)\nlinear counting is used on the\nleft of it, the basic formula\non the right", fontsize=11, color=GRAY, va="center")
ax[0].legend(loc="upper right", fontsize=10.5)
ax[1].plot(ns, gg.eb.std().values, "o-", ms=4, color=BLUE, label="basic HLL")
ax[1].plot(ns, gg.el.std().values, "s-", ms=4, color=ORANGE, label="with linear counting")
ax[1].axhline(0.81, color="k", ls="--", label="theory 0.81%")
ax[1].plot([], [], color=GRAY, ls=":", lw=2, label="switch point (40,960 items)")
ax[1].set_yscale("log"); ax[1].set_ylim(0.2, 6); ax[1].set_ylabel("spread of the error (%)")
ax[1].set_title("(b) How much the error varies between runs"); ax[1].legend(loc="upper right")
plt.tight_layout(); plt.savefig("results/fig_exp1_simple.png", dpi=150); plt.close()
