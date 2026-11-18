from bandgap_corners import Task as Base, _write
from robust_metrics import apply_directions, startup_score
from pathlib import Path

class Task(Base):
    def __init__(self,profile='search_full'):
        # Every search evaluation includes the existing 1ms startup qualification.
        super().__init__('full_verify')
        apply_directions(self.cfg['constraints'])
        self.cfg['constraints'].append({'name':'Startup_qualification','metric':'Startup_qualification',
            'lower':0,'upper':1,'paper_value':1,'unit':'normalized error','recipe':'startup',
            'source':'Engineering qualification, NOT a numerical paper target',
            'expression':'max(abs(tail_mean_V-1.2)/0.12, tail_vpp_V/0.001, abs(tail_mean_V-dc_vref)/abs(dc_vref)/0.01)',
            'conditions':[c['id'] for c in self.conditions]})
        self.cfg['description'] = 'All15process/supply corners at27C; temperature and line characterization sweeps retained. Better power/TC/line/PSRR accepted; Vref retains paper±10%. Startup qualification is enforced at all15corners.'
        self.cfg['startup_diagnostic']['optimization_constraint']=True
        self.cfg['startup_diagnostic']['search']='Same 1ms supply ramp as final verification; required at every evaluation.'

    def _extract(self,*args):
        values,diag=super()._extract(*args)
        values.pop('Startup_qualification',None)
        return values,diag

    def evaluate(self,design,out,keep_raw=False,timeout=180):
        result=super().evaluate(design,out,keep_raw,timeout)
        for row in result['corners']:
            diag=row['diagnostics']['startup'];diag['optimization_constraint']=True
            row['values']['Startup_qualification']=startup_score(diag)
            row['execution_ok']=row['execution_ok'] and row['values']['Startup_qualification'] is not None
            _write(Path(out)/row['id']/'metrics.json',row)
        result['execution_ok']=all(r['execution_ok'] for r in result['corners'])
        result['startup_qualification']='Required engineering guard at every search and verification corner'
        _write(Path(out)/'bandgap_results.json',result)
        return result
