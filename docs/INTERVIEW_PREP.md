# Interview Prep — Episode 14 Topics

## Data Engineering For AI

**Q: How would you tune HNSW parameters?**
- Start with M=32, efC=200, efS=100.
- Sweep efSearch, plot recall@k vs QPS — that's your operating curve.
- Increase efS until recall meets SLA at required QPS.
- If plateaus below target: rebuild with higher M or efC.

**Q: How would you choose a vector DB?**
- Existing ecosystem? (Postgres → pgvector first).
- Scale: <10M any, 10-100M Qdrant/Weaviate/Milvus, 100M+ Milvus/DiskANN.
- Filter-heavy? Qdrant/Weaviate.
- Managed vs self-hosted? Cost + ops trade-off.

**Q: How do you handle test set contamination?**
- Three levels: exact match (hash), n-gram overlap (13-gram threshold), embedding similarity (>0.90 cosine).
- Report all three in results.
- Re-eval after removing contaminated examples.
- Publish contaminated IDs for reproducibility.

## Prompt Engineering

**Q: When would you use DSPy over hand-written prompts?**
- Clear metric available.
- Training examples exist.
- Task at scale (compilation amortizes).
- Portability across models needed.

**Q: How do you A/B test a prompt change?**
- Offline eval on golden set first.
- Feature-flag deploy at small allocation.
- Measure primary metric + secondaries + guardrails.
- Rollback fast if regression.

## Security

**Q: How do you defend against indirect prompt injection?**
- Least-privilege tools (blast radius reduction).
- Dual-LLM pattern (quarantined LLM produces structured output).
- Spotlighting (mark untrusted content).
- Output filtering.
- Monitoring.

**Q: How do you red-team an LLM feature?**
- Automated suite (Garak, PyRIT) baseline.
- Manual creative sessions weekly.
- Attack success rate (ASR) tracked over time.
- Findings feed into training data + guardrails.

## A/B Testing

**Q: How do you compute sample size for an LLM A/B test?**
- n = 2 × (z_{α/2} + z_β)² × p̄(1-p̄) / δ².
- For proportions with p̄=0.73, δ=0.02, α=0.05, power=0.80: ~7,700 per arm.
- Adjust for variance (LLM outputs have higher variance than typical web A/B).

**Q: How do you handle novelty effects?**
- Run experiments 2-4 weeks (longer than novelty half-life).
- Segment new vs existing users.
- Holdout groups for long-term measurement.

**Q: Bayesian vs frequentist?**
- Both work. Consistency matters more.
- Bayesian better for sequential testing, easier to communicate.
- Frequentist standard, familiar, regulatory-friendly.

