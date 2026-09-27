"""Predeclared synthetic model discrimination, observation design and sensitivity.

Trajectories, not individual time points, are evaluation units. Public synthetic
holdouts are reproducibility fixtures, not independent biological validation.
"""
from __future__ import annotations
from dataclasses import asdict,replace
from itertools import combinations
import math
import random
import statistics
from .common import Invalid,digest,integer,number
from .dynamics import MODES,Parameters,Scenario,SCENARIOS,simulate

def make_protocol(seed=1729,negative_control=False):
    integer(seed,'seed',0,2**32-1)
    rng=random.Random(seed)
    p=Parameters(c=0.,d=0.) if negative_control else Parameters()
    specs=[('train',.05,5.,.30,30.),('train',1.6,5.,.30,30.),('train',.9,8.,.25,30.),
           ('development',.35,6.,.25,40.),('development',1.3,12.,.20,40.),
           ('audit',.15,10.,.35,60.),('audit',1.1,20.,.25,60.),('audit',1.8,25.,.30,60.)]
    trials=[]
    for i,(split,m,start,height,horizon) in enumerate(specs):
        s=Scenario(name=f'group_{i}',memory=0. if negative_control else m,pulse_start=start,
                   pulse_end=start+4,pulse_height=height,horizon=horizon)
        truth=simulate(s,p,step=.02)
        obs=[]
        for j in range(1,13):
            t=horizon*j/12;y=truth.at(t)
            obs.append({'t':t,'C':y[0]+rng.gauss(0.,.002),'R':y[2]+rng.gauss(0.,.002)})
        trials.append({'group_id':s.name,'split':split,'scenario':asdict(s),'observations':obs})
    return {'version':1,'data_kind':'synthetic','seed':seed,
            'negative_control':negative_control,'parameters_except_q':asdict(p),
            'q_grid':[.05,.1,.15,.2,.25],'selection_penalty_per_state':.00002,
            'channel_noise_standard_deviation':.002,'trials':trials,
            'generator_disclosure':'dynamic_history generates all observations; in the negative control M stays zero and all three hypotheses coincide.'}

def validate_protocol(protocol):
    from .common import keys
    expected={'version','data_kind','seed','negative_control','parameters_except_q','q_grid',
              'selection_penalty_per_state','channel_noise_standard_deviation','trials','generator_disclosure'}
    keys(protocol,expected,expected)
    if protocol['version']!=1 or protocol['data_kind']!='synthetic' or type(protocol['negative_control']) is not bool:
        raise Invalid("Only version-1 synthetic protocols are accepted by this benchmark.")
    Parameters.from_dict(protocol['parameters_except_q'])
    grid=protocol['q_grid']
    if not isinstance(grid,list) or not 1<=len(grid)<=20:raise Invalid('q_grid needs 1-20 entries.')
    for q in grid:number(q,'q',0.,1.)
    number(protocol['selection_penalty_per_state'],'penalty',0.,1.)
    number(protocol['channel_noise_standard_deviation'],'noise',1e-12,1.)
    from .common import identifier
    integer(protocol['seed'],'seed',0,2**32-1)
    trials=protocol['trials']
    if not isinstance(trials,list):raise Invalid('Trials must be an array.')
    integer(len(trials),'trial count',3,30)
    ids=set();splits=set(); fingerprints={}
    for trial in trials:
        keys(trial,{'group_id','split','scenario','observations'},{'group_id','split','scenario','observations'})
        identifier(trial['group_id'],'group_id')
        if trial['group_id'] in ids:raise Invalid('A trajectory group cannot appear in multiple splits.')
        ids.add(trial['group_id'])
        if trial['split'] not in {'train','development','audit'}:raise Invalid('Unknown split.')
        splits.add(trial['split'])
        s=Scenario.from_dict(trial['scenario'])
        if s.horizon>100:raise Invalid('Benchmark scenario horizon exceeds 100.')
        payload=dict(trial['scenario']);payload.pop('name',None)
        fingerprint=digest(payload)
        if fingerprint in fingerprints and fingerprints[fingerprint]!=trial['split']:
            raise Invalid('A generating scenario is reused across data splits.')
        fingerprints[fingerprint]=trial['split']
        if not isinstance(trial['observations'],list) or not 1<=len(trial['observations'])<=100:
            raise Invalid('Each trajectory needs 1-100 observations.')
        previous=-1.
        for obs in trial['observations']:
            keys(obs,{'t','C','R'},{'t','C','R'})
            t=number(obs['t'],'time',0.,s.horizon)
            if t<=previous:raise Invalid('Observation times must be strictly increasing.')
            previous=t
            for channel in ['C','R']:number(obs[channel],channel,-.5,1.5)
    if splits != {'train','development','audit'}:raise Invalid('All three data splits are required.')

def trajectory_losses(trials,mode,p):
    result={}
    for trial in trials:
        run=simulate(Scenario.from_dict(trial['scenario']),p,mode,step=.05)
        errors=[]
        for obs in trial['observations']:
            y=run.at(obs['t']); errors.extend([(y[0]-obs['C'])**2,(y[2]-obs['R'])**2])
        result[trial['group_id']]=statistics.fmean(errors)
    return result

