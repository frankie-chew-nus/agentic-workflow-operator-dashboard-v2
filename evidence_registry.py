"""Read-only claim registry. No workflow mutation or authority creation."""
import hashlib,json
from pathlib import Path
TYPES={"IN_VITRO","IN_VIVO","SANDBOX","INCOMPLETE"}
VERDICTS={"PASS","FAIL","HOLD","INCOMPLETE"}
def inspect_claim(claim,root):
 required=("claim_id","claim","proof_type","method","n","denominator","expected","observed","verdict","artifacts","stage","human_decision")
 missing=[k for k in required if k not in claim]
 if missing:return {"claim_id":claim.get("claim_id"),"verification":"INCOMPLETE","missing_fields":missing}
 if claim["proof_type"] not in TYPES or claim["verdict"] not in VERDICTS:raise ValueError("invalid classification")
 checks=[]
 for a in claim["artifacts"]:
  p=(Path(root)/a["path"]).resolve()
  inside=p.is_relative_to(Path(root).resolve())
  exists=inside and p.is_file()
  actual=hashlib.sha256(p.read_bytes()).hexdigest() if exists else None
  checks.append({"path":a["path"],"exists":exists,"hash_match":bool(exists and actual==a.get("sha256"))})
 verified=bool(checks) and all(c["hash_match"] for c in checks)
 return {"claim_id":claim["claim_id"],"verification":"VERIFIED_ARTIFACTS" if verified else "UNVERIFIED_ARTIFACTS",
         "proof_type":claim["proof_type"],"recorded_verdict":claim["verdict"],
         "production_authority":False,"checks":checks}
def inspect_registry(records,root):
 ids=[x.get("claim_id") for x in records]
 if len(ids)!=len(set(ids)):raise ValueError("duplicate claim IDs")
 return [inspect_claim(x,root) for x in records]
