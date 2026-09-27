"""Transport and thermodynamic ledgers. These are explicit teaching models.

The chapter-18 dimensionless reserve is NOT converted to joules, ATP or entropy.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
import math
from .common import Invalid,integer,number

@dataclass(frozen=True)
class TransportSpec:
    cells: int = 24
    volume_L: float = 1.
    flow_L_per_h: float = .6
    mixing_L_per_h: float = .04
    inlet_mmol_per_L: float = 1.
    reaction_per_h: float = .8
    horizon_h: float = 8.
    step_h: float = .005

    def validate(self):
        integer(self.cells,'cells',1,128)
        for k,v in asdict(self).items():
            if k!='cells':number(v,k,0.,100.)
        if self.volume_L<=0 or self.step_h<=0 or self.horizon_h<=0:
            raise Invalid("Volume, step and horizon must be positive.")
        if self.horizon_h/self.step_h>200000:
            raise Invalid("Transport work limit exceeded.")

def transport(spec:TransportSpec=TransportSpec(), initial=None, reaction_factors=None):
    spec.validate();n=spec.cells;V=spec.volume_L/n
    c=list(initial if initial is not None else [0.]*n)
    factors=list(reaction_factors if reaction_factors is not None else [1.]*n)
    if len(c)!=n or len(factors)!=n:raise Invalid("Initial profile and reaction factors must match the cell count.")
    for x in c+factors:number(x,'profile value',0.,100.)
    rates=[spec.reaction_per_h*f for f in factors]
    q,D=spec.flow_L_per_h,spec.mixing_L_per_h
    # Conservative positivity restriction, also valid at the one-cell boundary.
    rate=q/V+2*D/V+max(rates)
    allowed=.8/rate if rate>0 else spec.step_h
    dt=min(spec.step_h,allowed)
    count=math.ceil(spec.horizon_h/dt)
    if count*n>4_000_000:raise Invalid("Transport cell-update limit exceeded.")
    dt=spec.horizon_h/count
    initial_mass=sum(c)*V;incoming=outgoing=reacted=0.;profile=[]
    for j in range(count):
        flux=[q*spec.inlet_mmol_per_L]+[q*c[i-1]+D*(c[i-1]-c[i]) for i in range(1,n)]+[q*c[-1]]
        consumed=[rates[i]*V*c[i] for i in range(n)]
        nxt=[c[i]+dt*(flux[i]-flux[i+1]-consumed[i])/V for i in range(n)]
        if not all(math.isfinite(x) and x>=-1e-12 for x in nxt):
            raise Invalid("Transport positivity failed; no clipping is allowed.")
        incoming+=dt*flux[0];outgoing+=dt*flux[-1];reacted+=dt*sum(consumed)
        c=nxt
        if j%max(1,count//100)==0 or j==count-1:
            profile.append({'time_h':(j+1)*dt,'mean_mmol_per_L':sum(c)/n,'outlet_mmol_per_L':c[-1]})
    final_mass=sum(c)*V;residual=final_mass-initial_mass-incoming+outgoing+reacted
    return {'specification':asdict(spec),'effective_step_h':dt,'final_profile_mmol_per_L':c,
            'mass_ledger_mmol':{'initial':initial_mass,'input':incoming,'output':outgoing,
                                'reacted':reacted,'final':final_mass,'residual':residual},
            'trace':profile,'method':'positive finite-volume upwind advection, neighbor exchange, first-order reaction',
            'scope':'Synthetic chain, not anatomical reconstruction or calibrated liver perfusion.'}

def thermodynamic_audit(temperature_K:float, delta_g0_J_per_mol:float,
                        reaction_quotient:float, flux_mol_per_s:float):
    T=number(temperature_K,'temperature_K',1.,10000.)
    dg0=number(delta_g0_J_per_mol,'delta_g0_J_per_mol')
    Q=number(reaction_quotient,'reaction_quotient',1e-100,1e100)
    v=number(flux_mol_per_s,'flux_mol_per_s')
    dg=number(dg0+8.314462618*T*math.log(Q),"computed delta_g")
    production=number(-v*(dg/T),"computed entropy production")
    return {'delta_g_J_per_mol':dg,'entropy_production_J_per_K_s':production,
            'uncoupled_direction_consistent':production>=-1e-12,
            'scope':'Single isothermal uncoupled reaction with dimensionless activities; coupled networks require a joint ledger.'}

def energy_audit(input_W:float, output_W:float, work_W:float, heat_loss_W:float, storage_rate_W:float):
    values=[number(v,n) for v,n in zip([input_W,output_W,work_W,heat_loss_W,storage_rate_W],
                                      ['input_W','output_W','work_W','heat_loss_W','storage_rate_W'])]
    residual=number(values[0]-sum(values[1:]),"computed energy residual")
    return {'residual_W':residual,'balanced':abs(residual)<=1e-9,
            'scope':'Declared first-law boundary balance; no inference about biological function or moral value.'}

def field_contract(packet):
    from .common import keys,text
    required={'name','degrees_of_freedom','units','evolution_equation','coupling','observable',
              'null_model','discriminating_prediction','failure_condition','status'}
    keys(packet,required,required)
    for key in required:text(packet[key],key)
    if packet['status']!='hypothesis':
        raise Invalid("New-field contracts enter as hypotheses, not established physics.")
    return {'well_formed':True,'status':'hypothesis','empirically_confirmed':False,
            'scope':'Completeness of a proposal, not evidence that a new physical field exists.'}

def physics_demo():
    zoned=transport();well_mixed=transport(TransportSpec(cells=1))
    return {'zoned':zoned,'well_mixed':well_mixed,
            'outlet_difference_mmol_per_L':well_mixed['final_profile_mmol_per_L'][-1]-zoned['final_profile_mmol_per_L'][-1],
            'consistent_reaction':thermodynamic_audit(310.,-5000.,1.,.001),
            'inconsistent_uncoupled_reaction':thermodynamic_audit(310.,5000.,1.,.001),
            'balanced_energy':energy_audit(10.,2.,3.,4.,1.),
            'unbalanced_energy':energy_audit(10.,2.,3.,4.,3.)}
