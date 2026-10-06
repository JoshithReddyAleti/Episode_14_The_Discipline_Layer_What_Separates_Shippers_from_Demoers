# 🚀 Rollout Strategies — Deploying Winners Safely

> *The experiment declared a winner. Now deploy without breaking things. This section is the discipline of gradual, monitored, reversible deployment.*

---

## Gradual Rollout Patterns (`gradual_rollout_patterns.py`)

**Not all at once.**

**Standard progression:**
```
Day 1:   1% users
Day 3:   5% users
Day 5:   10% users
Day 8:   25% users
Day 11:  50% users
Day 14:  100% users
```

**Adjustments:**
- **Higher-risk changes:** slower progression, more monitoring at each step.
- **Lower-risk changes:** faster (skip intermediate steps).
- **Feature-flagged from the start** — instant rollback available.

**At each step:**
- Wait for monitoring window (24 hours typical).
- Check primary and guardrail metrics.
- Only proceed if all pass.
- Roll back to previous % if any fail.

**Auto-progression:**
- Some feature flag platforms support scheduled increments.
- Combined with metric thresholds for auto-halt.

**Manual gates:**
- High-stakes progressions require human review.
- On-call rotation for rollouts.

**Common rollout timings:**
- LLM prompt change: 3-7 days.
- New RAG source: 5-14 days.
- New model version: 2-4 weeks.
- New agent workflow: 4-8 weeks.

---

## Ring Deployment (`ring_deployment.py`)

**Internal → external progression.**

**Rings:**

**Ring 0: Dogfood.**
- Internal team members.
- Highest tolerance for issues.
- Fast feedback loop.

**Ring 1: Employees.**
- Company-wide.
- Higher expectations than dogfood.

**Ring 2: Beta users.**
- External users who opted in.
- Committed to reporting issues.
- Broader diversity than employees.

**Ring 3: General availability (GA).**
- All users.
- Standard production expectations.

**Ring 4: Broadcast (rare).**
- Actively marketed.
- Requires extra readiness for scale.

**Progression rules:**
- Each ring's duration: 1-7 days.
- Metrics gates between rings.
- Issues found in earlier ring must be fixed before promoting.

**Ring vs percentage:**
- Ring: qualitative user grouping (internal, external, etc.).
- Percentage: quantitative traffic split.
- Combined: rings within GA can be percentage-ramped.

**When to use rings:**
- New features (not iterations on existing).
- Features with security or trust implications.
- Features that materially change UX.

**Trade-off:**
- Slower launch.
- Better issue detection before broad exposure.

---

## Automated Rollback Triggers (`automated_rollback_triggers.py`)

**When to bail without waiting for humans.**

**Guardrail metrics + thresholds:**

**Error rate:**
- Threshold: 3× baseline for 15 minutes.
- Auto-rollback triggered.

**Latency:**
- P95 > 2× baseline for 15 minutes.
- Auto-rollback.

**Cost:**
- 5× baseline cost per query.
- Alert + human review; auto-rollback if sustained.

**Content moderation:**
- Content flag rate 5× baseline.
- Auto-rollback.

**Business metric:**
- Primary metric drops > X%.
- Human review; auto-rollback for severe drops.

**Alerting hierarchy:**
- Warning: notify on-call.
- Critical: page on-call.
- Auto-rollback: no waiting for human.

**Auto-rollback mechanism:**
```python
def check_and_rollback(experiment_id):
    metrics = get_current_metrics(experiment_id)
    baseline = get_baseline_metrics()
    
    for metric_name, threshold in ROLLBACK_THRESHOLDS.items():
        if metrics[metric_name] > baseline[metric_name] * threshold:
            revert_to_control(experiment_id)
            notify_team(experiment_id, metric_name, metrics[metric_name])
            return "ROLLED_BACK"
    
    return "OK"
```

Runs every 5-15 minutes.

**Rollback speed target:**
- Prompt changes: rollback in <1 minute.
- Model changes: rollback in <10 minutes.
- Infrastructure changes: rollback in <30 minutes.

**Rule:** every deployment must have documented rollback triggers and mechanism. Untested rollback capability doesn't count.

---

## Rollout For Prompt Changes (`rollout_for_prompt_changes.py`)

**Prompt-specific rollout patterns.**

**Advantages of prompt rollouts:**
- Fast: no infrastructure changes.
- Instant rollback: registry flip.
- Cheap: no compute changes.

**Standard prompt rollout:**
```
Day 1:  Deploy to 5% (canary)
Day 2:  Metrics review; if OK, expand to 25%
Day 3:  If OK, expand to 50%
Day 4-5: If OK, expand to 100%
Day 6:  Retire old prompt version after buffer period
```

**Prompt version management:**
- Multiple versions coexist in the registry.
- Feature flag selects which is active per user.
- Old versions remain accessible for rollback.

