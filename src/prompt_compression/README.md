# 🗜️ Prompt Compression — Buying Back Context And Cost

> *Long prompts cost more, run slower, and eventually hit context limits. Compression is the workaround — removing redundancy at the token level while preserving semantic content. LLMLingua showed it can be done at 5-10× compression with minimal quality loss.*

---

## LLMLingua Deep Dive (`llmlingua_deep_dive.py`)

**LLMLingua (Microsoft, 2023)** — token-level prompt compression using a small language model.

**Core idea:**
- Long prompts contain redundant tokens that don't contribute proportionally to output quality.
- Use a small model to score token importance.
- Drop low-importance tokens.
- Feed compressed prompt to the target (large) model.

**Algorithm:**
1. Given a prompt and a **budget** (e.g., "compress to 30% of original tokens").
2. Use a small model (e.g., LLaMA-7B) to compute perplexity contribution of each token.
3. Rank tokens by importance (contribution to conditional perplexity).
4. Drop tokens below the budget cutoff.
5. Result: shorter prompt, similar downstream quality.

**Example (from the paper):**
- Original prompt: 1500 tokens.
- Compressed: 500 tokens (3× compression).
- Downstream task accuracy: 96% of original.

**Two-stage LLMLingua:**
- **Coarse:** drop entire sentences deemed unimportant.
- **Fine:** within remaining sentences, drop low-importance tokens.

**Practical impact:**
- **Cost:** 3-10× reduction in prompt tokens (dominant cost for many workloads).
- **Latency:** proportional reduction in prompt processing time.
- **Context:** frees up context window for more retrieval or longer inputs.

