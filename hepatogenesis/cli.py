"""Command-line entry point. No command publishes, deploys or calls external AI."""
from __future__ import annotations
import argparse
from dataclasses import asdict
from importlib import resources
import json
from pathlib import Path
import platform
import sys
from . import __version__,RESEARCH_NOTICE
from .common import Invalid,load,write_json
from .dynamics import MODES,SCENARIOS,Scenario,Parameters,simulate,compare_models
from .experiments import benchmark,make_protocol,sensor_design,information_demo
from .finite import FiniteModel,finite_demo,solve_belief,quotient
from .physics import physics_demo
from .evidence import Ledger,import_hepatoscholar_v2
from .capsule import demo,verify,source_identity

def main(argv=None):
    parser=argparse.ArgumentParser(prog='hepatogenesis',description='DIKWP HepatoGenesis Lab - '+RESEARCH_NOTICE)
    parser.add_argument('--version',action='version',version=__version__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('doctor');sub.add_parser('chapters')
    d=sub.add_parser('demo');d.add_argument('--out',type=Path,required=True);d.add_argument('--samples',type=int,default=24)
    v=sub.add_parser('verify');v.add_argument('bundle',type=Path);v.add_argument('--manifest-sha256')
    for name in ['simulate','compare','design']:
        p=sub.add_parser(name);p.add_argument('--scenario',choices=list(SCENARIOS),default='high_history')
        p.add_argument('--config',type=Path);p.add_argument('--out',type=Path,required=True)
        if name=='simulate':p.add_argument('--model',choices=MODES,default='dynamic_history')
    b=sub.add_parser('benchmark');b.add_argument('--protocol',type=Path);b.add_argument('--negative-control',action='store_true');b.add_argument('--out',type=Path,required=True)
    for name in ['finite','physics','information']:
        p=sub.add_parser(name);p.add_argument('--out',type=Path,required=True)
    f=sub.add_parser('solve');f.add_argument('model',type=Path);f.add_argument('--initial',nargs='+',required=True);f.add_argument('--horizon',type=int,required=True);f.add_argument('--budget',type=int,required=True);f.add_argument('--out',type=Path,required=True)
    i=sub.add_parser('import-v2');i.add_argument('input',type=Path);i.add_argument('--ledger',type=Path,required=True);i.add_argument('--out',type=Path,required=True)
    s=sub.add_parser('serve');s.add_argument('--port',type=int,default=8766)
    args=parser.parse_args(argv)
    try:
        if args.command=='doctor':
            result={'system':'DIKWP HepatoGenesis Lab','version':__version__,'python':platform.python_version(),
                    'supported':sys.version_info>=(3,10),'runtime_dependencies':[],
                    'network_calls_required':False,'source':source_identity()['aggregate_sha256'],'scope':RESEARCH_NOTICE}
        elif args.command=='chapters':
            result=json.loads(resources.files('hepatogenesis').joinpath('assets','chapters.json').read_text())
        elif args.command=='serve':
            from .server import serve
            serve(args.port);return 0
        elif args.command=='demo':result=demo(args.out,args.samples)
        elif args.command=='verify':result=verify(args.bundle,args.manifest_sha256)
        elif args.command in ['simulate','compare','design']:
            p=Parameters();s=SCENARIOS[args.scenario]
            if args.config:
                from .common import keys
                packet=load(args.config);keys(packet,{'scenario','parameters'},{'scenario'})
                s=Scenario.from_dict(packet['scenario']);p=Parameters.from_dict(packet.get('parameters',{}))
            if args.command=='simulate':result=simulate(s,p,args.model).packet()
            elif args.command=='compare':result=compare_models(s,p)
            else:
                if args.config and 'parameters' in packet:raise Invalid('Design currently supports the declared default parameter family only.')
                result=sensor_design(s)
            write_json(args.out,result)
        elif args.command=='benchmark':
            if args.protocol and args.negative_control:raise Invalid('Do not combine a supplied protocol with the generated negative-control flag.')
            result=benchmark(load(args.protocol) if args.protocol else make_protocol(negative_control=args.negative_control));write_json(args.out,result)
        elif args.command in ['finite','physics','information']:
            result={'finite':finite_demo,'physics':physics_demo,'information':information_demo}[args.command]();write_json(args.out,result)
        elif args.command=='solve':
            m=FiniteModel.from_dict(load(args.model));result={'game':solve_belief(m,args.initial,args.horizon,args.budget),'quotient':quotient(m)};write_json(args.out,result)
        elif args.command=='import-v2':
            if args.ledger.exists():raise Invalid('Import requires a new dedicated ledger path.')
            result=import_hepatoscholar_v2(load(args.input),Ledger(args.ledger));write_json(args.out,result)
        else:raise Invalid('Unknown command.')
        if args.command not in ['demo','doctor','verify','chapters']:
            print(json.dumps({'status':'complete','output':str(args.out),'notice':RESEARCH_NOTICE},indent=2))
        else:print(json.dumps(result,indent=2,ensure_ascii=True,allow_nan=False))
        return 0
    except (Invalid,OSError,ValueError,TypeError,KeyError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
