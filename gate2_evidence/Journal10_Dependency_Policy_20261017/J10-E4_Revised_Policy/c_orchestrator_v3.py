import argparse,ast,hashlib,importlib.util,json,os,py_compile,traceback,urllib.request
from pathlib import Path
ALLOW={"math","statistics","typing","dataclasses","collections","functools","itertools","operator","decimal","fractions","numpy","pandas"}; BLOCK={"requests","urllib","http","socket","subprocess","metatrader5","openai","anthropic","google","tensorflow","torch"}; MAX=5
def env(p=".env"):
 if Path(p).exists():
  for s in Path(p).read_text(encoding="utf-8").splitlines():
   if "=" in s and not s.lstrip().startswith("#"):
    k,v=s.split("=",1);os.environ.setdefault(k.strip(),v.strip())
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def save(p,o):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(o,indent=2),encoding="utf-8")
def ask(x):
 base=os.getenv("DMR_BASE_URL","").rstrip("/");model=os.getenv("DMR_MODEL","")
 if not base or not model or os.getenv("DMR_CLOUD_FALLBACK","false").lower()!="false":raise RuntimeError("DMR_BOUNDARY_FAILURE")
 b={"model":model,"messages":[{"role":"system","content":"Restricted local implementation agent. Implement frozen strategy against machine contract exactly."},{"role":"user","content":x}],"temperature":0};q=urllib.request.Request(base+"/chat/completions",data=json.dumps(b).encode(),headers={"Content-Type":"application/json"})
 with urllib.request.urlopen(q,timeout=240) as z:d=json.load(z)
 s=d["choices"][0]["message"]["content"].strip()
 if s.startswith("```"):
  a=s.splitlines();a=a[1:] if a and a[0].startswith("```") else a;a=a[:-1] if a and a[-1].strip()=="```" else a;s="\n".join(a)
 return s,d
def static(code):
 try:t=ast.parse(code)
 except SyntaxError as e:return ["SYNTAX:"+str(e)]
 f=[];im=[]
 for n in ast.walk(t):
  if isinstance(n,ast.Import):im += [x.name.split(".")[0].lower() for x in n.names]
  elif isinstance(n,ast.ImportFrom):im.append((n.module or "").split(".")[0].lower())
 for x in im:
  if x in BLOCK:f.append("OPAQUE_REMOTE:"+x)
  elif x not in ALLOW:f.append("DEPENDENCY_REVIEW:"+x)
 funcs={n.name:n for n in t.body if isinstance(n,ast.FunctionDef)}
 for x in ["metadata","parameter_schema","prepare","signal"]:
  if x not in funcs:f.append("MISSING:"+x)
 if "signal" in funcs and len(funcs["signal"].args.args)!=3:f.append("SIGNAL_SIGNATURE")
 return sorted(set(f))
def functional(path,c,ct):
 try:
  s=importlib.util.spec_from_file_location("m",path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);f=[];md=m.metadata()
  if md.get("candidate_id")!=c["candidate_id"] or md.get("version")!=c["version"]:f.append("IDENTITY")
  if md.get("contract_version")!=ct["contract_version"]:f.append("CONTRACT_VERSION")
  if md.get("implementation_status")!="READY":f.append("MODEL_STATUS:"+str(md.get("implementation_status")))
  if set(m.parameter_schema())!=set(c.get("parameter_ranges",{})):f.append("PARAMETER_SCHEMA")
  short=[{"open":100.0,"high":100.3,"low":99.7,"close":100.1} for _ in range(5)];p0=m.prepare(short)
  if not isinstance(p0,dict):f.append("PREPARE_TYPE")
  par={k:(v[0] if isinstance(v,list) else v) for k,v in c.get("parameter_ranges",{}).items()}
  if m.signal(short,p0,par) is not None:f.append("WARMUP_SIGNAL")
  h=[{"open":100.0,"high":100.3,"low":99.7,"close":100.1} for _ in range(60)];before=json.dumps(h);prep=m.prepare(h);a=m.signal(h,prep,par);b=m.signal(h,prep,par)
  if json.dumps(h)!=before:f.append("HISTORY_MUTATED")
  if a!=b:f.append("NONDETERMINISTIC")
  if a is not None and (not isinstance(a,dict) or a.get("side") not in {"LONG","SHORT"} or not isinstance(a.get("entry"),dict)):f.append("SIGNAL_SCHEMA")
  return f,[]
 except Exception as e:return ["RUNTIME:"+type(e).__name__+":"+str(e)],[traceback.format_exc()]
