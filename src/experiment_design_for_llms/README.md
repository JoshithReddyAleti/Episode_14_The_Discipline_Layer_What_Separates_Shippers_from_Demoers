# 🎨 Experiment Design For LLMs

> *A well-designed experiment yields a clean signal. A poorly-designed one wastes months and produces ambiguity. Design is the highest-leverage part of the process.*

---

## Choosing Your Metric (`choosing_your_metric.py`)

**The metric decision drives everything downstream.**

**Selection criteria:**

**1. Directly tied to business value.**
- Not a proxy for a proxy.
- Not a metric that's easy to move but doesn't matter.

**2. Sensitive.**
- Moves detectably from realistic changes.
- Not floored or ceilinged.

**3. Low variance (relative to signal).**
- Higher signal-to-noise = smaller samples needed.
- User-level > session-level > query-level typically.

**4. Fast-moving.**
- Detectable within weeks, not months.
- Not blocked by long conversion cycles.

**5. Interpretable.**
- Stakeholders understand it.
- Directional interpretation is clear.

**Common metric options for LLM features:**

**Task success metrics:**
- Task completion rate.
- User acceptance of the LLM's output.
- Time to task completion.

**Quality metrics:**
- LLM-judge score.
- Human-rated quality (sampled).
- User rating (thumbs up/down).

**Engagement metrics:**
- Follow-up query rate (higher = confusion or interest?).
- Session length.
- Return rate.

**Business metrics:**
- Conversion (purchase, subscription).
- Retention.
- Revenue per user.

**Cost metrics:**
- Tokens per query.
- Cost per successful task.

**Metric-picking traps:**
- **Vanity metrics:** "engagement went up" — but is that good?
- **Gameable metrics:** LLM-judge score if judge has known biases.
- **Delayed metrics:** retention, LTV — too slow for iteration.

**Rule:** the metric is not decoration. Half your experiment quality is determined by metric choice.

---

## Randomization Units (`randomization_units.py`)

**"Who or what is assigned to variants?"**

**Options:**

**Per-request randomization.**
- Each query independently assigned.
- Maximum statistical power (largest sample size).
- **Problem:** same user gets different treatments across queries. Confusing UX. Contaminates learning about user-level effects.

**Per-session randomization.**
- User gets same treatment for the session.
- Balanced compromise.
- Works when sessions are well-defined.

**Per-user randomization.**
- User gets same treatment across all interactions.
- Clean UX, clean user-level metrics.
- Smaller effective sample size (fewer independent units).

**Per-cohort randomization.**
- Whole cohorts (dept, org, geo) get same treatment.
- Necessary when contamination is high (users talk to each other).
- Small sample size; large variance.

**Choosing:**

| Situation | Randomization |
|---|---|
| Stateless API, per-query metric | Per-request |
| Chat product, session-based | Per-session |
| Long-term user product | Per-user |
| Enterprise B2B, org-level rollout | Per-cohort |

**The unit determines what you can measure:**
- Per-request: instantaneous quality diff, but no user-level effect.
- Per-user: user-level effects (retention, satisfaction over time).
- Per-cohort: organizational effects.

**Consistency:**
- Same user should get same treatment across requests within the randomization unit.
- Use deterministic hash (user_id + experiment_id) → variant.

---

## Stratified Sampling (`stratified_sampling.py`)

**Ensuring balance across important segments.**

**Problem:**
- Random assignment can produce imbalance in small samples.
- Even in large samples, rare segments may be underrepresented.
- Analysis conclusions may not generalize.

**Solution: stratification.**
- Identify important segments (user type, region, tenure).
- Randomize within each stratum.
- Guarantees proportional representation.

**Example:**
- Users: 70% free, 25% paid, 5% enterprise.
- Simple random: 50-50 split may give paid users 45% treatment, 55% control by chance.
- Stratified: split each tier 50-50, then combine.

**When stratification matters:**
- Small overall sample size.
- Heterogeneous user base with different behaviors per segment.
- Interested in segment-specific effects.

**Stratum selection:**
- Variables strongly related to metric.
- Variables of interest for segmentation analysis.
- Not too many (each stratum needs enough sample).

**Analysis with stratification:**
- Estimate effect within each stratum.
- Combine via weighted average.
- CIs computed considering strata.

**Trade-off:** stratification adds complexity for often-modest gains. Worth it for heterogeneous populations or small samples.

---

## Traffic Allocation (`traffic_allocation.py`)

**"How much traffic goes to each variant?"**

**Options:**

**50/50 (standard):**
- Maximum statistical power.
- Standard for testing improvements.
- Use when both variants are considered safe.

**90/10, 95/5 (protective):**
- Small treatment allocation.
- Risk-averse; used when treatment is unproven or high-risk.
- Requires much larger total sample size to detect effects.

**Ramp allocation:**
- Start small (1-5% treatment).
- Increase over time (10%, 25%, 50%) if metrics look good.
- Standard for risky changes.

**Multi-variant (A/B/C/D):**
- Multiple treatments simultaneously.
- Each vs control.
- Effective sample per comparison is smaller.

**Considerations:**

**Novelty effects:**
- Early adopters may respond differently.
- Ramp allocations mix novel + non-novel users.

**Traffic budget:**
- Only so much traffic is available.
- Multiple simultaneous experiments compete.

**Risk tolerance:**
- New feature: start small.
- Iteration on a known-good feature: 50/50.

