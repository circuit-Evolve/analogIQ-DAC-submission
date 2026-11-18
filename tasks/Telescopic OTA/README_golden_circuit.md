<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`telescopic01_scl180_task_001`):** 8 metric types; **20 unique expanded scalar checks** (20 deterministic + 0 MC statistics). The evaluator has 20 constraint definitions and 20 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->

<!-- sizing-task-repair-20261112 -->
**Sizing-task update — 2026-11-12.** `telescopic01_scl180_task_001` now has 29 independent sizing variables, 20 scalar targets, 5 conditions and 8 simulator jobs per design. Optimizer exports use the standard start and omit reference sizes. Papers, target limits and physical reference sizes are preserved. Current package status: `benchmark_ready`. `benchmark_definition/` records the current task schema. `golden_sizing/` retains curator evidence; historical replay archives are under `testbench/_superseded/`.

[Verification and qualification report](../../../../docs/benchmark/sizing_task_repair_2026-11-12.md). Older import descriptions below describe historical replay evidence.
<!-- /sizing-task-repair-20261112 -->

# Analysis_and_Design_of_a_Two_stage_Telescopic_OTA_using_SCL_180nm_CMOS_Technology

Benchmark task `telescopic01_scl180_task_001` (proven solvable at the paper targets).

- `paper/`: paper PDF and the dataset's extracted metrics / conditions
- `schematic/`: dataset export `final.scs`, `dut_benchmark.scs` where the benchmark repairs a documented export issue, schematic figures, `topology.yaml` (ports, roles, netlist provenance)
- `testbench/telescopic01_scl180_task_001/`: the benchmark sizing pack (problem, Spectre decks at the start design, `evaluate.sh`); `variables.yaml` and `task_profiles/` are the task definition
- `golden_sizing/`: golden design (search design): `golden_design.json`, `golden_netlist.scs`, the decks of its verification run and `verification_result.json` (official reference check on the current task: feasible)

Source package: `circuits/21_10_2026/Telescopic cascode OTA/Analysis_and_Design_of_a_Two_stage_Telescopic_OTA_using_SCL_180nm_CMOS_Technology`. Assembled by the curator on 2026-11-02.
