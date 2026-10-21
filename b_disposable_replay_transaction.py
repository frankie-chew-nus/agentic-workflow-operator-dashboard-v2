"""Disposable-only atomic signed release with durable nonce replay prevention.
No active dashboard integration or production authority.
"""
import datetime,sqlite3,uuid
from b_release_authority_binding_v1 import evaluate_release
from b_disposable_signed_authority import verify as signed_verify

def attempt(conn,candidate_id,research_id,context,key,*,disposable=False):
 if not disposable:return {"state":"HOLD","reason":"ACTIVE_INTEGRATION_NOT_APPROVED"}
 conn.execute("BEGIN IMMEDIATE")
 try:
  conn.execute("""CREATE TABLE IF NOT EXISTS disposable_authority_nonces(
   nonce TEXT PRIMARY KEY,candidate_id TEXT NOT NULL,research_id TEXT NOT NULL,
   used_at TEXT NOT NULL)""")
  row=conn.execute("SELECT state,research_id FROM candidates WHERE id=?",(candidate_id,)).fetchone()
  if not row or row[0]!="B_REVIEW" or row[1]!=research_id:
   conn.rollback();return {"state":"HOLD","reason":"CANDIDATE_STATE_OR_COMMISSION_MISMATCH"}
  if conn.execute("SELECT 1 FROM decisions WHERE candidate_id=? AND decision='RELEASE_TO_C'",(candidate_id,)).fetchone():
   conn.rollback();return {"state":"HOLD","reason":"DUPLICATE_RELEASE"}
  verifier=lambda cid,rid,ctx:signed_verify(cid,rid,ctx,key=key)
  result=evaluate_release(candidate_id,research_id,context,verifier=verifier,disposable=True)
  if not result["release_authorized"]:
   conn.rollback();return {"state":"HOLD","reason":",".join(result["failures"])}
  nonce=context["approval"]["nonce"]
  if conn.execute("SELECT 1 FROM disposable_authority_nonces WHERE nonce=?",(nonce,)).fetchone():
   conn.rollback();return {"state":"HOLD","reason":"AUTHORITY_NONCE_REPLAY"}
  now=datetime.datetime.now(datetime.timezone.utc).isoformat()
  conn.execute("INSERT INTO disposable_authority_nonces VALUES(?,?,?,?)",(nonce,candidate_id,research_id,now))
  conn.execute("INSERT INTO decisions(id,research_id,candidate_id,decision,rationale,created_at) VALUES(?,?,?,?,?,?)",
   ("SYN-"+uuid.uuid4().hex[:10],research_id,candidate_id,"RELEASE_TO_C","Disposable signed nonce-checked release",now))
  conn.execute("UPDATE candidates SET state='READY_FOR_C',stage='B' WHERE id=?",(candidate_id,))
  conn.commit()
  return {"state":"DISPOSABLE_RELEASED","production_authority":False}
 except Exception:
  conn.rollback()
  raise
