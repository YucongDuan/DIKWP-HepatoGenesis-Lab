"""Numerical contracts, invariants and independently retained book references."""
import copy
from dataclasses import replace
import json
import math
from pathlib import Path
import tempfile
import unittest
from hepatogenesis.common import Invalid, number, integer, loads, keys, canonical, write_csv, write_json, load, identifier
from hepatogenesis.dynamics import Parameters, Scenario, SCENARIOS, simulate, derivative, controls, refinement
from hepatogenesis.finite import FiniteModel, hidden_state_fixture, abstraction_fixture, quotient, solve_belief
from hepatogenesis.physics import TransportSpec, transport, thermodynamic_audit, energy_audit, field_contract
ROOT=Path(__file__).resolve().parents[1]

class DataContracts(unittest.TestCase):
    def test_nan_rejected(self):
        with self.assertRaises(Invalid):number(float('nan'),'x')
    def test_infinity_rejected(self):
        with self.assertRaises(Invalid):number(float('inf'),'x')
    def test_boolean_not_number(self):
        with self.assertRaises(Invalid):number(True,'x')
    def test_huge_integer_rejected(self):
        with self.assertRaises(Invalid):number(10**1000,'x')
    def test_number_bounds(self):
        with self.assertRaises(Invalid):number(-1,'x',0,1)
    def test_integer_type(self):
        with self.assertRaises(Invalid):integer(1.,'x')
    def test_duplicate_json(self):
        with self.assertRaises(Invalid):loads('{"x":1,"x":2}')
    def test_json_nan(self):
        with self.assertRaises(Invalid):loads('{"x":NaN}')
    def test_json_overflow(self):
        with self.assertRaises(Invalid):loads('{"x":1e999}')
    def test_json_length(self):
        with self.assertRaises(Invalid):loads('{}',max_bytes=1)
    def test_no_code_in_identifier(self):
        with self.assertRaises(Invalid):identifier('../../unsafe')
    def test_extra_keys(self):
        with self.assertRaises(Invalid):keys({'x':1},{'y'})
    def test_canonical_order(self):self.assertEqual(canonical({'z':1,'a':2}),'{"a":2,"z":1}')
    def test_canonical_nan(self):
        with self.assertRaises(Invalid):canonical({'x':float('nan')})
    def test_empty_csv_clears_previous(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.csv';write_csv(p,['x'],[{'x':1}]);write_csv(p,['x'],[])
            self.assertEqual(p.read_text().strip(),'x')
    def test_csv_formula_escape(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.csv';write_csv(p,['x'],[{'x':'=1+1'}]);self.assertIn("'=1+1",p.read_text())
    def test_csv_missing_field(self):
        with self.assertRaises(Invalid):write_csv(Path('not-created.csv'),['x'],[{'y':2}])
    def test_json_validation_precedes_write(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.json';write_json(p,{'x':1})
            with self.assertRaises(Invalid):write_json(p,{'x':float('inf')})
            self.assertEqual(load(p),{'x':1})

class Dynamics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runs={n:simulate(s) for n,s in SCENARIOS.items()}
        cls.reference=load(ROOT/'validation/book_reference.json')['scenarios']
    def test_all_six_book_endpoints(self):
        for name,run in self.runs.items():
            with self.subTest(name=name):
                for a,b in zip(run.states[-1][:3],self.reference[name]['final_state']):self.assertLess(abs(a-b),1e-8)
    def test_book_clearance_integrals(self):
        for name,run in self.runs.items():self.assertAlmostEqual(run.states[-1][3],self.reference[name]['extra_clearance'],places=8)
    def test_tiny_horizon_includes_endpoint(self):
        r=simulate(Scenario(horizon=1e-9));self.assertEqual(r.times[-1],1e-9);self.assertEqual(len(r.times),2)
    def test_includes_control_breaks(self):
        r=self.runs['high_early_repair']
        for t in (0,5,9,25,60):self.assertIn(t,r.times)
    def test_half_open_controls(self):
        s=SCENARIOS['high_early_repair'];self.assertEqual(controls(9,s), (0.,3.,1.))
    def test_no_extrapolation(self):
        with self.assertRaises(Invalid):self.runs['low_history'].at(61)
    def test_negative_time(self):
        with self.assertRaises(Invalid):self.runs['low_history'].at(-.1)
    def test_interpolated_query(self):
        y=self.runs['low_history'].at(.013);self.assertTrue(all(math.isfinite(v) for v in y))
    def test_negative_parameter(self):
        with self.assertRaises(Invalid):simulate(Scenario(),Parameters(a=-1))
    def test_bad_interval(self):
        with self.assertRaises(Invalid):simulate(Scenario(pulse_start=10,pulse_end=9))
    def test_unknown_mode(self):
        with self.assertRaises(Invalid):simulate(Scenario(),mode='new_physics')
    def test_out_of_region_initial(self):
        with self.assertRaises(Invalid):simulate(Scenario(capacity=1.1))
    def test_work_limit(self):
        with self.assertRaises(Invalid):simulate(Scenario(horizon=2000),step=.0001)
    def test_modes_are_distinguishable(self):
        finals=[simulate(SCENARIOS['high_history'],mode=m).states[-1][0] for m in ['dynamic_history','frozen_history','erased_history']]
        self.assertGreater(max(finals)-min(finals),.1)
    def test_erased_history_is_zero(self):self.assertEqual(simulate(Scenario(memory=2),mode='erased_history').states[-1][1],0)
    def test_frozen_history_stays_fixed(self):self.assertEqual(simulate(Scenario(memory=2),mode='frozen_history').states[-1][1],2)
    def test_signed_effort_different_from_clearance(self):
        early=self.runs['high_early_repair'].metrics();late=self.runs['high_late_repair'].metrics()
        self.assertEqual(early['signed_extra_multiplier_time'],late['signed_extra_multiplier_time'])
        self.assertNotAlmostEqual(early['signed_extra_clearance_integral'],late['signed_extra_clearance_integral'],places=2)
    def test_refinement(self):self.assertLess(refinement(SCENARIOS['high_history'])['maximum_terminal_difference'],1e-7)
    def test_region_all_samples(self):
        self.assertTrue(all(0<=y[0]<=1 and y[1]>=0 and 0<=y[2]<=1 for r in self.runs.values() for y in r.states))
    def test_inward_vector_field(self):
        p=Parameters()
        self.assertGreaterEqual(derivative((0,2,.5,0),p,.3,1,1)[0],0)
        self.assertLessEqual(derivative((1,2,.5,0),p,.3,1,1)[0],0)
        self.assertGreaterEqual(derivative((.5,0,.5,0),p,.3,1,1)[1],0)
    def test_metric_scope(self):self.assertIn('not a continuous-time certificate',self.runs['low_history'].metrics()['scope'])

class FiniteGames(unittest.TestCase):
    def test_singletons_feasible(self):
        for state in ['A','B']:self.assertTrue(solve_belief(hidden_state_fixture(),[state],1,1)['feasible'])
    def test_hidden_common_policy_infeasible(self):self.assertFalse(solve_belief(hidden_state_fixture(),['A','B'],1,1)['feasible'])
    def test_observation_restores_policy(self):self.assertTrue(solve_belief(hidden_state_fixture(True),['A','B'],1,1)['feasible'])
    def test_no_budget(self):self.assertFalse(solve_belief(hidden_state_fixture(),['A'],1,0)['feasible'])
    def test_unsafe_initial(self):self.assertFalse(solve_belief(hidden_state_fixture(),['D'],0,0)['feasible'])
    def test_terminal_goal(self):self.assertTrue(solve_belief(hidden_state_fixture(),['G'],0,0)['feasible'])
    def test_terminal_not_goal(self):self.assertFalse(solve_belief(hidden_state_fixture(),['A'],0,0)['feasible'])
    def test_output_quotient_merges(self):self.assertEqual(quotient(abstraction_fixture(),False)['partition'],[['A','B']])
    def test_task_quotient_splits(self):self.assertEqual(quotient(abstraction_fixture(),True)['partition'],[['A'],['B']])
    def test_excessive_horizon_rejected(self):
        with self.assertRaises(Invalid):solve_belief(hidden_state_fixture(),['A'],99,1)
    def test_unknown_state_rejected(self):
        with self.assertRaises(Invalid):solve_belief(hidden_state_fixture(),['other'],1,1)
    def test_nondeterminism_is_adversarial(self):
        m=hidden_state_fixture();m.transitions['A']['left']=('G','D')
        self.assertFalse(solve_belief(m,['A'],1,1)['feasible'])
    def test_action_availability_preserved(self):
        m=abstraction_fixture();del m.transitions['B']['stay'];del m.costs['B']['stay']
        self.assertEqual(len(quotient(m,False)['partition']),2)
    def test_costs_split_abstraction(self):
        m=abstraction_fixture();m=replace(m,safe=frozenset(['A','B']),goal=frozenset(['A','B']))
        m.costs['B']['stay']=1;self.assertEqual(len(quotient(m)['partition']),2)
    def test_invalid_transition_rejected(self):
        p=load(ROOT/'examples/hidden_state_game.json');p['transitions']['A']['left']=['unknown']
        with self.assertRaises(Invalid):FiniteModel.from_dict(p)
    def test_goal_must_be_safe(self):
        p=load(ROOT/'examples/hidden_state_game.json');p['goal']=['D']
        with self.assertRaises(Invalid):FiniteModel.from_dict(p)

class PhysicalLedgers(unittest.TestCase):
    def test_mass_conservation(self):self.assertLess(abs(transport()['mass_ledger_mmol']['residual']),1e-10)
    def test_profiles_nonnegative(self):self.assertGreaterEqual(min(transport()['final_profile_mmol_per_L']),0)
    def test_closed_system(self):
        x=transport(TransportSpec(flow_L_per_h=0,reaction_per_h=0),initial=[1.]*24)
        self.assertAlmostEqual(x['mass_ledger_mmol']['initial'],x['mass_ledger_mmol']['final'],places=12)
    def test_zones_change_outlet(self):
        a=transport()['final_profile_mmol_per_L'][-1];b=transport(TransportSpec(cells=1))['final_profile_mmol_per_L'][-1]
        self.assertGreater(abs(a-b),.1)
    def test_adaptive_positivity_step(self):
        r=transport(TransportSpec(step_h=.5,horizon_h=.5));self.assertLess(r['effective_step_h'],.5)
    def test_invalid_cell_count(self):
        with self.assertRaises(Invalid):transport(TransportSpec(cells=0))
    def test_invalid_profile(self):
        with self.assertRaises(Invalid):transport(initial=[1])
    def test_forward_thermodynamics(self):self.assertTrue(thermodynamic_audit(310,-1000,1,.001)['uncoupled_direction_consistent'])
    def test_wrong_uncoupled_direction(self):self.assertFalse(thermodynamic_audit(310,1000,1,.001)['uncoupled_direction_consistent'])
    def test_thermodynamic_overflow_rejected(self):
        with self.assertRaises(Invalid):thermodynamic_audit(310,1e308,1,1e308)
    def test_energy_overflow_rejected(self):
        with self.assertRaises(Invalid):energy_audit(0,1e308,1e308,0,0)
    def test_zero_reaction_quotient_rejected(self):
        with self.assertRaises(Invalid):thermodynamic_audit(310,0,0,1)
    def test_energy_balance(self):self.assertTrue(energy_audit(10,2,3,4,1)['balanced'])
    def test_energy_imbalance(self):self.assertFalse(energy_audit(10,2,3,4,2)['balanced'])
    def test_field_proposal_not_confirmed(self):self.assertFalse(field_contract(load(ROOT/'examples/field_hypothesis.json'))['empirically_confirmed'])
    def test_field_cannot_self_certify(self):
        p=load(ROOT/'examples/field_hypothesis.json');p['status']='proven'
        with self.assertRaises(Invalid):field_contract(p)
