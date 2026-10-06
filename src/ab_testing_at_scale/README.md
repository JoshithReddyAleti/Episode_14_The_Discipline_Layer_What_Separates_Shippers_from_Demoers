# 🏢 A/B Testing At Scale — Enterprise Experimentation

> *When you're running 500+ experiments a year across dozens of teams, ad-hoc doesn't cut it. This section is what the mature experimentation function looks like.*

---

## Experimentation Platform Design (`experimentation_platform_design.py`)

**Architecture for scale.**

**Core components:**

**1. Experiment definition service.**
- Metadata store for all experiments.
- Owners, dates, status, allocation, metrics.
- API for CRUD.

**2. Assignment service.**
- Given (user_id, experiment_id) → variant.
- Deterministic hashing.
- Consistency across services.
- Sub-millisecond latency.

**3. Instrumentation SDK.**
- Client libraries (Python, JS, Java, Go).
- Logs assignments + events consistently.
- Handles edge cases (missing user_id, offline mode).

**4. Metric store.**
- Definitions of metrics (SQL, code).
- Aggregations at multiple time granularities.
- Versioned; changes tracked.

**5. Analysis service.**
- Runs statistical analyses on demand.
- Precomputes daily aggregates.
- Supports custom analyses.

**6. Dashboard.**
- Web UI for experiment monitoring.
- Automated reports.
- Alerts on guardrail breaches.

**7. Feature flag integration.**
- Assignment drives feature-flag decisions.
- Runtime lookup fast (edge caching).

**Reference architectures:**
- **Netflix's ABlaze** — internal, ~1000 experiments/quarter.
- **Airbnb's ERF** — Experimentation Reporting Framework.
- **Uber's XP** — cross-team experimentation.
- **Meta's Ax** — open-source Bayesian optimization + experimentation.
- **Statsig, Split** — commercial equivalents.

**Design principles:**
- **Decouple assignment from analysis.** Assignment must be always-on; analysis can be batch.
- **Batch aggregation.** Real-time is not needed for most decisions.
- **Metric versioning.** Definitions change; keep historical accuracy.
- **Self-serve for readers, gated for writers.** Anyone can view; changes go through review.

---

## Metric Stores For Experiments (`metric_stores_for_experiments.py`)

**The metric abstraction.**

**Problem without a metric store:**
- Each experiment defines metrics ad-hoc.
- Same metric computed differently across analyses.
- Definitions change silently.
- Historical comparisons impossible.

**Solution: centralized metric definitions.**
- Every metric has a canonical definition (SQL, code).
- Versioned.
- Owned by an accountable team.
- Available to all experimenters.

**Metric definition:**
```yaml
name: task_success_rate
description: Fraction of user tasks completed successfully
type: proportion
numerator:
  event: task_completed
  filter: outcome = 'success'
denominator:
  event: task_started
window: session
grain: user
current_version: 3.2
change_log:
  - v3.2 (2026-06): Updated to exclude bot traffic
  - v3.1 (2026-03): Corrected filter for retries
  - v3.0 (2026-01): Initial version
```

**Multiple metric versions:**
- Different experiments may use different versions.
- Comparisons across versions need care.

**Metric hierarchy:**
- **North star metrics** — 5-10 top-level.
- **Team metrics** — 20-100 per team.
- **Feature-specific metrics** — hundreds.

**Real-world platforms:**
- **Airbnb Minerva** — the well-known one.
- **Uber's Metric Platform.**
- **Custom** — most large orgs build their own.

**Rule:** without a metric store, experiment velocity plateaus at moderate scale. It's an infrastructure investment worth making.

---

## Experiment Governance (`experiment_governance.py`)

**Review, approval, cadence.**

**Governance levels:**

**Low-risk experiments (auto-approved):**
- Small allocation.
- Well-defined feature area.
- Standard metrics.
- No user-visible major changes.

**Medium-risk (team review):**
- Larger allocation.
- Cross-feature impact possible.
- New metrics or definitions.

**High-risk (org review):**
- Major user-facing change.
- Cross-team impact.
- Regulatory or safety-sensitive.
- New model deployment.

