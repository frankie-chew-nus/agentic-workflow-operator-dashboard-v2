"""Tiny deterministic D OOS executor. Consumes a predeclared hidden fixture only."""
import hashlib,json
from pathlib import Path
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def execute(run,hidden_path,output_path):
 p=Path(hidden_path);raw=p.read_bytes();rows=json.loads(raw)
 checks={"run_ready":run.get("state")=="D_READY_FOR_OOS","hidden_is_list":isinstance(rows,list) and bool(rows)}
 if not all(checks.values()):
  out={"state":"D_OOS_HOLD","checks":checks};Path(output_path).write_text(json.dumps(out,indent=2));return out
 # Fixture contract: outcome is predetermined synthetic OOS evidence, never strategy logic.
 score=sum(int(x["outcome"]) for x in rows);state="D_OOS_PASS" if score>0 else "D_OOS_FAIL"
 out={"state":state,"candidate_id":run["candidate_id"],"version":run["version"],"run_id":run["run_id"],
      "hidden_dataset_sha256":sha_bytes(raw),"observation_count":len(rows),"score":score,
      "hidden_rows_emitted":False,"production_decision_authority":False}
 Path(output_path).write_text(json.dumps(out,indent=2),encoding="utf-8");return out
