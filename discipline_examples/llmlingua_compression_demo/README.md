# LLMLingua Compression Demo — Cost Savings Measured

> Compress real-world RAG prompts with LLMLingua/LongLLMLingua, measure token savings and downstream quality impact. Compute break-even for your model tier.

## What This Lab Demonstrates

- Baseline: uncompressed prompts.
- Apply LLMLingua at multiple compression ratios.
- Measure quality (LLM-judge) at each ratio.
- Compute cost savings vs quality loss.
- Identify optimal operating point.

## Files

- `config.yaml` — configuration parameters
- `run.sh` — launcher script
- `README.md` — this file

## How To Run

```bash
cd discipline_examples/llmlingua_compression_demo
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

