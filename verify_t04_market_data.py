"""Read-only T04 resource verification for Operator review.

Checks actual MT5 TSV structure, row validity, chronology and day coverage.
Does not calculate ATR, modify data, execute strategies or confer approval.
"""
import csv,datetime,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/"data"/"stage1_xauusd_m1.csv"
REQUIRED={"<DATE>","<TIME>","<OPEN>","<HIGH>","<LOW>","<CLOSE>"}
def main():
 if not DATA.is_file():raise SystemExit("HOLD: dataset missing")
 digest=hashlib.sha256();rows=0;bad=0;nonmonotonic=0;days=set();first=None;last=None;previous=None
 with DATA.open("rb") as raw:
  for block in iter(lambda:raw.read(1048576),b""):digest.update(block)
 with DATA.open("r",encoding="utf-8-sig",newline="") as f:
  reader=csv.DictReader(f,delimiter="\t")
  fields=set(reader.fieldnames or [])
  if not REQUIRED.issubset(fields):raise SystemExit("HOLD: required OHLC/date columns absent")
  for row in reader:
   rows+=1
   try:
    stamp=datetime.datetime.strptime(row["<DATE>"]+" "+row["<TIME>"],"%Y.%m.%d %H:%M:%S")
    o,h,l,c=(float(row[k]) for k in ("<OPEN>","<HIGH>","<LOW>","<CLOSE>"))
    if not all(map(__import__("math").isfinite,(o,h,l,c))) or h<max(o,c,l) or l>min(o,c,h):raise ValueError("OHLC")
    if previous is not None and stamp<=previous:nonmonotonic+=1
    previous=stamp;first=first or stamp;last=stamp;days.add(stamp.date())
   except (ValueError,TypeError,KeyError):bad+=1
 report={"mode":"READ_ONLY_T04_DATASET_VALIDATION","file":"data/stage1_xauusd_m1.csv",
  "sha256":digest.hexdigest(),"size_bytes":DATA.stat().st_size,"rows":rows,
  "invalid_rows":bad,"non_increasing_timestamps":nonmonotonic,
  "first_timestamp":first.isoformat() if first else None,
  "last_timestamp":last.isoformat() if last else None,"distinct_calendar_days":len(days),
  "ohlc_data_check":"PASS" if rows>0 and bad==0 and nonmonotonic==0 else "HOLD",
  "atr_implementation":"NOT_VERIFIED","previous_day_ohlc_implementation":"NOT_VERIFIED",
  "operator_inventory_approval":"PENDING","writes_performed":False,"production_authority":False}
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
