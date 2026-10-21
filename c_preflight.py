import argparse,json,subprocess,sys
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--c-root',required=True)
a=p.parse_args()
root=Path(a.c_root)
scripts=['build_candidate_v2.py','semantic_gate_v2.py','stage1_runner_v3.py']
out={'state':'C_PREFLIGHT_READY','c_root':str(root),'contracts':{}}
for name in scripts:
    path=root/name
    if not path.exists():
        out['state']='C_PREFLIGHT_HOLD';out['contracts'][name]={'error':'missing'};continue
    q=subprocess.run([sys.executable,str(path),'--help'],cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
    out['contracts'][name]={'return_code':q.returncode,'help':q.stdout}
    if q.returncode!=0: out['state']='C_PREFLIGHT_HOLD'
ev=Path(__file__).resolve().parent/'evidence'/'c_preflight.json'
ev.parent.mkdir(parents=True,exist_ok=True);ev.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'state':out['state'],'evidence':str(ev),'scripts':scripts},indent=2))
raise SystemExit(0 if out['state']=='C_PREFLIGHT_READY' else 2)
