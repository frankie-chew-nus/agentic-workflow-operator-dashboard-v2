import argparse,json,hashlib,importlib.util
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
 s=importlib.util.spec_from_file_location("b003",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 p=argparse.ArgumentParser();p.add_argument("--release-record",required=True);p.add_argument("--output",required=True);a=p.parse_args()
 r=json.load(open(a.release_record));mp=Path(a.release_record).parent/r["module"]
 if not mp.exists() or sha(mp)!=r["module_sha256"]:
  out={"state":"SEMANTIC_HOLD","reason":"RELEASE_IDENTITY_FAILURE","candidate_code_executed":False};Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));return
 m=load(mp);checks=[]
 def ck(n,x,d=""):checks.append({"check":n,"state":"PASS" if x else "FAIL","detail":d})
 ck("IDENTITY",m.metadata().get("candidate_id")=="CAND-B-003" and m.metadata().get("version")=="v2.1.1",repr(m.metadata()))
 ck("PARAMETER_SCHEMA",m.parameter_schema()=={"wick_body_ratio":[2.0,5.0],"pivot_lookback":[1,1]},repr(m.parameter_schema()))
 # 3 complete days, crafted varying bars. Timestamp included for daily pivot construction.
 import datetime
 bars=[]
 for day in range(3):
  d=datetime.datetime(2024,1,2+day)
  for minute in range(60):
   o=2000+day*10+minute*.01;c=o+(.02 if minute%2 else -.02)
   bars.append({"timestamp":d+datetime.timedelta(minutes=minute),"open":o,"high":max(o,c)+.08,"low":min(o,c)-.08,"close":c})
 p2={"wick_body_ratio":2.0,"pivot_lookback":1};p5={"wick_body_ratio":5.0,"pivot_lookback":1}
 try:
  a2=m.prepare(bars,p2);a5=m.prepare(bars,p5);ck("PREPARE_LENGTH",len(a2)==len(bars) and len(a5)==len(bars))
  vals=[m.signal_at(i,a2,p2) for i in range(len(bars))];vals2=[m.signal_at(i,a2,p2) for i in range(len(bars))]
  ck("DETERMINISTIC",vals==vals2);ck("SIGNAL_DOMAIN",all(x in (-1,0,1) for x in vals),repr(set(vals)))
  # Future mutation after index must not change past signal.
  idx=130;barsx=[dict(x) for x in bars]
  for j in range(idx+1,len(barsx)):barsx[j].update(open=9999,high=10000,low=1,close=5000)
  ax=m.prepare(barsx,p2);ck("NO_FUTURE_LEAKAGE",m.signal_at(idx,a2,p2)==m.signal_at(idx,ax,p2))
  # Required prepared fields for harness.
  cols=set(getattr(a2,"columns",[]));needed={"high","low"}
  ck("HARNESS_FIELDS",needed.issubset(cols),"columns="+repr(sorted(cols)))
  # Parameter responsiveness: prepared or signal path should differ under ratio 2 vs 5 on crafted probe.
  responsive=False
  for i in range(len(bars)):
   if m.signal_at(i,a2,p2)!=m.signal_at(i,a5,p5):responsive=True;break
  if not responsive:
   for name in ("is_pin","pin_bar","lower_pin","upper_pin","is_lower_pin","is_upper_pin"):
    if name in cols and name in set(getattr(a5,"columns",[])):
     try:
      if not a2[name].equals(a5[name]):responsive=True;break
     except:pass
  ck("WICK_RATIO_RESPONSIVE",responsive,"ratio 2.0 vs 5.0")
 except Exception as e:ck("MODULE_RUNTIME",False,type(e).__name__+":"+str(e))
 fail=[x for x in checks if x["state"]=="FAIL"];out={"state":"SEMANTIC_B003_PASS" if not fail else "SEMANTIC_B003_HOLD","module_sha256":r["module_sha256"],"failure_count":len(fail),"checks":checks,"performance_data_used":False}
 Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(out,indent=2),encoding="utf-8");print(json.dumps(out,indent=2))
if __name__=="__main__":main()
