import argparse,json,os,py_compile,ast
from pathlib import Path
import c_controller as core
def strip(s):
 s=s.strip()
 if s.startswith("```"):
  a=s.splitlines();a=a[1:] if a and a[0].startswith("```") else a;a=a[:-1] if a and a[-1].strip()=="```" else a;s="\n".join(a)
 return s
def candidate(p,cid):
 r=json.load(open(p,encoding="utf-8"));return next(x for x in r["candidates"] if x["candidate_id"]==cid)
def green(task):
 b=json.dumps(task).lower();blocked=["xauusd","cand-b","cpc","drawdown","9-pip","stage 1","oos","risk_percent","starting_equity","profit factor"]
 if any(x in b for x in blocked):return False,["RESTRICTED_TERM"]
 return any(x in b for x in ["rolling","mean","atr","true range","numeric","moving average","pure python"]),[]
def static(code):
 try:t=ast.parse(code)
 except Exception as e:return ["SYNTAX:"+str(e)]
 f=[];funcs={n.name for n in t.body if isinstance(n,ast.FunctionDef)}
 for x in ["metadata","parameter_schema","prepare","signal"]:
  if x not in funcs:f.append("MISSING:"+x)
 return f
def main():
 p=argparse.ArgumentParser();p.add_argument("--env",default=".env");p.add_argument("--spec",required=True);p.add_argument("--candidate",required=True);p.add_argument("--workdir",default="evidence/build");a=p.parse_args();core.env(a.env)
 reg=json.load(open("config/agent_registry.json"));c=candidate(a.spec,a.candidate);wd=Path(a.workdir)/a.candidate;ws=Path("workspace")/a.candidate;wd.mkdir(parents=True,exist_ok=True);ws.mkdir(parents=True,exist_ok=True)
 ob,om,ok=core.agent(reg,"orchestrator")
 prompt="Decompose this frozen candidate into zero or more generic coding utilities safe to describe without instrument/candidate/combined strategy/parameter ranges, plus a local integration plan. Return JSON only with generic_tasks [{task_id,instruction}] and integration_plan. Full candidate:\\n"+json.dumps(c,indent=2)
 od=core.call(ob,om,[{"role":"system","content":"Local Restricted lead. Sanitize external tasks aggressively."},{"role":"user","content":prompt}],ok);raw=od["choices"][0]["message"]["content"]
 try:plan=core.parse(raw)
 except:out={"state":"HOLD_FOR_HUMAN","reason":"INVALID_DECOMPOSITION"};core.save(wd/"summary.json",out);print(json.dumps(out,indent=2));return
 core.save(wd/"01_decomposition.json",{"plan":plan,"orchestrator_model":om,"stage1_performance_seen":False});parts=[]
 for i,t in enumerate(plan.get("generic_tasks",[]),1):
  allowed,reasons=green(t);core.save(wd/f"02_gateway_{i:02d}.json",{"task":t,"classification":"GREEN" if allowed else "RED","reasons":reasons,"external_agent_called":False})
  if not allowed:continue
  cb,cm,ck=core.agent(reg,"coding_agent");cd=core.call(cb,cm,[{"role":"system","content":"Implement only this generic utility. Python source only. No trading/finance assumptions."},{"role":"user","content":t["instruction"]}],ck);code=strip(cd["choices"][0]["message"]["content"]);cp=ws/f"component_{i:02d}.py";cp.write_text(code,encoding="utf-8")
  core.save(wd/f"03_external_receipt_{i:02d}.json",{"coding_model":cm,"sha256":core.sh(code),"external_agent_received_full_candidate":False})
  try:py_compile.compile(str(cp),doraise=True);passed=True;err=None
  except Exception as e:passed=False;err=str(e)
  core.save(wd/f"04_component_check_{i:02d}.json",{"state":"PASS" if passed else "HOLD","error":err})
  if not passed:out={"state":"HOLD_FOR_HUMAN","reason":"GENERIC_COMPONENT_FAILED"};core.save(wd/"summary.json",out);print(json.dumps(out,indent=2));return
  parts.append({"task":t,"source":code})
 integration="Implement complete local strategy module with top-level metadata(), parameter_schema(), prepare(history), signal(history,prepared,params). history=list of completed OHLC dicts. No network/files/MT5/cloud or risk/performance controls. Frozen candidate:\\n"+json.dumps(c,indent=2)+"\\nLocal plan:\\n"+str(plan.get("integration_plan",""))+"\\nGeneric utilities available locally:\\n"+json.dumps(parts,indent=2)
 idata=core.call(ob,om,[{"role":"system","content":"Local Restricted integration. Full strategy must stay local."},{"role":"user","content":integration}],ok);module=strip(idata["choices"][0]["message"]["content"]);mp=ws/"strategy_module.py";mp.write_text(module,encoding="utf-8");core.save(wd/"05_local_integration.json",{"module":str(mp),"sha256":core.sh(module),"orchestrator_model":om})
 f=[]
 try:py_compile.compile(str(mp),doraise=True)
 except Exception as e:f.append("COMPILE:"+str(e))
 if not f:f+=static(module)
 core.save(wd/"06_implementation_gate.json",{"state":"PASS" if not f else "HOLD","failures":f})
 out={"state":"IMPLEMENTATION_READY" if not f else "HOLD_FOR_HUMAN","candidate_id":c["candidate_id"],"module":str(mp),"module_sha256":core.sh(module),"generic_tasks_proposed":len(plan.get("generic_tasks",[])),"generic_tasks_released":len(parts),"external_agent_received_full_candidate":False,"stage1_performance_seen":False};core.save(wd/"summary.json",out);print(json.dumps(out,indent=2))
if __name__=="__main__":main()
