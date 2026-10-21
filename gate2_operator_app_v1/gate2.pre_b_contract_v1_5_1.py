import json,sqlite3,datetime,uuid,subprocess,threading,webbrowser,html,sys,hashlib
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import parse_qs

BASE=Path(__file__).resolve().parent
DB=BASE/"evidence"/"operator.db"
PROJECT=BASE.parent
CROOT=PROJECT/"gate2_c_controller"
PORT=8787

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def cx():
 DB.parent.mkdir(parents=True,exist_ok=True)
 c=sqlite3.connect(DB,timeout=30);c.row_factory=sqlite3.Row
 c.executescript("""
 CREATE TABLE IF NOT EXISTS research(id TEXT PRIMARY KEY,title TEXT,state TEXT,stage TEXT);
 CREATE TABLE IF NOT EXISTS candidates(id TEXT PRIMARY KEY,research_id TEXT,state TEXT,stage TEXT,version TEXT,detail TEXT,q INTEGER);
 CREATE TABLE IF NOT EXISTS decisions(id TEXT PRIMARY KEY,research_id TEXT,candidate_id TEXT,decision TEXT,rationale TEXT,created_at TEXT);
 CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,research_id TEXT,candidate_id TEXT,kind TEXT,state TEXT,detail TEXT,log_path TEXT,created_at TEXT,started_at TEXT,finished_at TEXT,return_code INTEGER);
 CREATE TABLE IF NOT EXISTS artifacts(id TEXT PRIMARY KEY,candidate_id TEXT,kind TEXT,path TEXT,sha256 TEXT,created_at TEXT);
 """);return c
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def decision(c,rid,cid,d,rat):
 c.execute("INSERT INTO decisions VALUES(?,?,?,?,?,?)",("DEC-"+uuid.uuid4().hex[:10].upper(),rid,cid,d,rat,now()))
def init():
 c=cx()
 if not c.execute("SELECT 1 FROM research").fetchone():
  rid="RES-XAUUSD";c.execute("INSERT INTO research VALUES(?,?,?,?)",(rid,"XAUUSD M1 Price Action","ACTIVE","B"))
  for x in [("CAND-B-001","C_FAIL","C","v2.1.1","0/50 PASS",1),("CAND-B-002","B_REVIEW","B","v2.1.2","Corrected B release awaiting Human review",2),("CAND-B-003","C_FAIL","C","v2.1.1","0/7 PASS",3)]:
   c.execute("INSERT INTO candidates VALUES(?,?,?,?,?,?,?)",(x[0],rid,x[1],x[2],x[3],x[4],x[5]))
  decision(c,rid,"CAND-B-002","RETURN_TO_B","Volatility expansion is not deterministically defined. Return to B for a corrected specification before C implementation.")
 c.commit();c.close()
def active_job(c):return c.execute("SELECT * FROM jobs WHERE state IN ('QUEUED','RUNNING') LIMIT 1").fetchone()
def queue(c,rid,cid,kind,detail):
 if active_job(c):return False
 jid="JOB-"+uuid.uuid4().hex[:10].upper();log=BASE/"evidence"/"logs"/(jid+".log");log.parent.mkdir(parents=True,exist_ok=True)
 c.execute("INSERT INTO jobs VALUES(?,?,?,?,?,?,?,?,?,?,?)",(jid,rid,cid,kind,"QUEUED",detail,str(log),now(),None,None,None));return True
def b_flow_cmd():
 return [sys.executable,str(BASE/"b_resume_model_flow_v1_1.py"),"--db",str(DB),"--register",str(CROOT/"inputs"/"candidate_strategy_register_v2_1_1_frozen.json"),"--candidate","CAND-B-002","--output-dir",str(BASE/"evidence"/"b_resume"/"CAND-B-002"),"--env",str(CROOT/".env")]
def run_job(j):
 if j["kind"]=="B_RESUME":
  cmd=b_flow_cmd()
 else:return 99,"No registered worker"
 with open(j["log_path"],"w",encoding="utf-8") as f:q=subprocess.run(cmd,cwd=BASE,stdout=f,stderr=subprocess.STDOUT,text=True)
 return q.returncode," ".join(cmd)
