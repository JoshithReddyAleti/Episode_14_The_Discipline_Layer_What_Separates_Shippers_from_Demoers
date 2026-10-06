# 🧹 Deduplication At Scale — The Unsexy Essential

> *Duplicate documents in your training corpus teach your model to overweight repeated patterns. Duplicates in your RAG index give users the same answer three times. Duplicates in your eval set inflate your numbers. Every serious AI system dedups. Most don't do it well.*

---

## Why Dedup Matters (`why_dedup_matters.py`)

**In training:**
- Duplicates → over-representation → mode collapse toward the duplicated pattern.
- Empirical: reducing 30% near-duplication in pretraining corpora improves downstream benchmarks by 3-8% (Lee et al. 2022, "Deduplicating Training Data").
- Fine-tuning is even more sensitive; 10-20% dedup rate is common in polished datasets.

**In retrieval / RAG:**
- Same document indexed twice → retrieved twice → wastes context window.
- Near-duplicates (v1, v2 of the same policy doc) → confusion about which is current.
- User experience: "you gave me three copies of the same answer."

**In evaluation:**
- Duplicates between train and test → inflated benchmarks.
- Duplicates within test → weighted questions (asked "twice") skew metrics.

**In production monitoring:**
- Same input generating multiple log entries → misleading traffic metrics.
- Near-duplicate queries clustered → better user intent analysis.

**Real-world numbers from public corpora:**
- Common Crawl raw: **50-80% near-duplicates**.
- Wikipedia dumps: **5-15%** (mostly small edits).
- Curated instruction datasets: **10-30% before dedup**.
- Synthetic data (LLM-generated): **30-60% before aggressive dedup**.

**Rule:** every ingested corpus goes through a multi-stage dedup pipeline. Skipping it is not an optimization — it's a bug.

---

## Exact Deduplication (`exact_deduplication.py`)

**Exact dedup = binary-identical duplicates.**

**Algorithm:**
1. For each document, compute a strong hash (SHA-256 typical).
2. Store hashes in a set or database.
3. On insert, check membership; skip duplicates.

**Complexity:** O(N × doc_size) for hashing; O(N) memory for hash set.

**Implementation:**

```python
import hashlib
import sqlite3

def exact_dedup(docs, db_path):
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS seen_hashes (hash TEXT PRIMARY KEY)")
    unique_docs = []
    for doc in docs:
        h = hashlib.sha256(doc.encode()).hexdigest()
        cur = conn.execute("SELECT 1 FROM seen_hashes WHERE hash = ?", (h,))
        if cur.fetchone() is None:
            conn.execute("INSERT INTO seen_hashes VALUES (?)", (h,))
            unique_docs.append(doc)
    conn.commit()
    return unique_docs
```

**At petabyte scale:**
- Hash storage: 32 bytes SHA-256 per doc. For 1B docs: 32 GB.
- Bloom filter for approximate check (1% false-positive rate): ~1.2 GB for 1B docs.
- Use Bloom for fast negative check, exact hash lookup for potential matches.

**Distributed:**
- Compute hashes in parallel (Spark, Ray).
- Aggregate hashes to a central store.
- Coordinated dedup or per-partition + final merge.

**Catches:** exact copy-pastes, mirrors, retransmitted files.

**Doesn't catch:** anything with whitespace changes, timestamp differences, formatting variation. That's where near-dup comes in.

---

## MinHash and LSH (`minhash_and_lsh.py`)

**Near-duplicate detection at scale.**

**Jaccard similarity** — for two sets A and B:
```
Jaccard(A, B) = |A ∩ B| / |A ∪ B|
```
Range: 0 (disjoint) to 1 (identical).

For text: represent each doc as a set of **shingles** (n-grams). E.g., 5-shingles of "the quick brown fox" = {"the quick brown fox", "quick brown fox jumps", ...}.

**MinHash** — approximate Jaccard efficiently.

**The key theorem:**
For a random permutation π of the universe of shingles:
```
P(min(π(A)) == min(π(B))) = Jaccard(A, B)
```

**MinHash algorithm:**
1. Represent each doc as a set of shingles.
2. Apply K independent hash functions to each shingle.
3. For each doc, store the K minimum hash values (the MinHash sketch).
4. Estimate Jaccard: sketch_overlap(doc_a, doc_b) / K ≈ Jaccard(A, B).

**LSH (Locality-Sensitive Hashing)** — index MinHash sketches so similar ones collide.

**LSH banding:**
1. Split the K MinHash values into `b` bands of `r` values each (K = b × r).
2. Hash each band separately → each doc appears in `b` different hash buckets.
3. Docs sharing any band are candidates.
4. Verify candidates with actual Jaccard.

