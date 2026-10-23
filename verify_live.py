"""Run against your own already-started supervisor. Saves real HTTP evidence.
Usage: python verify_live.py --runtime PATH --output PATH [--url URL]
Use a disposable runtime; never point this at another person's application.
"""
import argparse,json,time,urllib.request,urllib.error,sqlite3,os,signal
from pathlib import Path
from datetime import datetime,timezone
p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);p.add_argument('--output',required=True);p.add_argument('--url',default='http://127.0.0.1:5082');args=p.parse_args()
runtime=Path(args.runtime).resolve();out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
source=Path(__file__).resolve().parent
sample=json.loads((source/'data/sample_inventory.json').read_text());timeline=[]
def record(event,**kw):
    timeline.append(dict(time=datetime.now(timezone.utc).isoformat(),event=event,**kw))
def request(path,data=None):
    req=urllib.request.Request(args.url+path,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=5) as r:return r.status,r.read()
    except urllib.error.HTTPError as e:return e.code,e.read()
def capture(name,path='/api/health',data=None):
    code,body=request(path,data);(out/(name+'.json')).write_bytes(body)
    record(name,http=code);return code,json.loads(body)
code,normal=capture('01_normal');assert code==200 and normal['health']=='HEALTHY'
code,saved=capture('02_workbook_review','/api/reviews',sample);assert code==201
expected=json.loads((source/'data/workbook_expected.json').read_text())
assert all(all(actual[k]==ref[k] for k in ref) for actual,ref in zip(saved['results'],expected))
code,refused=capture('03_invalid_refusal','/api/reviews',[dict(sample[1],on_hand=-1)]);assert code==400
code,edge=capture('04_safety_stock_case','/api/reviews',[dict(sample[3],safety_stock=20)]);assert code==201 and edge['results'][0]['order_qty']==38
_,before=capture('05_history_before','/api/history')
marker=runtime/'storage.unavailable';assert not marker.exists()
try:
    marker.touch();record('FAILURE_INTRODUCED',action='Create storage.unavailable in the test runtime')
    code,failed=capture('06_failed');assert code==503 and failed['health']=='FAILED'
    code,blocked=capture('07_save_blocked','/api/reviews',sample);assert code==503
    (out/'failed_dashboard.html').write_bytes(request('/')[1])
finally:
    marker.unlink(missing_ok=True);record('RECOVERY_ACTION',action='Remove only the control file')
code,recovered=capture('08_recovered');assert code==200 and recovered['health']=='HEALTHY'
_,after=capture('09_history_after','/api/history');assert before==after
code,new=capture('10_new_review','/api/reviews',sample);assert code==201
# A separate process-termination test verifies the supervisor, not the control-file simulation.
oldpid=recovered['pid'];assert oldpid==int((runtime/'child.pid').read_text())
(runtime/'kill-child.once').touch();record('CHILD_KILL_REQUESTED',pid=oldpid,mechanism='Supervisor opt-in control')
start=time.monotonic();restart=None
while time.monotonic()-start<12:
    try:
        code,body=request('/api/health');state=json.loads(body)
        if code==200 and state['pid']!=oldpid:restart=state;break
    except (OSError,ValueError):pass
    time.sleep(.2)
assert restart,'Supervisor did not recover in 12 seconds'
record('PROCESS_RECOVERED',pid=restart['pid'],seconds=time.monotonic()-start)
_,final=capture('11_final_history','/api/history');assert any(r['id']==new['id'] for r in final)
assert all(r in final for r in before)
(out/'recovered_dashboard.html').write_bytes(request('/')[1])
(out/'events.json').write_bytes(request('/api/events')[1])
with sqlite3.connect(runtime/'inventory.db') as c,sqlite3.connect(out/'inventory.db') as backup:
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok';c.backup(backup)
(out/'supervisor.jsonl').write_bytes((runtime/'supervisor.jsonl').read_bytes())
(out/'events.jsonl').write_bytes((runtime/'events.jsonl').read_bytes())
(out/'timeline.json').write_text(json.dumps(timeline,indent=2))
(out/'result.json').write_text(json.dumps(dict(workbook_cases_matched=6,invalid_refused=True,safety_stock_order=38,history_preserved=True,integrity_check='ok',supervisor_restarted=True,final_health=restart['health'],partner_handoff=False),indent=2))
print(json.dumps(timeline,indent=2))
