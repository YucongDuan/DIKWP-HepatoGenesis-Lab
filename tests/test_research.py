"""Whole-trajectory evaluation, correction propagation and bounded interfaces."""
import copy
import http.client
import json
from pathlib import Path
import sqlite3
from contextlib import closing
import tempfile
import threading
import unittest
from hepatogenesis.common import Invalid,canonical,load,write_json,file_digest
from hepatogenesis.experiments import make_protocol,benchmark,validate_protocol,sensor_design,sensitivity,mutual_information,information_demo
from hepatogenesis.dynamics import SCENARIOS
from hepatogenesis.evidence import Ledger,lineage_demo,scope_compatible,import_hepatoscholar_v2
from hepatogenesis.capsule import seal,verify,html_report,source_identity,demo
from hepatogenesis.server import Console
ROOT=Path(__file__).resolve().parents[1]

class ExperimentContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol=make_protocol();cls.result=benchmark(cls.protocol)
    def test_positive_dynamic_selection(self):self.assertEqual(self.result['selected_on_development'],'dynamic_history')
    def test_negative_control_prefers_simpler(self):self.assertEqual(benchmark(make_protocol(negative_control=True))['selected_on_development'],'erased_history')
    def test_generator_disclosed(self):self.assertIn('dynamic_history generates',self.protocol['generator_disclosure'])
    def test_unit_is_trajectory(self):self.assertEqual(self.result['evaluation_unit'],'whole trajectory, equally weighted')
    def test_seed_reproducibility(self):self.assertEqual(self.protocol,make_protocol())
    def test_audit_cannot_choose_model(self):
        p=copy.deepcopy(self.protocol)
        for trial in p['trials']:
            if trial['split']=='audit':
                for obs in trial['observations']:obs['C']=0.;obs['R']=0.
        altered=benchmark(p)
        self.assertEqual(self.result['selection_freeze_sha256'],altered['selection_freeze_sha256'])
        self.assertNotEqual(self.result['models'][0]['audit_mean_mse'],altered['models'][0]['audit_mean_mse'])
    def test_group_leakage_rejected(self):
        p=copy.deepcopy(self.protocol);p['trials'][-1]['group_id']=p['trials'][0]['group_id']
        with self.assertRaises(Invalid):validate_protocol(p)
    def test_scenario_leakage_rejected(self):
        p=copy.deepcopy(self.protocol);p['trials'][-1]['scenario']=p['trials'][0]['scenario']
        with self.assertRaises(Invalid):validate_protocol(p)
    def test_missing_split(self):
        p=copy.deepcopy(self.protocol)
        p['trials']=[t for t in p['trials'] if t['split']!='audit']
        with self.assertRaises(Invalid):validate_protocol(p)
    def test_bad_observation_order(self):
        p=copy.deepcopy(self.protocol);p['trials'][0]['observations'].reverse()
        with self.assertRaises(Invalid):validate_protocol(p)
    def test_nan_observation(self):
        p=copy.deepcopy(self.protocol);p['trials'][0]['observations'][0]['C']=float('nan')
        with self.assertRaises(Invalid):validate_protocol(p)
    def test_empirical_intake_not_implied(self):
        p=copy.deepcopy(self.protocol);p['data_kind']='patients'
        with self.assertRaises(Invalid):validate_protocol(p)
    def test_time_zero_non_discriminating(self):
        rows=sensor_design(SCENARIOS['high_history'])['candidate_designs']
        self.assertTrue(all(r['score_per_cost']==0 for r in rows if r['time']==0))
    def test_design_has_nonzero_separation(self):self.assertGreater(sensor_design(SCENARIOS['high_history'])['selected']['score_per_cost'],0)
    def test_zero_sensitivity_is_empty(self):self.assertEqual(sensitivity(0)['rows'],[])
    def test_sensitivity_reproducible(self):self.assertEqual(sensitivity(3),sensitivity(3))
    def test_sensitivity_bound(self):
        with self.assertRaises(Invalid):sensitivity(100000)
    def test_one_bit_two_decoders(self):
        r=information_demo();self.assertEqual(r['aligned_mutual_information_bits'],r['inverted_mutual_information_bits'])
        self.assertNotEqual(r['identity_decoder_accuracy_aligned'],r['identity_decoder_accuracy_inverted'])
    def test_independence_zero_information(self):self.assertAlmostEqual(mutual_information([[.25,.25],[.25,.25]]),0)
    def test_subnormal_information_no_division_underflow(self):
        import math
        self.assertTrue(math.isfinite(mutual_information([[1e-320,0.],[0.,1.]])))
    def test_bad_distribution(self):
        with self.assertRaises(Invalid):mutual_information([[1,1]])
    def test_ragged_distribution(self):
        with self.assertRaises(Invalid):mutual_information([[.2],[.2,.6]])

