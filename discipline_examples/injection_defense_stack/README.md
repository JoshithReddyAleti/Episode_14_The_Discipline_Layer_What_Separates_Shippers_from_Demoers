# Injection Defense Stack — Dual-LLM Pattern Live

> Reference implementation of the dual-LLM injection defense pattern. P-LLM (privileged) never reads untrusted content directly; Q-LLM (quarantined) produces structured output only.

## What This Lab Demonstrates

- Simulated indirect injection attack corpus.
- Naive baseline (single LLM reads retrieved content).
- Dual-LLM implementation.
- Attack success rate on each.
- Additional layers: spotlighting, output filtering.

## Files

- `config.yaml` — configuration parameters
- `run.sh` — launcher script
- `README.md` — this file

## How To Run

```bash
cd discipline_examples/injection_defense_stack
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

