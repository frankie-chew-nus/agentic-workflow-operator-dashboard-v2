"""Prepare a sanitized, read-only Gate 2 evidence archive for HUMAN review.

Writes only to --output, never to the source evidence directory.
No raw database, logs, strategy code, credentials, or market data are copied.
"""
import argparse,csv,hashlib,io,json,subprocess,unittest
from pathlib import Path
from gate2_proof_table import COLUMNS,proof_rows
from gate2_decision_digest import digest
from gate2_test_log_sanitize import sanitize
from gate2_approved_judgement import approved_judgements

FOLDERS=("01_governance_decisions","02_c_execution","03_d_e_sandbox",
         "04_automated_tests","05_proof_registry","06_operator_judgement")
def sha(b):return hashlib.sha256(b).hexdigest()
def build(root,output,test_run=None):
 root=Path(root).resolve();out=Path(output).resolve()
 if out==root or root in out.parents:raise ValueError("Output must be outside source evidence")
 if out.exists() and any(out.iterdir()):raise ValueError("Output directory must be empty")
 out.mkdir(parents=True,exist_ok=True)
 for folder in FOLDERS:(out/folder).mkdir()
 rows=proof_rows(root)
 for row in rows:
  if row["claim_id"].startswith("DISC-HUMAN-"):
   row["human_decision"]="REDACTED: inspect local decision ledger"
 # Keep decisions to action/time metadata only; rationales can contain sensitive details.
 decisions=[{"claim_id":x["claim_id"],"candidate_id":x["candidate_id"],
             "action":x["observed"],"artifact_verification":x["artifact_verification"]}
            for x in rows if x["claim_id"].startswith("DISC-HUMAN-")]
 decisions_digest=digest(root)
 snapshots={
  "01_governance_decisions/decision_digest.json":decisions_digest,
  "01_governance_decisions/decision_index.json":decisions,
  "02_c_execution/c_claims.json":[x for x in rows if x["stage"]=="C" and not x["claim_id"].startswith("DISC-HUMAN-")],
  "03_d_e_sandbox/sandbox_claims.json":[x for x in rows if x["proof_type"]=="SANDBOX"],
  "05_proof_registry/proof_claims.json":rows,
 }
 if test_run is not None:
  tr=Path(test_run).resolve()
  if not tr.is_file():raise FileNotFoundError("Test capture missing")
  captured=json.loads(tr.read_text(encoding="utf-8"))
  if captured.get("schema")!="gate2-test-run-v1" or captured.get("result")!="PASS":raise ValueError("A passing test capture is required")
  log=captured.get("log","")
  if sha(log.encode("utf-8"))!=captured.get("log_sha256"):raise ValueError("Test log hash mismatch")
  safe_log=sanitize(log)
  if not safe_log or "Ran " not in safe_log:raise ValueError("Sanitized test log has no unittest summary")
  snapshots["04_automated_tests/test_run_summary.json"]={k:v for k,v in captured.items() if k!="log"}
  snapshots["04_automated_tests/sanitized_test_log.json"]={"sanitized_log":safe_log,"sha256":sha(safe_log.encode("utf-8")),"original_log_sha256":captured["log_sha256"]}
 snapshots["06_operator_judgement/approved_judgement.json"]=approved_judgements()
 manifest=[]
 for rel,obj in snapshots.items():
  b=(json.dumps(obj,indent=2,ensure_ascii=True)+"\n").encode("utf-8")
  (out/rel).write_bytes(b);manifest.append({"path":rel,"sha256":sha(b),"bytes":len(b)})
 buffer=io.StringIO();writer=csv.DictWriter(buffer,fieldnames=COLUMNS);writer.writeheader();writer.writerows(rows)
 csvdata=buffer.getvalue().encode("utf-8");rel="05_proof_registry/gate2_proof.csv"
 (out/rel).write_bytes(csvdata);manifest.append({"path":rel,"sha256":sha(csvdata),"bytes":len(csvdata)})
 note=("GATE 2 EVIDENCE ARCHIVE — REVIEW REQUIRED\n"
       "This is a sanitized index, NOT a copy of raw source evidence.\n"
       "Source artifacts must be retained locally for independent verification.\n"
       "Do not commit strategy modules, raw market data, SQLite databases, secrets or raw logs.\n"
       "INCOMPLETE and SANDBOX claims are not empirical production PASS.\n"
       "Test-run output and operator judgement must be supplied and reviewed separately.\n")
 rel="README.txt";b=note.encode("utf-8");(out/rel).write_bytes(b)
 manifest.append({"path":rel,"sha256":sha(b),"bytes":len(b)})
 m={"archive_version":"v3","source_root":"LOCAL_EVIDENCE_NOT_COPIED",
    "claims":len(rows),"human_decision_index_entries":len(decisions),
    "files":manifest,"production_authority":False,"commissioning_authority":False}
 (out/"manifest.json").write_text(json.dumps(m,indent=2)+"\n",encoding="utf-8")
 return m
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--root",default="evidence")
 p.add_argument("--output",required=True);p.add_argument("--test-run");a=p.parse_args()
 print(json.dumps(build(a.root,a.output,a.test_run),indent=2))
