"""Append-only research lineage with explicit scope and correction propagation.

Hash chains detect modifications relative to a trusted head. They do not prevent
an administrator from rewriting the whole store or authenticate scientific truth.
"""
from __future__ import annotations
from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3
from .common import Invalid,canonical,digest,identifier,keys,text

LAYERS={'D','I','K','W','P'}
KINDS={'source','model','experiment','result','claim','decision'}

class Ledger:
    def __init__(self,path:Path):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self._connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY, payload TEXT NOT NULL, previous TEXT NOT NULL, hash TEXT NOT NULL)')

    @contextmanager
    def _connect(self):
        # sqlite3's context manager commits or rolls back but does not close.
        # Close deterministically so Windows can release and move ledger files.
        db=sqlite3.connect(self.path,timeout=5.)
        try:
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def _read(db,expected_head=None):
        rows=db.execute('SELECT seq,payload,previous,hash FROM events ORDER BY seq').fetchall()
        previous='0'*64;events=[]
        for expected,(seq,raw,prev,h) in enumerate(rows,1):
            if seq!=expected or prev!=previous:raise Invalid('Ledger chain is discontinuous.')
            try:payload=json.loads(raw)
            except json.JSONDecodeError as exc:raise Invalid('Invalid event JSON.') from exc
            if raw!=canonical(payload):raise Invalid('Noncanonical stored payload.')
            calculated=digest({'seq':seq,'payload':payload,'previous':prev})
            if h!=calculated:raise Invalid('Ledger hash mismatch.')
            previous=h;events.append({'seq':seq,'payload':payload,'previous':prev,'hash':h})
        if expected_head is not None and expected_head!=previous:
            raise Invalid('Ledger head differs from the independently retained head.')
        return events,previous

    def verify(self,expected_head=None):
        with self._connect() as db:events,head=self._read(db,expected_head)
        return {'valid':True,'events':len(events),'head':head,
                'scope':'Integrity relative to the retained head, not identity authentication or truth.'}

    @staticmethod
    def _project(events):
        nodes={}
        for entry in events:
            payload=entry['payload'];kind=payload['type']
            if kind=='add':
                node=dict(payload['node']);node['status']='unreviewed'
                if any(nodes[d]['status'] in {'invalidated','review_required'} or
                       not scope_compatible(nodes[d]['scope'],node['scope'])['compatible']
                       for d in node['depends_on']):
                    node['status']='review_required'
                nodes[node['id']]=node
            elif kind=='review':
                node=nodes[payload['id']]
                node['status']='reviewed_within_declared_scope';node['reviewer']=payload['reviewer']
            elif kind=='invalidate':
                root=payload['id'];nodes[root]['status']='invalidated';nodes[root]['reason']=payload['reason']
                affected={root}
                changed=True
                while changed:
                    changed=False
                    for name,node in nodes.items():
                        if name not in affected and set(node['depends_on'])&affected:
                            node['status']='review_required';affected.add(name);changed=True
        return nodes

    def project(self):
        with self._connect() as db:events,_=self._read(db)
        return self._project(events)

    def _append(self,payload,check):
        with self._connect() as db:
            db.execute('BEGIN IMMEDIATE')
            events,previous=self._read(db);nodes=self._project(events)
            check(nodes)
            seq=len(events)+1;h=digest({'seq':seq,'payload':payload,'previous':previous})
            db.execute('INSERT INTO events VALUES (?,?,?,?)',(seq,canonical(payload),previous,h))
        return h

    def add(self,node):
        required={'id','kind','layer','statement','depends_on','scope'}
        keys(node,required|{'external_annotation'},required)
        identifier(node['id']);text(node['statement'],'statement')
        if node['kind'] not in KINDS or node['layer'] not in LAYERS:raise Invalid('Invalid node kind or DIKWP layer.')
        if not isinstance(node['depends_on'],list) or len(set(node['depends_on']))!=len(node['depends_on']):
            raise Invalid('Dependencies must be a unique list.')
        for dep in node['depends_on']:identifier(dep)
        scope_keys={'species','data_kind','units','claim_strength'}
        keys(node['scope'],scope_keys,scope_keys)
        for k,v in node['scope'].items():text(v,k,300)
        if node['scope']['claim_strength'] not in {'hypothesis','simulation','reported_evidence','derived_under_assumptions'}:
            raise Invalid('Unsupported claim strength.')
        if node['scope']['data_kind']=='synthetic' and node['scope']['claim_strength']=='reported_evidence':
            raise Invalid('Synthetic data cannot be imported as empirical evidence.')
        def check(nodes):
            if node['id'] in nodes:raise Invalid('Node ids are immutable; create a new version id.')
            if any(dep not in nodes for dep in node['depends_on']):raise Invalid('Dependencies must already exist; forward references and cycles are rejected.')
        return self._append({'type':'add','node':node},check)

    def review(self,node_id,reviewer):
        identifier(node_id);text(reviewer,'reviewer',120)
        def check(nodes):
            if node_id not in nodes:raise Invalid('Unknown node.')
            node=nodes[node_id]
            if node['status'] in {'invalidated','review_required'}:raise Invalid('Correct affected evidence with a new version before reviewing it.')
            if any(nodes[d]['status'] in {'invalidated','review_required'} for d in node['depends_on']):
                raise Invalid('An invalid dependency blocks review.')
        return self._append({'type':'review','id':node_id,'reviewer':reviewer},check)

    def invalidate(self,node_id,reason):
        identifier(node_id);text(reason,'reason',1000)
        def check(nodes):
            if node_id not in nodes:raise Invalid('Unknown node.')
        return self._append({'type':'invalidate','id':node_id,'reason':reason},check)

    def export(self):
        with self._connect() as db:events,head=self._read(db)
        return {'head':head,'events':events,'nodes':self._project(events),
                'scope':'Local research lineage; reviewer names are assertions, not verified identities.'}

