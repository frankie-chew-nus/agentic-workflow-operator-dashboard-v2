"""Read-only discovery of existing evidence; no inference of empirical PASS."""
import hashlib,json
from pathlib import Path
from evidence_registry import inspect_registry
from evidence_c_discovery import discover_c,discover_decisions

KNOWN={
 "d_sandbox_demo/dashboard_summary.json":("D","SANDBOX"),
 "e_sandbox_demo/dashboard_summary.json":("E","SANDBOX"),
}
def discover(root):
 root=Path(root).resolve()
 if not root.is_dir():return []
 claims=[]
 for rel,(stage,kind) in KNOWN.items():
  p=root/rel
  if not p.is_file():continue
  raw=p.read_bytes()
  try:data=json.loads(raw)
  except (ValueError,UnicodeDecodeError):data={}
  state=data.get("state") if isinstance(data,dict) else None
  verdict="PASS" if state in ("D_SANDBOX_PASS","E_COMMISSIONING_BLOCKED_TEST_ARTIFACT") else "HOLD"
  claims.append({"claim_id":"DISC-"+stage,"claim":"Recorded "+stage+" workflow sandbox outcome",
   "proof_type":kind,"method":"existing local sandbox output inspection",
   "n":1,"denominator":1,"expected":"sandbox boundary enforced",
   "observed":state or "UNREADABLE","verdict":verdict,"stage":stage,
   "human_decision":None,"candidate_id":data.get("candidate_id") if isinstance(data,dict) else None,
   "version":None,"artifacts":[{"path":rel,"sha256":hashlib.sha256(raw).hexdigest()}]})
 return claims+discover_c(root)+discover_decisions(root)
def report(root):
 claims=discover(root)
 return {"mode":"READ_ONLY_EVIDENCE_DISCOVERY","claims":claims,
         "verification":inspect_registry(claims,root),
         "production_authority":False,"commissioning_authority":False}
if __name__=="__main__":
 import argparse
 p=argparse.ArgumentParser();p.add_argument("--root",default="evidence")
 args=p.parse_args()
 print(json.dumps(report(args.root),indent=2))
