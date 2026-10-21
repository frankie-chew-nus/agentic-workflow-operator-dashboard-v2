"""Disposable-only HMAC authority verifier. Never production authorization."""
import hashlib,hmac,json,time
FIELDS=("candidate_id","research_id","decision","expires_at","nonce")
def canonical(payload):
    return json.dumps({k:payload[k] for k in FIELDS},sort_keys=True,separators=(",",":")).encode()
def sign(payload,key):
    return hmac.new(key,canonical(payload),hashlib.sha256).hexdigest()
def verify(candidate_id,research_id,context,*,key,now=None):
    if not isinstance(context,dict) or not isinstance(key,bytes) or len(key)<32:return False
    try:
        p=context["approval"]
        if not isinstance(p,dict) or any(k not in p for k in FIELDS):return False
        if p["candidate_id"]!=candidate_id or p["research_id"]!=research_id:return False
        if p["decision"]!="RELEASE_TO_C" or not isinstance(p["nonce"],str) or len(p["nonce"])<16:return False
        if type(p["expires_at"]) is not int or p["expires_at"] <= (time.time() if now is None else now):return False
        mac=context["signature"]
        if not isinstance(mac,str) or len(mac)!=64:return False
        return hmac.compare_digest(sign(p,key),mac)
    except (KeyError,TypeError,ValueError):return False
