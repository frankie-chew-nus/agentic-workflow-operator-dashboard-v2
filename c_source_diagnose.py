import argparse,json,hashlib
from pathlib import Path

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
    try:return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:return {}
p=argparse.ArgumentParser()
p.add_argument("--run-root",required=True)
p.add_argument("--c-root",required=True)
a=p.parse_args()
root=Path(a.run_root);summary=load(root/"c_run_summary.json")
hold=summary.get("hold",{})
expected=hold.get("expected");actual=hold.get("actual")
files=[]
for path in [root/"c_boundary.json",root/"candidate_strategy_register_v2_1_3_frozen.json"]:
    if path.exists():files.append({"path":str(path),"sha256":sha(path)})
for path in sorted((root/"build").rglob("*.py")) if (root/"build").exists() else []:
    files.append({"path":str(path),"sha256":sha(path)})
matches=[x for x in files if x["sha256"] in (expected,actual)]
result={
 "state":"C_SOURCE_AUTHORITY_DIAGNOSIS",
 "candidate_id":summary.get("candidate_id"),
 "version":summary.get("version"),
 "reason":hold.get("reason"),
 "expected":expected,"actual":actual,
 "matched_artifacts":matches,
 "inspected_artifacts":files,
 "finding":"Source hash mismatch is confirmed; source authority cannot be reassigned from this evidence alone.",
 "safe_next_action":"Keep C blocked; investigate authoritative source-hash provenance in existing C build process.",
 "hash_override_permitted":False,
 "candidate_code_executed_downstream":hold.get("candidate_code_executed_downstream",False)
}
out=root/"source_authority_diagnosis.json"
out.write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps(result,indent=2))
