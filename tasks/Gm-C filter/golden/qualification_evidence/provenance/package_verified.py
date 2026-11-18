"""Freeze a fully screened all-nine candidate. Refuses partial candidates."""
import sys,json,hashlib,shutil,re
from pathlib import Path
N=Path(__file__).resolve().parent;R=N.parent
sys.path.insert(0,str(R.parent));import work
from run_policy import apply
apply(work)
candidate=Path(sys.argv[1]);screen=Path(sys.argv[2]);dest=N/'verified_sizing'
e=json.loads(candidate.read_text());e['grade']=work.grade(e['corners']);s=json.loads((screen/'qualification.json').read_text())
assert e['grade']['all_pass']==9 and e['grade']['scalar_pass']==54
assert all(x['diagnostics']['filter_response']['strict_shape_screen'] for x in e['corners'])
h=hashlib.sha256(json.dumps(e['design'],sort_keys=True).encode()).hexdigest()
assert s['physical_screen_pass']==9 and len(s['corners'])==9
ids={x['id'] for x in work.CONDITIONS}
assert len(e['corners'])==9 and {x['id'] for x in e['corners']}==ids
assert {x['corner']['id'] for x in s['corners']}==ids
assert all(x['design_sha256']==h and x['physical_screen_pass'] for x in s['corners'])
assert not dest.exists();dest.mkdir()
old=R/'retained_sizing'
for name in ('models','extractor'):shutil.copytree(old/name,dest/name)
cfgpath=dest/'extractor/base/gm_c.json'
cfg=json.loads(cfgpath.read_text());cfg['conditions']=work.CONDITIONS
cfg['replay_scope']='Extractor support only: frozen netlists are authoritative; do not use legacy template generation for the reconstructed filter.'
for c in cfg['constraints']:
 lo,hi,_=work.LIMITS[c['metric']];c.update(lower=lo,upper=hi,conditions=[x['id'] for x in work.CONDITIONS])
work.dump(cfgpath,cfg)
for p in (dest/'models').rglob('*'):
 if p.is_file():
  model=Path('<PDK_ROOT>/gpdk090_v4.6/models/spectre')/p.relative_to(dest/'models')
  assert model.is_file() and model.read_bytes()==p.read_bytes(),str(model)
shutil.copytree(screen,dest/'physical_screen')
(dest/'physical_screen/summary.json').rename(dest/'physical_screen/legacy_summary.json')
work.dump(dest/'physical_screen/summary.json',s)
for row in s['corners']:
 folder=dest/'physical_screen'/row['corner']['id'];(folder/'screen.json').rename(folder/'legacy_screen.json');work.dump(folder/'screen.json',row)
e.pop('golden_verified',None);e['qualification_scope']='Dense54/54 and physical9/9 verified; frozen-model replay recorded separately'
work.dump(dest/'design.json',e['design']);work.dump(dest/'evaluation.json',e);work.dump(dest/'conditions.json',work.CONDITIONS)
shutil.copy2(N/'target_policy.json',dest/'target_policy.json')
source=R/'trials'/e['label']
for p in source.glob('*/*/input.scs'):
 out=dest/'netlists'/p.relative_to(source);out.parent.mkdir(parents=True,exist_ok=True)
 text=p.read_text();assert 'dec=500' in text
 row=next(x for x in e['corners'] if x['id']==p.parent.parent.name)
 assert hashlib.sha256(text.encode()).hexdigest()==row['diagnostics']['jobs'][p.parent.name]['deck_sha256']
 text=text.replace('<PDK_ROOT>/gpdk090_v4.6/models/spectre/gpdk090.scs','../../../models/gpdk090.scs');out.write_text(text)
assert len(list((dest/'netlists').glob('*/*/input.scs')))==27
replay=(old/'replay.py').read_text().replace('golden_verified=False',"scope='Numerical scalar replay only; physical evidence is in physical_screen'")
(dest/'replay.py').write_text(replay)
prov=dest/'provenance';prov.mkdir()
for p in [N/'fit.py',N/'fit_range_only.py',N/'joint_refine_resume1.py',N/'joint_refine_resume2.py',N/'smooth_elastic_refine.py',N/'longcross_elastic_refine.py',N/'quadratic_elastic_refine.py',N/'cross_length_probe.py',N/'cross_input_probe.py',N/'feedback_task.py',N/'run_policy.py',N/'verify_dense.py',N/'verify_physical.py',N/'qualify_physical.py',R/'physical_screen.py',R/'reconstruct.py',R/'untied.py',R/'compact.py',R/'continuation_20261113/wide_task.py',R.parent/'work.py']:
 shutil.copy2(p,prov/p.name)
