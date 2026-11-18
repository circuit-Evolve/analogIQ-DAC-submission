"""One-time private setup; reads previously verified artifacts, never modifies them."""
from pathlib import Path
import json,hashlib,shutil
P=Path(__file__).resolve().parent
OLD=Path('<WORK>/four-circuit-corners-20261109/miso')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
write=lambda p,x:p.write_text(json.dumps(x,indent=2)+'\n')
seed=read(OLD/'best_sizing.json');cfg=read(P/'base/miso.json')
for v in cfg['variables']:v['initial']=seed[v['name']]
cs=read(OLD/'corners.json')
cfg['conditions']=[{**c,**cs['nominal_conditions']} for c in cs['corners']]
cfg['characterization']['new_corners']=True
cfg['characterization']['model']='gpdk180 NN, FF, SS, SF, FS'
cfg['seed_provenance']='Saved best eval685; exact prior verified current best; no new sizing.'
write(P/'miso_corners.json',cfg);write(P/'miso_seed.json',seed)
(P/'miso_templates').mkdir(exist_ok=True)
sources=[OLD/'best_sizing.json',OLD/'corners.json',OLD/'results.json',P/'base/miso_task.py',P/'base/engine.py',P/'base/miso.json']
sources+=sorted(Path(cs['model_file']).parent.glob('*.scs'))
for p in sorted((OLD/'runs/TT').glob('*/input.scs')):
    shutil.copyfile(p,P/'miso_templates'/(p.parent.name+'.scs'));sources.append(p)
for cid in ['TT','FF','SS','SF','FS']:sources.append(OLD/'runs'/cid/'results.json')
engine=(P/'base/engine.py').read_text();(P/'miso_engine.py').write_text(engine)
adapter=(P/'base/miso_task.py').read_text().replace('from engine import mutate, read_wave, dc','from miso_engine import mutate, read_wave, dc').replace('HERE=Path(__file__).resolve().parent','HERE=Path(__file__).resolve().parent/"base"')
(P/'miso_nominal.py').write_text(adapter)
write(P/'miso_provenance.json',{'seed_eval':685,'seed_sha256':sha(P/'miso_seed.json'),'source_files':[{'path':str(p),'sha256':sha(p)} for p in sources],'corner_evidence':cs,'helper_adaptations':['miso_engine.py is byte-identical to frozen base/engine.py','miso_nominal.py changes only engine import and HERE path; actual scalar extraction remains unchanged','candidate templates are exact prior verified best nominal decks, not paper seed decks'],'candidate_mutation':'Apply design against best-sized decks, with variable initial values equal saved best; all bounds/bindings retained.','acceptance':'All original17 constraints unchanged.'})
