* analogiq 0.1.0 testbench - generated, do not edit
* task fcrobust01_task_001  topology fcrobust01_arxiv_2207
* recipe amp_fd_ol_v1 v3  condition FF_T100_S0p89 (models FF, 100 C, supply 1.6 V)
* request golden_fcrobust01_task_001  candidate eaebf39efa854825
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure ac g_lf find vdb(od) at=1.0
.measure ac f3db when vdb(od)='g_lf-3' fall=1
.measure ac ugf when vdb(od)=0 fall=1
.measure ac pm find vp(odn) when vdb(od)=0 fall=1
.measure ac g_180 find vdb(od) when vp(odn)=0 fall=1
.measure ac ph_lf find vp(od) at=1.0
.measure ac g01 find vdb(od) at=1.0
