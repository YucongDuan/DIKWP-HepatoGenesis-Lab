#!/usr/bin/env python3
"""Optional audit against the supplied trusted book program (NumPy/SciPy needed).

This audit script intentionally imports explicitly supplied trusted local source.
It is not an input endpoint in the runtime or a sandbox for untrusted code.
The book module is not redistributed under the software companion's license.
"""
import argparse
from dataclasses import asdict
import importlib.util
from pathlib import Path
import random
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from hepatogenesis import dynamics as new
from hepatogenesis.common import load,file_digest,write_json
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--book-model',required=True,type=Path);p.add_argument('--out',required=True,type=Path);args=p.parse_args()
expected=load(ROOT/'validation/book_reference.json')['source_model_sha256']
if file_digest(args.book_model)!=expected:raise SystemExit('Refusing a different source identity. Audit the new module and update the contract explicitly.')
spec=importlib.util.spec_from_file_location('trusted_book_model',args.book_model);old=importlib.util.module_from_spec(spec);sys.modules[spec.name]=old;spec.loader.exec_module(old)
rows=[]
for s in old.SCENARIOS:
 ref=old.integrate(s,max_step=.025,rtol=1e-11,atol=1e-13);run=new.simulate(new.SCENARIOS[s.name])
 rows.append({'scenario':s.name,'maximum_endpoint_error':max(abs(float(a)-float(b)) for a,b in zip(run.states[-1][:3],ref.y[:,-1])),
              'clearance_error':abs(run.states[-1][3]-old.diagnostics(ref,s)['signed_excess_clearance_integral'])})
rng=random.Random(17);errors=[]
for _ in range(200):
 y=[rng.random(),3*rng.random(),rng.random()];u,k,S=rng.random(),3*rng.random(),2*rng.random()
 errors.append(max(abs(float(a)-float(b)) for a,b in zip(new.derivative(y,new.Parameters(),u,k,S)[:3],old.rhs(y,old.P,u,k,S))))
write_json(args.out,{'source_sha256':expected,'scenarios':rows,'maximum_endpoint_error':max(x['maximum_endpoint_error'] for x in rows),
                     'derivative_states':200,'maximum_derivative_error':max(errors),'scope':'Two implementations of the same model; no independent biological evidence.'})
print(args.out)
