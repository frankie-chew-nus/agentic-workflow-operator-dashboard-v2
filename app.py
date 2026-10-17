"""Local-only Operator A–E dashboard."""
import html,threading
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import parse_qs,urlsplit
from core import snapshot,new,db,approve,research,synthesize,execute

def esc(v): return html.escape(str(v),quote=True)
class Handler(BaseHTTPRequestHandler):
    def page(self, body, status=200):
        b=body.encode();self.send_response(status);self.send_header("Content-Type","text/html; charset=utf-8");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        body='<h1>Operator A–E</h1><p>Local workflow · XAUUSD M1 · diagnostic backtesting only; no broker execution.</p><form method=post action=/new><input name=objective required size=72 placeholder="Research objective"><button>Start from A</button></form>'
        for r in snapshot():
            rid=esc(r["id"]);st=esc(r["stage"]);state=esc(r["state"])
            body+=f'<section><h3>{rid} — {st}: {state}</h3><p>{esc(r["objective"])}</p><p>{esc(r["detail"])}</p><p>Elapsed since created: {max(0,int(r["updated"]-r["created"]))}s</p>'
            if r["state"] in ("READY","HOLD") and r["stage"] in ("A","B","C","D"):
                body+=f'<form method=post action=/run><input type=hidden name=id value="{rid}"><button>Run / retry {st}</button></form>'
            if r["state"]=="WAIT_HUMAN":
                body+=f'<form method=post action=/approve><input type=hidden name=id value="{rid}"><textarea name=rationale required minlength=8 placeholder="Decision rationale (minimum 8 characters)"></textarea><button name=decision value=APPROVE>Approve / release</button><button name=decision value=REJECT>Reject</button></form>'
            c=db();arts=list(c.execute("SELECT stage,kind,path,sha256 FROM artifacts WHERE run_id=? ORDER BY stage,kind",(r["id"],)));events=list(c.execute("SELECT stage,kind,detail,ts FROM events WHERE run_id=? ORDER BY id DESC LIMIT 10",(r["id"],)));c.close()
            body+='<details><summary>Artifacts and SHA256</summary><pre>'+esc("\n".join(f"{a[0]} {a[1]} {a[2]} {a[3]}" for a in arts))+'</pre></details><details><summary>Recent events</summary><pre>'+esc("\n".join(f"{e[0]} {e[1]} {e[2]}" for e in events))+'</pre></details></section>'
        body='<!doctype html><meta charset=utf-8><meta http-equiv=refresh content=10><title>Operator A–E</title><style>body{font:16px system-ui;max-width:1050px;margin:24px auto;padding:0 18px}section{border:1px solid #b8c7d9;padding:18px;margin:16px 0;border-radius:8px}button{padding:9px;margin:5px}textarea{display:block;width:90%;height:55px}pre{white-space:pre-wrap;overflow-wrap:anywhere}input{padding:9px}</style>'+body
        self.page(body)
    def do_POST(self):
        try:
            n=int(self.headers.get("Content-Length","0"))
            if n>10000:raise ValueError("Request too large")
            v={k:x[0] for k,x in parse_qs(self.rfile.read(n).decode()).items()}
            route=urlsplit(self.path).path
            if route=="/new": new(v["objective"])
            elif route=="/run":
                rid=v["id"];c=db();r=c.execute("SELECT stage,state FROM runs WHERE id=?",(rid,)).fetchone();c.close()
                if not r: raise ValueError("Unknown run")
                stage=r["stage"]
                if stage=="A": fn=research
                elif stage=="B": fn=synthesize
                elif stage in ("C","D"): fn=lambda x:execute(x,stage)
                else: raise ValueError("Stage cannot be run")
                threading.Thread(target=fn,args=(rid,),daemon=True).start()
            elif route=="/approve": approve(v["id"],v["decision"],v["rationale"])
            else: raise ValueError("Unknown route")
            self.send_response(303);self.send_header("Location","/");self.end_headers()
        except Exception as e:self.page("<h2>Request rejected</h2><pre>"+esc(e)+"</pre><a href='/'>Return</a>",400)
if __name__=="__main__":
    print("Local dashboard http://127.0.0.1:8788/")
    ThreadingHTTPServer(("127.0.0.1",8788),Handler).serve_forever()
