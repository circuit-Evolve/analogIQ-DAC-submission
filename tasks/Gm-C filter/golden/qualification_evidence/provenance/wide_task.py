"""Private expanded width search bounds; no model, connectivity or target changes."""
from untied import UntiedTask
UPPER={'cm_out_n_w':18e-6,'cross_n_w':2.6e-6,'cross_p_w':7.3e-6}
class WideTask(UntiedTask):
 def __init__(self):
  super().__init__()
  # Both the outer search metadata and inner netlist validator need the same local override.
  # These objects are private in-memory copies. No source task or AnalogIQ file is modified.
  for variables in (self.variables,self.nominal.variables):
   for v in variables:
    if v['name'] in UPPER:v['upper']=UPPER[v['name']]
