MISO all-process evaluator for the new eight-hour corner-aware run

Entry point: miso_corners.Task(profile='search_full').
- cfg: original 17 scalar constraints and variable bounds/bindings; initial values are saved best eval 685.
- seed_design()/paper_design(): independent copy of exact current-best parameter dictionary.
- plan_text(): inherited representative DUT and bindings, from best-sized templates.
- evaluate(design, out, keep_raw=False, timeout=180): all five paper processes, returns corners/values/diagnostics/execution_ok and simulator_invocations.

Paper process IDs are TT, FF, SS, SF, FS. TT maps to GPDK NN. SF means NMOS slow / PMOS fast; FS means NMOS fast / PMOS slow. Rails stay +0.9 V and -0.9 V; temperature stays 27 C. See miso_provenance.json for paper evidence and model/source hashes.

Each candidate is applied to the verified best-sized deck templates. All 26 parameters remain tunable within original bounds. Physical topology, test stimuli, scalar expressions, tolerances, sweeps and acceptance definitions remain frozen. There are 12 simulation recipes per corner, 60 invocations per full evaluation. At most two Spectre processes run concurrently; corners run serially. BP frequency and LP/BP THD use actual Cadence deriv/cross/thd expressions, including original 8192-point windows. No proxy is used.

Each corner retains design.json, metrics.json, input decks, Spectre logs/status and standalone read-only Cadence extraction scripts/logs. Failed dependencies force the affected scalar to null; missing/nonfinite extraction is distinct from a measured value. Physical warnings and interpolation warnings are retained. The parent generic judge owns original-constraint checking and worst-corner aggregation.

Each evaluation has a monotonic overall budget: 900 seconds for search, 1800 seconds for full_verify. Spectre timeouts are capped to the remaining budget; Cadence extraction is capped to the smaller of 90 seconds and remaining budget. Expired jobs are recorded with return code124 without launching a process; all five corner entries and all17 nullable metric keys are retained. preflight/miso_deadline_report.json verifies launch suppression at both one-corner and complete-evaluation levels.

For search evaluations, only the new candidate's raw directories are removed after per-corner extraction and saved metrics. With keep_raw=True, raw is losslessly archived to each corner's raw.tar.gz and uncompressed raw is removed. raw_archive.json records contents, byte size, hash and restoration command. Output must remain under this new run root. Nonempty evaluation/corner output directories are rejected to avoid stale reuse.

Preflight: pack/miso_preflight.py runs the exact saved seed across all five processes, compares all 85 scalar values and all classifications against prior verification (relative tolerance 1e-9, absolute 1e-15), then runs TT with OTA_IBIAS increased 1% to verify all 12 candidate decks and measured values respond. It also exercises raw cleanup and compressed retention. Evidence is in preflight/miso_report.json and corresponding preflight directories. No optimization is launched by the preflight.

Run Python with PYTHONDONTWRITEBYTECODE=1 and unset PYTHONHOME/PYTHONPATH, using <ANALOGIQ>/sizing/LEDRO/.venv/bin/python. Shared sources and earlier verification outputs are read-only inputs.