**Trade-offs:**
- **Small quality loss** (typically 2-5% on task metrics).
- **Extra inference step** (the small model doing scoring — but it's small, so cheap).
- **Not always safe** — some prompts (structured instructions, precise formats) shouldn't be compressed.

---

## LongLLMLingua (`longllmlingua.py`)

**LongLLMLingua (Microsoft, 2024)** — compression tuned for long-context RAG.

**Differences from LLMLingua:**

**1. Question-aware compression.**
- LLMLingua treats all context uniformly.
- LongLLMLingua uses the question as a query and compresses more aggressively on chunks less relevant to the question.

**2. Document-level scoring.**
- Assigns importance to entire retrieved documents.
- Aggressively drops or truncates less-relevant docs.

**3. Position-aware.**
- Understands the "lost in the middle" problem (models attend less to middle context).
- Reorders or compresses accordingly.

**Concrete gains:**
- On long-context RAG tasks, LongLLMLingua achieves 4-8× compression with <3% task quality loss.
- Frees ~70% of context on average without quality drop.

**When to use:**
- Long-context RAG systems.
- Applications where retrieval returns many irrelevant chunks.
- Cost-sensitive deployments at scale.

---

## Selective Context (`selective_context.py`)

**Selective Context (Li et al., 2023)** — content-aware compression using self-information.

**Idea:**
- Compute self-information for each token: `-log(P(token | context))`.
- High self-information = surprising/informative token.
- Drop low self-information tokens.

**Algorithm:**
1. Compute per-token self-information across the prompt.
2. Rank tokens by importance.
3. Keep top-K (budget).
4. Feed to model.

**Comparison to LLMLingua:**
- Simpler (no fine-tuned scorer model needed).
- Slightly lower compression ratios at same quality.
- Faster to run.

**Effective compression:** 2-5× with small quality loss.

**Rule of thumb:** if you need compression but don't want extra infrastructure, Selective Context is a solid baseline. If you need maximum compression at scale, LLMLingua or LongLLMLingua.

---

## Prompt Compression Evaluation (`prompt_compression_evaluation.py`)

**"Did quality survive compression?"**

**Metrics:**

**1. Task-specific.**
- Run downstream task on uncompressed vs compressed prompt.
- Compare accuracy, F1, task metric.
- Measures ultimate impact.

**2. Semantic similarity.**
- Embed model outputs from both.
- Cosine similarity should be high (>0.95 typical).

**3. LLM-judge preference.**
- Present pairs of outputs; ask judge to pick which is better.
- Ideal: 50/50 (compression didn't hurt).
- Worrying: judge consistently prefers uncompressed.

**4. Format compliance.**
- Compressed prompts sometimes drop format instructions.
- Test output structure.

**5. Cost/latency measurement.**
- Verify actual savings.
- Include the compression step's cost.

**Testing protocol:**
- Select 100-500 representative production queries.
- Run each through the uncompressed and compressed pipelines.
- Score both outputs on all metrics.
- Statistical test: is the difference significant?

**Rule:** compression is not free. Always measure the trade-off. Deploy through A/B test.

---

## Compression vs Summarization (`compression_vs_summarization.py`)

**Different techniques with different trade-offs.**

**Prompt compression:**
- Token-level dropping.
- Output is fragmented but content-preserving.
- Fast (single small-model pass).
- Model reads the fragmented input and still succeeds.

**Summarization:**
- LLM rewrites content into shorter form.
- Output is fluent and coherent.
- Slower (extra LLM call, potentially large).
- Higher quality result but higher cost.

**When to use which:**

**Prompt compression** for:
- Retrieved passages in RAG (fine to be fragmented).
- Long chat histories.
- Automated pipelines with clear budgets.

**Summarization** for:
- Human-readable intermediate outputs.
- Highly redundant sources where fluent summary aids understanding.
- Cases where compression fragments would confuse the model.

**Hybrid approach:**
- Summarize high-value chunks (customer records, key documents).
- Compress low-value chunks (log excerpts, boilerplate).
- Balances cost and quality.

---

## Compression In Production (`compression_in_production.py`)

**Making it real.**

**Pipeline placement:**
```
User query
    ↓
Retrieve relevant chunks
    ↓
[Optional: compress each chunk with LLMLingua]
    ↓
Assemble compressed context
    ↓
Send to main LLM
    ↓
Return answer to user
```

**When compression pays for itself:**
- Cost of compression (small model inference) < cost saved on main model call.
- LLMLingua uses a 7B model; cost is ~5% of a 70B model call.
- If compressing to 30% of original, savings are ~65% on prompt token cost minus 5% compression cost = ~60% net.

**Cost model example:**
- 10K queries/day, average prompt 5000 tokens.
- Uncompressed cost: $10K/day at $2/1M tokens.
- Compressed to 30% (1500 tokens): $3K/day + ~$500 compression cost = **$3.5K/day**.
- Monthly savings: ~$200K.

**Latency impact:**
- Compression adds ~50-200ms.
- Prompt processing time on the main model is proportional to length; savings can be significant on long prompts.
- Net latency: sometimes faster overall due to shorter main-model processing.

**Deployment considerations:**
- **Cache compressed prompts** for repeated queries.
- **A/B test** vs uncompressed baseline.
- **Monitor quality drift** — compression may hurt on certain query types.
- **Fall back** to uncompressed for high-stakes queries (paid tier, sensitive content).

**When not to compress:**
- Legal / medical / other high-stakes content where subtle wording matters.
- Very short prompts (compression overhead > savings).
- Prompts with structured formats (compressor may break format).

**Tooling:**
- **LLMLingua** as a library or API service.
- **LangChain integration** for RAG pipelines.
- **Custom** — most mature teams build their own compressor tuned to their data.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `llmlingua_deep_dive.py` | The paper + code |
| `longllmlingua.py` | Long-context version |
| `selective_context.py` | Content-aware compression |
| `prompt_compression_evaluation.py` | Did quality survive? |
| `compression_vs_summarization.py` | Two techniques compared |
| `compression_in_production.py` | Cost model, deployment |

---

*Previous: [← Structured Decoding](../structured_decoding_deep_dive/README.md) · Next: [Meta Prompting →](../meta_prompting/README.md)*  ·  *Back to [main README](../../README.md)*
