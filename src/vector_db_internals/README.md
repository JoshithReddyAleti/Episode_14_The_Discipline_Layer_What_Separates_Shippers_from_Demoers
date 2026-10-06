# 📐 Vector DB Internals — Deep Enough To Choose And Tune

> *"Just use Pinecone" is the answer teams give when they don't understand what vector DBs actually do. This section is the level of detail you need to make architecture decisions that scale, tune indexes that actually meet SLAs, and understand why your recall@10 dropped last week.*

---

## How Vectors Get Stored (`how_vectors_get_stored.py`)

**Fundamental unit:** a vector = fixed-length array of floats (typically 128-4096 dimensions).

**Storage math:**
- 1M vectors × 1536 dims × 4 bytes (fp32) = **~6 GB raw**.
- 100M vectors × 1536 dims × 4 bytes = **~600 GB raw**.
- 1B vectors × 1536 dims × 4 bytes = **~6 TB raw**.

**Reality:** you almost never store raw fp32. Compression is table stakes at scale.

**Storage layouts:**
- **Flat file (baseline):** contiguous array of vectors. Exact search possible; O(N) per query.
- **HNSW graph:** vectors + graph edges (~1.5-2× raw storage overhead).
- **IVF-quantized:** cluster centroids + quantized vector codes (10-100× compression vs fp32).
- **Disk-resident (DiskANN):** SSD-optimized layouts for billion-scale.

**Alongside the vector:**
- **Sparse ID** (int64): the record identifier.
- **Metadata** (JSON blob): document ID, timestamp, source, tags, tenant ID, ACL.
- **Sparse features** (optional): BM25 sparse vector for hybrid search.

**Key operations per vector:**
- `insert(id, vector, metadata)` — with index update.
- `delete(id)` — often deferred (tombstone + compaction).
- `search(query_vector, k, filter)` — the hot path.
- `update(id, vector)` — actually delete + insert.

---

## Exact vs Approximate Search (`exact_vs_approximate_search.py`)

**Exact search** — for a query vector `q`, compute distance to *every* stored vector, sort, return top-k.

- Time: **O(N × d)** where N = number of vectors, d = dimensions.
- 1M × 1536 fp32 vectors ≈ 6 GB read per query → ~100ms on modern hardware with SIMD.
- 100M vectors → ~10 seconds/query. Unusable interactively.

**Approximate Nearest Neighbor (ANN)** — trade a small amount of recall for a large amount of speed.

- Time: **O(log N)** or **O(√N)** typical.
- 100M vectors → sub-10ms if properly indexed.

