<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`ldo24c_conventional_task_001`):** 18 metric types; **32 unique expanded scalar checks** (31 deterministic + 1 MC statistics). The evaluator has 36 constraint definitions and 36 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->

<!-- sizing-task-repair-20261112 -->
**Sizing-task update — 2026-11-12.** `ldo24c_conventional_task_001` now has 31 independent sizing variables, 36 scalar targets, 11 conditions and 19 simulator jobs per design. Optimizer exports use the standard start and omit reference sizes. Papers, target limits and physical reference sizes are preserved. Current package status: `benchmark_ready`. `benchmark_definition/` records the current task schema. `golden_sizing/` retains curator evidence; historical replay archives are under `testbench/_superseded/`.

[Verification and qualification report](../../../../../docs/benchmark/sizing_task_repair_2026-11-12.md). Older import descriptions below describe historical replay evidence.
<!-- /sizing-task-repair-20261112 -->

# 1 - Design of low-dropout voltage regulator

Benchmark task `ldo24c_conventional_task_001` (proven solvable at the paper targets).

- `paper/`: paper PDF and the dataset's extracted metrics / conditions
- `schematic/`: dataset export `final.scs`, `dut_benchmark.scs` where the benchmark repairs a documented export issue, schematic figures, `topology.yaml` (ports, roles, netlist provenance)
- `testbench/ldo24c_conventional_task_001/`: the benchmark sizing pack (problem, Spectre decks at the start design, `evaluate.sh`); `variables.yaml` and `task_profiles/` are the task definition
- `golden_sizing/`: golden design (curator hand-sized design (re-stepped 2026-11-02 after the 10-digit .measure fix)): `golden_design.json`, `golden_netlist.scs`, the decks of its verification run and `verification_result.json` (official reference check on the current task: feasible)

Source package: `circuits/24_10_2026/LDOs/Conventional PMOS-pass LDO with error amplifier and output capacitor/1 - Design of low-dropout voltage regulator`. Assembled by the curator on 2026-11-02.
