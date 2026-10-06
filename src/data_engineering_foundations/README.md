# 🧱 Data Engineering For AI — Foundations

> *Every AI person quotes the "80% of the work is data" line. Very few teams actually treat data engineering as engineering. This section is what changes when you do.*

---

## What Makes AI Data Different (`what_makes_ai_data_different.py`)

Traditional data engineering optimizes for **structured, tabular, queryable** data serving BI dashboards, ML feature stores, and analytics. AI data engineering has different constraints:

**1. Unstructured is the default.** PDFs, HTML, images, audio, video, code, chat transcripts. Extraction is lossy, layout matters, and the "right" chunking depends on the downstream task.

**2. Embeddings, not just rows.** Every document becomes one-to-many vectors. A 10-page PDF might produce 20 chunks × 1536-dim embeddings = 30,720 floats. Storage math changes.

**3. The eval set is a first-class dataset.** Not a slice of train — a curated, versioned, contamination-free artifact that the whole team treats like production code.

**4. Data quality has AI-specific failure modes.** Near-duplicates degrade training. Test contamination invalidates benchmarks. PII in retrieved context causes leaks. Malformed markdown in RAG snippets confuses models.

**5. Reindexing is expensive.** Embedding a corpus of 100M documents costs $5,000-50,000. You can't afford full reindexes weekly. Incremental updates, embedding cache invalidation, and CDC become critical.

**6. Downstream tasks are the metric.** In traditional ETL, "the query returned the expected rows" is success. In AI, "the query returned rows *and the model gave a correct answer using them*" is success. Two more steps that can fail.

**7. Freshness has weird semantics.** Web scrapes at 6am; embeddings at 8am; index update at noon; user query at 3pm. Which "day" of data are they hitting? Cache invalidation is a real problem.

**Rule:** AI data engineering is 30% ETL, 30% embedding/indexing, 20% quality/dedup/contamination, 20% version/lineage. The last two categories are where most teams under-invest.

---

## Data As The Product (`data_as_the_product.py`)

**The mindset shift:** in an AI product, the data pipeline is not scaffolding for the model — it *is* the product.

**Why:**
- Model choice matters less than data quality. Same base model + better data almost always beats better base model + worse data.
- Iteration velocity on data > iteration velocity on model. You can rebuild the index in hours. Fine-tuning takes days-weeks.
- The moat is in the data. Vendor models are commoditizing. Curated, deduplicated, well-structured domain corpora are proprietary.

**Concrete implications:**
- **Data eng team headcount** should be at least equal to ML eng team headcount, often larger.
- **Data quality KPIs** are product KPIs. Dedup rate, format conformance, PII flag rate, freshness — all on the dashboard.
- **Data changes are product changes.** Same review, same rollout gates, same rollback paths.
- **Feedback loops for data.** User signals (thumbs, edits, escalations) flow back to data curation queues.

**Anti-pattern to watch for:** "we'll clean up the data later." Later never comes. Bad data ossifies because pipelines and downstream systems get built around its quirks.

---

## The AI Data Lifecycle (`the_ai_data_lifecycle.py`)

```
Sources (docs, DBs, APIs, web, media)
    ↓
Ingestion (batch, streaming, CDC)
    ↓
Parsing / extraction (per format)
    ↓
Cleaning (dedup, PII scrub, normalize, filter)
    ↓
Structure (chunking, layout preservation, metadata)
    ↓
Enrichment (labels, categories, quality scores)
    ↓
Embedding (per chunk, per modality)
    ↓
Indexing (vector, keyword, hybrid, graph)
    ↓
Serving (retrieval APIs, RAG, evals)
    ↓
Feedback (query logs, user signals, drift metrics)
    ↓ (loop back)
Curation queues, retraining, reindexing
```

Each stage has:
- **Latency SLA** (batch vs streaming).
- **Cost budget** (compute, storage, embedding API).
- **Quality gate** (test before promoting).
- **Observability** (metrics, sampling, drift detection).
- **Version boundary** (immutable outputs).

**The full lifecycle is at least 12-18 months of engineering work to build well.** Teams that try to skip stages ship prototypes that don't survive contact with real usage.

---

## Data Engineering Org Patterns (`data_engineering_org_patterns.py`)

**Three org patterns for AI data teams, in order of maturity:**

### 1. Embedded model (early stage)
- Data engineers embedded in ML/AI teams.
- Shared responsibility for pipelines with ML engineers.
- Fast iteration; poor cross-team leverage.
- Works up to ~5 AI features.

### 2. Platform team (growing)
- Dedicated data platform team owning pipelines, vector DBs, embedding services, and feature stores.
- Product teams consume via APIs.
- Scales to dozens of AI features.
- Requires strong product management on the platform.

### 3. Federated data ownership (mature)
- Domain teams own their data products (invoicing team owns the invoice corpus, support team owns support tickets).
- Platform team owns infrastructure only.
- Data mesh principles applied to AI.
- Scales to hundreds of features across a large org.

**Cross-cutting roles:**
- **Data quality lead** — owns metrics, gates, incident response for data.
- **Vector DB SRE** — owns index health, recall/QPS SLIs, cost.
- **Data lineage lead** — owns catalogs, provenance, compliance queries.

**Anti-patterns:**
- ML team owns data pipelines but not headcount. Result: pipelines rot.
- Data team ships to production without ML/AI review. Result: data changes silently break models.
- No cross-team on-call for data incidents. Result: incidents go unaddressed for days.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `what_makes_ai_data_different.py` | The 7 differences from traditional data eng |
| `data_as_the_product.py` | The mindset shift and its implications |
| `the_ai_data_lifecycle.py` | The 11-stage lifecycle |
| `data_engineering_org_patterns.py` | Embedded, platform, federated |

---

*Next: [Vector DB Internals →](../vector_db_internals/README.md)*  ·  *Back to [main README](../../README.md)*
