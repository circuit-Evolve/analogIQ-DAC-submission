* analogiq 0.1.0 testbench - generated, do not edit
* task ota3s24_task_001  topology ota3s24
* recipe amp_ol_v1 v3  condition NN_T27_S1p00_CL50n (models NN, 27 C, supply 1.8 V)
* request golden_ota3s24_task_001  candidate 4831fd3120c8d255
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure ac g_lf find vdb(out) at=1.0
.measure ac f3db when vdb(out)='g_lf-3' fall=1
.measure ac ugf when vdb(out)=0 fall=1
.measure ac pm find vp(outinv) when vdb(out)=0 fall=1
.measure ac g_180 find vdb(out) when vp(outinv)=0 fall=1
.measure ac ph_lf find vp(out) at=1.0
