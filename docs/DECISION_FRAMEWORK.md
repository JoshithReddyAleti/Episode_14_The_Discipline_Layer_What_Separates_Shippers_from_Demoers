# Decision Framework — Episode 14

## Data Engineering Decisions

**Which vector DB?**
- Existing Postgres shop → pgvector first.
- Prototype → Chroma.
- Production small-medium → Qdrant.
- Filter-heavy → Qdrant or Weaviate.
- Very large scale → Milvus or DiskANN-based.
- Cost-sensitive at scale → Turbopuffer.

**Which chunking strategy?**
- Simple text → fixed-size with overlap.
- Structured docs → semantic (sections).
- Long documents → hierarchical.
- Latest research → late chunking.

**Which dedup depth?**
- Web scrape → all 4 stages.
- Curated corpus → exact + semantic sufficient.
- Structured records → exact only.

## Prompt Engineering Decisions

**Prompt or DSPy?**
- Metric + examples → DSPy.
- Subjective/creative → hand-crafted.

**Structured decoding?**
- Format matters + provider supports → yes.
- Cost/latency-sensitive → use fast library (XGrammar, LLGuidance).
- Very complex schema → validate constrains still allow good outputs.

**Compression?**
- Long prompts + high volume → LLMLingua/LongLLMLingua.
- Short prompts → skip.
- High-stakes wording → skip.

## Security Decisions

**Defense-in-depth stack?**
- Every surface: minimum input filtering + output filtering + monitoring.
- With tools: add least-privilege + dual-LLM.
- Autonomous: add human-in-loop.

**Red team investment level?**
- Prototype: manual reviews.
- Production: continuous automated + weekly manual.
- Enterprise/regulated: full program + bug bounty + external.

## A/B Testing Decisions

**A/B or offline eval?**
- Offline first (filter).
- A/B for real user impact.
- Both when both signals matter.

**Bayesian or frequentist?**
- Standardize on one.
- Bayesian if sequential testing needed.
- Frequentist if regulatory pressure.

**How gradual?**
- Prompt change: 3-7 day rollout.
- Model change: 2-4 week rollout with dual-serving.
- New feature: ring deployment.
- Cost-sensitive: measure per-stage.

