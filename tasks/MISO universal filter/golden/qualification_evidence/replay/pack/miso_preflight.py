from pathlib import Path
import json,math,hashlib,re,time
from miso_corners import Task,write
P=Path(__file__).resolve().parent;ROOT=P.parent;OLD=Path('<WORK>/four-circuit-corners-20261109/miso')
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=Task();seed=t.seed_design();cfg=read(P/'base/miso.json')
assert seed==read(OLD/'best_sizing.json')
assert t.cfg['constraints']==cfg['constraints']
for a,b in zip(t.variables,cfg['variables']):assert {k:v for k,v in a.items() if k!='initial'}=={k:v for k,v in b.items() if k!='initial'}
assert [c['id'] for c in t.corners]==['TT','FF','SS','SF','FS']
base=t.decks(seed)
for job,s in base.items():assert s==(OLD/'runs/TT'/job/'input.scs').read_text()
assert 'MISO variable bindings' in t.plan_text()
print('Static seed/template/schema checks passed; running60-simulation seed preflight.',flush=True)
started=time.monotonic();result=t.evaluate(seed,ROOT/'preflight/miso_seed',keep_raw=False)
assert result['execution_ok'] and result['simulator_invocations']==60
comparisons=[]
for corner in result['corners']:
    old=read(OLD/'runs'/corner['id']/'results.json')
    for c in cfg['constraints']:
        name=c['metric'];v=corner['values'][name];reference=old['constraints'][name]['value']
        assert math.isclose(v,reference,rel_tol=1e-9,abs_tol=1e-15),(corner['id'],name,v,reference)
        passed=c['lower']<=v<=c['upper'] and (not c.get('upper_exclusive') or v<c['upper'])
        assert passed==old['constraints'][name]['passed']
        comparisons.append({'corner':corner['id'],'metric':name,'new_value':v,'previous_verification_value':reference,'delta':v-reference,'passed':passed})
assert not list((ROOT/'preflight/miso_seed').glob('*/*/raw'))
print('All85seed scalar values and pass/fail classifications match; raw pruned. Running+1%OTA_IBIAS atTT.',flush=True)
perturbed=dict(seed);perturbed['OTA_IBIAS']*=1.01
new=t.decks(perturbed)
assert all(new[j]!=base[j] for j in base)
for s in new.values():
    line=next(l for l in s.splitlines() if re.match(r'\s*IBIAS ',l))
    dc=float(re.search(r'\bdc=(\S+)',line)[1]);assert math.isclose(dc,perturbed['OTA_IBIAS'],rel_tol=1e-11)
r=t._evaluate_corner(perturbed,ROOT/'preflight/miso_perturbed_TT',t.corners[0],keep_raw=True)
assert r['execution_ok']
nominal=result['corners'][0]['values'];changes={k:{'seed':nominal[k],'perturbed':v,'delta':v-nominal[k]} for k,v in r['values'].items() if not math.isclose(v,nominal[k],rel_tol=1e-7,abs_tol=1e-15)}
assert 'OTA_gm' in changes and 'MISO_quiescent_power' in changes
archive=read(ROOT/'preflight/miso_perturbed_TT/raw_archive.json');assert archive['bytes']<3_000_000_000
assert not list((ROOT/'preflight/miso_perturbed_TT').glob('*/raw'))
provenance=read(P/'miso_provenance.json');assert all(sha(Path(s['path']))==s['sha256'] for s in provenance['source_files'])
report={'passed':True,'seed_eval':685,'seed_scalar_comparisons':85,'all_seed_scalar_values_match':True,'rtol':1e-9,'atol':1e-15,'all_classifications_match':True,'seed_simulations':60,'perturbation_simulations':12,'seed_raw_pruned':True,'perturbation':{'variable':'OTA_IBIAS','factor':1.01,'seed_value':seed['OTA_IBIAS'],'candidate_value':perturbed['OTA_IBIAS'],'all12_decks_changed':True,'changed_metrics':changes},'compressed_retention_test':archive,'sources_unchanged':True,'runtime_seconds':time.monotonic()-started,'comparisons':comparisons}
write(ROOT/'preflight/miso_report.json',report)
print(json.dumps({k:v for k,v in report.items() if k!='comparisons'},indent=2),flush=True)