**Probability a pair with true Jaccard s gets found:**
```
P(match) = 1 - (1 - s^r)^b
```

The **S-curve** tuning:
- r=5, b=20: 50% detection at ~55% Jaccard.
- r=10, b=20: 50% detection at ~72% Jaccard.
- Choose r/b for your target similarity threshold.

**Tool:** `datasketch` library (Python).

```python
from datasketch import MinHash, MinHashLSH

lsh = MinHashLSH(threshold=0.85, num_perm=128)

for doc_id, doc_text in docs:
    m = MinHash(num_perm=128)
    for shingle in shingles(doc_text, n=5):
        m.update(shingle.encode())
    lsh.insert(doc_id, m)

# Query
query = MinHash(num_perm=128)
for s in shingles(new_doc, n=5):
    query.update(s.encode())
duplicates = lsh.query(query)
```

**Complexity:**
- MinHash: O(shingles × K) per doc; K ≈ 128 typical.
- LSH insert: O(b) per doc.
- LSH query: O(b + candidates).

**At 1B docs:**
- Sketch storage: 128 × 8 bytes = 1 KB/doc → 1 TB.
- Use compact MinHash (e.g., 64-bit hashes packed) to reduce to ~256 bytes/doc → 256 GB.
- Distributed LSH via bucketized hashing across nodes.

---

## Semantic Deduplication (`semantic_deduplication.py`)

**When paraphrases matter.**

MinHash catches near-copies at the shingle level. It misses:
- Paraphrased versions with same meaning.
- Translated versions.
- Summary vs original.

**Semantic dedup = embedding-based.**
1. Embed each doc.
2. Find nearest neighbors above a cosine similarity threshold.
3. Cluster; keep representative from each cluster.

**Cosine similarity threshold guidance:**
- **0.99+**: near-identical (same content, minor differences).
- **0.95-0.99**: paraphrases, translations, close variants.
- **0.90-0.95**: same topic, different wording.
- **<0.90**: probably different.

**At scale:**
- 100M docs × 1536-dim embeddings = 600 GB.
- Semantic dedup requires vector similarity search over the whole corpus.
- HNSW / IVF with high threshold + retention policy.

**Practical:**
```python
# Threshold-based dedup with HNSW
from qdrant_client import QdrantClient
import numpy as np

client = QdrantClient(url="http://localhost:6333")
client.create_collection("dedup_corpus", vectors_config={"size": 1536, "distance": "Cosine"})

unique_ids = []
for doc_id, embedding in corpus_embeddings:
    hits = client.search(
        collection_name="dedup_corpus",
        query_vector=embedding,
        limit=1,
        score_threshold=0.95,
    )
    if not hits:
        client.upsert("dedup_corpus", points=[{"id": doc_id, "vector": embedding}])
        unique_ids.append(doc_id)
```

**Trade-off:** semantic dedup is more expensive (embedding cost + index cost) but catches paraphrase-level duplication that MinHash misses.

**Combined pipeline (most effective):**
1. Exact dedup (bloom → hash).
2. MinHash/LSH at ~0.7-0.85 Jaccard threshold.
3. Semantic dedup at ~0.95 cosine threshold within remaining docs.

---

## Document-Level Dedup (`document_level_dedup.py`)

**Dedup whole documents.**

**Strategy considerations:**
- **What's "the same" document?** Different versions of a policy doc? Different translations?
- **Which to keep?** Latest? Longest? Most authoritative source?

**Practical rules:**
- **By source:** prefer canonical source (official website over aggregator).
- **By recency:** latest revision.
- **By length:** longest complete version.
- **By quality score:** perplexity, classifier score.

**Metadata to track:**
- Duplicates_removed_because_of: [doc_id_1, doc_id_2, ...]
- Retention_reason: "canonical source" / "longest" / "highest quality"
- Alternate_source_urls: [...]

**Common failure:** deduping too aggressively when documents are actually distinct (e.g., news articles about the same event from different outlets — each has value).

**Rule:** dedup with human-review of a sample before running at scale. What "duplicate" means depends on the corpus.

---

## Chunk-Level Dedup (`chunk_level_dedup.py`)

**Within-document dedup — chunks that appear across many documents.**

**Common in:**
- Legal boilerplate (arbitration clauses, disclaimers).
- Website headers/footers scraped repeatedly.
- Book chapters excerpted in reviews.
- Standard forms with mostly-identical structure.

**Problem:** if 40% of your chunks are boilerplate, your embedding index is 40% wasted, and retrieval keeps returning boilerplate.

