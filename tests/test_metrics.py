import unittest

from thinkfast.metrics import (Decision, automation_rate, brier, expected_calibration_error, percentile,
                               probs_from_answer)


def d(label: str, p_true: float) -> Decision:
    return Decision(family="f", qtype="noul", probs={"true": p_true, "false": 1 - p_true}, label=label)


class MetricsTest(unittest.TestCase):
    def test_brier(self):
        self.assertAlmostEqual(brier(d("true", 1.0)), 0.0)
        self.assertAlmostEqual(brier(d("false", 1.0)), 2.0)
        self.assertAlmostEqual(brier(d("true", 0.5)), 0.5)

    def test_ece_perfectly_calibrated(self):
        # 80% confident, right 4 times out of 5
        decisions = [d("true", 0.8)] * 4 + [d("false", 0.8)]
        self.assertAlmostEqual(expected_calibration_error(decisions), 0.0)

    def test_ece_overconfident(self):
        decisions = [d("true", 0.95), d("false", 0.95)]
        self.assertAlmostEqual(expected_calibration_error(decisions), 0.45)

    def test_automation_rate_takes_confident_prefix(self):
        decisions = [d("true", 0.99)] * 19 + [d("false", 0.98)] + [d("false", 0.6)] * 5 + [d("true", 0.55)] * 5
        rate, threshold = automation_rate(decisions, budget=0.05)
        self.assertAlmostEqual(rate, 20 / 30)
        self.assertAlmostEqual(threshold, 0.98)

    def test_automation_rate_keeps_ties_together(self):
        decisions = [d("true", 0.9)] * 9 + [d("false", 0.9)] * 2
        rate, _ = automation_rate(decisions, budget=0.05)
        self.assertEqual(rate, 0.0)

    def test_probs_from_answer(self):
        choice = {"type": "choice", "criteria": {"a": None, "b": None}}
        self.assertEqual(probs_from_answer(choice, {"probabilities": {"a": 3, "b": 1}}), {"a": 0.75, "b": 0.25})
        self.assertEqual(probs_from_answer(choice, None), {"a": 0.5, "b": 0.5})
        self.assertEqual(probs_from_answer(choice, {"probabilities": "junk"}), {"a": 0.5, "b": 0.5})
        score = {"type": "score", "criteria": ["low", "high"]}
        self.assertEqual(probs_from_answer(score, {"probabilities": {"0": 0.2, "1": 0.8}}), {"0": 0.2, "1": 0.8})

    def test_percentile_nearest_rank(self):
        values = list(range(1, 11))
        self.assertEqual(percentile(values, 50), 5)
        self.assertEqual(percentile(values, 95), 10)
        self.assertEqual(percentile([], 95), 0.0)


if __name__ == "__main__":
    unittest.main()
