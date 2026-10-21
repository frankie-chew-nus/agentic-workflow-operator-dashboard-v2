import argparse,json,hashlib,importlib.util,math,statistics,time
from pathlib import Path
from market_data.policy import create_source
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
 s=importlib.util.spec_from_file_location("b003",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--plan",required=True);p.add_argument("--manifest",required=True);p.add_argument("--release-record",required=True);p.add_argument("--semantic-pass",required=True);p.add_argument("--output-dir",required=True);a=p.parse_args()
 cfg=json.load(open(a.config));plan=json.load(open(a.plan));man=json.load(open(a.manifest));rec=json.load(open(a.release_record));sem=json.load(open(a.semantic_pass));mp=Path(a.release_record).parent/rec["module"]
 checks={"release_hash":sha(mp)==rec["module_sha256"],"semantic":sem.get("state")=="SEMANTIC_B003_V3_PASS" and sem.get("module_sha256")==rec["module_sha256"],"manifest":sha(a.manifest)==cfg["dataset_manifest_sha256"],"raw":sha(man["raw_file"])==man["raw_sha256"],"variants":len(plan["variants"])==7}
 if not all(checks.values()):print(json.dumps({"state":"HOLD","reason":"PRE_RUN_IDENTITY_FAILURE","checks":checks},indent=2));return
 bars=create_source("C","CSV",path=man["raw_file"]).get_bars();m=load(mp);out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True);ledger=out/"trade_ledger.jsonl";ledger.write_text("");results=[];t0=time.time()
 for vi,v in enumerate(plan["variants"],1):
  vt=time.time();par=v["parameters"];prep=m.prepare(bars,par);equity=cfg["starting_equity_usd"];peak=equity;maxdd=0.;trades=[];acts={};i=1
  while i<len(bars)-1:
   sig=m.signal_at(i,prep,par)
   if sig not in (-1,1):i+=1;continue
   long=sig==1;ei=i+1;entry=bars[ei]["open"];o,h,l,c=prep["ohlc"][i];r1,r2,s1,s2=prep["pivots"][i]
   sl=float(l if long else h)
   # next pivot in trade direction relative to entry
   candidates=sorted([float(x) for x in (r1,r2,s1,s2) if math.isfinite(float(x)) and ((x>entry) if long else (x<entry))],reverse=not long)
   if not candidates:i+=1;continue
   tp=candidates[0];sd=abs(entry-sl)
   if sd<=0 or (long and tp<=entry) or ((not long) and tp>=entry):i+=1;continue
   risk=equity*cfg["risk_per_trade_fraction"];step=cfg["symbol_spec"]["volume_step"];lots=math.floor((risk/(sd*cfg["symbol_spec"]["contract_size"]))/step)*step;lots=max(cfg["symbol_spec"]["volume_min"],min(lots,cfg["symbol_spec"]["volume_max"]))
   xi=None
   for k in range(ei,len(bars)):
    b=bars[k];hs=b["low"]<=sl if long else b["high"]>=sl;ht=b["high"]>=tp if long else b["low"]<=tp
    if hs or ht:xi=k;xp=sl if hs else tp;reason="BOTH_HIT_STOP_FIRST" if hs and ht else ("STOP" if hs else "TARGET");break
   if xi is None:break
   gross=(xp-entry if long else entry-xp)*cfg["symbol_spec"]["contract_size"]*lots;fric=.09*cfg["symbol_spec"]["contract_size"]*lots;net=gross-fric;equity+=net;peak=max(peak,equity);maxdd=max(maxdd,(peak-equity)/peak*100 if peak else 0);day=bars[ei]["timestamp"].date().isoformat();acts[day]=acts.get(day,0)+2
   tr={"variant_id":v["variant_id"],"entry_time":bars[ei]["timestamp"].isoformat(),"exit_time":bars[xi]["timestamp"].isoformat(),"side":"LONG" if long else "SHORT","entry":entry,"exit":xp,"sl":sl,"tp":tp,"lots":lots,"gross_pnl":gross,"friction_usd":fric,"net_pnl":net,"equity_after":equity,"exit_reason":reason};trades.append(tr)
   with ledger.open("a",encoding="utf-8") as f:f.write(json.dumps(tr)+"\n")
   i=xi+1
  wins=[x["net_pnl"] for x in trades if x["net_pnl"]>0];loss=[x["net_pnl"] for x in trades if x["net_pnl"]<0];wr=len(wins)/len(trades) if trades else 0;gp=sum(wins);gl=sum(abs(x) for x in loss);pf=gp/gl if gl else 0;avgl=gl/len(loss) if loss else 0;cpc=wr*pf/avgl if avgl else 0
  rets=[x["net_pnl"]/cfg["starting_equity_usd"] for x in trades];sh=(statistics.mean(rets)/statistics.stdev(rets)*math.sqrt(len(rets))) if len(rets)>1 and statistics.stdev(rets)>0 else 0;ma=max(acts.values()) if acts else 0
  gates={"cpc":cpc>=cfg["hard_gates"]["cpc_min"],"drawdown":maxdd<cfg["hard_gates"]["max_drawdown_pct_strictly_less_than"],"activities":ma<cfg["hard_gates"]["daily_activities_strictly_less_than"]}
  state="HOLD_FOR_HUMAN" if cpc>2 or sh>2 else ("PASS" if all(gates.values()) else "FAIL")
  res={"variant_id":v["variant_id"],"parameters":par,"trade_count":len(trades),"ending_equity":equity,"win_rate":wr,"profit_factor":pf,"average_loss":avgl,"cpc":cpc,"max_drawdown_pct":maxdd,"sharpe":sh,"max_daily_activities":ma,"gates":gates,"state":state,"elapsed_seconds":round(time.time()-vt,3)};results.append(res);(out/"variant_results.json").write_text(json.dumps(results,indent=2));print(f"Variant {vi}/7 | {res['elapsed_seconds']:.1f}s | trades={len(trades)} | state={state}",flush=True)
 summary={"state":"STAGE1_COMPLETE","variant_count":len(results),"pass_count":sum(x["state"]=="PASS" for x in results),"fail_count":sum(x["state"]=="FAIL" for x in results),"human_hold_count":sum(x["state"]=="HOLD_FOR_HUMAN" for x in results),"elapsed_seconds":round(time.time()-t0,3),"release_sha256":rec["module_sha256"],"dataset_raw_sha256":man["raw_sha256"],"results_sha256":sha(out/"variant_results.json"),"trade_ledger_sha256":sha(ledger)}
 (out/"summary.json").write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
