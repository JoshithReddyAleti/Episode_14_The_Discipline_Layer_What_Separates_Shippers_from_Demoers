# Vector DB Selection — Deep Guide

## The four axes

**Recall requirement** — 0.99+ for correctness-critical, 0.90-0.98 for typical RAG, 0.80+ acceptable for candidate generation with re-ranking.

**Scale** — <10M vectors (anything works), 10-100M (Qdrant/Weaviate/Milvus/Pinecone), 100M-1B (Milvus/Qdrant with sharding, DiskANN), 1B+ (Milvus/Vespa/DiskANN).

**Query pattern** — filter-heavy (Qdrant/Weaviate excel), hybrid keyword+vector (Weaviate/Vespa), pure semantic (any).

**Ops model** — managed (Pinecone, Qdrant Cloud, Weaviate Cloud), self-hosted OSS (Qdrant, Weaviate, Milvus, pgvector), embedded (Chroma, LanceDB).

## Decision tree

```
Already have Postgres?
├─ Yes, small scale → pgvector
└─ No, or larger scale → continue

Data lake pattern? (S3/lake, batch load)
├─ Yes, cost-sensitive → Turbopuffer or LanceDB
└─ No, want live queries → continue

Filter-heavy?
├─ Yes → Qdrant or Weaviate
└─ No → continue

Very large scale (500M+)?
├─ Yes → Milvus, Vespa, or DiskANN
└─ No → Qdrant is the safe default
```

## Cost model summary (100M × 1536-dim)

| Approach | Approx monthly |
|---|---|
| Managed (Pinecone) | $2,000-5,000 |
| Self-hosted HNSW (fp32) | $2,500-3,500 (large instance) |
| Self-hosted HNSW + SQ | $800-1,200 |
| Disk-based (DiskANN, Turbopuffer) | $400-1,000 |
| Managed disk-based | $500-1,500 |

## Migration paths

- **Chroma → Qdrant** when moving from prototype to production.
- **pgvector → Qdrant** when scale outgrows Postgres.
- **Pinecone → self-hosted** when cost matters more than ops burden.
- **Any → Milvus** at billion-scale.

