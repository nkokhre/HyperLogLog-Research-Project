"""Builds slides.pptx. Run: python3 report/make_slides.py  (needs python-pptx)"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
NAVY, BLUE, GRAY = RGBColor(0x1F, 0x38, 0x64), RGBColor(0x4F, 0x81, 0xBD), RGBColor(0x55, 0x55, 0x55)
RED, GREEN, DARK = RGBColor(0xC0, 0x39, 0x2B), RGBColor(0x2E, 0x7D, 0x32), RGBColor(0x22, 0x22, 0x22)
FONT = "Calibri"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
blank = prs.slide_layouts[6]
count = [0]

def text(slide, x, y, w, h, s, size=20, bold=False, color=DARK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = s
    r.font.size, r.font.bold, r.font.name = Pt(size), bold, FONT
    r.font.color.rgb = color
    return tb

def new(title):
    s = prs.slides.add_slide(blank); count[0] += 1
    text(s, 0.7, 0.4, 12, 0.9, title, 32, True, NAVY)
    ln = s.shapes.add_shape(1, Inches(0.7), Inches(1.25), Inches(11.9), Inches(0.04))
    ln.fill.solid(); ln.fill.fore_color.rgb = BLUE; ln.line.fill.background()
    text(s, 12.2, 6.95, 0.8, 0.4, str(count[0]), 12, color=GRAY, align=PP_ALIGN.RIGHT)
    return s

def bullets(slide, items, x=0.7, y=1.6, w=11.9, h=5, size=22, gap=12):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        parts = it if isinstance(it, list) else [(it, False)]
        r0 = p.add_run(); r0.text = "•  "; r0.font.size = Pt(size); r0.font.name = FONT; r0.font.color.rgb = BLUE
        for t, b in parts:
            r = p.add_run(); r.text = t
            r.font.size, r.font.bold, r.font.name = Pt(size), b, FONT
            r.font.color.rgb = DARK

def picture(slide, name, y=1.5, max_w=12.0, max_h=4.3, left=None):
    from PIL import Image
    path = os.path.join(RES, name)
    iw, ih = Image.open(path).size
    w = max_w; h = w * ih / iw
    if h > max_h: h = max_h; w = h * iw / ih
    slide.shapes.add_picture(path, Inches((13.333 - w) / 2 if left is None else left), Inches(y), Inches(w), Inches(h))
    return y + h

def table(slide, rows, x, y, w, col_w=None, size=18, row_h=0.5, hl=None):
    nr, nc = len(rows), len(rows[0])
    gs = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(row_h * nr))
    t = gs.table
    if col_w:
        for i, cw in enumerate(col_w): t.columns[i].width = Inches(cw)
    for r in range(nr):
        for c in range(nc):
            cell = t.cell(r, c); cell.text = ""
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER
            run = p.add_run(); run.text = rows[r][c]
            run.font.size, run.font.name = Pt(size), FONT
            run.font.bold = (r == 0)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(0xDC, 0xE6, 0xF2) if r == 0 else RGBColor(0xFF, 0xFF, 0xFF)
            run.font.color.rgb = DARK
            if hl and (r, c) in hl: run.font.color.rgb = hl[(r, c)]; run.font.bold = True
    return t

# 1 Title
s = prs.slides.add_slide(blank); count[0] += 1
text(s, 0.9, 2.3, 11.5, 1.3, "How accurate is HyperLogLog?", 50, True, NAVY)
text(s, 0.9, 3.6, 11.5, 0.8, "We tested its error, and where it stops being accurate", 24, color=GRAY)
text(s, 0.9, 4.6, 11.5, 0.6, "Ibrahim and Nika · Advanced Algorithms & Data Structures · Fall 2026", 18, color=GRAY)

# 2 Idea
s = new("The idea: count different items without storing them")
y = picture(s, "fig_how.png", y=1.5, max_w=11.5, max_h=3.9)
bullets(s, [
    "Keep only m small counters (registers). Memory stays tiny, however long the stream is.",
    "A long run of zeros in a hash is rare, so a long run means many different items.",
], y=y + 0.15, size=20, gap=6)

# 3 Example
s = new("Example: from registers to an estimate")
y = picture(s, "fig_example.png", y=1.5, max_w=11.5, max_h=3.8)
bullets(s, [
    "Basic formula: 23.2.   Linear counting (uses the 2 empty registers): 33.3.",
    "Linear counting is the fix for small counts: it looks at how many registers are still empty.",
], y=y + 0.15, size=20, gap=6)

# 4 Questions
s = new("What we wanted to know")
bullets(s, [
    [("Question 1: ", True), ("how does the error change with the real count n? Does linear counting fix small counts?", False)],
    [("Question 2: ", True), ("how does the number of registers change the error? Theory says 1.04/√m.", False)],
    "m = number of registers = 2^p. We use p = 14, so m = 16,384.",
    "Error = (estimate − real count) / real count.",
])

# 5 Method
s = new("How we tested")
bullets(s, [
    "We wrote HyperLogLog ourselves in C++.",
    [("Two versions: ", True), ("basic, and basic + linear counting.", False)],
    "Input: random IDs with repeats. We know the real count exactly.",
    "Every point: 20 random runs (seeds).",
    "Tests cover 100% of the code. Hash checked for uniformity.",
])

# 6 Expectations
s = new("What we expected")
bullets(s, [
    [("Large counts: ", True), ("error about 0.81% (16,384 registers), whatever n is.", False)],
    [("1,000 items: ", True), ("basic about 12 times too big; linear counting within about 1%.", False)],
    "Linear counting should not slow things down.",
    "Not sure: what happens where the two formulas hand over (40,000 to 80,000 items).",
])

# 7 Small counts
s = new("Small counts: basic HLL cannot go below ~12,000")
y = picture(s, "fig_small.png", y=1.45, max_w=8.0, max_h=4.6, left=0.7)
text(s, 9.0, 2.0, 3.8, 3.5, "Even for 10 items, basic HLL says about 12,000.\n\nLinear counting follows the real count.", 20)

# 8 Exp1
s = new("Experiment 1: error vs real count (p = 14)")
y = picture(s, "exp1_p14.png", y=1.5, max_w=12.2, max_h=3.6)
text(s, 0.7, y + 0.15, 11.9, 1.4,
     "Blue = basic. Orange = with linear counting. Left: mean error. Middle: spread of the error (dashed line = theory 0.81%). "
     "Right: share of empty registers.", 18, color=GRAY)

# 9 Exp1 results
s = new("Experiment 1: results")
text(s, 0.7, 1.6, 5.5, 0.5, "1,000 items, basic HLL", 20, color=GRAY)
text(s, 0.7, 2.1, 5.5, 1.2, "+1130%", 56, True, RED)
text(s, 0.7, 3.5, 5.5, 0.5, "1,000 items, with linear counting", 20, color=GRAY)
text(s, 0.7, 4.0, 5.5, 1.2, "−0.05%", 56, True, GREEN)
bullets(s, [
    "Basic HLL: 12 times too big for small counts, as expected.",
    "Linear counting fixes it.",
    "From 10^6 items the error is about 0.8%, whatever n is. This matches the theory.",
], x=6.6, y=1.7, w=6.1, size=21)

# 10 Surprise chart
s = new("The surprise: both versions are too high around 2.5m")
y = picture(s, "fig_handover.png", y=1.45, max_w=9.0, max_h=4.9, left=0.7)
text(s, 9.9, 1.9, 3.0, 4.0, "Between 41,000 and 74,000 items the error is up to +2.4%.\n\nThat is about 3 times the normal noise.", 19)

# 11 Why
s = new("Why does this happen?")
bullets(s, [
    [("1. ", True), ("Near 2.5m items, the basic formula is a little too high (+2.4%).", False)],
    [("2. ", True), ("We switch to linear counting when the estimate is at most 2.5m.", False)],
    [("3. ", True), ("The estimate is too high, so it passes 2.5m a bit early.", False)],
    [("4. ", True), ("Linear counting is turned off while the bias is still there.", False)],
    "HLL++ fixes this with a correction table. We only report it.",
    "Our tests also check that this bias is real.",
], size=22, gap=10)

# 12 Exp2
s = new("Experiment 2: error vs number of registers")
y = picture(s, "exp2_n1e6.png", y=1.5, max_w=11.5, max_h=3.9)
bullets(s, [
    "Real count 10^6. The measured error follows 1.04/√m for every p from 4 to 16.",
    "p = 14: 0.87% measured, 0.81% theory.",
], y=y + 0.1, size=20, gap=6)

# 13 Exp3
s = new("Experiment 3: speed and memory")
y = picture(s, "fig_summary.png", y=1.45, max_w=8.4, max_h=3.9, left=0.7)
text(s, 9.3, 1.9, 3.6, 3.6, "10 million items, p = 14.\n\nHLL: 12 KB, 1.2 ns per item.\nHash set: 345 MB, 208 ns per item.", 19)
bullets(s, [
    "HLL is 8 to 170 times faster. Its memory does not grow with n.",
    "Linear counting does not slow the updates (same code).",
], y=y + 0.15, size=20, gap=6)

# 14 Real data
s = new("Real data: words in War and Peace")
y = picture(s, "fig_real.png", y=1.45, max_w=11.0, max_h=3.9)
bullets(s, [
    "583,368 words, 17,445 different (counted exactly).",
    "Same result: basic is too high when n/m is small (+28%), linear counting fixes it.",
], y=y + 0.1, size=20, gap=6)

# 15 Answers
s = new("Answers to our questions")
bullets(s, [
    [("Q1: ", True), ("the error is about 0.8% once n is above about 4.5m. Below 2.5m basic HLL is far off, and linear counting fixes it.", False)],
    "Small catch: a bump of up to 2.4% between 2.5m and 4.5m.",
    [("Q2: ", True), ("the error follows 1.04/√m for all p from 4 to 16.", False)],
    "Linear counting costs no time per item.",
])

# 16 Corrections
s = new("Corrections to our seminar slides")
bullets(s, [
    [("Memory: ", True), ("16,384 registers × 6 bits = 12 KB. The 1.5 KB on the slide would be only 2,048 registers.", False)],
    [("Typical error: ", True), ("0.81% for p = 14, not about 2%. (2% matches p = 11.)", False)],
    "Our code stores 1 byte per register (16 KB). Packing to 6 bits gives 12 KB.",
])

# 17 Limits
s = new("Limits")
bullets(s, [
    "20 runs per point: spread values are uncertain by about ±16%.",
    "Timings: one laptop, plugged in. Ratios matter more than exact ns.",
    "No HLL++ correction table and no sparse mode.",
    "All code, data and plots are in the project folder; the README shows how to rerun them.",
])

prs.save(os.path.join(ROOT, "slides.pptx"))
print("saved", count[0], "slides")
