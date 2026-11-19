"""Explanatory figures for the slides (build-up slides before the real plots).
Figures marked 'illustration' are NOT data; the others are simulated/plotted from experiment output.
Usage: python3 exp/plot_schematics.py  (from project root)"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
RAW, LC, TEXT, BEST, INK, GRAYC = "#1f77b4", "#ff7f0e", "#8e44ad", "#2e7d32", "#222222", "#777777"
plt.rcParams.update({"font.size": 17, "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 3.2, "savefig.dpi": 200})


def save(fig, name):
    fig.savefig(os.path.join(RES, name), bbox_inches="tight", pad_inches=0.15); plt.close(fig)


def box(ax, x, y, w, h, t, fc, ec, fs=17, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03", fc=fc, ec=ec, lw=2.4))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal")


def arrow(ax, x1, y1, x2, y2, c=GRAYC):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=22, lw=2.4, color=c))


# ---- slide 3: the question on a number line (illustration) ----
fig, ax = plt.subplots(figsize=(12.5, 3.6)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 3.6)
ax.add_patch(Rectangle((0.3, 1.2), 4.4, 1.0, fc="#fdebd8", ec=LC, lw=2.6)); ax.text(2.5, 1.7, "Linear counting\nis better", ha="center", va="center", fontsize=19, fontweight="bold", color="#b35a00")
ax.add_patch(Rectangle((4.7, 1.2), 2.6, 1.0, fc="#eeeeee", ec=INK, lw=2.6)); ax.text(6.0, 1.7, "?", ha="center", va="center", fontsize=40, fontweight="bold", color=INK)
ax.add_patch(Rectangle((7.3, 1.2), 4.4, 1.0, fc="#dbe9f6", ec=RAW, lw=2.6)); ax.text(9.5, 1.7, "Plain HLL\nis enough", ha="center", va="center", fontsize=19, fontweight="bold", color="#124e78")
arrow(ax, 0.3, 0.7, 11.7, 0.7, INK)
ax.text(6.0, 0.15, "number of distinct items n  (few → many)", ha="center", fontsize=16)
ax.text(6.0, 2.9, "Where exactly is the border?", ha="center", fontsize=19, fontweight="bold", color=INK)
save(fig, "schem_question.png")

# ---- slide 6: a sketch filling up (simulated balls into registers) ----
rng = np.random.default_rng(7)
fig, axs = plt.subplots(1, 3, figsize=(10.5, 4.4))
M = 64
for ax, t in zip(axs, (0.5, 2, 6)):
    n = int(t * M); hit = np.zeros(M, bool); hit[rng.integers(0, M, n)] = True
    g = hit.reshape(8, 8)
    ax.imshow(g, cmap=matplotlib.colors.ListedColormap(["#ffffff", RAW]), vmin=0, vmax=1)
    for i in range(9):
        ax.axhline(i - 0.5, color="#999999", lw=1); ax.axvline(i - 0.5, color="#999999", lw=1)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(True)
    ax.set_title(f"n / m = {t:g}\n{hit.mean() * 100:.0f}% used", fontsize=20, fontweight="bold")
fig.text(0.5, -0.04, "Illustration: 64 registers; each item lands in a random register.\nBlue = used, white = still empty.", ha="center", fontsize=15, color=GRAYC)
save(fig, "schem_filling.png")

# ---- slide 7: same n/m, same picture (simulated) ----
fig, axs = plt.subplots(1, 2, figsize=(9.5, 5.6))
for ax, (m, side) in zip(axs, ((1024, 32), (16384, 128))):
    n = 2 * m; hit = np.zeros(m, bool); hit[rng.integers(0, m, n)] = True
    ax.imshow(hit.reshape(side, side), cmap=matplotlib.colors.ListedColormap(["#ffffff", RAW]), interpolation="nearest")
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(True); sp.set_color("#999999")
    ax.set_title(f"m = {m:,} registers\nn = {n:,} items\nn / m = 2", fontsize=18, fontweight="bold")
    ax.set_xlabel(f"{hit.mean() * 100:.0f}% of registers used", fontsize=18, fontweight="bold", color=RAW)
fig.text(0.5, -0.03, "Illustration (simulated): each pixel = one register; blue = used, white = empty", ha="center", fontsize=14, color=GRAYC)
save(fig, "schem_same_ratio.png")

# ---- slide 8: what "error" means (worked number) ----
fig, ax = plt.subplots(figsize=(12.5, 3.4)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 3.4)
ax.plot([0.8, 11.2], [1.5, 1.5], color=INK, lw=3)
ax.plot([3.0], [1.5], "o", color=INK, ms=20); ax.plot([7.2], [1.5], "o", color=RAW, ms=20)
ax.text(3.0, 2.15, "true count\n10,000", ha="center", fontsize=18, fontweight="bold", color=INK)
ax.text(7.2, 2.15, "estimate\n10,300", ha="center", fontsize=18, fontweight="bold", color=RAW)
ax.annotate("", xy=(7.0, 1.0), xytext=(3.2, 1.0), arrowprops=dict(arrowstyle="<|-|>", color=GRAYC, lw=2.4))
ax.text(5.1, 0.45, "off by 300 = 3% of 10,000", ha="center", fontsize=18, fontweight="bold", color=GRAYC)
save(fig, "schem_error.png")

# ---- slide 10: how to read the next graph (illustration) ----
fig, ax = plt.subplots(figsize=(9.5, 5.4))
x = np.linspace(0, 1, 100)
ax.plot(x, 0.9 - 0.8 * x ** 0.7, color=RAW); ax.plot(x, 0.15 + 0.7 * x ** 1.8, color=LC)
ax.text(0.04, 0.82, "Method A", color=RAW, fontsize=22, fontweight="bold"); ax.text(0.72, 0.9, "Method B", color=LC, fontsize=22, fontweight="bold")
ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel("how full the sketch is  →", fontsize=18); ax.set_ylabel("error  →  (higher = worse)", fontsize=18)
ax.set_title("Question for every graph:  which line is LOWER, and where?", fontsize=19, fontweight="bold", color=INK, pad=16)
ax.text(0.99, 0.02, "illustration, not real data", transform=ax.transAxes, ha="right", fontsize=13, color=GRAYC)
ax.annotate("lines cross: the border", xy=(0.52, 0.5), xytext=(0.42, 0.12), fontsize=17, color=INK, arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.2))
save(fig, "schem_two_curves.png")

# ---- slide 14: what we would see if one rule fits all sizes (illustration) ----
fig, axs = plt.subplots(1, 2, figsize=(10.5, 5.0), sharey=True)
rows = (0.78, 0.5, 0.22); names = ("small", "medium", "large")
for ax, pos, ttl in ((axs[0], [3.0, 3.0, 3.0], "If ONE rule fits every size:\nthe crossovers line up"),
                     (axs[1], [2.1, 3.0, 4.2], "If NOT:\nthe crossovers drift")):
    ax.set_xlim(1, 6); ax.set_ylim(0, 1); ax.set_yticks([]); ax.spines["left"].set_visible(False)
    for y_, x_, nm in zip(rows, pos, names):
        ax.plot([1.0, 6.0], [y_, y_], color="#dddddd", lw=2, zorder=1)
        ax.plot([x_], [y_], "o", color=INK, ms=24, zorder=5)
        ax.text(1.05, y_ + 0.09, nm, fontsize=14, color=GRAYC)
    ax.set_title(ttl, fontsize=18, fontweight="bold")
    ax.set_xlabel("items per register (n/m)  →", fontsize=16)
axs[0].axvline(3.0, color=INK, ls="--", lw=2)
fig.text(0.5, -0.1, "illustration, not real data  (each dot = the crossover of one sketch size)", ha="center", fontsize=13.5, color=GRAYC)
save(fig, "schem_expectation.png")

# ---- slide 17: the rule uses only what the sketch can see ----
fig, ax = plt.subplots(figsize=(13, 4.8)); ax.axis("off"); ax.set_xlim(0, 13); ax.set_ylim(0, 4.8)
box(ax, 0.1, 1.8, 2.9, 1.3, "the sketch\n(m registers)", "#eaf1fb", RAW, 18, True)
arrow(ax, 3.1, 2.45, 3.9, 2.45)
box(ax, 4.0, 1.5, 3.0, 1.9, "it can tell us:\nraw estimate  E\nempty registers  V", "#fff4e5", LC, 17)
arrow(ax, 7.1, 2.45, 7.9, 2.45)
box(ax, 8.0, 1.8, 2.3, 1.3, "E ≤ c · m\nand V > 0 ?", "#f3e8f8", TEXT, 18, True)
arrow(ax, 10.4, 2.9, 11.2, 3.7, BEST); arrow(ax, 10.4, 2.0, 11.2, 1.2, RAW)
box(ax, 11.3, 3.3, 1.65, 0.9, "yes:\nLC", "#fdebd8", LC, 17, True)
box(ax, 11.3, 0.7, 1.65, 0.9, "no:\nraw E", "#dbe9f6", RAW, 17, True)
ax.text(6.5, 0.2, "The true count n is never needed.  c is the switch place we are looking for (textbook: 2.5).", ha="center", fontsize=16, color=INK)
save(fig, "schem_rule.png")
print("schematics written")
