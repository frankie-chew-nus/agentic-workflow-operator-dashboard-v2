import argparse,json,os,hashlib,urllib.request
from pathlib import Path
def env(p=".env"):
 if Path(p).exists():
  for s in Path(p).read_text(encoding="utf-8").splitlines():
   if "=" in s and not s.lstrip().startswith("#"):
    k,v=s.split("=",1);os.environ.setdefault(k.strip(),v.strip())
def save(p,o):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(o,indent=2,ensure_ascii=False),encoding="utf-8")
def sh(s):return hashlib.sha256(s.encode()).hexdigest()
def agent(reg,n):
 a=reg["agents"][n];base=os.getenv(a["base_url_env"],"");model=os.getenv(a["model_env"],"");key=(os.getenv("DMR_API_KEY","") or None) if n=="orchestrator" else (os.getenv(a.get("api_key_env",""),"") if a.get("api_key_env") else None)
 if not base or not model:raise SystemExit("HOLD: "+n+" configuration missing")
 return base,model,key
def call(base,model,msg,key=None,timeout=None):
 h={"Content-Type":"application/json"}
 if key:h["Authorization"]="Bearer "+key
 q=urllib.request.Request(base.rstrip("/")+"/chat/completions",data=json.dumps({"model":model,"messages":msg,"temperature":0}).encode(),headers=h)
 with urllib.request.urlopen(q,timeout=(timeout or (900 if base.startswith("http://192.168.51.81") else 180))) as r:return json.load(r)
def parse(t):
 t=t.strip()
 if t.startswith("```"):
  a=t.splitlines();a=a[1:] if a and a[0].startswith("```") else a;a=a[:-1] if a and a[-1].strip()=="```" else a;t="\n".join(a)
 try:return json.loads(t)
 except:
  i,j=t.find("{"),t.rfind("}")
  if i>=0 and j>i:return json.loads(t[i:j+1])
  raise
def classify(c,reg):
 blob=json.dumps(c,ensure_ascii=False).lower();reasons=[]
 # Python, not DMR, assigns task class.
 generic_markers=["rolling_mean","arithmetic mean","numeric","values","period"]
 if not any(x in blob for x in generic_markers):reasons.append("NOT_RECOGNIZED_GENERIC_UTILITY")
 if len(blob)>reg["gateway"]["max_green_chars"]:reasons.append("PAYLOAD_TOO_LARGE")
 for x in reg["gateway"]["blocked_terms"]:
  if x in blob:reasons.append("BLOCKED_TERM:"+x)
 for x in ["http://","https://","c:\\\\","/users/","read_csv","read_excel","metatrader","dataset","market data","historical data"]:
  if x in blob:reasons.append("DATA_OR_EXTERNAL_REFERENCE:"+x)
 return ("GREEN" if not reasons else "RED"),sorted(set(reasons))
def self_test(reg,ed):
 ob,om,ok=agent(reg,"orchestrator")
 prompt="""Create a bounded coding commission for this generic task only: implement pure Python function rolling_mean(values, period). period<=0 raises ValueError; return None until at least period numeric observations exist; otherwise return arithmetic mean of last period values. No finance/trading/strategy/data/file/network/API content. Return JSON only with task_id, coding_instruction, acceptance_tests. Do not classify the task."""
 od=call(ob,om,[{"role":"system","content":"Local lead orchestrator. Describe the coding commission only. Python owns disclosure classification."},{"role":"user","content":prompt}],ok);raw=od["choices"][0]["message"]["content"]
 save(ed/"01_proposed_raw.json",{"state":"CAPTURED_PRE_GATE","raw_response":raw,"orchestrator_model":om,"raw_sha256":sh(raw),"system_fingerprint":od.get("system_fingerprint"),"usage":od.get("usage",{})})
 try:c=parse(raw)
 except Exception as e:
  out={"state":"DISCLOSURE_HOLD","classification":"RED","external_agent_called":False,"reasons":["INVALID_JSON"]};save(ed/"summary.json",out);print(json.dumps(out,indent=2));return
 save(ed/"02_proposed_parsed.json",{"commission":c,"sha256":sh(json.dumps(c,sort_keys=True))})
 cls,reasons=classify(c,reg);released=cls=="GREEN";save(ed/"03_gateway.json",{"classification":cls,"released":released,"reasons":reasons,"external_agent_called":False})
 if not released:
  out={"state":"DISCLOSURE_HOLD","classification":cls,"external_agent_called":False,"reasons":reasons};save(ed/"summary.json",out);print(json.dumps(out,indent=2));return
 cb,cm,ck=agent(reg,"coding_agent")
 cd=call(cb,cm,[{"role":"system","content":"Implement only the released GREEN coding commission. Return Python source only."},{"role":"user","content":c["coding_instruction"]+"\nAcceptance tests:\n"+json.dumps(c["acceptance_tests"])}],ck);src=cd["choices"][0]["message"]["content"].strip()
 if src.startswith("```"):
  a=src.splitlines();a=a[1:] if a and a[0].startswith("```") else a;a=a[:-1] if a and a[-1].strip()=="```" else a;src="\n".join(a)
 wp=Path("workspace")/"self_test_component.py";wp.write_text(src,encoding="utf-8");save(ed/"04_coding_receipt.json",{"state":"CALLED_AFTER_GREEN","coding_model":cm,"module_sha256":sh(src),"usage":cd.get("usage",{}),"system_fingerprint":cd.get("system_fingerprint")})
 import importlib.util
 f=[]
 try:
  s=importlib.util.spec_from_file_location("x",wp);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
  if not hasattr(m,"rolling_mean"):f.append("MISSING_FUNCTION")
  else:
   if m.rolling_mean([1,2],3) is not None:f.append("WARMUP")
   if abs(m.rolling_mean([1,2,3,4],3)-3.0)>1e-12:f.append("MEAN")
   try:m.rolling_mean([1,2],0);f.append("ZERO_NOT_REJECTED")
   except ValueError:pass
   except Exception as e:f.append("WRONG_EXCEPTION:"+type(e).__name__)
 except Exception as e:f.append("IMPORT_RUNTIME:"+type(e).__name__+":"+str(e))
 save(ed/"05_acceptance.json",{"state":"PASS" if not f else "HOLD","failures":f,"module_sha256":sh(src)})
 out={"state":"SELF_TEST_READY" if not f else "HOLD_FOR_HUMAN","classification":"GREEN","external_agent_called":True,"orchestrator_model":om,"coding_model":cm,"acceptance_test":"PASS" if not f else "HOLD"};save(ed/"summary.json",out);print(json.dumps(out,indent=2))
def main():
 p=argparse.ArgumentParser(description="Permanent Gate2 C Controller");p.add_argument("--env",default=".env");p.add_argument("--registry",default="config/agent_registry.json");sp=p.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("self-test");q.add_argument("--evidence-dir",default="evidence/self_test")
 q=sp.add_parser("build");q.add_argument("candidate");q.add_argument("--evidence-dir",default="evidence/build")
 q=sp.add_parser("build-all");q.add_argument("--evidence-dir",default="evidence/build")
 q=sp.add_parser("stage1");q.add_argument("--evidence-dir",default="evidence/stage1")
 a=p.parse_args();env(a.env);reg=json.load(open(a.registry,encoding="utf-8"))
 if a.cmd=="self-test":self_test(reg,Path(a.evidence_dir))
 else:
  out={"state":"NOT_YET_ENABLED","command":a.cmd,"reason":"Command scaffold reserved; enable only after self-test architecture passes."};print(json.dumps(out,indent=2))
if __name__=="__main__":main()
