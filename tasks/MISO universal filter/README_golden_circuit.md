<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`miso_universal_111126_task_001`):** 9 metric types; **45 unique expanded scalar checks** (45 deterministic + 0 MC statistics). The evaluator has 9 constraint definitions and 45 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->


**User-authorized gate waiver — 2026-11-12.** This is a registered parameterized sizing task with the listed validity gates **waived, not passed**. All performance targets and corners remain active. Diagnostic results, original sizing, standard starts, bounds and physical/model limitations are preserved. See `validity_gate_waiver.json` in the circuit package; this does not certify a physically qualified golden.

<!-- sizing-task-repair-20261112 -->
**Sizing-task update — 2026-11-12.** `miso_universal_111126_task_001` now has 58 independent sizing variables, 9 scalar targets, 5 conditions and 35 simulator jobs per design. Optimizer exports use the standard start and omit reference sizes. Papers, target limits and physical reference sizes are preserved. Current package status: `needs_owner_decision`. `benchmark_definition/` records the current task schema. `golden_sizing/` retains curator evidence; historical replay archives are under `testbench/_superseded/`.

[Verification and qualification report](../../../../../docs/benchmark/sizing_task_repair_2026-11-12.md). Older import descriptions below describe historical replay evidence.
<!-- /sizing-task-repair-20261112 -->

# MISO universal filter

Imported 2026-11-11, batch `11_11_26`, task `miso_universal_111126_task_001`. Nine retained metrics, five corners, 45/45 selected checks.

`golden_sizing/golden_netlist.scs` and `golden_design.json` preserve the authoritative selected design. `golden_sizing/qualification_evidence/` preserves the verified source, including raw archives once. `testbench/miso_universal_111126_task_001/` mirrors the runnable task. `golden_sizing/verification_result.json` records import checks.

Final-sized netlists are authoritative. Historical OA is not claimed as final sizing. The source paper is in `paper/`. No shared optimizer registration or G8 physical certification.

- Fixed retained golden sizing: 45 physical parameters, the same design at TT/FF/SS/SF/FS, nine retained targets only.
- Scalar qualification is schematic-level GPDK180 at the specified 27 C and +/-0.9 V conditions; paper MISO power is post-layout.
- VM_BP uses 600 AC points/decade; 1200-point source convergence results are preserved. Cadence deriv/cross and THD expressions and original stimuli are unchanged.
- Core gains use the disclosed 2 kohm X load and clamped current output; paper characterization loads are unspecified.
- Noise is sampled at 3.98 MHz; paper says in-passband without an exact extraction frequency.
- LP THD uses 500 kHz and 200 mVpp; BP THD uses assumed 100 mVpp at 3.98 MHz. Qualification applies to these stimuli only.
- Pack-local fixed scalar replay; no shared optimizer registration or G8 physical certification. Final-sized netlist and exact decks are authoritative; no live OA is required.
- Raw source archives occur only in golden_sizing/qualification_evidence/evidence/<corner>/raw.tar.gz; task evidence omits archive bytes.

Historical paper-sizing OA is preserved under `schematic/historical_paper_sizing/DAC_20261107_MISO/`; `schematic/asset_status.json` records per-file source hashes. It is historical provenance, not the final selected sizing.
