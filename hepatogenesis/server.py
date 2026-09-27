"""Loopback-only teaching console. Not a production web service.

No arbitrary file paths, shell commands, uploaded code or external model calls.
Requests run synchronously and the accepted work contracts are bounded.
"""
from __future__ import annotations
from dataclasses import asdict,replace
from http.server import BaseHTTPRequestHandler,HTTPServer
from importlib import resources
import json
import secrets
from urllib.parse import urlsplit
from .common import Invalid,canonical,keys,loads,number,integer
from .dynamics import MODES,SCENARIOS,simulate
from .experiments import benchmark,make_protocol,sensor_design,information_demo
from .finite import finite_demo
from .physics import physics_demo

class Console(HTTPServer):
    def __init__(self,port=8766):
        integer(port,'port',0,65535)
        self.token=secrets.token_urlsafe(32)
        super().__init__(('127.0.0.1',port),Handler)
        self.host=f'127.0.0.1:{self.server_port}'
        self.origin=f'http://{self.host}'

class Handler(BaseHTTPRequestHandler):
    server_version='HepatoGenesis/1.0'
    def setup(self):
        super().setup();self.connection.settimeout(5.)

    def log_message(self,format,*args):
        # Do not persist request contents or tokens.
        pass

    def _host_ok(self):
        return self.headers.get_all('Host')==[self.server.host]

    def _reply(self,status,payload,ctype='application/json'):
        raw=(canonical(payload) if ctype=='application/json' else payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type',ctype+'; charset=utf-8')
        self.send_header('Content-Length',str(len(raw)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',f"default-src 'none'; script-src 'nonce-{self.server.token}'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers();self.wfile.write(raw)

    def do_GET(self):
        if not self._host_ok():return self._reply(403,{'error':'Invalid Host header.'})
        if self.path=='/':
            html=resources.files('hepatogenesis').joinpath('assets','live.html').read_text(encoding='utf-8')
            return self._reply(200,html.replace('__TOKEN__',self.server.token),'text/html')
        if self.path=='/api/catalog':
            return self._reply(200,{'scenarios':{n:asdict(s) for n,s in SCENARIOS.items()},'models':MODES})
        return self._reply(404,{'error':'Unknown route.'})

    def do_POST(self):
        if not self._host_ok():return self._reply(403,{'error':'Invalid Host header.'})
        if self.headers.get_all('Origin')!=[self.server.origin]:return self._reply(403,{'error':'Exact same-origin requests required.'})
        if len(self.headers.get_all('X-Hepato-Token') or [])!=1:
            return self._reply(403,{'error':'Exactly one session token required.'})
        token=self.headers.get('X-Hepato-Token','')
        if not secrets.compare_digest(token,self.server.token):return self._reply(403,{'error':'Invalid session token.'})
        if self.headers.get('Transfer-Encoding') is not None:return self._reply(400,{'error':'Chunked requests not accepted.'})
        if self.headers.get_content_type()!='application/json':return self._reply(415,{'error':'JSON required.'})
        lengths=self.headers.get_all('Content-Length') or []
        try:
            if len(lengths)!=1:raise Invalid('Exactly one Content-Length is required.')
            n=int(lengths[0])
            if not 1<=n<=16384:raise Invalid('Payload must be 1-16384 bytes.')
            data=loads(self.rfile.read(n),max_bytes=16384)
            if self.path=='/api/simulate':
                keys(data,{'scenario','model','memory','repair_multiplier'},{'scenario','model'})
                if data['scenario'] not in SCENARIOS:raise Invalid('Unknown scenario.')
                s=SCENARIOS[data['scenario']]
                changes={}
                if 'memory' in data:changes['memory']=number(data['memory'],'memory',0.,5.)
                if 'repair_multiplier' in data:changes['repair_multiplier']=number(data['repair_multiplier'],'repair_multiplier',0.,8.)
                s=replace(s,**changes)
                result=simulate(s,mode=data['model']).packet(thin=8)
            elif self.path=='/api/lab':
                keys(data,{'name'},{'name'})
                labs={'finite':finite_demo,'physics':physics_demo,'information':information_demo,
                      'benchmark':lambda:benchmark(make_protocol()),
                      'negative_control':lambda:benchmark(make_protocol(negative_control=True)),
                      'design':lambda:sensor_design(SCENARIOS['high_history'])}
                if data['name'] not in labs:raise Invalid('Unknown lab.')
                result=labs[data['name']]()
            else:return self._reply(404,{'error':'Unknown route.'})
        except (Invalid,ValueError,TypeError,KeyError) as exc:
            return self._reply(400,{'error':str(exc)})
        return self._reply(200,result)

def serve(port=8766):
    server=Console(port)
    print(f'HepatoGenesis research console: {server.origin}',flush=True)
    print('Local synthetic computation only. Press Ctrl+C to stop.',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
