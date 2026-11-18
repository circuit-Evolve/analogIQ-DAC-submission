from pathlib import Path
from unittest.mock import patch
from dtmos_corners import Task
P=Path(__file__).resolve().parent
for profile in ['search_full','full_verify']:
 t=Task(profile);clock=iter([0]+[1000000]*50)
 with patch('dtmos_corners.time.monotonic',side_effect=lambda:next(clock)),patch('dtmos_corners.execute',side_effect=AssertionError('expired must not launch')):
  r=t.evaluate(t.seed_design(),P.parent/'runtime_checks'/('dtmos_'+profile))
 assert len(r['corners'])==12 and not r['execution_ok'] and r['simulator_invocations']==0
 assert all(all(v is None for v in c['values'].values()) for c in r['corners'])
print('PASS: DTMOS search/final overall expiry suppresses all launches and preserves12missingcorners')
