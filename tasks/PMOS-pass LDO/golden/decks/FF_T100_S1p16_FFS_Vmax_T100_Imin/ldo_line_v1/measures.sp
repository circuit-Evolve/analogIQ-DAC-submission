* analogiq 0.1.0 testbench - generated, do not edit
* task ldo24c_conventional_task_001  topology ldo24c_conventional
* recipe ldo_line_v1 v4  condition FF_T100_S1p16_FFS_Vmax_T100_Imin (models FF, 100 C, supply 1.98 V)
* request golden_ldo24c_conventional_task_001  candidate 92f6c13c43387af9
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure dc vout_nom find v(out) at=1.9799985000000002
.measure dc ig_nom find par('-i(VIN)-iload') at=1.9799985000000002
.measure dc vout_lo find v(out) at=1.7
.measure dc vout_hi find v(out) at=1.98
