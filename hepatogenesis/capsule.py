"""Deterministic experiment capsules, provenance manifests and safe verification."""
from __future__ import annotations
from dataclasses import asdict
from importlib import resources
import os
from pathlib import Path,PurePosixPath
import platform
import shutil
import tempfile
from . import __version__,RESEARCH_NOTICE
from .common import Invalid,atomic_text,digest,file_digest,load,write_csv,write_json
from .dynamics import SCENARIOS,simulate,refinement
from .evidence import lineage_demo
from .experiments import benchmark,make_protocol,information_demo,sensor_design,sensitivity
from .finite import finite_demo
from .physics import physics_demo


def source_identity():
    import hashlib
    root=resources.files('hepatogenesis'); found={}
    def visit(node,prefix=''):
        for item in sorted(node.iterdir(),key=lambda x:x.name):
            name=prefix+item.name
            if item.is_dir() and item.name!='__pycache__':visit(item,name+'/')
            elif item.is_file() and item.name.endswith(('.py','.html','.json')):
                found[name]=hashlib.sha256(item.read_bytes()).hexdigest()
    visit(root)
    return {'file_hashes':found,'aggregate_sha256':digest(found)}

def seal(root:Path):
    root=Path(root)
    entries={}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():raise Invalid('Capsules cannot contain symlinks.')
        if path.is_file() and path!=root/'manifest.json':
            entries[path.relative_to(root).as_posix()]=file_digest(path)
    record={'schema_version':1,'files':entries,'manifest_scope':'Content integrity, not authenticity or scientific validity.'}
    write_json(root/'manifest.json',record)
    return record

def verify(root:Path,expected_manifest_sha256=None):
    root=Path(root)
    manifest=root/'manifest.json'
    if root.is_symlink() or manifest.is_symlink():raise Invalid('Symlinked capsule roots or manifests are not accepted.')
    # Resolve operating-system ancestor aliases (e.g. macOS /var -> /private/var).
    # The root itself and all symlinks inside the capsule remain prohibited.
    root=root.resolve()
    manifest=root/'manifest.json'
    if expected_manifest_sha256 is not None and file_digest(manifest)!=expected_manifest_sha256:
        raise Invalid('Manifest differs from externally retained digest.')
    record=load(manifest)
    if record.get('schema_version')!=1 or not isinstance(record.get('files'),dict):raise Invalid('Unknown manifest schema.')
    expected=set(record['files'])
    if any(p.is_symlink() for p in root.rglob('*')):
        raise Invalid('Symlinked payload paths are rejected.')
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p!=manifest}
    if actual!=expected:raise Invalid(f'File set mismatch: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}')
    for name,wanted in record['files'].items():
        relative=PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts or '\\' in name or ':' in name:
            raise Invalid('Unsafe manifest path.')
        path=root.joinpath(*relative.parts)
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p!=root.parent):
            raise Invalid('Symlinked payload paths are rejected.')
        if not path.is_file() or file_digest(path)!=wanted:raise Invalid(f'Content hash mismatch: {name}')
    return {'valid':True,'files':len(expected),'manifest_sha256':file_digest(manifest),
            'scope':'Hashes require an independently trusted digest to establish external integrity.'}

def html_report(report):
    import json
    template=resources.files('hepatogenesis').joinpath('assets','report.html').read_text(encoding='utf-8')
    payload=json.dumps(report,ensure_ascii=True,allow_nan=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    return template.replace('__REPORT_DATA__',payload)

def demo(destination:Path,samples=24):
    destination=Path(destination)
    if destination.exists():raise Invalid('Output must not exist. Use a new run directory; old experiments are never silently replaced.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix='.hepatogenesis-',dir=destination.parent))
    try:
        runs={name:simulate(s) for name,s in SCENARIOS.items()}
        dynamics={name:r.packet(thin=8) for name,r in runs.items()}
        positive=make_protocol();negative=make_protocol(negative_control=True)
        result={'system':'DIKWP HepatoGenesis Lab','version':__version__,'notice':RESEARCH_NOTICE,
                'dynamics':dynamics,'refinement':{name:refinement(s) for name,s in SCENARIOS.items()},
                'benchmark':benchmark(positive),'negative_control':benchmark(negative),
                'finite':finite_demo(),'physics':physics_demo(),'information':information_demo(),
                'design':sensor_design(SCENARIOS['high_history']),'sensitivity':sensitivity(samples),
                'lineage':lineage_demo(staging/'lineage.sqlite'),
                'runtime':{'python':platform.python_version(),'implementation':platform.python_implementation()},
                'source_identity':source_identity()}
        for key in ['dynamics','refinement','benchmark','negative_control','finite','physics','information','design','sensitivity','lineage','source_identity','runtime']:
            write_json(staging/f'{key}.json',result[key])
        write_json(staging/'protocol.json',positive);write_json(staging/'negative_control_protocol.json',negative)
        for name,run in runs.items():
            rows=[{'t':t,'C':y[0],'M':y[1],'R':y[2]} for t,y in zip(run.times,run.states)]
            write_csv(staging/'trajectories'/f'{name}.csv',['t','C','M','R'],rows)
        sens=[{k:v for k,v in r.items() if k!='parameters'} for r in result['sensitivity']['rows']]
        write_csv(staging/'sensitivity.csv',['sample','low_capacity','high_capacity','difference'],sens)
        atomic_text(staging/'report.html',html_report(result))
        seal(staging);verify(staging)
        os.rename(staging,destination)
        return {'output':str(destination),'verification':verify(destination),
                'selected_model':result['benchmark']['selected_on_development'],
                'negative_control_selection':result['negative_control']['selected_on_development']}
    finally:
        if staging.exists():shutil.rmtree(staging)
