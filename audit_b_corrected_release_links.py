"""Read-only audit of B corrected-release artifact links; no candidate payloads exported.

Only aggregate counts and presence of linkage fields are printed. This is discovery,
not verification of release authorization or research-commission membership.
"""
import json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
DB=ROOT/"gate2_operator_app_v1"/"evidence"/"operator.db"
def main():
 if not DB.is_file():raise SystemExit("DB missing")
 con=sqlite3.connect(DB.resolve().as_uri()+"?mode=ro",uri=True)
 con.row_factory=sqlite3.Row
 try:
  cols={r[1] for r in con.execute("PRAGMA table_info(artifacts)")}
  if not {"candidate_id","kind","path","sha256"}.issubset(cols):raise SystemExit("Unexpected artifacts schema")
  rows=con.execute("SELECT candidate_id,kind,path,sha256 FROM artifacts WHERE kind='B_CORRECTED_RELEASE'").fetchall()
  findings=[]
  for row in rows:
   raw_path=Path(row["path"] or "")
   # Only examine files inside known local workflow evidence root.
   base=(ROOT/"gate2_operator_app_v1"/"evidence").resolve()
   p=(raw_path if raw_path.is_absolute() else ROOT/"gate2_operator_app_v1"/raw_path).resolve()
   safe=(p==base or base in p.parents)
   record={"file_within_expected_evidence_root":safe,"exists":False,
           "recorded_hash_present":bool(row["sha256"]),"candidate_id_present":bool(row["candidate_id"])}
   if safe and p.is_file():
    record["exists"]=True
    try:
     d=json.loads(p.read_text(encoding="utf-8"))
     record["state"]=d.get("state")
     record["has_parent_register_hash"]=bool(d.get("parent_register_sha256"))
     record["has_candidate_id"]=bool(d.get("candidate_id"))
     record["has_research_commission_id"]=bool(d.get("research_commission_id"))
     record["has_explicit_human_release_decision"]=bool(d.get("human_release_decision"))
    except (OSError,ValueError):record["parse_error"]=True
   findings.append(record)
  print(json.dumps({"mode":"READ_ONLY_B_CORRECTED_RELEASE_LINK_AUDIT",
   "artifact_count":len(rows),"records":findings,
   "authoritative_commission_release_count":"NOT_VERIFIED",
   "production_authority":False,"writes_performed":False},indent=2))
 finally:con.close()
if __name__=="__main__":main()
