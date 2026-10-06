# Prompt A/B Testing Framework — End-to-End

> Full A/B framework: power calculation, feature-flag routing, metric collection, statistical analysis, decision. Demonstrates the discipline on a prompt-vs-prompt comparison.

## What This Lab Demonstrates

- Power calculation to determine sample size.
- Deterministic user-to-variant assignment.
- Metric collection (primary + secondary + guardrails).
- Analysis with CIs and multiple-testing correction.
- Pre-registered decision criteria.

## Files

- `config.yaml` — configuration parameters
- `run.sh` — launcher script
- `README.md` — this file

## How To Run

```bash
cd discipline_examples/prompt_ab_testing_framework
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

