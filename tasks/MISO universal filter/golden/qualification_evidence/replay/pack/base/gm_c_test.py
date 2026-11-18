import importlib.util
import json
from pathlib import Path
import re
import unittest
import numpy as np

HERE = Path(__file__).resolve().parent
class GMCContract(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('gm_c_task'), 'gm-C adapter must exist')
        from gm_c_task import Task
        self.task = Task()

    def test_seed_has_exact_published_geometry_and_inferred_caps(self):
        s = self.task.decks(self.task.paper_design())['FILTER_AC_NOISE']
        self.assertIn('w=0.13u l=0.2u', s)
        self.assertIn('w=0.365u l=0.1u', s)
        self.assertIn('w=0.6u l=0.12u', s)
        self.assertIn('w=1.18u l=0.1u', s)
        self.assertEqual(len(re.findall(r'^OTA[1234] ', s, re.M)), 4)
        self.assertEqual(len(re.findall(r'^C[1234] .*c=7.65804778642e-12$', s, re.M)), 4)

    def test_width_mutation_updates_diffusion_without_stimulus_or_topology_drift(self):
        seed = self.task.paper_design()
        before = self.task.decks(seed)['OTA_DIFF']
        seed['input_p_w'] = 2.36e-6
        after = self.task.decks(seed)['OTA_DIFF']
        block = re.search(r'subckt ota_fig2_interpreted .*?\n(.*?)ends ota_fig2_interpreted', after, re.S)[1]
        line = re.search(r'^M1 .*$', block, re.M)[0]
        vals = dict(re.findall(r'(\w+)=(\S+)', line))
        self.assertAlmostEqual(float(vals['w']), 2.36e-6, places=16)
        self.assertAlmostEqual(float(vals['as']), 6.608e-13, places=23)
        self.assertAlmostEqual(float(vals['ps']), 5.28e-6, places=16)
        topology = lambda s: [(x[0], x[1], x[2]) for x in re.findall(r'^(\w+) \(([^\n]+)\) (\S+)', s, re.M)]
        self.assertEqual(topology(before), topology(after))
        self.assertEqual([x for x in before.splitlines() if x.startswith(('VIN','VDD','VREF','simulatorOptions','ac '))], [x for x in after.splitlines() if x.startswith(('VIN','VDD','VREF','simulatorOptions','ac '))])

    def test_all_variables_mutate_binding_and_invalid_design_rejected(self):
        seed = self.task.paper_design()
        original = self.task.decks(seed)
        for var in self.task.variables:
            changed = dict(seed)
            changed[var['name']] = min(var['upper'], seed[var['name']] * 1.1)
            self.assertNotEqual(original, self.task.decks(changed), var['name'])
        for bad in ({}, dict(seed, unknown=1), dict(seed, input_p_w=float('nan')), dict(seed, input_p_w=0)):
            with self.assertRaises(ValueError): self.task.decks(bad)

    def test_missing_outputs_are_missing_not_pass_defaults(self):
        values, diagnostics = self.task.extract({})
        self.assertEqual(len(values), 6)
        self.assertTrue(all(v is None for v in values.values()))
        self.assertTrue(diagnostics['errors'])

    def test_frozen_output_matches_saved_scalar_definitions(self):
        original = Path('<WORK>/four-papers-20261107/gm_c')
        values, _ = self.task.extract({n: original/'sim'/n for n in self.task.decks(self.task.paper_design())})
        for row in json.loads((original/'comparison.json').read_text()):
            if not row.get('diagnostic_only'):
                self.assertAlmostEqual(values[row['name']]/row['result'], 1, places=10)
        self.assertEqual(len(self.task.cfg['constraints']), 6)
        cm = next(c for c in self.task.cfg['constraints'] if c['metric']=='OTA_common_mode_gain_dB')
        self.assertEqual((cm['lower'],cm['upper']),(-26.400000000000002,-21.6))

    def test_unmodified_ledro_prompt_accepts_schema_and_shows_bindings(self):
        import sys
        sys.path.insert(0, '<ANALOGIQ>/sizing')
        from ledro_adapter.prompt import system_prompt
        prompt=system_prompt(self.task.cfg,self.task.plan_text(),'Test reward description')
        self.assertIn('NN_27',prompt)
        self.assertIn('w=<input_p_w>',prompt)

    def test_crossing_failure_and_nonfinite_waveform_fail_closed(self):
        from gm_c_task import crossing
        self.assertIsNone(crossing(np.array([1.,10.]),np.array([2.,3.]),1.))
        with self.assertRaises(ValueError): crossing(np.array([1.,10.]),np.array([2.,np.nan]),1.)

if __name__ == '__main__': unittest.main(verbosity=2)
