# HNSW Tuning Workshop — Recall vs QPS Trade-offs

> An end-to-end workshop for tuning HNSW parameters (M, efConstruction, efSearch) on a real vector dataset. Measure recall@10 and QPS at each operating point to find your recall/latency Pareto frontier.

## What This Lab Demonstrates

- Build HNSW indexes at multiple (M, efC) combinations.
- Sweep efSearch and record recall@10 + QPS.
- Plot the operating curves.
- Identify the operating point meeting your SLA.

## Files

- `config.yaml` — configuration parameters
- `run.sh` — launcher script
- `README.md` — this file

## How To Run

```bash
cd discipline_examples/hnsw_tuning_workshop
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

