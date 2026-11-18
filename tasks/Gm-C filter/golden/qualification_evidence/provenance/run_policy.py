"""Use this run's saved policy, independently of later global-policy changes."""
import json
from pathlib import Path
def apply(work):
 p=json.loads((Path(__file__).resolve().parent/'target_policy.json').read_text())
 work.LIMITS={k:(v['lower'],v['upper'],work.LIMITS[k][2]) for k,v in p['limits'].items()}
 return p
