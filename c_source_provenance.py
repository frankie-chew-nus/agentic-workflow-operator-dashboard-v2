"""Read-only C source authority provenance inspection; never rewrites expected hashes."""
import argparse,ast,hashlib,json,re
from pathlib import Path

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):
    try:return json.loads(path.read_text(encoding="utf-8"))
    except Exception:return {}
def inspect(root,run):
    summary=load(run/"c_run_summary.json");hold=summary.get("hold") or {}
    expected=hold.get("expected");actual=hold.get("actual")
    files=[]
    for p in sorted(root.glob("*.py")):
        try:
            txt=p.read_text(encoding="utf-8",errors="replace")
            relevant=bool(re.search(r"source.hash|hashlib|sha256|HOLD_FOR_HUMAN|candidate_code_executed_downstream",txt,re.I))
            if not relevant:continue
            matches=[]
            for no,line in enumerate(txt.splitlines(),1):
                if re.search(r"source.hash|hashlib|sha256|HOLD_FOR_HUMAN|candidate_code_executed_downstream",line,re.I):
                    matches.append({"line":no,"snippet":line.strip()[:180]})
            files.append({"file":p.name,"sha256":digest(p),"references":matches[:35]})
        except OSError:continue
    result={
      "state":"C_SOURCE_PROVENANCE_INSPECTED","candidate_id":summary.get("candidate_id"),
      "version":summary.get("version"),"reason":hold.get("reason"),
      "expected":expected,"actual":actual,"c_source_hash_logic":files,
      "finding":"Inspection only. Source hash mismatch remains a governance HOLD.",
      "next":"Verify the expected-hash authority and generated-source hashing algorithm against the existing C build; do not substitute actual for expected.",
      "expected_hash_overridden":False,"candidate_code_executed_downstream":False
    }
    out=run/"source_provenance_inspection.json"
    out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--c-root",required=True);p.add_argument("--run-root",required=True);a=p.parse_args()
    print(json.dumps(inspect(Path(a.c_root),Path(a.run_root)),indent=2))
