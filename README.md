# analogIQ: benchmark results artifact

Results of four sizing methods (TuRBO-1, LASO-BOSS, LEDRO, Agentic Sizing) on the 30 analogIQ tasks, with each
task's source, reference design and task definition.

## Files

| File | Content |
|---|---|
| `results.csv` | one row per task and method (30 × 4): the Table 3 cell, final score, feasible, gate valid, targets met, designs evaluated, simulator runs, wall-clock hours, stop reason, and the file holding the design |
| `table4_equal_budget.csv` | Table 4 per task: $N$ (designs evaluated by Agentic Sizing), each optimizer's best search score and feasibility within its first $N$ designs, and Agentic Sizing's score |
| `table4_summary.json` | the Table 4 rows computed from `table4_equal_budget.csv` |
| `INDEX.tsv` | per task: task id, source circuit, number of paper files and golden files, and the run each best design comes from |
| `tasks/<name>/` | one folder per task, named as in Table 3 (`/` replaced by `-`, trailing `.` dropped) |

Each `tasks/<name>/` folder:

| Folder / file | Content |
|---|---|
| `TASK_ID.txt` | the analogIQ task id |
| `paper/` | the source paper (PDF) and the extracted metrics and conditions |
| `golden/` | the reference design, which meets all targets, and its verification |
| `testbench/` | the task definition: `problem.json` / `problem.yaml` (variables, bounds, targets, conditions), `designs/start.json` (the standard start), testbenches per condition |
| `schematic/` | schematic netlist and pictures |
| `best_designs/<method>/` | `verify.json`: the best design (`params`) and its final evaluation with 100 Monte Carlo samples, which is the reported result (score, targets met, gate, value and margin of every target); `best.json`: the same design as evaluated during the search; `summary.json`: designs, simulator runs, wall clock, LLM calls and cost, stop reason; `meta.json`: run settings |

## Runs

All runs: at most 2000 designs, 12 h wall clock or $100 of LLM calls; seed 1299; best design re-evaluated with 100
Monte Carlo samples (10 during the search for the latch comparator and the I/Q modulator).

## Notes

- Paths are anonymized: `<ANALOGIQ>`, `<RUNS>`, `<WORK>`, `<HOME>`, `<SCRATCH>` stand for the benchmark's own
  directories, `<PDK_ROOT>` and `<CADENCE_SHARED>` for the process design kits. The testbench files are therefore a
  record of each task, not a ready-to-run setup.
- The process design kits (Cadence GPDK045/090/180, SkyWater SKY130 and the BJT models) are not included.
- LLM cost (`llm_cost_usd` in `summary.json` and `meta.json` of LEDRO and LASO-BOSS) is given at the paper's price
  basis, 2 x the cost the runs recorded at claude-sonnet-5-5 API prices; the recorded value is kept as
  `llm_cost_usd_recorded`, and `llm_cost_basis` states the basis. The two standard-start LASO-BOSS runs (CT comparator,
  NVM charge pump) reused an earlier run's strategy without an LLM call; their `llm_cost_usd` counts that strategy's
  cost. `llm_budget_usd` is the $100 limit and is not scaled.
