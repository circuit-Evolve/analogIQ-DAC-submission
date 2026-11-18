from pathlib import Path
import json,math,hashlib
from gm_c_corners import Task,gm_dump
R=Path(__file__).resolve().parent.parent
out=R/'gm_preflight';out.mkdir(exist_ok=True)
task=Task();seed=task.seed_design()
gm_dump(R/'pack/gm_config.json',task.cfg)
previous=json.loads(Path('<WORK>/four-circuit-corners-20261109/gm_c/percornerresults.json').read_text())
expected={r['corner']['id']:r['metrics'] for r in previous}
print('Starting45corner saved-best seed reproduction',flush=True)
r=task.evaluate(seed,out/'seed',keep_raw=False)
errors=[];max_relative=0;checked=0
for c in r['corners']:
 for m,v in c['values'].items():
  want=expected[c['id']][m];checked+=1
  if v is None or want is None or not math.isclose(v,want,rel_tol=1e-8,abs_tol=1e-9):errors.append({'corner':c['id'],'metric':m,'expected':want,'actual':v})
  if v is not None and want is not None:max_relative=max(max_relative,abs(v-want)/max(abs(want),1e-100))
assert r['execution_ok'] and len(r['corners'])==45 and checked==270 and not errors,errors
print('Seed matches all270 values',flush=True)
nom=next(c for c in task.cfg['conditions'] if c['id']=='NN_V1.0_T+27')
perturb=dict(seed);perturb['vt_bias_V']+=.01
p=task.evaluate_corner(perturb,nom,out/'perturb_vt_10mV',keep_raw=False)
assert p['execution_ok']
changed={m:{'seed':expected[nom['id']][m],'perturbed':v} for m,v in p['values'].items() if not math.isclose(v,expected[nom['id']][m],rel_tol=1e-6,abs_tol=1e-9)}
assert changed,'VT perturbation did not affect simulated metrics'
summary={'passed':True,'seed_corners':45,'seed_scalars_checked':checked,'seed_max_relative_difference':max_relative,'seed_simulator_invocations':r['simulator_invocations'],'seed_execution_ok':r['execution_ok'],'perturbation':{'parameter':'vt_bias_V','delta_V':.01,'corner':nom['id'],'changed_metrics':changed,'execution_ok':p['execution_ok']},'seed_sha256':hashlib.sha256((R/'pack/gm_seed.json').read_bytes()).hexdigest()}
gm_dump(out/'summary.json',summary)
print(json.dumps(summary,indent=2),flush=True)