**Retirement:**
- Old versions marked deprecated after N days.
- Physically retired after longer buffer (30-90 days).
- Full audit trail preserved indefinitely.

**Related concern: prompt caching.**
- LLM providers cache prompt prefixes (Anthropic, OpenAI).
- Changing prompt invalidates cache.
- Consider cache-friendliness in prompt design.

**Rollout in RAG systems:**
- Prompt changes affect retrieval processing.
- May require reindexing (chunk template changes).
- Coordinate rollout with data pipeline.

---

## Rollout For Model Changes (`rollout_for_model_changes.py`)

**Slower, riskier.**

**Why harder than prompt:**
- May require infrastructure changes (different serving stack).
- Rollback requires model reload (minutes to hours).
- Cost differences may be large.
- Behavioral changes are harder to predict.

**Standard model rollout:**
```
Week 1: Shadow test (0% user traffic, log outputs)
Week 2: 5% traffic (canary)
Week 3: 25% traffic
Week 4: 50% traffic (A/B test proper)
Week 5: 100% traffic (if winner)
```

**Model dual-serving:**
- Old and new model both running.
- Users routed based on feature flag.
- Enables instant rollback (route change).

**Cost considerations:**
- Dual-serving is 2× cost during transition.
- Budget for the transition period.

**Data considerations:**
- Different models may have different tokenizers.
- Different context limits.
- Verify all inputs compatible with new model.

**Model version pinning:**
- Pin to specific API version (e.g., `gpt-4o-2024-08-06`).
- Don't use "latest" — silent updates cause drift.
- Test with pinned version; deploy with pinned version.

**When to skip A/B (rare):**
- Provider deprecated the old model (forced migration).
- Security patch required immediately.
- Even then, do shadow testing.

---

## Canary Analysis For LLMs (`canary_analysis_for_llms.py`)

**Automated pass/fail on canaries.**

**Concept:**
- Deploy to small % (canary).
- Automated analysis compares canary to baseline.
- Pass/fail decision without human intervention.

**Analysis dimensions:**

**Statistical significance:**
- Is the canary metric different from baseline?
- Both directions checked.

**Directional health:**
- Metrics moving in expected direction.
- No unexpected regressions.

**Distribution check:**
- Similar shape of output distribution.
- No new failure modes.

**Anomaly detection:**
- Unusual patterns in logs.
- New error types.

**Practical implementation:**
- Run analysis every N minutes.
- Metrics: p95 latency, error rate, quality score, cost.
- Rules:
  - If any critical metric fails → auto-rollback.
  - If any warning metric fails → notify + pause promotion.
  - If all pass for K consecutive hours → auto-promote to next stage.

**Tools:**
- Kayenta (Netflix / Google) — general canary analysis.
- Custom LLM-specific tooling common.

**Rule:** canaries reduce risk substantially. Every non-trivial deployment should be canaried.

---

## Post-Launch Monitoring (`post_launch_monitoring.py`)

**Ties to Episode 11's observability.**

**After the rollout is at 100%:**

**Continuous metric monitoring:**
- Same guardrail metrics as during rollout.
- Alerts on regression.
- Trending vs baseline.

**Long-term effects:**
- Effects that took weeks to appear.
- Holdout comparison (if set up).
- Retention and engagement metrics.

**Cost tracking:**
- Actual cost per query.
- Compare to projection.
- Optimization opportunities.

**Feedback loops:**
- User complaints/thumbs-down.
- Support ticket analysis.
- Content moderation flags.

**Regular review cadence:**
- Daily: automated dashboards.
- Weekly: team review of metrics.
- Monthly: leadership review.
- Quarterly: full performance review.

**When to intervene:**
- Guardrail regression → immediate rollback consideration.
- Slow drift → investigation without immediate action.
- Emerging user segments unhappy → segment-specific fix.

**Retention of experimentation infrastructure:**
- Keep feature flag in place for months after launch.
- Enables rollback if regression detected.
- Enables holdout studies.

**Rule:** launch is not the end. Post-launch monitoring is when you learn what really happened.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `gradual_rollout_patterns.py` | 1% → 10% → 50% → 100% |
| `ring_deployment.py` | Internal → beta → GA |
| `automated_rollback_triggers.py` | Guardrail-based |
| `rollout_for_prompt_changes.py` | Fastest to rollback |
| `rollout_for_model_changes.py` | Slower, riskier |
| `canary_analysis_for_llms.py` | Automated pass/fail |
| `post_launch_monitoring.py` | Ties to Episode 11 |

---

*Previous: [← Analyzing Experiments](../analyzing_experiments/README.md) · Next: [Causal Inference For AI →](../causal_inference_for_ai/README.md)*  ·  *Back to [main README](../../README.md)*
