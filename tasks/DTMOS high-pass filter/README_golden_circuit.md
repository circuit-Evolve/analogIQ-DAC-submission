<!-- target-count-reporting-20261113 -->
**Current target counts — 2026-11-13 (`dtmos_hpf_101126_task_001`):** 4 metric types; **48 unique expanded scalar checks** (48 deterministic + 0 MC statistics). The evaluator has 4 constraint definitions and 48 expanded constraint checks before deduplicating overlapping bounds. Operating-point gates are excluded. These counts do not change the recorded qualification or pass/fail evidence below. [Count definitions and audit](../../../../../docs/benchmark/target_count_reporting_2026-11-13.md).
<!-- /target-count-reporting-20261113 -->


**User-authorized gate waiver — 2026-11-12.** This is a registered parameterized sizing task with the listed validity gates **waived, not passed**. All performance targets and corners remain active. Diagnostic results, original sizing, standard starts, bounds and physical/model limitations are preserved. See `validity_gate_waiver.json` in the circuit package; this does not certify a physically qualified golden.

<!-- sizing-task-repair-20261112 -->
**Sizing-task update — 2026-11-12.** `dtmos_hpf_101126_task_001` now has 44 independent sizing variables, 4 scalar targets, 12 conditions and 24 simulator jobs per design. Optimizer exports use the standard start and omit reference sizes. Papers, target limits and physical reference sizes are preserved. Current package status: `benchmark_ready_unproven`. The retained reference is outside the standard search bounds; it is not an in-bounds solution witness. `benchmark_definition/` records the current task schema. `golden_sizing/` retains curator evidence; historical replay archives are under `testbench/_superseded/`.

[Verification and qualification report](../../../../../docs/benchmark/sizing_task_repair_2026-11-12.md). Older import descriptions below describe historical replay evidence.
<!-- /sizing-task-repair-20261112 -->

# DTMOS high-pass filter — fixed 200 Hz gain qualification

Retained golden sizing imported on 2026-11-10, batch `10_11_26`. Task `dtmos_hpf_101126_task_001` has 12 configured conditions.

`golden_sizing/golden_netlist.scs` and `golden_design.json` preserve the final-sized design. `verification_result.json` records import replay verification. `testbench/` mirrors the standalone task.

The paper is in `paper/`. Schematic status is documented in `schematic/asset_status.json`; historical OA views are not the final sizing.

## Qualification scope

- Fixed replay of latest approved golden checkpoint; no new sizing, optimization bounds, corners, or G8 certification.
- Canonical decks are byte-for-byte copies; all external include directives are PDK models.
- Historic schematic assets are provenance only and have not been updated to final sizing.
- Canonical aggregate worst labels are preserved only in evidence; saved_results uses per-corner scalars and directional summaries use metric-aware bounds.
- 12/12 corners and 48/48 scalar checks use fixed 200 Hz gain -3.5..-2.5 dB. Paper Fig6a measurement frequency is unspecified; alternative passband interpretation fails all 12 gain checks and is diagnostic only.
- Same 17 named MOS and four actual PMOS gate-body ties; native Mpb1/Mpb2 m=242, per-instance W=100 um L=0.18 um. Known native DTMOS body ties are retained as an explicit scalar-qualification exception; no broader body-junction or physical-legality certification.
- Total gate area 9547.358124632283 um2, 9.789686963176017 times prior 11/12 design; this is gate-area proxy, not layout area.
- Ideal C1=70.67315305125076 nF and C2=908.0839105919211 nF; no layout parasitics, mismatch, or Monte Carlo verification.
- M2 at 100 C remains weak inversion, with positive 0.1084067382639857 uA DC current; all agreed scalar tests pass.
- Output current is measured into ideal 0 V clamp; output compliance and complete fractional-order behavior are unverified. Ideal current-source realization overhead is unmodeled.
- M3 logical width is total width with native m=2; size_Mpb* overrides take precedence over grouped logical widths. Physical netlist table is final implemented sizing.
- Cutoff is first rising half-power crossing relative to measured 6.324555 kHz passband, with 2–20 kHz ripple <=1 dB and low-frequency rejection guard; no falling-crossing substitution.
- Historical extraction-source configs under evidence may contain earlier bounds or scopes; bundle.json alone defines the imported final target scope and fixed sizing.
