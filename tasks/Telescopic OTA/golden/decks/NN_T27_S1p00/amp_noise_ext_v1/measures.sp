* analogiq 0.1.0 testbench - generated, do not edit
* task telescopic01_scl180_task_001  topology telescopic01_scl180
* recipe amp_noise_ext_v1 v1  condition NN_T27_S1p00 (models NN, 27 C, supply 1.8 V)
* request golden_telescopic01_scl180_task_001  candidate 452035997487ea9d
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure noise n00 find inoise at=1000000.0
.measure noise o00 find onoise at=1000000.0
