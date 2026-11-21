import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from forecast_v2 import create_forecast, record_outcome, review, bands_to_direction

BASE = dict(model="BTC-GT", horizon="24h", direction="震荡偏多",
            asof="2026-11-20T08:00:00+08:00",
            baseline_at="2026-11-20T07:00:00+08:00",
            baseline_price=100, baseline_source="https://example.org/price",
            neutral_pct=1, strong_pct=3, confidence=.55,
            rationale="Test-only independent evidence", asset="BTCUSD")
class ForecastTests(unittest.TestCase):
    def setUp(self):
        self.dir=tempfile.TemporaryDirectory()
        self.root=Path(self.dir.name)
    def tearDown(self):
        self.dir.cleanup()
    def test_five_classes(self):
        self.assertEqual([bands_to_direction(i,1,3) for i in (-4,-2,0,2,4)],
                         ["偏空","震荡偏空","震荡","震荡偏多","偏多"])
    def test_create_and_exact_outcome(self):
        f=create_forecast(self.root,**BASE)
        self.assertEqual(f["baseline_price"],100)
        out=record_outcome(self.root,forecast_id=f["id"],
            observed_at="2026-11-21T08:00:00+08:00",observed_price=102,
            source="https://example.org/actual")
        self.assertTrue(out["exact_match"])
        self.assertEqual(out["observed_direction"],"震荡偏多")
        self.assertEqual(review(self.root)["groups"]["BTC-GT/24h"]["exact_rate"],None)
    def test_immutable_forecast(self):
        create_forecast(self.root,**BASE)
        with self.assertRaises(FileExistsError):
            create_forecast(self.root,**BASE)
    def test_duplicate_outcome_fails(self):
        f=create_forecast(self.root,**BASE)
        kw=dict(forecast_id=f["id"],observed_at="2026-11-21T08:00:00+08:00",
                observed_price=102,source="https://example.org/actual")
        record_outcome(self.root,**kw)
        with self.assertRaises(FileExistsError):
            record_outcome(self.root,**kw)
    def test_not_matured(self):
        f=create_forecast(self.root,**BASE)
        with self.assertRaises(ValueError):
            record_outcome(self.root,forecast_id=f["id"],
                observed_at="2026-11-20T12:00:00+08:00",observed_price=102,
                source="https://example.org/actual")
    def test_overdue_noncomparable(self):
        f=create_forecast(self.root,**BASE)
        with self.assertRaises(ValueError):
            record_outcome(self.root,forecast_id=f["id"],
                observed_at="2026-11-27T12:00:00+08:00",observed_price=102,
                source="https://example.org/actual")
    def test_future_baseline_rejected(self):
        kw=dict(BASE,baseline_at="2026-11-20T09:00:00+08:00")
        with self.assertRaises(ValueError):
            create_forecast(self.root,**kw)
    def test_invalid_bands_rejected(self):
        kw=dict(BASE,neutral_pct=4,strong_pct=3)
        with self.assertRaises(ValueError):
            create_forecast(self.root,**kw)
    def test_invalid_source_rejected(self):
        kw=dict(BASE,baseline_source="not-a-url")
        with self.assertRaises(ValueError):
            create_forecast(self.root,**kw)
    def test_same_asof_distinct_assets(self):
        a=create_forecast(self.root,**BASE)
        b=create_forecast(self.root,**dict(BASE,asset="BTCUSDT"))
        self.assertNotEqual(a["id"],b["id"])
if __name__=="__main__":
    unittest.main()
