"""Pre-integration backup of dashboard files and both SQLite databases.

Run locally before further HTTP integration tests. Uses SQLite online backup API
for consistent snapshots and verifies restored snapshot integrity. Never restores
or modifies active files. Keep backup OUTSIDE GitHub.
"""
import datetime,hashlib,json,shutil,sqlite3,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
SOURCES=[ROOT/"gate2.py",ROOT/"operator_artifacts.py",ROOT/"operator_paths.json",
 ROOT/"b_release_guard_candidate.py",ROOT/"b_release_authority_binding_v1.py",
 ROOT/"evidence"/"operator.db",PROJECT/"gate2_operator_app_v1"/"evidence"/"operator.db"]
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
 return h.hexdigest()
def main():
 missing=[str(p) for p in SOURCES if not p.is_file()]
 if missing:raise SystemExit("Required source missing; no complete backup: "+", ".join(missing))
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
 base=PROJECT/"Gate2_Evidence"/"W6_GOVERNANCE_ROLLBACK_BACKUPS"/stamp
 base.mkdir(parents=True,exist_ok=False)
 records=[]
 for src in SOURCES:
  relative=src.relative_to(PROJECT)
  dst=base/relative
  dst.parent.mkdir(parents=True,exist_ok=True)
  if src.suffix.lower()==".db":
   source=sqlite3.connect(src.resolve().as_uri()+"?mode=ro",uri=True)
   target=sqlite3.connect(dst)
   try:
    source.backup(target)
    check=target.execute("PRAGMA integrity_check").fetchone()[0]
    if check!="ok":raise RuntimeError("SQLite integrity failure: "+str(relative))
   finally:target.close();source.close()
   kind="SQLITE_ONLINE_BACKUP"
  else:
   shutil.copy2(src,dst)
   if sha(src)!=sha(dst):raise RuntimeError("Hash mismatch: "+str(relative))
   kind="BYTE_IDENTICAL_COPY"
  records.append({"source":str(relative),"backup":str(dst.relative_to(base)),
                  "backup_type":kind,"sha256":sha(dst),"size_bytes":dst.stat().st_size})
 manifest={"mode":"PRE_INTEGRATION_BACKUP","created_at_utc":stamp,
  "git_branch":subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip(),
  "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
  "files":records,"sqlite_integrity":"PASS","restoration_performed":False,
  "active_files_modified":False}
 (base/"backup_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
 print("Backup directory:",base)
 print("Files backed up:",len(records))
 print("SQLite integrity: PASS")
 print("Manifest:",base/"backup_manifest.json")
 print("Keep this backup outside GitHub; databases may contain sensitive data.")
if __name__=="__main__":main()
