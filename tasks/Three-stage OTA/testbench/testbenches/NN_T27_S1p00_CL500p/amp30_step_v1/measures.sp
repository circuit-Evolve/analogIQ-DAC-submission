* analogiq 0.1.0 testbench - generated, do not edit
* task ota3s24_task_001  topology ota3s24
* recipe amp30_step_v1 v1  condition NN_T27_S1p00_CL500p (models NN, 27 C, supply 1.8 V)
* request ota3s24_task_001__plan  candidate 25f7ea5cdf3edbba
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure tran v_beg_1 find v(out) at=1.9999000000000003e-05
.measure tran v_end_1 find v(out) at=3.9999e-05
.measure tran sr_1 trig v(out) val='v_beg_1+0.2*(v_end_1-v_beg_1)' rise=1 td=2e-05 targ v(out) val='v_beg_1+0.8*(v_end_1-v_beg_1)' rise=1 td=2e-05
.measure tran x_hi_1 when v(out)='(vc+og*step/2)+band' cross=last from=2e-05 to=3.9999e-05
.measure tran x_lo_1 when v(out)='(vc+og*step/2)-band' cross=last from=2e-05 to=3.9999e-05
.measure tran y_hi_1 when v(out)='v_end_1+band' cross=last from=2e-05 to=3.9999e-05
.measure tran y_lo_1 when v(out)='v_end_1-band' cross=last from=2e-05 to=3.9999e-05
.measure tran pk_1 max v(out) from=2e-05 to=3.9999e-05
.measure tran tg_1 min v(out) from=2e-05 to=3.9999e-05
.measure tran v_beg_2 find v(out) at=3.9999e-05
.measure tran v_end_2 find v(out) at=5.9999000000000006e-05
.measure tran sr_2 trig v(out) val='v_beg_2+0.2*(v_end_2-v_beg_2)' fall=1 td=4e-05 targ v(out) val='v_beg_2+0.8*(v_end_2-v_beg_2)' fall=1 td=4e-05
.measure tran x_hi_2 when v(out)='(vc-og*step/2)+band' cross=last from=4e-05 to=5.9999000000000006e-05
.measure tran x_lo_2 when v(out)='(vc-og*step/2)-band' cross=last from=4e-05 to=5.9999000000000006e-05
.measure tran y_hi_2 when v(out)='v_end_2+band' cross=last from=4e-05 to=5.9999000000000006e-05
.measure tran y_lo_2 when v(out)='v_end_2-band' cross=last from=4e-05 to=5.9999000000000006e-05
.measure tran pk_2 max v(out) from=4e-05 to=5.9999000000000006e-05
.measure tran tg_2 min v(out) from=4e-05 to=5.9999000000000006e-05
