"""Run once in a fresh private preflight path; assert seed and parameter propagation."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib, json, re
from bandgap_corners import Task, P, BASE, _write

ROOT = P.parent
OUT = ROOT/'preflight/bandgap'
task = Task()
seed = task.seed_design()
original_best = Path('<RUNS>/ledro8h_four_papers_20261107T173619Z/bandgap/best.json')
prior_results = Path('<WORK>/four-circuit-corners-20261109/bandgap/results.json')
sha = lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
_write(P/'bandgap_config.json',task.cfg)
_write(P/'bandgap_provenance.json',{
    'seed_original':str(original_best),'seed_original_sha256':sha(original_best),
    'seed_copy':str(P/'bandgap_seed.json'),'seed_copy_sha256':sha(P/'bandgap_seed.json'),
    'previous_verification':str(prior_results),'previous_verification_sha256':sha(prior_results),
    'paper_conditions':'Paper Table I/V: 1.8V nominal; Fig.5c sweep endpoints1.71/1.89V; Fig.6 FF/SS/SF/FS plus nominalTT.',
    'frozen_base':str(BASE),'frozen_bandgap_config_sha256':sha(BASE/'bandgap.json'),
    'nominal_template_sha256':sha(BASE/'templates/bandgap/nominal.scs'),
    'target_rule':'Original five two-sided10% paper matching bands unchanged at all15 corners.',
    'temperature':'Only retained -40..120C sweep for19..120C TC; no extra temperature corner grid.',
    'startup':'Search constant-supply ripple only; full_verify adds all15 1ms ramp diagnostics, not a target.',
    'cleanup':'Search removes raw after each completed corner; shared line raw removed after its three supply corners. Full verification archives raw per job before removing uncompressed copies.',
    'implementation_sha256':sha(P/'bandgap_corners.py')})
assert seed==json.loads(original_best.read_text())['params']

# Every one of the19 exposed variables must reach each bound device in all decks.
baseline_decks = task.decks(seed)
binding_checks = []
for var in task.variables:
    changed = dict(seed)
    changed[var['name']] *= 1.001
    decks = task.decks(changed)
    for name,text in decks.items():
        for device in var['devices']:
            pattern = r'(?m)^\s*'+re.escape(device)+r' \([^\n]+\) [^\n]*?\b'+var['parameter']+r'=(\S+)'
            old = re.search(pattern,baseline_decks[name])[1]
            new = re.search(pattern,text)[1]
            assert float(old)!=float(new),(var['name'],name,device)
            expected = changed[var['name']]*(1e6 if var['parameter'] in ('w','l') else 1)
            assert abs(float(new)-expected)<=abs(expected)*1e-10
    binding_checks.append(var['name'])

fresh = task.evaluate(seed,OUT/'seed',keep_raw=False)
assert fresh['execution_ok'] and fresh['simulator_invocations']==35
prior = {r['id']:r for r in json.loads(prior_results.read_text())['results']}
comparisons=[]
for row in fresh['corners']:
    for name,value in row['values'].items():
        expected=prior[row['id']]['metrics'][name]
        delta=abs(value-expected)
        assert delta<=max(1e-12,abs(expected)*1e-12),(row['id'],name,value,expected)
        comparisons.append({'corner':row['id'],'metric':name,'previous':expected,'fresh':value,'absolute_delta':delta})

# One actual circuit perturbation, all five scalars at TT1.8V, without a search.
perturbed=dict(seed); perturbed['R3_r']*=1.01
decks=task.decks(perturbed)
dest=OUT/'perturb_R3_plus1percent'
dest.mkdir(parents=True,exist_ok=True)
_write(dest/'design.json',{'parameters':perturbed,'changed_parameter':'R3_r','factor':1.01})
line=task._run(task.corner_deck(decks['line'],'tt',1.8),dest/'line',180)
assert line['returncode']==0
_,y=task._sweep(dest/'line/raw/dc.dc','VS')
import numpy as np
with ThreadPoolExecutor(max_workers=2) as pool:
    futures={n:pool.submit(task._run,task.corner_deck(decks[n],'tt',1.8),dest/n,180) for n in ('nominal','temperature')}
    jobs={n:f.result() for n,f in futures.items()}
values,diag=task._extract(jobs,1.8,float(100*np.ptp(y)/.18),None)
assert not diag['errors']
assert abs(values['Vref_V']-prior['TT_1.80V_27C']['metrics']['Vref_V'])>1e-4
_write(dest/'metrics.json',{'id':'TT_1.80V_27C','values':values,'diagnostics':diag,'jobs':jobs,'line_job':line})
for job in list(jobs.values())+[line]:task._finish_raw(job,False)
report={'passed':True,'seed_values_checked':len(comparisons),'all19_variable_bindings_checked':binding_checks,
    'seed_simulator_invocations':fresh['simulator_invocations'],'perturb_simulator_invocations':3,
    'scalar_comparisons':comparisons,'perturbed_nominal_values':values,
    'all_raw_pruned':not any(OUT.rglob('raw')),
    'original_best_unchanged':sha(original_best)==sha(P/'bandgap_seed.json')}
_write(OUT/'report.json',report)
print(json.dumps({k:v for k,v in report.items() if k!='scalar_comparisons'},indent=2))