**Approach:**
1. Chunk each document.
2. MinHash / semantic dedup at chunk level.
3. **Keep unique chunks; track which docs they came from.**
4. On retrieval, if a boilerplate chunk matches, expand to source doc IDs.

**Alternative:** filter boilerplate before chunking with heuristics (position in doc, frequency across corpus, low semantic content).

**Metric to watch:** proportion of chunks appearing in >1 document. In enterprise corpora: 5-30% typical. Above 30% suggests boilerplate is a big issue.

---

## Dedup Pipeline at Scale (`dedup_pipeline_at_scale.py`)

**Petabyte-scale dedup pipeline:**

```
Raw corpus (1B+ docs, 10 TB)
    ↓
[Stage 1] Exact dedup (SHA-256 hashing)
    ├── Bloom filter for quick negative check
    ├── Distributed hash map (Redis / KeyDB / disk-based)
    └── Removes ~20-40% typical
    ↓
[Stage 2] MinHash/LSH (near-duplicate)
    ├── Spark / Ray job computing sketches
    ├── LSH banding at ~0.85 Jaccard threshold
    ├── Similarity graph → connected components
    └── Removes another ~20-40%
    ↓
[Stage 3] Semantic dedup (paraphrase-level)
    ├── Batch embedding job
    ├── HNSW/IVF index at high threshold
    ├── Removes another ~5-15%
    ↓
[Stage 4] Chunk-level dedup (boilerplate)
    ├── Applied after chunking
    ├── Removes another ~10-20% of chunks
    ↓
Deduplicated corpus (~30-60% of original)
```

**Infrastructure:**
- **Spark or Ray** for distributed compute.
- **Object storage** (S3/GCS) for input/output.
- **Metadata DB** (Postgres) tracking dedup decisions.
- **Bloom filter service** for hot-path exact check.
- **Vector DB** for semantic dedup.

**Cost model:**
- Exact stage: cheap (~$50 per 100M docs).
- MinHash stage: moderate (~$200-500 per 100M docs).
- Semantic stage: expensive (embedding cost dominant, $500-5000 per 100M docs).
- Total: **$1000-10000 per 100M-doc dedup pass** depending on quality.

**Cadence:**
- Full re-dedup: quarterly or on-major-corpus-refresh.
- Incremental: on every ingestion batch.
- Real-time: near-impossible at scale; use "seen recently" cache for hot path.

---

## Dedup Evaluation (`dedup_evaluation.py`)

**"How do I know my dedup worked?"**

**Metrics:**

**1. Deduplication rate**
- (docs_before − docs_after) / docs_before.
- Baseline expectations: 30-70% for web scrape; 10-30% for curated; 5-15% for polished.

**2. Precision**
- Of docs marked as duplicates, what fraction really are duplicates?
- Verify on a sampled subset with human review.
- Target: >95%.

**3. Recall**
- Of true duplicates in the corpus, what fraction were caught?
- Requires labeled duplicate pairs.
- Target: >90%.

**4. False-positive rate on hard cases**
- Different-but-similar docs (e.g., two news articles about same event).
- Target: <5%.

**5. Downstream impact metrics**
- Training loss curves on dedup vs non-dedup subsets.
- Eval benchmark scores.
- Retrieval quality (recall@k on golden test set).

**Testing methodology:**
1. Sample 500-1000 pairs across a range of similarity levels.
2. Human-label as duplicate / not.
3. Run dedup pipeline; check predictions.
4. Compute precision, recall, F1.

**Common failure:**
- Being too aggressive: F1 tuned to high recall drops precision, removes distinct content.
- Being too lax: recall stays low, corpus stays bloated.
- No downstream metrics: quality changes go unmeasured.

**Rule:** treat dedup pipeline like a classifier. Version it. Test it. Measure precision/recall. Deploy changes through A/B.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `why_dedup_matters.py` | Training + retrieval quality |
| `exact_deduplication.py` | Hashing, bloom filters |
| `minhash_and_lsh.py` | Near-dup at scale — full math |
| `semantic_deduplication.py` | Embedding-based |
| `document_level_dedup.py` | Whole docs |
| `chunk_level_dedup.py` | Within-doc, boilerplate |
| `dedup_pipeline_at_scale.py` | Petabyte-scale 4-stage pipeline |
| `dedup_evaluation.py` | Precision, recall, downstream impact |

---

*Previous: [← Data Versioning](../data_versioning/README.md) · Next: [Contamination Detection →](../contamination_detection/README.md)*  ·  *Back to [main README](../../README.md)*
