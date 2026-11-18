"""Fresh physical screening with the same geometry validator as the current search."""
import os,sys,json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
N=Path(__file__).resolve().parent
sys.path[:0]=[str(N.parent),str(N.parent/'continuation_20261113')]
os.environ['GMC_SCREEN_DM_STEP_V']='0.0001'
import reconstruct as r
import physical_screen as p
from feedback_task import FeedbackTask
p.UntiedTask=FeedbackTask
candidate=json.loads(Path(sys.argv[1]).read_text());design=candidate.get('design',candidate);label=sys.argv[2]
r.work.dump(r.ROOT/label/'design.json',design)
with ThreadPoolExecutor(max_workers=2) as pool:
 rows=list(pool.map(lambda c:p.screen(design,c,label),r.work.CONDITIONS))
s=dict(corners=rows,physical_screen_pass=sum(x['physical_screen_pass'] for x in rows),total=len(rows),golden_verified=False,geometry_validator='FeedbackTask; same bounds as current search',DM_step_V=p.DM_STEP_V)
r.work.dump(r.ROOT/label/'summary.json',s)
print(json.dumps({k:v for k,v in s.items() if k!='corners'},indent=2))
