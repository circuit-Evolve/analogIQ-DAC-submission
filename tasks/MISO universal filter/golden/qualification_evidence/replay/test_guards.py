from engine9 import *
v={c['metric']:(5.9 if c['metric'].endswith('THD') else c['paper_value']) for c in POLICY}
rows=[{'id':c,'values':v,'execution_ok':True} for c in ['TT','FF','SS','SF','FS']]
assert grade(rows)['golden'] and valid_full(grade(rows))
assert not grade([rows[0]]*5)['golden'] and not valid_full(grade([rows[0]]*5))
assert not grade(rows[:4])['golden']
assert not grade([{**r,'execution_ok':False} for r in rows])['golden']
assert not grade([{**r,'values':{**v,'LP_THD':6.0}} for r in rows])['golden']
assert not valid_full(grade([{**r,'values':{**v,'Y1_gain':float('nan')}} for r in rows]))
print('nine_metric_unique_corner_and_fail_closed_guards_pass')