**Practical ramp schedule (typical):**
```
Day 1-2:   1% treatment
Day 3-5:   5% treatment
Day 6-8:   10% treatment
Day 9-14:  50% treatment (unless guardrails triggered)
```

Total experiment duration: 2-4 weeks typical for LLM A/B.

---

## Holdout Design (`holdout_design.py`)

**Measuring long-term effects.**

**Standard A/B:**
- All users split control/treatment during test.
- After test, everyone gets the winner.
- **Limitation:** can't measure long-term effects.

**Holdout design:**
- After the test, keep a small group (5-10%) permanently on control.
- Long-term difference between treatment (majority) and holdout (control) shows long-term effect.

**Uses:**
- **Learning effects.** Users adapt to new interaction style over months.
- **Trust building.** Better bot experience → more use over time.
- **Cross-feature interactions.** Feature A better only in combination with feature B.

**Duration:**
- Standard holdout: 3-6 months post-launch.
- Long-term learnings: 1-2 years.

**Considerations:**
- Fairness: some users get worse (or better) experience longer.
- Business impact: forgone revenue on holdout group.
- Statistical: holdout is small, so smaller effect sizes are needed.

**Ethical:**
- Should not disadvantage users significantly.
- Disclose in TOS if relevant.
- Rotate users through holdout when possible.

**Rule:** for high-stakes LLM changes with expected long-term effects, holdout design is worth the ongoing cost.

---

## Interference and Spillover (`interference_and_spillover.py`)

**When users affect each other.**

**Standard A/B assumes SUTVA** (Stable Unit Treatment Value Assumption):
- Each unit's outcome depends only on its own treatment.
- No interference between units.

**LLM systems often violate SUTVA:**

**1. Shared context.**
- Agents that share memory across users.
- Treatment user's actions modify shared state.
- Control user's next query is affected.

**2. Multi-tenant systems.**
- One user's expensive query slows down others.
- Latency-based metrics contaminated.

**3. Social effects.**
- Users share LLM outputs with each other.
- Treatment users advocate for the new version.
- Word-of-mouth affects control users.

**4. Marketplace / matching.**
- Users are matched (e.g., support tickets to agents).
- Treatment affects the pool of available matches.

**Detection:**
- Compare control users' metrics before vs during experiment.
- If control metric drifts → possible spillover.
- Check for shared-resource contention.

**Mitigation:**

**1. Cluster randomization.**
- Randomize whole clusters (orgs, geos, time periods).
- Interference within cluster, not between.

**2. Time-based switching.**
- Alternate control/treatment days.
- Assumes no drift over short time scales.

**3. Isolated infrastructure.**
- Separate serving stacks per variant.
- Eliminates shared-resource interference.

**4. Two-sided design (for marketplaces).**
- Randomize on both sides of the marketplace.
- Complex; specialized techniques.

**Rule:** think about interference before designing the experiment. Detecting it after the fact is much harder than preventing it.

---

## Experiment Documentation (`experiment_documentation.py`)

**Pre-registration and after.**

**Pre-registration (before running):**
- Hypothesis.
- Metrics (primary, secondary, guardrails).
- Sample size and duration.
- Analysis plan (test, significance level, multiple testing correction).
- Decision criteria (ship if X, kill if Y, iterate if Z).
- Segment analyses planned.

**Why pre-register:**
- Prevents p-hacking (looking at data, then choosing test).
- Forces upfront rigor.
- Enables honest reporting.

**Ongoing documentation (during):**
- Traffic ramp changes.
- Guardrail triggers.
- Anomalies noticed.

**Post-experiment documentation (after):**
- Results (all metrics, not just favorable ones).
- Deviations from plan.
- Decision made and rationale.
- Learnings for future experiments.

**Standard experiment doc template:**
```markdown
# Experiment: [Name]
**Owner:** [name]
**Status:** [planning / running / complete]
**Dates:** [start] - [end]

## Hypothesis
[Statement of what we expect]

## Success criteria
- Primary: [metric] moves by ≥ [MDE] with p < 0.05.
- No guardrail regression > [threshold].

## Design
- Randomization: [per-user / per-session / per-request]
- Allocation: [50/50, 90/10 ramp, etc.]
- Sample size: [X] users, [Y] days.
- Power: [80%] at MDE [X].

## Metrics
- Primary: [metric name and definition]
- Secondary: [list]
- Guardrails: [list with thresholds]

## Analysis plan
- Statistical test: [t-test / z-test / bootstrap]
- Multiple testing: [none / Bonferroni / FDR]
- Segmentation: [pre-planned segments]

## Results
[Filled in after]

## Decision
[Ship / kill / iterate + rationale]

## Learnings
[Filled in after]
```

**Rule:** every A/B test has a pre-reg doc. Everyone can see it. Changes to the plan are documented as amendments, not silently made.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `choosing_your_metric.py` | Primary, secondary, guardrail |
| `randomization_units.py` | User, session, request |
| `stratified_sampling.py` | For fairness and balance |
| `traffic_allocation.py` | 50/50, 90/10, ramp |
| `holdout_design.py` | For long-term effects |
| `interference_and_spillover.py` | LLMs can interact |
| `experiment_documentation.py` | Pre-registration |

---

*Previous: [← Statistical Foundations](../statistical_foundations/README.md) · Next: [Running Experiments →](../running_experiments/README.md)*  ·  *Back to [main README](../../README.md)*
