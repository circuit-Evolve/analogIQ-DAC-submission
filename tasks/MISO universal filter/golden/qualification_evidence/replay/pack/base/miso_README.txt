MISO paper-start LEDRO adapter

26 sizing variables;17 retained scored metrics;12 search jobs;20 full_verify jobs.
Original project is read-only. Templates are frozen native_runs decks; hashes in templates/miso/manifest.json. Paper seed decks are byte-identical to these source decks.

Variable / unit / seed / lower / upper / binding
ota_input_w | m | 1.8e-06 | 4.5e-07 | 7.2e-06 | {'cell': 'mdvccta_fig2', 'instances': ['M1', 'M2'], 'parameter': 'w'}
ota_input_l | m | 3.6e-07 | 1.8e-07 | 1.44e-06 | {'cell': 'mdvccta_fig2', 'instances': ['M1', 'M2'], 'parameter': 'l'}
ota_pmirror_w | m | 8e-06 | 2e-06 | 3.2e-05 | {'cell': 'mdvccta_fig2', 'instances': ['M3', 'M4', 'M7', 'M8', 'M9'], 'parameter': 'w'}
ota_pmirror_l | m | 7.2e-07 | 3.6e-07 | 2.88e-06 | {'cell': 'mdvccta_fig2', 'instances': ['M3', 'M4', 'M7', 'M8', 'M9'], 'parameter': 'l'}
ota_pload_w | m | 1.8e-06 | 4.5e-07 | 7.2e-06 | {'cell': 'mdvccta_fig2', 'instances': ['M5', 'M6'], 'parameter': 'w'}
ota_pload_l | m | 3.6e-07 | 1.8e-07 | 1.44e-06 | {'cell': 'mdvccta_fig2', 'instances': ['M5', 'M6'], 'parameter': 'l'}
ota_nmirror_w | m | 3e-06 | 7.5e-07 | 1.2e-05 | {'cell': 'mdvccta_fig2', 'instances': ['M10', 'M11', 'M12', 'M13', 'M14'], 'parameter': 'w'}
ota_nmirror_l | m | 7.2e-07 | 3.6e-07 | 2.88e-06 | {'cell': 'mdvccta_fig2', 'instances': ['M10', 'M11', 'M12', 'M13', 'M14'], 'parameter': 'l'}
frontend_input_w | m | 4.5e-06 | 1.125e-06 | 1.8e-05 | {'cell': 'mdvccta_fig2', 'instances': ['M15', 'M16', 'M17', 'M18'], 'parameter': 'w'}
frontend_input_l | m | 3.6e-07 | 1.8e-07 | 1.44e-06 | {'cell': 'mdvccta_fig2', 'instances': ['M15', 'M16', 'M17', 'M18'], 'parameter': 'l'}
frontend_pmirror_w | m | 2e-05 | 5e-06 | 8e-05 | {'cell': 'mdvccta_fig2', 'instances': ['M19', 'M20'], 'parameter': 'w'}
frontend_pmirror_l | m | 3.6e-07 | 1.8e-07 | 1.44e-06 | {'cell': 'mdvccta_fig2', 'instances': ['M19', 'M20'], 'parameter': 'l'}
frontend_pout_w | m | 8.75e-06 | 2.1875e-06 | 3.5e-05 | {'cell': 'mdvccta_fig2', 'instances': ['M21', 'M22', 'M23', 'M24'], 'parameter': 'w'}
frontend_pout_l | m | 3.6e-07 | 1.8e-07 | 1.44e-06 | {'cell': 'mdvccta_fig2', 'instances': ['M21', 'M22', 'M23', 'M24'], 'parameter': 'l'}
frontend_ntail_w | m | 1.35e-05 | 3.375e-06 | 5.4e-05 | {'cell': 'mdvccta_fig2', 'instances': ['M25', 'M26'], 'parameter': 'w'}
frontend_ntail_l | m | 3.6e-07 | 1.8e-07 | 1.44e-06 | {'cell': 'mdvccta_fig2', 'instances': ['M25', 'M26'], 'parameter': 'l'}
frontend_nout_w | m | 1.875e-05 | 4.6875e-06 | 7.5e-05 | {'cell': 'mdvccta_fig2', 'instances': ['M27', 'M28', 'M29', 'M30'], 'parameter': 'w'}
frontend_nout_l | m | 3.6e-07 | 1.8e-07 | 1.44e-06 | {'cell': 'mdvccta_fig2', 'instances': ['M27', 'M28', 'M29', 'M30'], 'parameter': 'l'}
resistor_w | m | 1.8e-06 | 4.5e-07 | 7.2e-06 | {'cell': 'grounded_resistor_fig8a', 'instances': ['MR1', 'MR2'], 'parameter': 'w'}
resistor_l | m | 3.6e-07 | 1.8e-07 | 1.44e-06 | {'cell': 'grounded_resistor_fig8a', 'instances': ['MR1', 'MR2'], 'parameter': 'l'}
C1 | F | 2e-11 | 5e-12 | 8e-11 | {'cell': 'miso_fig3', 'instances': ['C1'], 'parameter': 'c'}
C2 | F | 2e-11 | 5e-12 | 8e-11 | {'cell': 'miso_fig3', 'instances': ['C2'], 'parameter': 'c'}
R3 | ohm | 2000 | 500 | 8000 | {'cell': 'miso_fig3', 'instances': ['R3'], 'parameter': 'r'}
OTA_IBIAS | A | 4.7e-05 | 1e-05 | 0.00015 | {'cell': 'mdvccta_fig2', 'instances': ['IBIAS'], 'parameter': 'dc'}
VBIAS | V | -0.3 | -0.55 | -0.1 | {'cell': '__top__', 'instances': ['VBIAS_SRC'], 'parameter': 'dc'}
VCTRL | V | 0.776844608205 | 0.5 | 0.9 | {'cell': '__top__', 'instances': ['VCTRL_SRC'], 'parameter': 'dc'}

