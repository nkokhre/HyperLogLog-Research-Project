"""Builds slides.html (the defense deck): 23 main slides + 4 backup slides.

Run from the project root:   python3 report/make_slides.py      (needs pandas)
Open slides.html in a browser (or VS Code: right-click -> "Open with Live Server").
Keys: -> / space = next, <- = back, Home / End, N = speaker notes, P = print view (one page per slide).

Every number on a slide is read from results/*.csv at build time; the source file is written in the notes.
Colour code (same in every plot and slide): plain HLL = blue, linear counting = orange,
textbook 2.5 rule = purple, best rule = green.
"""
import html
import math
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
SECTIONS = ["Question", "Method", "Results", "Impact", "Takeaway"]
MAIN_SLIDES = 23

# ------------------------------------------------------------------ numbers from results/
cross = pd.read_csv(os.path.join(RES, "exp5_crossover.csv")).set_index("p")
rules = pd.read_csv(os.path.join(RES, "exp5_rules.csv"))
bestc = pd.read_csv(os.path.join(RES, "exp5_best_threshold.csv")).set_index("p")
formula = pd.read_csv(os.path.join(RES, "exp5_formula.csv")).iloc[0]
real = pd.read_csv(os.path.join(RES, "exp6_real_crossover.csv")).set_index("p")
curves = pd.read_csv(os.path.join(RES, "exp5_curves.csv"))
exp3 = pd.read_csv(os.path.join(RES, "exp3_p14.csv")).iloc[-1]
c14 = curves[curves.p == 14].sort_values("n_over_m")
SEEDS = int(curves.seeds.iloc[0])
GRID = c14.n_over_m.nunique()
PS = sorted(cross.index)


def rule(p, name):
    return rules[(rules.p == p) & (rules.rule == name)].iloc[0]


tb, bs, fm, raw14 = (rule(14, n) for n in ("textbook_2.5m", "best_c_per_p", "formula_c(p)", "raw_only"))
cs = {p: cross.loc[p, "c_star"] for p in PS}
ci = {p: (cross.loc[p, "ci_lo"], cross.loc[p, "ci_hi"]) for p in PS}
n_star = {p: cross.loc[p, "n_star"] for p in PS}
raw_t025 = c14.rmse_raw.iloc[0] * 100
lc_t025 = c14.rmse_lc.iloc[0] * 100
lc_t8 = c14.rmse_lc.iloc[-1] * 100
raw_t8 = c14.rmse_raw.iloc[-1] * 100
empty_at_cross = 100 * math.exp(-cs[14])
big_meas = {p: curves[curves.p == p].sort_values("n_over_m").rmse_raw.iloc[-1] * 100 for p in PS}
big_theory = {p: 104 / math.sqrt(2 ** p) for p in PS}
model_dev = max(abs(cross.loc[p, "c_star_model"] - cs[p]) for p in PS if p >= 10)
by_p = {p: rule(p, "best_c_per_p").wc_ratio_to_textbook for p in PS}
lo_n, hi_n = cross.n_star.min(), cross.n_star.max()
best14 = bestc.loc[14, "best_c"]


def pct(v, d=2):
    return f"{v:.{d}f}%"


# ------------------------------------------------------------------ slide builders
SLIDES = []
E = html.escape


def add(section, title, body, notes, source=""):
    SLIDES.append(dict(section=section, title=title, body=body, notes=notes, source=source))


def ul(items, cls=""):
    return f'<ul class="{cls}">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def img(name, alt, cls="plot"):
    return f'<img class="{cls}" src="results/{name}" alt="{E(alt)}">'


def how(text):
    return f'<div class="how"><b>How to read this:</b> {text}</div>'


def graph(name, alt, side, how_text, wide=False):
    if wide or not side:
        return f'<div class="wide">{img(name, alt)}</div>{how(how_text)}'
    return (f'<div class="graph"><div class="pic">{img(name, alt)}</div>'
            f'<div class="side">{ul(side)}</div></div>{how(how_text)}')


def b(t, c=""):
    return f'<b class="{c}">{t}</b>'


# ================================================================== QUESTION
add("Question", "When does linear counting stop helping HyperLogLog?",
    '<div class="titlepage"><h1 class="big">When does linear counting stop helping HyperLogLog?</h1>'
    '<p class="sub">Measuring the crossover between linear counting and plain HLL</p>'
    '<p class="who">Ibrahim and Nika · Advanced Algorithms &amp; Data Structures · Fall 2026</p></div>',
    "Last week we presented HyperLogLog and linear counting. This project asks one precise question about them: "
    "at which number of distinct items does linear counting stop helping, and what should the switch rule be?")

add("Question", "Recap from last week: two ways to estimate how many different items we saw",
    '<div class="cards">'
    '<div class="card raw"><h3>Plain HLL</h3><p>m registers keep the longest run of zeros seen.<br>The estimate is computed from their values.</p></div>'
    '<div class="card lc"><h3>Linear counting (LC)</h3><p>Count the empty registers V.<br>Estimate = m · ln(m / V).<br>Accurate while many registers are empty.</p></div>'
    '</div><p class="note">m = number of registers (the sketch\'s memory slots)</p>',
    "One line each. Plain HLL turns the values in its m registers into an estimate. Linear counting only counts how many registers are still empty. "
    "We presented both last week, so this is only a reminder.")

