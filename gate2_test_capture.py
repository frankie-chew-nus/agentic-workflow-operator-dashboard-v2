"""Explicitly captured test-run evidence, separate from test source code."""
import argparse,datetime,hashlib,json,subprocess,sys
from pathlib import Path
def capture(output):
 p=Path(output)
 if p.exists():raise FileExistsError("Refusing to overwrite test evidence")
 cmd=[sys.executable,"-m","unittest","discover","-p","test_*.py","-v"]
 started=datetime.datetime.now(datetime.timezone.utc).isoformat()
 run=subprocess.run(cmd,capture_output=True,text=True,errors="replace")
 ended=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
 except (OSError,subprocess.CalledProcessError):commit=None
 log=(run.stdout+"\n"+run.stderr)
 data={"schema":"gate2-test-run-v1","started_at_utc":started,"ended_at_utc":ended,
       "commit_sha":commit,"command":cmd,"return_code":run.returncode,
       "log_sha256":hashlib.sha256(log.encode()).hexdigest(),
       "log":log,"result":"PASS" if run.returncode==0 else "FAIL"}
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2),encoding="utf-8")
 return {"result":data["result"],"return_code":run.returncode,"path":str(p)}
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--output",required=True);args=a.parse_args()
 print(json.dumps(capture(args.output),indent=2))
