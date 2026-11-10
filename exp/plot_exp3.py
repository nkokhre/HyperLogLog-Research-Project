"""Plot experiment 3. Usage: python3 plot_exp3.py results/exp3_p14.csv out.png"""
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = pd.read_csv(sys.argv[1]); out = sys.argv[2]
fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
for col, lab, mk in [("hll_basic", "Basic HLL (update only)", "o-"),
                     ("hll_lc", "HLL + linear counting (update + 1 estimate)", "s-"),
                     ("set", "Hash set (std::unordered_set)", "^-")]:
    ax[0].errorbar(d.n, d[col + "_ns"], [d[col + "_ns"] - d[col + "_q1"], d[col + "_q3"] - d[col + "_ns"]],
                   fmt=mk, capsize=2, label=lab)
ax[0].set_xscale("log"); ax[0].set_yscale("log")
ax[0].set_xlabel("true count n"); ax[0].set_ylabel("time per inserted item (ns)")
ax[0].set_title("(a) Time per item, p=14; median, bars = quartiles (21 runs)")
ax[0].legend()
ax[1].plot(d.n, d.set_bytes / 1024, "^-", label="Hash set (exact)")
ax[1].plot(d.n, d.hll_bytes_stored / 1024, "o-", label="HLL stored (1 byte/reg)")
ax[1].plot(d.n, d.hll_bytes_packed6 / 1024, "s--", label="HLL packed 6-bit")
ax[1].set_xscale("log"); ax[1].set_yscale("log")
ax[1].set_xlabel("true count n"); ax[1].set_ylabel("memory (KB)")
ax[1].set_title("(b) Memory"); ax[1].legend()
plt.tight_layout(); plt.savefig(out, dpi=140)
d["mem_ratio_stored"] = d.set_bytes / d.hll_bytes_stored
d["mem_ratio_packed"] = d.set_bytes / d.hll_bytes_packed6
d["lc_extra_est_ns"] = d.est_lc_ns - d.est_basic_ns
print(d[["n", "hll_basic_ns", "hll_lc_ns", "set_ns", "est_basic_ns", "est_lc_ns",
         "lc_extra_est_ns", "set_bytes", "mem_ratio_stored", "mem_ratio_packed"]].round(2).to_string())