add("Question", "The question: below which number of items does linear counting help, and above which is plain HLL enough?",
    f'<div class="center">{img("schem_question.png", "number line: linear counting zone, unknown border, plain HLL zone", "plot mid")}</div>'
    '<p class="callout">We call this border the <b>crossover</b>.</p>',
    "This is the whole project in one picture. For few items, linear counting is better. For many items, plain HLL is enough. "
    "Somewhere in between is a border. We call that border the crossover and we want to measure it.",
    "illustration, not data")

add("Question", "Today the border is a magic constant: switch to linear counting when the estimate is at most 2.5 × m",
    '<div class="rulebox text">E ≤ 2.5 · m &nbsp; → &nbsp; use linear counting</div>'
    + ul(["How good is 2.5?", "Is one number right for every sketch size?"], "bigl"),
    "The textbook rule says: if the raw HLL estimate E is at most 2.5 times m, and some register is empty, use linear counting. "
    "Nobody told us why 2.5, or whether it is right for small and for large sketches. That gap is what we study.")

add("Question", "Our goal: measure the crossover and test whether one threshold fits every sketch size",
    '<div class="two"><div><h3 class="navy">We will measure</h3>'
    + ul(["The crossover <b>c* = n*/m</b>", "The best switch rule that uses only what the sketch can see",
          "How much that rule shrinks the biggest errors vs the 2.5 rule"])
    + '</div><div class="card lc hyp"><h3>Hypothesis</h3><p>One fixed crossover (about 2.5) works for every sketch size.</p></div></div>',
    "We will measure the crossover as a ratio c* = n*/m, because we think the border scales with the number of registers. "
    "Then we look for the best switch rule that only uses what the sketch can observe, and measure how much it shrinks the biggest errors compared with the textbook 2.5 rule. "
    "Our hypothesis is that one fixed c*, around 2.5, works for every sketch size. The later slides confirm or reject it.")

# ================================================================== METHOD
add("Method", "n / m tells us how full the sketch is",
    graph("schem_filling.png", "three grids of 64 registers filling up",
          ["m = number of registers (memory slots)", "n / m = distinct items per register on average", "= how full the sketch is"],
          "each grid = 64 registers (squares). Blue = register used, white = still empty. Left to right = more items per register. Look at how the white squares disappear."),
    "Before any graph: m is the number of registers, the sketch's memory slots. n/m is the average number of distinct items per register, so it tells us how full the sketch is. "
    "Look at the three grids: with half an item per register about half the registers are used; at six items per register nearly all are used. "
    "Plain HLL and linear counting care about how full the sketch is, not about the absolute n.",
    "illustration simulated with a fixed seed in exp/plot_schematics.py (not experiment data)")

add("Method", "The same n/m gives the same picture, whatever the sketch size",
    graph("schem_same_ratio.png", "two sketches of different size at n/m = 2",
          ["p = 14: m = 16,384, so n / m = 2 means n = 32,768 items", "Both sketches: about 87% of registers used",
           "So we measure fill level with n / m, and one rule could fit every size"],
          "each pixel = one register. Blue = used, white = empty. Left: 1,024 registers, right: 16,384 registers. Look: both have the same share of white pixels."),
    "Here are two sketches of very different sizes: 1,024 and 16,384 registers. We feed each one twice as many items as it has registers, so n/m = 2. "
    "That is 2,048 items for the small one and 32,768 for the large one. Both end up with about 87 percent of their registers used. "
    "That is why we describe how full the sketch is with n/m, and why one switching rule could in principle work for every size.",
    "illustration simulated with a fixed seed in exp/plot_schematics.py (not experiment data)")

add("Method", "Error = how far the estimate is from the true count, as a percentage",
    f'<div class="center">{img("schem_error.png", "worked example: true count 10,000, estimate 10,300, 3% error", "plot mid")}</div>'
    + ul(["True count is known: we generate the items ourselves",
          "<b>Typical error</b> = the usual size of this mistake over many runs (root-mean-square)"]),
    "We always measure error the same way: the distance between the estimate and the true count, as a percentage of the true count. "
    "For example, a true count of 10,000 and an estimate of 10,300 is a 3 percent error. We know the true count because we generate the items ourselves. "
    "Because every estimate is random, we repeat each experiment many times and report the typical error, which is the usual size of the mistake over those runs.",
    "illustration, not data")

add("Method", f"Experiment: 5 sketch sizes × {GRID} fill levels × {SEEDS} runs",
    '<div class="tiles">'
    '<div class="tile"><div class="tb">p = 8 … 16</div><div class="ts">5 sketch sizes<br>256 to 65,536 registers</div></div>'
    f'<div class="tile"><div class="tb">{GRID} fill levels</div><div class="ts">n / m from 0.25 to 8<br>(fine steps near the crossover)</div></div>'
    f'<div class="tile"><div class="tb">{SEEDS} runs</div><div class="ts">per point; same data<br>for every method</div></div></div>'
    '<p class="note center">Compared: plain HLL, linear counting, and switch rules (textbook 2.5 and our best)</p>',
    f"We tested five sketch sizes, p from 8 to 16. For each size we looked at {GRID} fill levels, n/m from 0.25 to 8, with a fine grid around where we expect the crossover. "
    f"Every point is {SEEDS} independent runs, and plain HLL, linear counting and every switch rule see exactly the same sketches. "
    "To avoid fooling ourselves, we choose the best switch place on one half of the runs and measure it on the other half.",
    "exp/exp5_crossover.cpp, results/exp5_raw.csv.gz")

