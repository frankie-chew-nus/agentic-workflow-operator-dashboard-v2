import argparse,json,hashlib
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument("--manifest",required=True);p.add_argument("--release-record",required=True);p.add_argument("--semantic-pass",required=True);p.add_argument("--output-dir",required=True);a=p.parse_args()
 man=json.load(open(a.manifest));rec=json.load(open(a.release_record));sem=json.load(open(a.semantic_pass))
 if man.get("state")!="FROZEN":raise SystemExit("HOLD: dataset not frozen")
 if sem.get("state")!="SEMANTIC_B003_V3_PASS" or sem.get("module_sha256")!=rec["module_sha256"]:raise SystemExit("HOLD: semantic/release mismatch")
 # One real search dimension: pivot_lookback is fixed [1,1].
 ratios=[2.0,2.5,3.0,3.5,4.0,4.5,5.0]
 variants=[{"variant_id":f"CAND-B-003-S1-{i:03d}","parameters":{"wick_body_ratio":x,"pivot_lookback":1},"selection_reason":"PRECOMMITTED_UNIFORM_GRID"} for i,x in enumerate(ratios,1)]
 cfg={"state":"STAGE1_CONFIG_FROZEN","candidate_id":"CAND-B-003","candidate_version":"v2.1.1","implementation_sha256":rec["module_sha256"],
 "dataset_manifest_sha256":sha(a.manifest),"dataset_raw_sha256":man["raw_sha256"],"dataset_normalized_sha256":man["normalized_sha256"],"market_data_adapter_version":man["adapter_version"],
 "starting_equity_usd":10000.0,"risk_per_trade_fraction":0.01,"symbol":"XAUUSD.r","timeframe":"M1",
 "symbol_spec":{"digits":2,"point":0.01,"contract_size":100.0,"tick_size":0.01,"tick_value":1.0,"volume_min":0.01,"volume_max":20.0,"volume_step":0.01},
 "friction":{"pip_size":0.01,"round_trip_pips":9.0,"round_trip_price":0.09,"owner":"OPERATOR_HARNESS"},
 "hard_gates":{"cpc_min":1.2,"max_drawdown_pct_strictly_less_than":15.0,"daily_activities_strictly_less_than":2000},
 "outlier_hold":{"cpc_strictly_greater_than":2.0,"sharpe_strictly_greater_than":2.0},
 "search":{"max_variants":7,"design":"PRECOMMITTED_UNIFORM_GRID","wick_body_ratio_points":ratios,"pivot_lookback_points":[1],"adaptive_extension_allowed":False},
 "execution":{"entry":"next_bar_open_after_completed_signal","stop":"signal_pinbar_extreme","target":"next_pivot_level_in_trade_direction","same_bar_stop_target":"STOP_FIRST"},"stage1_performance_seen_when_frozen":False}
 out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
 (out/"stage1_config.json").write_text(json.dumps(cfg,indent=2),encoding="utf-8")
 (out/"variant_plan.json").write_text(json.dumps({"state":"VARIANT_PLAN_FROZEN","variant_count":len(variants),"variants":variants},indent=2),encoding="utf-8")
 record={"state":"STAGE1_PLAN_FROZEN","config_sha256":sha(out/"stage1_config.json"),"variant_plan_sha256":sha(out/"variant_plan.json"),"variant_count":7,"performance_seen":False}
 (out/"freeze_record.json").write_text(json.dumps(record,indent=2),encoding="utf-8");print(json.dumps(record,indent=2))
if __name__=="__main__":main()
