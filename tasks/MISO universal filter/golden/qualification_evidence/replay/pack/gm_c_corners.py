"""Fixed 45-corner Gm-C evaluator; original six scalar metrics, no tuning per corner."""
from pathlib import Path
import sys,json,re,time,subprocess,os,signal,hashlib,gzip,shutil,concurrent.futures,copy
import numpy as np
HERE=Path(__file__).resolve().parent
BASE=HERE/'base'
if str(BASE) not in sys.path:sys.path.insert(0,str(BASE))
from gm_base_task import Task as NominalTask,validate_wave
from engine import read_wave

def gm_dump(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def gm_sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def gm_replace(deck,pattern,replacement,count=1):
    value,n=re.subn(pattern,replacement,deck)
    if n!=count:raise ValueError(f'Gm-C corner binding failed: {pattern}: {n}')
    return value

class Task:
    def __init__(self,profile='search_full'):
        if profile not in ('search_full','full','full_verify','verification','final'):raise ValueError('Unsupported Gm-C corner profile')
        self.profile=profile
        self.nominal=NominalTask('search_full')
        self.cfg=copy.deepcopy(self.nominal.cfg)
        self._seed=json.loads((HERE/'gm_seed.json').read_text())
        self.cfg['conditions']=[{'id':f'{p}_V{v:.1f}_T{t:+d}','model_set':p,'process':p,'supply_V':v,'temperature_C':t,'VREF_V':v/2,'input_common_mode_V':v/2,'nominal':p=='NN' and v==1 and t==27} for p in ['NN','SS','SF','FS','FF'] for v in [.9,1.,1.1] for t in [-40,27,85]]
        ids=[c['id'] for c in self.cfg['conditions']]
        for c in self.cfg['constraints']:c['conditions']=ids.copy();c['aggregate']='worst'
        for v in self.cfg['variables']:v['initial']=self._seed[v['name']]
        self.variables=self.cfg['variables']
        self.cfg['operating_conditions']={'processes':['NN','SS','SF','FS','FF'],'supply_V':[.9,1.,1.1],'temperature_C':[-40,27,85],'VREF_and_input_common_mode':'VDD/2','VT':'candidate vt_bias_V fixed across all corners'}
        self.cfg['description']='Saved-best-start Gm-C optimization across all45 fixed PVT corners; original six scalar bands. Four-OTA reconstruction, no exact paper reproduction claim.'
        self.cfg['execution_limits']={'search_evaluation_s':900,'full_verification_s':1800,'scope':'infrastructure deadline, not a paper acceptance constraint','process_termination_grace_s':5}
        self.cfg['measurement_scope']='Original six comparable scalars only; nonlinear and response shape remain diagnostic-only and add no acceptance target.'
        self.cfg['assumptions']['current_run_override']='Historical nominal and paper-seed statements refer to original setup. Current run uses saved-best seed, original31variable bounds and all45PVT conditions; candidate VT optimized globally but fixed across each candidate corner grid.'

    def seed_design(self):return copy.deepcopy(self._seed)
    def paper_design(self):return self.seed_design()
    def plan_text(self):return '// All45 PVT corners; VREF/input common-mode track half-supply. Candidate VT fixed across corners.\n'+self.nominal.plan_text()

    def corner_decks(self,design,corner):
        decks=self.nominal.decks(design)
        output={}
        for job,deck in decks.items():
            deck=gm_replace(deck,r'section=NN\b','section='+corner['process'])
            deck=gm_replace(deck,r'(?m)^VDD_SRC \(VDD 0\) vsource dc=1$',f"VDD_SRC (VDD 0) vsource dc={corner['supply_V']:.12g}")
            deck=gm_replace(deck,r'(?m)^VREF_SRC \(VREF 0\) vsource dc=\.5$',f"VREF_SRC (VREF 0) vsource dc={corner['VREF_V']:.12g}")
            deck=gm_replace(deck,r'(?m)^(VIN[PM] \(VI[PM] 0\) vsource dc=)\.5',lambda m:m[1]+f"{corner['input_common_mode_V']:.12g}",2)
            deck=gm_replace(deck,r'\btemp=27\b',f"temp={corner['temperature_C']}")
            output[job]=deck
        return output

    def _simulate(self,item,out,corner,timeout,deadline=None):
        job,deck=item;d=out/job;d.mkdir(parents=True,exist_ok=True);(d/'input.scs').write_text(deck)
        start=time.monotonic();rc=127;error=None;launched=False
        cmd=['/opt/cadence/bin/spectre','input.scs','-format','psfascii','-raw','raw','+log','spectre.log']
        effective_timeout=float(timeout)
        if deadline is not None:effective_timeout=min(effective_timeout,max(0.,deadline-time.monotonic()))
        if effective_timeout<=0:
            rc=124;error='Evaluator deadline exhausted before launch'
            (d/'stdout.log').write_text(error+'\n')
        else:
            try:
                with (d/'stdout.log').open('w') as log:
                    p=subprocess.Popen(cmd,cwd=d,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);launched=True
                    try:rc=p.wait(timeout=effective_timeout)
                    except subprocess.TimeoutExpired:
                        try:os.killpg(p.pid,signal.SIGTERM)
                        except ProcessLookupError:pass
                        try:p.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            try:os.killpg(p.pid,signal.SIGKILL)
                            except ProcessLookupError:pass
                            p.wait()
                        rc=124;error='Spectre timeout or evaluator deadline'
            except OSError as e:error=str(e)
        status={'returncode':rc,'error':error,'wall_s':time.monotonic()-start,'corner':corner,'job':job,'deck_sha256':gm_sha(d/'input.scs'),'command':cmd,'nominal_only':False,'launched':launched,'effective_timeout_s':effective_timeout,'evaluator_deadline_monotonic':deadline}
        gm_dump(d/'status.json',status)
        return job,d,status

    def _shape(self,path,values):
        f,v=read_wave(path/'raw/ac.ac',{'VOP','VOM'});h=v['VOP']-v['VOM'];validate_wave(f,h)
        if not np.isclose(f[0],1) or not np.isclose(f[-1],1e11):raise ValueError('Incomplete full filter AC sweep')
        a=abs(h)
        if np.any(a<=0):raise ValueError('Zero filter transfer sample')
        db=20*np.log10(a);threshold=a[0]/np.sqrt(2)
        falls=np.flatnonzero((a[:-1]>=threshold)&(a[1:]<threshold));rises=np.flatnonzero((a[:-1]<threshold)&(a[1:]>=threshold))
        shape={'full_four_OTA_filter':True,'ac_start_Hz':float(f[0]),'ac_stop_Hz':float(f[-1]),'samples':len(f),'dc_gain_dB':float(db[0]),'peak_gain_dB':float(max(db)),'peaking_above_dc_dB':float(max(db)-db[0]),'peak_frequency_Hz':float(f[np.argmax(db)]),'falling_relative_3dB_crossings':len(falls),'rising_relative_3dB_crossings':len(rises),'cutoff_valid':values['Filter_cutoff_Hz'] is not None and len(falls)>0,'lowpass_endpoint_below_relative_3dB':bool(a[-1]<threshold),'response_order_verified':False,'stability_verified':False,'diagnostic_only':True,'note':'First falling DC-relative crossing retained. Peaking and repeated crossings are diagnostic; no extra optimization acceptance targets.'}
        np.savetxt(path.parent/'filter_response.csv',np.column_stack([f,db,np.unwrap(np.angle(h))*180/np.pi]),delimiter=',',header='frequency_Hz,gain_dB,phase_deg',comments='')
        return shape

    def _retain_or_prune(self,out,keep_raw):
        evidence=[]
        for raw in out.glob('*/raw'):
            if keep_raw:
                for p in raw.iterdir():
                    if p.is_file() and p.stat().st_size>100000:
                        h=gm_sha(p);n=p.stat().st_size;gz=p.with_name(p.name+'.gz')
                        with p.open('rb') as src,gzip.open(gz,'wb',compresslevel=3) as dst:shutil.copyfileobj(src,dst)
                        with gzip.open(gz,'rb') as f:
                            if hashlib.sha256(f.read()).hexdigest()!=h:raise IOError('Raw compression hash mismatch')
                        evidence.append({'original':str(p.relative_to(out)),'gzip':str(gz.relative_to(out)),'uncompressed_sha256':h,'uncompressed_bytes':n})
                        p.unlink()
            else:shutil.rmtree(raw)
        gm_dump(out/'raw_retention.json',{'keep_raw':keep_raw,'policy':'gzip large raw after verified roundtrip' if keep_raw else 'raw removed after metric extraction; decks/logs/status/results retained','compressed_files':evidence})

    def evaluate_corner(self,design,corner,out,keep_raw=False,timeout=180,pool=None,deadline=None):
        out=Path(out);out.mkdir(parents=True,exist_ok=True);decks=self.corner_decks(design,corner)
        owns=pool is None
        if owns:pool=concurrent.futures.ThreadPoolExecutor(max_workers=2)
        try:jobs=list(pool.map(lambda item:self._simulate(item,out,corner,timeout,deadline),decks.items()))
        finally:
            if owns:pool.shutdown()
        paths={job:str(d) for job,d,s in jobs if s['returncode']==0}
        values,diag=self.nominal.extract(paths);diag.update(nominal_only=False,corner=corner,profile=self.profile)
        try:
            if 'FILTER_AC_NOISE' not in paths:raise ValueError('Filter simulation unavailable')
            diag['filter_response']=self._shape(Path(paths['FILTER_AC_NOISE']),values)
        except Exception as e:
            diag['errors']['full_filter_response']=str(e)
            # Missing/invalid full sweep means cutoff is not a verified scalar.
            values['Filter_cutoff_Hz']=None
        diag['jobs']={job:status for job,d,status in jobs}
        ok=len(paths)==3 and not diag['errors'] and all(v is not None and np.isfinite(v) for v in values.values())
        result={'id':corner['id'],'values':values,'diagnostics':diag,'execution_ok':bool(ok)}
        gm_dump(out/'results.json',result)
        self._retain_or_prune(out,keep_raw)
        return result

    def evaluate(self,design,out:Path,keep_raw=False,timeout=180):
        evaluator_budget_s=900 if self.profile=='search_full' else 1800
        deadline=time.monotonic()+evaluator_budget_s
        # Validate full sizing before creating simulations or partial candidate evidence.
        self.nominal.decks(design)
        out=Path(out);out.mkdir(parents=True,exist_ok=True)
        gm_dump(out/'design.json',design);gm_dump(out/'conditions.json',self.cfg['conditions'])
        gm_dump(out/'provenance.json',{'seed_provenance':json.loads((HERE/'gm_provenance.json').read_text()),'design_sha256':gm_sha(out/'design.json'),'six_metric_definitions_unchanged':True,'all45corners':True,'candidate_VT_fixed_across_corners':design['vt_bias_V']})
        corners=[]
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            for corner in self.cfg['conditions']:
                result=self.evaluate_corner(design,corner,out/corner['id'],keep_raw,timeout,pool,deadline)
                corners.append(result)
                gm_dump(out/'progress.json',{'completed':len(corners),'planned':45,'last_corner':corner['id'],'execution_ok_so_far':all(r['execution_ok'] for r in corners)})
        result={'corners':corners,'execution_ok':all(c['execution_ok'] for c in corners),'simulator_invocations':sum(j['launched'] for c in corners for j in c['diagnostics']['jobs'].values()),'planned_simulator_invocations':len(corners)*3,'evaluator_budget_s':evaluator_budget_s,'evaluator_deadline_exhausted':time.monotonic()>=deadline}
        gm_dump(out/'evaluation.json',result)
        return result
