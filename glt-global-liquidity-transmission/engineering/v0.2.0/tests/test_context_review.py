import csv,datetime as dt,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from glt import calculate,timestamp
ROOT=Path(__file__).resolve().parents[1]
class ContextReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        (self.root/'data').mkdir();(self.root/'config').mkdir()
        for name in ('config/indicators.csv','data/calibration.csv'):
            (self.root/name).write_bytes((ROOT/name).read_bytes())
        (self.root/'data/observations.csv').write_text(
          'indicator_id,observation_date,published_at,value,unit,source_url,retrieved_at,revision,transform\n'
          'tga,2026-11-18,2026-11-19T12:00:00+00:00,900,Millions of USD,https://example.org/dts,2026-11-19T13:00:00+00:00,initial,raw\n',encoding='utf-8')
    def tearDown(self):self.temp.cleanup()
    def review(self,time='2026-11-19T14:00:00+00:00',source='https://example.org/dts',score='60',status='approved'):
        (self.root/'data/context_reviews.csv').write_text(
          'indicator_id,observation_date,reviewed_at,reviewer,score,evidence_url,methodology_version,rationale,status,source_url\n'
          f'tga,2026-11-18,{time},reviewer-A,{score},https://example.org/proof,V1.0,Verified treasury liquidity context,{status},{source}\n',
          encoding='utf-8')
    def status(self):
        r=calculate(self.root,timestamp('2026-11-20T08:00:00+08:00'))
        return next(i for i in r['indicators'] if i['indicator_id']=='tga'),r
    def test_approved_context_scores(self):
        self.review()
        x,r=self.status()
        self.assertEqual(x['status'],'valid')
        self.assertEqual(x['score'],60)
        self.assertEqual(r['covered_points'],8)
        self.assertIsNone(r['layers']['L1']['score'])
    def test_future_review_not_accepted(self):
        self.review(time='2026-11-21T14:00:00+00:00')
        self.assertEqual(self.status()[0]['status'],'requires_context_review')
    def test_mismatched_source_not_accepted(self):
        self.review(source='https://example.org/other')
        self.assertEqual(self.status()[0]['status'],'requires_context_review')
    def test_unapproved_review_not_accepted(self):
        self.review(status='draft')
        self.assertEqual(self.status()[0]['status'],'requires_context_review')
    def test_invalid_score_not_accepted(self):
        self.review(score='110')
        self.assertEqual(self.status()[0]['status'],'requires_context_review')
if __name__=='__main__':unittest.main()