# ================================================================== RESULTS
add("Results", "How to read the next graph: which line is lower, and where?",
    graph("schem_two_curves.png", "two crossing curves, illustration",
          ["x-axis: how full the sketch is", "y-axis: error, so lower is better", "Where the lines cross, the better method changes"],
          "x-axis = how full the sketch is, y-axis = error (higher = worse), each line = one method. Look for where the lines cross."),
    "All our graphs have the same shape, so here is a simple one first. The x-axis says how full the sketch is. The y-axis says the error, so higher is worse. "
    "Two methods are two lines. The question for every graph is: which line is lower, and where? Where the lines cross, the better method changes.",
    "illustration, not data")

add("Results", "Plain HLL is far off when the sketch is mostly empty; linear counting stays steady",
    graph("exp5_plotA_p14_plain.png", "typical error vs items per register, p = 14",
          [f'{b("Blue:", "raw")} plain HLL, {raw_t025:.0f}% error at 0.25 items per register, falling to {raw_t8:.2f}% at 8',
           f'{b("Orange:", "lc")} linear counting, {lc_t025:.2f}% at the start, rising to {lc_t8:.1f}% at 8'],
          f"x-axis = items per register (n/m); top axis = the same in real items for p = 14. y-axis = typical error (log scale). Blue = plain HLL, orange = linear counting. Shaded band = 95% confidence interval (CI, the range the true value lies in with 95% certainty) over {SEEDS} runs. Look for: which line is lower on the left and on the right?"),
    "(1) The x-axis is items per register, n/m, so how full the sketch is; the top axis shows the same position in actual items for p = 14, where m = 16,384. "
    "(2) The y-axis is the typical error of the estimate, on a log scale where each gridline is ten times more. "
    f"(3) Blue is plain HLL, orange is linear counting; the thin shaded bands are the 95 percent confidence intervals over {SEEDS} runs. "
    f"(4) On the left, plain HLL is at {raw_t025:.0f} percent error while linear counting is at {lc_t025:.2f} percent. On the right the orange line climbs to {lc_t8:.1f} percent and the blue line is at {raw_t8:.2f} percent. "
    "(5) Each method has a region where it is better, so there must be a border between them.",
    "results/exp5_curves.csv (p = 14 rows); plot: exp/plot_exp5.py")

lo, hi = ci[14]
add("Results", f"Linear counting wins below {cs[14]:.1f} items per register; plain HLL wins above",
    graph("exp5_plotA_p14_crossover.png", "same graph with the crossover marked",
          [f"Crossover c* = {b(f'{cs[14]:.2f}', 'navy')} (95% CI {lo:.2f} to {hi:.2f})",
           f"≈ {n_star[14]:,.0f} items for p = 14",
           "Left of the dashed line linear counting is lower; right of it plain HLL is lower"],
          "same graph as before. Dashed line = crossover, gray band = its 95% CI, shaded zones = which method is better. Look for: where the two lines cross."),
    "(1) Same x-axis as before: items per register. (2) Same y-axis: typical error. (3) Blue is plain HLL and orange is linear counting. "
    f"(4) The dashed vertical line is where the two lines cross: {cs[14]:.2f} items per register, with a 95 percent interval from {lo:.2f} to {hi:.2f}. "
    f"For p = 14 that is about {n_star[14]:,.0f} items. (5) Below that point linear counting has the lower error; above it plain HLL does. "
    "We define the crossover as the smallest point after which plain HLL stays at least as good.",
    "results/exp5_crossover.csv, results/exp5_curves.csv; bootstrap over runs in exp/analyze_exp5.py")

add("Results", "Why: linear counting runs out of empty registers",
    graph("exp5_plotE_empty_share.png", "share of empty registers vs items per register",
          [f"At the crossover ({cs[14]:.2f}) only {empty_at_cross:.1f}% of registers are still empty",
           "Linear counting needs empty registers", "When they run out, it has nothing to work with"],
          "x-axis = items per register, y-axis = share of registers still empty (%). Dots = measured, dashed = formula e^(−n/m). Look for: how close to zero the curve is at the crossover."),
    "(1) The x-axis is items per register again. (2) The y-axis is the share of registers that are still empty. "
    "(3) The dots are measured, the dashed gray line is the simple formula e to the minus n over m, and they agree. "
    f"(4) At the dashed vertical line, the crossover, only about {empty_at_cross:.1f} percent of the registers are still empty. "
    "(5) Linear counting reads the empty registers, so when almost none are left it has very little information and its error grows. That is why plain HLL takes over.",
    "results/exp5_curves.csv (empty_frac column, p = 14)")

