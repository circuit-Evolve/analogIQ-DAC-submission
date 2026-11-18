"""SKY130 bandgap: unchanged five paper targets at every process/supply corner.

Search uses 35 simulations. Full verification adds 15 supply-ramp diagnostics;
those diagnostics never become hidden optimization constraints. All writes are
restricted to the explicitly supplied evaluation output and run-local pack.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import copy, hashlib, importlib.util, json, math, numbers, re, shutil, tarfile, time
import numpy as np

P = Path(__file__).resolve().parent
BASE = P / 'base'
_spec = importlib.util.spec_from_file_location('bandgap_frozen_engine', BASE/'engine.py')
_engine = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_engine)
PROCESSES = ('tt', 'ff', 'ss', 'sf', 'fs')
SUPPLIES = (1.71, 1.8, 1.89)

def _write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')

def _hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

def _finite(value):
    return isinstance(value, numbers.Real) and not isinstance(value, bool) and math.isfinite(value)

def _integrate(y, x):
    return (getattr(np, 'trapezoid', None) or np.trapz)(y, x)

class Task:
    def __init__(self, profile='search_full'):
        self.profile = profile
        self.cfg = json.loads((BASE/'bandgap.json').read_text())
        self.variables = self.cfg['variables']
        seed = self.seed_design()
        for variable in self.variables:
            variable['initial'] = seed[variable['name']]
        self.conditions = [{'id': f'{p.upper()}_{v:.2f}V_27C', 'model_set': p,
                            'supply_V': v, 'temperature_C': 27,
                            'nominal': p=='tt' and v==1.8}
                           for p in PROCESSES for v in SUPPLIES]
        self.cfg['conditions'] = copy.deepcopy(self.conditions)
        self.cfg['description'] = ('All 15 process/supply corners at 27C; unchanged five two-sided paper-target bands. '
            'Temperature sweeps characterize TC; line sweeps shared per process. Scalar feasibility is not startup qualification.')
        for constraint in self.cfg['constraints']:
            constraint['target_origin_conditions'] = constraint['conditions']
            constraint['conditions'] = [c['id'] for c in self.conditions]
            constraint['aggregate'] = 'worst'
            if constraint['name']=='Power_uW':
                constraint['expression'] = '-1e6*average(VS*getData("VDD_SRC:p" ?result "tran"))'
        self.cfg['startup_diagnostic'] = {'search': 'No extra startup job; existing constant-supply transient ripple recorded.',
            'full_verify': 'No nodeset; supply0V at0..1us, ramp toVS by2us, hold through1ms. Last900..1000us analyzed.',
            'optimization_constraint': False}
        self.cfg['evaluation_deadlines_s'] = {'search_full':900, 'full_verify':1800}
        self.cfg['objective'] = None
        self.templates = {n: (BASE/'templates/bandgap'/f'{n}.scs').read_text()
                          for n in ('nominal', 'line', 'temperature')}

    def seed_design(self):
        return dict(json.loads((P/'bandgap_seed.json').read_text())['params'])

    def paper_design(self):
        return self.seed_design()

    def validate(self, design):
        if set(design) != {v['name'] for v in self.variables}:
            raise ValueError('Bandgap design must specify all 19 sizing variables exactly')
        for v in self.variables:
            x = design[v['name']]
            if not _finite(x) or not v['lower'] <= x <= v['upper']:
                raise ValueError('Invalid bandgap sizing: '+v['name'])

    def decks(self, design):
        self.validate(design)
        changes = {}
        for var in self.variables:
            value = design[var['name']] * (1e6 if var['parameter'] in ('w','l') else 1)
            for device in var['devices']:
                changes.setdefault(var['cell'], {}).setdefault(device, {})[var['parameter']] = value
        return {n: _engine.mutate(_engine.clean(text), changes) for n,text in self.templates.items()}

    def plan_text(self):
        text = _engine.clean(self.templates['nominal'])
        dut = re.search(r'(?ms)^subckt bgr_fig3_paper .*?^ends bgr_fig3_paper', text)[0]
        for var in self.variables:
            for device in var['devices']:
                value = f'(<{var["name"]}>*1e6)' if var['parameter'] in ('w','l') else f'<{var["name"]}>'
                pattern = r'(?m)^(\s*'+re.escape(device)+r' \([^\n]+\) [^\n]*?\b'+var['parameter']+r'=)\S+'
                dut, count = re.subn(pattern, lambda m: m[1]+value, dut)
                assert count == 1
        return '// W/L variables use SI meters; model netlist dimensions use microns.\n'+dut

    def corner_deck(self, base, process, supply):
        text = re.sub(r'(?m)^parameters VS=\S+', f'parameters VS={supply:.12g}', base)
        return re.sub(r'section=tt\b', 'section='+process, text)

    def _run(self, text, dest, timeout, deadline=None):
        if (dest/'input.scs').exists():
            raise FileExistsError('Refusing to overwrite bandgap simulation: '+str(dest))
        started = time.monotonic()
        remaining = deadline-started if deadline is not None else None
        effective_timeout = min(timeout,remaining) if remaining is not None else timeout
        if remaining is not None and remaining <= 0:
            dest.mkdir(parents=True, exist_ok=True)
            (dest/'input.scs').write_text(text)
            error = 'Overall bandgap evaluation deadline exhausted; simulator not launched'
            (dest/'stdout.log').write_text(error+'\n')
            rc = 124
        else:
            try:
                rc = _engine.execute(text, dest, timeout=effective_timeout)
                error = None
            except Exception as exc:
                dest.mkdir(parents=True, exist_ok=True)
                rc, error = 1, type(exc).__name__+': '+str(exc)
        item = {'path': str(dest), 'returncode': rc, 'error': error,
                'wall_s': time.monotonic()-started, 'deck_sha256': _hash(text),
                'nominal_only': False, 'simulator_launched': remaining is None or remaining > 0,
                'effective_timeout_s': max(0,effective_timeout)}
        _write(dest/'status.json', item)
        return item

    def _sweep(self, path, axis):
        text = path.read_text().split('VALUE', 1)[1]
        x = np.array([float(a) for a in re.findall(r'^"'+axis+r'" (\S+)', text, re.M)])
        _, waves = _engine.read_wave(path, {'VREF'})
        y = waves['VREF']
        assert len(x)==len(y) and np.all(np.isfinite(y))
        if axis=='VS':
            assert len(x)==91 and abs(x[0]-1.71)<1e-8 and abs(x[-1]-1.89)<1e-8
        else:
            assert len(x)==161 and x[0]==-40 and x[-1]==120
        return x,y

    def _extract(self, jobs, supply, line_value, line_error):
        values = {c['name']: None for c in self.cfg['constraints']}
        values['Line_sensitivity_percent'] = line_value
        diag = {'errors': {}, 'startup_qualification': 'not inferred from DC/scalar feasibility'}
        if line_error:
            diag['errors']['line'] = line_error
        nominal = Path(jobs['nominal']['path'])/'raw'
        vref = None
        try:
            assert jobs['nominal']['returncode']==0, 'nominal simulator failed'
            vref = _engine.dc(nominal/'dcOp.dc')['VREF']
            assert _finite(vref)
            values['Vref_V'] = vref
        except Exception as exc:
            diag['errors']['nominal_dc'] = str(exc)
        try:
            assert jobs['nominal']['returncode']==0, 'nominal simulator failed'
            freq, waves = _engine.read_wave(nominal/'ac.ac', {'VREF'})
            assert len(freq)>0 and abs(freq[0]-1)<1e-8
            values['PSRR_LF_dB'] = float(-20*np.log10(abs(waves['VREF'][0])))
        except Exception as exc:
            diag['errors']['nominal_ac'] = str(exc)
        try:
            assert jobs['nominal']['returncode']==0, 'nominal simulator failed'
            t,waves = _engine.read_wave(nominal/'tran.tran.tran', {'VREF','VDD_SRC:p'})
            assert t[-1]>=30e-6*(1-1e-8)
            values['Power_uW'] = float(-1.8*_integrate(waves['VDD_SRC:p'],t)/(t[-1]-t[0])*1e6)*(supply/1.8)
            diag['constant_supply_tran_vpp_V'] = float(np.ptp(waves['VREF'][t>20e-6]))
            diag['constant_supply_tran_final_V'] = float(waves['VREF'][-1])
        except Exception as exc:
            diag['errors']['nominal_tran'] = str(exc)
        try:
            assert jobs['temperature']['returncode']==0, 'temperature simulator failed'
            x,y = self._sweep(Path(jobs['temperature']['path'])/'raw/dc.dc', 'temp')
            assert vref is not None and vref != 0, 'TC normalization requires valid DC Vref'
            values['TC_19_120_ppm_C'] = float(1e6*np.ptp(y[x>=19])/(vref*101))
        except Exception as exc:
            diag['errors']['temperature'] = str(exc)
        for name,value in list(values.items()):
            if value is not None and not _finite(value):
                values[name] = None
                diag['errors'][name] = 'nonfinite extracted metric'
        return values,diag

    def _startup_deck(self, nominal):
        text = re.sub(r'(?m)^nodeset .*\n', '', nominal)
        text = text.replace('vsource dc=VS mag=1 type=dc', 'vsource type=pwl wave=[0 0 1u 0 2u VS 1m VS]')
        text = re.sub(r'(?m)^tran tran .*$', 'tran tran stop=1m maxstep=100n errpreset=conservative', text)
        text = re.sub(r'(?m)^(ac ac|dcOp dc|finalTimeOP info).*\n', '', text)
        return re.sub(r'(?m)^saveOptions options .*$', 'saveOptions options save=selected\nsave VREF VDD VDD_SRC:p', text)

    def _startup(self, job, dc_vref):
        diagnostic = {'status': 'failed', 'passed': False, 'optimization_constraint': False}
        try:
            assert job['returncode']==0, 'startup simulator failed'
            t,waves = _engine.read_wave(Path(job['path'])/'raw/tran.tran.tran', {'VREF'})
            assert t[-1]>=1e-3*(1-1e-8)
            tail = t>=900e-6
            mean = float(_integrate(waves['VREF'][tail],t[tail])/(t[tail][-1]-t[tail][0]))
            vpp = float(np.ptp(waves['VREF'][tail]))
            relative = abs(mean-dc_vref)/abs(dc_vref) if dc_vref else None
            diagnostic.update(status='completed', tail_mean_V=mean, tail_vpp_V=vpp,
                dc_relative_mismatch=relative, final_V=float(waves['VREF'][-1]),
                passed=bool(1.08<=mean<=1.32 and vpp<=.001 and relative is not None and relative<=.01))
        except Exception as exc:
            diagnostic['error'] = str(exc)
        return diagnostic

    def _finish_raw(self, job, keep_raw):
        raw = Path(job['path'])/'raw'
        if not raw.exists(): return
        if keep_raw:
            archive = raw.parent/'raw.tar.gz'
            if archive.exists(): raise FileExistsError(archive)
            with tarfile.open(archive, 'w:gz', compresslevel=1) as tar:
                tar.add(raw, arcname='raw')
            job['raw_archive'] = str(archive)
        shutil.rmtree(raw)

    def evaluate(self, design, out, keep_raw=False, timeout=180):
        started = time.monotonic()
        budget = 1800 if self.profile=='full_verify' else 900
        deadline = started+budget
        self.validate(design)
        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        if (out/'bandgap_design.json').exists() or (out/'bandgap_results.json').exists():
            raise FileExistsError('Refusing to overwrite bandgap evaluation: '+str(out))
        _write(out/'bandgap_design.json', {'parameters': design,
            'parameters_sha256': _hash(json.dumps(design,sort_keys=True,separators=(',',':'))),
            'profile': self.profile})
        base = self.decks(design)
        full = self.profile=='full_verify'
        rows, invocations = [], 0
        with ThreadPoolExecutor(max_workers=2) as pool:
            for process in PROCESSES:
                line = self._run(self.corner_deck(base['line'],process,1.8), out/f'{process.upper()}_line',timeout,deadline)
                invocations += int(line['simulator_launched'])
                line_value, line_error = None,None
                try:
                    assert line['returncode']==0, 'line simulator failed'
                    _,y = self._sweep(Path(line['path'])/'raw/dc.dc','VS')
                    line_value = float(100*np.ptp(y)/.18)
                except Exception as exc: line_error = str(exc)
                for supply in SUPPLIES:
                    cid = f'{process.upper()}_{supply:.2f}V_27C'
                    dest = out/cid
                    decks = {n:self.corner_deck(base[n],process,supply) for n in ('nominal','temperature')}
                    futures = {n:pool.submit(self._run,text,dest/n,timeout,deadline) for n,text in decks.items()}
                    jobs = {n:f.result() for n,f in futures.items()}
                    invocations += sum(int(job['simulator_launched']) for job in jobs.values())
                    values,diag = self._extract(jobs,supply,line_value,line_error)
                    execution_ok = all(j['returncode']==0 for j in jobs.values()) and line['returncode']==0 and not diag['errors'] and all(x is not None for x in values.values())
                    if full:
                        jobs['startup'] = self._run(self._startup_deck(decks['nominal']),dest/'startup',timeout,deadline)
                        invocations += int(jobs['startup']['simulator_launched'])
                        diag['startup'] = self._startup(jobs['startup'],values['Vref_V'])
                        execution_ok = execution_ok and jobs['startup']['returncode']==0
                    else:
                        diag['startup'] = {'status':'not_run_search', 'optimization_constraint':False,
                            'reason':'Additional 1ms startup simulation is reserved for full_verify; constant-supply ripple is recorded above.'}
                    for job in jobs.values(): self._finish_raw(job,keep_raw)
                    diag['jobs'] = jobs
                    diag['line_job'] = line
                    row = {'id':cid,'process':process,'supply_V':supply,'temperature_C':27,
                           'values':values,'diagnostics':diag,'execution_ok':bool(execution_ok)}
                    _write(dest/'metrics.json',row)
                    rows.append(row)
                self._finish_raw(line,keep_raw)
        result = {'corners':rows,'execution_ok':all(r['execution_ok'] for r in rows),
                  'simulator_invocations':invocations,
                  'scheduled_job_count':50 if full else 35,
                  'evaluation_budget_s':budget,'wall_s':time.monotonic()-started,
                  'deadline_exhausted':time.monotonic()>=deadline,
                  'startup_qualification':'diagnostic only; scalar feasibility does not imply a golden or startup-qualified circuit'}
        _write(out/'bandgap_results.json',result)
        return result
