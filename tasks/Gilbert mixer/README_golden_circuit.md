<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`gmix04_task_001`):** 4 metric types; **4 unique expanded scalar checks** (4 deterministic + 0 MC statistics). The evaluator has 4 constraint definitions and 4 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->

# patulea_carleton_2015

Benchmark task `gmix04_task_001` (proven solvable at the paper targets).

- `paper/`: paper PDF and the dataset's extracted metrics / conditions
- `schematic/`: dataset export `final.scs`, `dut_benchmark.scs` where the benchmark repairs a documented export issue, schematic figures, `topology.yaml` (ports, roles, netlist provenance)
- `testbench/gmix04_task_001/`: the benchmark sizing pack (problem, Spectre decks at the start design, `evaluate.sh`); `variables.yaml` and `task_profiles/` are the task definition
- `golden_sizing/`: golden design (search design): `golden_design.json`, `golden_netlist.scs`, the decks of its verification run and `verification_result.json` (official reference check on the current task: feasible)

Source package: `circuits/RF FRONT END/Double_balanced_Gilbert_cell_active_mixer/patulea_carleton_2015`. Assembled by the curator on 2026-11-02.
