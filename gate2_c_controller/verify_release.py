import argparse,json,hashlib,subprocess,sys
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument("--release-record",required=True);p.add_argument("--semantic-gate",required=True);p.add_argument("--output",required=True);a=p.parse_args()
 rec=json.load(open(a.release_record,encoding="utf-8"));module=Path(a.release_record).parent/rec["module"]
 if not module.exists():raise SystemExit("HOLD: released module missing")
 actual=sha(module)
 if actual!=rec["module_sha256"]:
  out={"state":"SEMANTIC_GATE_HOLD","reason":"RELEASE_HASH_MISMATCH","expected":rec["module_sha256"],"actual":actual,"candidate_code_executed":False}
  Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(out,indent=2),encoding="utf-8");print(json.dumps(out,indent=2));return
 print(json.dumps({"state":"RELEASE_HASH_PASS","module":str(module),"module_sha256":actual,"next":"Run semantic gate against this exact release module."},indent=2))
if __name__=="__main__":main()
