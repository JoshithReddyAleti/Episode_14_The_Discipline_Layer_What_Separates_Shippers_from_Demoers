# Prompt Compression Guide

## When compression pays for itself

Compression cost < prompt token cost saved.

LLMLingua uses a 7B scorer model. Approximate cost:
- Compression: ~5% of a 70B target model call.
- Savings: 60-90% of prompt tokens.
- Net win: ~55-85% cost reduction on prompt tokens.

**Break-even math:** compression is worth it when compressed_target_cost + compression_cost < original_target_cost, i.e., roughly when your target model is ≥ 10x the cost of the compressor.

## When to use each technique

- **LLMLingua:** general prompts, batch scenarios.
- **LongLLMLingua:** long-context RAG, retrieval returns many chunks.
- **Selective Context:** need simple, minimal-infra option.
- **Summarization (instead):** high-value chunks; need human-readable intermediates.

## Where NOT to compress

- Legal/medical/other high-stakes wording-sensitive content.
- Structured format instructions (compressor may break format).
- Very short prompts (overhead > savings).
- Highly-cached prompts (compression breaks cache alignment).

## Deployment pattern

- Cache compressed prompts for repeated queries.
- A/B vs uncompressed baseline before scaling.
- Fall back to uncompressed for high-stakes queries.
- Monitor per-query-type quality drift.

## Compression ratios in practice

- LLMLingua: 3-10× reduction on generic prompts.
- LongLLMLingua: 4-8× on long-context RAG.
- Selective Context: 2-5×.

Quality loss:
- LLMLingua: 2-5% on task metrics.
- LongLLMLingua: <3% on long-context tasks.
- Selective Context: slightly more.

