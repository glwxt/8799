import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from readiness import assess
ROOT=Path(__file__).resolve().parents[1]
ASOF="2026-11-20T08:00:00+08:00"
class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        (self.root/"config").mkdir();(self.root/"data").mkdir()
        for p in ("config/indicators.csv","data/calibration.csv"):
            (self.root/p).write_bytes((ROOT/p).read_bytes())
    def tearDown(self):
        self.temp.cleanup()
    def write_obs(self,rows):
        (self.root/"data/observations.csv").write_text(
            "indicator_id,observation_date,published_at,value,unit,source_url,retrieved_at,revision,transform\n"+
            "".join(rows),encoding="utf-8")
    def test_empty_data_no_score(self):
        self.write_obs([])
        r=assess(self.root,ASOF)
        self.assertEqual(r["raw_input_coverage"],0)
        self.assertEqual(r["score_coverage"],0)
        self.assertFalse(r["official_publishable"])
    def test_context_data_present_but_not_scored(self):
        self.write_obs(["tga,2026-11-18,2026-11-19T12:00:00+00:00,900,Millions of USD,https://example.org/dts,2026-11-19T13:00:00+00:00,initial,raw\n"])
        r=assess(self.root,ASOF)
        self.assertEqual(r["raw_input_coverage"],.08)
        self.assertEqual(r["score_coverage"],0)
        self.assertEqual(r["layers"]["L1"]["raw_input_points"],8)
        self.assertEqual(r["layers"]["L1"]["issues"][1]["status"],"requires_context_review")
    def test_stale_not_counted_as_fresh(self):
        self.write_obs(["tga,2026-10-01,2026-10-02T12:00:00+00:00,900,Millions of USD,https://example.org/dts,2026-10-02T13:00:00+00:00,initial,raw\n"])
        r=assess(self.root,ASOF)
        self.assertEqual(r["raw_input_coverage"],0)
if __name__=="__main__":
    unittest.main()
