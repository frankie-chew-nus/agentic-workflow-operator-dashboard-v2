"""Disposable-only version-bound signed release with atomic nonce replay protection."""
import datetime,sqlite3,uuid
from b_release_authority_binding_v1 import evaluate_release
from b_disposable_trusted_approval import verify as trusted_verify
def attempt(conn,candidate_id,research_id,context,trusted_keys,*,revoked=None,disposable=False):
 if not disposable:return {"state":"HOLD","reason":"ACTIVE_INTEGRATION_NOT_APPROVED"}
 conn.execute("BEGIN IMMEDIATE")
 try:
  row=conn.execute("SELECT state,research_id,version FROM candidates WHERE id=?",(candidate_id,)).fetchone()
  if not row or row[0]!="B_REVIEW" or row[1]!=research_id or not row[2]:
   conn.rollback();return {"state":"HOLD","reason":"CANDIDATE_STATE_COMMISSION_OR_VERSION_MISMATCH"}
  version=row[2]
  if conn.execute("SELECT 1 FROM decisions WHERE candidate_id=? AND decision='RELEASE_TO_C'",(candidate_id,)).fetchone():
   conn.rollback();return {"state":"HOLD","reason":"DUPLICATE_RELEASE"}
  def verifier(cid,rid,ctx):
   return trusted_verify(cid,version,rid,ctx,trusted_keys=trusted_keys,revoked=revoked)
  result=evaluate_release(candidate_id,research_id,context,verifier=verifier,disposable=True)
  if not result["release_authorized"]:
   conn.rollback();return {"state":"HOLD","reason":",".join(result["failures"])}
  nonce=context["approval"]["nonce"]
  if conn.execute("SELECT 1 FROM disposable_authority_nonces WHERE nonce=?",(nonce,)).fetchone():
   conn.rollback();return {"state":"HOLD","reason":"AUTHORITY_NONCE_REPLAY"}
  now=datetime.datetime.now(datetime.timezone.utc).isoformat()
  conn.execute("INSERT INTO disposable_authority_nonces(nonce,candidate_id,research_id,used_at) VALUES(?,?,?,?)",(nonce,candidate_id,research_id,now))
  conn.execute("INSERT INTO decisions(id,research_id,candidate_id,decision,rationale,created_at) VALUES(?,?,?,?,?,?)",
   ("SYN-"+uuid.uuid4().hex[:10],research_id,candidate_id,"RELEASE_TO_C","Disposable version-bound signed release",now))
  conn.execute("UPDATE candidates SET state='READY_FOR_C',stage='B' WHERE id=? AND version=?",(candidate_id,version))
  if conn.total_changes<1:raise RuntimeError("UNEXPECTED_TRANSACTION_STATE")
  conn.commit()
  return {"state":"DISPOSABLE_RELEASED","candidate_version":version,"production_authority":False}
 except Exception:
  conn.rollback();raise
