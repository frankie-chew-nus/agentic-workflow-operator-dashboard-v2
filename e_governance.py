"""Production E governance v1: provenance audit only, never auto-commission."""
from workflow_matrix import PROD,commissioning
REQUIRED_STATES={"A":"A_PASS","B":"READY_FOR_C","C":"C_PASS","D":"D_OOS_PASS"}
def audit(chain,human_decisions,required_decisions):
 checks={"four_stage_chain":len(chain)==4,
         "required_decisions":all(x in human_decisions for x in required_decisions)}
 ids={(x.get("candidate_id"),x.get("version")) for x in chain}
 checks["identity_continuity"]=len(ids)==1
 checks["production_only"]=all(x.get("kind")==PROD for x in chain)
 checks["hashes_valid"]=all(x.get("hash_ok") is True for x in chain)
 checks["states_valid"]=all(x.get("state")==REQUIRED_STATES.get(x.get("stage")) for x in chain)
 eligible,reason=commissioning(chain,human=checks["required_decisions"])
 ok=all(checks.values()) and eligible
 return {"state":"E_HUMAN_DECISION_ELIGIBLE" if ok else "E_GOVERNANCE_HOLD",
         "checks":checks,"matrix_reason":reason,"commissioned":False,
         "automatic_commissioning":False,"human_final_decision_required":True}
