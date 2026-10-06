# 📊 A/B Testing Foundations — Why LLM Experimentation Is Different

> *A/B testing web features is a solved problem. A/B testing LLM features is not — stochastic outputs, subjective quality, tiny effects, and drift make it harder than most teams realize.*

---

## Why A/B Testing LLMs Is Harder (`why_ab_testing_llms_is_harder.py`)

**Traditional web A/B:**
- Deterministic feature (button color, checkout flow).
- Discrete outcome (converted / didn't).
- Independent user sessions.
- Static feature during test.
- Sample sizes tractable.

**LLM A/B:**
- **Stochastic output.** Same input → different outputs at temperature > 0.
- **Subjective quality.** No single "correct" answer for many tasks.
- **Small effects.** Prompt changes shift metrics 1-3%. Large sample sizes needed.
- **High variance.** Output quality varies per query due to model sampling.
- **Drift.** Base model changes silently (provider updates).
- **Interference.** Users may interact (agents talking to each other, shared context).
- **Cost per sample.** Every impression costs $0.001-0.01 in inference.

**Specific challenges:**

**1. Metric selection.**
- Traditional: revenue, retention, engagement.
- LLM: quality score (subjective), task success, user satisfaction, cost, latency.

**2. Variance from stochasticity.**
- LLM output variance is often larger than the effect size you're trying to detect.
- Need much larger samples or variance reduction techniques.

**3. Long-term effects.**
- Users adapting to a new interaction style (novelty).
- Trust building over time.
- Cannot measure in a short A/B window.

**4. Judge fidelity.**
- Automated metrics (LLM-judge) have their own noise.
- Human evaluation is expensive.
- Choice of judge affects results.

**5. Interaction effects.**
- Prompt change interacts with model version.
- Model change interacts with data.
- Multi-variable design needed for causal understanding.

**Rule:** LLM A/B testing requires larger samples, more careful metric design, and awareness of drift. The playbook from web A/B doesn't fully translate.

---

## The Experimentation Lifecycle (`the_experimentation_lifecycle.py`)

**End-to-end lifecycle for LLM experiments:**

```
1. Hypothesis formulation
   - "Adding chain-of-thought will improve accuracy by 3%+."
   - Specific, testable, tied to business metric.

2. Metric definition
   - Primary: task accuracy.
   - Secondary: latency, cost.
   - Guardrails: hallucination rate, user complaints.

3. Power calculation
   - Given expected effect size and variance:
   - What sample size do we need for 80% power at α=0.05?

4. Design
   - Randomization unit (user / session / request).
   - Traffic allocation.
   - Duration bounds.

5. Implementation
   - Feature flag / prompt registry.
   - Instrumentation for metrics.
   - Sanity checks.

6. Pre-registration
   - Document design, hypotheses, analysis plan.
   - Freeze before running.

7. Running
   - Ramp up traffic to allocation.
   - Monitor guardrails.
   - Sanity checks (SRM, imbalance).

8. Analysis
   - Primary metric result.
   - Secondary metrics.
   - Segmentation.
   - Confidence intervals.

9. Decision
   - Ship / kill / iterate based on pre-registered criteria.

10. Rollout
    - Gradual deploy of winner.
    - Monitor in production.

11. Learning capture
    - Write up findings.
    - Add to institutional learnings library.
```

**Timing per stage:**
- Hypothesis to design: 1-2 weeks.
- Implementation: 1-2 weeks.
- Running: 1-4 weeks (depending on traffic).
- Analysis + decision: 1 week.
- **Total per experiment: 4-9 weeks.**

**Common failure modes:**
- Skipping power calc → underpowered experiments, false negatives.
- Skipping pre-registration → analyst degrees of freedom, p-hacking.
- Continuous monitoring with early stopping → inflated false positive rate.
- No guardrails → shipping regressions.

---

## A/B Testing vs Offline Eval (`ab_testing_vs_offline_eval.py`)

**Two complementary tools.**

**Offline eval:**
- Curated test set.
- Model / prompt scored against known correct answers.
- Fast, cheap, deterministic (mostly).
- Metrics: accuracy, F1, LLM-judge score.

**A/B test:**
- Real users, real traffic.
- Real metrics tied to business.
- Slower, more expensive, statistical uncertainty.
- Metrics: user satisfaction, task completion, revenue.

**Relationship:**
- **Offline eval:** filter candidates. Reject changes that regress offline before A/B.
- **A/B test:** validate candidates. Final judgment on real users.

**When offline eval is enough:**
- Sub-metric optimizations (e.g., format compliance).
- Changes with clearly measurable impact on eval set.
- Early iterations of a feature.

**When A/B test is required:**
- User-facing changes.
- Subjective quality where offline metrics don't capture UX.
- Changes with unclear directional impact on user behavior.
- Regulatory or contractual proof-of-improvement requirements.

**Alignment between offline and online:**
- Track correlation between offline eval score and A/B results.
- If poorly correlated: offline eval isn't measuring what matters.
- Iteratively improve offline eval based on A/B findings.

**Typical pattern:**
```
Prompt change proposed
    ↓
Offline eval on golden set → pass?
    ↓ (if pass)
Small-scale A/B (5-10% traffic)
    ↓
Full A/B (50-50 for 2-4 weeks)
    ↓
Rollout if winner
```

**Rule:** offline eval is your filter; A/B is your judge. Both matter. Neither alone is enough.

---

## Metrics That Matter (`metrics_that_matter.py`)

**Choosing what to measure for LLM A/B tests.**

**Layered metric framework:**

**1. Primary metric (one).**
- The metric that drives ship/kill decision.
- Should be tightly tied to product/business value.
- Examples:
  - Task success rate (bookings completed, queries answered).
  - User satisfaction rating.
  - Downstream conversion.

**2. Secondary metrics (2-5).**
- Metrics that inform interpretation.
- Examples:
  - Response quality (LLM-judge score).
  - Response length.
  - Time to resolution.
  - Follow-up query rate (proxy for confusion).

**3. Guardrails (3-10).**
- Metrics that shouldn't regress.
- Trigger auto-rollback if breached.
- Examples:
  - Latency (P95).
  - Cost per query.
  - Error rate.
  - Content moderation flag rate.
  - Hallucination rate (sampled).

**4. Operational metrics.**
- Not for decision but for debugging.
- Tokens per query.
- Cache hit rate.
- Tool call frequency.

**Business vs quality metrics:**

**Business metrics** (revenue, conversion): what you ultimately care about, often noisy, need large samples.

**Quality metrics** (LLM-judge score, satisfaction): less noisy, faster to move, but risk optimizing the proxy.

**Rule:** primary metric should be business-relevant. Quality metrics as secondaries + guardrails.

**Composite metrics** (weighted sums of multiple metrics) are risky:
- Different components weighted arbitrarily.
- Hard to interpret changes.
- Sometimes necessary but should be pre-agreed.

**Metric hierarchy example (customer support bot):**
- **Primary:** ticket resolution rate.
- **Secondary:** average handle time, escalation rate, LLM-judge quality score.
- **Guardrails:** latency P95 < 3s, cost per ticket < $0.10, complaint rate < 1%, hallucination rate < 2% (sampled).

---

## Organizational Experimentation Maturity (`organizational_experimentation_maturity.py`)

**Where teams sit on the ladder.**

**Level 0: No experimentation.**
- Changes ship without measurement.
- Bugs found by users.
- "It seems better" as decision criterion.

**Level 1: Ad-hoc A/B.**
- Occasional experiments on high-stakes changes.
- No standardized framework.
- Analysis in spreadsheets.

**Level 2: Feature-flag driven.**
- Feature flags for all changes.
- Simple % rollouts.
- Metrics logged.
- Some experimenters run analyses.

**Level 3: Experimentation platform.**
- Dedicated platform (Statsig, Split, LaunchDarkly + analytics).
- Standardized experiment templates.
- Automated analysis.
- Power calcs.
- Dashboards.

**Level 4: Culture of experimentation.**
- Every change is A/B tested unless justified.
- Institutional learning library.
- Cross-functional experiment reviews.
- Statistical literacy across team.

**Level 5: Cutting-edge.**
- Bandit algorithms for adaptive traffic allocation.
- Multi-arm experiments as default.
- Bayesian methods deployed.
- Causal inference for post-hoc analysis.
- Metric store with governance.

**In 2026:**
- Most companies at Level 1-2.
- Best AI-native companies at Level 3-4.
- Frontier labs approaching Level 5.

**Rule:** you don't need Level 5 to start. You need Level 2 minimum to have any hope of shipping better AI features than random. Move up the ladder deliberately.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `why_ab_testing_llms_is_harder.py` | Non-determinism, drift, small effects |
| `the_experimentation_lifecycle.py` | End-to-end 11-stage lifecycle |
| `ab_testing_vs_offline_eval.py` | When you need each |
| `metrics_that_matter.py` | Business + quality + cost |
| `organizational_experimentation_maturity.py` | The maturity ladder |

---

*Previous: [← LLM Security Operations](../llm_security_operations/README.md) · Next: [Statistical Foundations →](../statistical_foundations/README.md)*  ·  *Back to [main README](../../README.md)*
