"""Targeted fake-clock integration checks; no Spectre process is launched."""
from pathlib import Path
from types import SimpleNamespace
import hashlib, json, time
import bandgap_corners as mod

ROOT=mod.P.parent
OUT=ROOT/'preflight/bandgap/deadline_checks'
assert not OUT.exists(), 'Use fresh output; never overwrite historical tests'
OUT.mkdir(parents=True)
real_time, real_execute = mod.time, mod._engine.execute
reports=[]
try:
    # Exhaust the whole evaluation budget during its first mocked job. All later
    # line, nominal, temperature and startup jobs must write rc124 without launch.
    for profile,budget,count in [('search_full',900,35),('full_verify',1800,50)]:
        clock=SimpleNamespace(value=100.)
        mod.time=SimpleNamespace(monotonic=lambda:clock.value)
        calls=[]
        def fake_execute(text,dest,timeout):
            calls.append(timeout)
            dest.mkdir(parents=True,exist_ok=True)
            (dest/'input.scs').write_text(text)
            (dest/'stdout.log').write_text('Mock simulation; no external process.\n')
            clock.value+=budget+1
            return 124
        mod._engine.execute=fake_execute
        task=mod.Task(profile=profile)
        result=task.evaluate(task.seed_design(),OUT/profile,timeout=5000)
        assert calls==[budget],calls
        assert result['simulator_invocations']==1
        assert result['scheduled_job_count']==count
        assert result['deadline_exhausted'] and not result['execution_ok']
        assert len(result['corners'])==15
        assert all(not row['execution_ok'] and all(value is None for value in row['values'].values()) for row in result['corners'])
        statuses=[json.loads(p.read_text()) for p in (OUT/profile).rglob('status.json')]
        assert len(statuses)==count
        assert sum(not status['simulator_launched'] for status in statuses)==count-1
        assert all(status['returncode']==124 for status in statuses)
        reports.append({'profile':profile,'budget_s':budget,'first_timeout_capped_to_budget':True,
            'mock_launch_count':len(calls),'later_jobs_not_launched':count-1,'all15_corners_invalid_with_None_metrics':True})
    # Initial metadata changes must leave the electrical decks byte-identical.
    task=mod.Task()
    seed=task.seed_design()
    assert all(v['initial']==seed[v['name']] for v in task.variables)
    for name,text in task.decks(seed).items():
        generated=task.corner_deck(text,'tt',1.8)
        if name=='line': prior=ROOT/'preflight/bandgap/seed/TT_line/input.scs'
        else: prior=ROOT/f'preflight/bandgap/seed/TT_1.80V_27C/{name}/input.scs'
        assert generated==prior.read_text(),name
    mod._write(mod.P/'bandgap_config.json',task.cfg)
    provenance=json.loads((mod.P/'bandgap_provenance.json').read_text())
    provenance.update(implementation_sha256=hashlib.sha256((mod.P/'bandgap_corners.py').read_bytes()).hexdigest(),
        initial_metadata='All19 variable.initial values equal the exact saved best seed; bounds and generated decks unchanged.',
        deadline_policy='Overall monotonic budget900s search/1800s full_verify. Each simulator timeout capped by remaining budget; exhausted jobs rc124 without launch.',
        deadline_test=str(OUT/'report.json'))
    mod._write(mod.P/'bandgap_provenance.json',provenance)
    report={'passed':True,'no_real_simulators_launched':True,'profiles':reports,
        'all19_initials_equal_seed':True,'all_seed_decks_identical_to_preflight':True}
    mod._write(OUT/'report.json',report)
    print(json.dumps(report,indent=2))
finally:
    mod.time,mod._engine.execute=real_time,real_execute
