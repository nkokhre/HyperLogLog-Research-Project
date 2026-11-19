"""Analysis of experiment 5 (crossover). Reads results/exp5_raw.csv.gz (made by build/exp5_crossover).

Usage (from project root):  python3 exp/analyze_exp5.py
Writes:
  results/exp5_curves.csv     per (p, n/m): typical error of every method, bias, empty share, CI half-widths
  results/exp5_crossover.csv  per p: crossover c* with bootstrap 95% CI (+ simple-model prediction)
  results/exp5_scan.csv       per p and switch threshold: worst-case error and hand-over bump (train and test halves)
  results/exp5_rules.csv      per p: raw-only vs textbook 2.5m vs best rule, with 95% CIs, paired improvements
  results/exp5_best_threshold.csv, exp5_formula.csv   best switch threshold per p and the fitted formula c(p)
  results/exp6_real_crossover.csv   the same crossover measured on real text (War and Peace)

Definitions (used everywhere in the project):
  error of one estimate      = (estimate - n) / n
  typical error (%)          = root-mean-square of that error over the seeds (RMSE)
  Raw HLL                    = estimate_basic();  LC = pure linear counting m*ln(m/V), V clamped to >= 1
  textbook rule              = LC if raw E <= 2.5 m and V > 0, else raw
  crossover c*               = n*/m: smallest n/m after which raw's typical error <= LC's for every larger n/m
  worst case                 = largest typical error over the whole grid n/m = 0.25 .. 8
  hand-over bump             = largest |average error| (bias) of the combined estimator anywhere on the grid
  best rule                  = LC while raw E <= c*m, c chosen on half of the seeds (train), evaluated on the other half (test)
"""
import os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
RNG = np.random.default_rng(12345)  # fixed seed -> reproducible bootstrap
B = 1000                            # bootstrap replicates
C_GRID = np.round(np.arange(1.50, 5.0001, 0.05), 2)
F_GRID = np.round(np.arange(0.005, 0.3001, 0.005), 3)


def lc_value(m, v):
    return m * np.log(m / np.maximum(v, 1))


def load(name="exp5_raw.csv.gz"):
    df = pd.read_csv(os.path.join(RES, name))
    out = {}
    for p, g in df.groupby("p"):
        n = np.sort(g.n.unique()).astype(float)
        piv = lambda c: g.pivot(index="seed", columns="n", values=c).values
        m = 2 ** int(p)
        out[int(p)] = dict(m=m, n=n, t=n / m, seeds=np.sort(g.seed.unique()),
                           raw=piv("est_raw"), V=piv("empty"))
        out[int(p)]["lc"] = lc_value(m, out[int(p)]["V"])
    return out


def rule_e(d, c):
    """switch on raw estimate: LC while raw <= c*m (and V > 0)"""
    return np.where((d["raw"] <= c * d["m"]) & (d["V"] > 0), d["lc"], d["raw"])


def rule_f(d, f):
    """switch on empty share: LC while empty share > f"""
    return np.where((d["V"] > 0) & (d["V"] / d["m"] > f), d["lc"], d["raw"])


def rel_err(d, est):
    return (est - d["n"]) / d["n"]


def weights(nseeds, b=B):
    """bootstrap weights: row = replicate, col = seed (resample seeds with replacement)"""
    idx = RNG.integers(0, nseeds, size=(b, nseeds))
    w = np.zeros((b, nseeds))
    for r in range(b):
        w[r] = np.bincount(idx[r], minlength=nseeds)
    return w / nseeds


def curves_boot(e, w):
    """per replicate: rmse curve and bias curve over the grid"""
    return np.sqrt(w @ (e ** 2)), w @ e


def wc_bump(e, rows=None, w=None):
    """worst-case typical error and hand-over bump; point value or bootstrap array"""
    if w is None:
        e = e if rows is None else e[rows]
        return np.sqrt((e ** 2).mean(0)).max(), np.abs(e.mean(0)).max()
    rm, bi = curves_boot(e if rows is None else e[rows], w)
    return rm.max(1), np.abs(bi).max(1)


def crossover(t, rr, rl):
    d = rr - rl
    viol = np.where(d > 0)[0]
    if len(viol) == 0:
        return float(t[0])
    j = viol.max()
    if j == len(t) - 1:
        return float("nan")
    return float(t[j] + (t[j + 1] - t[j]) * d[j] / (d[j] - d[j + 1]))


