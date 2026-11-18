* analogiq 0.1.0 testbench - generated, do not edit
* task ldo24c_conventional_task_001  topology ldo24c_conventional
* recipe ldo_psrr_v1 v2  condition FF_Tm50_S1p00_FFS_Vmin_Tmin (models FF, -50 C, supply 1.7 V)
* request ldo24c_conventional_task_001__plan  candidate 164e80879370aa97
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure ac g00 find vdb(out) at=57100.0
.measure ac g01 find vdb(out) at=571000.0
.measure ac g02 find vdb(out) at=1000000.0
.measure ac g03 find vdb(out) at=5710000.0
