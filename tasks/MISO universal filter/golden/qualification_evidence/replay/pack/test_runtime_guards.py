import subprocess
import run_ledro as module
flat={'constraints':{'THD':{'value':6,'lower':0,'upper':6,'upper_exclusive':True,'passed':False}}}
s=module.strict_score(flat,{},1,None);assert s['f']>0 and s['reward']<0
flat['constraints']['THD'].update(value=5,passed=True);assert module.strict_score(flat,{},1,None)['f']==0
original=module._original_ask
for typ in [OSError,subprocess.TimeoutExpired]:
 def fail(*args):raise OSError('test') if typ is OSError else subprocess.TimeoutExpired('test',1)
 module._original_ask=fail
 try:module.bounded_ask(None,'','');raise AssertionError('Missing recovery')
 except module.run.llm_mod.LLMError:pass
module._original_ask=original
print('PASS: strict-bound positive penalty and CLI timeout/OS-error recovery')
