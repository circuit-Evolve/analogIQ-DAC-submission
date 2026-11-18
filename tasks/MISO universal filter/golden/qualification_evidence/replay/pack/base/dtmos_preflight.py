"""Read-only source comparison and fresh simulations exclusively in run preflight."""
from pathlib import Path
import json,re,math,hashlib,time,concurrent.futures
import numpy as np
import engine
from dtmos_task import Task,TEMPLATES,ROOT

OUT=ROOT.parent/'preflight/dtmos'

def parts(s):
 return {m[1]:(m[2].split(),m[3],dict(re.findall(r'(\w+)=(\S+)',m[4]))) for m in re.finditer(r'^\s*(\w+) \(([^)]+)\) (\w+) ([^\n]+)',s,re.M)}

def run():
 OUT.mkdir(parents=True,exist_ok=True)
 t=Task();seed=t.paper_design();decks=t.decks(seed); proof={'dimension_count':len(seed)}
 assert seed==json.loads((ROOT/'dtmos_paper_seed.json').read_text())
 original=Path(json.loads((TEMPLATES/'provenance.json').read_text())['source'])
 assert (ROOT/'dtmos_hpf_cutoff.py').read_bytes()==(original/'hpf_cutoff.py').read_bytes()
 inv=json.loads((TEMPLATES/'design_inventory.json').read_text())
 for kind,cell in [('CORE','dtmos_fig1b_paper'),('HPF','dtmos_hpf_derived')]:
  name='DTMOS_'+kind+'_NOMINAL';src=(original/'results'/name/'input.scs').read_text()
  assert decks[name]==src
  pp=parts(src)
  for dev in inv[cell]['devices']:
   if dev['kind'] not in ['n','p']:continue
   nodes,model,pars=pp[dev['name']]
   assert nodes==dev['nodes']
   assert math.isclose(engine.num(pars['w'])*float(pars['m']),engine.num(dev['parameters']['w']),rel_tol=1e-14)
   assert math.isclose(engine.num(pars['l']),engine.num(dev['parameters']['l']),rel_tol=1e-14)
 proof['seed_identity']='PASS: byte-identical saved decks; all total W/L and pins match original inventory'
 checked=[]
 for v in t.variables:
  d=dict(seed);d[v['name']]=min(v['upper'],v['initial']*1.1);changed=t.decks(d)
  for name,s in decks.items():
   old=parts(s);new=parts(changed[name]);assert old.keys()==new.keys()
   bindings={n for n in v['binding']['instances'] if n in old};par=v['binding']['parameter']
   for dev,(nodes,model,pars) in old.items():
    nn,nm,np_=new[dev];assert nodes==nn and model==nm
    if dev not in bindings:assert pars==np_;continue
    expected=d[v['name']]/2 if dev=='M3' and par=='w' else d[v['name']]
    assert math.isclose(engine.num(np_[par]),expected,rel_tol=1e-11)
    allowed={par}|({'as','ad','ps','pd'} if par=='w' else set())
    for k in pars:
     if k not in allowed:assert pars[k]==np_[k]
    if par=='w':
     wn=engine.num(np_['w'])
     for a in ['as','ad']:assert math.isclose(engine.num(np_[a]),wn*.4e-6,rel_tol=1e-11)
     for a in ['ps','pd']:assert math.isclose(engine.num(np_[a]),2*(wn+.4e-6),rel_tol=1e-11)
   # Rest of deck (stimuli, model, analysis, temperature) untouched.
   strip=lambda text:re.sub(r'(?ms)^subckt .*?^ends [^\n]+','DUT_BODY',text)
   assert strip(s)==strip(changed[name])
  checked.append(v['name'])
 proof['mutation_checks']=checked
 for bad in [{},dict(seed,unknown=1),dict(seed,M1_w=float('nan')),dict(seed,M1_w=0)]:
  try:t.decks(bad)
  except ValueError:pass
  else:raise AssertionError('Invalid design accepted')
 missing,diag=t.extract({});assert all(x is None for x in missing.values())
 proof['invalid_design_and_missing_metrics']='PASS'
 # Synthetic cutoff regression verifies rising half-power measurement, not falling crossing.
 from dtmos_hpf_cutoff import measure
 f=np.logspace(0,7,701);hp=f/np.sqrt(f*f+200**2);lp=1/np.sqrt(1+(f/200)**2)
 assert abs(measure(f,hp)['cutoff_Hz']-200)<1
 assert measure(f,lp)['cutoff_Hz'] is None
 proof['cutoff_regression']='PASS: rising 200Hz HPF accepted; falling LPF rejected'
 saved_values,saved_diag=t.extract({name:original/'results'/name for name in decks})
 expected={('DTMOS_CORE_NOMINAL','Rail_power_mW'):'CORE_Rail_power_mW',('DTMOS_HPF_NOMINAL','Rail_power_mW'):'HPF_Rail_power_mW',('DTMOS_HPF_NOMINAL','THD_500Hz_10uApp_percent'):'THD_500Hz_10uApp_percent',('DTMOS_HPF_NOMINAL','HPF_cutoff_Hz'):'HPF_cutoff_Hz'}
 for row in json.loads((TEMPLATES/'comparison.json').read_text()):
  actual=saved_values[expected[(row['test'],row['metric'])]];want=row['nominal_result']
  assert actual is None if want is None else math.isclose(actual,want,rel_tol=1e-12)
 proof['saved_extraction_agreement']='PASS';proof['saved_values']=saved_values
 start=time.monotonic()
 def sim(item):
  name,deck=item;p=OUT/name;rc=engine.execute(deck,p,timeout=180);return name,rc,p
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:jobs=list(pool.map(sim,decks.items()))
 assert all(rc==0 for _,rc,_ in jobs),jobs
 values,diag=t.extract({name:p for name,rc,p in jobs if rc==0})
 for metric,want in saved_values.items():
  actual=values[metric];assert actual is None if want is None else math.isclose(actual,want,rel_tol=1e-8,abs_tol=1e-12),(metric,actual,want)
 assert diag['HPF']['cutoff_measurement']['status']=='FAIL_NO_FLAT_HPF_PASSBAND'
 proof.update(fresh_values=values,fresh_diagnostics=diag,fresh_baseline_agreement='PASS',baseline_expected_failure='Missing HPF cutoff from measured nonflat passband; power above target',elapsed_s=time.monotonic()-start,concurrent_spectre_limit=2)
 (OUT/'proof.json').write_text(json.dumps(proof,indent=2,allow_nan=False)+'\n')
 print(json.dumps({k:v for k,v in proof.items() if k!='fresh_diagnostics'},indent=2))

if __name__=='__main__':run()