def ci(a):
    return float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))


def main():
    data = load()
    ps = sorted(data)
    curves, cross, scan, rules, summ = [], [], [], [], []

    # ---------- crossover c* per p (all seeds) ----------
    for p in ps:
        d = data[p]; S = len(d["seeds"]); m = d["m"]; t = d["t"]
        er, el = rel_err(d, d["raw"]), rel_err(d, d["lc"])
        rr, rl = np.sqrt((er ** 2).mean(0)), np.sqrt((el ** 2).mean(0))
        w = weights(S)
        rr_b, _ = curves_boot(er, w); rl_b, _ = curves_boot(el, w)
        cs = crossover(t, rr, rl)
        cs_b = np.array([crossover(t, rr_b[i], rl_b[i]) for i in range(B)])
        lo, hi = ci(cs_b)
        # first-principles check: raw bias (m-independent) + raw noise vs LC noise
        cross.append(dict(p=p, m=m, seeds=S, c_star=cs, ci_lo=lo, ci_hi=hi,
                          f_star=float(np.exp(-cs)),
                          n_star=cs * m))
        # curves table
        er_t = rel_err(d, rule_e(d, 2.5))
        ci_r = np.stack([np.percentile(rr_b, 2.5, axis=0), np.percentile(rr_b, 97.5, axis=0)])
        ci_l = np.stack([np.percentile(rl_b, 2.5, axis=0), np.percentile(rl_b, 97.5, axis=0)])
        for j in range(len(t)):
            curves.append(dict(
                p=p, m=m, n=int(d["n"][j]), n_over_m=t[j], seeds=S,
                mean_abs_err_raw=np.abs(er[:, j]).mean(), mean_abs_err_lc=np.abs(el[:, j]).mean(),
                rmse_raw=rr[j], rmse_lc=rl[j],
                rmse_raw_ci_lo=ci_r[0, j], rmse_raw_ci_hi=ci_r[1, j],
                rmse_lc_ci_lo=ci_l[0, j], rmse_lc_ci_hi=ci_l[1, j],
                bias_raw=er[:, j].mean(), bias_lc=el[:, j].mean(),
                rmse_textbook=np.sqrt((er_t[:, j] ** 2).mean()), bias_textbook=er_t[:, j].mean(),
                empty_frac=(d["V"][:, j] / m).mean(), theory_raw_sd=1.04 / np.sqrt(m)))

    cross_df = pd.DataFrame(cross)

    # ---------- switch-threshold scan and rule comparison (train / test split) ----------
    best_c = {}
    for p in ps:
        d = data[p]; S = len(d["seeds"]); m = d["m"]
        rows_tr = np.arange(0, S, 2); rows_te = np.arange(1, S, 2)   # alternate seeds
        # candidate rules
        wc_tr_e = []
        for c in C_GRID:
            e = rel_err(d, rule_e(d, c))
            a_tr, b_tr = wc_bump(e, rows_tr); a_te, b_te = wc_bump(e, rows_te)
            wc_tr_e.append(a_tr)
            scan.append(dict(p=p, family="raw_estimate_threshold", param=c, wc_train=a_tr, bump_train=b_tr,
                             wc_test=a_te, bump_test=b_te))
        wc_tr_f = []
        for f in F_GRID:
            e = rel_err(d, rule_f(d, f))
            a_tr, b_tr = wc_bump(e, rows_tr); a_te, b_te = wc_bump(e, rows_te)
            wc_tr_f.append(a_tr)
            scan.append(dict(p=p, family="empty_share_threshold", param=f, wc_train=a_tr, bump_train=b_tr,
                             wc_test=a_te, bump_test=b_te))
        best_c[p] = dict(c=float(C_GRID[int(np.argmin(wc_tr_e))]), f=float(F_GRID[int(np.argmin(wc_tr_f))]))
        # bootstrap CI of the best c (train half)
        e_all = np.stack([rel_err(d, rule_e(d, c))[rows_tr] for c in C_GRID])   # C x S/2 x J
        w = weights(len(rows_tr), 300)
        wc_b = np.stack([np.sqrt(w @ (e_all[i] ** 2)).max(1) for i in range(len(C_GRID))])  # C x b
        arg_b = C_GRID[wc_b.argmin(0)]
        best_c[p]["c_ci"] = ci(arg_b)
    scan_df = pd.DataFrame(scan)

    # simple formula c(p) = a + b*p fitted to the best c per p (train half only)
    px = np.array(ps, dtype=float); cy = np.array([best_c[p]["c"] for p in ps])
    slope, icpt = np.polyfit(px, cy, 1)
    formula = lambda p: icpt + slope * p

    for p in ps:
        d = data[p]; S = len(d["seeds"]); m = d["m"]
        rows_te = np.arange(1, S, 2)
        w = weights(len(rows_te))
        c_best, c_form = best_c[p]["c"], float(round(formula(p), 2))
        specs = {"raw_only": d["raw"], "textbook_2.5m": rule_e(d, 2.5),
                 "best_c_per_p": rule_e(d, c_best), "formula_c(p)": rule_e(d, c_form),
                 "best_empty_share": rule_f(d, best_c[p]["f"])}
        params = {"raw_only": float("nan"), "textbook_2.5m": 2.5, "best_c_per_p": c_best,
                  "formula_c(p)": c_form, "best_empty_share": best_c[p]["f"]}
        wcb, bpb = {}, {}
        for name, est in specs.items():
            e = rel_err(d, est)
            wc, bp = wc_bump(e, rows_te)
            wcb[name], bpb[name] = wc_bump(e, rows_te, w)
            lo_w, hi_w = ci(wcb[name]); lo_b, hi_b = ci(bpb[name])
            rules.append(dict(p=p, m=m, rule=name, param=params[name], wc=wc, wc_ci_lo=lo_w, wc_ci_hi=hi_w,
                              bump=bp, bump_ci_lo=lo_b, bump_ci_hi=hi_b))
        for name in ("best_c_per_p", "formula_c(p)", "best_empty_share"):
            for metric, arr in (("wc", wcb), ("bump", bpb)):
                diff = arr["textbook_2.5m"] - arr[name]
                ratio = arr[name] / arr["textbook_2.5m"]
                lo, hi = ci(diff); rlo, rhi = ci(ratio)
                for r in rules:
                    if r["p"] == p and r["rule"] == name:
                        r[f"{metric}_gain_vs_textbook"] = float(np.mean(diff))
                        r[f"{metric}_gain_ci_lo"], r[f"{metric}_gain_ci_hi"] = lo, hi
                        r[f"{metric}_ratio_to_textbook"] = float(np.mean(ratio))
                        r[f"{metric}_ratio_ci_lo"], r[f"{metric}_ratio_ci_hi"] = rlo, rhi

    rules_df = pd.DataFrame(rules)

    # best rule columns in the curves table (evaluated on all seeds, for plotting)
    cur = pd.DataFrame(curves)
    add_b, add_bb = [], []
    for p in ps:
        d = data[p]; e = rel_err(d, rule_e(d, best_c[p]["c"]))
        add_b += list(np.sqrt((e ** 2).mean(0))); add_bb += list(e.mean(0))
    cur["rmse_best"] = add_b; cur["bias_best"] = add_bb
    cur["best_c"] = cur.p.map(lambda p: best_c[p]["c"])

    # model check: raw bias b(t) is (almost) independent of m, LC noise has a known formula,
    # raw noise = measured raw typical error at n/m = 8. Solve  b(t)^2 + s_raw^2 = (e^t - t - 1)/(t^2 m).
    big = [p for p in ps if p >= 10]
    tt = data[ps[0]]["t"]
    b_t = np.mean([rel_err(data[p], data[p]["raw"]).mean(0) for p in big], axis=0)
    model = []
    for p in ps:
        m = data[p]["m"]; er = rel_err(data[p], data[p]["raw"])
        s_raw2 = (er[:, -1] ** 2).mean()  # typical error at n/m = 8 (bias ~ 0 there)
        lhs = b_t ** 2 + s_raw2
        rhs = (np.exp(tt) - tt - 1) / (tt ** 2 * m)
        model.append(crossover(tt, np.sqrt(lhs), np.sqrt(rhs)))
    cross_df["c_star_model"] = model

    # ---------- real text (exp6): same crossover on War and Peace ----------
    real = load("exp6_real_raw.csv.gz")
    rc = []
    for p in sorted(real):
        d = real[p]; S = len(d["seeds"]); t = d["t"]
        er, el = rel_err(d, d["raw"]), rel_err(d, d["lc"])
        rr, rl = np.sqrt((er ** 2).mean(0)), np.sqrt((el ** 2).mean(0))
        w = weights(S)
        rr_b, _ = curves_boot(er, w); rl_b, _ = curves_boot(el, w)
        cs = crossover(t, rr, rl)
        cs_b = np.array([crossover(t, rr_b[i], rl_b[i]) for i in range(B)])
        lo, hi = ci(cs_b)
        syn = float(cross_df.loc[cross_df.p == p, "c_star"].iloc[0])
        rc.append(dict(p=p, m=d["m"], seeds=S, max_n_over_m=float(t.max()), c_star_real=cs, ci_lo=lo, ci_hi=hi,
                       c_star_synthetic=syn))
        for j in range(len(t)):
            curves.append(dict(p=-p, m=d["m"], n=int(d["n"][j]), n_over_m=t[j], seeds=S, rmse_raw=rr[j], rmse_lc=rl[j]))
    real_df = pd.DataFrame(rc)
    real_df.round(4).to_csv(os.path.join(RES, "exp6_real_crossover.csv"), index=False)
    pd.DataFrame([r for r in curves if r["p"] < 0]).round(6).to_csv(os.path.join(RES, "exp6_real_curves.csv"), index=False)
    curves[:] = [r for r in curves if r["p"] > 0]
    print("\n== real text (War and Peace): crossover vs synthetic ==")
    print(real_df.round(3).to_string(index=False))

    # ---------- write ----------
    cur.round(6).to_csv(os.path.join(RES, "exp5_curves.csv"), index=False)
    cross_df.round(4).to_csv(os.path.join(RES, "exp5_crossover.csv"), index=False)
    scan_df.round(6).to_csv(os.path.join(RES, "exp5_scan.csv"), index=False)
    rules_df.round(6).to_csv(os.path.join(RES, "exp5_rules.csv"), index=False)
    bc = pd.DataFrame([dict(p=p, m=data[p]["m"], best_c=best_c[p]["c"], best_c_ci_lo=best_c[p]["c_ci"][0],
                            best_c_ci_hi=best_c[p]["c_ci"][1], best_f=best_c[p]["f"]) for p in ps])
    bc["formula_c"] = [round(formula(p), 2) for p in ps]
    bc.to_csv(os.path.join(RES, "exp5_best_threshold.csv"), index=False)
    fit = pd.DataFrame([dict(intercept=icpt, slope_per_bit_of_p=slope)])
    fit.round(4).to_csv(os.path.join(RES, "exp5_formula.csv"), index=False)

    pd.set_option("display.width", 220); pd.set_option("display.max_columns", 30)
    print("== crossover c* (equal typical error) ==")
    print(cross_df.round(3).to_string(index=False))
    print("\n== best thresholds (train half) ==")
    print(bc.round(3).to_string(index=False))
    print(f"\nformula c(p) = {icpt:.3f} + {slope:.4f} * p")
    print("\n== rules on the test half ==")
    cols = ["p", "rule", "param", "wc", "wc_ci_lo", "wc_ci_hi", "bump", "bump_ci_lo", "bump_ci_hi"]
    print((rules_df[cols].assign(wc=lambda x: x.wc * 100, wc_ci_lo=lambda x: x.wc_ci_lo * 100, wc_ci_hi=lambda x: x.wc_ci_hi * 100,
                                 bump=lambda x: x.bump * 100, bump_ci_lo=lambda x: x.bump_ci_lo * 100, bump_ci_hi=lambda x: x.bump_ci_hi * 100)).round(3).to_string(index=False))
    print("\n== improvements vs textbook (ratio of worst case, bump) ==")
    cols2 = ["p", "rule", "wc_ratio_to_textbook", "wc_ratio_ci_lo", "wc_ratio_ci_hi", "bump_ratio_to_textbook", "bump_ratio_ci_lo", "bump_ratio_ci_hi"]
    print(rules_df[rules_df.rule.isin(["best_c_per_p", "formula_c(p)", "best_empty_share"])][cols2].round(3).to_string(index=False))
    # large-n agreement with theory
    print("\n== large-n check: typical error of raw HLL at n/m = 8 vs 1.04/sqrt(m) ==")
    for p in ps:
        c = cur[(cur.p == p)].iloc[-1]
        print(f"p={p}: measured {100*c.rmse_raw:.3f}%  theory {100*c.theory_raw_sd:.3f}%  ratio {c.rmse_raw/c.theory_raw_sd:.3f}")


if __name__ == "__main__":
    main()