add("Results", "Does the crossover depend on the sketch size? Two possible answers",
    graph("schem_expectation.png", "illustration: crossovers lined up vs drifting",
          ["Is c* the same for every sketch size?", "If yes: one switch rule fits all", "If no: the rule must depend on size"],
          "each row = one sketch size, each dot = the crossover of that size (an illustration, not data). Look for: do the dots line up in one column?"),
    "Now the central question. Is the crossover the same number of items per register for every sketch size? If yes, one switching rule fits all sizes. "
    "If not, the rule has to depend on the size. The picture is only an illustration of those two possible worlds, not data. The next slides show what we measured.",
    "illustration, not data")

add("Results", f"On the n/m axis the crossovers fall between {min(cs.values()):.1f} and {max(cs.values()):.1f}; in items they range from {lo_n:,.0f} to {hi_n:,.0f}",
    graph("exp5_plotA_all_p.png", "all sketch sizes on an n axis and on an n/m axis", None,
          "both panels show the same lines (blue = plain HLL, orange = linear counting, one pair per sketch size p = 8 to 16). Left x-axis = items n, right x-axis = items per register n/m. Dots = crossovers. Look at how spread out the dots are in each panel.", wide=True),
    "(1) On the left, the x-axis is the plain number of items n. On the right it is items per register, n over m. "
    "(2) The y-axis is the typical error on both sides. (3) Blue lines are plain HLL and orange lines are linear counting; each sketch size p from 8 to 16 has its own thin pair, and the dots are the crossovers. "
    f"(4) On the left the dots are spread from {lo_n:,.0f} to {hi_n:,.0f} items. On the right they stay between {min(cs.values()):.1f} and {max(cs.values()):.1f}. "
    "(5) So n over m is the right axis: it removes almost all of the size dependence. But the dots on the right still drift, which the next slide quantifies.",
    "results/exp5_curves.csv, results/exp5_crossover.csv")

add("Results", "The crossover rises with sketch size, so no single threshold fits every size",
    graph("exp5_plotB_crossover_vs_p.png", "crossover vs sketch size with 95% CI and the 2.5 line",
          [f'{b("Hypothesis rejected:", "red")} c* grows from {cs[8]:.2f} (p = 8) to {cs[16]:.2f} (p = 16)',
           "Why: plain HLL's built-in over-estimate does not shrink with more registers, but linear counting's random error does",
           f"A simple model reproduces c* within {model_dev:.2f} for p ≥ 10"],
          "x-axis = sketch size, y-axis = crossover (items per register), each dot = one sketch size with its 95% CI, purple line = the textbook 2.5. Look for: do the dots sit on one horizontal line?"),
    "(1) The x-axis is the sketch size p, from 8 to 16. (2) The y-axis is the crossover in items per register. "
    "(3) Each black dot is one sketch size with its 95 percent interval, and the purple dashed line is the textbook rule at 2.5. "
    f"(4) The dots are not on a horizontal line: they climb from {cs[8]:.2f} to {cs[16]:.2f}. "
    "(5) Our hypothesis that one fixed crossover fits every size is rejected. Plain HLL's built-in over-estimate does not shrink when we add registers, but the random error of linear counting does, "
    f"so bigger sketches keep linear counting useful for longer. A simple model built from that idea reproduces the crossovers within {model_dev:.2f} for p of 10 or more. "
    "The textbook 2.5 is close only for small sketches.",
    "results/exp5_crossover.csv (c_star, ci_lo, ci_hi, c_star_model)")

# ================================================================== IMPACT
add("Impact", "A usable rule can only use what the sketch can see: E, V and its size m",
    f'<div class="center">{img("schem_rule.png", "flow: sketch -> E and V -> is E <= c*m and V > 0 -> LC or raw", "plot mid")}</div>'
    '<p class="callout">We are looking for the best value of c, possibly depending on the sketch size.</p>',
    "In practice we never know the true count n, so a switching rule cannot use it. It can only use the raw estimate E, the number of empty registers V, and the sketch size m. "
    "So the rule has the form: use linear counting while E is at most c times m and some register is empty. The question is what c should be, and whether c may depend on m.",
    "illustration; rule implemented in src/hll.hpp (estimate_switch)")

add("Impact", f"Scanning the switch place: the lowest worst-case error is at {best14:.2f}, not at 2.5 (p = 14)",
    graph("exp5_plotD_threshold_scan.png", "worst-case error vs switch threshold",
          [f'{b("Worst-case error", "navy")} = the largest typical error anywhere between 0.25 and 8 items per register',
           "Textbook 2.5 sits on the steep part of the curve", f"Lowest point: switch at {best14:.2f}"],
          "x-axis = where we switch from linear counting to plain HLL (items per register), y-axis = worst-case error. Each point = one possible switch place. Lower is better. Look for: the lowest point."),
    "First, worst-case error means the largest typical error anywhere between 0.25 and 8 items per register. "
    "(1) The x-axis is the place where we switch from linear counting to plain HLL. (2) The y-axis is the worst-case error of the resulting estimator. "
    "(3) Each black point is one possible switch place; we want the lowest point. "
    f"(4) The purple dot is the textbook rule at 2.5, on the steep part of the curve; the green dot is the lowest point at {best14:.2f}. "
    f"(5) For p = 14, switching later than the textbook rule removes a large part of the error. This curve uses half of the {SEEDS} runs; the other half is kept for the final comparison.",
    "results/exp5_scan.csv (family raw_estimate_threshold, p = 14, wc_train), results/exp5_best_threshold.csv")

