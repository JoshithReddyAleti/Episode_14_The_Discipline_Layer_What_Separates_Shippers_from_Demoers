# A/B Testing LLMs — Playbook

## Why LLM A/B is harder

- Stochastic output (variance from sampling).
- Subjective quality (no single correct answer).
- Small effect sizes (prompt changes shift metrics 1-3%).
- Drift (base model updates silently).
- Interference (agents interact, shared context).
- Cost per sample.

## The 11-stage lifecycle

1. Hypothesis formulation.
2. Metric definition (primary + secondary + guardrails).
3. Power calculation (sample size).
4. Design (randomization unit, allocation, duration).
5. Implementation (feature flag, instrumentation).
6. Pre-registration.
7. Running (with sanity checks).
8. Analysis (SRM, primary, secondary, segmentation).
9. Decision (pre-registered criteria).
10. Rollout (canary → gradual → full).
11. Learning capture (institutional library).

Duration per experiment: 4-9 weeks.

## Common failure modes

- Skipping power calc → underpowered experiments.
- Skipping pre-registration → p-hacking.
- Continuous monitoring with early stopping → inflated α.
- No guardrails → shipping regressions.
- Testing many metrics without correction → false positives.
- Novelty effects reported as real gains → premature ship.

## The four LLM change types

- **Prompt changes** — fastest to rollback; typical duration 1-2 weeks.
- **Model changes** — dual-serving during transition; 2-4 weeks.
- **RAG changes** — end-to-end + retrieval-specific metrics; 2-4 weeks.
- **Agent changes** — hardest; 4-8 weeks; simulator first.

## Metrics framework

- **Primary (1)** — drives ship/kill decision. Business-relevant.
- **Secondary (2-5)** — inform interpretation.
- **Guardrails (3-10)** — trigger rollback if breached (latency, cost, error, safety).
- **Operational** — for debugging (tokens, cache hits, tool calls).

