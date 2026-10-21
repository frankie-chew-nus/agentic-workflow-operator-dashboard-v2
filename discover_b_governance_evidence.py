"""Discover actual local T04/T05/T09/T10 evidence candidates, read-only.

Never auto-approves, changes manifests, or touches active databases.
Search is limited to explicit roots; paths/hashes are recommendations for review.
"""
import argparse,hashlib,json
from pathlib import Path
TOKENS=("T04","T05","T09","T10")
EXTS={".json",".md",".txt",".csv",".log"}
def sha(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
 return h.hexdigest()
def discover(roots):
 found={t:[] for t in TOKENS}
 for root in roots:
  root=Path(root).resolve()
  if not root.exists():continue
  for path in root.rglob("*"):
   if not path.is_file() or path.suffix.lower() not in EXTS:continue
   if any(x in path.parts for x in (".git","__pycache__","node_modules")):continue
   if path.stat().st_size>2_000_000:continue
   try:
    content=path.read_text(encoding="utf-8",errors="replace")
    matches=[t for t in TOKENS if t.lower() in path.name.lower() or t in content]
    if not matches:continue
    record={"path":str(path),"sha256":sha(path),"bytes":path.stat().st_size,
            "review_status":"UNVERIFIED_CANDIDATE"}
    for t in matches:found[t].append(record)
   except OSError:continue
 return found
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--root",action="append",required=True)
 a=p.parse_args()
 print(json.dumps({"status":"EVIDENCE_DISCOVERY_ONLY","candidates":discover(a.root),
  "operator_approved":False,"manifest_modified":False},indent=2))
