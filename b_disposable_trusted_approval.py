"""Disposable-only version-bound approval verifier.

Trusted key registry is supplied out-of-band by test host, never from request.
This proves possession of a configured signing key, not real-world Human identity.
"""
import hashlib,hmac,json,time
FIELDS=("candidate_id","candidate_version","research_id","decision","expires_at","nonce","signer_id")
def canonical(approval):
 return json.dumps({k:approval[k] for k in FIELDS},sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()
def sign(approval,key):
 return hmac.new(key,canonical(approval),hashlib.sha256).hexdigest()
def verify(candidate_id,candidate_version,research_id,context,*,trusted_keys,revoked=None,now=None):
 if not isinstance(context,dict) or not isinstance(trusted_keys,dict):return False
 try:
  a=context["approval"];signature=context["signature"]
  if not isinstance(a,dict) or not isinstance(signature,str) or len(signature)!=64:return False
  if any(k not in a for k in FIELDS):return False
  if a["candidate_id"]!=candidate_id or a["candidate_version"]!=candidate_version or a["research_id"]!=research_id:return False
  if a["decision"]!="RELEASE_TO_C" or type(a["expires_at"]) is not int:return False
  if a["expires_at"]<= (time.time() if now is None else now):return False
  if not isinstance(a["nonce"],str) or len(a["nonce"])<16:return False
  signer=a["signer_id"]
  if not isinstance(signer,str) or signer in (revoked or set()):return False
  key=trusted_keys.get(signer)
  if not isinstance(key,bytes) or len(key)<32:return False
  return hmac.compare_digest(sign(a,key),signature)
 except (KeyError,TypeError,ValueError):return False
