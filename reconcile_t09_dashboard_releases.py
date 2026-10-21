"""Read-only T09 reconciliation of dashboard B->C Human decision records.

Inspects dashboard evidence/operator.db, NOT legacy B evidence/operator.db.
A recorded RELEASE_TO_C is a dashboard decision, not independently authenticated
Human identity or proof that downstream C consumed the release. No writes.
"""
import json,sqlite3,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DB=ROOT/"evidence"/"operator.db"
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
 return h.hexdigest()
def main():
 if not DB.is_file():raise SystemExit("HOLD: dashboard DB missing")
 con=sqlite3.connect(DB.resolve().as_uri()+"?mode=ro",uri=True)
 con.row_factory=sqlite3.Row
 try:
  required={"id","research_id","candidate_id","decision","created_at"}
  cols={r["name"] for r in con.execute("PRAGMA table_info(decisions)")}
  if not required.issubset(cols):raise SystemExit("HOLD: decision schema incomplete")
  records=list(con.execute("SELECT id,research_id,candidate_id,decision,created_at FROM decisions WHERE decision='RELEASE_TO_C' ORDER BY research_id,candidate_id,created_at"))
  commission={}
  for r in records:
   rid=r["research_id"] or ""
   g=commission.setdefault(rid,{"release_event_count":0,"distinct_candidates":set(),"decision_ids":set(),"incomplete_records":0})
   g["release_event_count"]+=1
   if not r["id"] or not r["candidate_id"] or not r["created_at"] or not rid:g["incomplete_records"]+=1
   if r["id"] in g["decision_ids"]:g["incomplete_records"]+=1
   g["decision_ids"].add(r["id"])
   if r["candidate_id"]:g["distinct_candidates"].add(r["candidate_id"])
  summary=[{"research_id":rid if rid else "MISSING","release_event_count":v["release_event_count"],
   "distinct_candidate_count":len(v["distinct_candidates"]),
   "duplicate_or_retry_events":v["release_event_count"]-len(v["distinct_candidates"]),
   "incomplete_records":v["incomplete_records"],
   "over_three":len(v["distinct_candidates"])>3}
   for rid,v in sorted(commission.items())]
  state_counts=[{"state":r["state"],"count":r["n"]} for r in con.execute("SELECT state,COUNT(*) AS n FROM candidates GROUP BY state")]
  print(json.dumps({"mode":"READ_ONLY_T09_DASHBOARD_RELEASE_RECONCILIATION",
   "db":"evidence/operator.db","db_sha256":sha(DB),
   "release_event_total":len(records),"commissions":summary,"candidate_state_counts":state_counts,
   "verified_human_identity":False,"downstream_C_consumption_verified":False,
   "historical_completeness_verified":False,
   "authoritative_ledger_approved":False,
   "verdict":"HOLD_PENDING_HUMAN_RECONCILIATION",
   "note":"Zero observed RELEASE_TO_C events would NOT establish zero historical releases.",
   "writes_performed":False,"production_authority":False},indent=2))
 finally:con.close()
if __name__=="__main__":main()
