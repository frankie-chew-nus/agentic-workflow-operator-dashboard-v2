import argparse,ast,hashlib,importlib.util,json,os,py_compile,traceback,urllib.request,datetime
from pathlib import Path
MAX_REVISIONS=5
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
def save(p,o):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(o,indent=2,ensure_ascii=False),encoding="utf-8")
def dmr(prompt):
 base=os.getenv("DMR_BASE_URL","").rstrip("/");model=os.getenv("DMR_MODEL","")
 if not base or not model or os.getenv("DMR_CLOUD_FALLBACK","false").lower()!="false":raise RuntimeError("DMR_BOUNDARY_FAILURE")
 body={"model":model,"messages":[{"role":"system","content":"You are a restricted local implementation agent. Frozen strategy semantics and Operator-owned controls are immutable. Repair implementation defects only."},{"role":"user","content":prompt}],"temperature":0}
 req=urllib.request.Request(base+"/chat/completions",data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
 with urllib.request.urlopen(req,timeout=240) as r:d=json.load(r)
 s=d["choices"][0]["message"]["content"].strip()
 if s.startswith("```"):
  a=s.splitlines();a=a[1:] if a and a[0].startswith("```") else a;a=a[:-1] if a and a[-1].strip()=="```" else a;s="\n".join(a)
 return s,d
def static(code):
 fs=[]
 try:t=ast.parse(code)
 except SyntaxError as e:return ["SYNTAX_ERROR:"+str(e)]
 allowed={"math"};imports=[]
 for n in ast.walk(t):
  if isinstance(n,ast.Import):imports += [x.name.split(".")[0] for x in n.names]
  elif isinstance(n,ast.ImportFrom):imports.append((n.module or "").split(".")[0])
 for x in imports:
  if x not in allowed:fs.append("FORBIDDEN_IMPORT:"+x)
 names={n.id.lower() for n in ast.walk(t) if isinstance(n,ast.Name)}
 for b in {"position_size","lot_size","cpc","profit_factor","drawdown","friction","starting_equity","risk_percent"}:
  if b in names:fs.append("C_OWNED_CONTROL:"+b)
 funcs={n.name for n in t.body if isinstance(n,ast.FunctionDef)}
 for f in {"metadata","parameter_schema","prepare","signal"}:
  if f not in funcs:fs.append("MISSING_FUNCTION:"+f)
 low=code.lower()
 for x in ["requests","urllib","socket","subprocess","metatrader5","openai","anthropic","google.","eval(","exec(","__import__","open("]:
  if x in low:fs.append("FORBIDDEN_TOKEN:"+x)
 return sorted(set(fs))
def functional(path,cid,ver):
 fs=[];details=[]
 try:
  s=importlib.util.spec_from_file_location("cand",path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
  md=m.metadata()
  if md.get("candidate_id")!=cid or md.get("version")!=ver:fs.append("IDENTITY")
  hist=[{"open":100,"high":100.3,"low":99.7,"close":100.1,"Open":100,"High":100.3,"Low":99.7,"Close":100.1} for _ in range(40)]
  m.prepare(hist)
  ps=m.parameter_schema(); keys=set(ps)
  if cid=="CAND-B-001":p={"atr_period":14,"body_multiplier":1.2,"risk_reward_ratio":2.25}
  elif cid=="CAND-B-002":p={"lookback_period":7,"breakout_buffer":0.125,"trailing_atr_multiplier":2.25}
  else:p={"wick_body_ratio":3.5,"pivot_lookback":1}
  a=m.signal(hist,p);b=m.signal(hist,p)
  if a!=b:fs.append("NONDETERMINISTIC")
  if a is not None and not isinstance(a,dict):fs.append("SIGNAL_TYPE")
 except Exception as e:fs.append("RUNTIME:"+type(e).__name__+":"+str(e));details.append(traceback.format_exc())
 return fs,details
def candidate(spec,cid):
 r=json.load(open(spec,encoding="utf-8"))
 for c in r["candidates"]:
  if c["candidate_id"]==cid:return c
 raise RuntimeError("CANDIDATE_NOT_FOUND")
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--env",default=".env");ap.add_argument("--spec",required=True);ap.add_argument("--candidate",required=True);ap.add_argument("--workdir",required=True);a=ap.parse_args();env(a.env)
 c=candidate(a.spec,a.candidate);wd=Path(a.workdir)/a.candidate;wd.mkdir(parents=True,exist_ok=True);history=[];parent=None;feedback=""
 for rev in range(1,MAX_REVISIONS+1):
  rd=wd/f"r{rev}";rd.mkdir(exist_ok=True)
  if rev==1:
   task=f"""Generate complete Python source for this frozen candidate only:\n{json.dumps(c,indent=2)}\nContract: metadata(), parameter_schema(), prepare(history), signal(history,params). OHLC only. No files/network/MT5/cloud. No risk sizing, friction, CPC, drawdown, optimisation ranking or PASS/FAIL. Completed bars only. If specification requires semantic guessing, metadata must set implementation_status HOLD_SPEC_AMBIGUITY and signal returns None."""
  else:
   task=f"""Repair the previous implementation for ONLY these deterministic implementation failures:\n{feedback}\nFrozen candidate remains:\n{json.dumps(c,indent=2)}\nPrevious source:\n{parent}\nDo not change strategy semantics, identity, parameter ranges, indicators or Operator-owned controls. If repair requires a semantic change, return source whose metadata implementation_status is HOLD_FOR_HUMAN and signal returns None."""
  code,raw=dmr(task);mp=rd/"module.py";mp.write_text(code,encoding="utf-8")
  gen={"revision":rev,"module_sha256":sha(mp),"model":os.getenv("DMR_MODEL"),"system_fingerprint":raw.get("system_fingerprint"),"usage":raw.get("usage",{})};save(rd/"generation.json",gen)
  try:py_compile.compile(str(mp),doraise=True);comp=[]
  except Exception as e:comp=["COMPILE:"+str(e)]
  save(rd/"compile.json",{"state":"PASS" if not comp else "HOLD","failures":comp})
  sf=static(code) if not comp else [];save(rd/"static.json",{"state":"PASS" if not sf and not comp else "HOLD","failures":sf})
  ff,trace=functional(mp,c["candidate_id"],c["version"]) if not comp and not sf else ([],[])
  save(rd/"functional.json",{"state":"PASS" if not ff and not comp and not sf else "HOLD","failures":ff,"traceback":trace})
  failures=comp+sf+ff
  history.append({"revision":rev,"module_sha256":sha(mp),"failures":failures})
  if not failures:
   release={"state":"IMPLEMENTATION_READY","candidate_id":c["candidate_id"],"version":c["version"],"revision":rev,"module":str(mp),"module_sha256":sha(mp),"history":history,"stage1_performance_seen":False};save(wd/"implementation_release.json",release);print(json.dumps(release,indent=2));return
  feedback=json.dumps(failures);parent=code
 hold={"state":"HOLD_FOR_HUMAN","candidate_id":c["candidate_id"],"version":c["version"],"reason":"MAX_BOUNDED_REPAIR_REVISIONS","history":history,"stage1_performance_seen":False};save(wd/"implementation_hold.json",hold);print(json.dumps(hold,indent=2))
if __name__=="__main__":main()
