import csv,datetime as dt,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from glt import calculate,timestamp,qualified_state
ROOT=Path(__file__).resolve().parents[1]
class TestGLT(unittest.TestCase):
 def test_empty(self):
  r=calculate(ROOT,timestamp('2026-11-20T08:00:00+08:00'))
  self.assertEqual(r['coverage'],0);self.assertFalse(r['publishable']);self.assertIsNone(r['composite_score'])
 def test_fixed_weights(self):
  with (ROOT/'config/indicators.csv').open(encoding='utf-8') as f:cfg=list(csv.DictReader(f))
  self.assertEqual(len(cfg),19)
  self.assertEqual({k:sum(int(x['points']) for x in cfg if x['layer']==k) for k in ['L1','L2','L3','L4']},{'L1':30,'L2':25,'L3':20,'L4':25})
 def test_boundary(self):
  self.assertEqual([qualified_state(i) for i in [29.9,30,44.9,45,64.9,65,79.9,80]],['强势收紧','温和收紧','温和收紧','中性震荡','中性震荡','温和宽松','温和宽松','强势宽松'])
 def test_timezones(self):
  with self.assertRaises(ValueError):timestamp('2026-11-20T08:00:00')
 def test_no_context_auto_score(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);(root/'config').mkdir();(root/'data').mkdir()
   (root/'config/indicators.csv').write_bytes((ROOT/'config/indicators.csv').read_bytes())
   (root/'data/calibration.csv').write_bytes((ROOT/'data/calibration.csv').read_bytes())
   (root/'data/observations.csv').write_text('indicator_id,observation_date,published_at,value,unit,source_url,retrieved_at,revision,transform\ntga,2026-11-18,2026-11-19T12:00:00+00:00,900,Millions of USD,https://example.org,2026-11-19T13:00:00+00:00,initial,raw\n',encoding='utf-8')
   r=calculate(root,timestamp('2026-11-20T08:00:00+08:00'))
   self.assertEqual(next(x for x in r['indicators'] if x['indicator_id']=='tga')['status'],'requires_context_review')
 def test_future_publication_excluded(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);(root/'config').mkdir();(root/'data').mkdir()
   (root/'config/indicators.csv').write_bytes((ROOT/'config/indicators.csv').read_bytes())
   (root/'data/calibration.csv').write_bytes((ROOT/'data/calibration.csv').read_bytes())
   (root/'data/observations.csv').write_text('indicator_id,observation_date,published_at,value,unit,source_url,retrieved_at,revision,transform\nvix,2026-11-19,2026-11-20T15:00:00+00:00,25,Index,https://example.org,2026-11-20T15:01:00+00:00,initial,raw\n',encoding='utf-8')
   r=calculate(root,timestamp('2026-11-20T08:00:00+08:00'))
   self.assertEqual(next(x for x in r['indicators'] if x['indicator_id']=='vix')['status'],'missing')
if __name__=='__main__':unittest.main()
