# Model A/B Testing Platform — Compare 3 Models

> Simultaneous A/B/C test comparing three LLM providers on the same task. Includes dual-serving, statistical rigor, and cost/latency analysis alongside quality.

## What This Lab Demonstrates

- Three-arm design with proper power calc.
- Dual-serving infrastructure.
- Quality + cost + latency measurement.
- Statistically-valid pairwise comparisons.
- Winner selection and rollout plan.

## Files

- `config.yaml` — configuration parameters
- `run.sh` — launcher script
- `README.md` — this file

## How To Run

```bash
cd discipline_examples/model_ab_testing_platform
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

