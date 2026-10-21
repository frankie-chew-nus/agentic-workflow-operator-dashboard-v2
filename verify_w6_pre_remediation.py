"""Read-only pre-remediation verification manifest. Never uploads DB or private evidence.

Usage: py verify_w6_pre_remediation.py
Produces sanitized JSON in gate2_submission_evidence/governance_tests/.
Run only with dashboard/workflow stopped to stabilize evidence-file hashes.
"""
import datetime,hashlib,json,sqlite3,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
DB=BASE/"gate2_operator_app_v1"/"evidence"/"operator.db"
BACKUPS=DB.parent/"backups"
OUT=ROOT/"gate2_submission_evidence"/"governance_tests"/"w6_pre_remediation_manifest.json"
ADAPTERS=[
 BASE/"gate2_operator_app_v1"/"b_resume.py",
 BASE/"gate2_operator_app_v1"/"b_regression_guard.py",
 BASE/"gate2_operator_app_v1"/"b_resume_model_flow_v1_1.py",
]
def digest(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
 return h.hexdigest()
def integrity(p):
 con=sqlite3.connect(p.resolve().as_uri()+"?mode=ro",uri=True)
 try:return con.execute("PRAGMA integrity_check").fetchone()[0]
 finally:con.close()
def main():
 branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
 if branch!="fix/w6-b-governance-controls":raise SystemExit("Wrong branch")
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 unstaged=subprocess.run(["git","diff","--quiet"],cwd=ROOT).returncode
 staged=subprocess.run(["git","diff","--cached","--quiet"],cwd=ROOT).returncode
 if unstaged!=0 or staged!=0:raise SystemExit("Tracked files have changes; inspect before proceeding")
 if not DB.is_file():raise SystemExit("Original SQLite DB missing")
 backups=sorted(BACKUPS.glob("operator_pre_governance_fix_*.db"),key=lambda p:p.stat().st_mtime,reverse=True) if BACKUPS.is_dir() else []
 if not backups:raise SystemExit("No matching backup found")
 backup=backups[0]
 original_check=integrity(DB);backup_check=integrity(backup)
 if original_check!="ok" or backup_check!="ok":raise SystemExit("Database integrity failed")
 if any(not p.is_file() for p in ADAPTERS):raise SystemExit("Required adapter missing")
 original=sqlite3.connect(DB.resolve().as_uri()+"?mode=ro",uri=True)
 copy=sqlite3.connect(backup.resolve().as_uri()+"?mode=ro",uri=True)
 try:
  tables=[x[0] for x in original.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
  if tables!=[x[0] for x in copy.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]:raise SystemExit("Backup schema differs")
  counts={}
  for t in tables:
   quoted='"'+t.replace('"','""')+'"'
   a=original.execute("SELECT COUNT(*) FROM "+quoted).fetchone()[0]
   b=copy.execute("SELECT COUNT(*) FROM "+quoted).fetchone()[0]
   counts[t]={"original":a,"backup":b,"match":a==b}
 finally:original.close();copy.close()
 if not all(v["match"] for v in counts.values()):raise SystemExit("Row counts differ; original may have changed since backup")
 obj={"evidence_class":"PRE_REMEDIATION_SNAPSHOT_VERIFICATION","timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "branch":branch,"git_commit":commit,"tracked_files_clean":True,"untracked_files_excluded_from_check":True,
  "database":{"original_sha256":digest(DB),"backup_sha256":digest(backup),
   "original_integrity":original_check,"backup_integrity":backup_check,
   "table_row_counts":counts,"note":"Row counts and integrity match; logical database equality not proven"},
  "adapters":[{"file":p.name,"sha256":digest(p)} for p in ADAPTERS],
  "raw_database_uploaded":False,"production_authority":False,
  "verification":"PASS"}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 if OUT.exists():raise SystemExit("Manifest already exists; refusing overwrite")
 OUT.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8")
 print("Manifest:",OUT.relative_to(ROOT))
 print("Verification: PASS; sanitized manifest only")
if __name__=="__main__":main()
