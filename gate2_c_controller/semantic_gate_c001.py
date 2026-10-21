import argparse,hashlib,importlib.util,json,math,traceback
from pathlib import Path

EXPECTED_HASH="2b20baf5bcedb38baa6eb82f0df070c8df187e12003c14181e62ea6202f0fc4a"

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
 s=importlib.util.spec_from_file_location("candidate_under_test",p)
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def bar(o,h,l,c): return {"open":float(o),"high":float(h),"low":float(l),"close":float(c)}

def main():
 p=argparse.ArgumentParser();p.add_argument("--module",required=True);p.add_argument("--output",required=True);a=p.parse_args()
 checks=[]
 def ck(name,ok,detail=""): checks.append({"check":name,"state":"PASS" if ok else "FAIL","detail":detail})
 actual=sha(a.module);ck("RELEASED_MODULE_HASH",actual==EXPECTED_HASH,actual)
 try:
  m=load(a.module)
  md=m.metadata();ck("IDENTITY",md.get("candidate_id")=="CAND-B-001" and md.get("version")=="v2.1.1",repr(md))
  ps=m.parameter_schema();blob=json.dumps(ps).lower()
  ck("PARAMETER_NAMES",all(x in blob for x in ["atr_period","body_multiplier","risk_reward_ratio"]),repr(ps))
  ck("NO_C_OWNED_PARAMETERS",not any(x in blob for x in ["friction","equity","risk_percent","cpc","drawdown","lot"]),repr(ps))

  # Warm-up contract.
  short=[bar(100,100.2,99.8,100.05) for _ in range(5)]
  prep=m.prepare(short);ck("PREPARE_RETURNS_DICT",isinstance(prep,dict),type(prep).__name__)
  params={"atr_period":14,"body_multiplier":1.2,"risk_reward_ratio":2.25}
  try:sig=m.signal(short,prep,params);ck("WARMUP_NON_ACTIONABLE",sig is None,repr(sig))
  except Exception as e:ck("WARMUP_NON_ACTIONABLE",False,type(e).__name__+":"+str(e))

  # Determinism + no mutation on sufficiently long synthetic history.
  hist=[bar(100,100.30,99.70,100.05) for _ in range(60)]
  before=json.dumps(hist,sort_keys=True)
  prep=m.prepare(hist);a1=m.signal(hist,prep,params);a2=m.signal(hist,prep,params)
  ck("HISTORY_NOT_MUTATED",json.dumps(hist,sort_keys=True)==before)
  ck("DETERMINISTIC",a1==a2,f"{a1!r} vs {a2!r}")
  ck("SIGNAL_TYPE",a1 is None or isinstance(a1,dict),type(a1).__name__)

  # Parameter boundary probes: out-of-range values must not become actionable.
  for label,bad in [
   ("ATR_RANGE",{"atr_period":999,"body_multiplier":1.2,"risk_reward_ratio":2.25}),
   ("BODY_RANGE",{"atr_period":14,"body_multiplier":99,"risk_reward_ratio":2.25}),
   ("RR_RANGE",{"atr_period":14,"body_multiplier":1.2,"risk_reward_ratio":99})]:
   rejected=False
   try:
    x=m.signal(hist,prep,bad);rejected=(x is None)
   except Exception: rejected=True
   ck("OUT_OF_RANGE_"+label,rejected,repr(bad))

  # Synthetic semantic probes. These are deliberately non-performance examples.
  # Construct stable history, then a large exhaustion-like candle with small body.
  base=[bar(100,100.20,99.80,100.02) for _ in range(60)]
  bearish=base+[bar(100.50,101.50,98.50,100.45)] # large range, small bearish body
  bullish=base+[bar(100.45,101.50,98.50,100.50)] # large range, small bullish body
  def probe(h):
   pr=m.prepare(h);return m.signal(h,pr,params)
  try:
   sb=probe(bearish);su=probe(bullish)
   # We do not force a signal if the frozen low-volatility regime is not met by this synthetic series.
   # But if actionable, direction must follow frozen reversal semantics.
   ck("BEARISH_EXHAUSTION_DIRECTION",sb is None or (isinstance(sb,dict) and str(sb.get("side","")).upper() in {"LONG","BUY"}),repr(sb))
   ck("BULLISH_EXHAUSTION_DIRECTION",su is None or (isinstance(su,dict) and str(su.get("side","")).upper() in {"SHORT","SELL"}),repr(su))
  except Exception as e:
   ck("SEMANTIC_PROBES_NO_RUNTIME_ERROR",False,type(e).__name__+":"+str(e))

 except Exception as e:
  ck("MODULE_RUNTIME",False,type(e).__name__+":"+str(e)+"\n"+traceback.format_exc())

 failures=[x for x in checks if x["state"]!="PASS"]
 out={"state":"SEMANTIC_GATE_PASS" if not failures else "SEMANTIC_GATE_HOLD",
      "candidate_id":"CAND-B-001","module_sha256":actual,"performance_data_used":False,
      "synthetic_ohlc_only":True,"failure_count":len(failures),"checks":checks}
 Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(out,indent=2),encoding="utf-8")
 print(json.dumps(out,indent=2))
if __name__=="__main__":main()