**Review criteria:**
- Design soundness (metric selection, power calc, allocation).
- Ethical considerations.
- Interference with other experiments.
- Cost budget.
- Rollback plan.

**Reviewer role:**
- Not gatekeeping.
- Ensuring quality and consistency.
- Often other experimenters ("peer review").

**Approval SLA:**
- Low-risk: automated, seconds.
- Medium-risk: 1-2 days.
- High-risk: 1-2 weeks.

**Conflict resolution:**
- Same users in multiple experiments — pre-check for conflicts.
- Sensitive combinations require sequencing.

**Post-experiment review:**
- Winners: verify sound analysis before ship.
- Interesting findings: share broadly.
- Failures: capture lessons.

---

## Democratizing Experiments (`democratizing_experiments.py`)

**Self-serve for teams.**

**Goal:** any product team can run an experiment without central team's involvement.

**Requirements:**

**1. Tooling.**
- UI for defining experiments.
- Instrumentation SDK.
- Automated analysis reports.
- Documentation.

**2. Education.**
- Statistical training for PMs and engineers.
- Case studies of good and bad experiments.
- Regular workshops.

**3. Standards.**
- Templates for common experiment types.
- Metric library to reuse.
- Design review checklist.

**4. Support.**
- Central team available for consultations.
- Slack channel for questions.
- Office hours.

**Progression from centralized to democratized:**
- **Phase 1:** central team runs all experiments.
- **Phase 2:** teams propose, central team runs.
- **Phase 3:** teams run with central review.
- **Phase 4:** teams run independently with tools + standards.
- **Phase 5:** central team focuses on platform + hardest experiments.

**Guardrails against misuse:**
- Automated sanity checks (SRM, sample size).
- Prevent obviously flawed designs (e.g., power < 20%).
- Flag experiments for review based on risk score.

**Metrics of democratization:**
- Number of experiments per quarter.
- Teams running experiments.
- Time from idea to insight.
- Success rate of experiments (proportion resulting in actionable decisions).

**Rule:** democratization is the difference between "an experimentation team" and "an experimentation culture." The latter is the target for high-maturity orgs.

---

## Learnings Libraries (`learnings_libraries.py`)

**Institutional memory.**

**Problem without a learnings library:**
- Same experiments run repeatedly by different teams.
- Insights lost when people leave.
- New experimenters lack context on prior efforts.
- Corporate memory measured in months, not years.

**Solution: searchable, curated library of experiment findings.**

**Content types:**
- **Experiment reports.** Full documents.
- **Summary cards.** 1-page insights per experiment.
- **Pattern findings.** Cross-experiment generalizations.
- **Anti-patterns.** Things that don't work.
- **Domain playbooks.** Best practices per area.

**Structure:**
- Tagged by feature area, metric, user segment, model.
- Searchable full-text.
- Cross-referenced.
- Curated by an experimentation team.

**Contribution flow:**
- After every experiment: mandatory summary card.
- Quarterly curation: identify patterns across recent experiments.
- Annual reviews: update playbooks based on year's learnings.

**Example patterns captured:**
- "Prompt changes affecting enterprise users take 3+ weeks to stabilize."
- "Latency > 3s degrades user metrics regardless of quality improvement."
- "Content moderation guardrails trigger 2× more on non-English users."
- "Retrieval changes benefit from small A/B before full rollout — retrieval quality doesn't predict user metrics well."

**Tools:**
- Wiki (Notion, Confluence).
- Custom UI on top of experiment DB.
- Search integrated with metric store.

**ROI:**
- Reduces duplicate experiments.
- Faster onboarding of new team members.
- Better hypothesis generation.
- Institutional resilience to turnover.

**Rule:** the learnings library is what compounds over years. Individual experiments teach one thing. The library teaches everything the org has learned.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `experimentation_platform_design.py` | Core architecture |
| `metric_stores_for_experiments.py` | Canonical metric definitions |
| `experiment_governance.py` | Review, approval |
| `democratizing_experiments.py` | Self-serve for teams |
| `learnings_libraries.py` | Institutional memory |

---

*Previous: [← Causal Inference For AI](../causal_inference_for_ai/README.md)*  ·  *Back to [main README](../../README.md)*
