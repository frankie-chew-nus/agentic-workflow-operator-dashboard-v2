"""Single-command final local B->C evidence/rollback acceptance.

Read-only on active files and DB. Does not set approval flags or activate release.
Performs actual restore into a temporary directory, validates SQLite, and
checks candidate-bound governance evidence files without inventing approval.
"""
import argparse,hashlib,json,shutil,sqlite3,tempfile
from pathlib import Path
from b_local_operator_release import check_evidence
from verify_b_rollback_readonly import check as backup_check
from b_one_command_readiness import latest_backup
from build_local_pin_dashboard_candidate import build
ROOT=Path(__file__).resolve().parent
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(config_path,backup_dir=None):
 active=ROOT/"gate2.py";before=digest(active)
 cfg=json.loads(Path(config_path).read_text(encoding="utf-8"))
 manifest=Path(cfg["evidence_manifest"]);m=json.loads(manifest.read_text(encoding="utf-8"))
 evidence=check_evidence(m.get("candidate_id"),m.get("candidate_version"),m.get("research_id"),manifest)
 backup=Path(backup_dir) if backup_dir else latest_backup(ROOT.parent)
 if backup is None:raise RuntimeError("BACKUP_NOT_FOUND")
 integrity=backup_check(backup)
 restored=[]
 with tempfile.TemporaryDirectory() as td:
  scratch=Path(td)
  for entry in json.loads((backup/"backup_manifest.json").read_text(encoding="utf-8"))["files"]:
   src=(backup/entry["backup"]).resolve()
   if not src.is_relative_to(backup.resolve()):raise RuntimeError("BACKUP_PATH_ESCAPE")
   dest=scratch/"restored"/entry["backup"]
   dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
   if digest(dest)!=entry["sha256"]:raise RuntimeError("RESTORE_HASH_MISMATCH")
   if dest.suffix.lower()==".db":
    db=sqlite3.connect(dest.as_uri()+"?mode=ro",uri=True)
    try:
     if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":raise RuntimeError("RESTORED_DB_INVALID")
    finally:db.close()
   restored.append(entry["backup"])
  target=scratch/"w6_disposable_dashboard"/"gate2.py"
  build(active,target)
  compile(target.read_text(encoding="utf-8"),str(target),"exec")
 return {"status":"ACCEPTANCE_REVIEW",
  "governance_evidence":"PASS" if evidence is None else evidence,
  "release_enabled":cfg.get("enabled") is True,
  "rollback_integrity":integrity["status"],
  "isolated_restore":"PASS","restored_files":len(restored),
  "dashboard_candidate_build":"PASS",
  "active_dashboard_unchanged":digest(active)==before,
  "activation_authorized":False,
  "next_decision":"Do not activate until actual evidence is checked and Operator explicitly approves"}
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--config",default=str(Path.home()/"MSI5002_Local_Approval"/"local_approval_config.json"))
 p.add_argument("--backup-dir")
 a=p.parse_args()
 try:print(json.dumps(run(a.config,a.backup_dir),indent=2))
 except Exception as exc:
  print(json.dumps({"status":"BLOCKED","reason":str(exc),"activation_authorized":False},indent=2))
  raise SystemExit(1)