add("Impact", "Two measures in plain words: worst case and hand-over bump",
    graph("exp5_bump_definition.png", "textbook rule error with worst case and hand-over bump marked",
          [f'{b("Worst case:", "navy")} the tallest point of the typical-error curve',
           f'{b("Hand-over bump:", "text")} how far the average estimate is off, right where the rule switches',
           "For both, lower is better"],
          "x-axis = items per register, y-axis = error of the textbook rule (%). Solid line = typical error, dotted line = average error. Look for: the spike where the rule switches (p = 14)."),
    "(1) The x-axis is items per register. (2) The y-axis is the error of the textbook rule at p = 14, from our measurements. "
    "(3) The solid line is the typical error and the dotted line is the average error, meaning whether the estimate is on average too high. "
    "(4) Look at the spike at the switch point 2.5. The worst case is the tallest point of the solid line anywhere. The hand-over bump is the tallest point of the dotted line: the extra average error that appears where the estimator hands over from linear counting to plain HLL. "
    "(5) A good switch rule should keep both low.",
    "results/exp5_curves.csv (rmse_textbook, bias_textbook, p = 14)")

add("Impact", f"Switching at the best place cuts the worst-case error from {pct(tb.wc * 100)} to {pct(bs.wc * 100)} at p = 14",
    graph("exp5_plotC_rules.png", "worst case and hand-over bump for three rules",
          [f"Worst case: {pct(tb.wc * 100)} → {b(pct(bs.wc * 100), 'best')} (×{bs.wc_ratio_to_textbook:.2f}, 95% CI {bs.wc_ratio_ci_lo:.2f}–{bs.wc_ratio_ci_hi:.2f})",
           f"Hand-over bump: {pct(tb.bump * 100)} → {b(pct(bs.bump * 100), 'best')}",
           f"Plain HLL alone: {raw14.wc * 100:.0f}% (off the chart)"],
          "bars = error (lower is better); two groups = the two measures; colour = method (blue plain HLL only, purple textbook 2.5, green best rule); black bars = 95% CI. Look for: how much shorter the green bars are than the purple ones."),
    "(1) The x-axis has two groups, the worst case and the hand-over bump. (2) The y-axis is the error in percent, lower is better. "
    "(3) Each group has three bars: blue is plain HLL alone, purple is the textbook rule, green is our best rule; black bars are 95 percent confidence intervals. "
    f"(4) For p = 14 the worst case drops from {pct(tb.wc * 100)} to {pct(bs.wc * 100)}, a factor of {bs.wc_ratio_to_textbook:.2f} with a 95 percent interval from {bs.wc_ratio_ci_lo:.2f} to {bs.wc_ratio_ci_hi:.2f}. "
    f"The hand-over bump drops from {pct(tb.bump * 100)} to {pct(bs.bump * 100)}. Plain HLL alone has {raw14.wc * 100:.0f} percent worst-case error. "
    f"(5) These numbers come from the {SEEDS // 2} runs that were not used to pick the switch place, so they are not inflated by the choice.",
    "results/exp5_rules.csv (p = 14; wc, bump, CIs, wc_ratio_to_textbook)")

# ================================================================== TAKEAWAY
add("Takeaway", "Sanity checks: large-count error matches theory, and real text shows the same crossover",
    graph("exp5_sanity.png", "measured vs theory error; real-text vs synthetic crossover", None,
          "left: blue = measured typical error of plain HLL at 8 items per register, gray = theory 1.04/√m. Right: black squares = crossover on random data, orange dots = crossover on War and Peace (bars = 95% CI). Look for: do blue and gray match, and do squares and dots agree?", wide=True),
    "(1) Left: the x-axis is the sketch size and the y-axis is the typical error of plain HLL at 8 items per register. Blue is measured, gray is the theory 1.04 over the square root of m. "
    f"They agree within about 10 percent, for example {big_meas[14]:.2f} against {big_theory[14]:.2f} percent at p = 14. "
    "(2) Right: the x-axis is the sketch size and the y-axis is the crossover. Black squares are random data, orange dots are the real text War and Peace, with 95 percent intervals. "
    f"For p = 10 and 12 the real text gives {real.loc[10, 'c_star_real']:.2f} and {real.loc[12, 'c_star_real']:.2f}, against {real.loc[10, 'c_star_synthetic']:.2f} and {real.loc[12, 'c_star_synthetic']:.2f} on random data. "
    "For p = 8 the real-text interval is wide, so we do not read much into that point. (3) So the effect is not an artifact of our generator.",
    "results/exp5_curves.csv (rmse_raw at n/m = 8), results/exp6_real_crossover.csv")

