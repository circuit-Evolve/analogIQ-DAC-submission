* analogiq 0.1.0 testbench - generated, do not edit
* task tia02_task_001  topology tia02_singh_2018
* recipe tia_ac_v1 v1  condition NN_T27_S1p00 (models NN, 27 C, supply 1.8 V)
* request tia02_task_001__plan  candidate b4979bc7899dfdaa
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure ac zt find vdb(out) at=1000000.0
.measure ac f3 when vdb(out)='zt-3' fall=1
