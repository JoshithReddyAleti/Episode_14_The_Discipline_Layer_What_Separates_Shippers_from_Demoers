# Data Versioning Guide

## Why version data

Every serious production AI incident traces back to code, prompts, or data. The first two are versioned; the third usually isn't. Fix that.

## Three approaches by scale

**File-level (up to hundreds of GB): DVC.**
- Git-native workflow.
- Manifest files (.dvc) in Git; data in S3/GCS.
- Best for ML teams up to ~50 people.

**Data-lake (multi-TB): lakeFS.**
- Git-like branch/commit/merge on the whole lake.
- Zero-copy branching.
- Best for enterprise data platforms.

**Table format (unlimited): Delta Lake / Iceberg.**
- ACID transactions on object storage.
- Time-travel queries.
- Schema evolution.
- Best when data lives in queryable tables.

## Snapshot cadence

- Fast-changing corpora: daily.
- Reference datasets: weekly or on-change.
- Golden eval sets: versioned per change, not periodically.

## Reproducibility test

**Given only the run manifest, can you regenerate all output artifacts?**

If yes: reproducible. If no: some dependency is unlogged. Common culprits:
- Time-dependent data (current time, timezone).
- Random seeds not fixed.
- External API calls (non-deterministic outputs).
- Package versions not pinned.
- Environment variables not captured.

## What to version

Every AI artifact should record:
- SHA-256 content hash.
- Upstream artifact SHAs.
- Timestamp of creation.
- Producer (pipeline run).
- Environment (packages + versions).