add("Takeaway", f"For implementers: switch at c(p)·m with c(p) = {formula.intercept:.2f} + {formula.slope_per_bit_of_p:.3f}·p; the bigger the sketch, the more it saves",
    graph("exp5_plotC_by_p.png", "worst-case error by sketch size, textbook vs best",
          [f"Formula at p = 14: worst case {pct(fm.wc * 100)} (best choice {pct(bs.wc * 100)})",
           f"No gain at p = 8; worst case ×{by_p[16]:.2f} at p = 16",
           "Limits: random IDs and one text, XXH3 hash, p = 8 … 16 tested, 1 byte stored per register"],
          "x-axis = sketch size, y-axis = worst-case error (%), purple = textbook rule 2.5, green = best rule, black bars = 95% CI. Look for: how the gap between purple and green grows with sketch size."),
    "(1) The x-axis is the sketch size, the y-axis is the worst-case error. (2) Purple is the textbook rule and green is the best rule, with 95 percent confidence intervals. "
    f"(3) At p = 8 the two are the same. The bigger the sketch, the larger the gap: at p = 16 the best rule has {by_p[16]:.2f} times the textbook worst-case error. "
    f"(4) For someone implementing HLL: switch at c of p times m with c = {formula.intercept:.2f} + {formula.slope_per_bit_of_p:.3f} times p; at p = 14 that gives {pct(fm.wc * 100)} against {pct(bs.wc * 100)} for the individually best choice. "
    "(5) Limits: random IDs and one real text, one hash function, p from 8 to 16 only, so we do not claim the formula outside that range.",
    "results/exp5_rules.csv, results/exp5_formula.csv")

add("Takeaway", f"Conclusion: the border is not a constant; it moves from {cs[8]:.1f} to {cs[16]:.1f} items per register as the sketch grows",
    ul([f'{b("Answer:", "navy")} crossover c* = {cs[8]:.2f} (p = 8) … {cs[16]:.2f} (p = 16), each with a narrow 95% CI',
        f'{b("Hypothesis (one fixed threshold ≈ 2.5):", "red")} {b("rejected", "red")}',
        f'{b("Impact at p = 14:", "best")} worst case {pct(tb.wc * 100)} → {pct(bs.wc * 100)}, hand-over bump {pct(tb.bump * 100)} → {pct(bs.bump * 100)}',
        "Future work: derive c(m) from theory; other hashes and real streams"], "bigl concl"),
    f"Our answer: the crossover is not one number. It grows with the sketch size, from {cs[8]:.2f} at p = 8 to {cs[16]:.2f} at p = 16, with narrow confidence intervals. "
    f"So the hypothesis that one fixed threshold of about 2.5 fits every size is rejected. The textbook rule is fine for small sketches, but for p = 14 the best switch place cuts the worst-case error by more than half and the hand-over bump from {pct(tb.bump * 100)} to {pct(bs.bump * 100)}. "
    "Future work: derive the crossover from theory, and test other hash functions and real streams.",
    "results/exp5_crossover.csv, results/exp5_rules.csv")

assert len(SLIDES) == MAIN_SLIDES, len(SLIDES)

# ================================================================== BACKUP
add("Backup", "Backup: plain HLL's error follows 1.04/√m for every sketch size",
    graph("exp5_backup_theory.png", "measured error vs p against theory",
          ["Measured error tracks the theory line", "Theory: 0.81% at p = 14, not about 2% as on our seminar slides"],
          "x-axis = p (sketch size), y-axis = typical error of plain HLL (log scale). Blue = measured, gray dashed = theory 1.04/√m. 20 runs per point. Look for: do the points follow the line?"),
    "(1) The x-axis is p, so the sketch size doubles with every step. (2) The y-axis is the typical error of plain HLL for one million items, log scale. "
    "(3) Blue dots are measured, the gray dashed line is the theory 1.04 over the square root of m. (4) They agree within the noise of 20 runs. "
    "(5) Correction to our seminar slides: the typical error at p = 14 is 0.81 percent, not about 2 percent; 2 percent would be p = 11.",
    "results/exp2_n1e6.csv; plot: exp/plot_exp5.py (plot_backup_theory)")

add("Backup", f"Backup: HLL needs 12 KB and about {exp3.hll_basic_ns:.1f} ns per item; an exact hash set needs {exp3.set_bytes / 1e6:.0f} MB and {exp3.set_ns:.0f} ns",
    graph("fig_summary.png", "memory and time: HLL vs hash set",
          ["12 KB packed 6-bit (16 KB as our code stores it), not 1.5 KB", "Linear counting adds no time to updates"],
          "left = memory (log scale), right = time per item. Green = HyperLogLog (p = 14), gray = exact hash set, both for 10 million items. Look for: the size of the gap."),
    "(1) The two panels compare memory and time for ten million items. (2) Left is memory on a log scale, right is time per item. (3) Green is HyperLogLog at p = 14, gray is an exact hash set. "
    f"(4) HLL uses 12 KB when registers are packed to 6 bits (our code stores one byte per register, so 16 KB), against {exp3.set_bytes / 1e6:.0f} MB for the hash set. "
    "(5) Correction to our seminar slides: 16,384 registers times 6 bits is 12 KB, not 1.5 KB.",
    "results/exp3_p14.csv; plot: exp/plot_extra.py")

