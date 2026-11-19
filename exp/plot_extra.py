"""Supporting figure: memory and time of HLL vs an exact hash set at n = 10^7 (from experiment 3).
Usage (from project root):  python3 exp/plot_extra.py   -> results/fig_summary.png
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

GREEN, GRAY = "#2e7d32", "#666666"
plt.rcParams.update({"font.size": 18, "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 200})

e = pd.read_csv("results/exp3_p14.csv").iloc[-1]
fig, ax = plt.subplots(1, 2, figsize=(10, 5.5))
ax[0].bar(["HyperLogLog", "hash set"], [e.hll_bytes_packed6 / 1024, e.set_bytes / 1024], color=[GREEN, GRAY])
ax[0].set_yscale("log"); ax[0].set_ylabel("Memory (KB, log scale)")
ax[0].set_title("Memory, 10 million items")
ax[0].text(0, e.hll_bytes_packed6 / 1024 * 1.5, f"{e.hll_bytes_packed6 / 1024:.0f} KB", ha="center", fontweight="bold")
ax[0].text(1, e.set_bytes / 1024 * 1.5, f"{e.set_bytes / 1e6:.0f} MB", ha="center", fontweight="bold")
ax[0].set_ylim(1, 5e6)
ax[1].bar(["HyperLogLog", "hash set"], [e.hll_basic_ns, e.set_ns], color=[GREEN, GRAY])
ax[1].set_ylabel("Time per item (ns)"); ax[1].set_title("Speed, 10 million items")
ax[1].text(0, e.hll_basic_ns + 5, f"{e.hll_basic_ns:.1f} ns", ha="center", fontweight="bold")
ax[1].text(1, e.set_ns + 5, f"{e.set_ns:.0f} ns", ha="center", fontweight="bold")
ax[1].set_ylim(0, e.set_ns * 1.2)
plt.tight_layout(); plt.savefig("results/fig_summary.png", bbox_inches="tight", pad_inches=0.12); plt.close()
print("fig_summary written")
