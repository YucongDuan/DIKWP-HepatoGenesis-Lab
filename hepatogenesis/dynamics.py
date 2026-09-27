"""Chapter 18 model, independently implemented with segmented fixed-step RK4.

C: relative capacity; M: structural burden; R: reserve. All are dimensionless.
No state clipping and no medical interpretation of parameters or thresholds.
"""
from __future__ import annotations
from bisect import bisect_left
from dataclasses import asdict, dataclass, fields, replace
import math
from .common import Invalid, identifier, keys, number

MODES = ("dynamic_history", "frozen_history", "erased_history")

@dataclass(frozen=True)
class Parameters:
    a: float = .45
    b: float = .70
    q: float = .15
    c: float = .50
    d: float = .12
    e: float = .08
    f: float = .25
    g: float = .20
    h: float = .10

    def validate(self):
        for k, v in asdict(self).items():
            number(v, k, 0., 100.)

    @classmethod
    def from_dict(cls, data):
        keys(data, {f.name for f in fields(cls)})
        p = cls(**data)
        p.validate()
        return p

@dataclass(frozen=True)
class Scenario:
    name: str = "low_history"
    memory: float = .05
    capacity: float = .8
    reserve: float = .8
    pulse_start: float = 5.
    pulse_end: float = 9.
    pulse_height: float = .30
    repair_start: float = 0.
    repair_end: float = 0.
    repair_multiplier: float = 1.
    support: float = 1.
    horizon: float = 60.

    def validate(self):
        identifier(self.name, "scenario.name")
        for k, v in asdict(self).items():
            if k != "name":
                number(v, k, 0., 2000.)
        number(self.capacity, "capacity", 0, 1)
        number(self.reserve, "reserve", 0, 1)
        if self.horizon <= 0:
            raise Invalid("Horizon must be positive.")
        if self.pulse_end < self.pulse_start or self.repair_end < self.repair_start:
            raise Invalid("Control intervals must be ordered.")

    @classmethod
    def from_dict(cls, data):
        keys(data, {f.name for f in fields(cls)})
        s = cls(**data)
        s.validate()
        return s

SCENARIOS = {
    s.name: s for s in [Scenario(), Scenario("middle_history", memory=.9),
        Scenario("high_history", memory=1.6),
        Scenario("high_early_repair", memory=1.6, repair_start=9., repair_end=25., repair_multiplier=3.),
        Scenario("high_late_repair", memory=1.6, repair_start=35., repair_end=51., repair_multiplier=3.),
        Scenario("high_delayed_pulse", memory=1.6, pulse_start=25., pulse_end=29.)]
}

def controls(t: float, s: Scenario) -> tuple[float, float, float]:
    return (s.pulse_height if s.pulse_start <= t < s.pulse_end else 0.,
            s.repair_multiplier if s.repair_start <= t < s.repair_end else 1., s.support)

def derivative(y, p: Parameters, u: float, k: float, support: float, mode="dynamic_history"):
    C, M, R = y[:3]
    m = 0. if mode == "erased_history" else M
    dC = p.a * R * (1. - C) / (1. + m) - p.b * (u + p.q * m) * C
    dM = p.c * u * C + p.d * (1. - C) - k * p.e * R * M if mode == "dynamic_history" else 0.
    dR = p.f * support * (1. - R) - p.g * (1. - C) * R - p.h * u * R
    extra_clearance = (k - 1.) * p.e * R * m
    return dC, dM, dR, extra_clearance

def rk4(y, dt, fun):
    k1 = fun(y)
    k2 = fun(tuple(a + dt*b/2 for a, b in zip(y, k1)))
    k3 = fun(tuple(a + dt*b/2 for a, b in zip(y, k2)))
    k4 = fun(tuple(a + dt*b for a, b in zip(y, k3)))
    return tuple(a + dt*(b + 2*c + 2*d + e)/6 for a,b,c,d,e in zip(y,k1,k2,k3,k4))

