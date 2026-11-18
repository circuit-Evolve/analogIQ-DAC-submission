<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`ccmp_lelo_task_001`):** 19 metric types; **103 unique expanded scalar checks** (91 deterministic + 12 MC statistics). The evaluator has 35 constraint definitions and 145 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->

# lelo_CCMP

Benchmark task `ccmp_lelo_task_001` (proven solvable at the paper targets).

- `paper/`: paper PDF and the dataset's extracted metrics / conditions
- `schematic/`: dataset export `final.scs`, `dut_benchmark.scs` where the benchmark repairs a documented export issue, schematic figures, `topology.yaml` (ports, roles, netlist provenance)
- `testbench/ccmp_lelo_task_001/`: the benchmark sizing pack (problem, Spectre decks at the start design, `evaluate.sh`); `variables.yaml` and `task_profiles/` are the task definition
- `golden_sizing/`: golden design (the paper design (reference_candidate.json); its PMOS tail is exempt from the G8 saturation check by owner decision 2026-11-01): `golden_design.json`, `golden_netlist.scs`, the decks of its verification run and `verification_result.json` (official reference check on the current task: feasible)

Source package: `circuits/29_10_2026/Comparators/CT_open-loop_comparator/lelo_CCMP`. Assembled by the curator on 2026-11-02.
