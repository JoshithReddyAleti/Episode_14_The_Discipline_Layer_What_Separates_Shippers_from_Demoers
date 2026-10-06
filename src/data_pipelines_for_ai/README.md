# 🚰 Data Pipelines For AI — The Plumbing

> *Every AI feature has a data pipeline. Most AI features fail at the pipeline layer before they fail at the model layer. This is the boring, essential engineering.*

---

## Batch vs Streaming Ingestion (`batch_vs_streaming_ingestion.py`)

**Batch ingestion:**
- Scheduled runs (daily, hourly).
- High throughput, high latency (hours to days from source to index).
- Simpler operationally.
- Best for slow-changing corpora (policies, product catalogs, knowledge bases).

**Streaming ingestion:**
- Real-time or near-real-time (seconds to minutes).
- Lower throughput per node, higher operational complexity.
- Best for fast-changing data (news, support tickets, social feeds).

**Hybrid (most common):**
- Batch for backfill and periodic refresh.
- Streaming for incremental updates.
- Batch + CDC (change data capture) combined.

**Decision framework:**
- Freshness SLA >1 hour: batch is fine.
- Freshness SLA <1 hour: streaming or CDC.
- Freshness SLA <1 minute: real-time streaming with dedicated infrastructure.
- Freshness SLA <1 second: very rare in AI use cases; usually you're overthinking freshness.

**Infrastructure:**
- **Batch:** Airflow, Prefect, Dagster orchestrating Spark/Ray jobs.
- **Streaming:** Kafka, Kinesis, Pub/Sub feeding Flink, Spark Streaming, or Beam.
- **CDC:** Debezium capturing DB changes → stream processing.

---

## Document Processing Pipelines (`document_processing_pipelines.py`)

**The classic RAG ingestion pipeline:**

```
Source (S3 bucket, SharePoint, CMS, drive)
    ↓
Format detection (PDF, DOCX, HTML, TXT, image, video)
    ↓
Extraction (per-format extractors)
    ↓
Content cleaning (dedup, PII scrub, normalize)
    ↓
Chunking (semantic, fixed, hierarchical, agentic)
    ↓
Metadata enrichment (source, timestamp, tags, ACL)
    ↓
Embedding (batch, per-chunk)
    ↓
Vector DB upsert
    ↓
Index optimization (compaction, sharding)
    ↓
Cache warming / smoke test
```

**Chunking strategies:**

**Fixed-size:**
- Every 512 or 1024 tokens.
- Simple, predictable.
- Breaks semantic units.

**Semantic:**
- Chunks at paragraph or section boundaries.
- Preserves context better.
- Variable size — some chunks tiny, some huge.

**Hierarchical:**
- Multiple levels: doc → section → paragraph → sentence.
- Retrieve at multiple granularities.
- More expensive index, richer retrieval.

**Recursive (LangChain-style):**
- Split by paragraph; if too big, split by sentence; if too big, split by fixed size.
- Reasonable default.

**Late chunking (2024+):**
- Embed the whole document first.
- Chunk after embedding, preserving global context.
- Better for long-range dependencies.

**Overlapping chunks:**
- 10-20% overlap between adjacent chunks.
- Prevents boundary information loss.
- Increases storage cost.

---

## Incremental Indexing (`incremental_indexing.py`)

**Not rebuilding from scratch.**

**The problem:** full reindex of 100M docs = hours to days. Doing it daily is expensive and disruptive.

**Approaches:**

**1. Insert-only (append).**
- New docs added to existing index.
- Simplest; index grows over time.
- Fine until deletes/updates matter.

**2. Insert + tombstone.**
- Deleted docs marked but not physically removed.
- Reads skip tombstones.
- Periodic compaction removes tombstoned data.

**3. Rolling reindex.**
- Segment the corpus (by date, by source, by shard).
- Rebuild one segment at a time.
- Never rebuild the whole thing.

**4. Blue/green indexes.**
- Two indexes: active (serving) and shadow (being updated).
- On refresh, swap.
- Requires 2× storage; provides zero-downtime updates.

**Update patterns for vector indexes:**
- HNSW: insert-only is efficient; deletes are slow (require compaction).
- IVF: incremental adds require re-clustering periodically.
- Disk-ANN: rebuild segments; append new.

**Practical rule:** design for incremental updates from day one. Retrofitting is very painful.

---

## Change Data Capture (`change_data_capture.py`)

**CDC for RAG — keeping indexes fresh from operational data.**

**Sources:**
- Application DBs (Postgres, MySQL, SQL Server).
- Document stores (MongoDB, DynamoDB).
- SaaS APIs (Salesforce, Zendesk, GitHub).

**Approach:**
1. Capture change events from source (Debezium for DBs; polling or webhooks for APIs).
2. Publish to message queue (Kafka topic per source table).
3. Stream processor consumes changes, updates:
   - Content extraction (if document changed).
   - Re-embed if content changed.
   - Metadata updates (cheap).
   - Deletes on record removal.
4. Vector DB upsert.

**Challenges:**
- **Ordering:** must apply changes in order for the same record.
- **Idempotency:** same event may be delivered multiple times; upsert semantics needed.
- **Backfill:** initial load of the whole DB before starting CDC.
- **Schema evolution:** source schema changes; downstream must adapt.

**Freshness math:**
- Source DB update → CDC event: milliseconds.
- CDC event → queue: milliseconds.
- Queue → processor: seconds.
- Processor → embedding → index: seconds to minutes.
- **Total: 10 seconds to a few minutes** typical.

