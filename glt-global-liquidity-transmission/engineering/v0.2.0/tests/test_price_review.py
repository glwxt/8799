"""Regression checks for point-in-time price evaluation."""
from datetime import datetime
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from price_review import PROTOCOL, calculate_outcome, lock_benchmark
from review import price_summary


class LockedPriceReview(unittest.TestCase):
    def setUp(self):
        start = "2026-11-20T08:00:00+08:00"
        end = "2026-11-21T08:00:00+08:00"
        data = dict(series_id="test", instrument="BTC", price_type="spot", unit="USD",
                    calendar="24/7", session_rule="exact", source_url="https://example.com",
                    start_at=start, end_at=end, start_value="100", neutral_pct="1.5")
        self.forecast = dict(
            id="1", direction="震荡偏空", model="BTC-GT", horizon="24h",
            protocol=PROTOCOL, issued_at=start,
            benchmark=lock_benchmark(data, start, "24h", datetime.fromisoformat(start)),
        )
        self.quote = dict(observed_at=end, value="98.50", series_id="test",
                          unit="USD", price_type="spot", source_url="https://example.com")
        self.end = end

    def test_decimal_boundary_and_mapping(self):
        outcome = calculate_outcome(self.forecast, self.quote, self.end)
        self.assertEqual(outcome["observed_direction"], "震荡")
        self.assertFalse(outcome["exact_match"])
        self.quote["value"] = "98.49"
        self.assertTrue(calculate_outcome(self.forecast, self.quote, self.end)["exact_match"])

    def test_rejects_wrong_series_and_early_evaluation(self):
        with self.assertRaisesRegex(ValueError, "matured"):
            calculate_outcome(self.forecast, self.quote, "2026-11-21T07:59:00+08:00")
        self.quote["series_id"] = "other"
        with self.assertRaisesRegex(ValueError, "series_id"):
            calculate_outcome(self.forecast, self.quote, self.end)

    def test_cutoff_excludes_later_outcome(self):
        before = datetime.fromisoformat("2026-11-21T07:59:00+08:00")
        end = datetime.fromisoformat(self.end)
        outcome = calculate_outcome(self.forecast, self.quote, "2026-11-21T09:00:00+08:00")
        outcomes = {"1": outcome}
        waiting = next(iter(price_summary([self.forecast], outcomes, before).values()))
        due = next(iter(price_summary([self.forecast], outcomes, end).values()))
        self.assertEqual(waiting["pending"], 1)
        self.assertEqual(due["missing_quote"], 1)
        self.assertEqual(due["scored"], 0)
