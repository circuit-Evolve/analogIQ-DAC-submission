"""Publish only a successfully replayed and physically qualified result under the explicit cutoff range."""
import json,pathlib,hashlib,shutil,datetime,sys
N=pathlib.Path(__file__).resolve().parent;R=N.parent;P=R.parent;F=N/'verified_sizing'
sys.path.insert(0,str(P));import work
from run_policy import apply
apply(work)
replay=pathlib.Path('<WORK>/four_papers_20261109/gmc_individual_15pct_20261112/reconstruction_20261113/cutoff10to20_frozen_replay/replay_result.json')
rp=json.loads(replay.read_text());assert rp['all_metrics_reproduced'] and rp['frozen_inputs_verified'] and rp['max_relative_difference']==0
manifest=json.loads((F/'manifest.json').read_text());assert all(hashlib.sha256((F/p).read_bytes()).hexdigest()==v for p,v in manifest.items())
e=json.loads((F/'evaluation.json').read_text());g=work.grade(e['corners']);assert g['all_pass']==9 and g['scalar_pass']==54
s=json.loads((F/'physical_screen/summary.json').read_text());assert s['physical_screen_pass']==9
ids={x['id'] for x in work.CONDITIONS}
assert len(s['corners'])==len(e['corners'])==len(rp['corners'])==9
assert {x['id'] for x in e['corners']}=={x['id'] for x in rp['corners']}=={x['corner']['id'] for x in s['corners']}==ids
h=hashlib.sha256(json.dumps(e['design'],sort_keys=True).encode()).hexdigest();assert all(x['design_sha256']==h for x in s['corners'])
shutil.copy2(replay,F/'replay_result.json')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
q=dict(state='verified_under_explicit_cutoff_range',updated_utc=now,golden_verified=True,paper_exact=False,design_sha256=h,scalar_checks_pass=54,scalar_checks_total=54,conditions_pass=9,conditions_total=9,finite_physical_screens_pass=9,frozen_replay_matches_exactly=True,policy_revision='cutoff_10_20MHz_20261113',other_metric_tolerance=.15,cutoff_range_MHz=[10,20],OTA_connectivity_unchanged=True,filter_topology='Disclosed experimental four-state reconstruction, not paper-exact Fig.3',corner_scope='Independent variation, not Cartesian PVT',noise_frequency_Hz=1e6,noise_frequency_is_assumed=True,phase_margin_scope='Existing OTA unity-feedback estimate, not full-filter STB margin',pole_screen_revision=s['revision'],pole_screen_caveat=s['scope'],analogiQ_updated=False)
work.dump(F/'qualification.json',q)
(N/'RESULTS.txt').write_text('Verified result under explicit 10–20 MHz cutoff and 15% rules for other metrics: 9/9 conditions, 54/54 scalar checks, 9/9 finite physical screens.\nFrozen-model replay reproduced all 54 scalar values exactly.\n\n'+(F/'README.txt').read_text())
status=dict(state='complete',updated_utc=now,active_pid=None,active_status=None,policy_revision=q['policy_revision'],current_target_policy=str(N/'target_policy.json'),retained_package=str(F),retained_design=str(F/'design.json'),retained_regraded_result=str(F/'evaluation.json'),retained_full_conditions=9,retained_scalar_checks=54,total_conditions=9,total_scalar_checks=54,golden_verified=True,paper_exact=False,qualification=str(F/'qualification.json'),report=str(N/'RESULTS.txt'),analogiQ_updated=False,previous_15pct_golden=str(R/'minimum_targets_20261113/verified_sizing'))
for path in [P/'checkpoint.json',R/'FINAL_STATUS.json',N/'STATUS.json']:work.dump(path,status)
allhash={str(p.relative_to(F)):hashlib.sha256(p.read_bytes()).hexdigest() for p in F.rglob('*') if p.is_file() and p.name!='archive_manifest.json'}
work.dump(F/'archive_manifest.json',allhash)
print('Verified frozen inputs',len(manifest),'final archive files',len(allhash));print('Final checks',g['all_pass'],g['scalar_pass'],s['physical_screen_pass']);print('Saved',N/'RESULTS.txt')
