<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`gbfc21_task_001`):** 9 metric types; **25 unique expanded scalar checks** (25 deterministic + 0 MC statistics). The evaluator has 25 constraint definitions and 25 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->

<!-- sizing-task-repair-20261112 -->
**Sizing-task update — 2026-11-12.** `gbfc21_task_001` now has 84 independent sizing variables, 25 scalar targets, 5 conditions and 12 simulator jobs per design. Optimizer exports use the standard start and omit reference sizes. Papers, target limits and physical reference sizes are preserved. Current package status: `benchmark_ready`. `benchmark_definition/` records the current task schema. `golden_sizing/` retains curator evidence; historical replay archives are under `testbench/_superseded/`.

[Verification and qualification report](../../../../docs/benchmark/sizing_task_repair_2026-11-12.md). Older import descriptions below describe historical replay evidence.
<!-- /sizing-task-repair-20261112 -->

# Design_of_a_2_mW_Power_112_dB_Gain-Boosted_Folded_Cascode_Amplifier_in_0.18m_Process

Benchmark task `gbfc21_task_001` (proven solvable at the paper targets).

- `paper/`: paper PDF and the dataset's extracted metrics / conditions
- `schematic/`: dataset export `final.scs`, `dut_benchmark.scs` where the benchmark repairs a documented export issue, schematic figures, `topology.yaml` (ports, roles, netlist provenance)
- `testbench/gbfc21_task_001/`: the benchmark sizing pack (problem, Spectre decks at the start design, `evaluate.sh`); `variables.yaml` and `task_profiles/` are the task definition
- `golden_sizing/`: golden design (LEDRO design (8 h run, 2026-10-28)): `golden_design.json`, `golden_netlist.scs`, the decks of its verification run and `verification_result.json` (official reference check on the current task: feasible)

Source package: `circuits/21_10_2026/Gain-boosted folded-cascode OTA/Design_of_a_2_mW_Power_112_dB_Gain-Boosted_Folded_Cascode_Amplifier_in_0.18m_Process`. Assembled by the curator on 2026-11-02.
