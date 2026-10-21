"""Read-only inventory of candidate release states and provenance, without row payloads.

No authority is inferred from a state name. Outputs counts only, no IDs, rationales,
paths, private contents or credentials. Does not modify SQLite.
"""
import json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
DB=ROOT/"gate2_operator_app_v1"/"evidence"/"operator.db"
def main():
 if not DB.is_file():raise SystemExit("Governance DB not found")
 con=sqlite3.connect(DB.resolve().as_uri()+"?mode=ro",uri=True)
 try:
  columns={t:{r[1] for r in con.execute('PRAGMA table_info("'+t+'")')} for t in ("candidates","decisions","artifacts")}
  groups={}
  if {"state","stage"}.issubset(columns["candidates"]):
   groups["candidate_states"]=[{"state":s,"stage":g,"count":n} for s,g,n in con.execute("SELECT state,stage,COUNT(*) FROM candidates GROUP BY state,stage ORDER BY state,stage")]
  if {"decision"}.issubset(columns["decisions"]):
   groups["decision_types"]=[{"decision":d,"count":n} for d,n in con.execute("SELECT decision,COUNT(*) FROM decisions GROUP BY decision ORDER BY decision")]
  if {"kind"}.issubset(columns["artifacts"]):
   groups["artifact_kinds"]=[{"kind":k,"count":n} for k,n in con.execute("SELECT kind,COUNT(*) FROM artifacts GROUP BY kind ORDER BY kind")]
  report={"mode":"READ_ONLY_B_RELEASE_PROVENANCE_AUDIT","groups":groups,
   "commission_release_count_verified":False,
   "human_policy_change_authority_verified":False,
   "approved_resources_verified":False,"approved_dependencies_verified":False,
   "note":"Counts and labels are discovery only. Do not treat these as release authority.",
   "writes_performed":False,"production_authority":False}
  print(json.dumps(report,indent=2))
 finally:con.close()
if __name__=="__main__":main()
