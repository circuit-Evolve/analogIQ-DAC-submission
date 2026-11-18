<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`cmppl24_task_001`):** 5 metric types; **158 unique expanded scalar checks** (157 deterministic + 1 MC statistics). The evaluator has 106 constraint definitions and 158 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->

<!-- sizing-task-repair-20261112 -->
**Sizing-task update — 2026-11-12.** `cmppl24_task_001` now has 51 independent sizing variables, 106 scalar targets, 5 conditions and 6 simulator jobs per design. Optimizer exports use the standard start and omit reference sizes. Papers, target limits and physical reference sizes are preserved. Current package status: `needs_owner_decision`. `benchmark_definition/` records the current task schema. `golden_sizing/` retains curator evidence; historical replay archives are under `testbench/_superseded/`.

[Verification and qualification report](../../../../../docs/benchmark/sizing_task_repair_2026-11-12.md). Older import descriptions below describe historical replay evidence.
<!-- /sizing-task-repair-20261112 -->

# 14 - Performance-efficient comparator (IEEE UPCON, 2022)

Benchmark task `cmppl24_task_001` (proven solvable after curator target scaling, see testbench/task_profiles provenance).

- `paper/`: paper PDF and the dataset's extracted metrics / conditions
- `schematic/`: dataset export `final.scs`, `dut_benchmark.scs` where the benchmark repairs a documented export issue, schematic figures, `topology.yaml` (ports, roles, netlist provenance)
- `testbench/cmppl24_task_001/`: the benchmark sizing pack (problem, Spectre decks at the start design, `evaluate.sh`); `variables.yaml` and `task_profiles/` are the task definition
- `golden_sizing/`: golden design (search design; targets scaled): `golden_design.json`, `golden_netlist.scs`, the decks of its verification run and `verification_result.json` (official reference check on the current task: feasible)

Source package: `circuits/24_10_2026/Comparators/Preamplifier + regenerative latch comparator/14 - Performance-efficient comparator (IEEE UPCON, 2022)`. Assembled by the curator on 2026-11-02.
