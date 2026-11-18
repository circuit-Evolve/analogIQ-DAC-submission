def enable_tail_override(T):
 if any(v['name']=='M25_w' for v in T.variables):return
 for dim in ['w','l']:
  T.variables.append({'name':'M25_'+dim,'kind':'real','unit':'m','lower':.4e-6 if dim=='w' else .18e-6,'upper':100e-6 if dim=='w' else 20e-6,'initial':-1.0,'scale':'log','binding':{'cell':'mdvccta_fig2','instances':['M25'],'parameter':dim},'provenance':'User-authorized existingM25 sizing independent ofM26; same acrossallcorecopies/corners'})
 original=T.decks
 def decks(d):return original({**d,**{'M25_'+dim:d.get('M25_'+dim,d['frontend_ntail_'+dim]) for dim in ['w','l']}})
 T.decks=decks

def enable_resistor_override(T):
 import re
 if any(v['name']=='R2_w' for v in T.variables):return
 for job,s in list(T.templates.items()):
  m=re.search(r'(?ms)^subckt grounded_resistor_fig8a .*?^ends grounded_resistor_fig8a',s)
  if not m:continue
  clone=m[0].replace('subckt grounded_resistor_fig8a ','subckt grounded_resistor_fig8a_R2 ').replace('ends grounded_resistor_fig8a','ends grounded_resistor_fig8a_R2')
  s=s[:m.end()]+'\n'+clone+s[m.end():]
  s,n=re.subn(r'(?m)^(\s*R2 \([^\n]+\)\s+)grounded_resistor_fig8a\b',r'\1grounded_resistor_fig8a_R2',s);assert n==1,(job,n);T.templates[job]=s
 for dim in ['w','l']:
  T.variables.append({'name':'R2_'+dim,'kind':'real','unit':'m','lower':.4e-6 if dim=='w' else .18e-6,'upper':100e-6 if dim=='w' else 20e-6,'initial':-1.0,'scale':'log','binding':{'cell':'grounded_resistor_fig8a_R2','instances':['MR1','MR2'],'parameter':dim},'provenance':'IndependentexistingR2geometry, same2MOSconnectivity;R1originalcell unchanged'})
 original=T.decks
 def decks(d):return original({**d,**{'R2_'+dim:d.get('R2_'+dim,d['resistor_'+dim]) for dim in ['w','l']}})
 T.decks=decks

def enable_input_multiplicity(T):
 if any(v['name']=='OTA_input_m' for v in T.variables):return
 T.variables.append({'name':'OTA_input_m','kind':'integer','lower':1,'upper':16,'initial':1,'scale':'linear','binding':{'cell':'mdvccta_fig2','instances':['M1','M2'],'parameter':'m'},'provenance':'Native matchedinputpairmultiplicity, unchangedports/connectivity andPDKper-devicegeometry'})
 original=T.decks
 def decks(d):
  d={**d,'OTA_input_m':d.get('OTA_input_m',1)}
  if int(d['OTA_input_m'])!=d['OTA_input_m']:raise ValueError('OTA_input_m mustbeinteger')
  return original(d)
 T.decks=decks

def enable_pmirror_multiplicity(T):
 if any(v['name']=='OTA_pmirror_m' for v in T.variables):return
 T.variables.append({'name':'OTA_pmirror_m','kind':'integer','lower':1,'upper':8,'initial':1,'scale':'linear','binding':{'cell':'mdvccta_fig2','instances':['M3','M4','M7','M8','M9'],'parameter':'m'},'provenance':'Native equal multiplicity onallmatchedPMOSOTAcurrentmirrorbranches'})
 original=T.decks
 def decks(d):
  d={**d,'OTA_pmirror_m':d.get('OTA_pmirror_m',1)}
  if int(d['OTA_pmirror_m'])!=d['OTA_pmirror_m']:raise ValueError('OTA_pmirror_m must beinteger')
  return original(d)
 T.decks=decks

