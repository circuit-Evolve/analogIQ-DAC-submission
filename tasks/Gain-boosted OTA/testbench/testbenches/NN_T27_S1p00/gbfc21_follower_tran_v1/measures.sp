* analogiq 0.1.0 testbench - generated, do not edit
* task gbfc21_task_001  topology gbfc21
* recipe gbfc21_follower_tran_v1 v1  condition NN_T27_S1p00 (models NN, 27 C, supply 1.8 V)
* request gbfc21_task_001__plan  candidate 3a14c89e438419ec
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure tran v_beg_r find v(od) at=4.999e-07
.measure tran v_end_r find v(od) at=9.999e-07
.measure tran sr_r trig v(od) val='v_beg_r+0.2*(v_end_r-v_beg_r)' rise=1 td=5e-07 targ v(od) val='v_beg_r+0.8*(v_end_r-v_beg_r)' rise=1 td=5e-07
.measure tran x_hi_r when v(od)='v_end_r+0.01*abs(v_end_r-v_beg_r)' cross=last from=5e-07 to=9.999e-07
.measure tran x_lo_r when v(od)='v_end_r-0.01*abs(v_end_r-v_beg_r)' cross=last from=5e-07 to=9.999e-07
.measure tran vmax_r max v(od) from=5e-07 to=9.999e-07
.measure tran v_beg_f find v(od) at=9.999e-07
.measure tran v_end_f find v(od) at=1.4999e-06
.measure tran sr_f trig v(od) val='v_beg_f+0.2*(v_end_f-v_beg_f)' fall=1 td=1e-06 targ v(od) val='v_beg_f+0.8*(v_end_f-v_beg_f)' fall=1 td=1e-06
.measure tran x_hi_f when v(od)='v_end_f+0.01*abs(v_end_f-v_beg_f)' cross=last from=1e-06 to=1.4999e-06
.measure tran x_lo_f when v(od)='v_end_f-0.01*abs(v_end_f-v_beg_f)' cross=last from=1e-06 to=1.4999e-06
.measure tran vmin_f min v(od) from=1e-06 to=1.4999e-06
