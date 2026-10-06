# Contamination Detector — Train/Test Overlap Pipeline

> Detects contamination between a training corpus and a test set at three levels: exact match, n-gram overlap (13-grams), and embedding similarity. Produces a contamination report suitable for publication.

## What This Lab Demonstrates

- Exact match via SHA-256.
- N-gram overlap detection.
- Embedding-based semantic overlap.
- Contamination report with impact on eval scores.

## Files

- `config.yaml` — configuration parameters
- `run.sh` — launcher script
- `README.md` — this file

## How To Run

```bash
cd discipline_examples/contamination_detector
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

