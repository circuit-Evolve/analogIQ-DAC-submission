"""Remove the old absolute-frequency assumption from the auxiliary four-pole screen.
No simulation values or scalar acceptance limits are changed. Original evidence is preserved.
"""
import json,math,hashlib,sys
from pathlib import Path
N=Path(__file__).resolve().parent;R=N.parent
sys.path.insert(0,str(R.parent));import work
from run_policy import apply
apply(work)
physical=Path(sys.argv[1])
s=json.loads((physical/'summary.json').read_text())
e=json.loads(Path(sys.argv[2]).read_text())
ids={x['id'] for x in work.CONDITIONS};h=hashlib.sha256(json.dumps(e['design'],sort_keys=True).encode()).hexdigest()
assert len(s['corners'])==9 and {x['corner']['id'] for x in s['corners']}==ids
assert len(e['corners'])==9 and {x['id'] for x in e['corners']}==ids
assert work.grade(e['corners'])['scalar_pass']==54
for row in s['corners']:
 assert row['design_sha256']==h
 poles=sorted(row['poles_Hz'],key=lambda p:math.hypot(*p))
 assert len(poles)>=5 and all(len(p)==2 and all(math.isfinite(v) for v in p) for p in poles)
 first4=poles[:4];ratio=math.hypot(*poles[4])/math.hypot(*poles[3])
 qualifies=all(a<0 and abs(b)<1 for a,b in first4) and ratio>=3
 shape=next(x for x in e['corners'] if x['id']==row['corner']['id'])['diagnostics']['filter_response']['strict_shape_screen']
 row['legacy_fixed_200MHz_four_poles']=row.pop('four_dominant_real_poles')
 row['legacy_physical_screen_pass']=row.pop('physical_screen_pass')
 row['four_dominant_real_poles']=bool(qualifies)
 row['dominant_pole_screen']=dict(first_four_poles_Hz=first4,fifth_pole_magnitude_Hz=math.hypot(*poles[4]),fifth_to_fourth_magnitude_ratio=ratio,required_ratio=3,real_pole_imaginary_tolerance_Hz=1,finite_pole_count=len(poles),pass_screen=bool(qualifies))
 row['physical_screen_pass']=bool(not row['errors'] and all(a<0 for a,b in poles) and qualifies and row['DM']['screen_pass'] and row['CM']['screen_pass'] and shape)
s['physical_screen_pass']=sum(x['physical_screen_pass'] for x in s['corners'])
s['revision']='frequency_independent_four_dominant_poles'
s['criterion']='Four lowest-magnitude poles must be real (|imag|<1Hz) and LHP; fifth magnitude>=3x fourth; all reported poles LHP; existing AC shape, DM/CM settling/rails/agreement checks unchanged.'
s['reason']='Same frequency-independent four-pole screen established for15% sizing. UGF remains minimum-only; filter cutoff now has its separate10..20MHz scalar range. The pole screen has no arbitrary absolute-frequency limit. Original fixed200MHz diagnostic preserved for provenance.'
s['scope']='Finite engineering screen, not unrestricted stability proof. BSIM3 PZ frequency-dependent terms approximated at1Hz. No scalar targets changed.'
work.dump(physical/'qualification.json',s)
print('Qualified physical screens',s['physical_screen_pass'],'/9; pole separation range',min(x['dominant_pole_screen']['fifth_to_fourth_magnitude_ratio'] for x in s['corners']),max(x['dominant_pole_screen']['fifth_to_fourth_magnitude_ratio'] for x in s['corners']))
