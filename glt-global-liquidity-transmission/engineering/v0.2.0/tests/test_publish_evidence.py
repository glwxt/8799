import datetime as dt
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import publish_evidence as pe
from batch_stage import SERIES

NOW=dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
DAY=(NOW-dt.timedelta(days=1)).date().isoformat()
def manifest(errors=()):
    items={}
    fails={}
    for sid, info in SERIES.items():
        if sid in errors:
            fails[sid]="HTTPError: unavailable"
        else:
            items[sid]=dict(indicator=info["indicator"], unit=info["unit"],
                frequency=info["frequency"],
                last_observation_date=DAY, last_value_current_vintage=12.3,
                retrieved_at_utc=NOW.isoformat(),
                source_url="https://fred.stlouisfed.org/graph/fredgraph.csv?id="+sid,
                sha256="0"*64, release_timestamp_verified=False)
    return dict(status="staging_only",eligible_for_official_glt_score=False,
                retrieved_at_utc=NOW.isoformat(),series=items,errors=fails,
                success_count=len(items),failure_count=len(fails))

class TestEvidence(unittest.TestCase):
    def test_raw_hash_and_observation_verified(self):
        d=manifest()
        with tempfile.TemporaryDirectory() as name:
            directory=Path(name)
            for sid,entry in d["series"].items():
                content=("DATE,"+sid+"\\n"+DAY+",12.3\\n").encode()
                (directory/(sid+".csv")).write_bytes(content)
                entry["sha256"]=hashlib.sha256(content).hexdigest()
            pe.verify_raw_bundle(d,directory)
            (directory/"DFII10.csv").write_bytes(b"tampered data")
            with self.assertRaises(ValueError):
                pe.verify_raw_bundle(d,directory)
    def test_all_six(self):
        result=pe.build(manifest())
        self.assertEqual(result["success_count"],6)
        self.assertEqual(result["collection_status"],"OK")
        self.assertIsNone(result["official_glt_score"])
        self.assertFalse(result["source_release_timestamps_verified"])
        self.assertIn("当前版本",pe.markdown(result))
    def test_degraded_not_hidden(self):
        result=pe.build(manifest(errors=("DFII10","DGS10","WALCL")))
        self.assertEqual(result["collection_status"],"DEGRADED")
        self.assertIn("DFII10",result["errors"])
        self.assertNotIn("DFII10",result["series"])
    def test_bad_checksum(self):
        d=manifest()
        d["series"]["DFII10"]["sha256"]="insecure"
        with self.assertRaises(ValueError):pe.build(d)
    def test_duplicate_success_failure(self):
        d=manifest()
        d["errors"]["DFII10"]="duplicate"
        with self.assertRaises(ValueError):pe.build(d)
    def test_not_official_score(self):
        d=manifest()
        d["eligible_for_official_glt_score"]=True
        with self.assertRaises(ValueError):pe.build(d)
    def test_invalid_release_verified(self):
        d=manifest()
        d["series"]["DFII10"]["release_timestamp_verified"]=True
        with self.assertRaises(ValueError):pe.build(d)
    def test_wrong_unit(self):
        d=manifest()
        d["series"]["DFII10"]["unit"]="USD"
        with self.assertRaises(ValueError):pe.build(d)
    def test_write_files(self):
        with tempfile.TemporaryDirectory() as root:
            root=Path(root)
            p=root/"run"/"manifest.json"
            p.parent.mkdir(parents=True)
            p.write_text(json.dumps(manifest()),encoding="utf-8")
            out=pe.build(json.loads(p.read_text()))
            (root/"feed").mkdir()
            (root/"feed"/"fred_latest.json").write_text(json.dumps(out),encoding="utf-8")
            (root/"feed"/"fred_latest.md").write_text(pe.markdown(out),encoding="utf-8")
            self.assertEqual(json.loads((root/"feed"/"fred_latest.json").read_text())["schema"],"glt-fred-evidence-summary-v1")
if __name__=="__main__":unittest.main()
