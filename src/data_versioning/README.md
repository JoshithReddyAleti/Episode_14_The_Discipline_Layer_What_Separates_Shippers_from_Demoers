# 🔄 Data Versioning — Reproducibility As A First-Class Concern

> *If you can't answer "what data was used to produce this model" with a SHA, you're not doing production ML.*

---

## Why Version Data (`why_version_data.py`)

**Every serious production AI incident traces back to one of:**
1. Model change (traceable via model registry).
2. Prompt change (traceable via prompt versioning).
3. **Data change (usually not traceable).**

The third is the one that eats months of debugging time.

**Concrete scenarios that require data versioning:**
- **Regression debugging:** "Quality dropped 15% last Tuesday. What changed?" Without versioned data, you check code, prompts, model — never find it. It was a scrape that pulled 2M new low-quality docs.
- **Compliance audit:** "Prove this model was trained without European citizen data as of the GDPR effective date." Requires point-in-time snapshots.
- **Reproducibility:** "Reproduce the training run from 6 months ago." Impossible without dataset SHA.
- **Failure analysis:** "The model started refusing benign queries after retraining." Diff current training data vs previous, find the poisoned batch.
- **A/B fairness:** "Rerun the same query on the same data to isolate model change." Requires immutable data at experiment start.

**Rule:** every artifact that trains, evaluates, or feeds a model must be identified by a **content hash** (SHA-256 of manifest). Every downstream artifact records the input hash.

---

## DVC Deep Dive (`dvc_deep_dive.py`)

**DVC (Data Version Control)** — "Git for data." Widely adopted in AI teams.

**Model:**
- Data files not stored in Git; **manifest files (.dvc)** stored in Git.
- Actual data on remote storage (S3, GCS, Azure Blob, SSH).
- Manifest contains SHA-256 hash of each file + remote location.

**Basic workflow:**

```bash
# Track a dataset
dvc add data/raw_corpus.jsonl
# → creates data/raw_corpus.jsonl.dvc (manifest)
# → moves file to cache, replaces with symlink
git add data/raw_corpus.jsonl.dvc .gitignore
git commit -m "Add v1 raw corpus"

# Push data to remote
dvc push

# On another machine
git clone repo && dvc pull
# → fetches the exact same data
```

**Pipeline versioning:**

```yaml
# dvc.yaml
stages:
  preprocess:
    cmd: python preprocess.py --in data/raw_corpus.jsonl --out data/clean.jsonl
    deps:
      - data/raw_corpus.jsonl
      - preprocess.py
    outs:
      - data/clean.jsonl
  
  embed:
    cmd: python embed.py --in data/clean.jsonl --out data/embeddings.parquet
    deps:
      - data/clean.jsonl
      - embed.py
    outs:
      - data/embeddings.parquet
```

DVC tracks which stage inputs changed and re-runs downstream stages automatically.

**Strengths:**
- Git-native workflow — familiar to engineers.
- Works with any cloud storage.
- Pipeline reproducibility.
- Good for medium-scale (up to hundreds of GB).

**Weaknesses:**
- Not great at very large scale (multi-TB datasets).
- No fine-grained diff (dataset is opaque blob).
- Local cache grows large; requires management.

**When to use:** ML/AI teams up to ~50 people. Standard tooling for a lot of ML shops in 2026.

---

## lakeFS Deep Dive (`lakefs_deep_dive.py`)

**lakeFS** — data lake versioning with Git-like semantics.

**Model:**
- Sits between your application and object storage (S3/GCS/Azure).
- Provides **branch/commit/merge** on the entire data lake.
- **Zero-copy branching** — new branch shares storage until modification.
- Objects immutable within a commit; commits are permanent.

**Workflow:**

```bash
# Create a branch for experimentation
lakectl branch create lakefs://my-lake/experiment-v2 --source main

# Work in the branch
aws s3 cp new_data.parquet s3://my-lake/experiment-v2/datasets/

# Commit changes
lakectl commit lakefs://my-lake/experiment-v2 -m "Add v2 corpus"

# Merge back to main after review
lakectl merge lakefs://my-lake/experiment-v2 lakefs://my-lake/main
```

