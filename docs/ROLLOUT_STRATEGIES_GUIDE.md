# Rollout Strategies Guide

## Standard progression

```
Day 1:   1% users
Day 3:   5% users
Day 5:   10% users
Day 8:   25% users
Day 11:  50% users
Day 14:  100% users
```

## Ring deployment (for major changes)

- **Ring 0:** Dogfood (internal team).
- **Ring 1:** Employees (company-wide).
- **Ring 2:** Beta users (opt-in externals).
- **Ring 3:** GA (all users).
- **Ring 4:** Broadcast (marketed).

## Auto-rollback triggers

- Error rate: 3× baseline for 15 min → rollback.
- P95 latency: 2× baseline for 15 min → rollback.
- Cost: 5× baseline for query → alert; auto if sustained.
- Content moderation: 5× baseline flag rate → rollback.
- Primary metric: severe drop (>X%) → rollback.

Runs every 5-15 min.

## Rollback speed targets

- Prompt changes: <1 minute (registry flip).
- Model changes: <10 minutes (dual-serving; route change).
- Infrastructure: <30 minutes.

## Prompt vs model rollout differences

**Prompt:**
- Fast (registry flip).
- Cheap (no infra changes).
- Instant rollback.
- Typical 3-7 day rollout.

**Model:**
- Slower (dual-serving required).
- More expensive during transition.
- Rollback ~10 minutes.
- Typical 2-4 week rollout.

## Post-launch monitoring

- Keep feature flag in place months after launch.
- Enables regression rollback.
- Enables holdout studies for long-term effects.
- Review cadence: daily (dashboards), weekly (team), monthly (leadership).

