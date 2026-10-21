import argparse,json,os,urllib.request
from pathlib import Path

def load_env(p='.env'):
    if Path(p).exists():
        for s in Path(p).read_text(encoding='utf-8').splitlines():
            if '=' in s and not s.lstrip().startswith('#'):
                k,v=s.split('=',1); os.environ.setdefault(k.strip(),v.strip())

def patch():
    p=Path('c_controller.py')
    s=p.read_text(encoding='utf-8')
    needle='key=os.getenv(a.get("api_key_env",""),"") if a.get("api_key_env") else None'
    replacement='key=(os.getenv("DMR_API_KEY","") or None) if n=="orchestrator" else (os.getenv(a.get("api_key_env",""),"") if a.get("api_key_env") else None)'
    if needle not in s:
        print('HOLD: expected controller line not found; no file changed'); return
    Path('c_controller.py.pre_endpoint_adapter_backup').write_text(s,encoding='utf-8')
    p.write_text(s.replace(needle,replacement),encoding='utf-8')
    print('PATCHED: optional DMR_API_KEY enabled')

def test():
    load_env()
    base=os.getenv('DMR_BASE_URL','').rstrip('/'); model=os.getenv('DMR_MODEL',''); key=os.getenv('DMR_API_KEY','') or None
    if not base or not model: raise SystemExit('HOLD: DMR_BASE_URL/DMR_MODEL missing')
    h={'Content-Type':'application/json'}
    if key: h['Authorization']='Bearer '+key
    b={'model':model,'messages':[{'role':'user','content':'Return exactly: DMR_ENDPOINT_OK'}],'temperature':0}
    q=urllib.request.Request(base+'/chat/completions',data=json.dumps(b).encode(),headers=h)
    with urllib.request.urlopen(q,timeout=180) as z: d=json.load(z)
    print(json.dumps({'state':'PASS','model_requested':model,'content':d['choices'][0]['message'].get('content'),'usage':d.get('usage',{})},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('cmd',choices=['patch','test']); a=p.parse_args()
    patch() if a.cmd=='patch' else test()
