<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`ldo_ifx_task_001`):** 14 metric types; **14 unique expanded scalar checks** (14 deterministic + 0 MC statistics). The evaluator has 19 constraint definitions and 19 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->

<!-- sizing-task-repair-20261112 -->
**Sizing-task update — 2026-11-12.** `ldo_ifx_task_001` now has 68 independent sizing variables, 19 scalar targets, 1 conditions and 2 simulator jobs per design. Optimizer exports use the standard start and omit reference sizes. Papers, target limits and physical reference sizes are preserved. Current package status: `benchmark_ready`. `benchmark_definition/` records the current task schema. `golden_sizing/` retains curator evidence; historical replay archives are under `testbench/_superseded/`.

[Verification and qualification report](../../../../../docs/benchmark/sizing_task_repair_2026-11-12.md). Older import descriptions below describe historical replay evidence.
<!-- /sizing-task-repair-20261112 -->

# Infineon_LDO

Benchmark task `ldo_ifx_task_001` (proven solvable after curator target scaling, see testbench/task_profiles provenance).

- `paper/`: paper PDF and the dataset's extracted metrics / conditions
- `schematic/`: dataset export `final.scs`, `dut_benchmark.scs` where the benchmark repairs a documented export issue, schematic figures, `topology.yaml` (ports, roles, netlist provenance)
- `testbench/ldo_ifx_task_001/`: the benchmark sizing pack (problem, Spectre decks at the start design, `evaluate.sh`); `variables.yaml` and `task_profiles/` are the task definition
- `golden_sizing/`: golden design (builder witness design, curator-verified 2026-10-31; supply 3.3 V with the supply-monitor thresholds x1.32 by owner decision 2026-11-01): `golden_design.json`, `golden_netlist.scs`, the decks of its verification run and `verification_result.json` (official reference check on the current task: feasible)

Source package: `circuits/29_10_2026/LDOs/Capless_FVF_LDO/Infineon_LDO`. Assembled by the curator on 2026-11-02.