class EvidenceContracts(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.ledger=Ledger(Path(self.tmp.name)/'ledger.sqlite')
        self.scope={'species':'synthetic_system','data_kind':'synthetic','units':'dimensionless','claim_strength':'simulation'}
    def node(self,id='a',dependencies=None,scope=None):
        return {'id':id,'kind':'source','layer':'D','statement':'A synthetic test statement.',
                'depends_on':dependencies or [],'scope':scope or self.scope}
    def test_add_and_verify(self):self.ledger.add(self.node());self.assertEqual(self.ledger.verify()['events'],1)
    def test_duplicates_rejected(self):
        self.ledger.add(self.node())
        with self.assertRaises(Invalid):self.ledger.add(self.node())
    def test_forward_dependency_rejected(self):
        with self.assertRaises(Invalid):self.ledger.add(self.node(dependencies=['future']))
    def test_self_cycle_rejected(self):
        with self.assertRaises(Invalid):self.ledger.add(self.node(dependencies=['a']))
    def test_transitive_correction(self):
        self.ledger.add(self.node());self.ledger.add(self.node('b',['a']));self.ledger.add(self.node('c',['b']))
        self.ledger.invalidate('a','Source corrected.')
        self.assertEqual(self.ledger.project()['c']['status'],'review_required')
    def test_unrelated_node_unchanged(self):
        self.ledger.add(self.node());self.ledger.add(self.node('other'));self.ledger.invalidate('a','Corrected.')
        self.assertEqual(self.ledger.project()['other']['status'],'unreviewed')
    def test_invalidated_cannot_be_reviewed(self):
        self.ledger.add(self.node());self.ledger.invalidate('a','Corrected.')
        with self.assertRaises(Invalid):self.ledger.review('a','reviewer')
    def test_late_dependent_inherits_correction(self):
        self.ledger.add(self.node());self.ledger.invalidate('a','Corrected.');self.ledger.add(self.node('b',['a']))
        self.assertEqual(self.ledger.project()['b']['status'],'review_required')
    def test_scope_mismatch_requires_review(self):
        self.ledger.add(self.node());scope=dict(self.scope,species='human');self.ledger.add(self.node('b',['a'],scope))
        self.assertEqual(self.ledger.project()['b']['status'],'review_required')
        with self.assertRaises(Invalid):self.ledger.review('b','reviewer')
    def test_scope_match_not_truth(self):self.assertIn('not sufficient',scope_compatible(self.scope,self.scope)['scope'])
    def test_synthetic_cannot_be_empirical(self):
        with self.assertRaises(Invalid):self.ledger.add(self.node(scope=dict(self.scope,claim_strength='reported_evidence')))
    def test_review_identity_is_asserted(self):
        self.ledger.add(self.node());self.ledger.review('a','local-reviewer')
        self.assertIn('not verified identities',self.ledger.export()['scope'])
    def test_tamper_detected(self):
        self.ledger.add(self.node())
        with closing(sqlite3.connect(self.ledger.path)) as db, db:db.execute("UPDATE events SET hash='changed'")
        with self.assertRaises(Invalid):self.ledger.verify()
    def test_retained_head_detects_truncation(self):
        self.ledger.add(self.node());self.ledger.add(self.node('b'));head=self.ledger.verify()['head']
        with closing(sqlite3.connect(self.ledger.path)) as db, db:db.execute('DELETE FROM events WHERE seq=2')
        with self.assertRaises(Invalid):self.ledger.verify(head)
    def test_v2_quality_not_promoted(self):
        result=import_hepatoscholar_v2(load(ROOT/'examples/hepatoscholar_v2_synthetic.json'),self.ledger)
        self.assertTrue(result['no_quality_score_promotion'])
        self.assertTrue(all(n['status']=='unreviewed' for n in self.ledger.project().values()))
    def test_v2_empirical_rejected(self):
        p=load(ROOT/'examples/hepatoscholar_v2_synthetic.json');p['scenarios'][0]['records'][0]['source_type']='REAL'
        with self.assertRaises(Invalid):import_hepatoscholar_v2(p,self.ledger)
        self.assertEqual(self.ledger.verify()['events'],0)
    def test_demo_invalidates_four_descendants(self):
        r=lineage_demo(Path(self.tmp.name)/'demo.sqlite');self.assertEqual(r['review_required_count'],4)

class CapsuleContracts(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)/'run';self.root.mkdir()
        (self.root/'data.txt').write_text('example');seal(self.root)
    def test_manifest_verifies(self):self.assertTrue(verify(self.root)['valid'])
    def test_payload_tamper(self):
        (self.root/'data.txt').write_text('changed')
        with self.assertRaises(Invalid):verify(self.root)
    def test_extra_payload(self):
        (self.root/'extra').write_text('x')
        with self.assertRaises(Invalid):verify(self.root)
    def test_missing_payload(self):
        (self.root/'data.txt').unlink()
        with self.assertRaises(Invalid):verify(self.root)
    def test_external_head(self):
        with self.assertRaises(Invalid):verify(self.root,'0'*64)
    def test_traversal_manifest(self):
        write_json(self.root/'manifest.json',{'schema_version':1,'files':{'../x':'0'*64}})
        with self.assertRaises(Invalid):verify(self.root)
    def test_symlink_rejected(self):
        try:(self.root/'link').symlink_to(self.root/'data.txt')
        except OSError:self.skipTest('Host does not permit symlinks for this user.')
        with self.assertRaises(Invalid):seal(self.root)
    def test_existing_output_not_reset(self):
        with self.assertRaises(Invalid):demo(self.root,0)
        self.assertEqual((self.root/'data.txt').read_text(),'example')
    def test_source_identity_present(self):self.assertIn('dynamics.py',source_identity()['file_hashes'])
    def test_embedded_html_escaped(self):self.assertNotIn('</script><script>evil',html_report({'x':'</script><script>evil'}))

class ConsoleContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=Console(0);cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=3)
    def request(self,path='/',method='GET',body=None,headers=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=10)
        h={'Host':self.server.host}
        if method=='POST':h.update({'Origin':self.server.origin,'X-Hepato-Token':self.server.token,'Content-Type':'application/json'})
        if headers:h.update(headers)
        conn.request(method,path,body=body,headers=h);r=conn.getresponse();data=r.read();status=r.status;hdr=dict(r.getheaders());conn.close()
        return status,data,hdr
    def post(self,payload,path='/api/simulate',headers=None):return self.request(path,'POST',canonical(payload),headers)
    def test_home(self):
        status,data,h=self.request();self.assertEqual(status,200);self.assertIn(b'DIKWP HepatoGenesis',data);self.assertIn('Content-Security-Policy',h)
    def test_host_gate(self):self.assertEqual(self.request(headers={'Host':'evil.example'})[0],403)
    def test_origin_gate(self):self.assertEqual(self.post({},headers={'Origin':'https://evil.example'})[0],403)
    def test_token_gate(self):self.assertEqual(self.post({},headers={'X-Hepato-Token':'wrong'})[0],403)
    def test_unknown_route(self):self.assertEqual(self.request('/../../etc/passwd')[0],404)
    def test_catalog(self):self.assertEqual(len(json.loads(self.request('/api/catalog')[1])['scenarios']),6)
    def test_simulation_route(self):
        status,raw,_=self.post({'scenario':'high_history','model':'dynamic_history'})
        self.assertEqual(status,200);self.assertAlmostEqual(json.loads(raw)['metrics']['final_capacity'],.5971026844,places=8)
    def test_extra_key_rejected(self):self.assertEqual(self.post({'scenario':'high_history','model':'dynamic_history','path':'/etc/passwd'})[0],400)
    def test_nan_body_rejected(self):self.assertEqual(self.request('/api/simulate','POST','{"x":NaN}')[0],400)
    def test_non_json(self):self.assertEqual(self.request('/api/simulate','POST','x',{'Content-Type':'text/plain'})[0],415)
    def test_bounded_memory(self):self.assertEqual(self.post({'scenario':'high_history','model':'dynamic_history','memory':999})[0],400)
    def test_duplicate_json_rejected(self):self.assertEqual(self.request('/api/simulate','POST','{"a":1,"a":2}')[0],400)
    def test_all_lab_routes(self):
        for name in ['finite','physics','information','benchmark','negative_control','design']:
            with self.subTest(lab=name):self.assertEqual(self.post({'name':name},'/api/lab')[0],200)
