"""Fast candidate-driven Stage 1 runner.

Optimization: the released module is evaluated on a fixed rolling window large
enough for its declared parameter ranges instead of repeatedly copying/recomputing
the entire history. This preserves completed-bar/no-lookahead semantics while
making work O(bars * variants * bounded_window), not O(bars^2).
"""
import argparse,json,hashlib,importlib.util,time,sys,math,uuid
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,o):Path(p).write_text(json.dumps(o,indent=2),encoding="utf-8")
def loadmod(p):
 s=importlib.util.spec_from_file_location("candidate_strategy",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def progress(path,t0,run_id,phase,done,total,detail=""):
 o={"state":"STAGE1_RUNNING","run_id":run_id,"phase":phase,"completed":done,"total":total,"percent":round(100*done/total,1) if total else 0,"elapsed_seconds":round(time.time()-t0,1),"heartbeat_epoch":time.time(),"detail":detail};save(path,o);print(json.dumps(o),flush=True)
def max_lookback(schema):
 vals=[]
 for k,v in schema.items():
  if isinstance(v,list) and len(v)==2 and all(isinstance(x,(int,float)) for x in v):vals.append(max(v))
 return max([40]+[int(math.ceil(x)) for x in vals])
def main():
 p=argparse.ArgumentParser()
 for n in ("config","plan","manifest","release-record","semantic-pass","output-dir"):p.add_argument("--"+n,required=True)
 a=p.parse_args();plan=json.load(open(a.plan));man=json.load(open(a.manifest));rec=json.load(open(a.release_record));sem=json.load(open(a.semantic_pass));mp=Path(a.release_record).parent/rec["module"]
 checks={"release_hash":sha(mp)==rec["module_sha256"],"semantic_pass":sem.get("state")=="SEMANTIC_GATE_PASS" and sem.get("module_sha256")==rec["module_sha256"],"candidate_plan":plan.get("state")=="STAGE1_CANDIDATE_PLAN_FROZEN"}
 if not all(checks.values()):print(json.dumps({"state":"HOLD","reason":"PRE_RUN_IDENTITY_FAILURE","checks":checks},indent=2));raise SystemExit(20)
 croot=Path(a.manifest).resolve().parents[2];sys.path.insert(0,str(croot)) if str(croot) not in sys.path else None
 from market_data.policy import create_source
 bars=create_source("C","CSV",path=man["raw_file"]).get_bars()
 bars=[{**b,"Open":b.get("Open",b.get("open")),"High":b.get("High",b.get("high")),"Low":b.get("Low",b.get("low")),"Close":b.get("Close",b.get("close"))} for b in bars]
 m=loadmod(mp);schema=m.parameter_schema();window=max_lookback(schema)+32
 out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True);pf=out/"progress.json";run_id="S1-"+uuid.uuid4().hex[:12].upper();t0=time.time();variants=plan["variants"];vtotal=len(variants);results=[]
 progress(pf,t0,run_id,"FAST_STAGE1",0,vtotal,f"bounded history window={window}; bars={len(bars)}")
 for vn,v in enumerate(variants,1):
  params=v["parameters"];signals=[]
  for i in range(window-1,len(bars)):
   history=bars[i-window+1:i+1];prepared=m.prepare(history);sig=m.signal(history,prepared,params)
   if sig in (-1,1):signals.append({"index":i,"signal":sig})
  results.append({"variant_id":v["variant_id"],"parameters":params,"signal_count":len(signals),"state":"STAGE1_EXECUTED","signals_sha256":hashlib.sha256(json.dumps(signals,sort_keys=True).encode()).hexdigest()})
  progress(pf,t0,run_id,"FAST_STAGE1",vn,vtotal,f"variant {vn}/{vtotal}; bounded history={window}")
 rp=out/"variant_results.json";save(rp,results)
 summary={"state":"STAGE1_COMPLETE","variant_count":len(results),"pass_count":0,"fail_count":0,"human_hold_count":len(results),"classification":"EXECUTION_EVIDENCE_ONLY_NO_PERFORMANCE_PASS","run_id":run_id,"execution_model":"BOUNDED_COMPLETED_HISTORY","history_window":window,"elapsed_seconds":round(time.time()-t0,3),"release_sha256":rec["module_sha256"],"semantic_gate_sha256":sha(a.semantic_pass),"results_sha256":sha(rp)}
 save(out/"summary.json",summary);progress(pf,t0,run_id,"COMPLETE",vtotal,vtotal,"Stage 1 execution evidence complete");print(json.dumps(summary,indent=2),flush=True)
if __name__=="__main__":main()
