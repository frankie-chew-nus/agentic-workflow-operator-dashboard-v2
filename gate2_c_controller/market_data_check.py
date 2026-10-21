import argparse,json,hashlib
from pathlib import Path
from market_data.policy import create_source
def main():
 p=argparse.ArgumentParser();s=p.add_subparsers(dest="cmd",required=True)
 s.add_parser("policy-test");q=s.add_parser("freeze-csv");q.add_argument("--input",required=True);q.add_argument("--output",default="evidence/market_data/stage1_manifest.json");a=p.parse_args()
 if a.cmd=="policy-test":
  z=[]
  try:create_source("C","MT5");z.append("FAIL:C_ALLOWED_MT5")
  except PermissionError:z.append("PASS:C_BLOCKS_MT5")
  try:create_source("D","CSV",path="x");z.append("FAIL:D_ALLOWED_CSV")
  except PermissionError:z.append("PASS:D_BLOCKS_CSV")
  print(json.dumps({"state":"PASS" if all(x.startswith("PASS") for x in z) else "HOLD","checks":z},indent=2));return
 src=create_source("C","CSV",path=a.input);bars=src.get_bars();fail=[];prev=None;h=hashlib.sha256()
 for i,b in enumerate(bars):
  if b["high"]<max(b["open"],b["close"],b["low"]) or b["low"]>min(b["open"],b["close"],b["high"]):fail.append("BAD_OHLC:"+str(i))
  if prev is not None and b["timestamp"]<=prev:fail.append("NON_INCREASING:"+str(i))
  prev=b["timestamp"];h.update(json.dumps({**b,"timestamp":b["timestamp"].isoformat()},sort_keys=True,separators=(",",":")).encode()+b"\\n")
  if len(fail)>=20:break
 m={"state":"FROZEN" if not fail else "HOLD","stage":"C","binding":"FROZEN_CSV","raw_file":str(Path(a.input)),"raw_sha256":src.raw_sha256(),"normalized_sha256":h.hexdigest(),"row_count":len(bars),"start":bars[0]["timestamp"].isoformat(),"end":bars[-1]["timestamp"].isoformat(),"schema":["timestamp","open","high","low","close","tick_volume","volume","spread"],"validation_failures":fail,"adapter_version":"market_data_v1"}
 Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(m,indent=2),encoding="utf-8");print(json.dumps(m,indent=2))
if __name__=="__main__":main()
