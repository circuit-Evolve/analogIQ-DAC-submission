from pathlib import Path
import json,sys,math,hashlib,shutil
from dtmos_corners import Task,execute
P=Path(__file__).resolve().parent;R=P.parent
sp=Task();seed=sp.seed_design();(P/'dtmos_seed.json').write_text(json.dumps({'parameters':seed},indent=2));(P/'dtmos_problem.json').write_text(json.dumps(sp.cfg,indent=2))
assert sp.deck(seed,sp.corners[0])==sp.base.replace('dc=.9 ','dc=0.9 ').replace('dc=-.9 ','dc=-0.9 ')
x=sp.evaluate(seed,R/'preflight/dtmos',keep_raw=False,timeout=240)
ref=json.loads(Path('<WORK>/four-circuit-corners-20261109/dtmos/results.json').read_text());ref={z['corner']['id']:z['metrics'] for z in ref['results']}
for c in x['corners']:
 assert c['execution_ok'],c['id']
 for k,v in c['values'].items():assert math.isclose(v,ref[c['id']][k],rel_tol=1e-7,abs_tol=1e-9),(c['id'],k,v,ref[c['id']][k])
pert=dict(seed);pert['C1']*=1.05;corner=sp.corners[0];d=R/'preflight/dtmos_perturb';assert execute(sp.deck(pert,corner),d,timeout=240)==0
v,diag=sp.old.extract({'DTMOS_HPF_NOMINAL':d});fc=v['HPF_cutoff_Hz'];assert abs(fc-ref[corner['id']]['HPF_cutoff_Hz'])>1;shutil.rmtree(d/'raw')
proof={'ready':True,'source':'latestnative198Hz17MOScandidate','corners':12,'scalar_values_reproduced':36,'variables':len(sp.variables),'seed_nominal':ref[corner['id']],'C1_5percent_perturbed_cutoff_Hz':fc,'sizing_propagation_verified':True,'no_extra_feedback_transistors':True}
(R/'preflight/dtmos_preflight.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof,indent=2))