add("Backup", "Backup: full experiment setup",
    ul(["Data: random 64-bit IDs with repeats (true count known) and the words of War and Peace; hash XXH3-64, a different seed per run",
        "Estimators: plain HLL, pure linear counting m·ln(m/V) with V ≥ 1, switch rules on E ≤ c·m or on the empty share",
        "Crossover c* = smallest n/m after which plain HLL's typical error stays ≤ LC's; 95% CI by bootstrap over runs (1,000 resamples)",
        "Best switch place chosen on half of the runs, evaluated on the other half",
        "Worst case = largest typical error on n/m = 0.25 … 8; hand-over bump = largest average error on that range"], "small"),
    "Reference slide for questions. Everything here is also in the README and in exp/analyze_exp5.py.",
    "README.md, exp/analyze_exp5.py")

add("Backup", "Backup: the crossover for each sketch size",
    graph("exp5_backup_small_multiples.png", "one panel per sketch size", None,
          "each panel = one sketch size. x-axis = items per register, y-axis = typical error. Blue = plain HLL, orange = linear counting, dashed line = crossover (value in the panel title). Look for: the dashed line moves right as p grows.", wide=True),
    "(1) x-axis: items per register, log scale, in all five panels. (2) y-axis: typical error, log scale. (3) Blue is plain HLL, orange is linear counting, the dashed line is the crossover. "
    "(4) The left part of the blue line is the same in every panel, because it is dominated by the built-in over-estimate, while the orange line moves down as the sketch gets bigger. "
    "(5) That is why the crossover moves to the right.",
    "results/exp5_curves.csv, results/exp5_crossover.csv")

# ------------------------------------------------------------------ HTML
CSS = """
:root{--navy:#1F3864;--blue:#4F81BD;--ink:#222;--gray:#666;--raw:#1f77b4;--lc:#ff7f0e;--text:#8e44ad;--best:#2e7d32;--red:#c0392b}
*{box-sizing:border-box}
html,body{margin:0;height:100%;background:#2b2b2b;font-family:Calibri,Carlito,"Segoe UI","Helvetica Neue",Arial,sans-serif;color:var(--ink)}
#deck{position:absolute;left:50%;top:50%;width:1280px;height:720px;transform-origin:center center}
.slide{position:absolute;inset:0;width:1280px;height:720px;background:#fff;padding:22px 52px 0;display:none;flex-direction:column;overflow:hidden}
.slide.on{display:flex}
h2{margin:0;height:84px;display:flex;align-items:center;font-size:31px;line-height:1.15;color:var(--navy);font-weight:700}
h2.s{font-size:27px} h2.xs{font-size:24px}
.rule{height:4px;background:var(--blue);margin:4px 0 16px;flex:none}
.content{flex:1;display:flex;flex-direction:column;min-height:0}
ul{margin:6px 0;padding-left:28px} li{font-size:23px;line-height:1.3;margin:0 0 14px} li::marker{color:var(--blue)}
.small li{font-size:20px;margin-bottom:12px}
.bigl li{font-size:28px;margin-bottom:20px}
.concl li{font-size:26px}
.graph{display:flex;gap:24px;flex:1;min-height:0}
.pic{flex:0 0 820px;display:flex;align-items:flex-start;justify-content:center}
.side{flex:1} .side li{font-size:20px;margin-bottom:16px}
.wide{flex:1;display:flex;justify-content:center;min-height:0}
img.plot{max-width:100%;max-height:452px;object-fit:contain}
.wide img.plot{max-height:458px}
img.mid{max-height:360px}
.how{flex:none;margin:8px 0 0;background:#EAF1FB;border:1.5px solid var(--blue);border-radius:10px;padding:9px 16px;font-size:16.5px;line-height:1.3;min-height:58px;display:flex;align-items:center}
.how b{color:var(--navy);margin-right:6px;white-space:nowrap}
.footer{flex:none;height:44px;display:flex;align-items:center;justify-content:space-between;font-size:14px;color:#aaa;margin-top:auto}
.footer .cur{color:var(--navy);font-weight:700;font-size:15px} .footer .sep{color:#ccc;margin:0 8px}
.footer .num{color:var(--gray)}
.center{display:flex;justify-content:center} p.center{text-align:center;display:block}
.note{font-size:21px;color:var(--gray);margin:16px 0}
.callout{font-size:28px;color:var(--navy);font-weight:700;text-align:center;margin:18px 0}
b.raw{color:var(--raw)} b.lc{color:var(--lc)} b.text{color:var(--text)} b.best{color:var(--best)} b.red{color:var(--red)} b.navy{color:var(--navy)}
h3{margin:0 0 12px;font-size:30px} h3.navy{color:var(--navy);font-size:27px}
.cards{display:flex;gap:40px;margin-top:20px}
.card{flex:1;border:3px solid;border-radius:14px;padding:20px 26px;font-size:23px;line-height:1.4}
.card p{margin:0} .card.raw{border-color:var(--raw)} .card.raw h3{color:var(--raw)} .card.lc{border-color:var(--lc)} .card.lc h3{color:var(--lc)}
.card.hyp{background:#FFF4E5;font-size:27px;flex:0 0 520px}
.two{display:flex;gap:40px;margin-top:10px} .two>div:first-child{flex:1}
.rulebox{margin:30px auto 30px;padding:28px 40px;border:3px solid var(--text);background:#F3E8F8;border-radius:14px;font-size:38px;font-weight:700;color:var(--text);text-align:center;width:900px}
.tiles{display:flex;gap:30px;margin-top:30px}
.tile{flex:1;border:2.5px solid var(--blue);background:#EAF1FB;border-radius:14px;padding:30px 14px;text-align:center}
.tb{font-size:36px;font-weight:700;color:var(--navy);margin-bottom:14px} .ts{font-size:21px;line-height:1.35}
.titlepage{flex:1;display:flex;flex-direction:column;justify-content:center;padding-left:30px}
h1.big{font-size:52px;color:var(--navy);margin:0 0 24px;line-height:1.1}
.sub{font-size:27px;color:var(--gray);margin:0 0 34px} .who{font-size:20px;color:var(--gray);margin:0}
.notes{display:none}
#notes{position:fixed;left:0;right:0;bottom:0;max-height:34vh;overflow:auto;background:#fffbe6;border-top:3px solid #e0c060;padding:12px 22px;font-size:17px;line-height:1.4;display:none;z-index:9}
#notes.on{display:block} #notes .src{color:#777;font-size:14px;margin-top:6px}
#hint{position:fixed;right:12px;bottom:8px;color:#bbb;font-size:12px}
@media print{
  @page{size:1280px 720px;margin:0}
  html,body{background:#fff;height:auto}
  #deck{position:static;transform:none!important;width:auto;height:auto}
  .slide{display:flex!important;position:relative;page-break-after:always;break-after:page}
  #notes,#hint{display:none!important}
}
body.print{background:#fff} body.print #deck{position:static;transform:none!important;width:auto;height:auto}
body.print .slide{display:flex;position:relative;margin:0 auto 20px;box-shadow:0 0 0 1px #ccc}
"""

