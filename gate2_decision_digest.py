"""Sanitized Human decision digest with local DB fingerprint; no rationale export."""
import hashlib,json,sqlite3
from pathlib import Path
def digest(root):
 p=Path(root)/"operator.db"
 if not p.is_file():return {"state":"MISSING_LEDGER","decisions":[]}
 con=sqlite3.connect(p.as_uri()+"?mode=ro",uri=True)
 try:rows=con.execute("SELECT id,candidate_id,decision,created_at FROM decisions ORDER BY created_at,id").fetchall()
 finally:con.close()
 out=[{"id":str(i),"candidate_id":str(c),"action":str(a),"created_at":str(t)} for i,c,a,t in rows]
 return {"state":"INDEX_ONLY_UNVERIFIED_DECISION_AUTHORITY","count":len(out),
         "source_db_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"decisions":out,
         "note":"Decision metadata does not prove authority. Rationale and raw database remain local."}
