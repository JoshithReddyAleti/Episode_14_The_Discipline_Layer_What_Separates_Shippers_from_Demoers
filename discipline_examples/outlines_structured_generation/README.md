# Outlines Structured Generation — 100% Valid JSON

> Constrained decoding demo showing 100% schema-conformant JSON generation with Outlines. Compare unconstrained vs constrained on the same task.

## What This Lab Demonstrates

- JSON schema definition (via Pydantic).
- Outlines FSA-based constrained decoding.
- Unconstrained baseline for comparison.
- Format compliance rate: 100% vs baseline.
- Quality comparison.

## Files

- `config.yaml` — configuration parameters
- `run.sh` — launcher script
- `README.md` — this file

## How To Run

```bash
cd discipline_examples/outlines_structured_generation
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

