# Deduplication Playbook

## The 4-stage pipeline

```
Raw corpus
    ↓
Stage 1: Exact dedup (SHA-256 hashing) — removes 20-40%
    ↓
Stage 2: MinHash/LSH (near-duplicate) — removes another 20-40%
    ↓
Stage 3: Semantic dedup (paraphrase-level) — removes another 5-15%
    ↓
Stage 4: Chunk-level dedup (boilerplate) — removes 10-20% of chunks
    ↓
Deduplicated corpus (30-60% of original)
```

## Cost per 100M docs

- Stage 1: ~$50.
- Stage 2: $200-500.
- Stage 3: $500-5,000 (embedding cost dominant).
- Stage 4: applied at chunk time; marginal.

## LSH parameter tuning

For MinHash+LSH banding with K permutations, b bands of r rows each (K = b × r):

- Detection probability: P(match) = 1 - (1 - s^r)^b, where s = Jaccard similarity.
- r=5, b=20: 50% detection at ~55% Jaccard.
- r=10, b=20: 50% detection at ~72% Jaccard.

Choose r/b for your target similarity threshold.

## Semantic dedup thresholds

- 0.99+ cosine: near-identical (same content, minor diffs).
- 0.95-0.99: paraphrases, translations.
- 0.90-0.95: same topic, different wording.
- <0.90: probably distinct.

## When NOT to dedup

- News articles about the same event from different outlets — each has value.
- Legal docs with mostly-identical structure but distinct details.
- Multiple translations of the same document.

Always sample-review before deploying dedup at scale.

