"""Exact finite-model tools: constraint-aware bisimulation and belief-state games.

The guarantees concern the supplied finite transition model, never an unknown
continuous organ. Nondeterministic successors represent adversarial disturbances.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from .common import Invalid, identifier, integer, keys

@dataclass(frozen=True)
class FiniteModel:
    states: tuple[str, ...]
    actions: tuple[str, ...]
    observation: dict[str, str]
    transitions: dict[str, dict[str, tuple[str, ...]]]
    costs: dict[str, dict[str, int]]
    safe: frozenset[str]
    goal: frozenset[str]

    @classmethod
    def from_dict(cls, obj):
        required = {"states","actions","observation","transitions","costs","safe","goal"}
        keys(obj,required,required)
        if not isinstance(obj['states'],list) or not isinstance(obj['actions'],list):
            raise Invalid("States and actions must be arrays.")
        states,actions = tuple(obj['states']),tuple(obj['actions'])
        integer(len(states),"state count",1,32); integer(len(actions),"action count",1,8)
        for s in states+actions: identifier(s)
        if len(set(states)) != len(states) or len(set(actions)) != len(actions):
            raise Invalid("Duplicate state or action.")
        for name in ['observation','transitions','costs']:
            keys(obj[name],set(states),set(states))
        trans,costs = {},{}
        for s in states:
            identifier(obj['observation'][s],"observation")
            keys(obj['transitions'][s],set(actions))
            keys(obj['costs'][s],set(obj['transitions'][s]),set(obj['transitions'][s]))
            trans[s],costs[s] = {},{}
            for a, successors in obj['transitions'][s].items():
                if not isinstance(successors,list) or not successors or not set(successors) <= set(states):
                    raise Invalid("Each enabled action needs nonempty, known successors.")
                if len(set(successors)) != len(successors):
                    raise Invalid("Duplicate successor.")
                trans[s][a] = tuple(sorted(successors))
                costs[s][a] = integer(obj['costs'][s][a],"action cost",0,50)
        for name in ['safe','goal']:
            if not isinstance(obj[name],list) or not set(obj[name]) <= set(states):
                raise Invalid(f"Invalid {name} set.")
        if not set(obj['goal']) <= set(obj['safe']):
            raise Invalid("Goal states must be safe states in this contract.")
        return cls(states,actions,dict(obj['observation']),trans,costs,
                   frozenset(obj['safe']),frozenset(obj['goal']))

def quotient(model: FiniteModel, constraint_aware=True):
    """Greatest stable partition for the declared observation and task signature."""
    def label(s):
        base = (model.observation[s],)
        return base+(s in model.safe,s in model.goal) if constraint_aware else base
    groups={}
    for s in model.states:groups.setdefault(label(s),[]).append(s)
    partition=sorted(sorted(g) for g in groups.values()); trace=[partition]
    for _ in range(len(model.states)):
        block={s:i for i,g in enumerate(partition) for s in g}; groups={}
        for s in model.states:
            actions=tuple((a,model.costs[s][a] if constraint_aware else None,
                           tuple(sorted({block[t] for t in model.transitions[s][a]})))
                          for a in model.actions if a in model.transitions[s])
            groups.setdefault((label(s),actions),[]).append(s)
        new=sorted(sorted(g) for g in groups.values())
        if new==partition:
            return {"partition":partition,"refinement_trace":trace,"constraint_aware":constraint_aware,
                    "scope":"Exact stable finite bisimulation; observation, enabled actions and successor blocks preserved.",
                    "task_preservation":"safe/goal flags and action costs preserved" if constraint_aware else "NOT guaranteed"}
        partition=new;trace.append(partition)
    raise RuntimeError("Finite refinement did not stabilize.")

def solve_belief(model: FiniteModel, initial: list[str], horizon: int, budget: int):
    """Existence of ONE observation-based policy for ALL hidden states/disturbances.

    Costs are not additional observations. Charge the worst state-dependent cost
    in the current belief. Thus the guarantee uses this conservative cost budget.
    """
    integer(horizon,"horizon",0,12);integer(budget,"budget",0,50)
    if not isinstance(initial,list) or not initial or not set(initial) <= set(model.states):
        raise Invalid("Initial belief must be a nonempty set of known states.")
    initial=tuple(sorted(set(initial)))
    counter=[0]
    @lru_cache(None)
    def search(belief,remaining,fuel):
        counter[0]+=1
        if counter[0]>50000:raise Invalid("Belief search exceeded its 50,000-node work limit.")
        if not set(belief) <= model.safe:return False,{"reason":"unsafe_possible_state","belief":list(belief)}
        if remaining==0:
            good=set(belief)<=model.goal
            return good,{"terminal_goal":good,"belief":list(belief)}
        rejected=[]
        for action in model.actions:
            if any(action not in model.transitions[s] for s in belief):continue
            cost=max(model.costs[s][action] for s in belief)
            if cost>fuel:continue
            successors={t for s in belief for t in model.transitions[s][action]}
            groups={}
            for t in sorted(successors):groups.setdefault(model.observation[t],[]).append(t)
            branches={};good=True
            for obs,states in sorted(groups.items()):
                ok,policy=search(tuple(states),remaining-1,fuel-cost)
                branches[obs]=policy
                if not ok:good=False
            if good:return True,{"belief":list(belief),"action":action,"worst_step_cost":cost,"next":branches}
            rejected.append(action)
        return False,{"reason":"no_common_feasible_action","belief":list(belief),"rejected_actions":rejected}
    groups={}
    for s in initial:groups.setdefault(model.observation[s],[]).append(s)
    outcomes={obs:search(tuple(states),horizon,budget) for obs,states in sorted(groups.items())}
    return {"feasible":all(ok for ok,_ in outcomes.values()),"policy_by_initial_observation":{k:v[1] for k,v in outcomes.items()},
            "visited_belief_nodes":counter[0],"horizon":horizon,"budget":budget,
            "quantifiers":"exists one observation-based policy; for all admitted hidden states and successor choices",
            "cost_semantics":"Worst per-step cost over the belief; costs do not reveal the hidden state.",
            "scope":"Exact finite-model result only. No continuous or clinical viability certificate."}

def hidden_state_fixture(reveal=False):
    states=['A','B','G','D'];actions=['left','right']
    return FiniteModel.from_dict({
        "states":states,"actions":actions,
        "observation":{"A":"A" if reveal else "same","B":"B" if reveal else "same","G":"goal","D":"danger"},
        "transitions":{"A":{"left":["G"],"right":["D"]},"B":{"left":["D"],"right":["G"]},
                       "G":{"left":["G"],"right":["G"]},"D":{"left":["D"],"right":["D"]}},
        "costs":{s:{a:1 for a in actions} for s in states},"safe":["A","B","G"],"goal":["G"]})

def abstraction_fixture():
    return FiniteModel.from_dict({"states":["A","B"],"actions":["stay"],
        "observation":{"A":"same","B":"same"},
        "transitions":{"A":{"stay":["A"]},"B":{"stay":["B"]}},
        "costs":{"A":{"stay":0},"B":{"stay":0}},"safe":["A"],"goal":["A"]})

def finite_demo():
    model=hidden_state_fixture()
    individual={s:solve_belief(model,[s],1,1)['feasible'] for s in ['A','B']}
    return {"individually_informed_feasibility":individual,
            "hidden_belief":solve_belief(model,['A','B'],1,1),
            "with_observation":solve_belief(hidden_state_fixture(True),['A','B'],1,1),
            "observation_only_quotient":quotient(abstraction_fixture(),False),
            "task_aware_quotient":quotient(abstraction_fixture(),True)}
