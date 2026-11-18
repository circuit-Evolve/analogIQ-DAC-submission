from pathlib import Path
import importlib.util,json
HERE=Path(__file__).resolve().parent
spec=importlib.util.find_spec('gm_c_corners')
assert spec is not None, 'Missing Gm-C PVT evaluator'
from gm_c_corners import Task

def test_contract():
 t=Task(); seed=t.seed_design()
 previous=json.loads(Path('<WORK>/four-circuit-corners-20261109/gm_c/sizing.json').read_text())
 assert seed==previous, 'Evaluator must initialize from saved best, not paper seed'
 assert len(t.cfg['variables'])==31 and len(t.cfg['constraints'])==6
 assert len(t.cfg['conditions'])==45
 bad=dict(seed);bad['vt_bias_V']=float('nan')
 try:t.corner_decks(bad,t.cfg['conditions'][0])
 except ValueError:pass
 else:raise AssertionError('Invalid sizing must be rejected before Spectre')
 corner=next(c for c in t.cfg['conditions'] if c['id']=='NN_V1.0_T+27')
 perturbed=dict(seed);perturbed['vt_bias_V']+=.01
 original=t.corner_decks(seed,corner);changed=t.corner_decks(perturbed,corner)
 assert len(original)==3
 for name in original:
  assert original[name]!=changed[name], 'Candidate tuning voltage must reach all testbenches'
  assert f"VT_SRC (VT 0) vsource dc={perturbed['vt_bias_V']:.12g}\n" in changed[name]
 corner=next(c for c in t.cfg['conditions'] if c['id']=='SS_V0.9_T-40')
 for s in t.corner_decks(seed,corner).values():
  assert 'section=SS\n' in s and 'temp=-40 tnom=27' in s
  assert 'VREF_SRC (VREF 0) vsource dc=0.45\n' in s
 print('Gm-C evaluator contract and candidate propagation passed')
if __name__=='__main__':test_contract()
