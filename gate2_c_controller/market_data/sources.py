from pathlib import Path
import csv,hashlib,datetime
def bar(ts,x):
 return {"timestamp":ts,"open":float(x["<OPEN>"]),"high":float(x["<HIGH>"]),"low":float(x["<LOW>"]),"close":float(x["<CLOSE>"]),"tick_volume":int(x.get("<TICKVOL>",0)),"volume":float(x.get("<VOL>",0)),"spread":float(x.get("<SPREAD>",0))}
class CSVDataSource:
 def __init__(self,path): self.path=Path(path)
 def raw_sha256(self): return hashlib.sha256(self.path.read_bytes()).hexdigest()
 def get_bars(self):
  with self.path.open("r",encoding="utf-8-sig",newline="") as f:
   r=csv.DictReader(f,delimiter="\t"); out=[]
   for x in r:
    ts=datetime.datetime.strptime(x["<DATE>"]+" "+x["<TIME>"],"%Y.%m.%d %H:%M:%S");out.append(bar(ts,x))
   return out
class MT5DataSource:
 def __init__(self,symbol="XAUUSD.r"): self.symbol=symbol
 def get_bars(self,start,end):
  import MetaTrader5 as mt5
  if not mt5.initialize(): raise RuntimeError("MT5_INITIALIZE_FAILED")
  try:
   rows=mt5.copy_rates_range(self.symbol,mt5.TIMEFRAME_M1,start,end)
   return [{"timestamp":datetime.datetime.fromtimestamp(int(x["time"]),datetime.timezone.utc).replace(tzinfo=None),"open":float(x["open"]),"high":float(x["high"]),"low":float(x["low"]),"close":float(x["close"]),"tick_volume":int(x["tick_volume"]),"volume":float(x["real_volume"]),"spread":float(x["spread"])} for x in rows]
  finally: mt5.shutdown()
