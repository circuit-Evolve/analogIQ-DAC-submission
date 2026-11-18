<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`rvco24_um_task_001`):** 7 metric types; **7 unique expanded scalar checks** (7 deterministic + 0 MC statistics). The evaluator has 8 constraint definitions and 8 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->

# R01_CurrentStarvedRingVCO_Um_TCASII2023_180nm

Benchmark task `rvco24_um_task_001` (proven solvable after curator target scaling, see testbench/task_profiles provenance).

- `paper/`: paper PDF and the dataset's extracted metrics / conditions
- `schematic/`: dataset export `final.scs`, `dut_benchmark.scs` where the benchmark repairs a documented export issue, schematic figures, `topology.yaml` (ports, roles, netlist provenance)
- `testbench/rvco24_um_task_001/`: the benchmark sizing pack (problem, Spectre decks at the start design, `evaluate.sh`); `variables.yaml` and `task_profiles/` are the task definition
- `golden_sizing/`: golden design (search design; targets scaled): `golden_design.json`, `golden_netlist.scs`, the decks of its verification run and `verification_result.json` (official reference check on the current task: feasible)

Source package: `circuits/24_10_2026/PLLs/Ring-VCO PLL (Block)/R01_CurrentStarvedRingVCO_Um_TCASII2023_180nm`. Assembled by the curator on 2026-11-02.
