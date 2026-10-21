"""D production governance contract v1. Admission/evidence only; no trading logic."""
import json,uuid
from pathlib import Path
from operator_handoff import validate
ALLOWED_C={"C_PASS"}
def admit(c_handoff,candidate_id,version):
 v=validate(c_handoff,"C",candidate_id,version,allow_test=False)
 checks=dict(v["checks"]);checks["c_state_authorized"]=c_handoff.get("state") in ALLOWED_C
 ok=all(checks.values())
 return {"state":"D_ADMISSION_PASS" if ok else "D_ADMISSION_HOLD","checks":checks,"production_authority":ok}
def open_run(c_handoff,candidate_id,version,hidden_manifest):
 a=admit(c_handoff,candidate_id,version);p=Path(hidden_manifest)
 checks={"admission":a["production_authority"],"hidden_manifest_exists":p.is_file()}
 if p.is_file():
  m=json.loads(p.read_text(encoding="utf-8"))
  checks["hidden_boundary_declared"]=bool(m.get("dataset_sha256")) and bool(m.get("boundary_id"))
 state="D_READY_FOR_OOS" if all(checks.values()) else "D_GOVERNANCE_HOLD"
 return {"state":state,"run_id":"D-"+uuid.uuid4().hex[:12].upper(),"candidate_id":candidate_id,
         "version":version,"checks":checks,"c_admission":a,"human_review_required":True}
def finalize(run,evidence_path,out_path):
 p=Path(evidence_path);checks={"run_ready":run.get("state")=="D_READY_FOR_OOS","evidence_exists":p.is_file()}
 ev=json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}
 checks["identity"]=ev.get("candidate_id")==run.get("candidate_id") and ev.get("version")==run.get("version")
 checks["oos_state_declared"]=ev.get("state") in ("D_OOS_PASS","D_OOS_FAIL")
 state=ev.get("state") if all(checks.values()) else "D_GOVERNANCE_HOLD"
 summary={"state":state,"candidate_id":run.get("candidate_id"),"version":run.get("version"),
          "checks":checks,"human_review_required":True,"advance_to_e":False}
 Path(out_path).write_text(json.dumps(summary,indent=2),encoding="utf-8");return summary
