"""Disposable-only release transaction with fail-closed authority and idempotency.

Not wired into active dashboard. Caller supplies independent verifier; mock verifier
is allowed only in disposable tests. SQLite transaction prevents duplicate release.
"""
import sqlite3
from b_release_authority_binding_v1 import evaluate_release

def attempt(conn,candidate_id,research_id,context,verifier,*,disposable=False):
 if not disposable:
  return {"state":"HOLD","reason":"ACTIVE_INTEGRATION_NOT_APPROVED"}
 conn.execute("BEGIN IMMEDIATE")
 try:
  row=conn.execute("SELECT state,research_id FROM candidates WHERE id=?",(candidate_id,)).fetchone()
  if not row or row[0]!="B_REVIEW" or row[1]!=research_id:
   conn.rollback();return {"state":"HOLD","reason":"CANDIDATE_STATE_OR_COMMISSION_MISMATCH"}
  previous=conn.execute("SELECT COUNT(*) FROM decisions WHERE candidate_id=? AND decision='RELEASE_TO_C'",(candidate_id,)).fetchone()[0]
  if previous:
   conn.rollback();return {"state":"HOLD","reason":"DUPLICATE_RELEASE"}
  result=evaluate_release(candidate_id,research_id,context,verifier=verifier,disposable=True)
  if not result["release_authorized"]:
   conn.rollback();return {"state":"HOLD","reason":",".join(result["failures"])}
  import uuid,datetime
  conn.execute("INSERT INTO decisions(id,research_id,candidate_id,decision,rationale,created_at) VALUES(?,?,?,?,?,?)",
   ("SYN-"+uuid.uuid4().hex[:10],research_id,candidate_id,"RELEASE_TO_C",
    "Synthetic disposable release only",datetime.datetime.now(datetime.timezone.utc).isoformat()))
  conn.execute("UPDATE candidates SET state='READY_FOR_C',stage='B' WHERE id=?",(candidate_id,))
  conn.commit()
  return {"state":"DISPOSABLE_RELEASED","production_authority":False}
 except Exception:
  conn.rollback()
  raise
