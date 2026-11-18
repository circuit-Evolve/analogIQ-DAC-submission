"""MISO process-corner evaluator: active constraints come from local miso_corners.json."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,math,re,os,signal,subprocess,time,shutil,tarfile
from miso_nominal import Task as NominalTask
from miso_engine import execute
HERE=Path(__file__).resolve().parent
RUN_ROOT=HERE.parent.resolve()

def json_safe(value):
    if isinstance(value,float) and not math.isfinite(value):return None
    if isinstance(value,dict):return {k:json_safe(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [json_safe(v) for v in value]
    return value

def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(json_safe(value),indent=2,allow_nan=False)+'\n');temp.replace(path)
def digest(text):return hashlib.sha256(text.encode()).hexdigest()

class Task(NominalTask):
    def __init__(self,profile='search_full'):
        super().__init__('search_full')
        self.profile=profile
        self.cfg=json.loads((HERE/'miso_corners.json').read_text())
        self.variables=self.cfg['variables']
        self.templates={p.stem:p.read_text() for p in sorted((HERE/'miso_templates').glob('*.scs'))}
        self.score_jobs=sorted({c['recipe'] for c in self.cfg['constraints']})
        self.corners=self.cfg['conditions']
        self._seed=json.loads((HERE/'miso_seed.json').read_text())
    def seed_design(self):return dict(self._seed)
    def paper_design(self):return self.seed_design()
    def _budget_seconds(self):return 1800.0 if self.profile=='full_verify' else 900.0
    def _remaining(self):
        now=time.monotonic()
        return max(0.0,getattr(self,'_eval_deadline',now+self._budget_seconds())-now)
    def _ocean(self,paths,diagnostics):
        if self._remaining()<=0:
            diagnostics['ocean']={'returncode':124,'deadline_exhausted':True,'launched':False,'error':'Overall evaluation deadline exhausted before Cadence extraction'}
            return {}
        expressions={c['name']:(c['recipe'],c['expression']) for c in self.cfg['constraints'] if c['name'] in ('MISO_BP_frequency','LP_THD','BP_THD')}
        present={name:(job,expr) for name,(job,expr) in expressions.items() if job in paths}
        if not present:return {}
        work=Path(next(iter(paths.values()))).resolve().parent/'ocean';work.mkdir(exist_ok=True)
        (work/'cds.lib').write_text('# Isolated read-only results extraction; no shared library.\n')
        lines=[]
        for name,(job,expr) in present.items():
            raw=Path(paths[job]).resolve()/'raw'
            lines+=['openResults('+json.dumps(str(raw))+')','v=errset('+expr+' t)',f'when(v && numberp(car(v)) printf("MISO_SCALAR {name} %.17g\\n" car(v)))']
        lines.append('exit()');script=work/'extract.ocn';script.write_text('\n'.join(lines)+'\n')
        started=time.monotonic()
        remaining=min(90.0,self._remaining())
        if remaining<=0:
            diagnostics['ocean']={'returncode':124,'deadline_exhausted':True,'launched':False,'error':'Overall evaluation deadline exhausted before Cadence extraction'}
            write(work/'status.json',diagnostics['ocean'])
            return {}
        with (work/'stdout.log').open('w') as f:
            p=subprocess.Popen(['/opt/cadence/bin/virtuoso','-nograph','-nocdsinit','-cdslib',str(work/'cds.lib'),'-restore',str(script),'-log',str(work/'virtuoso.log')],cwd=work,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
            try:rc=p.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid,signal.SIGTERM)
                try:p.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
                rc=124
        text=(work/'stdout.log').read_text(errors='replace')
        if (work/'virtuoso.log').exists():text+='\n'+(work/'virtuoso.log').read_text(errors='replace')
        diagnostics['ocean']={'returncode':rc,'launched':True,'timeout_seconds':remaining,'deadline_exhausted':self._remaining()<=0,'runtime_seconds':time.monotonic()-started,'method':'Unchanged Cadence deriv/cross and thd builtins;8192samples;frozen windows','interpolation_warning':'interpolated' in text,'log':text[-16000:],'evidence_directory':str(work)}
        write(work/'status.json',diagnostics['ocean'])
        return {name:float(value) for name,value in re.findall(r'MISO_SCALAR (\w+) ([-+0-9.eE]+)',text)} if rc==0 else {}
    def _owned(self,out):
        out=Path(out).resolve()
        if not out.is_relative_to(RUN_ROOT):raise ValueError('MISO outputs must stay inside new run root')
        return out
    def _evaluate_corner(self,design,out,corner,keep_raw=False,timeout=180):
        if not hasattr(self,'_eval_deadline'):self._eval_deadline=time.monotonic()+self._budget_seconds()
        out=self._owned(out)
        if out.exists() and any(out.iterdir()):raise FileExistsError('Refusing nonempty MISO candidate corner '+str(out))
        out.mkdir(parents=True,exist_ok=True)
        decks=self.decks(design)
        write(out/'design.json',{'parameters':design,'corner':corner})
        def one(item):
            name,nominal=item
            deck,n=re.subn(r'(include "<PDK_ROOT>/gpdk180/models/spectre/gpdk.scs" section=)NN',lambda m:m[1]+corner['model_section'],nominal)
            if n!=1:raise ValueError('Expected one GPDK include')
            d=out/name;started=time.monotonic();error=None;launched=False
            remaining=min(float(timeout),self._remaining())
            if remaining<=0:
                d.mkdir(parents=True,exist_ok=True);(d/'input.scs').write_text(deck)
                rc=124;error='Overall evaluation deadline exhausted before Spectre launch'
                (d/'stdout.log').write_text(error+'\n')
            else:
                try:
                    launched=True;rc=execute(deck,d,timeout=remaining)
                except Exception as exc:rc=-1;error=type(exc).__name__+': '+str(exc)
            warnings=[]
            if (d/'spectre.log').exists():
                log=(d/'spectre.log').read_text(errors='replace')
                warnings=[line for line in log.splitlines() if re.search(r'warning|ERROR|FATAL',line,re.I)]
            state={'job':name,'returncode':rc,'launched':launched,'timeout_seconds':remaining,'deadline_exhausted':self._remaining()<=0,'error':error,'runtime_seconds':time.monotonic()-started,'corner':corner['id'],'model_section':corner['model_section'],'netlist_sha256':digest(deck),'warnings':warnings}
            write(d/'status.json',state);return state
        jobs=[];values={c['metric']:None for c in self.cfg['constraints']};diagnostics={};extract_error=None
        try:
            with ThreadPoolExecutor(max_workers=getattr(self,'max_workers',4)) as pool:jobs=list(pool.map(one,decks.items()))
            paths={j['job']:out/j['job'] for j in jobs if j['returncode']==0}
            try:values,diagnostics=self.extract(paths)
            except Exception as exc:extract_error=type(exc).__name__+': '+str(exc)
            by_job={j['job']:j for j in jobs};status={}
            for c in self.cfg['constraints']:
                name=c['metric'];v=values.get(name)
                if by_job[c['recipe']]['returncode']!=0:values[name]=None;status[name]='simulation_failure'
                elif v is None or not math.isfinite(float(v)):values[name]=None;status[name]='missing_metric'
                else:values[name]=float(v);status[name]='measured'
            diagnostics.update({'jobs':jobs,'metric_execution_status':status,'extraction_error':extract_error,'measurement_profile':'all9_user_retained_scalars_all5_paper_processes'})
            ok=all(j['returncode']==0 for j in jobs) and extract_error is None and all(v is not None for v in values.values())
            result=json_safe({'id':corner['id'],'condition':corner,'values':values,'diagnostics':diagnostics,'execution_ok':ok})
            write(out/'metrics.json',result)
            return result
        finally:
            raw=[p for p in out.glob('*/raw') if p.is_dir()]
            if keep_raw and raw:
                archive=out/'raw.tar.gz'
                with tarfile.open(archive,'w:gz',compresslevel=1) as tar:
                    for p in raw:tar.add(p,arcname=str(p.relative_to(out)))
                write(out/'raw_archive.json',{'archive':archive.name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'restore':'tar -xzf raw.tar.gz in this corner directory','members':[str(p.relative_to(out)) for p in raw]})
            for p in raw:shutil.rmtree(p)
    def evaluate(self,design,out:Path,keep_raw=False,timeout=180):
        self._eval_deadline=time.monotonic()+self._budget_seconds()
        out=self._owned(out)
        if out.exists() and any(out.iterdir()):raise FileExistsError('Refusing nonempty MISO evaluation '+str(out))
        self.decks(design)  # Validate before creating evaluation artifacts.
        out.mkdir(parents=True,exist_ok=True);write(out/'design.json',{'parameters':design,'seed_source':'miso_seed.json'})
        corners=[]
        for corner in self.corners:
            if (out/'STOP_AFTER_CURRENT_CORNER').exists():break
            corners.append(self._evaluate_corner(design,out/corner['id'],corner,keep_raw,timeout))
        result={'corners':corners,'execution_ok':all(c['execution_ok'] for c in corners),'simulator_invocations':sum(j['launched'] for c in corners for j in c['diagnostics']['jobs']),'evaluation_budget_seconds':self._budget_seconds(),'deadline_exhausted':self._remaining()<=0}
        write(out/'metrics.json',result)
        return result