def dispatcher():
 while True:
  c=cx();j=c.execute("SELECT * FROM jobs WHERE state='QUEUED' ORDER BY created_at LIMIT 1").fetchone()
  if not j:c.close();threading.Event().wait(1);continue
  c.execute("UPDATE jobs SET state='RUNNING',started_at=? WHERE id=?",(now(),j["id"]))
  c.execute("UPDATE candidates SET state='B_RUNNING',stage='B',detail='Governed B correction running' WHERE id=?",(j["candidate_id"],));c.commit();c.close()
  rc,cmd=run_job(j)
  c=cx();c.execute("UPDATE jobs SET state='COMPLETE',finished_at=?,return_code=? WHERE id=?",(now(),rc,j["id"]))
  rel=BASE/"evidence"/"b_resume"/j["candidate_id"]/"b_corrected_release.json"
  if rc==0 and rel.exists():
   x=json.load(open(rel,encoding="utf-8"));ver=x.get("candidate",{}).get("version","")
   c.execute("UPDATE candidates SET state='B_REVIEW',stage='B',version=?,detail='Corrected B release awaiting Human review' WHERE id=?",(ver,j["candidate_id"]))
   c.execute("INSERT INTO artifacts VALUES(?,?,?,?,?,?)",("ART-"+uuid.uuid4().hex[:8],j["candidate_id"],"B_CORRECTED_RELEASE",str(rel),sha(rel),now()))
  else:c.execute("UPDATE candidates SET state='SYSTEM_HOLD',detail=? WHERE id=?",("B workflow failed. View "+j["log_path"],j["candidate_id"]))
  c.commit();c.close()
def review_data():
 p=BASE/"evidence"/"b_resume"/"CAND-B-002"/"b_corrected_release.json"
 if p.exists():return json.load(open(p,encoding="utf-8"))
 # Seed from the already-executed release if user copies it into this app later.
 return None

def journey_html(c,r,cs):
    active_stage=r["stage"]
    ac=next((x for x in cs if x["state"] in ("B_RUNNING","B_REVIEW","WAITING_FOR_B","READY_FOR_C","C_RUNNING","D_RUNNING","E_RUNNING","SYSTEM_HOLD","GOVERNANCE_HOLD")),None)
    defs={
      "A":("Research & Source Qualification","Grounded Researcher + Human Operator","Approved research evidence package / source register","Only Human-approved A evidence enters B.","Public evidence is qualified and frozen; B has no independent retrieval authority."),
      "B":("Evidence Synthesis & Strategy Formulation","Knowledge Archivist + Strategy Optimizer + Human Operator","Versioned Candidate Strategy Specifications","Human RELEASE / RETURN TO B / REJECT before C.","B owns the strategy concept and search envelope; returned candidates are reformulated and reassessed."),
      "C":("Local Integration & Stage 1 Backtesting","Existing local C CLI / Local Backtest Runner","Reproducible Stage 1 build, ledger, metrics, logs and hashes","Only C-PASS frozen candidate/version may proceed to D.","C operates within B authority; mandatory friction remains 9 pips."),
      "D":("Hidden OOS / Walk-Forward Validation","Local deterministic harness + MT5 + Human OOS boundary","Independent OOS ledger, metrics and integrity evidence","D PASS may proceed to E; D FAIL is withheld; integrity defects HOLD.","D uses unseen MT5 evidence and may not optimise against it."),
      "E":("Commissioning Audit & Decision","Human Operator + deterministic commissioning checks","Signed commissioning decision and frozen installation record","Terminal APPROVE / REJECT / CLOSE.","Human owns live-capital commissioning authority.")
    }
    order="ABCDE"
    idx=order.index(active_stage) if active_stage in order else 0
    cards=[]
    for i,k in enumerate(order):
        title,owner,output,handoff,detail=defs[k]
        if i<idx:
            state,status,cls="FROZEN","HANDED OVER TO "+order[i+1],"done"
        elif i==idx:
            state="ACTIVE"
            status="HUMAN ACTION REQUIRED" if ac and ac["state"] in ("B_REVIEW","WAITING_FOR_B","SYSTEM_HOLD","GOVERNANCE_HOLD") else "WORKFLOW ACTIVE"
            cls="active"
        else:
            state,status,cls="NOT STARTED","Awaiting "+order[i-1]+" handoff","future"
        extra=""
        if k=="B" and ac:
            extra="<p><b>Current candidate:</b> "+html.escape(ac["id"])+" · "+html.escape(ac["version"] or "")+" · "+html.escape(ac["state"])+"</p><p><b>Current detail:</b> "+html.escape(ac["detail"])+"</p>"
        cards.append('<section class="journey-card '+cls+'"><div class="journey-head"><span class="stage-letter">'+k+'</span><div><b>'+html.escape(title)+'</b><div class="state">'+state+' · '+status+'</div></div></div><p><b>Owner:</b> '+html.escape(owner)+'</p><p><b>Produces:</b> '+html.escape(output)+'</p><p><b>Handoff:</b> '+html.escape(handoff)+'</p><p><b>Operating context:</b> '+html.escape(detail)+'</p>'+extra+'</section>')
    return '<div class="card"><h2>Full research journey</h2><p class="muted">Persistent A→E context, evidence lineage and current operating position.</p><div class="journey">'+'<div class="arrow">↓</div>'.join(cards)+'</div></div>'



