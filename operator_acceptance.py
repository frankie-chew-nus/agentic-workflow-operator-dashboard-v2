"""Tiny deterministic A-E Operator acceptance model."""
from workflow_matrix import PROD,allowed
from e_governance import audit
def chain():
 return [{"stage":"A","state":"A_PASS","kind":PROD,"hash_ok":True,"identity":True,"candidate_id":"ACC-001","version":"v1"},
 {"stage":"B","state":"READY_FOR_C","kind":PROD,"hash_ok":True,"identity":True,"candidate_id":"ACC-001","version":"v1"},
 {"stage":"C","state":"C_PASS","kind":PROD,"hash_ok":True,"identity":True,"candidate_id":"ACC-001","version":"v1"},
 {"stage":"D","state":"D_OOS_PASS","kind":PROD,"hash_ok":True,"identity":True,"candidate_id":"ACC-001","version":"v1"}]
def run():
 c=chain();transitions=[]
 for src,dst,item in [("A","B",c[0]),("B","C",c[1]),("C","D",c[2]),("D","E",c[3])]:
  ok,reason=allowed(src,dst,item["state"],item["kind"],identity=item["identity"],hash_ok=item["hash_ok"])
  transitions.append({"from":src,"to":dst,"pass":ok,"reason":reason})
 e=audit(c,["A_REVIEW","B_RELEASE","C_REVIEW","D_REVIEW"],["A_REVIEW","B_RELEASE","C_REVIEW","D_REVIEW"])
 return {"state":"OPERATOR_ACCEPTANCE_PASS" if all(x["pass"] for x in transitions) and e["state"]=="E_HUMAN_DECISION_ELIGIBLE" and not e["commissioned"] else "OPERATOR_ACCEPTANCE_FAIL","transitions":transitions,"e":e}
if __name__=="__main__":
 import json;print(json.dumps(run(),indent=2))
