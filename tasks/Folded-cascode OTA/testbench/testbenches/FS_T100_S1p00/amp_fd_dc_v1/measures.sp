* analogiq 0.1.0 testbench - generated, do not edit
* task fcrobust01_task_001  topology fcrobust01_arxiv_2207
* recipe amp_fd_dc_v1 v1  condition FS_T100_S1p00 (models FS, 100 C, supply 1.8 V)
* request fcrobust01_task_001__plan  candidate bb6894fc5155c810
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure dc p_sup find par('-v(vdd)*i(VSUP)+-v(vss)*i(VNEG)') at=1.2
.measure dc v_cm find par('(v(out)+v(outn))/2') at=1.2
.measure dc v_od find par('v(out)-v(outn)') at=1.2
