"""Experimental B policy provenance checks; no production release authority.

A matching digest only proves bytes match a trusted external digest. It does not
authenticate Human identity or independently establish a release ledger.
"""
import hashlib,json

def canonical(obj):
 return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")

def verify_bundle(bundle,expected_digest=None):
 if not isinstance(bundle,dict):return ["BUNDLE_MISSING"]
 errors=[]
 if bundle.get("status")!="OPERATOR_REVIEWED":errors.append("APPROVAL_NOT_RECORDED")
 dec=bundle.get("operator_decision")
 if not isinstance(dec,dict) or not all(dec.get(k) for k in ("decision_id","decision_at","reviewer")):
  errors.append("DECISION_PROVENANCE_MISSING")
 for key in ("resource_inventory","dependency_allowlist"):
  v=bundle.get(key)
  if not isinstance(v,list) or not v or any(not isinstance(x,str) or not x.strip() for x in v):
   errors.append(key.upper()+"_UNVERIFIED")
 ledger=bundle.get("release_ledger")
 if not isinstance(ledger,dict) or not ledger.get("commission_id") or not isinstance(ledger.get("released_candidate_ids"),list):
  errors.append("RELEASE_LEDGER_UNVERIFIED")
 elif len(set(ledger["released_candidate_ids"]))!=len(ledger["released_candidate_ids"]):
  errors.append("RELEASE_LEDGER_DUPLICATES")
 if bundle.get("rule_change_authority")!="HUMAN_ONLY":errors.append("RULE_CHANGE_AUTHORITY_UNVERIFIED")
 if bundle.get("production_authority") is not False:errors.append("PRODUCTION_AUTHORITY_FORBIDDEN")
 if not isinstance(expected_digest,str) or len(expected_digest)!=64:
  errors.append("TRUSTED_DIGEST_MISSING")
 elif hashlib.sha256(canonical(bundle)).hexdigest()!=expected_digest:
  errors.append("BUNDLE_HASH_MISMATCH")
 return sorted(set(errors))
