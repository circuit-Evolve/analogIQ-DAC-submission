<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`rvco_khan2025_task_001`):** 13 metric types; **48 unique expanded scalar checks** (42 deterministic + 6 MC statistics). The evaluator has 46 constraint definitions and 50 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->

# Wideband_Linear_CS-VCO_Charge_Pump_QPAIN2025

Benchmark task `rvco_khan2025_task_001` (proven solvable after curator target scaling, see testbench/task_profiles provenance).

- `paper/`: paper PDF and the dataset's extracted metrics / conditions
- `schematic/`: dataset export `final.scs`, `dut_benchmark.scs` where the benchmark repairs a documented export issue, schematic figures, `topology.yaml` (ports, roles, netlist provenance)
- `testbench/rvco_khan2025_task_001/`: the benchmark sizing pack (problem, Spectre decks at the start design, `evaluate.sh`); `variables.yaml` and `task_profiles/` are the task definition
- `golden_sizing/`: golden design (search design; targets scaled): `golden_design.json`, `golden_netlist.scs`, the decks of its verification run and `verification_result.json` (official reference check on the current task: feasible)

Source package: `circuits/Oscillators/Ring_VCO_PLL/QPAIN2025_wideband_cs_vco`. Assembled by the curator on 2026-11-02.
