"""Local inventory application with atomic reviews and structured event logs."""
import csv,io,json,os,sqlite3,threading,uuid
from pathlib import Path
from datetime import datetime,timezone
from flask import Flask,request,render_template,jsonify,Response
from logic import review,ValidationError,POLICY
ROOT=Path(__file__).resolve().parent

def create_app(runtime=None):
    app=Flask(__name__)
    app.config['MAX_CONTENT_LENGTH']=256*1024
    folder=Path(runtime or os.environ.get('INVENTORY_RUNTIME',ROOT/'runtime')).resolve()
    folder.mkdir(parents=True,exist_ok=True)
    db=folder/'inventory.db'; logpath=folder/'events.jsonl'; lock=threading.Lock()
    def event(kind,**fields):
        record=dict(timestamp=datetime.now(timezone.utc).isoformat(),component='inventory',event=kind,pid=os.getpid(),**fields)
        with lock,logpath.open('a') as f:f.write(json.dumps(record,allow_nan=False)+'\n')
    def connect():
        c=sqlite3.connect(db,timeout=2);c.row_factory=sqlite3.Row;return c
    with connect() as c:
        c.execute('PRAGMA journal_mode=WAL')
        c.executescript('''CREATE TABLE IF NOT EXISTS reviews(id TEXT PRIMARY KEY, created_at TEXT NOT NULL,policy TEXT NOT NULL,results TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS app_state(id INTEGER PRIMARY KEY CHECK(id=1),last_health TEXT NOT NULL);
        INSERT OR IGNORE INTO app_state VALUES(1,'RECOVERING');''')
    last_health = 'RECOVERING'
    def health():
        nonlocal last_health
        try:
            # Classroom failure injection leaves the database itself untouched.
            if (folder/'storage.unavailable').exists(): raise sqlite3.OperationalError('Controlled storage outage is active')
            with connect() as c:
                c.execute('BEGIN IMMEDIATE')
                prior=c.execute('SELECT last_health FROM app_state WHERE id=1').fetchone()[0]
                c.execute("UPDATE app_state SET last_health='HEALTHY' WHERE id=1")
            if last_health!='HEALTHY':event('HEALTH_CHANGED',previous=last_health,current='HEALTHY')
            last_health='HEALTHY'
            return 'HEALTHY',None
        except sqlite3.Error as e:
            if last_health!='FAILED':
                event('STORAGE_UNAVAILABLE',exception=type(e).__name__,reason=str(e))
                event('HEALTH_CHANGED',previous=last_health,current='FAILED')
            last_health='FAILED'
            # The separate file log survives the simulated DB outage.
            return 'FAILED','Storage is unavailable. No review can be saved. Inspect the logs and recovery guide.'
    def records():
        with connect() as c:return [dict(r) for r in c.execute('SELECT * FROM reviews ORDER BY created_at DESC')]
    @app.get('/')
    def home():
        state,error=health()
        rows=records() if state=='HEALTHY' else []
        return render_template('index.html',health=state,error=error,history=rows,policy=POLICY)
    @app.get('/api/health')
    def api_health():
        state,error=health();return jsonify(health=state,error=error,pid=os.getpid()),200 if state=='HEALTHY' else 503
    @app.get('/api/sample')
    def sample():return jsonify(json.loads((ROOT/'data/sample_inventory.json').read_text()))
    @app.post('/api/reviews')
    def save():
        payload=request.get_json(silent=True)
        try: results=review(payload)
        except ValidationError as e:
            event('INPUT_REFUSED',reason=str(e));return jsonify(error=str(e)),400
        state,error=health()
        if state!='HEALTHY':return jsonify(error=error),503
        rid=uuid.uuid4().hex;timestamp=datetime.now(timezone.utc).isoformat()
        try:
            with connect() as c:c.execute('INSERT INTO reviews VALUES(?,?,?,?)',(rid,timestamp,POLICY,json.dumps(results,allow_nan=False)))
        except sqlite3.Error as e:
            event('SAVE_FAILED',exception=type(e).__name__,reason=str(e));return jsonify(error='Review was not saved. Inspect storage and retry.'),503
        event('REVIEW_SAVED',review_id=rid,item_count=len(results),policy=POLICY)
        return jsonify(id=rid,created_at=timestamp,results=results),201
    @app.get('/api/history')
    def history():
        state,error=health()
        if state!='HEALTHY':return jsonify(error=error),503
        return jsonify([dict(r,results=json.loads(r['results'])) for r in records()])
    @app.get('/api/events')
    def logs():
        lines=logpath.read_text().splitlines()[-100:] if logpath.exists() else []
        return jsonify([json.loads(s) for s in lines])
    @app.get('/export/<rid>.csv')
    def export(rid):
        state,error=health()
        if state!='HEALTHY':return jsonify(error=error),503
        with connect() as c:r=c.execute('SELECT * FROM reviews WHERE id=?',(rid,)).fetchone()
        if r is None:return jsonify(error='Review not found.'),404
        rows=json.loads(r['results']);out=io.StringIO();w=csv.DictWriter(out,fieldnames=list(rows[0]))
        w.writeheader()
        # Prevent spreadsheet programs treating user labels as formulas.
        for row in rows:
            w.writerow({k:("'"+v if isinstance(v,str) and v.startswith(('=','+','-','@','\t','\r')) else v) for k,v in row.items()})
        event('REVIEW_EXPORTED',review_id=rid)
        return Response(out.getvalue(),mimetype='text/csv',headers={'Content-Disposition':f'attachment; filename=review-{rid}.csv'})
    @app.errorhandler(sqlite3.Error)
    def storage_error(e):
        event('STORAGE_ERROR',exception=type(e).__name__,reason=str(e))
        return jsonify(error='Storage operation failed. Preserve the logs and inspect the database.'),503
    @app.errorhandler(413)
    def too_large(_):return jsonify(error='Request exceeds the 256 KB limit.'),413
    event('APPLICATION_START',policy=POLICY)
    app.config.update(RUNTIME=folder,DB=db)
    return app

if __name__=='__main__':
    create_app().run(host='127.0.0.1',port=int(os.environ.get('INVENTORY_PORT','5082')),debug=False,use_reloader=False)
