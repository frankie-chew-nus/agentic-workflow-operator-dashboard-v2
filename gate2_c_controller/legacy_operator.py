import argparse,sqlite3,json,datetime,uuid
from pathlib import Path
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def dbopen(p):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);c=sqlite3.connect(p);c.row_factory=sqlite3.Row
 c.executescript("""CREATE TABLE IF NOT EXISTS candidates(candidate_id TEXT PRIMARY KEY,evidence_class TEXT,production_eligible INTEGER,stage TEXT,state TEXT,detail TEXT,updated_at TEXT);
 CREATE TABLE IF NOT EXISTS holds(hold_id TEXT PRIMARY KEY,candidate_id TEXT,trigger TEXT,reason TEXT,permitted_actions TEXT,status TEXT,decision TEXT,decision_reason TEXT,created_at TEXT,resolved_at TEXT);
 CREATE TABLE IF NOT EXISTS events(event_id TEXT PRIMARY KEY,candidate_id TEXT,event_type TEXT,payload TEXT,created_at TEXT);""");return c
def up(c,i,k,p,stage,state,d):
 c.execute("INSERT OR REPLACE INTO candidates VALUES(?,?,?,?,?,?,?)",(i,k,int(p),stage,state,d,now()))
def evt(c,edir,cid,t,p):
 eid="EVT-"+uuid.uuid4().hex[:10].upper();ts=now();c.execute("INSERT INTO events VALUES(?,?,?,?,?)",(eid,cid,t,json.dumps(p),ts))
 q=Path(edir);q.mkdir(parents=True,exist_ok=True);(q/(eid+".json")).write_text(json.dumps({"event_id":eid,"candidate_id":cid,"event_type":t,"payload":p,"created_at":ts},indent=2))
def init(c,e):
 up(c,"CAND-B-001","PRODUCTION",1,"C","STAGE1_FAIL","0/50 PASS")
 up(c,"CAND-B-002","PRODUCTION",1,"B_TO_C","HOLD_FOR_HUMAN","VOLATILITY_EXPANSION_UNDEFINED")
 up(c,"CAND-B-003","PRODUCTION",1,"C","STAGE1_FAIL","0/7 PASS")
 if not c.execute("SELECT 1 FROM holds WHERE candidate_id='CAND-B-002' AND status='OPEN'").fetchone():
  h="HOLD-"+uuid.uuid4().hex[:8].upper();c.execute("INSERT INTO holds VALUES(?,?,?,?,?,?,?,?,?,?)",(h,"CAND-B-002","SPECIFICATION_AMBIGUITY","Volatility expansion has no deterministic mathematical definition",json.dumps(["RETURN_TO_B","REJECT"]),"OPEN",None,None,now(),None))
 evt(c,e,None,"CONTROLLER_INITIALIZED",{});c.commit();print("CONTROLLER_INITIALIZED")
def status(c):
 print("GATE 2 OPERATOR CONSOLE");print("="*72)
 for r in c.execute("SELECT * FROM candidates ORDER BY candidate_id"):
  print(f"{r['candidate_id']:<15} {r['evidence_class']:<14} {r['stage']:<8} {r['state']:<22} {r['detail'] or ''}")
 print("\nOPEN HOLDS:",c.execute("SELECT COUNT(*) n FROM holds WHERE status='OPEN'").fetchone()["n"])
def holds(c):
 rs=list(c.execute("SELECT * FROM holds WHERE status='OPEN' ORDER BY created_at"))
 if not rs: print("No open HOLDs.")
 for r in rs: print(json.dumps(dict(r),indent=2))
def inspect(c,cid):
 r=c.execute("SELECT * FROM candidates WHERE candidate_id=?",(cid,)).fetchone()
 if not r: raise SystemExit("Unknown candidate")
 print(json.dumps(dict(r),indent=2))
 for h in c.execute("SELECT * FROM holds WHERE candidate_id=? ORDER BY created_at",(cid,)): print(json.dumps(dict(h),indent=2))
def resolve(c,e,hid,decision,reason):
 h=c.execute("SELECT * FROM holds WHERE hold_id=? AND status='OPEN'",(hid,)).fetchone()
 if not h: raise SystemExit("Open HOLD not found")
 if decision not in json.loads(h["permitted_actions"]): raise SystemExit("Decision not permitted")
 c.execute("UPDATE holds SET status='RESOLVED',decision=?,decision_reason=?,resolved_at=? WHERE hold_id=?",(decision,reason,now(),hid))
 st="RETURNED_TO_B" if decision=="RETURN_TO_B" else "REJECTED";c.execute("UPDATE candidates SET state=?,detail=?,updated_at=? WHERE candidate_id=?",(st,reason,now(),h["candidate_id"]))
 evt(c,e,h["candidate_id"],"HOLD_RESOLVED",{"hold_id":hid,"decision":decision,"reason":reason});c.commit();print("HOLD_RESOLVED")
def loadfix(c,e,p):
 x=json.load(open(p))
 if x.get("evidence_class") not in ["SYNTHETIC_TEST","SYSTEM_TEST"] or x.get("production_eligible") is not False: raise SystemExit("Invalid non-production fixture")
 up(c,x["candidate_id"],x["evidence_class"],0,x["stage"],x["state"],x.get("detail",""));evt(c,e,x["candidate_id"],"FIXTURE_LOADED",x);c.commit();print(json.dumps({"state":"FIXTURE_LOADED","candidate_id":x["candidate_id"]},indent=2))
def promote(c,e,cid,target):
 r=c.execute("SELECT * FROM candidates WHERE candidate_id=?",(cid,)).fetchone()
 if not r: raise SystemExit("Unknown candidate")
 if target=="LIVE" and not r["production_eligible"]:
  evt(c,e,cid,"PROMOTION_BLOCKED",{"target":"LIVE","reason":"NON_PRODUCTION"});c.commit();print(json.dumps({"state":"HOLD","reason":"NON_PRODUCTION_FIXTURE_CAN_NEVER_BE_LIVE"},indent=2));return
 if target=="D" and r["state"] not in ["STAGE1_PASS","SYNTHETIC_STAGE1_PASS"]: print(json.dumps({"state":"HOLD","reason":"C_STAGE1_PASS_REQUIRED"},indent=2));return
 print(json.dumps({"state":"ELIGIBLE_FOR_"+target,"candidate_id":cid},indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument("--db",default="evidence/controller/gate2_state.db");p.add_argument("--events",default="evidence/controller/events");s=p.add_subparsers(dest="cmd",required=True)
 s.add_parser("init");s.add_parser("status");s.add_parser("holds");q=s.add_parser("inspect");q.add_argument("candidate_id")
 q=s.add_parser("resolve");q.add_argument("hold_id");q.add_argument("--decision",required=True,choices=["RETURN_TO_B","REJECT"]);q.add_argument("--reason",required=True)
 q=s.add_parser("load-fixture");q.add_argument("path");q=s.add_parser("promotion-check");q.add_argument("candidate_id");q.add_argument("--target",required=True,choices=["D","LIVE"])
 a=p.parse_args();c=dbopen(a.db)
 if a.cmd=="init":init(c,a.events)
 elif a.cmd=="status":status(c)
 elif a.cmd=="holds":holds(c)
 elif a.cmd=="inspect":inspect(c,a.candidate_id)
 elif a.cmd=="resolve":resolve(c,a.events,a.hold_id,a.decision,a.reason)
 elif a.cmd=="load-fixture":loadfix(c,a.events,a.path)
 else:promote(c,a.events,a.candidate_id,a.target)
if __name__=="__main__":main()
