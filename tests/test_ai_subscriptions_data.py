"""Arithmetic self-consistency of the figures transcribed from the user's AI-subscription document.

This proves the document's derived numbers follow from its own inputs (and that the transcription matches).
It does NOT verify any price or quota against the vendors; that was not done.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ai_subscriptions_data as D  # noqa: E402


class CostTables(unittest.TestCase):
    def test_deepseek_cost_per_100m_matches_document(self):
        for (model, period), printed in D.DOC_COST_100M_USD.items():
            self.assertAlmostEqual(D.cost_per_100m(D.DEEPSEEK[model][period]), printed, places=6, msg=(model, period))

    def test_deepseek_one_billion_is_ten_times(self):
        for key, printed in D.DOC_COST_1B_USD.items():
            self.assertAlmostEqual(D.DOC_COST_100M_USD[key] * 10, printed, places=6, msg=key)

    def test_deepseek_peak_is_twice_offpeak(self):
        for model, prices in D.DEEPSEEK.items():
            for k in ("cache", "input", "output"):
                self.assertAlmostEqual(prices["peak"][k], 2 * prices["offpeak"][k], places=6, msg=(model, k))

    def test_kimi_cost_per_100m_matches_document(self):
        for model, printed in D.DOC_COST_100M_CNY.items():
            self.assertAlmostEqual(D.cost_per_100m(D.KIMI_API[model]), printed, places=6, msg=model)

    def test_mix_adds_up_to_100m(self):
        self.assertEqual(sum(D.MIX.values()), 100.0)


class OpenCodeGo(unittest.TestCase):
    def test_reference_limits_follow_the_20_50_100_rule(self):
        for model, plans in D.GO_MODELS.items():
            for plan, (h5, week, month) in plans.items():
                for got, frac in zip((h5, week, month), D.GO_FRACTIONS):
                    self.assertAlmostEqual(got, month * frac, places=6, msg=(model, plan))

    def test_worked_example_from_the_document(self):
        # US$1 on a model with a US$15 monthly reference uses 6.67 % of the pool; on a US$60 model 1.67 %.
        self.assertAlmostEqual(1 / 15 * 100, 6.67, places=2)
        self.assertAlmostEqual(1 / 60 * 100, 1.67, places=2)


class Charts(unittest.TestCase):
    def test_tb4_is_sorted_best_first(self):
        scores = [s for _, s, _ in D.TB4_INDEPENDENT]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_eval_weights_sum_to_100(self):
        self.assertEqual(sum(w for _, w in D.EVAL_WEIGHTS), 100)

    def test_ladders_are_increasing(self):
        for name, _cur, tiers in D.LADDER:
            prices = [p for _, p in tiers]
            self.assertEqual(prices, sorted(prices), name)

    def test_cursor_multipliers_rise_with_price(self):
        prices = [p for _, p, _ in D.CURSOR_MULTIPLIERS]
        mults = [m for _, _, m in D.CURSOR_MULTIPLIERS]
        self.assertEqual(prices, sorted(prices))
        self.assertEqual(mults, [1, 4, 15, 50])  # Plus 1x, Premium 4x, Super 15x, Ultra 50x as printed


if __name__ == "__main__":
    unittest.main()
