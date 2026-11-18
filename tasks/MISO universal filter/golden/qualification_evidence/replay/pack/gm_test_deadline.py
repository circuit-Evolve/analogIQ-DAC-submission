"""Evaluator infrastructure deadline tests; no real Spectre processes."""
from pathlib import Path
import tempfile,itertools,json
from unittest.mock import patch
from gm_c_corners import Task
ROOT=Path(__file__).resolve().parent.parent

def test_remaining_budget_caps_job():
    task=Task();corner=task.cfg['conditions'][0];item=next(iter(task.corner_decks(task.seed_design(),corner).items()));seen=[]
    class FakeProcess:
        def wait(self,timeout=None):seen.append(timeout);return 0
    with tempfile.TemporaryDirectory(dir=ROOT/'tmp',prefix='gm_deadline_test_') as tmp:
        with patch('gm_c_corners.time.monotonic',return_value=100),patch('gm_c_corners.subprocess.Popen',return_value=FakeProcess()):
            _,_,status=task._simulate(item,Path(tmp),corner,180,deadline=107)
        assert seen==[7],seen
        assert status['returncode']==0 and status['launched'] is True

def test_expiration_preserves_failed_corner_grid():
    for profile,budget in [('search_full',900),('full_verify',1800)]:
        task=Task(profile);clock=itertools.chain([0],itertools.repeat(budget+1))
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp',prefix='gm_deadline_test_') as tmp:
            with patch('gm_c_corners.time.monotonic',side_effect=lambda:next(clock)),patch('gm_c_corners.subprocess.Popen',side_effect=AssertionError('Expired budget must not launch Spectre')):
                result=task.evaluate(task.seed_design(),Path(tmp))
            assert result['evaluator_budget_s']==budget
            assert result['simulator_invocations']==0 and result['planned_simulator_invocations']==135
            assert not result['execution_ok'] and len(result['corners'])==45
            for row in result['corners']:
                assert not row['execution_ok'] and all(x is None for x in row['values'].values())
                for name,job in row['diagnostics']['jobs'].items():
                    assert job['returncode']==124 and job['launched'] is False
                    assert (Path(tmp)/row['id']/name/'input.scs').exists()
                    assert (Path(tmp)/row['id']/name/'status.json').exists()
if __name__=='__main__':
    test_remaining_budget_caps_job();test_expiration_preserves_failed_corner_grid();print('PASS: remaining timeout cap and expired 45-corner search/final grids; no Spectre launched')
