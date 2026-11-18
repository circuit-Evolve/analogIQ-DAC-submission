"""Replay frozen dense-sweep decks and models. Requires installed Spectre and NumPy."""
import os,sys,json,hashlib,shutil,subprocess,argparse,math
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'extractor'),str(ROOT/'extractor/base')]
from gm_base_task import Task

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--keep-raw',action='store_true');a=p.parse_args()
 out=Path(a.out).resolve()
 if out.exists() and any(out.iterdir()):raise RuntimeError('Replay output must be empty')
 if shutil.disk_usage(out.parent).free<3e9:raise RuntimeError('At least3GB free space required')
 manifest=json.loads((ROOT/'manifest.json').read_text())
 for name,h in manifest.items():
  if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=h:raise RuntimeError('Frozen input changed: '+name)
 expected=json.loads((ROOT/'evaluation.json').read_text());task=Task('search_full')
 out.mkdir(parents=True,exist_ok=True)
 def job(p):
  corner,kind=p.parent.parent.name,p.parent.name;d=out/corner/kind;d.mkdir(parents=True)
  deck=p.read_text().replace('../../../models/gpdk090.scs',str(ROOT/'models/gpdk090.scs'))
  (d/'input.scs').write_text(deck)
  with (d/'stdout.log').open('w') as log:
   result=subprocess.run(['/opt/cadence/bin/spectre','input.scs','-format','psfascii','-raw','raw','+log','spectre.log'],cwd=d,stdout=log,stderr=subprocess.STDOUT,timeout=180)
  return corner,kind,d,result.returncode
 with ThreadPoolExecutor(max_workers=4) as pool:jobs=list(pool.map(job,sorted((ROOT/'netlists').glob('*/*/input.scs'))))
 rows=[];maximum=0.
 for old in expected['corners']:
  paths={k:str(d) for c,k,d,rc in jobs if c==old['id'] and rc==0}
  values,diag=task.extract(paths)
  valid=len(paths)==3 and not diag['errors'] and all(v is not None and math.isfinite(v) for v in values.values())
  errors={k:abs(v-old['values'][k])/max(abs(old['values'][k]),1e-30) for k,v in values.items()} if valid else {}
  maximum=max(maximum,max(errors.values(),default=0.))
  rows.append(dict(id=old['id'],values=values,errors=diag['errors'],execution_ok=valid,relative_replay_errors=errors))
  if not a.keep_raw:
   for raw in (out/old['id']).glob('*/raw'):shutil.rmtree(raw)
 result=dict(corners=rows,frozen_inputs_verified=True,all_metrics_reproduced=all(x['execution_ok'] for x in rows) and maximum<1e-8,max_relative_difference=maximum,expected_scalar_pass=expected['grade']['scalar_pass'],expected_full_corner_pass=expected['grade']['all_pass'],scope='Numerical scalar replay only; physical evidence is in physical_screen')
 (out/'replay_result.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='corners'},indent=2))
 if not result['all_metrics_reproduced']:raise SystemExit(1)
if __name__=='__main__':main()
