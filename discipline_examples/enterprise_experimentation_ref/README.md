# Enterprise Experimentation Reference — Full Architecture

> Reference architecture for an org-wide experimentation platform: assignment service, metric store, analysis service, dashboards, governance. Shows what a mature platform looks like.

## What This Lab Demonstrates

- Component diagram of an experimentation platform.
- Sample metric definitions in YAML.
- Governance workflow (review, approval, ship criteria).
- Self-serve UX principles.
- Learnings library patterns.

## Files

- `config.yaml` — configuration parameters
- `run.sh` — launcher script
- `README.md` — this file

## How To Run

```bash
cd discipline_examples/enterprise_experimentation_ref
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

