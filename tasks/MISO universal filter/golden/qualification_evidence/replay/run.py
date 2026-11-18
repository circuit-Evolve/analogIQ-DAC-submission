from engine9 import *
label=sys.argv[1] if len(sys.argv)>1 else 'verified_replay'
d=json.loads((B/'selected_design.json').read_text())['parameters']
full(label,d,workers=4,ac_points=600)
