# Data Engineering Taxonomy For AI

## The eight dimensions

**1. Storage layer.** Object storage (S3, GCS, ADLS) is the substrate. Table formats (Delta, Iceberg) provide ACID + time travel. Vector stores (Qdrant, Weaviate, Milvus) provide similarity search.

**2. Ingestion mode.** Batch (Airflow/Spark), streaming (Kafka/Flink), CDC (Debezium), or hybrid. Choice driven by freshness SLA.

**3. Processing paradigm.** ETL (transform before load — traditional), ELT (transform in warehouse — modern), or ELE (Extract-Load-Embed — AI-specific).

**4. Chunking strategy.** Fixed-size, semantic (paragraph/section), hierarchical, recursive, late chunking, overlapping.

**5. Quality controls.** Deduplication (exact/near/semantic), contamination detection, validation (Great Expectations, Pydantic), PII scrubbing.

**6. Versioning strategy.** File-level (DVC), data-lake (lakeFS), table-format (Delta/Iceberg), snapshot-based.

**7. Indexing pattern.** Full rebuild (small scale only), incremental append, blue/green, rolling reindex.

**8. Observability layer.** Volume, freshness, quality metrics, lineage tracking.

## The AI-specific extensions to traditional data engineering

- Embedding pipelines (per-chunk vectorization; expensive; version-sensitive).
- Vector DB operations (index build, sharding, quantization).
- Contamination checking (train/test overlap detection).
- Data-model coupling (data changes require model consistency checks).
- Human-in-the-loop labels (annotation flows, LLM-assisted labeling).

## Anti-patterns

- Vector DB as first thing chosen; everything else built around it.
- Chunking strategy chosen once and never revisited.
- No version boundary between "raw" and "curated" datasets.
- Reindexing weekly with no incremental strategy.
- No contamination gate between training and eval data.

