# DSPy Optimized Pipeline — Compile Beats Manual

> Build a task pipeline in DSPy, compile it via BootstrapFewShotWithRandomSearch or MIPRO, and compare to a hand-crafted baseline prompt on the same eval set.

## What This Lab Demonstrates

- DSPy Signature and Module definition.
- Metric function.
- Compilation with an optimizer.
- Comparison to hand-crafted baseline.
- Ship-worthy compiled artifact.

## Files

- `config.yaml` — configuration parameters
- `run.sh` — launcher script
- `README.md` — this file

## How To Run

```bash
cd discipline_examples/dspy_optimized_pipeline
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

