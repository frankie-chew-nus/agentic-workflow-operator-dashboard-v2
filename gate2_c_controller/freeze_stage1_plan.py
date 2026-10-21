import argparse,json,hashlib,itertools,datetime
from pathlib import Path

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def objsha(o): return hashlib.sha256(canon(o).encode()).hexdigest()

def main():
 p=argparse.ArgumentParser();p.add_argument("--manifest",required=True);p.add_argument("--release-record",required=True);p.add_argument("--spec",required=True);p.add_argument("--output-dir",default="evidence/stage1_config");a=p.parse_args()
 m=json.load(open(a.manifest,encoding="utf-8"));r=json.load(open(a.release_record,encoding="utf-8"));s=json.load(open(a.spec,encoding="utf-8"))
 if m.get("state")!="FROZEN":raise SystemExit("HOLD: dataset manifest not FROZEN")
 if r.get("state")!="IMPLEMENTATION_RELEASED":raise SystemExit("HOLD: implementation not RELEASED")
 c=next(x for x in s["candidates"] if x["candidate_id"]==r["candidate_id"])
 # 50-point precommitted deterministic search: 5 x 5 x 2 = 50.
 # All points lie inside B's frozen ranges; no performance has been observed.
 atr=[10,12,15,18,20]
 body=[1.2,1.4,1.6,1.8,2.0]
 rr=[1.5,3.0]
 variants=[]
 for i,(x,y,z) in enumerate(itertools.product(atr,body,rr),1):
  variants.append({"variant_id":f"{c['candidate_id']}-S1-{i:03d}","parameters":{"atr_period":x,"body_multiplier":y,"risk_reward_ratio":z},"selection_reason":"PRECOMMITTED_FACTORIAL_GRID"})
 cfg={"state":"STAGE1_CONFIG_FROZEN","candidate_id":c["candidate_id"],"candidate_version":c["version"],
 "implementation_sha256":r["module_sha256"],"dataset_manifest_sha256":sha(a.manifest),"dataset_raw_sha256":m["raw_sha256"],"dataset_normalized_sha256":m["normalized_sha256"],
 "market_data_adapter_version":m["adapter_version"],"binding":"FROZEN_CSV","starting_equity_usd":10000.0,"risk_per_trade_fraction":0.01,
 "symbol":"XAUUSD.r","timeframe":"M1","symbol_spec":{"digits":2,"point":0.01,"contract_size":100.0,"tick_size":0.01,"tick_value":1.0,"volume_min":0.01,"volume_max":20.0,"volume_step":0.01},
 "friction":{"round_trip_pips":9.0,"owner":"OPERATOR_HARNESS","candidate_override_permitted":False},
 "hard_gates":{"cpc_min":1.2,"max_drawdown_pct_strictly_less_than":15.0,"daily_activities_strictly_less_than":2000,"martingale_grid_averaging_down_allowed":False,"black_box_dependency_allowed":False},
 "outlier_hold":{"cpc_strictly_greater_than":2.0,"sharpe_strictly_greater_than":2.0},
 "cpc_definition":{"name":"Harris CPC / Trader's Index","formula":"win_rate * profit_factor / average_loss","average_loss_definition":"sum(abs(net_loss)) / losing_trade_count"},
 "search":{"max_variants":50,"design":"PRECOMMITTED_FACTORIAL_GRID","atr_period_points":atr,"body_multiplier_points":body,"risk_reward_ratio_points":rr,"adaptive_extension_allowed":False},
 "stage1_performance_seen_when_frozen":False}
 out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
 (out/"stage1_config.json").write_text(json.dumps(cfg,indent=2),encoding="utf-8")
 (out/"variant_plan.json").write_text(json.dumps({"state":"VARIANT_PLAN_FROZEN","variant_count":len(variants),"variants":variants},indent=2),encoding="utf-8")
 record={"state":"STAGE1_PLAN_FROZEN","config_sha256":sha(out/"stage1_config.json"),"variant_plan_sha256":sha(out/"variant_plan.json"),"variant_count":len(variants),"performance_seen":False}
 (out/"freeze_record.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
 print(json.dumps(record,indent=2))
if __name__=="__main__":main()
