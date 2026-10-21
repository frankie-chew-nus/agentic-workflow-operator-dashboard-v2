import argparse,json,hashlib,datetime,shutil,py_compile,re
from pathlib import Path
import c_controller as core

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def strip(s):
 s=s.strip()
 m=re.search(r"```(?:json)?\s*(.*?)```",s,re.S|re.I)
 if m:s=m.group(1).strip()
 try:
  o=json.loads(s)
  if isinstance(o,dict) and isinstance(o.get("python_source"),str):return o["python_source"]
 except Exception:pass
 m=re.search(r"```(?:python)?\s*(.*?)```",s,re.S|re.I)
 return m.group(1) if m else s

def main():
 p=argparse.ArgumentParser();p.add_argument("--env",default=".env");p.add_argument("--release-record",required=True);p.add_argument("--spec",required=True);p.add_argument("--run-root",default="evidence/r003_repairs");a=p.parse_args();core.env(a.env)
 old=json.load(open(a.release_record));om=Path(a.release_record).parent/old["module"]
 if sha(om)!=old["module_sha256"]:raise SystemExit("HOLD: parent release hash mismatch")
 spec=json.load(open(a.spec));c=next(x for x in spec["candidates"] if x["candidate_id"]==old["candidate_id"])
 rid=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ");rd=Path(a.run_root)/c["candidate_id"]/rid;ws=rd/"workspace";rel=rd/"release";ws.mkdir(parents=True);rel.mkdir()
 authority={"state":"AUTHORIZED_INTERFACE_REPAIR","parent_release_sha256":old["module_sha256"],"performance_result_used":False,
 "required_contract":["prepare(history, params)","signal_at(index, prepared, params)"],
 "required_semantics":["atr_period must control ATR calculation","body_multiplier must control exhaustion threshold","risk_reward_ratio remains harness-consumed exit parameter","signal_at may use only rows <= index"],
 "prohibited_changes":["candidate hypothesis","parameter ranges","Stage-1 dataset","50-variant plan","risk","friction","performance gates"]}
 core.save(rd/"repair_authority.json",authority)
 reg=json.load(open("config/agent_registry.json"));base,model,key=core.agent(reg,"orchestrator")
 prompt="""Repair the released module for backtest correctness and computational efficiency only.
Return JSON only {"python_source":"<complete module>"}.

MANDATORY CONTRACT:
- metadata() unchanged in identity.
- parameter_schema() preserves frozen ranges exactly.
- prepare(history, params): vectorized Pandas/Numpy preparation ONCE per variant. ATR rolling period MUST use params['atr_period']; ATR moving-average regime window remains the strategy's existing 20; average-body window remains existing 10.
- signal_at(index, prepared, params): O(1) lookup using only prepared rows index and index-1. It MUST NOT inspect future rows. Return -1 short, +1 long, 0 no action.
- body_multiplier controls the existing exhaustion threshold.
- risk_reward_ratio is intentionally harness-consumed and need not alter signal generation.
- Preserve existing R002 exhaustion/reversal logic; do not redesign strategy.
- No risk sizing, friction, CPC, drawdown, PASS/FAIL, files, network, MT5 or cloud calls.

FROZEN CANDIDATE:
"""+json.dumps(c,indent=2)+"\nPARENT R002 SOURCE:\n"+om.read_text(encoding="utf-8")
 d=core.call(base,model,[{"role":"system","content":"Restricted implementation repair agent. Only authorized interface/performance repair."},{"role":"user","content":prompt}],key)
 src=strip(d["choices"][0]["message"]["content"]);mp=ws/"strategy_module.py";mp.write_text(src,encoding="utf-8")
 try:py_compile.compile(str(mp),doraise=True)
 except Exception as e:raise SystemExit("HOLD: compile failure "+str(e))
 target=rel/"strategy_module.py";shutil.copy2(mp,target)
 if sha(target)!=sha(mp):raise SystemExit("HOLD: release copy mismatch")
 rec={"state":"IMPLEMENTATION_RELEASED","candidate_id":c["candidate_id"],"version":c["version"],"run_id":rid,"module":"strategy_module.py","module_sha256":sha(target),"parent_release_sha256":old["module_sha256"],"repair_type":"INTERFACE_PERFORMANCE_CORRECTNESS","stage1_valid_performance_seen":False}
 core.save(rel/"implementation_release.json",rec)
 out={"state":"IMPLEMENTATION_RELEASED","release_module":str(target),"release_record":str(rel/"implementation_release.json"),"module_sha256":sha(target),"parent_release_sha256":old["module_sha256"],"usage":d.get("usage",{})}
 core.save(rd/"summary.json",out);print(json.dumps(out,indent=2))
if __name__=="__main__":main()
