import argparse,ast,hashlib,importlib.util,json,os,py_compile,traceback,urllib.request
from pathlib import Path
MAX_REVISIONS=5
ALLOWED={"math","statistics","typing","dataclasses","collections","functools","itertools","operator","decimal","fractions","numpy","pandas"}
BLOCKED={"requests","urllib","http","socket","subprocess","metatrader5","openai","anthropic","google","tensorflow","torch"}
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
def ask(prompt):
 base=os.getenv("DMR_BASE_URL","").rstrip("/");model=os.getenv("DMR_MODEL","")
 if not base or not model or os.getenv("DMR_CLOUD_FALLBACK","false").lower()!="false":raise RuntimeError("DMR_BOUNDARY_FAILURE")
 body={"model":model,"messages":[{"role":"system","content":"Restricted local implementation agent. Produce inspectable local Python. Frozen strategy semantics and Operator controls are immutable."},{"role":"user","content":prompt}],"temperature":0}
 req=urllib.request.Request(base+"/chat/completions",data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
 with urllib.request.urlopen(req,timeout=240) as r:d=json.load(r)
 s=d["choices"][0]["message"]["content"].strip()
 if s.startswith("```"):
  q=s.splitlines();q=q[1:] if q and q[0].startswith("```") else q;q=q[:-1] if q and q[-1].strip()=="```" else q;s="\n".join(q)
 return s,d
def static(code):
 try:t=ast.parse(code)
 except SyntaxError as e:return ["SYNTAX_ERROR:"+str(e)]
 fs=[];im=[]
 for n in ast.walk(t):
  if isinstance(n,ast.Import):im += [x.name.split(".")[0].lower() for x in n.names]
  elif isinstance(n,ast.ImportFrom):im.append((n.module or "").split(".")[0].lower())
 for x in im:
  if x in BLOCKED:fs.append("OPAQUE_OR_REMOTE_DEPENDENCY:"+x)
  elif x not in ALLOWED:fs.append("DEPENDENCY_REVIEW_REQUIRED:"+x)
 funcs={n.name for n in t.body if isinstance(n,ast.FunctionDef)}
 for f in {"metadata","parameter_schema","prepare","signal"}:
  if f not in funcs:fs.append("MISSING_FUNCTION:"+f)
 names={n.id.lower() for n in ast.walk(t) if isinstance(n,ast.Name)}
 for b in {"position_size","lot_size","cpc","profit_factor","drawdown","friction","starting_equity","risk_percent"}:
  if b in names:fs.append("C_OWNED_CONTROL:"+b)
 return sorted(set(fs))
def functional(path,cid,ver):
 try:
  s=importlib.util.spec_from_file_location("cand",path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);md=m.metadata()
  fs=[]
  if md.get("candidate_id")!=cid or md.get("version")!=ver:fs.append("IDENTITY")
  if md.get("implementation_status") in {"HOLD_SPEC_AMBIGUITY","HOLD_FOR_HUMAN"}:fs.append("MODEL_ESCALATED:"+md["implementation_status"])
  h=[{"open":100,"high":100.3,"low":99.7,"close":100.1,"Open":100,"High":100.3,"Low":99.7,"Close":100.1} for _ in range(40)]
  m.prepare(h)
  p={"atr_period":14,"body_multiplier":1.2,"risk_reward_ratio":2.25} if cid=="CAND-B-001" else ({"lookback_period":7,"breakout_buffer":.125,"trailing_atr_multiplier":2.25} if cid=="CAND-B-002" else {"wick_body_ratio":3.5,"pivot_lookback":1})
  a=m.signal(h,p);b=m.signal(h,p)
  if a!=b:fs.append("NONDETERMINISTIC")
  if a is not None and not isinstance(a,dict):fs.append("SIGNAL_TYPE")
  return fs,[]
 except Exception as e:return ["RUNTIME:"+type(e).__name__+":"+str(e)],[traceback.format_exc()]
def cand(p,cid):
 r=json.load(open(p,encoding="utf-8"))
 return next(x for x in r["candidates"] if x["candidate_id"]==cid)
def main():
 p=argparse.ArgumentParser();p.add_argument("--env",default=".env");p.add_argument("--spec",required=True);p.add_argument("--candidate",required=True);p.add_argument("--workdir",required=True);a=p.parse_args();env(a.env);c=cand(a.spec,a.candidate);wd=Path(a.workdir)/a.candidate;wd.mkdir(parents=True,exist_ok=True)
 save(wd/"operator_dependency_clarification.json",{"decision_id":"BLACK_BOX_CLARIFICATION_V1","timing":"PRE_STAGE1_PERFORMANCE","rule":"Locally inspectable, traceable and reproducible computation is permitted; opaque/remote material strategy computation is prohibited.","allowed_examples":["standard library","numpy","pandas"],"performance_evidence_seen":False})
 hist=[];parent="";feedback="";last=None
 contract="Required top-level functions exactly: metadata(), parameter_schema(), prepare(history), signal(history, params). numpy/pandas/standard-library are allowed. Remote/opaque computation is prohibited."
 for rev in range(1,MAX_REVISIONS+1):
  rd=wd/f"r{rev}";rd.mkdir(exist_ok=True)
  prompt=(f"Generate COMPLETE Python source for frozen candidate:\n{json.dumps(c,indent=2)}\n{contract}\nNo files/network/MT5/cloud. No risk sizing, friction, CPC, drawdown, optimisation ranking or PASS/FAIL. Completed bars only." if rev==1 else f"Repair ONLY these deterministic failures: {feedback}\n{contract}\nFrozen candidate:\n{json.dumps(c,indent=2)}\nPrevious source:\n{parent}\nDo not change semantics, parameters, indicators or Operator controls.")
  code,raw=ask(prompt);mp=rd/"module.py";mp.write_text(code,encoding="utf-8");save(rd/"generation.json",{"revision":rev,"module_sha256":sha(mp),"model":os.getenv("DMR_MODEL"),"system_fingerprint":raw.get("system_fingerprint"),"usage":raw.get("usage",{})})
  try:py_compile.compile(str(mp),doraise=True);cf=[]
  except Exception as e:cf=["COMPILE:"+str(e)]
  save(rd/"compile.json",{"state":"PASS" if not cf else "HOLD","failures":cf});sf=static(code) if not cf else [];save(rd/"static.json",{"state":"PASS" if not sf and not cf else "HOLD","failures":sf,"policy":"inspectability_v1"});ff,tb=functional(mp,c["candidate_id"],c["version"]) if not cf and not sf else ([],[]);save(rd/"functional.json",{"state":"PASS" if not ff and not cf and not sf else "HOLD","failures":ff,"traceback":tb})
  failures=cf+sf+ff;sig=(sha(mp),tuple(sorted(failures)));hist.append({"revision":rev,"module_sha256":sha(mp),"failures":failures})
  if not failures:
   out={"state":"IMPLEMENTATION_READY","candidate_id":c["candidate_id"],"version":c["version"],"revision":rev,"module":str(mp),"module_sha256":sha(mp),"history":hist,"dependency_policy":"inspectability_v1","stage1_performance_seen":False};save(wd/"implementation_release.json",out);print(json.dumps(out,indent=2));return
  if last==sig:
   out={"state":"HOLD_FOR_HUMAN","candidate_id":c["candidate_id"],"version":c["version"],"reason":"NO_REPAIR_PROGRESS","history":hist,"dependency_policy":"inspectability_v1","stage1_performance_seen":False};save(wd/"implementation_hold.json",out);print(json.dumps(out,indent=2));return
  last=sig;feedback=json.dumps(failures);parent=code
 out={"state":"HOLD_FOR_HUMAN","candidate_id":c["candidate_id"],"version":c["version"],"reason":"MAX_BOUNDED_REPAIR_REVISIONS","history":hist,"dependency_policy":"inspectability_v1","stage1_performance_seen":False};save(wd/"implementation_hold.json",out);print(json.dumps(out,indent=2))
if __name__=="__main__":main()
