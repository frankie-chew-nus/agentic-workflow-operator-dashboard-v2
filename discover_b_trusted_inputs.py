"""Read-only discovery of B governance source candidates. No file contents exported.

Checks existing local artifacts by filename and schema only. Does not open credentials,
write to SQLite, alter evidence, or grant release authority.
"""
import json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
FOLDERS=[ROOT/"gate2_operator_app_v1",ROOT/"gate2_c_controller",ROOT/"gate2_dispatcher_app_v1"]
TERMS=("resource","dependency","dependencies","allowlist","approval","release","policy")
def main():
 candidates=[]
 for base in FOLDERS:
  if not base.is_dir():continue
  for p in base.rglob("*"):
   if not p.is_file() or any(x in p.parts for x in ("__pycache__", ".git")):continue
   if p.suffix.lower() not in (".json",".csv",".md",".py",".db"):continue
   if any(term in p.name.lower() for term in TERMS):
    candidates.append({"path":str(p.relative_to(ROOT)),"type":p.suffix.lower()})
 db=ROOT/"gate2_operator_app_v1"/"evidence"/"operator.db"
 schemas={}
 if db.is_file():
  con=sqlite3.connect(db.resolve().as_uri()+"?mode=ro",uri=True)
  try:
   for table in ("research","candidates","decisions","artifacts"):
    schemas[table]=[r[1] for r in con.execute('PRAGMA table_info("'+table+'")')]
  finally:con.close()
 report={"mode":"READ_ONLY_TRUSTED_INPUT_DISCOVERY",
  "candidate_files":sorted(candidates,key=lambda x:x["path"])[:120],
  "candidate_file_list_truncated":len(candidates)>120,
  "db_columns":schemas,
  "resource_inventory_authoritative":False,
  "dependency_allowlist_authoritative":False,
  "commission_release_count_authoritative":False,
  "rule_change_approval_authoritative":False,
  "note":"Filename and DB schema discovery only; Human verification required.",
  "writes_performed":False,"production_authority":False}
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
