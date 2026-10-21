"""Gate 2 proof table: conservative, read-only claim export."""
import argparse,csv,io,json
from evidence_discovery import report

COLUMNS=("claim_id","stage","claim","proof_type","method","n","denominator","expected","observed","recorded_verdict","artifact_verification","evidence_paths","candidate_id","version","human_decision","limitations")
def proof_rows(root):
 data=report(root)
 checks={x["claim_id"]:x for x in data["verification"]}
 rows=[]
 for c in data["claims"]:
  check=checks[c["claim_id"]]
  classification=c["proof_type"]
  limits=[]
  if classification=="SANDBOX":limits.append("Synthetic workflow proof; not trading performance or production authority")
  if classification=="INCOMPLETE":limits.append("Incomplete proof; no empirical or qualification PASS inferred")
  if not c["artifacts"]:limits.append("No individually hashed artifact attached to this claim")
  if check["verification"]!="VERIFIED_ARTIFACTS":limits.append("Artifact verification not established")
  rows.append({"claim_id":c["claim_id"],"stage":c["stage"],"claim":c["claim"],"proof_type":classification,
   "method":c["method"],"n":c["n"],"denominator":c["denominator"],"expected":c["expected"],
   "observed":c["observed"],"recorded_verdict":c["verdict"],
   "artifact_verification":check["verification"],
   "evidence_paths":"; ".join(a["path"] for a in c["artifacts"]),
   "candidate_id":c.get("candidate_id"),"version":c.get("version"),
   "human_decision":json.dumps(c.get("human_decision"),sort_keys=True),
   "limitations":"; ".join(limits)})
 return rows
def csv_text(root):
 out=io.StringIO();writer=csv.DictWriter(out,fieldnames=COLUMNS);writer.writeheader()
 writer.writerows(proof_rows(root));return out.getvalue()
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--root",default="evidence");a=p.parse_args()
 print(csv_text(a.root),end="")
