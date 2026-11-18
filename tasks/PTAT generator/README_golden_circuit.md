<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`ptat_lelo_task_001`):** 56 metric types; **320 unique expanded scalar checks** (283 deterministic + 37 MC statistics). The evaluator has 107 constraint definitions and 493 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->

# lelo_PTAT_bias

Benchmark task `ptat_lelo_task_001` (proven solvable at the paper targets).

- `paper/`: paper PDF and the dataset's extracted metrics / conditions
- `schematic/`: dataset export `final.scs`, `dut_benchmark.scs` where the benchmark repairs a documented export issue, schematic figures, `topology.yaml` (ports, roles, netlist provenance)
- `testbench/ptat_lelo_task_001/`: the benchmark sizing pack (problem, Spectre decks at the start design, `evaluate.sh`); `variables.yaml` and `task_profiles/` are the task definition
- `golden_sizing/`: golden design (search design (8 h TuRBO solvability search seeded with the repository sizes, found at design 155, 2026-11-01; re-verified with 100 Monte Carlo samples)): `golden_design.json`, `golden_netlist.scs`, the decks of its verification run and `verification_result.json` (official reference check on the current task: feasible)

Source package: `circuits/29_10_2026/Blocks/Bias_generator/lelo_PTAT_bias`. Assembled by the curator on 2026-11-02.
