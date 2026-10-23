import unittest,json,tempfile,sqlite3
from pathlib import Path
from logic import calculate,review,ValidationError
from app import create_app
ROOT=Path(__file__).resolve().parent
SAMPLE=json.loads((ROOT/'data/sample_inventory.json').read_text())
EXPECTED=json.loads((ROOT/'data/workbook_expected.json').read_text())
class CalculationTests(unittest.TestCase):
    def test_01_six_original_workbook_cases(self):
        for row,expected in zip(SAMPLE,EXPECTED):
            with self.subTest(sku=row['sku']):
                actual=calculate(row)
                for key in expected:self.assertEqual(actual[key],expected[key])
    def test_02_ignored_safety_stock_edge(self):
        result=calculate(dict(SAMPLE[3],safety_stock=20))
        self.assertEqual((result['demand'],result['reorder_point'],result['reorder'],result['order_qty']),(10,30,'YES',38))
        # Original C7 = B7 + 5 still yields 15 and NO at stock 22.
        self.assertEqual(5*2+5,15)
    def test_03_negative_stock_refused(self):
        with self.assertRaisesRegex(ValidationError,'On hand'):calculate(dict(SAMPLE[1],on_hand=-1))
    def test_04_sku_association_survives_sort_and_add(self):
        added=dict(SAMPLE[0],sku='NEW-1',on_hand=0)
        a={x['sku']:x for x in review(SAMPLE+[added])}
        b={x['sku']:x for x in review(list(reversed(SAMPLE+[added])))}
        self.assertEqual(a,b);self.assertEqual(a['NEW-1']['order_qty'],68)
    def test_reorder_boundary(self):
        for stock,decision,qty in [(29,'YES',31),(30,'YES',30),(31,'NO',0)]:
            r=calculate(dict(SAMPLE[1],on_hand=stock));self.assertEqual((r['reorder'],r['order_qty']),(decision,qty))
    def test_fractional_demand_rounds_up(self):
        r=calculate(dict(SAMPLE[1],on_hand=0,weekly_use='0.1',lead_time='1.5',safety_stock=0))
        self.assertEqual(r['order_qty'],1);self.assertEqual(r['exact_order_qty'],0.3)
    def test_zero_demand(self):
        r=calculate(dict(SAMPLE[1],on_hand=0,weekly_use=0,lead_time=0,safety_stock=0))
        self.assertEqual(r['order_qty'],0)
    def test_bad_numeric_inputs(self):
        for x in [None,'','abc','NaN','Infinity',True,1000001]:
            with self.subTest(value=x),self.assertRaises(ValidationError):calculate(dict(SAMPLE[0],weekly_use=x))
    def test_fractional_counts_refused(self):
        with self.assertRaises(ValidationError):calculate(dict(SAMPLE[0],safety_stock=1.5))
    def test_units_refused(self):
        for field,value in [('unit','pack'),('lead_unit','days')]:
            with self.assertRaises(ValidationError):calculate(dict(SAMPLE[0],**{field:value}))
    def test_missing_identifiers(self):
        for field in ['sku','item']:
            with self.assertRaises(ValidationError):calculate(dict(SAMPLE[0],**{field:None}))
    def test_duplicate_and_empty(self):
        for rows in [[],[SAMPLE[0],dict(SAMPLE[0],sku='p-100')],None,[3]]:
            with self.assertRaises(ValidationError):review(rows)
class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.folder=Path(self.temp.name)
        self.app=create_app(self.folder);self.client=self.app.test_client()
    def tearDown(self):self.temp.cleanup()
    def test_atomic_refusal_does_not_save_partial_rows(self):
        r=self.client.post('/api/reviews',json=[SAMPLE[0],dict(SAMPLE[1],on_hand=-1)])
        self.assertEqual(r.status_code,400);self.assertEqual(self.client.get('/api/history').json,[])
    def test_save_export_restart_preserves_history(self):
        r=self.client.post('/api/reviews',json=SAMPLE);self.assertEqual(r.status_code,201)
        rid=r.json['id'];self.assertIn(b'P-110',self.client.get('/export/'+rid+'.csv').data)
        other=create_app(self.folder).test_client();self.assertEqual(other.get('/api/history').json[0]['id'],rid)
    def test_controlled_failure_and_recovery(self):
        first=self.client.post('/api/reviews',json=SAMPLE).json
        marker=self.folder/'storage.unavailable';marker.touch()
        self.assertEqual(self.client.get('/api/health').status_code,503)
        self.assertEqual(self.client.post('/api/reviews',json=SAMPLE).status_code,503)
        marker.unlink()
        self.assertEqual(self.client.get('/api/health').json['health'],'HEALTHY')
        self.assertEqual(self.client.get('/api/history').json[0]['id'],first['id'])
        events=self.client.get('/api/events').json
        self.assertTrue(any(e.get('previous')=='FAILED' and e.get('current')=='HEALTHY' for e in events))
    def test_html_and_malformed_json(self):
        self.assertEqual(self.client.get('/').status_code,200)
        self.assertEqual(self.client.post('/api/reviews',data='{bad',content_type='application/json').status_code,400)
    def test_csv_formula_label_escaped(self):
        r=self.client.post('/api/reviews',json=[dict(SAMPLE[0],item='=1+1')]).json
        self.assertIn(b"'=1+1",self.client.get('/export/'+r['id']+'.csv').data)
    def test_actual_sqlite_lock_refuses_then_recovers(self):
        lock=sqlite3.connect(self.folder/'inventory.db');lock.execute('BEGIN EXCLUSIVE')
        try:self.assertEqual(self.client.get('/api/health').status_code,503)
        finally:lock.rollback();lock.close()
        self.assertEqual(self.client.get('/api/health').status_code,200)
if __name__=='__main__':unittest.main(verbosity=2)
