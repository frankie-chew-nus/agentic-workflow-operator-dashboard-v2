import argparse,json,hashlib,importlib.util
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
 s=importlib.util.spec_from_file_location("r003",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 p=argparse.ArgumentParser();p.add_argument("--release-record",required=True);p.add_argument("--output",required=True);a=p.parse_args()
 r=json.load(open(a.release_record));mp=Path(a.release_record).parent/r["module"]
 if sha(mp)!=r["module_sha256"]:raise SystemExit("HOLD: hash mismatch")
 m=load(mp);bars=[]
 # deterministic varying OHLC, enough to make ATR periods observably different
 for i in range(100):
  amp=0.2+(i%11)*0.07;o=100+i*.01;c=o+(.08 if i%3 else -.11);bars.append({"open":o,"high":max(o,c)+amp,"low":min(o,c)-amp*.7,"close":c})
 p10={"atr_period":10,"body_multiplier":1.2,"risk_reward_ratio":1.5};p20={"atr_period":20,"body_multiplier":2.0,"risk_reward_ratio":3.0}
 checks=[]
 def ck(n,x,d=""):checks.append({"check":n,"state":"PASS" if x else "FAIL","detail":d})
 a10=m.prepare(bars,p10);a20=m.prepare(bars,p20)
 ck("PREPARE_LENGTH",len(a10)==len(bars) and len(a20)==len(bars))
 # ATR parameter responsiveness
 try:
  x=float(a10.iloc[-1]["atr"]);y=float(a20.iloc[-1]["atr"]);ck("ATR_PERIOD_RESPONSIVE",abs(x-y)>1e-12,f"{x} vs {y}")
 except Exception as e:ck("ATR_PERIOD_RESPONSIVE",False,str(e))
 # index-addressability/determinism
 vals=[m.signal_at(i,a10,p10) for i in range(40,100)]
 vals2=[m.signal_at(i,a10,p10) for i in range(40,100)]
 ck("DETERMINISTIC",vals==vals2)
 ck("SIGNAL_DOMAIN",all(x in (-1,0,1) for x in vals),repr(set(vals)))
 # future leakage probe: mutate only rows after index and require same signal at index
 idx=70;bars2=[dict(x) for x in bars]
 for j in range(idx+1,len(bars2)):bars2[j]={"open":9999.,"high":10000.,"low":1.,"close":5000.}
 b10=m.prepare(bars2,p10);ck("NO_FUTURE_LEAKAGE",m.signal_at(idx,a10,p10)==m.signal_at(idx,b10,p10))
 # parameter schema exact
 ck("PARAMETER_SCHEMA",m.parameter_schema()=={"atr_period":[10,20],"body_multiplier":[1.2,2.0],"risk_reward_ratio":[1.5,3.0]},repr(m.parameter_schema()))
 fail=[x for x in checks if x["state"]=="FAIL"];out={"state":"SEMANTIC_V2_PASS" if not fail else "SEMANTIC_V2_HOLD","module_sha256":r["module_sha256"],"failure_count":len(fail),"checks":checks,"performance_data_used":False}
 Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(out,indent=2),encoding="utf-8");print(json.dumps(out,indent=2))
if __name__=="__main__":main()
