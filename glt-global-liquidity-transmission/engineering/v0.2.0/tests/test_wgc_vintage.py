"""Regression tests for WGC article vs PDF availability."""
import hashlib
import json
import sys
import unittest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import fund_flows

ARTICLE = "2026-09-07T12:30:00+00:00"
FIRST = "2026-09-07T16:00:00+00:00"
NOW = "2026-09-08T05:00:00+00:00"
RAW = b"one PDF version"
OBS = {"indicator": "gold_flow", "observation_date": "2026-09-04", "published_at": ARTICLE}
VERSION = {"indicator": "gold_flow", "observation_date": "2026-09-04",
           "sha256": hashlib.sha256(RAW).hexdigest(), "pdf_first_verified_at": FIRST}


class WgcVintageTest(unittest.TestCase):
    def test_existing_vintage(self):
        result = fund_flows.wgc_vintage_metadata(OBS, RAW, datetime.fromisoformat(NOW), [VERSION])
        self.assertEqual(result["pdf_first_verified_at"], FIRST)
        self.assertEqual(result["article_published_at"], ARTICLE)
        self.assertIsNone(result["pdf_first_available_at"])

    def test_new_hash_and_invalid_times(self):
        for data, row in [
            (b"revised", VERSION),
            (RAW, dict(VERSION, pdf_first_verified_at="2026-09-07T16:00:00")),
            (RAW, dict(VERSION, pdf_first_verified_at="2030-01-01T00:00:00Z")),
            (RAW, dict(VERSION, pdf_first_verified_at="2026-09-07T11:00:00Z")),
            (RAW, dict(VERSION, pdf_first_verified_at=None)),
        ]:
            result = fund_flows.wgc_vintage_metadata(OBS, data, datetime.fromisoformat(NOW), [row])
            self.assertEqual(result["pdf_first_verified_at"], NOW)

    def test_survives_an_outage_without_emitting_stale_observation(self):
        with TemporaryDirectory() as temp:
            dest = Path(temp) / "latest.json"
            dest.write_text(json.dumps({"wgc_recent_verified_versions": [VERSION]}), encoding="utf-8")
            args = ["fund_flows.py", "--output", str(dest), "--raw-dir", temp]
            with patch.object(sys, "argv", args), patch.object(fund_flows, "download", side_effect=ValueError("outage")):
                fund_flows.main()
            miss = json.loads(dest.read_text(encoding="utf-8"))
            self.assertEqual(miss["wgc_recent_verified_versions"], [VERSION])
            self.assertEqual(miss["observations"], [])
            with patch.object(sys, "argv", args), patch.object(fund_flows, "download", side_effect=ValueError("outage")), patch.object(fund_flows, "collect_wgc", return_value=("https://www.gold.org/sample.pdf", RAW, OBS)):
                fund_flows.main()
            recovered = json.loads(dest.read_text(encoding="utf-8"))
            self.assertEqual(recovered["observations"][0]["pdf_first_verified_at"], FIRST)
            self.assertFalse(recovered["eligible_for_official_score"])