def benchmark(protocol):
    validate_protocol(protocol)
    splits={k:[t for t in protocol['trials'] if t['split']==k] for k in ['train','development','audit']}
    base=Parameters.from_dict(protocol['parameters_except_q'])
    rows=[]
    for mode in MODES:
        grid=[base.q] if mode=='erased_history' else protocol['q_grid']
        fits=[]
        for q in grid:
            loss=trajectory_losses(splits['train'],mode,replace(base,q=q))
            fits.append((statistics.fmean(loss.values()),q))
        train_loss,q=min(fits)
        frozen=replace(base,q=q)
        development=trajectory_losses(splits['development'],mode,frozen)
        complexity=2 if mode=='erased_history' else 3
        score=statistics.fmean(development.values())+protocol['selection_penalty_per_state']*complexity
        rows.append({'model':mode,'fitted_q':q,'train_mse':train_loss,
                     'development_group_mse':development,'development_selection_score':score,
                     'state_count_penalty':complexity,'frozen_parameters':asdict(frozen)})
    # Freeze selection before computing any audit loss.
    selected=min(rows,key=lambda x:(x['development_selection_score'],x['model']))['model']
    freeze=digest({'selection':selected,'rows':rows,'train':splits['train'],'development':splits['development']})
    for row in rows:
        audit=trajectory_losses(splits['audit'],row['model'],Parameters(**row['frozen_parameters']))
        row['audit_group_mse']=audit;row['audit_mean_mse']=statistics.fmean(audit.values())
        row['audit_worst_group_mse']=max(audit.values())
    return {'protocol_sha256':digest(protocol),'selection_freeze_sha256':freeze,
            'selected_on_development':selected,'negative_control':protocol['negative_control'],
            'split_counts':{k:len(v) for k,v in splits.items()},'models':rows,
            'units':'squared dimensionless observation units','evaluation_unit':'whole trajectory, equally weighted',
            'complexity_semantics':'Penalty counts retained coordinates: three for dynamic/frozen history, two when M is erased. This is a declared representation cost, not the number of evolving degrees of freedom.',
            'scope':'Finite synthetic benchmark; generator is disclosed and favors dynamic history outside the negative control. No external generalization claim.'}

def sensor_design(s:Scenario,noise=.01):
    number(noise,'noise',1e-6,1.)
    runs={m:simulate(s,mode=m,step=.05) for m in MODES}
    rows=[]
    for t in sorted({0.,s.horizon/6,s.horizon/3,s.horizon/2,s.horizon*2/3,s.horizon}):
        for channels in [(0,),(2,),(0,2)]:
            predictions={m:[r.at(t)[i] for i in channels] for m,r in runs.items()}
            distances=[sum(((predictions[a][i]-predictions[b][i])/noise)**2 for i in range(len(channels)))
                       for a,b in combinations(MODES,2)]
            cost=len(channels)
            rows.append({'time':t,'channels':[['C','M','R'][i] for i in channels],
                         'min_pair_standardized_distance_squared':min(distances),'cost_proxy':cost,
                         'score_per_cost':min(distances)/cost,'predictions':predictions})
    best=max(rows,key=lambda x:x['score_per_cost'])
    return {'candidate_designs':rows,'selected':best,'noise_assumption':noise,
            'scope':'Finite model-separation design under common independent noise; no causal proof or clinical test recommendation.'}

def sensitivity(samples=24,seed=20260926):
    integer(samples,'samples',0,128);integer(seed,'seed',0,2**32-1)
    rng=random.Random(seed);rows=[]
    for i in range(samples):
        p=Parameters(**{k:v*rng.uniform(.8,1.2) for k,v in asdict(Parameters()).items()})
        low=simulate(SCENARIOS['low_history'],p,step=.05).states[-1][0]
        high=simulate(SCENARIOS['high_history'],p,step=.05).states[-1][0]
        rows.append({'sample':i,'low_capacity':low,'high_capacity':high,'difference':low-high,'parameters':asdict(p)})
    return {'seed':seed,'samples':samples,'rows':rows,'positive_count':sum(r['difference']>0 for r in rows),
            'scope':'Finite independent-uniform parameter perturbations, not a posterior or patient probability.'}

def mutual_information(joint):
    if not isinstance(joint,list) or not joint or not isinstance(joint[0],list) or not joint[0]:
        raise Invalid('Nonempty probability matrix required.')
    width=len(joint[0])
    if any(not isinstance(row,list) or len(row)!=width for row in joint):raise Invalid('Ragged joint matrix.')
    for row in joint:
        for p in row:number(p,'probability',0.,1.)
    if abs(sum(map(sum,joint))-1)>1e-10:raise Invalid('Joint probabilities must sum to one.')
    px=list(map(sum,joint));py=[sum(row[j] for row in joint) for j in range(width)]
    return sum(p*(math.log2(p)-math.log2(px[i])-math.log2(py[j])) for i,row in enumerate(joint) for j,p in enumerate(row) if p>0)

def information_demo():
    aligned=[[.5,0.],[0.,.5]];inverted=[[0.,.5],[.5,0.]]
    return {'aligned_mutual_information_bits':mutual_information(aligned),
            'inverted_mutual_information_bits':mutual_information(inverted),
            'identity_decoder_accuracy_aligned':1.,'identity_decoder_accuracy_inverted':0.,
            'scope':'Two exactly specified binary distributions; information quantity alone does not choose a task decoder.'}