def embed_current_action_in_journey(page):
    candidates=[
      '<div class="card action"><b>ACTION REQUIRED — HUMAN B→C REVIEW</b>',
      '<div class="card hold"><b>ACTION REQUIRED — SYSTEM HOLD</b>',
      '<div class=card><b>ACTION REQUIRED</b><h2>Resume B</h2>'
    ]
    starts=[page.find(x) for x in candidates]
    starts=[x for x in starts if x >= 0]
    if not starts: return page
    start=min(starts)
    end=page.find('<div class=card><h2>Candidate pipeline</h2>',start)
    if end < 0: return page
    action=page[start:end]
    page=page[:start]+page[end:]
    action=action.replace('<div class="card action">','<div class="embedded-action">',1)
    action=action.replace('<div class="card hold">','<div class="embedded-action hold-inline">',1)
    action=action.replace('<div class=card>','<div class="embedded-action">',1)
    if 'View corrected specification' not in action and 'View last corrected specification' not in action:
        rel=review_data()
        if rel and rel.get('candidate'):
            cand=rel['candidate']
            evidence='<details><summary>View last corrected specification</summary><pre>'+html.escape(json.dumps(cand,indent=2))+'</pre></details>'
            close=action.rfind('</div>')
            if close >= 0: action=action[:close]+evidence+action[close:]
    marker='</section><div class="arrow">↓</div><section class="journey-card future">'
    pos=page.find(marker)
    if pos < 0: return page
    return page[:pos]+action+'</div></section><div class="arrow">↓</div><section class="journey-card future">'+page[pos+len(marker):]


def expandable_log_html(log_path):
    try:
        p=Path(log_path)
        if not p.exists():
            return '<details><summary>View failure log</summary><pre>Log file not found: '+html.escape(str(p))+'</pre></details>'
        text=p.read_text(encoding='utf-8',errors='replace')
        return '<details><summary>View failure log</summary><pre>'+html.escape(text)+'</pre></details>'
    except Exception as e:
        return '<details><summary>View failure log</summary><pre>Unable to read log: '+html.escape(str(e))+'</pre></details>'

