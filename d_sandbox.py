"""D Sandbox v1: deterministic hidden/OOS workflow test, never production authority."""
import hashlib,json
from pathlib import Path
from operator_handoff import TEST,envelope,validate
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def run(c_handoff,hidden_rows,output_dir):
 out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
 admission=validate(c_handoff,"C",c_handoff.get("candidate_id"),c_handoff.get("version"),allow_test=True)
 checks={"c_handoff_valid":admission["pass"],"test_fixture_only":c_handoff.get("evidence_kind")==TEST,
         "hidden_fixture_present":isinstance(hidden_rows,list) and len(hidden_rows)>0}
 if not all(checks.values()):
  x={"state":"D_SANDBOX_HOLD","checks":checks,"production_authority":False};(out/"d_summary.json").write_text(json.dumps(x,indent=2));return x
 raw=json.dumps(hidden_rows,sort_keys=True,separators=(",",":")).encode();hidden_hash=sha_bytes(raw)
 # Deterministic sandbox score exists only to exercise D evidence plumbing.
 score=sum(int(r.get("outcome",0)) for r in hidden_rows)
 state="D_SANDBOX_PASS" if score>0 else "D_SANDBOX_FAIL"
 summary={"state":state,"evidence_kind":TEST,"hidden_dataset_sha256":hidden_hash,
          "observation_count":len(hidden_rows),"deterministic_score":score,
          "production_authority":False,"advance_to_e_production":False,"checks":checks}
 sp=out/"d_summary.json";sp.write_text(json.dumps(summary,indent=2),encoding="utf-8")
 handoff=envelope("D",c_handoff["candidate_id"],c_handoff["version"],TEST,[("d_summary",sp)],state)
 (out/"d_handoff.json").write_text(json.dumps(handoff,indent=2),encoding="utf-8")
 return summary
