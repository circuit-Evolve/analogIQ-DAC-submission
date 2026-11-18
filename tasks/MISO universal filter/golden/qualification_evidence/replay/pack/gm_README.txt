Gm-C PVT evaluator

Entry point: gm_c_corners.Task(profile='search_full').
seed_design() returns the exact previous saved best parameters (evaluation 8435), not the paper seed.
cfg contains the original 31 variable bounds, original six metric bands/expressions, and all 45 actual conditions.
evaluate(design, out, keep_raw=False, timeout=180) returns the requested corner list, execution_ok, and simulator_invocations.

Grid: NN/SS/SF/FS/FF x 0.9/1.0/1.1 V x -40/27/85 C.
Every candidate uses every corner. VREF and input common mode track VDD/2.
vt_bias_V is an optimization variable, but its candidate value remains fixed across all 45 corners.
No per-corner tuning, geometry changes, or capacitor changes occur within a candidate evaluation.

Original metric definitions remain unchanged:
- OTA gain at 1 Hz, two-sided band 35.1..42.9 dB.
- First falling OTA unity crossing, 9..11 GHz.
- Differential open-loop phase-margin proxy at that crossing, 71.1..86.9 degrees.
- OTA common-mode gain at 1 Hz, -26.4..-21.6 dB.
- Full filter first falling -3 dB crossing relative to 1 Hz/DC, 13.5..16.5 MHz.
- Full filter input-referred noise at assumed 1 MHz, 76.5..93.5 nV/sqrt(Hz).

The complete reconstructed four-OTA filter is simulated. The topology uses inferred side-input summing resistors and is not an exact paper reproduction. Phase margin remains the original proxy, not a verified author loop-break measurement. Peaking, repeated -3 dB crossings, and full filter shape are diagnostics only: no additional optimization target is added. The nominal seed exhibits a low-frequency shelf followed by a high-frequency resonance; a passing first-crossing scalar is not evidence of the paper's clean low-pass response.

Concurrency is limited to two Spectre processes within one evaluator; corners run sequentially. Missing/invalid scalars or failed simulations produce execution_ok=false; no missing scalar is converted to a pass value. All corners still run.
Search raw data is removed after each corner's extraction. Candidate and per-corner JSON, decks, logs, statuses, and full filter response CSV remain. Final keep_raw=True retains raw data; files over 100 kB are gzip-compressed after SHA256 roundtrip verification. raw_retention.json records original hashes and paths.

gm_base_task.py is a private copy of the original nominal extractor using the private base directory. Its obsolete np.trapz calls are replaced with np.trapezoid. These affect only nonlinear diagnostic helpers; the retained six scalar extractions are unchanged. The original pack is not edited.

Validation: gm_test_corners.py checks interface, exact best seed, invalid sizing rejection, PVT source bindings, and candidate VT propagation. gm_preflight.py evaluates all 270 seed scalars against the previous corner verification with 1e-8 relative tolerance, then simulates a +10 mV candidate VT perturbation at NN/1 V/27 C. Results live in ../gm_preflight/summary.json.

Infrastructure deadlines: each search evaluation has a monotonic 900-second budget; full verification has 1800 seconds. These limits are not paper acceptance targets. Job timeouts are capped by remaining evaluator time. Once exhausted, subsequent jobs retain input/status evidence with return code 124 and are not launched. All 45 corner rows remain explicit failures or partial results; simulator_invocations counts actual starts. Process termination may use a five-second grace. gm_test_deadline.py exercises remaining-time capping and both expired 45-corner grids using process/clock mocks; no repeat full simulation preflight is required because measurement/netlist code is unchanged.
