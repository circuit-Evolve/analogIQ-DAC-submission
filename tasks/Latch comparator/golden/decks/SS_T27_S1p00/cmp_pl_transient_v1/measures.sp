* analogiq 0.1.0 testbench - generated, do not edit
* task cmppl24_task_001  topology cmppl24_upcon2022
* recipe cmp_pl_transient_v1 v2  condition SS_T27_S1p00 (models SS, 27 C, supply 1.8 V)
* request golden_cmppl24_task_001  candidate eca5dc39e87484f5
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs.
* Results: input.measure. Raw samples only; pass/fail rules are applied by analogiq.
.option measdgt=10
.measure tran chk_clk_edge when v(clk)='0.5*vdd_v' rise=1