@dataclass
class Trajectory:
    scenario: Scenario
    parameters: Parameters
    mode: str
    times: list[float]
    states: list[tuple[float, ...]]
    max_step: float
    load_integral: float
    effort_integral: float

    def at(self, time: float):
        number(time, "query time")
        if time < 0 or time > self.scenario.horizon:
            raise Invalid("Cannot extrapolate outside the simulated interval.")
        j = bisect_left(self.times, time)
        if j == 0 or self.times[j] == time:
            return self.states[j][:3]
        left, right = self.times[j-1], self.times[j]
        alpha = (time-left)/(right-left)
        return tuple((1-alpha)*a + alpha*b for a,b in zip(self.states[j-1][:3], self.states[j][:3]))

    def metrics(self, floor=.45, terminal=.85):
        number(floor, "capacity floor", 0., 1.)
        number(terminal, "terminal target", 0., 1.)
        i = min(range(len(self.states)), key=lambda j:self.states[j][0])
        C, M, R = self.states[-1][:3]
        return {"final_capacity": C, "final_memory": M, "final_reserve": R,
                "minimum_sampled_capacity":self.states[i][0], "time_of_sampled_minimum":self.times[i],
                "sampled_path_and_terminal_pass": self.states[i][0] >= floor and C >= terminal,
                "teaching_thresholds": {"capacity_floor":floor, "terminal_capacity":terminal},
                "load_integral":self.load_integral, "signed_extra_multiplier_time":self.effort_integral,
                "signed_extra_clearance_integral":self.states[-1][3],
                "clearance_semantics":"Removal contribution to the dynamic burden equation." if self.mode=="dynamic_history" else "Diagnostic rate only: countermodel burden does not evolve by this rate.",
                "scope":"Numerical sample check; not a continuous-time certificate or clinical threshold."}

    def packet(self, thin: int = 1):
        if type(thin) is not int or thin < 1:
            raise Invalid("thin must be a positive integer.")
        ii = sorted(set(range(0,len(self.times),thin)) | {len(self.times)-1})
        return {"scenario":asdict(self.scenario), "parameters":asdict(self.parameters), "model":self.mode,
                "units":"dimensionless", "method":"segmented fixed-step RK4", "max_step":self.max_step,
                "metrics":self.metrics(),
                "trajectory":[{"t":self.times[i],"C":self.states[i][0],"M":self.states[i][1],"R":self.states[i][2]}
                              for i in ii]}

def simulate(s: Scenario, p: Parameters | None = None, mode="dynamic_history", step=.025) -> Trajectory:
    p = p or Parameters()
    s.validate(); p.validate(); number(step,"step",1e-5,.2)
    if mode not in MODES:
        raise Invalid(f"Unknown model: {mode}")
    if s.horizon / step > 200_000:
        raise Invalid("Integration exceeds the 200,000-step work limit.")
    breaks = sorted({0., s.horizon} | {t for t in [s.pulse_start,s.pulse_end,s.repair_start,s.repair_end]
                                     if 0 < t < s.horizon})
    y = (s.capacity, 0. if mode == "erased_history" else s.memory, s.reserve, 0.)
    ts, ys = [0.], [y]
    load = effort = 0.
    for left,right in zip(breaks,breaks[1:]):
        u,k,S = controls((left+right)/2,s)
        n = max(1, math.ceil((right-left)/step))
        dt = (right-left)/n
        load += u*(right-left); effort += (k-1)*(right-left)
        for j in range(1,n+1):
            try:
                y = rk4(y,dt,lambda state:derivative(state,p,u,k,S,mode))
            except (OverflowError, ZeroDivisionError) as exc:
                raise Invalid("Numerical integration failed; reduce the step or revise the model.") from exc
            if (not all(math.isfinite(v) for v in y) or
                not (-1e-9 <= y[0] <= 1+1e-9 and y[1] >= -1e-9 and -1e-9 <= y[2] <= 1+1e-9)):
                raise Invalid("Invariant-region check failed; no state clipping was applied.")
            ts.append(right if j == n else left+j*dt); ys.append(y)
    return Trajectory(s,p,mode,ts,ys,step,load,effort)

def compare_models(s: Scenario, p: Parameters | None = None, step=.025):
    return {mode:simulate(s,p,mode,step).packet(thin=8) for mode in MODES}

def refinement(s: Scenario, p: Parameters | None = None, step=.05):
    coarse = simulate(s,p,step=step)
    fine = simulate(s,p,step=step/2)
    error = max(abs(a-b) for a,b in zip(coarse.states[-1],fine.states[-1]))
    return {"coarse_step":step,"fine_step":step/2,"maximum_terminal_difference":error,
            "scope":"Step-refinement diagnostic, not a rigorous global error bound."}