for name in ('configuration.json','steps.jsonl','status.json'):
 shutil.copy2(N/'longcross_elastic_fit'/name,prov/('longcross_'+name))
shutil.copy2(N/'selected_candidate.json',prov/'search_selected_candidate.json')
shutil.copy2(N/'package_verified.py',prov/'package_verified.py')
shutil.copy2(N/'finalize.py',prov/'finalize.py')
metrics=[('OTA_differential_gain_dB','OTA differential gain','dB',39,1),('OTA_unity_gain_frequency_Hz','OTA UGF','GHz',10,1e9),('OTA_phase_margin_deg','OTA phase-margin estimate','deg',79,1),('OTA_common_mode_gain_dB','OTA common-mode gain','dB',-24,1),('Filter_cutoff_Hz','Filter cutoff','MHz',15,1e6),('Filter_input_noise_nV_sqrtHz','Input noise at 1 MHz','nV/sqrtHz',85,1)]
lines=['Gm-C FILTER — VERIFIED SIZING WITH 10–20 MHz CUTOFF RANGE','='*110,'All 9 independent conditions / 54 scalar checks pass, with one common sizing.','Scope: this qualifies the existing experimental reconstructed filter, NOT a paper-exact Fig.3 implementation.','Margins are narrow at several limits; this does not establish additional manufacturing or rounding margin.','UGF uses a minimum-only 15% target. Filter cutoff uses the explicit user-specified 10–20 MHz range.','Phase margin retains its two-sided 15% band; other metric directions remain unchanged.','', 'Metric                         Unit       Paper       Allowed             Range across nine      Pass','-'*110]
for k,name,unit,paper,scale in metrics:
 vals=[r['values'][k]/scale for r in e['corners']];lo,hi,_=work.LIMITS[k]
 bound=('>= '+format(lo/scale,'.5g')) if hi is None else ('<= '+format(hi/scale,'.5g')) if lo is None else f'{lo/scale:g}..{hi/scale:g}'
 lines.append(f'{name:30} {unit:10} {paper:8g}  {bound:18}  {min(vals):11.6g}..{max(vals):11.6g}  9/9')
lines+=['','Condition                Gain dB    UGF GHz     PM deg      CM dB     Fc MHz     Noise','-'*110]
for row in e['corners']:
 vals=[row['values'][k]/scale for k,_,_,_,scale in metrics]
 lines.append(f"{row['id']:22}"+''.join(f'{v:11.6g}' for v in vals)+'  PASS')
lines+=['','Scope and limitations:','- Nine independent process, voltage and temperature conditions, not a 45-point Cartesian PVT grid.','- Original interpreted OTA connectivity unchanged. All four OTA instances use one global sizing.','- Filter is the disclosed experimental four-state reconstruction: four 32-MOS OTAs, 16 diode-feedback MOS and four differential capacitors. It is NOT a paper-exact Fig.3 reproduction.','- Noise evaluated at the existing assumed 1 MHz measurement point.','- Phase margin is the existing OTA unity-feedback estimate, not a full-filter STB margin.','- Dense scalar sweep: 500 points/decade. Fresh finite pole and small-step physical screens pass at all nine conditions.','- Physical screens check four dominant poles, reported poles in LHP, settling, rails and agreement with small-signal AC at outputs and internal bias nodes.','- Auxiliary pole screen: four lowest-magnitude poles real (imaginary part<1 Hz) and LHP, with fifth/fourth magnitude ratio>=3. Measured separation ratios are recorded per condition in physical_screen/summary.json.','- Original fixed 200 MHz screening result is retained in legacy_summary.json/legacy_screen.json; The fixed 200 MHz result is informational; it is not a scalar target; cutoff is separately checked against 10–20 MHz. Scalar limits are unchanged by this diagnostic.','- Finite PZ/transient checks are not unrestricted stability proof; installed BSIM3 PZ approximates frequency-dependent terms at1 Hz.','- No layout/parasitic extraction. Original libraries and curator AnalogIQ folder remain unchanged.','','Sizing (SI units):',json.dumps(e['design'],indent=2),'','Frozen extractor templates support extraction only; use packaged netlists to reproduce this reconstructed circuit.','Replay: cd to this folder and run replay.py --out <empty SSD directory> with the existing LEDRO Python environment.','Replay validates frozen inputs and numerical reproduction; see replay_result.json for the actual completed replay outcome.']
(dest/'README.txt').write_text('\n'.join(lines)+'\n')
manifest={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.rglob('*') if p.is_file()}
work.dump(dest/'manifest.json',manifest)
print(dest)
