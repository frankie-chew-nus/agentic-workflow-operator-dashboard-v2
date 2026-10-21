import argparse,json,hashlib,importlib.util,datetime,math
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
 s=importlib.util.spec_from_file_location("b003r003",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 p=argparse.ArgumentParser();p.add_argument("--release-record",required=True);p.add_argument("--output",required=True);a=p.parse_args()
 r=json.load(open(a.release_record));mp=Path(a.release_record).parent/r["module"]
 if not mp.exists() or sha(mp)!=r["module_sha256"]:
  out={"state":"SEMANTIC_B003_V2_HOLD","reason":"RELEASE_IDENTITY_FAILURE","candidate_code_executed":False};Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));return
 m=load(mp);checks=[]
 def ck(n,x,d=""):checks.append({"check":n,"state":"PASS" if x else "FAIL","detail":d})
 ck("IDENTITY",m.metadata()=={"candidate_id":"CAND-B-003","version":"v2.1.1"},repr(m.metadata()))
 ck("PARAMETER_SCHEMA",m.parameter_schema()=={"wick_body_ratio":[2.0,5.0],"pivot_lookback":[1,1]},repr(m.parameter_schema()))
 # Day 1 creates known pivots for Day 2. Day 2 contains a crafted lower-wick bar near S1.
 bars=[]
 d1=datetime.datetime(2024,1,2)
 # Previous day H=110 L=90 C=100 => P=100, S1=90, S2=80, R1=110, R2=120.
 for i in range(10):
  bars.append({"timestamp":d1+datetime.timedelta(minutes=i),"open":100.0,"high":110.0 if i==2 else 101.0,"low":90.0 if i==3 else 99.0,"close":100.0 if i<9 else 100.0,"tick_volume":1,"volume":0,"spread":0})
 d2=datetime.datetime(2024,1,3)
 for i in range(5):
  bars.append({"timestamp":d2+datetime.timedelta(minutes=i),"open":91.0,"high":91.2,"low":90.8,"close":91.0,"tick_volume":1,"volume":0,"spread":0})
 # Crafted bar: range=1.0, body=.4 => passes ratio2 (1 > .8), fails ratio5 (1 > 2 false);
 # lower wick .76/range, low=90 exactly S1.
 bars.append({"timestamp":d2+datetime.timedelta(minutes=5),"open":90.76,"high":91.0,"low":90.0,"close":90.36,"tick_volume":1,"volume":0,"spread":0})
 p2={"wick_body_ratio":2.0,"pivot_lookback":1};p5={"wick_body_ratio":5.0,"pivot_lookback":1}
 try:
  a2=m.prepare(bars,p2);a5=m.prepare(bars,p5)
  ck("PREPARED_DICT",isinstance(a2,dict),repr(type(a2)))
  ck("PREPARED_LENGTH",len(a2.get("ohlc",[]))==len(bars) and len(a2.get("pivots",[]))==len(bars),f"{len(a2.get('ohlc',[]))}/{len(a2.get('pivots',[]))}/{len(bars)}")
  # First day must be nonactionable due no prior day.
  ck("NO_PRIOR_DAY_NONACTIONABLE",all(m.signal_at(i,a2,p2)==0 for i in range(10)))
  idx=len(bars)-1;s2=m.signal_at(idx,a2,p2);s5=m.signal_at(idx,a5,p5)
  ck("WICK_RATIO_RESPONSIVE",s2==1 and s5==0,f"ratio2={s2}, ratio5={s5}")
  ck("DETERMINISTIC",m.signal_at(idx,a2,p2)==m.signal_at(idx,a2,p2))
  ck("SIGNAL_DOMAIN",all(m.signal_at(i,a2,p2) in (-1,0,1) for i in range(len(bars))))
  # mutate future only relative to earlier day2 index
  probe=12;barsx=[dict(x) for x in bars]
  for j in range(probe+1,len(barsx)):barsx[j].update(open=9999,high=10000,low=1,close=5000)
  ax=m.prepare(barsx,p2);ck("NO_FUTURE_LEAKAGE",m.signal_at(probe,a2,p2)==m.signal_at(probe,ax,p2))
 except Exception as e:ck("MODULE_RUNTIME",False,type(e).__name__+":"+str(e))
 fail=[x for x in checks if x["state"]=="FAIL"];out={"state":"SEMANTIC_B003_V2_PASS" if not fail else "SEMANTIC_B003_V2_HOLD","module_sha256":r["module_sha256"],"failure_count":len(fail),"checks":checks,"performance_data_used":False}
 Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(out,indent=2),encoding="utf-8");print(json.dumps(out,indent=2))
if __name__=="__main__":main()