**Why it beats DVC for large-scale data lakes:**
- Handles petabytes without cache duplication.
- Branch-per-experiment enables safe experimentation.
- Zero-copy branching means experiments cost nothing until they diverge.
- Integrated with Spark, Flink, Airflow.

**Weaknesses:**
- Requires operating the lakeFS service.
- Vendor lock-in to the lakeFS abstraction.
- Less approachable for small teams.

**When to use:** enterprise data platforms with petabyte-scale storage, multiple teams sharing data, need for safe experimentation.

---

## Delta Lake and Iceberg (`delta_lake_and_iceberg.py`)

**Delta Lake (Databricks) and Apache Iceberg (Netflix origin, Apache) — table formats with time travel.**

**What they provide:**
- **ACID transactions** on top of object storage (S3, GCS, ADLS).
- **Time travel** — query as-of any commit.
- **Schema evolution** — add/drop/rename columns without full rewrite.
- **Partition evolution** — change partitioning strategy over time.
- **Streaming + batch** unified.

**How they work:**
- Data stored as Parquet files.
- Metadata files (JSON for Delta, Avro for Iceberg) track the "current" version, previous versions, statistics, schema.
- Each write creates a new metadata snapshot; old data files kept for time travel.

**Delta Lake time travel:**
```sql
-- Query current version
SELECT * FROM my_table WHERE date = '2026-07-01';

-- Query as of a specific version
SELECT * FROM my_table VERSION AS OF 42;

-- Query as of a specific timestamp
SELECT * FROM my_table TIMESTAMP AS OF '2026-06-01T00:00:00';
```

**Iceberg equivalent:**
```python
spark.read.option("snapshot-id", "1234567890").format("iceberg").load("catalog.db.table")
```

**Comparison:**
| Aspect | Delta Lake | Iceberg |
|---|---|---|
| Origin | Databricks | Netflix (Apache) |
| Format | Parquet + JSON logs | Parquet + Avro metadata |
| Vendor neutrality | Historically Databricks-favored (now open) | Vendor-neutral |
| Adoption in 2026 | Very high | Growing rapidly, especially in AWS/Snowflake |
| Streaming support | Structured Streaming | Robust |

**For AI workloads:**
- Training datasets: use time-travel to reproduce old runs.
- Feature stores: Iceberg/Delta as the persistent layer.
- Eval datasets: pinned snapshot to prevent drift.

**Trend:** Iceberg gaining share in 2025-2026 as it becomes vendor-neutral standard. Both are strong choices.

---

## Dataset Snapshots (`dataset_snapshots.py`)

**Snapshot** = a named, immutable point-in-time view of a dataset.

**Simplest implementation:**
```
s3://data-lake/datasets/customer-support/
  ├── snapshot-2026-07-01T00:00:00Z/
  ├── snapshot-2026-07-08T00:00:00Z/
  └── snapshot-2026-07-15T00:00:00Z/
```

Each snapshot is an immutable directory. Downstream jobs reference by snapshot ID.

**Snapshot vs. version:**
- Snapshot = point-in-time state, typically periodic (daily, weekly).
- Version = every logical change. Higher granularity but more overhead.

**Snapshot metadata:**
- Snapshot ID (e.g., `snapshot-YYYY-MM-DDTHH:MM:SSZ`).
- SHA-256 of manifest (list of files + their hashes).
- Row count, byte size, schema hash.
- Upstream lineage (which raw data was ingested).
- Downstream references (which models trained on this).
- Retention policy.

**Snapshot cadence:**
- Frequently-changing corpora: daily.
- Reference datasets: weekly or on-change.
- Golden eval sets: rarely changed (versioned, not snapshotted per-change).

**Snapshot pinning:**
- Training run references snapshot ID.
- Evaluation references snapshot ID.
- Serving system references snapshot ID.
- All pins recorded in run metadata → full reproducibility.

**Storage cost:** snapshots share storage via CoW (copy-on-write) semantics. Only the delta between snapshots costs extra.

---

## Data Lineage Tracking (`data_lineage_tracking.py`)

**Lineage** = the graph of "data X derived from data Y via process Z."

**Why:**
- Compliance: "which records contributed to this model?"
- Debugging: "which upstream change broke this downstream table?"
- Impact analysis: "if I change this source, what breaks?"
- Cost attribution: "which downstream consumers should share the cost of this ingestion?"

