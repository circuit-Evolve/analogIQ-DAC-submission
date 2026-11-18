"""Fresh baseline integration proof, at most two Spectre processes concurrently."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,time,hashlib
from gm_c_task import Task,TEMPLATE
from engine import execute
P=Path(__file__).resolve().parent
OUT=P.parent/'preflight/gm_c'

def main():
    task=Task('full');decks=task.decks(task.paper_design());paths={};timings={};start=time.monotonic()
    def job(name,deck):
        t=time.monotonic();path=OUT/'paper_seed'/name;rc=execute(deck,path,180)
        return name,path,rc,time.monotonic()-t
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(job,n,d) for n,d in decks.items()]
        for f in as_completed(futures):
            n,p,rc,elapsed=f.result();timings[n]={'returncode':rc,'elapsed_seconds':elapsed}
            if rc==0:paths[n]=p
            print(n,rc,round(elapsed,3),flush=True)
    values,diagnostics=task.extract(paths)
    rows=json.loads((TEMPLATE/'comparison.json').read_text());comparison=[]
    for r in rows:
        val=diagnostics['nonlinear'][r['name']]['value'] if r.get('diagnostic_only') else values[r['name']]
        rel=None if val is None else abs(val-r['result'])/max(abs(r['result']),1e-30)
        comparison.append({'name':r['name'],'saved':r['result'],'fresh':val,'relative_error':rel,'agrees':rel is not None and rel<1e-6,'diagnostic_only':r.get('diagnostic_only',False)})
    # Physical sizing perturbation proof, preserving input sources/topology.
    changed=task.paper_design();changed['input_p_w']*=1.1
    mt=Task();mutation_paths={};mutation_start=time.monotonic()
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures={pool.submit(execute,d,OUT/'mutation'/n,180):n for n,d in mt.decks(changed).items()}
        for f in as_completed(futures):
            n=futures[f]
            if f.result()==0:mutation_paths[n]=OUT/'mutation'/n
    mutation_values,mutation_diagnostics=mt.extract(mutation_paths)
    mutation_proof={'design':changed,'values':mutation_values,'diagnostics':mutation_diagnostics,'elapsed_seconds':time.monotonic()-mutation_start,'all_scalars_finite':all(v is not None for v in mutation_values.values()),'response_changes':any(mutation_values[n] is not None and abs(mutation_values[n]-v)>max(1e-12,abs(v)*1e-8) for n,v in values.items() if v is not None)}
    proof={'complete':all(r['agrees'] for r in comparison) and all(t['returncode']==0 for t in timings.values()) and mutation_proof['all_scalars_finite'] and mutation_proof['response_changes'],'profile':'full','max_concurrent_spectre':2,'dimensions':len(task.variables),'objective_count':len(task.cfg['constraints']),'values':values,'diagnostics':diagnostics,'comparison':comparison,'timings':timings,'elapsed_seconds':time.monotonic()-start,'mutation':mutation_proof,'artifact_sha256':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ['gm_c_task.py','gm_c.json','gm_c_paper_seed.json']}}
    (OUT/'proof.json').write_text(json.dumps(proof,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'complete':proof['complete'],'comparison':comparison,'elapsed_seconds':proof['elapsed_seconds'],'mutation_response_changes':mutation_proof['response_changes']},indent=2),flush=True)
    if not proof['complete']:raise SystemExit(1)
if __name__=='__main__':main()