JS = """
const S=[...document.querySelectorAll('.slide')];let i=0;
const deck=document.getElementById('deck'),notes=document.getElementById('notes');
function fit(){if(document.body.classList.contains('print'))return;const k=Math.min(innerWidth/1280,innerHeight/720);deck.style.transform=`translate(-50%,-50%) scale(${k})`;}
function show(n){i=Math.max(0,Math.min(S.length-1,n));S.forEach((s,k)=>s.classList.toggle('on',k===i));
  const a=S[i].querySelector('.notes');notes.innerHTML=a?a.innerHTML:'';history.replaceState(null,'','#'+(i+1));}
addEventListener('keydown',e=>{const k=e.key;
  if(['ArrowRight','PageDown',' ','Enter'].includes(k)){show(i+1);e.preventDefault();}
  else if(['ArrowLeft','PageUp','Backspace'].includes(k)){show(i-1);e.preventDefault();}
  else if(k==='Home')show(0);else if(k==='End')show(S.length-1);
  else if(k==='n'||k==='N')notes.classList.toggle('on');
  else if(k==='p'||k==='P'){document.body.classList.toggle('print');if(!document.body.classList.contains('print'))fit();else deck.style.transform='none';}});
deck.addEventListener('click',e=>{if(e.clientX>innerWidth/2)show(i+1);else show(i-1);});
addEventListener('resize',fit);fit();show((parseInt(location.hash.slice(1))||1)-1);
"""


def footer(section, num):
    if section == "Backup":
        secs = '<span class="cur">Backup</span>'
    else:
        parts = [f'<span class="{"cur" if s == section else ""}">{s}</span>' for s in SECTIONS]
        secs = '<span class="sep">›</span>'.join(parts)
    return f'<div class="footer"><div>{secs}</div><div class="num">{num} / {MAIN_SLIDES}{" (backup)" if section == "Backup" else ""}</div></div>'


def title_cls(t):
    return "" if len(t) <= 66 else ("s" if len(t) <= 88 else "xs")


out = []
for k, s in enumerate(SLIDES, 1):
    note = E(s["notes"]) + (f'<div class="src">Source: {E(s["source"])}</div>' if s["source"] else "")
    if k == 1:
        inner = s["body"]
    else:
        inner = f'<h2 class="{title_cls(s["title"])}">{E(s["title"])}</h2><div class="rule"></div><div class="content">{s["body"]}</div>'
    out.append(f'<section class="slide" id="s{k}">{inner}{footer(s["section"], k)}<aside class="notes">{note}</aside></section>')

page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>When does linear counting stop helping HyperLogLog?</title><style>{CSS}</style></head><body>'
        f'<div id="deck">{"".join(out)}</div><div id="notes"></div>'
        f'<div id="hint">→ / ← move · N notes · P print view</div><script>{JS}</script></body></html>')
with open(os.path.join(ROOT, "slides.html"), "w", encoding="utf-8") as f:
    f.write(page)
print(f"saved slides.html: {len(SLIDES)} slides ({MAIN_SLIDES} main + {len(SLIDES) - MAIN_SLIDES} backup)")
