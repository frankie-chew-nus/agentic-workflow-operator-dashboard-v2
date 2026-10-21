"""Explicit A-E workflow governance matrix for contract testing."""
PROD="PRODUCTION_EVIDENCE";TEST="WORKFLOW_TEST_FIXTURE"
def allowed(src,dst,state,kind,human=True,identity=True,hash_ok=True,interrupted=False):
 if interrupted:return False,"INTERRUPTED_HOLD"
 if not identity:return False,"IDENTITY_HOLD"
 if not hash_ok:return False,"HASH_HOLD"
 if not human:return False,"HUMAN_AUTHORITY_HOLD"
 rules={("A","B"):(("A_PASS",),PROD),("B","C"):(("READY_FOR_C",),PROD),
        ("C","D"):(("C_PASS",),PROD),("D","E"):(("D_OOS_PASS",),PROD)}
 key=(src,dst)
 if key not in rules:return False,"UNAUTHORIZED_TRANSITION"
 states,required=rules[key]
 if kind!=required:return False,"EVIDENCE_KIND_HOLD"
 if state not in states:return False,"STATE_HOLD"
 return True,"AUTHORIZED"
def commissioning(chain,human=True):
 if tuple(x.get("stage") for x in chain)!=("A","B","C","D"):return False,"PROVENANCE_CHAIN_HOLD"
 if any(x.get("kind")!=PROD for x in chain):return False,"TEST_EVIDENCE_BLOCK"
 if any(not x.get("hash_ok",False) for x in chain):return False,"HASH_HOLD"
 if any(not x.get("identity",False) for x in chain):return False,"IDENTITY_HOLD"
 if [x.get("state") for x in chain]!=["A_PASS","READY_FOR_C","C_PASS","D_OOS_PASS"]:return False,"STATE_HOLD"
 if not human:return False,"HUMAN_COMMISSIONING_REQUIRED"
 return True,"E_HUMAN_DECISION_ELIGIBLE"