**Tracking approaches:**

**1. Framework-native**
- Airflow / Prefect / Dagster track task-level lineage automatically.
- Limited to what runs in the framework.

**2. OpenLineage**
- Vendor-neutral lineage standard.
- Integrations with Airflow, Spark, dbt, Great Expectations.
- Emits lineage events → central store (Marquez, DataHub, OpenMetadata).

**3. Column-level lineage**
- Not just "table A → table B" but "column A.x → column B.y via SQL expression."
- SQL parsers (SqlLineage, SQLGlot) extract from queries.
- Critical for regulatory (GDPR right-to-be-forgotten).

**4. AI-specific lineage**
- Track which vectors came from which chunks came from which documents came from which sources.
- Which model version + which dataset version → which output.
- Emerging: MLflow lineage, W&B lineage, Datadog data lineage.

**Storage:**
- **Marquez** (Apache) — OpenLineage reference implementation.
- **DataHub (LinkedIn origin)** — full data catalog with lineage.
- **OpenMetadata** — similar, newer.
- **Amundsen (Lyft origin)** — data discovery + lineage.

**Practical rule:** every AI dataset artifact should record `upstream_dataset_ids: [...]` in metadata. Every model artifact should record `training_dataset_ids: [...]`. Every serving deployment should record `model_ids: [...]`.

---

## Reproducibility Workflow (`reproducibility_workflow.py`)

**The end-to-end reproducible AI workflow:**

```
Source Data (versioned via DVC / lakeFS / Iceberg)
    ↓ [manifest SHA logged]
Extraction / Cleaning (pipeline versioned via DVC / Airflow DAG)
    ↓ [output SHA logged]
Curated Dataset (snapshot with ID)
    ↓ [snapshot ID logged]
Embedding Job (versioned model)
    ↓ [output SHA logged; model version pinned]
Vector Index (versioned)
    ↓ [index SHA logged]
Training / Prompt Optimization / Retrieval
    ↓ [all input SHAs logged in run metadata]
Model Artifact / Prompt Template / Feature
    ↓ [artifact SHA logged]
Deployment (references artifact SHA + config SHA)
    ↓ [deployment ID logged]
Serving Traffic (each request logs deployment ID)
    ↓ [request-level provenance]
Feedback / Evaluation (references deployment ID)
    ↓
Loop back with new curated data
```

**Every artifact has:**
- SHA-256 hash of content.
- Metadata including upstream artifact SHAs.
- Timestamp of creation.
- Producer (which pipeline run created it).
- Consumer registry (who's using it).

**Every run has:**
- Run ID (unique).
- Pipeline version (git SHA).
- Input artifact SHAs.
- Output artifact SHAs.
- Configuration (fully materialized, no env vars).
- Environment (packages + versions).

**The reproducibility test:**
- Delete all output artifacts.
- Given only the run manifest, can you regenerate them exactly?
- If yes: reproducible.
- If no: there's an unlogged dependency.

**Common unlogged dependencies to watch for:**
- Time-dependent data (current time, timezone).
- Random seeds not fixed.
- External API calls with non-deterministic outputs.
- Package versions not pinned.
- Environment variables not captured.
- File-system ordering (rare, but happens).

**Tools that help:**
- **MLflow** — experiment tracking with artifact lineage.
- **W&B Artifacts** — versioned datasets, models, indexes tied to runs.
- **Guild AI** — reproducibility-focused ML.
- **Metaflow** — Netflix's ML workflow tool.
- **ZenML** — MLOps framework with lineage.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `why_version_data.py` | Real reasons — the incidents that trace back |
| `dvc_deep_dive.py` | Git for data |
| `lakefs_deep_dive.py` | Data lake versioning |
| `delta_lake_and_iceberg.py` | Table formats with time travel |
| `dataset_snapshots.py` | Point-in-time |
| `data_lineage_tracking.py` | Where did this come from |
| `reproducibility_workflow.py` | End-to-end |

---

*Previous: [← Vector DB Internals](../vector_db_internals/README.md) · Next: [Deduplication at Scale →](../deduplication_at_scale/README.md)*  ·  *Back to [main README](../../README.md)*
