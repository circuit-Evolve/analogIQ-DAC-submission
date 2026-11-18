* analogiq 0.1.0 testbench - generated, do not edit
* task ldo24c_conventional_task_001  topology ldo24c_conventional
* recipe ldo_line_step_v1 v1  condition NN_T27_S1p00 (models NN, 27 C, supply 1.7 V)
* request golden_ldo24c_conventional_task_001  candidate 92f6c13c43387af9
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure tran v_pre1 find v(out) at=9.99e-05
.measure tran v_max1 max v(out) from=0.0001 to=0.0001999
.measure tran v_min1 min v(out) from=0.0001 to=0.0001999
.measure tran v_end1 find v(out) at=0.0001999
.measure tran v_mid1 find v(out) at=0.00019
.measure tran xa1 when v(out)='v_end1+0.00015' cross=last from=0.0001 to=0.0001999
.measure tran xb1 when v(out)='v_end1-0.00015' cross=last from=0.0001 to=0.0001999
.measure tran v_max2 max v(out) from=0.0002 to=0.0002999
.measure tran v_min2 min v(out) from=0.0002 to=0.0002999
.measure tran v_end2 find v(out) at=0.0002999
.measure tran v_mid2 find v(out) at=0.00029
.measure tran xa2 when v(out)='v_end2+0.00015' cross=last from=0.0002 to=0.0002999
.measure tran xb2 when v(out)='v_end2-0.00015' cross=last from=0.0002 to=0.0002999
