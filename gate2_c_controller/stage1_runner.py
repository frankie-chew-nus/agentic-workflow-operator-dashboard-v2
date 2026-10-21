import argparse,json,hashlib,importlib.util,math,statistics,datetime
from pathlib import Path
from market_data.policy import create_source

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadmod(p):
 s=importlib.util.spec_from_file_location("released_strategy",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--plan",required=True);p.add_argument("--manifest",required=True);p.add_argument("--release-record",required=True);p.add_argument("--output-dir",required=True);a=p.parse_args()
 cfg=json.load(open(a.config));plan=json.load(open(a.plan));man=json.load(open(a.manifest));rec=json.load(open(a.release_record))
 release=Path(a.release_record).parent/rec["module"]
 # fail-fast identities
 checks={"release_hash":sha(release)==rec["module_sha256"],"dataset_manifest":sha(a.manifest)==cfg["dataset_manifest_sha256"],"raw_dataset":sha(man["raw_file"])==man["raw_sha256"],"variant_count":len(plan["variants"])==cfg["search"]["max_variants"]}
 if not all(checks.values()):
  print(json.dumps({"state":"HOLD","reason":"PRE_RUN_IDENTITY_FAILURE","checks":checks},indent=2));return
 # Explicit Operator amendment: XAUUSD 1 pip = 0.01, so 9 pips = 0.09 price units.
 if cfg.get("friction",{}).get("round_trip_pips")!=9.0: raise SystemExit("HOLD: friction config changed")
 pip_size=0.01;friction_price=0.09
 src=create_source("C","CSV",path=man["raw_file"]);bars=src.get_bars()
 m=loadmod(release);out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
 results=[];alltrades=[]
 for v in plan["variants"]:
  par=v["parameters"];equity=cfg["starting_equity_usd"];peak=equity;maxdd=0.0;trades=[];activities={}
  prepared=m.prepare(bars)
  # Completed bar i generates decision; entry is next bar open. One position at a time.
  i=60
  while i < len(bars)-1:
   hist=bars[:i+1];sig=m.signal(hist,prepared,par)
   side=None
   if isinstance(sig,dict): side=str(sig.get("side") or sig.get("signal") or "").upper()
   elif sig in (1,"BUY","LONG"):side="LONG"
   elif sig in (-1,"SELL","SHORT"):side="SHORT"
   if side not in ("LONG","BUY","SHORT","SELL"):i+=1;continue
   long=side in ("LONG","BUY");entry_i=i+1;entry=bars[entry_i]["open"]
   # Stop distance: current ATR from raw bars, Wilder-style simple TR mean over atr_period, using completed bars only.
   n=int(par["atr_period"]);trs=[]
   for j in range(max(1,i-n+1),i+1):
    pc=bars[j-1]["close"];b=bars[j];trs.append(max(b["high"]-b["low"],abs(b["high"]-pc),abs(b["low"]-pc)))
   if len(trs)<n:i+=1;continue
   stopdist=sum(trs)/len(trs)
   if stopdist<=0:i+=1;continue
   sl=entry-stopdist if long else entry+stopdist;tp=entry+stopdist*par["risk_reward_ratio"] if long else entry-stopdist*par["risk_reward_ratio"]
   risk_usd=equity*cfg["risk_per_trade_fraction"];raw_lots=risk_usd/(stopdist*cfg["symbol_spec"]["contract_size"])
   step=cfg["symbol_spec"]["volume_step"];lots=math.floor(raw_lots/step)*step;lots=max(cfg["symbol_spec"]["volume_min"],min(lots,cfg["symbol_spec"]["volume_max"]))
   exit_i=None;exit_price=None;reason=None
   for k in range(entry_i,len(bars)):
    b=bars[k]
    hit_sl=(b["low"]<=sl if long else b["high"]>=sl);hit_tp=(b["high"]>=tp if long else b["low"]<=tp)
    if hit_sl and hit_tp: exit_i=k;exit_price=sl;reason="BOTH_HIT_STOP_FIRST";break
    if hit_sl:exit_i=k;exit_price=sl;reason="STOP";break
    if hit_tp:exit_i=k;exit_price=tp;reason="TARGET";break
   if exit_i is None:break
   gross=(exit_price-entry if long else entry-exit_price)*cfg["symbol_spec"]["contract_size"]*lots
   friction=friction_price*cfg["symbol_spec"]["contract_size"]*lots
   net=gross-friction;equity+=net;peak=max(peak,equity);dd=(peak-equity)/peak*100 if peak else 0;maxdd=max(maxdd,dd)
   day=bars[entry_i]["timestamp"].date().isoformat();activities[day]=activities.get(day,0)+2
   t={"variant_id":v["variant_id"],"entry_time":bars[entry_i]["timestamp"].isoformat(),"exit_time":bars[exit_i]["timestamp"].isoformat(),"side":"LONG" if long else "SHORT","entry":entry,"exit":exit_price,"sl":sl,"tp":tp,"lots":lots,"gross_pnl":gross,"friction_usd":friction,"net_pnl":net,"exit_reason":reason,"equity_after":equity}
   trades.append(t);alltrades.append(t);i=exit_i+1
  wins=[x["net_pnl"] for x in trades if x["net_pnl"]>0];loss=[x["net_pnl"] for x in trades if x["net_pnl"]<0]
  wr=len(wins)/len(trades) if trades else 0;gp=sum(wins);gl=sum(abs(x) for x in loss);pf=gp/gl if gl else (float("inf") if gp else 0);avgl=gl/len(loss) if loss else 0
  cpc=(wr*pf/avgl) if avgl and math.isfinite(pf) else (float("inf") if wr and pf==float("inf") else 0)
  rets=[x["net_pnl"]/cfg["starting_equity_usd"] for x in trades]
  sharpe=(statistics.mean(rets)/statistics.stdev(rets)*math.sqrt(len(rets))) if len(rets)>1 and statistics.stdev(rets)>0 else 0
  maxact=max(activities.values()) if activities else 0
  gates={"cpc":cpc>=cfg["hard_gates"]["cpc_min"],"drawdown":maxdd<cfg["hard_gates"]["max_drawdown_pct_strictly_less_than"],"activities":maxact<cfg["hard_gates"]["daily_activities_strictly_less_than"]}
  state="HOLD_FOR_HUMAN" if cpc>2.0 or sharpe>2.0 else ("PASS" if all(gates.values()) else "FAIL")
  results.append({"variant_id":v["variant_id"],"parameters":par,"trade_count":len(trades),"ending_equity":equity,"win_rate":wr,"profit_factor":pf,"average_loss":avgl,"cpc":cpc,"max_drawdown_pct":maxdd,"sharpe":sharpe,"max_daily_activities":maxact,"gates":gates,"state":state})
 (out/"variant_results.json").write_text(json.dumps(results,indent=2,allow_nan=True),encoding="utf-8")
 (out/"trade_ledger.json").write_text(json.dumps(alltrades,indent=2),encoding="utf-8")
 summary={"state":"STAGE1_COMPLETE","variant_count":len(results),"pass_count":sum(x["state"]=="PASS" for x in results),"fail_count":sum(x["state"]=="FAIL" for x in results),"human_hold_count":sum(x["state"]=="HOLD_FOR_HUMAN" for x in results),"release_sha256":rec["module_sha256"],"dataset_raw_sha256":man["raw_sha256"],"friction_pip_size":pip_size,"round_trip_friction_price":friction_price,"execution_rule":"completed bar signal -> next bar open; same-bar SL+TP ambiguity resolves STOP first","results_sha256":sha(out/"variant_results.json"),"trade_ledger_sha256":sha(out/"trade_ledger.json")}
 (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8");print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