def main():
 a=argparse.ArgumentParser();a.add_argument("--env",default=".env");a.add_argument("--spec",required=True);a.add_argument("--contract",required=True);a.add_argument("--candidate",required=True);a.add_argument("--workdir",required=True);x=a.parse_args();env(x.env);rr=json.load(open(x.spec,encoding="utf-8"));c=next(q for q in rr["candidates"] if q["candidate_id"]==x.candidate);ct=json.load(open(x.contract));wd=Path(x.workdir)/x.candidate;wd.mkdir(parents=True,exist_ok=True);save(wd/"contract_lock.json",{"contract_version":ct["contract_version"],"contract_sha256":sha(x.contract),"performance_evidence_seen":False})
 hist=[];parent="";feedback="";last=None
 for rev in range(1,MAX+1):
  rd=wd/f"r{rev}";rd.mkdir(exist_ok=True);base="FROZEN CANDIDATE:\n"+json.dumps(c,indent=2)+"\nCONTRACT:\n"+json.dumps(ct,indent=2)+"\nOutput complete Python only. Implement all required functions. No files/network/MT5/cloud or harness-owned controls."
  prompt=base if rev==1 else "Repair ONLY these deterministic contract failures: "+feedback+"\n"+base+"\nPREVIOUS SOURCE:\n"+parent
  code,raw=ask(prompt);mp=rd/"module.py";mp.write_text(code,encoding="utf-8");save(rd/"generation.json",{"revision":rev,"module_sha256":sha(mp),"model":os.getenv("DMR_MODEL"),"system_fingerprint":raw.get("system_fingerprint"),"usage":raw.get("usage",{})})
  try:py_compile.compile(str(mp),doraise=True);cf=[]
  except Exception as e:cf=["COMPILE:"+str(e)]
  sf=static(code) if not cf else [];ff,tb=functional(mp,c,ct) if not cf and not sf else ([],[])
  save(rd/"compile.json",{"state":"PASS" if not cf else "HOLD","failures":cf});save(rd/"static.json",{"state":"PASS" if not sf and not cf else "HOLD","failures":sf});save(rd/"functional.json",{"state":"PASS" if not ff and not cf and not sf else "HOLD","failures":ff,"traceback":tb})
  fail=cf+sf+ff;sig=(sha(mp),tuple(sorted(fail)));hist.append({"revision":rev,"module_sha256":sha(mp),"failures":fail})
  if not fail:
   o={"state":"IMPLEMENTATION_READY","candidate_id":c["candidate_id"],"version":c["version"],"contract_version":ct["contract_version"],"module":str(mp),"module_sha256":sha(mp),"history":hist,"stage1_performance_seen":False};save(wd/"implementation_release.json",o);print(json.dumps(o,indent=2));return
  if sig==last:
   o={"state":"HOLD_FOR_HUMAN","reason":"NO_REPAIR_PROGRESS","candidate_id":c["candidate_id"],"history":hist,"stage1_performance_seen":False};save(wd/"implementation_hold.json",o);print(json.dumps(o,indent=2));return
  last=sig;feedback=json.dumps(fail);parent=code
 o={"state":"HOLD_FOR_HUMAN","reason":"MAX_BOUNDED_REPAIR_REVISIONS","candidate_id":c["candidate_id"],"history":hist,"stage1_performance_seen":False};save(wd/"implementation_hold.json",o);print(json.dumps(o,indent=2))
if __name__=="__main__":main()
