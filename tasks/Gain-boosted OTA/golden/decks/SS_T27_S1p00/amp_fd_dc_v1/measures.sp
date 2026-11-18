* analogiq 0.1.0 testbench - generated, do not edit
* task gbfc21_task_001  topology gbfc21
* recipe amp_fd_dc_v1 v1  condition SS_T27_S1p00 (models SS, 27 C, supply 1.8 V)
* request golden_gbfc21_task_001  candidate b2e5c7227f264828
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure dc p_sup find par('-v(vdd)*i(VSUP)+-v(vss)*i(VNEG)') at=0.8
.measure dc v_cm find par('(v(out)+v(outn))/2') at=0.8
.measure dc v_od find par('v(out)-v(outn)') at=0.8