def scope_compatible(source_scope,target_scope):
    """Conservative exact contract matching; no automatic species/units transfer."""
    dimensions=['species','data_kind','units']
    mismatches=[k for k in dimensions if k not in source_scope or k not in target_scope or source_scope[k]!=target_scope[k]]
    return {'compatible':not mismatches,'mismatched_dimensions':mismatches,
            'scope':'Matching declared scope is necessary here, not sufficient evidence of truth.'}

def import_hepatoscholar_v2(packet,ledger:Ledger):
    """File adapter for the inspected V2 scenario/records contract; no live API."""
    if not isinstance(packet,dict) or not isinstance(packet.get('scenarios'),list):
        raise Invalid('Expected a V2 object containing scenarios.')
    plans=[];seen=set()
    for scenario in packet['scenarios']:
        identifier(scenario.get('id'),'scenario.id')
        records=scenario.get('records')
        if not isinstance(records,list):raise Invalid('V2 records must be an array.')
        for record in records:
            identifier(record.get('id'),'record.id')
            if record.get('source_type')!='SYNTHETIC_DEMO':
                raise Invalid('This adapter accepts synthetic V2 fixtures only; empirical intake needs a separate reviewed scope contract.')
            node_id=identifier(scenario['id']+'.'+record['id'])
            if node_id in seen:raise Invalid('Duplicate imported record id.')
            seen.add(node_id)
            for field in ['title','population','results','limitations']:text(record.get(field),field)
            plans.append({'id':node_id,'kind':'source','layer':'D','statement':record['title'],
                          'depends_on':[],
                          'scope':{'species':record['population'],'data_kind':'synthetic','units':'not_declared','claim_strength':'hypothesis'},
                          'external_annotation':{'upstream_quality':record.get('quality'),
                                                 'interpretation':'Uncalibrated upstream annotation; not a probability, proof or admission criterion.'}})
    # Validate all input before appending. A concurrent writer can still cause a
    # later id conflict; the CLI creates a fresh dedicated ledger for each import.
    existing=ledger.project()
    if any(n['id'] in existing for n in plans):raise Invalid('Imported ids already exist.')
    for node in plans:canonical(node)
    for node in plans:ledger.add(node)
    return {'imported':len(plans),'mapping':'V2 synthetic records to D-layer source nodes','no_quality_score_promotion':True}

def lineage_demo(path):
    ledger=Ledger(path)
    if ledger.verify()['events']!=0:raise Invalid('Lineage demo requires an empty ledger.')
    scope={'species':'synthetic_system','data_kind':'synthetic','units':'dimensionless','claim_strength':'simulation'}
    nodes=[('source-v1','source','D',[],'Synthetic observation record.'),
           ('model-v1','model','K',['source-v1'],'History-conditioned model contract.'),
           ('result-v1','result','I',['model-v1'],'Computed result within a declared horizon.'),
           ('claim-v1','claim','W',['result-v1'],'A scoped comparison, not a patient conclusion.'),
           ('experiment-v1','experiment','P',['claim-v1'],'A proposed discriminating follow-up experiment.')]
    for id,kind,layer,deps,statement in nodes:
        ledger.add({'id':id,'kind':kind,'layer':layer,'statement':statement,'depends_on':deps,'scope':scope})
    before=ledger.export()
    ledger.invalidate('source-v1','Synthetic correction exercise: source provenance failed.')
    return {'before':before,'after':ledger.export(),'review_required_count':sum(n['status']=='review_required' for n in ledger.project().values())}