**The recall/speed trade-off:**
- **Recall@k** = (# of true top-k neighbors returned) / k.
- Recall@10 = 0.95 means: out of the true top-10, you got 9.5 on average.
- Realistic operating points:
  - HNSW at reasonable params: recall@10 = 0.95-0.99.
  - IVF-Flat: 0.90-0.98.
  - IVF-PQ: 0.85-0.95.
  - Binary quantization: 0.80-0.92.

**When to use exact:**
- N < 100K (small enough to be fast).
- Recall = 1.0 required (regulatory, correctness-critical).
- Cost of missing a true neighbor is catastrophic.

**When to use ANN:** everything else in 2026.

---

## Flat Indexes (`flat_indexes.py`)

**Flat = no index.** Vectors stored contiguously; search = linear scan.

**Why they still matter:**
- **Ground truth for benchmarking recall.** Every ANN evaluation uses flat as the "true top-k" reference.
- **Small collections** (<100K) where index build cost isn't worth it.
- **Development / debugging** — deterministic, no tuning.
- **Component in composite indexes** — IVF uses flat inside each cluster.

**FAISS Flat variants:**
- `IndexFlatL2` — L2 distance, brute force.
- `IndexFlatIP` — inner product, brute force. For cosine, normalize vectors first.

**Optimizations even for flat:**
- SIMD (AVX-512): 8-16× speedup vs naive loops.
- GPU flat: 100-1000× over CPU when vectors fit in HBM.
- Batched query (search 100 queries at once): amortizes cache misses.

**Practical rule:** if N × d × 4 bytes fits in cache (L3 or GPU HBM), flat is faster than most ANN algorithms because ANN has index-traversal overhead.

---

## HNSW Deep Dive (`hnsw_deep_dive.py`)

**HNSW (Hierarchical Navigable Small World)** — Malkov & Yashunin, 2016. The workhorse ANN algorithm of 2020-2026. Used inside Qdrant, Weaviate, Milvus, pgvector (recent), Chroma, and every managed vector DB.

**The intuition:**
- Build a multi-layer graph where each node is a vector.
- Upper layers = sparse "shortcuts" spanning distant regions.
- Lower layers = dense local connections.
- Search: start at the top of the pyramid, greedy descent to nearest neighbor at each layer.

**The graph construction algorithm:**

```
def build_hnsw(vectors, M, efConstruction):
    # For each vector, assign a max layer:
    # layer = floor(-log(random()) * mL) where mL = 1 / ln(M)
    # Layer 0 always exists; higher layers are exponentially rarer.
    
    for i, v in enumerate(vectors):
        max_layer_i = sample_layer()
        
        # Insert v at every layer from max_layer_i down to 0.
        entry_point = graph.entry_point  # highest-layer node
        
        for l in range(graph.top_layer, max_layer_i, -1):
            # Greedy search in layer l starting from entry_point.
            entry_point = greedy_search_layer(v, entry_point, l, ef=1)
        
        for l in range(min(max_layer_i, graph.top_layer), -1, -1):
            # Find candidates via search with ef=efConstruction.
            candidates = search_layer(v, entry_point, l, ef=efConstruction)
            
            # Select up to M neighbors from candidates using a heuristic
            # (e.g., prefer diverse rather than just closest).
            neighbors = select_neighbors(v, candidates, M)
            
            # Add bidirectional edges.
            for u in neighbors:
                add_edge(v, u, l)
                add_edge(u, v, l)
                # Prune u's neighbor list if it exceeds max_M.
                if degree(u, l) > max_M:
                    prune_edges(u, l, max_M)
```

**The query algorithm:**

```
def search(query, k, efSearch):
    entry_point = graph.entry_point
    
    # Descend through upper layers greedily (ef=1).
    for l in range(graph.top_layer, 0, -1):
        entry_point = greedy_search_layer(query, entry_point, l, ef=1)
    
    # Search bottom layer with ef=efSearch (candidates > k).
    candidates = search_layer(query, entry_point, 0, ef=efSearch)
    
    # Return the top-k closest from candidates.
    return top_k(candidates, k)
```

**Complexity:**
- Build: **O(N × log(N) × M × efConstruction)** — dominant term is graph traversal per insert.
- Query: **O(log(N))** amortized, with constant factor determined by efSearch.
- Memory: **~N × (d × 4 + M × 8)** bytes — vector + M edges (int64) per node. For M=32, d=1536: overhead ~256 bytes/vector on top of raw.

**Real numbers on modern hardware:**
- Build 10M × 1536 vectors, M=32, efC=400: ~2-4 hours on 32-core CPU.
- Query same index at efS=128: ~0.5-2ms per query, 500-2000 QPS single-thread.
- Memory footprint: ~64 GB for 10M × 1536 including graph.

---

## HNSW Parameter Tuning (`hnsw_parameter_tuning.py`)

**Three tunables, in order of impact:**

### `efSearch` (query-time)
- Beam width for search at layer 0.
- **Larger** → higher recall, higher latency.
- Typical range: 64-512.
- **Tuning approach:** start with efS=100, measure recall@10 on a labeled query set, increase efS until recall meets SLA.
- **Cost:** roughly linear in latency and CPU per query.

### `M` (build-time, per-node max connections)
- Higher M → denser graph → higher recall potential, more memory, slower build.
- Typical range: 16-64.
- **M=16:** OK for lower-dim (<512) or small collections.
- **M=32:** default for text embeddings (768-1536 dim).
- **M=64:** high-dim (>2048) or high-recall requirements.
- **Memory cost per doubling M:** ~+8 bytes × M × N.

### `efConstruction` (build-time)
- Beam width during graph construction.
- Higher → better graph quality → higher recall at query time.
- Typical range: 100-500.
- **Diminishing returns** past ~500 for most cases.
- **Cost:** build time scales linearly with efConstruction.

### Rule-of-thumb starting points

| Use case | M | efConstruction | efSearch |
|---|---|---|---|
| Small (<1M), fast build needed | 16 | 100 | 50-100 |
| Medium (1-10M), balanced | 32 | 200 | 100 |
| Large (10-100M), quality-critical | 32 | 400 | 128-256 |
| Very large (100M+), extreme SLA | 48 | 500 | 200-400 |

### The tuning loop
1. Fix build params, sweep `efSearch`, plot recall@10 vs QPS. This is your operating curve.
2. Pick the efSearch that meets your recall SLA at the QPS you need.
3. If neither is achievable → rebuild with higher M or efConstruction.
4. Rebuilds are expensive at scale, so most tuning happens at query time.

**Signals you need higher M/efC:**
- Recall plateaus below SLA regardless of efSearch.
- Recall drops steeply with high k (>100).
- Filtered queries have much lower recall than unfiltered.

---

## IVF Deep Dive (`ivf_deep_dive.py`)

**IVF (Inverted File Index)** — coarse quantization by clustering, then search within relevant clusters.

**Algorithm:**

**Training:**
1. Sample subset of vectors.
2. Run k-means with `nlist` centroids.
3. For each stored vector, assign to nearest centroid → cluster ID.
4. Store inverted lists: `centroid_id → [vector_id, ...]`.

**Query:**
1. For query `q`, compute distance to all `nlist` centroids.
2. Pick top `nprobe` closest centroids.
3. Search vectors in those clusters exhaustively (or with sub-index).
4. Return top-k.

**Parameters:**
- **`nlist`** — number of clusters. Typical: `√N` (e.g., 10K for 100M vectors).
- **`nprobe`** — clusters to search at query time. Typical: 1-256, tunable per query.

**Complexity:**
- Build: O(N × nlist) for k-means.
- Query: O(nlist × d) for centroid distances + O((N/nlist) × nprobe × d) for cluster search.
- With nprobe=16 out of nlist=10000: search ~0.16% of vectors → ~600× speedup vs exact.

**Variants:**
- **IVF-Flat:** vectors stored uncompressed in clusters. High recall, less compression.
- **IVF-PQ:** vectors compressed with Product Quantization (below). Massive compression, some recall loss.
- **IVF-SQ:** scalar quantization (int8). Middle ground.

**HNSW vs IVF:**
- HNSW: better recall at low memory budgets; simpler tuning.
- IVF: better for very large collections with heavy compression (IVF-PQ scales to billions).
- Hybrid **HNSW-on-IVF** or **IVFPQ+refine** used at frontier scale.

---

## Product Quantization (`product_quantization.py`)

**Product Quantization (PQ)** — Jégou et al. 2011. The workhorse compression technique for billion-scale vector search.

**The idea:**
- Split each `d`-dim vector into `M` sub-vectors of dim `d/M`.
- For each sub-space, run k-means with `k*` centroids (typically 256 → 8-bit codes).
- Encode a vector as `M` × 1-byte codes (indices into centroids).
- **Compression:** `d × 4` bytes fp32 → `M` bytes. For d=1536, M=64: 6144 → 64 bytes = **96× compression**.

**Concrete example:**
- 1536-dim vector.
- Split into M=64 sub-vectors of dim 24.
- Each sub-vector encoded to 8 bits (256 centroids).
- Total: 64 bytes vs 6144 bytes raw.

**Distance computation (Asymmetric Distance Computation - ADC):**
- Query vector `q` stays uncompressed.
- Precompute: for each of M sub-spaces, distance from query sub-vector to all 256 centroids → M×256 distance tables.
- For each stored vector (M byte-codes): look up M values from precomputed tables, sum. **Zero mults, only lookups.**

```
def pq_search(query, codes, centroids, top_k):
    # Precompute distance tables: M x 256
    tables = []
    for m in range(M):
        q_sub = query[m*sub_d : (m+1)*sub_d]
        dists = [l2_dist(q_sub, centroids[m][c]) for c in range(256)]
        tables.append(dists)
    
    # Score each database vector via table lookups
    scores = []
    for i, code in enumerate(codes):
        s = sum(tables[m][code[m]] for m in range(M))
        scores.append((s, i))
    
    return heapq.nsmallest(top_k, scores)
```

**Trade-offs:**
- Recall drops with higher compression (higher M helps within limits).
- Recall drops on hard queries (out-of-distribution).
- ADC is exact for the compressed representation but approximate for the original.

**Typical operating points (1536-dim text embeddings):**
- M=48 (32 bytes/vec, 192× compression): recall@10 ~0.90.
- M=64 (64 bytes/vec, 96× compression): recall@10 ~0.94.
- M=96 (96 bytes/vec, 64× compression): recall@10 ~0.97.

**Refinement:** many production systems use PQ for candidate generation, then re-rank top-N with fp32 flat distances → hits ~0.98 recall.

---

## Scalar Quantization (`scalar_quantization.py`)

**Scalar quantization** — the simple compression: fp32 → int8 (or int4).

**Algorithm:**
1. For each dimension, find min and max values across the corpus.
2. Linearly map to int8 range: `int8_val = round((fp32_val - min) / (max - min) * 255) - 128`.
3. Store 1 byte per dimension instead of 4.
4. On query: dequantize on the fly or use asymmetric distance.

**Compression:** 4×.

**Recall loss:** typically 1-3% vs fp32.

**Advantages over PQ:**
- Simpler; less tuning.
- Preserves per-dimension semantics.
- Compatible with SIMD int8 kernels.
- Random access is fast (no table lookups).

**Disadvantages vs PQ:**
- Less compression (4× vs 100×).
- Doesn't handle dimensions with different scales as gracefully.

**When to use scalar over PQ:**
- Memory budget is 4× compression but not more.
- Deployment supports int8 hardware acceleration.
- Simpler pipeline.

**Modern hybrid:** **RaBitQ** and similar techniques combine scalar-like simplicity with better compression, gaining adoption in 2025-2026.

---

## Binary Quantization (`binary_quantization.py`)

**Binary quantization** — the extreme compression: fp32 → 1 bit per dimension.

**Algorithm:**
1. For each dimension, threshold (typically 0 or the mean).
2. Store 1 bit per dim: 1 if above threshold, 0 otherwise.
3. Distance = Hamming distance (population count of XOR), computed with `popcount` CPU instruction.

**Compression:** 32×.

**Speed:** **enormous.** Hamming distance on 1536 bits = 24 × 64-bit XOR + popcount = a few nanoseconds per comparison. 10-100× faster than fp32 L2.

**Recall loss:**
- Naive: recall@10 drops from 0.98 (fp32) to 0.60-0.75.
- With **query-side asymmetric** (binary corpus, fp32 query): recall@10 ~0.85-0.90.
- With **re-ranking top-N** with fp32: recall@10 ~0.95-0.97.

**When to use:**
- Massive scale (>100M vectors) where memory dominates cost.
- First-pass filter before more expensive re-ranking.
- Combined with PQ or scalar quantization in tiered indexes.

**Modern adoption (2025-2026):** MRL (Matryoshka Representation Learning) embeddings + binary quantization getting deployed at scale by search-heavy companies.

---

## Disk-ANN and DiskANN (`disk_ann_and_diskann.py`)

**DiskANN (Microsoft, 2019)** — vector search beyond RAM.

**Why:** billion-vector RAM-only indexes cost tens of thousands of dollars in memory. Disk-based indexes are 10-100× cheaper.

**Key ideas:**
- **Vamana graph** — DiskANN's HNSW-like graph algorithm, optimized for SSD access patterns.
- **Two-tier storage:**
  - Compressed representations (PQ) in RAM.
  - Full vectors on SSD, fetched only when needed.
- **Cache-conscious layout:** graph edges and vectors grouped by locality.

**Query:**
1. In-RAM PQ codes used for initial candidate ranking.
2. Best few hundred candidates fetched from SSD for exact scoring.
3. Return top-k.

**Performance (1B vectors, 128 dims):**
- Memory: ~64 GB (down from ~500 GB for RAM-only).
- Latency: 5-15 ms per query.
- QPS: 1000-5000 single-node.

**Production systems using DiskANN-like:**
- **Milvus** with disk-based mode.
- **Weaviate** with lazy loading.
- **Qdrant** on-disk vectors.
- **Turbopuffer** (2023+) — serverless, disk-backed.

**Trade-off:** SSD latency (~100μs) vs RAM (~100ns). Disk-ANN designs minimize SSD accesses per query.

---

## Hybrid Search — BM25 + Vector (`hybrid_search_bm25_vector.py`)

**Why hybrid:** vector search excels at semantics; keyword search excels at exact terms (product SKUs, names, jargon). Real queries mix both.

**Architecture:**
- Build **two indexes** side by side:
  - **Sparse (BM25 / TF-IDF)** — inverted index of tokens.
  - **Dense (vector)** — HNSW/IVF.
- Query hits both, results fused.

**Fusion strategies:**
- **Reciprocal Rank Fusion (RRF)** — score(item) = Σ 1/(k + rank_in_list). Simple, robust.
- **Weighted sum** — normalize both scores to [0,1], weight (typically 0.3-0.7 for dense).
- **Learned fusion** — model that combines both signals given query features.

**Result:** hybrid consistently beats either alone by 5-15% on recall metrics, especially on:
- Rare terms (names, IDs, technical jargon).
- Short queries.
- Queries where semantic match ≠ lexical match ("cheap flights to NYC" — need "cheap" and "NYC" literal).

**Sparse-dense fusion in practice:**
- **Native support:** Qdrant, Weaviate, Vespa, Elastic (with vector plugin).
- **Manual assembly:** two separate services + fusion in application code.
- **Sparse encoders (SPLADE, uniCOIL):** learned sparse representations that behave like BM25 but with neural-generated weights. Increasingly common.

**When to use hybrid:** default in 2026 for enterprise search and RAG. The overhead is small; the recall gain is real.

---

## Metadata Filtering at Scale (`metadata_filtering_at_scale.py`)

**The problem:** users want "top 10 similar docs, but only from Q3 2025 and only from the finance folder." The vector similarity search returns 10 unfiltered results. Post-filtering leaves you with 3 (or 0).

**Two strategies:**

### Pre-filtering
- Apply filter first, then search only among matching vectors.
- Correct results, but requires index that supports it.
- **HNSW:** requires filter-aware graph traversal (Weaviate, Qdrant, Milvus support this).
- **IVF:** filter within each probed cluster.

### Post-filtering
- Search over full index, then filter results.
- Simple to implement but can miss neighbors.
- **Requires overfetching** — retrieve k' >> k, filter, hope enough survive.
- Fails when filter is very selective (<10% of corpus matches).

**Modern approach:**
- **Attribute-aware HNSW** — filter checked during graph traversal, guiding walk to matching nodes.
- **Partitioned indexes** — separate index per common filter value (e.g., per tenant).
- **Metadata index** — B-tree / inverted index on metadata + intersection with vector search results.

**Rule of thumb:**
- Filter selectivity >30%: post-filter with overfetch (k' = 3× k) usually fine.
- 5-30%: use filter-aware search.
- <5%: consider partitioned indexes.

**Common pitfalls:**
- **Silent recall drop** — post-filter without overfetch produces fewer results than requested; app doesn't notice.
- **Filter cardinality explosion** — many low-cardinality filters (tenant + user + region + date) → partitioning becomes complex.

---

## Sharding and Replication (`sharding_and_replication.py`)

**Distribute the index across machines.**

**Sharding strategies:**

### 1. Random / hash-based
- Each vector randomly assigned to a shard.
- Query fanned out to all shards, results merged.
- Simple, balanced, but every query hits every shard.

### 2. Attribute-based
- Shard by tenant, region, or category.
- Query with the attribute hits only the relevant shard.
- Efficient for filter-heavy workloads.
- Risk: uneven shard sizes.

### 3. Cluster-based
- Vectors clustered by similarity, each cluster is a shard.
- Query broadcast only to top-k relevant clusters.
- Requires re-sharding as data drifts.

**Replication:**
- Each shard has 2-3 replicas for availability.
- Read replicas can serve queries independently.
- Write coordination via consensus (Raft) or dedicated leader.

**Consistency models:**
- **Strong consistency** — writes visible to next query. Slower.
- **Eventual consistency** — writes visible within N seconds. Faster; typical for vector DBs.
- Vector search often tolerates eventual consistency (recall drops slightly during propagation).

**Real-world scales:**
- 100M vectors: single node with 128GB RAM often sufficient.
- 1B vectors: 4-8 shards typical.
- 10B+ vectors: 20+ shards, disk-ANN, careful cluster ops.

**Managed services** (Pinecone, Qdrant Cloud, Weaviate Cloud) handle sharding/replication for you at a premium.

---

## Choosing a Vector DB (`choosing_a_vector_db.py`)

**The 2026 landscape:**

| DB | Strengths | Weaknesses | When to pick |
|---|---|---|---|
| **Qdrant** | Rust, fast, great filtering, good docs, generous OSS | Younger ecosystem | Modern default; excellent all-rounder |
| **Weaviate** | Strong hybrid search, GraphQL, modules | Java-heavy config | Semantic + keyword blend |
| **Milvus** | Massive scale, GPU support, mature | Complex ops | Very large scale (1B+ vectors) |
| **Pinecone** | Fully managed, simple API | Vendor lock-in, cost at scale | Fast time-to-market |
| **pgvector** | Postgres integration | Slower at scale, weaker filtering | Small-medium in Postgres shop |
| **Chroma** | Simple, embedded, dev-friendly | Not for production scale | Prototyping, dev |
| **Turbopuffer** | Serverless, disk-based, cheap | Newer, limited features | Cost-sensitive, sparse queries |
| **Vespa** | Complex ranking, sparse+dense, mature | Steep learning curve | Search-first applications |
| **Elasticsearch/OpenSearch (vector)** | Existing OpenSearch shop | Slower ANN | Adding vector to keyword stack |

**Decision framework:**
1. **Existing ecosystem?** In Postgres → pgvector first. In Elastic → their vector plugin first.
2. **Scale?** <10M: any works. 10M-1B: Qdrant/Weaviate/Milvus. 1B+: Milvus, disk-ANN, or Turbopuffer.
3. **Managed vs self-hosted?** Managed = velocity. Self-hosted = cost + control at scale.
4. **Filtering-heavy?** Qdrant or Weaviate.
5. **Cost-critical?** Turbopuffer, Milvus with disk-ANN, or self-hosted.

**Anti-patterns:**
- Pinecone for a 500M-vector production system (cost explodes).
- pgvector at 100M+ with heavy filtering (query planner limitations).
- Chroma in production (not designed for it).
- Managed vector DB when you already have Postgres/OpenSearch expertise.

---

## Benchmarking Vector DBs (`benchmarking_vector_dbs.py`)

**Not all benchmarks are equal.**

**Metrics that matter:**
- **Recall@k** — against ground truth flat index. Report at multiple k (10, 100, 1000).
- **QPS** — sustained throughput per node. Report at target recall.
- **P50/P95/P99 latency** — single-query response times.
- **Index build time** — time to insert N vectors.
- **Memory footprint** — RAM at rest.
- **Cost per M vectors per month** — total infrastructure cost.

**Standard benchmarks:**
- **ANN-Benchmarks** (ann-benchmarks.com) — the canonical suite.
- **Big-ANN Benchmarks** — for billion-scale.
- **VectorDBBench** — vendor-agnostic comparison.

**Benchmarking pitfalls:**
- Testing at their preferred operating point, not yours.
- Missing filtered queries (many benchmarks skip these).
- Ignoring update workload (index build only).
- Single-thread testing (production is concurrent).
- Cold vs warm cache differences.

**Fair benchmarking checklist:**
- Same dataset (embeddings), same k, same recall target.
- Fixed hardware (CPU count, RAM, SSD).
- Warmup phase before measurement.
- Include filtered queries at realistic selectivity.
- Multi-threaded/concurrent workload.
- Long-running (>10 min) to catch tail latency.

**Rule:** run your own benchmark on your data. Vendor benchmarks are optimistic.

---

## Vector DB Cost Model (`vector_db_cost_model.py`)

**Real costs at scale:**

### RAM-based vector DB (HNSW)
Per 100M × 1536-dim vectors:
- Raw memory: ~600 GB (fp32) or ~150 GB (int8/SQ).
- HNSW overhead: ~30-50 GB.
- Total: ~200-650 GB.
- Cloud (r7g.16xlarge = 512 GB): ~$3.5/hr × 730 hr = **~$2,550/month**.

### Disk-based (DiskANN, Turbopuffer)
Per 100M vectors:
- RAM footprint: ~5-30 GB (just PQ codes).
- SSD: ~200 GB.
- Node: 32-64 GB RAM + 1 TB SSD.
- Cloud: ~$500-1,500/month.

### Managed (Pinecone typical)
Per 100M vectors, 100 QPS:
- ~$2,000-5,000/month depending on tier.

### Query costs
- Embedding API for user queries (~$0.02/1M tokens with modern embeddings): typically small.
- Vector DB CPU per query: negligible when index resident.
- Reranker (if used) per query: cross-encoder ~$0.001/query on GPU.

### Hidden costs
- **Reindexing** — full rebuild after model change.
- **Sharding ops** — as collection grows, resharding is painful.
- **Backup/restore** — vector data is bulky.
- **Cross-region** — replication cost for global RAG.

**Cost optimization tactics:**
- Quantization (int8, PQ) → 4-100× compression.
- Disk-ANN for less-latency-sensitive workloads.
- Filter partitioning — smaller effective search space per query.
- Cache popular queries.
- Cache embeddings for identical inputs.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `how_vectors_get_stored.py` | Storage layouts and math |
| `exact_vs_approximate_search.py` | The recall/speed trade-off |
| `flat_indexes.py` | The baseline, still useful |
| `hnsw_deep_dive.py` | Algorithm, math, complexity |
| `hnsw_parameter_tuning.py` | M, efConstruction, efSearch |
| `ivf_deep_dive.py` | IVF-Flat, IVF-PQ |
| `product_quantization.py` | PQ math and code |
| `scalar_quantization.py` | int8 vectors |
| `binary_quantization.py` | 1-bit vectors |
| `disk_ann_and_diskann.py` | Beyond RAM |
| `hybrid_search_bm25_vector.py` | The dual-index pattern |
| `metadata_filtering_at_scale.py` | Pre vs post filter |
| `sharding_and_replication.py` | Distributed vector DBs |
| `choosing_a_vector_db.py` | The 2026 landscape |
| `benchmarking_vector_dbs.py` | Recall@K, QPS, latency |
| `vector_db_cost_model.py` | Real costs at scale |

---

*Previous: [← Data Engineering Foundations](../data_engineering_foundations/README.md) · Next: [Data Versioning →](../data_versioning/README.md)*  ·  *Back to [main README](../../README.md)*
