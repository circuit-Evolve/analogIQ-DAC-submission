* analogiq 0.1.0 testbench - generated, do not edit
* task gbfc21_task_001  topology gbfc21
* recipe amp_fd_noise_v1 v1  condition NN_T27_S1p00 (models NN, 27 C, supply 1.8 V)
* request gbfc21_task_001__plan  candidate 3a14c89e438419ec
* execution profile search_full
* .measure statements (SPICE syntax), included by input.scs. Results: input.measure.
.option measdgt=10
.measure noise n00 find inoise at=10000000.0
.measure noise o00 find onoise at=10000000.0