**Tools:**
- **Debezium** — the standard CDC engine.
- **Airbyte** — ELT with CDC support.
- **Estuary Flow** — streaming ELT.
- **StreamNative** — Pulsar-based.

---

## Data Validation at Ingest (`data_validation_at_ingest.py`)

**Catch bad data before it hits the index.**

**What to validate:**

**Schema:**
- Required fields present.
- Field types correct.
- Ranges reasonable.
- Enum values in valid set.

**Content:**
- Non-empty.
- Length within bounds.
- Encoding valid (UTF-8).
- Not garbage (perplexity check, coherence).

**Metadata:**
- Timestamps parseable, within reasonable range.
- Source ID valid.
- ACL/tenant present.

**Cross-record:**
- No duplicate IDs.
- Consistent schemas across a batch.
- Referential integrity.

**Tools:**
- **Great Expectations** — declarative data quality; widely used.
- **Pydantic** — Python-native schema validation.
- **Pandera** — schema for DataFrames.
- **Deequ** (Amazon) — Spark-native.
- **dbt tests** — for warehouse pipelines.

**Practical setup:**
```python
from pydantic import BaseModel, Field, validator

class DocumentIngest(BaseModel):
    doc_id: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=10, max_length=1_000_000)
    source: str
    ingested_at: datetime
    
    @validator('content')
    def content_not_boilerplate(cls, v):
        if v.strip().startswith('Access denied'):
            raise ValueError('Access denied content')
        return v
```

**Deployment:**
- Validation runs at ingest.
- Failures logged and monitored.
- Failure rate is a SLI (should be <1% typically).
- Batch-level rejection if failure rate spikes.

---

## Data Pipeline Orchestration (`data_pipeline_orchestration.py`)

**The 2026 landscape:**

**Airflow (Airbnb origin, Apache):**
- Most widely deployed.
- DAG-based, Python-native.
- Rich ecosystem of operators.
- Weaknesses: cluster complexity, slow scheduling.

**Prefect:**
- Modern rewrite of Airflow ideas.
- Better developer ergonomics.
- Prefect 2.0/3.0 focused on ease of use.

**Dagster:**
- Software-defined assets (data as first-class objects).
- Strong type system.
- Excellent for data-lineage-heavy pipelines.

**Argo Workflows:**
- Kubernetes-native.
- Container-per-step.
- For infrastructure-heavy teams.

**Temporal:**
- Not a data-first tool but excellent for durable orchestration.
- Good for long-running, retry-heavy pipelines.

**Choosing:**
- **Airflow:** legacy shops, large teams.
- **Prefect:** modern Python teams, developer velocity.
- **Dagster:** data-lineage-first teams, complex asset graphs.
- **Argo:** Kubernetes-native shops.
- **Temporal:** high-reliability requirements, complex workflows.

**Pipeline patterns:**
- **Extract → Transform → Load** (ETL classic).
- **Extract → Load → Transform** (ELT — modern, transforms in warehouse).
- **Extract → Load → Embed → Index** (AI-specific).

**Every pipeline should have:**
- Retries with exponential backoff.
- Timeouts.
- Notifications on failure.
- Metrics (duration, throughput, error rate).
- Lineage tracking.

---

## Pipeline Observability (`pipeline_observability.py`)

**Extending Episode 11's observability to data pipelines.**

**Metrics:**
- Task duration (P50/P95/P99).
- Throughput (records/sec, MB/sec).
- Success/failure rate.
- Data volume in/out.
- Error breakdown by type.
- SLA adherence (did we finish in time?).

**Logs:**
- Structured (JSON) per pipeline run.
- Request IDs threaded through steps.
- Sampling for high-volume steps.

**Traces:**
- Distributed tracing across pipeline stages.
- Especially useful for streaming pipelines.

**Data quality metrics:**
- Row count in / row count out (attrition rate).
- Null rate per column.
- Schema conformance rate.
- Duplicate rate.
- PII flag rate.
- Freshness (max lag from source event to indexed).

**Data-specific alerts:**
- **Attrition spike:** filter dropping more data than usual.
- **Freshness lag:** index falling behind source.
- **Quality drop:** conformance rate below threshold.
- **Volume anomaly:** unexpectedly high or low ingestion volume.
- **Schema drift:** new field appearing in source.

**Tools:**
- **Monte Carlo, Datafold, Metaplane** — data observability platforms.
- **Great Expectations checkpoints** — integrated into pipelines.
- **Custom Prometheus + Grafana** — DIY approach.
- **OpenLineage** — for lineage-aware monitoring.

**Rule:** pipeline observability catches issues that make it to production before users report them. Skimping here means users find your data problems for you.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `batch_vs_streaming_ingestion.py` | Batch, streaming, hybrid |
| `document_processing_pipelines.py` | Chunking, embedding, indexing |
| `incremental_indexing.py` | Not rebuilding from scratch |
| `change_data_capture.py` | CDC for RAG |
| `data_validation_at_ingest.py` | Great Expectations, Pydantic |
| `data_pipeline_orchestration.py` | Airflow, Prefect, Dagster |
| `pipeline_observability.py` | Extends Episode 11 |

---

*Previous: [← Synthetic Data Engineering](../synthetic_data_engineering/README.md) · Next: [Prompt Engineering Foundations →](../prompt_engineering_foundations/README.md)*  ·  *Back to [main README](../../README.md)*