def render():
 c=cx();r=c.execute("SELECT * FROM research WHERE state='ACTIVE'").fetchone();cs=list(c.execute("SELECT * FROM candidates ORDER BY q"));job=active_job(c)
 b='<div class=card><small>ACTIVE RESEARCH</small><h1>'+html.escape(r["title"])+'</h1><div class=lock>One research / one active process. New research blocked until terminal.</div></div>'
 b+=journey_html(c,r,cs)
 if job:
  b+='<div class=card><b>RUNNING — NO ACTION REQUIRED</b><h2>'+job["candidate_id"]+'</h2><p>'+html.escape(job["detail"])+'</p><p>Evidence log: '+html.escape(job["log_path"])+'</p><button onclick="location.reload()">Refresh</button></div>'
 else:
  x=next((z for z in cs if z["id"]=="CAND-B-002"),None)
  if x and x["state"]=="B_REVIEW":
   rel=review_data()
   b+='<div class="card action"><b>ACTION REQUIRED — HUMAN B→C REVIEW</b><h2>CAND-B-002 '+html.escape(x["version"] or "")+'</h2>'
   if rel:
    cand=rel["candidate"];b+='<p><b>Hypothesis:</b> '+html.escape(cand.get("hypothesis",""))+'</p><p><b>Volatility expansion:</b> '+html.escape((cand.get("operator_assumptions",{}).get("volatility_expansion_definition") or cand.get("operator_assumptions",{}).get("volatility_expansion_condition","")))+'</p><p><b>Unresolved:</b> '+html.escape("; ".join(cand.get("unresolved_questions",[])))+'</p><details><summary>View corrected specification</summary><pre>'+html.escape(json.dumps(cand,indent=2))+'</pre></details>'
   else:b+='<p>Corrected release evidence has not yet been imported into this app. Return to B can still launch a fresh governed correction.</p>'
   b+='<form method=post action=/decide><textarea name=rationale required minlength=12 placeholder="Human rationale"></textarea><input type=hidden name=candidate value=CAND-B-002><button name=decision value=RETURN_TO_B>Return to B</button><button class=bad name=decision value=REJECT>Reject</button><button class=good name=decision value=RELEASE_TO_C>Release to C</button></form></div>'
  elif x and x["state"]=="SYSTEM_HOLD":
   b+='<div class="card hold"><b>ACTION REQUIRED — SYSTEM HOLD</b><h2>CAND-B-002</h2><p>'+html.escape(x["detail"])+'</p>'+expandable_log_html(x["detail"].split("View ",1)[1] if "View " in x["detail"] else "")+'<form method=post action=/decide><textarea name=rationale required minlength=12 placeholder="Human rationale"></textarea><input type=hidden name=candidate value=CAND-B-002><button name=decision value=RETRY_B>Retry same B work</button></form></div>'
  elif x and x["state"]=="WAITING_FOR_B":
   b+='<div class=card><b>ACTION REQUIRED</b><h2>Resume B</h2><form method=post action=/decide><textarea name=rationale required minlength=12></textarea><input type=hidden name=candidate value=CAND-B-002><button name=decision value=RESUME_B>Resume B</button></form></div>'
 b+='<div class=card><h2>Candidate pipeline</h2><table><tr><th>ID</th><th>Version</th><th>Stage</th><th>State</th><th>Detail</th></tr>'
 for x in cs:
  ar=x["state"] in ("B_RUNNING","B_REVIEW","WAITING_FOR_B","READY_FOR_C","C_RUNNING","D_RUNNING","E_RUNNING","SYSTEM_HOLD","GOVERNANCE_HOLD")
  rowcls=' class="candidate-active"' if ar else ""
  badge='<span class="active-badge">ACTIVE · HUMAN ACTION REQUIRED</span> ' if x["state"] in ("B_REVIEW","WAITING_FOR_B","SYSTEM_HOLD","GOVERNANCE_HOLD") else ('<span class="active-badge">ACTIVE</span> ' if ar else "")
  b+='<tr'+rowcls+'><td>'+badge+x["id"]+'</td><td>'+html.escape(x["version"] or "")+'</td><td>'+x["stage"]+'</td><td>'+x["state"]+'</td><td>'+html.escape(x["detail"])+'</td></tr>'
 b+='</table></div><div class=card><h2>Human decision ledger</h2><table><tr><th>Candidate</th><th>Decision</th><th>Rationale</th></tr>'
 for d in c.execute("SELECT * FROM decisions ORDER BY created_at DESC"):b+='<tr><td>'+d["candidate_id"]+'</td><td>'+d["decision"]+'</td><td>'+html.escape(d["rationale"])+'</td></tr>'
 b+='</table></div>';c.close()
 css="body{font-family:Segoe UI,Arial;background:#f3f5f7;margin:0}header{background:#111827;color:white;padding:18px}main{max-width:1120px;margin:auto;padding:22px}.card{background:white;padding:18px;margin:14px 0;border:1px solid #ddd;border-radius:12px}.lock{background:#fee2e2;padding:12px}.action{border-left:6px solid #2563eb}.hold{border-left:6px solid #d97706}textarea{width:96%;min-height:75px;padding:10px;font-size:16px}button{padding:10px 14px;margin:8px 5px 0 0;background:#2563eb;color:white;border:0;border-radius:6px}.good{background:#15803d}.bad{background:#b91c1c}table{width:100%;border-collapse:collapse}td,th{padding:9px;border-bottom:1px solid #ddd;text-align:left}pre{white-space:pre-wrap;background:#f8fafc;padding:12px;max-height:520px;overflow:auto;border:1px solid #d1d5db;border-radius:8px}details{margin:12px 0;border:1px solid #bfdbfe;border-radius:8px;background:white;padding:10px}details summary{cursor:pointer;font-weight:700;color:#1d4ed8}.embedded-action{margin-top:16px;padding-top:16px;border-top:2px solid #93c5fd}.embedded-action h2{margin-top:8px}.journey{display:grid;gap:10px}.journey-card{border:1px solid #d1d5db;border-radius:10px;padding:14px}.journey-card.done{background:#f0fdf4}.journey-card.active{border:2px solid #2563eb;background:#eff6ff}.journey-card.future{background:#f3f4f6;color:#6b7280}.journey-head{display:flex;gap:12px;align-items:center}.stage-letter{display:inline-flex;width:42px;height:42px;border-radius:50%;align-items:center;justify-content:center;background:#111827;color:white;font-weight:700;font-size:20px}.future .stage-letter{background:#9ca3af}.state{font-size:13px;margin-top:3px;font-weight:700}.arrow{text-align:center;font-size:22px;color:#6b7280}.muted{color:#6b7280}.candidate-active{background:#eff6ff}.active-badge{display:inline-block;font-size:11px;font-weight:700;padding:3px 6px;border-radius:10px;background:#2563eb;color:white;margin-right:5px}"
 return embed_current_action_in_journey("<html><head><meta charset=utf-8><style>"+css+"</style></head><body><header><h2>Gate 2 Operator App</h2></header><main>"+b+"</main></body></html>")
