"""Read-only B governance database schema and decision-type inventory.
No decision text, rationale, credentials, or candidate payload is exported.
"""
import json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
DB=ROOT/"gate2_operator_app_v1"/"evidence"/"operator.db"
def main():
 if not DB.is_file():raise SystemExit("DB missing")
 con=sqlite3.connect(DB.resolve().as_uri()+"?mode=ro",uri=True)
 try:
  tables={}
  for name in ("research","candidates","decisions","jobs","artifacts"):
   cols=[r[1] for r in con.execute('PRAGMA table_info("'+name+'")')]
   tables[name]=cols
  decisions=[{"decision":str(k),"count":n} for k,n in con.execute("SELECT decision,COUNT(*) FROM decisions GROUP BY decision ORDER BY decision")]
  out={"mode":"READ_ONLY_B_DB_SCHEMA_AUDIT","tables":tables,"decision_type_counts":decisions,
   "authoritative_commission_release_count":"NOT_ESTABLISHED",
   "human_rule_change_authority":"NOT_ESTABLISHED",
   "resource_inventory":"NOT_IDENTIFIED","dependency_allowlist":"NOT_IDENTIFIED",
   "writes_performed":False,"production_authority":False}
  print(json.dumps(out,indent=2))
 finally:con.close()
if __name__=="__main__":main()
