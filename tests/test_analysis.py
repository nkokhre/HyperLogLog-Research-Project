"""Tests for the crossover-finding logic (exp/analyze_exp5.py) on synthetic curves.
Run: python3 tests/test_analysis.py"""
import os, sys, unittest
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exp"))
import analyze_exp5 as A


class CrossoverTests(unittest.TestCase):
    t = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

    def test_clean_crossing_is_interpolated(self):
        raw = np.array([9.0, 5.0, 3.0, 2.0, 1.0]); lc = np.array([1.0, 2.0, 4.0, 6.0, 9.0])
        # d = raw - lc = 8, 3, -1, -4, -8 -> last violation at t=2, crosses between 2 and 3 at 2 + 3/4
        self.assertAlmostEqual(A.crossover(self.t, raw, lc), 2.75)

    def test_stays_requires_all_later_points(self):
        raw = np.array([9.0, 1.0, 3.0, 2.0, 1.0]); lc = np.array([1.0, 2.0, 2.0, 6.0, 9.0])
        # raw is better at t=2 but worse again at t=3 -> the crossover is after t=3
        c = A.crossover(self.t, raw, lc)
        self.assertGreater(c, 3.0); self.assertLess(c, 4.0)

    def test_raw_always_better_returns_first_point(self):
        self.assertEqual(A.crossover(self.t, np.ones(5), np.full(5, 2.0)), 1.0)

    def test_lc_always_better_returns_nan(self):
        self.assertTrue(np.isnan(A.crossover(self.t, np.full(5, 2.0), np.ones(5))))


class RuleTests(unittest.TestCase):
    d = dict(m=16, raw=np.array([[20.0, 30.0, 50.0]]), lc=np.array([[10.0, 12.0, 15.0]]),
             V=np.array([[3, 2, 0]]), n=np.array([10.0, 12.0, 15.0]))

    def test_threshold_rule(self):
        # c = 2.5: E <= 40 and V > 0 -> LC; E = 50 (> 40, V = 0) -> raw
        self.assertEqual(A.rule_e(self.d, 2.5).tolist(), [[10.0, 12.0, 50.0]])
        self.assertEqual(A.rule_e(self.d, 1.5).tolist(), [[10.0, 30.0, 50.0]])  # E <= 24 only for the first point

    def test_empty_share_rule(self):
        self.assertEqual(A.rule_f(self.d, 0.1).tolist(), [[10.0, 12.0, 50.0]])  # shares 0.1875, 0.125, 0
        self.assertEqual(A.rule_f(self.d, 0.15).tolist(), [[10.0, 30.0, 50.0]])

    def test_lc_value_clamps(self):
        self.assertAlmostEqual(float(A.lc_value(16, np.array([0]))[0]), 16 * np.log(16.0))

    def test_rel_err(self):
        self.assertEqual(A.rel_err(self.d, np.array([[11.0, 12.0, 30.0]])).tolist(), [[0.1, 0.0, 1.0]])


if __name__ == "__main__":
    unittest.main()
