# Deduplication Pipeline — MinHash + LSH At Scale

> Multi-stage dedup pipeline: exact (SHA-256), near-duplicate (MinHash + LSH), and semantic (embedding-based). Demonstrates the 4-stage pattern on a mid-scale corpus (~1M docs).

## What This Lab Demonstrates

- Exact dedup via hashing.
- MinHash sketching (K=128 permutations).
- LSH banding for near-dup detection.
- Semantic dedup at high cosine threshold.
- Per-stage attrition metrics.

## Files

- `config.yaml` — configuration parameters
- `run.sh` — launcher script
- `README.md` — this file

## How To Run

```bash
cd discipline_examples/deduplication_pipeline
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

