import argparse,json,os,hashlib,urllib.request,py_compile,re,time
from pathlib import Path
import c_controller as core
MAX_REPAIRS=4
def strip_source(s):
 s=s.strip()
 # JSON structured response preferred
 try:
  o=json.loads(s)
  if isinstance(o,dict) and isinstance(o.get("python_source"),str):return o["python_source"].strip()
 except:pass
 # fenced source fallback
 m=re.search(r"```(?:python)?\\s*(.*?)```",s,re.S|re.I)
 if m:return m.group(1).strip()
 return s
def usage(d):
 u=d.get("usage") or {}
 return {"prompt_tokens":u.get("prompt_tokens",u.get("promptTokenCount",0)) or 0,
         "completion_tokens":u.get("completion_tokens",u.get("candidatesTokenCount",0)) or 0,
         "total_tokens":u.get("total_tokens",u.get("totalTokenCount",0)) or 0}
def record(ledger,agent,model,purpose,payload_class,d):
 x=usage(d);ledger.append({"agent":agent,"model":model,"purpose":purpose,"payload_class":payload_class,**x})
def summary(ledger,released,withheld,repairs):
 by={}
 for x in ledger:
  z=by.setdefault(x["agent"],{"calls":0,"prompt_tokens":0,"completion_tokens":0,"total_tokens":0})
  z["calls"]+=1
  for k in ["prompt_tokens","completion_tokens","total_tokens"]:z[k]+=x[k]
 return {"agents":by,"total_calls":len(ledger),"total_tokens":sum(x["total_tokens"] for x in ledger),
         "green_delegations_released":released,"delegations_withheld":withheld,"local_repair_attempts":repairs,
         "external_api_cost_usd":"NOT_CALCULATED_PRICE_CONFIG_REQUIRED"}
def candidate(p,cid):
 x=json.load(open(p,encoding="utf-8"));return next(q for q in x["candidates"] if q["candidate_id"]==cid)
def green(t):
 b=json.dumps(t).lower();bad=["xauusd","cand-b","cpc","drawdown","9-pip","stage 1","oos","risk_percent","starting_equity","profit factor","parameter range"]
 if any(x in b for x in bad):return False
 return any(x in b for x in ["rolling","mean","atr","true range","numeric","moving average","pure python"])
def main():
 p=argparse.ArgumentParser();p.add_argument("--env",default=".env");p.add_argument("--spec",required=True);p.add_argument("--candidate",required=True);p.add_argument("--workdir",default="evidence/build_v2");a=p.parse_args();core.env(a.env)
 reg=json.load(open("config/agent_registry.json"));c=candidate(a.spec,a.candidate);wd=Path(a.workdir)/a.candidate;ws=Path("workspace")/a.candidate/"build_v2";wd.mkdir(parents=True,exist_ok=True);ws.mkdir(parents=True,exist_ok=True);ledger=[];released=withheld=repairs=0
 ob,om,ok=core.agent(reg,"orchestrator")
 od=core.call(ob,om,[{"role":"system","content":"Local Restricted lead. Sanitize external tasks aggressively."},{"role":"user","content":"Decompose frozen candidate into generic utilities safe to disclose without instrument/candidate/combined rules/parameter ranges and a local integration plan. JSON only: generic_tasks [{task_id,instruction}], integration_plan. Candidate:\\n"+json.dumps(c,indent=2)}],ok);record(ledger,"LOCAL_DMR",om,"DECOMPOSITION","RED_LOCAL",od)
 try:plan=core.parse(od["choices"][0]["message"]["content"])
 except:plan={"generic_tasks":[],"integration_plan":"Implement locally."}
 core.save(wd/"01_decomposition.json",{"plan":plan,"stage1_performance_seen":False})
 parts=[]
 for i,t in enumerate(plan.get("generic_tasks",[]),1):
  allow=green(t);core.save(wd/f"02_gateway_{i:02d}.json",{"task":t,"classification":"GREEN" if allow else "RED","released":allow})
  if not allow:withheld+=1;continue
  cb,cm,ck=core.agent(reg,"coding_agent");d=core.call(cb,cm,[{"role":"system","content":"Generic coding utility only. Return Python source only."},{"role":"user","content":t["instruction"]}],ck);record(ledger,"EXTERNAL_CODING_AGENT",cm,t.get("task_id","GENERIC"),"GREEN",d);released+=1
  code=strip_source(d["choices"][0]["message"]["content"]);cp=ws/f"component_{i:02d}.py";cp.write_text(code,encoding="utf-8")
  try:py_compile.compile(str(cp),doraise=True);passed=True;err=None
  except Exception as e:passed=False;err=str(e)
  core.save(wd/f"03_component_{i:02d}.json",{"state":"PASS" if passed else "HOLD","sha256":hashlib.sha256(code.encode()).hexdigest(),"error":err})
  if passed:parts.append({"task":t,"source":code})
 base="""Implement COMPLETE self-contained local Python strategy module.
Return JSON ONLY: {"python_source":"<complete source>"}.
Required top-level functions: metadata(), parameter_schema(), prepare(history), signal(history,prepared,params).
history is list of completed OHLC dicts. No network/files/MT5/cloud. No account sizing, equity, friction, CPC, drawdown or PASS/FAIL.
Frozen candidate:
"""+json.dumps(c,indent=2)+"\\nIntegration plan:\\n"+str(plan.get("integration_plan",""))+"\\nGeneric utilities:\\n"+json.dumps(parts,indent=2)
 feedback="";last=None;final=None;failures=[]
 for rev in range(1,MAX_REPAIRS+2):
  prompt=base if rev==1 else base+"\\nPrevious implementation failed deterministic compilation/checks. Repair ONLY implementation defects. Failure:\\n"+feedback+"\\nPrevious source:\\n"+final
  d=core.call(ob,om,[{"role":"system","content":"Local Restricted integrator. Output requested JSON only."},{"role":"user","content":prompt}],ok);record(ledger,"LOCAL_DMR",om,"INTEGRATION" if rev==1 else "REPAIR","RED_LOCAL",d)
  final=strip_source(d["choices"][0]["message"]["content"]);mp=ws/f"strategy_module_r{rev}.py";mp.write_text(final,encoding="utf-8")
  failures=[]
  try:py_compile.compile(str(mp),doraise=True)
  except Exception as e:failures=["COMPILE:"+str(e)]
  core.save(wd/f"04_integration_r{rev}.json",{"state":"PASS" if not failures else "HOLD","module":str(mp),"sha256":hashlib.sha256(final.encode()).hexdigest(),"failures":failures})
  if not failures:break
  repairs+=1;sig=(hashlib.sha256(final.encode()).hexdigest(),tuple(failures))
  if sig==last:failures.append("NO_REPAIR_PROGRESS");break
  last=sig;feedback=json.dumps(failures)
 state="IMPLEMENTATION_READY" if not failures else "HOLD_FOR_HUMAN"
 rs=summary(ledger,released,withheld,repairs);core.save(wd/"resource_ledger.json",ledger);core.save(wd/"resource_summary.json",rs)
 out={"state":state,"candidate_id":c["candidate_id"],"module":str(mp),"module_sha256":hashlib.sha256(final.encode()).hexdigest(),"generic_tasks_proposed":len(plan.get("generic_tasks",[])),"generic_tasks_released":released,"delegations_withheld":withheld,"external_agent_received_full_candidate":False,"stage1_performance_seen":False,"failures":failures,"resources":rs}
 core.save(wd/"summary.json",out);print(json.dumps(out,indent=2))
if __name__=="__main__":main()
