import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH=Path(__file__).resolve().parents[1]/"src"/"batch_stage.py"
spec=importlib.util.spec_from_file_location("batch_stage",MODULE_PATH)
batch=importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)

class FakeResponse:
    def __init__(self,raw):self.raw=raw
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,n):return self.raw

def fake_open(req,timeout=30):
    sid=req.full_url.split("id=")[-1]
    return FakeResponse(("DATE,"+sid+"\n2026-11-17,1.2\n2026-11-18,1.3\n").encode())

class TestStaging(unittest.TestCase):
    def test_parse_csv(self):
        v=batch.parse_csv(b"DATE,DFII10\n2026-11-01,.\n2026-11-18,1.3\n","DFII10")
        self.assertEqual(v["rows_numeric"],1)
        self.assertEqual(v["last_observation_date"],"2026-11-18")
    def test_invalid_columns(self):
        with self.assertRaises(ValueError):
            batch.parse_csv(b"DATE,OTHER\n2026-11-18,2\n","DFII10")
    def test_collect_is_not_scoring(self):
        with tempfile.TemporaryDirectory() as t:
            out=batch.collect(t,opener=fake_open,retries=0)
            self.assertEqual(out["success_count"],6)
            self.assertFalse(out["eligible_for_official_glt_score"])
            self.assertEqual(out["glt_scoring_coverage"],"NOT_CALCULATED")
            self.assertTrue((Path(t)/"manifest.json").is_file())
            self.assertFalse(next(iter(out["series"].values()))["release_timestamp_verified"])
            self.assertTrue((Path(t)/"DGS10.csv").is_file())
if __name__=="__main__":
    unittest.main()
