"""Read-only backup manifest audit; never restores active files."""
import argparse,hashlib,json,sqlite3
from pathlib import Path
def check(directory):
 root=Path(directory).resolve()
 m=json.loads((root/"backup_manifest.json").read_text(encoding="utf-8"))
 failures=[]
 for entry in m.get("files",[]):
  rel=Path(entry["backup"])
  p=(root/rel).resolve()
  if not p.is_relative_to(root) or not p.is_file():
   failures.append("MISSING:"+str(rel));continue
  digest=hashlib.sha256(p.read_bytes()).hexdigest()
  if digest!=entry["sha256"]:failures.append("HASH:"+str(rel))
  if p.suffix.lower()==".db":
   c=sqlite3.connect(p.as_uri()+"?mode=ro",uri=True)
   try:
    if c.execute("PRAGMA integrity_check").fetchone()[0]!="ok":failures.append("SQLITE:"+str(rel))
   finally:c.close()
 return {"status":"PASS" if not failures else "FAIL","files_checked":len(m.get("files",[])),
  "failures":failures,"restore_performed":False,"active_files_modified":False}
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--backup-dir",required=True);a=p.parse_args()
 print(json.dumps(check(a.backup_dir),indent=2))