def enable_front_output_multiplicity(T):
 if any(v['name']=='frontend_output_m' for v in T.variables):return
 T.variables.append({'name':'frontend_output_m','kind':'integer','lower':1,'upper':8,'initial':1,'scale':'linear','binding':{'cell':'mdvccta_fig2','instances':['M21','M22','M23','M24','M27','M28','M29','M30'],'parameter':'m'},'provenance':'Equal native multiplicity on all four matched frontend output branches; same per-device bins and all ports retained'})
 original=T.decks
 def decks(d):
  d={**d,'frontend_output_m':d.get('frontend_output_m',1)}
  if int(d['frontend_output_m'])!=d['frontend_output_m']:raise ValueError('frontend_output_m must be integer')
  return original(d)
 T.decks=decks

def enable_A1_ota_override(T):
 import re
 from miso_engine import mutate
 cell='mdvccta_fig2_A1'
 if any(v['name'].startswith('A1_') for v in T.variables):return
 for job,s in list(T.templates.items()):
  if 'subckt miso_fig3 ' not in s:continue
  m=re.search(r'(?ms)^subckt mdvccta_fig2 .*?^ends mdvccta_fig2',s);assert m
  clone=m[0].replace('subckt mdvccta_fig2 ','subckt '+cell+' ').replace('ends mdvccta_fig2','ends '+cell)
  s=s[:m.end()]+'\n'+clone+s[m.end():]
  s,n=re.subn(r'(?m)^(\s*A1 \([^\n]+\)\s+)mdvccta_fig2\b',r'\1'+cell,s);assert n==1,(job,n);T.templates[job]=s
 shared=[];ota=[]
 for v in list(T.variables):
  if v['name'].startswith('ota_') or v['name'] in ['OTA_IBIAS','OTA_input_m','OTA_pmirror_m']:
   q=dict(v);q['name']='A1_'+v['name'];q['binding']={**v['binding'],'cell':cell};q['provenance']='Existing A1 OTA independent sizing, identical device/port connectivity; A2 retains common base OTA';T.variables.append(q);ota.append(v['name'])
  elif v['name'].startswith(('frontend_','M25_')):shared.append(v)
 original=T.decks
 def decks(d):
  d={**d,**{'A1_'+k:d.get('A1_'+k,d.get(k,d['ota_nmirror_'+k[-1]]) if k.startswith('ota_ndiode_') else d[k]) for k in ota}}
  for k in ['A1_OTA_input_m','A1_OTA_pmirror_m']:
   if k in d and int(d[k])!=d[k]:raise ValueError(k+' must be integer')
  out=original(d)
  changes={}
  for v in shared:
   for inst in v['binding']['instances']:changes.setdefault(inst,{})[v['binding']['parameter']]=d[v['name']]
  for job,s in list(out.items()):
   if 'subckt '+cell+' ' in s:out[job]=mutate(s,{cell:changes})
  return out
 T.decks=decks

def enable_R1_multiplicity(T):
 if any(v['name']=='R1_m' for v in T.variables):return
 T.variables.append({'name':'R1_m','kind':'integer','lower':1,'upper':32,'initial':1,'scale':'linear','binding':{'cell':'grounded_resistor_fig8a','instances':['MR1','MR2'],'parameter':'m'},'provenance':'Equal native multiplicity on the existing two MOS R1 devices; R2 independent clone unchanged'})
 original=T.decks
 def decks(d):
  d={**d,'R1_m':d.get('R1_m',1)}
  if int(d['R1_m'])!=d['R1_m']:raise ValueError('R1_m must be integer')
  return original(d)
 T.decks=decks

def enable_ndiode_override(T):
 if any(v['name']=='ota_ndiode_w' for v in T.variables):return
 for dim in ['w','l']:
  T.variables.append({'name':'ota_ndiode_'+dim,'kind':'real','lower':.4e-6 if dim=='w' else .18e-6,'upper':100e-6 if dim=='w' else 20e-6,'initial':-1,'scale':'log','binding':{'cell':'mdvccta_fig2','instances':['M11','M14'],'parameter':dim},'provenance':'Separate existing matched NMOS diode pair sizing; M10/M12/M13 output copies remain matched'})
 original=T.decks
 def decks(d):return original({**d,**{'ota_ndiode_'+dim:d.get('ota_ndiode_'+dim,d['ota_nmirror_'+dim]) for dim in ['w','l']}})
 T.decks=decks