class H(BaseHTTPRequestHandler):
 def do_GET(self):
  b=render().encode();self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.end_headers();self.wfile.write(b)
 def do_POST(self):
  n=int(self.headers.get("Content-Length",0));f=parse_qs(self.rfile.read(n).decode());c=cx();r=c.execute("SELECT * FROM research WHERE state='ACTIVE'").fetchone()
  cid=f.get("candidate",[""])[0];d=f.get("decision",[""])[0];rat=f.get("rationale",[""])[0].strip();x=c.execute("SELECT * FROM candidates WHERE id=?",(cid,)).fetchone()
  if x and len(rat)>=12 and not active_job(c):
   if d in ("RETURN_TO_B","RESUME_B","RETRY_B"):
    decision(c,r["id"],cid,d,rat);queue(c,r["id"],cid,"B_RESUME","Governed B correction via configured model endpoint")
   elif d=="REJECT":
    decision(c,r["id"],cid,d,rat);c.execute("UPDATE candidates SET state='REJECTED',detail='Human rejected candidate' WHERE id=?",(cid,))
   elif d=="RELEASE_TO_C":
    decision(c,r["id"],cid,d,rat);c.execute("UPDATE candidates SET state='READY_FOR_C',stage='B',detail='Human released corrected B candidate to C queue' WHERE id=?",(cid,))
  c.commit();c.close();self.send_response(303);self.send_header("Location","/");self.end_headers()
 def log_message(self,*a):pass
if __name__=="__main__":
 init();threading.Thread(target=dispatcher,daemon=True).start();u=f"http://127.0.0.1:{PORT}/";print(u);threading.Timer(.5,lambda:webbrowser.open(u)).start();ThreadingHTTPServer(("127.0.0.1",PORT),H).serve_forever()
