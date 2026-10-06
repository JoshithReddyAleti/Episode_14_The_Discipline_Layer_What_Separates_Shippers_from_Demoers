# Red Team Lab — Garak + PyRIT + Promptfoo

> End-to-end red team pipeline combining Garak (broad scanner), PyRIT (custom orchestration), and Promptfoo (test-driven). Produces a red team report on a target model.

## What This Lab Demonstrates

- Garak scan across probes.
- PyRIT custom attack scenarios.
- Promptfoo test suite.
- Aggregate ASR by category.
- Severity-classified findings report.

## Files

- `config.yaml` — configuration parameters
- `run.sh` — launcher script
- `README.md` — this file

## How To Run

```bash
cd discipline_examples/red_team_lab
./run.sh
```

## Expected Outputs

- Console logs showing the pipeline stages.
- Metrics summary at the end.
- (Where applicable) an output artifact directory.

## Cost / Latency Estimates

Approximate for a small run (default config):
- Compute: minutes on a single machine.
- API cost: $0.10–5 depending on model choice.
- Storage: negligible.

Scale up parameters in `config.yaml` for realistic tests.

## References

See the corresponding section README in `src/` for the deep technical background.

