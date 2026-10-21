"""T10 experimental policy-change authorization gate.

Requires a separately supplied trusted decision ID and trusted prior-policy digest.
Never trusts the candidate's own claim of Human approval. Does not authenticate
Human identity by itself or grant production authority.
"""
import hashlib,json
def digest(x):
 return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def authorize_change(previous,proposed,decision,*,trusted_decision_ids=None,trusted_previous_digest=None):
 failures=[]
 if not isinstance(previous,dict) or not isinstance(proposed,dict):return ["POLICY_MISSING"]
 if not trusted_previous_digest or digest(previous)!=trusted_previous_digest:
  failures.append("PRIOR_POLICY_UNVERIFIED")
 if not isinstance(decision,dict):return sorted(set(failures+["HUMAN_DECISION_MISSING"]))
 if decision.get("actor_type")!="HUMAN_OPERATOR":failures.append("NON_HUMAN_ACTOR")
 did=decision.get("decision_id")
 if not did or trusted_decision_ids is None or did not in trusted_decision_ids:
  failures.append("DECISION_NOT_IN_TRUSTED_REGISTER")
 if decision.get("previous_policy_sha256")!=digest(previous):
  failures.append("PRIOR_POLICY_HASH_MISMATCH")
 if decision.get("proposed_policy_sha256")!=digest(proposed):
  failures.append("PROPOSED_POLICY_HASH_MISMATCH")
 if decision.get("decision")!="APPROVE_POLICY_CHANGE":
  failures.append("POLICY_CHANGE_NOT_APPROVED")
 if proposed.get("production_authority") is not False:
  failures.append("PRODUCTION_AUTHORITY_FORBIDDEN")
 if proposed.get("max_released_candidates")!=3:
  failures.append("COMMISSION_LIMIT_CHANGE_FORBIDDEN")
 return sorted(set(failures))