Metric / target / lower / upper / fresh seed / saved relative difference
Y1_gain | 0.99 | 0.891 | 1.089 | 0.960318 | 0
Y1_bandwidth | 1400000000 | 1260000000 | 1540000000 | 1043511815.27 | 0
Y2_gain | 0.99 | 0.891 | 1.089 | 0.965263 | 0
Y2_bandwidth | 1300000000 | 1170000000 | 1430000000 | 1125609543.88 | 0
IZP_gain | 0.998 | 0.8982 | 1.0978 | 0.994979 | 0
IZP_bandwidth | 1420000000 | 1278000000 | 1562000000 | 1561962368.7 | 0
RX | 86.34 | 77.706 | 94.974 | 74.7193 | 0
RZP | 56890 | 51201 | 62579 | 34514.8931764 | 0
ROP | 85500 | 76950 | 94050 | 225853.953799 | 0
ROM | 85500 | 76950 | 94050 | 225853.953799 | 0
OTA_gm | 0.0005 | 0.00045 | 0.00055 | 0.000499892 | 0
MISO_BP_frequency | 3980000 | 3582000 | 4378000 | 4366010.98193 | -4.13881973078e-09
MISO_quiescent_power | 0.00469 | 0.004221 | 0.005159 | 0.00491135757626 | 0
BP_noise_in | 6.604e-08 | 5.9436e-08 | 7.2644e-08 | 1.93240081963e-07 | 0
BP_noise_out | 5.684e-08 | 5.1156e-08 | 6.2524e-08 | 1.49096464657e-07 | 0
LP_THD | 6 | 0 | 6 exclusive | 2.78557813239 | 4.75263600312e-08
BP_THD | 6 | 0 | 6 exclusive | 3.7675592354 | 6.24798438059e-08

Extraction fidelity:
BP frequency is actual Cadence cross(deriv(mag(VOUT))) first falling zero, not a peak fit. LP/BP THD use actual Cadence builtin8192-point DFT and fixed saved windows, preserving builtin harmonic handling; no Python harmonic2-10 substitution. All three run in one isolated batch with90s timeout and process-group cleanup. Baseline extraction45.63s, total12-job preflight66.15s.
Other scalars reproduce retained comparison. First bandwidth crossing is relative to low-frequency magnitude. Log-frequency interpolation is intentionally retained; saved coarse ADE linear crossing differs20-24ppm. IZP uses existing fine grid only if the first coarse crossing lies in its existing1.5-1.65GHz window; otherwise first coarse crossing remains valid. Never select a later crossing or invent a missing one.

Verification:
preflight/miso/report.json:17/17 fresh scalar matches, max relative error6.25e-8 (saved output rounding); seed9/17 paper targets.
binding_checks.json and structural_checks.json:26 perturbations bind, connectivity fixed, diffusion geometry coherent, stimuli/models/load sweeps fixed, invalid input rejected, missing outputs fail independently.
integration.json:LEDRO prompt construction and shared judge pass; full_verify executes20 existing jobs.

No blockers. Full profile retains20-response diagnostics, fixed existing DC characterization sweeps and unavailable/incomparable metric scope remains excluded. No new corners, new topology, native project edits, best-size seed, or optimizer launch. Assumptions and baseline provenance in miso_provenance.json and templates/miso/.
