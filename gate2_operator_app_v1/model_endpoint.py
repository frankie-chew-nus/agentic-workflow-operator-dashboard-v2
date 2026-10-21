from pathlib import Path
from urllib.parse import urlparse
import json,urllib.request,urllib.parse

def load_env(path):
    p=Path(path)
    if not p.exists(): raise RuntimeError("model endpoint config file not found: "+str(p))
    vals={}
    for raw in p.read_text(encoding="utf-8-sig").splitlines():
        s=raw.strip()
        if not s or s.startswith("#") or "=" not in s: continue
        k,v=s.split("=",1);k=k.strip();v=v.strip()
        if len(v)>=2 and v[0]==v[-1] and v[0] in ("'",'"'):v=v[1:-1]
        vals[k]=v
    return vals

def endpoint_config(path):
    e=load_env(path)
    # Backward-compatible aliases. Existing .env does NOT need to change.
    base=e.get("MODEL_BASE_URL") or e.get("DMR_BASE_URL")
    model=e.get("MODEL_NAME") or e.get("DMR_MODEL")
    key=e.get("MODEL_API_KEY") or e.get("DMR_API_KEY")
    protocol=(e.get("MODEL_PROTOCOL") or "auto").lower()
    missing=[n for n,v in [("base_url",base),("model",model),("api_key",key)] if not v]
    if missing: raise RuntimeError("missing model endpoint settings: "+",".join(missing))
    return {"base_url":base.rstrip("/"),"model":model,"api_key":key,"protocol":protocol}

def safe_endpoint(url):
    u=urlparse(url);return (u.scheme+"://"+u.netloc) if u.scheme and u.netloc else "configured-endpoint"

def _request(url,key,payload,timeout,auth="bearer"):
    data=json.dumps(payload).encode("utf-8")
    headers={"Content-Type":"application/json"}
    if auth=="bearer": headers["Authorization"]="Bearer "+key
    req=urllib.request.Request(url,data=data,method="POST",headers=headers)
    with urllib.request.urlopen(req,timeout=timeout) as r:return json.loads(r.read().decode("utf-8"))

def chat(cfg,messages,temperature=0,timeout=120):
    base,model,key=cfg["base_url"],cfg["model"],cfg["api_key"]
    # Adapter auto-detects protocol from endpoint shape, not provider identity.
    if cfg["protocol"] in ("openai","openai_compatible") or "/v1" in base:
        payload={"model":model,"messages":messages,"temperature":temperature}
        r=_request(base+"/chat/completions",key,payload,timeout)
        return r["choices"][0]["message"]["content"],"openai_compatible"
    # Google Generative Language REST shape; this is a protocol adapter, not a provider policy.
    if "generativelanguage.googleapis.com" in base:
        url=base+"/models/"+model+":generateContent?key="+urllib.parse.quote(key,safe="")
        text="\n\n".join(m["content"] for m in messages)
        r=_request(url,"",{"contents":[{"parts":[{"text":text}]}],"generationConfig":{"temperature":temperature}},timeout,auth="none")
        return r["candidates"][0]["content"]["parts"][0]["text"],"google_generate_content"
    raise RuntimeError("configured endpoint protocol is not supported by this adapter; no fallback attempted")
