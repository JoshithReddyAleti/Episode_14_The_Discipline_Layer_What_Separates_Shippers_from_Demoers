# 📈 Analyzing Experiments — Making Sense Of Results

> *The experiment ran. Numbers are in. This is where most teams make bad decisions. This section is how to actually read A/B results.*

---

## Analyzing LLM Experiment Data (`analyzing_llm_experiment_data.py`)

**The core analysis workflow:**

**1. Sanity checks first.**
- **Sample Ratio Mismatch (SRM):** did users end up in the assigned proportions?
  - Expected: 50/50. Observed: 48.2/51.8. χ² test on the split.
  - Significant SRM → assignment bug. **Don't analyze results until fixed.**
- **Data completeness:** all logged events present?
- **Metric sanity:** are metrics in expected ranges?
- **Overlap with other experiments:** were users in other simultaneous experiments? Confounding possible?

**2. Primary metric analysis.**
- Effect size + confidence interval + p-value.
- Compare to pre-registered decision criteria.
- Ship / kill / iterate.

**3. Secondary metrics.**
- Consistent with primary?
- Any counterintuitive movements?
- Apply multiple-testing correction.

**4. Guardrail checks.**
- No regressions on latency, cost, error rate, safety metrics?
- Blocking gates for shipping.

**5. Segmentation.**
- Consistent effect across user segments?
- Heterogeneity may reveal important interactions.

**6. Diagnostic analysis.**
- Distribution of outcomes (histogram).
- Heavy tails, bimodality.
- Outliers driving the effect?

**Analysis code pattern:**
```python
import scipy.stats as stats
import numpy as np

def analyze_ab(control_values, treatment_values, alpha=0.05):
    n_c, n_t = len(control_values), len(treatment_values)
    mean_c, mean_t = np.mean(control_values), np.mean(treatment_values)
    var_c, var_t = np.var(control_values, ddof=1), np.var(treatment_values, ddof=1)
    
    # Welch's t-test (unequal variances)
    se = np.sqrt(var_c/n_c + var_t/n_t)
    t_stat = (mean_t - mean_c) / se
    df = (var_c/n_c + var_t/n_t)**2 / ((var_c/n_c)**2/(n_c-1) + (var_t/n_t)**2/(n_t-1))
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))
    
    # 95% CI on difference
    t_crit = stats.t.ppf(1 - alpha/2, df)
    ci_low = (mean_t - mean_c) - t_crit * se
    ci_high = (mean_t - mean_c) + t_crit * se
    
    return {
        "effect": mean_t - mean_c,
        "effect_pct": (mean_t - mean_c) / mean_c,
        "ci_95": (ci_low, ci_high),
        "p_value": p_value,
        "significant": p_value < alpha,
        "n_control": n_c,
        "n_treatment": n_t,
    }
```

**Reporting format:**
```
Primary metric: task_success_rate
Control: 72.3% (n=8104)
Treatment: 74.8% (n=8091)
Effect: +2.5 pp (95% CI: +1.4 to +3.6 pp)
Relative effect: +3.5%
p-value: 0.0002 (significant at α=0.05)
```

---

## Handling Variance In LLM Outputs (`handling_variance_in_llm_outputs.py`)

**LLM outputs are noisy. Analysis must account for this.**

**Sources of variance:**
1. **Sampling stochasticity.** Model output varies at temperature > 0.
2. **Judge stochasticity.** LLM-judge score varies.
3. **User variance.** Different users respond differently.
4. **Query variance.** Different queries have different quality.

**Techniques to handle variance:**

**1. Larger samples.**
- Straightforward but expensive.
- Use only when other techniques don't help.

**2. Variance reduction (CUPED).**
- 20-50% variance reduction on user-level metrics.
- (Discussed in statistical_foundations.)

**3. Repeat sampling.**
- For each query, sample the LLM output N times.
- Use average or median.
- Reduces sampling variance by √N.
- Trade-off: N× cost per query.

**4. Multi-judge.**
- Average LLM-judge scores across 3-5 judges.
- Reduces judge variance.
- Also more robust.

**5. Aggregation.**
- User-level > query-level metrics.
- Fewer independent units but less variance per unit.

**6. Robust statistics.**
- Median instead of mean for heavy-tailed metrics.
- Trimmed means (drop top and bottom 5%).
- Bootstrap CIs (don't assume normality).

**7. Rank-based tests.**
- Mann-Whitney U instead of t-test.
- More robust to outliers.

**Bootstrap CI for LLM metrics:**
```python
def bootstrap_ci(control, treatment, n_boot=10000, ci=0.95):
    diffs = []
    for _ in range(n_boot):
        c_sample = np.random.choice(control, size=len(control), replace=True)
        t_sample = np.random.choice(treatment, size=len(treatment), replace=True)
        diffs.append(np.mean(t_sample) - np.mean(c_sample))
    lower = np.percentile(diffs, (1 - ci) / 2 * 100)
    upper = np.percentile(diffs, (1 + ci) / 2 * 100)
    return lower, upper
```

---

## Segmentation Analysis (`segmentation_analysis.py`)

**"Who benefited? Who didn't?"**

**Standard segments to analyze:**
- User tenure (new vs existing).
- User tier (free vs paid vs enterprise).
- Geographic region.
- Device / platform.
- Query type or complexity.
- Language.
- Time of day / day of week.

**Analysis pattern:**
- Compute the effect within each segment.
- Compute confidence intervals per segment (wider than overall).
- Compare across segments — is the effect consistent?

**Heterogeneity of treatment effect (HTE):**
- Effect varies by segment.
- Common findings:
  - New users benefit more from tutorial-style prompts.
  - Enterprise users tolerate longer responses.
  - Non-English speakers benefit more from certain patterns.

**Statistical caveats:**
- **Multiple testing:** many segments → some will look significant by chance.
- **Correction:** FDR (Benjamini-Hochberg) across segment tests.
- **Pre-register** segment analyses; post-hoc segments are exploratory.

**Segment size threshold:**
- Segments with < 50 samples: don't report; too noisy.
- Segments with 50-500 samples: report with wide CIs; take with grain of salt.
- Segments with 500+ samples: robust estimates.

**Actionable output:**
- Ship if positive on all major segments.
- Investigate if some segments negative.
- Consider segment-specific deploys if HTE is significant.

**Anti-pattern:**
- P-hacking through segments (test 20 segments, one is significant, claim victory).
- Not documenting which segments were pre-planned.

---

## Novelty And Primacy Effects (`novelty_and_primacy_effects.py`)

**Time-based bias.**

**Novelty effect:**
- Users respond to newness itself, not the change quality.
- Positive at first, fades over time.

**Primacy effect:**
- Users prefer what they saw first.
- Existing users may resist change; new users adapt easily.

**Detection:**
- Plot effect over time (week 1, week 2, week 3).
- Trend up → novelty effect (short-lived positive).
- Trend down after initial dip → primacy (users learning new pattern).

**Mitigation:**
- **Longer experiments.** Effects stabilize after 2-4 weeks typically.
- **New-user segmentation.** Analyze new vs existing users separately.
- **Holdout groups.** Long-term measurement.

**Effect fadeout:**
- Novelty typically fades in 2-6 weeks.
- If effect fades to zero → the change wasn't real, users just liked "new".
- If effect stabilizes → real effect.

**Warning signs:**
- Large positive effect in week 1, near-zero by week 3.
- Different effects on new vs returning users.
- Effect decays with user tenure in the experiment.

**Reporting:**
- Report effect at multiple time points.
- Trend analysis.
- Explicit statement of novelty/primacy consideration.

**Rule:** don't ship on week-1 numbers. Especially for major changes, wait for effect to stabilize.

---

## Bayesian vs Frequentist (`bayesian_vs_frequentist.py`)

**The debate.**

**Frequentist (traditional):**
- p-values, confidence intervals.
- Ship if p < α.
- Prescribes single decision rule.

**Bayesian:**
- Posterior probability of effect.
- Ship if P(effect > 0) > 95%.
- Incorporates prior beliefs.

**Bayesian advantages:**
- **Interpretable.** "95% probability treatment is better" vs "p-value 0.05."
- **Sequential analysis** without inflating error rates.
- **Combines prior knowledge** with data.
- **Effect size distribution** rather than binary significant/not.

**Bayesian disadvantages:**
- Requires choosing a prior (subjective).
- Computationally more expensive.
- Less familiar to most teams.

**Practical implementation:**

**Beta-Binomial for proportions:**
- Prior: Beta(α, β) — uniform prior is Beta(1, 1).
- Data: control (s_c successes, f_c failures), treatment (s_t, f_t).
- Posterior: Beta(1+s, 1+f) for each arm.
- Sample from posteriors; compute P(treatment > control).

**Example:**
```python
import numpy as np

def bayesian_ab_proportion(s_c, f_c, s_t, f_t, n_samples=100000):
    # Posterior samples
    samples_c = np.random.beta(1 + s_c, 1 + f_c, n_samples)
    samples_t = np.random.beta(1 + s_t, 1 + f_t, n_samples)
    
    prob_t_better = np.mean(samples_t > samples_c)
    expected_uplift = np.mean(samples_t - samples_c)
    ci_low, ci_high = np.percentile(samples_t - samples_c, [2.5, 97.5])
    
    return {
        "P(treatment > control)": prob_t_better,
        "expected_uplift": expected_uplift,
        "95%_credible_interval": (ci_low, ci_high),
    }
```

**When to use Bayesian:**
- Sequential testing / early stopping.
- Prior knowledge is strong and relevant.
- Communicating with non-statisticians.

**When to stick with frequentist:**
- Standard operating procedure.
- Regulatory requirements.
- Prior selection is contentious.

**Rule:** either works. Consistency matters more than choice. Pick one and standardize across the org.

---

## Confidence Intervals Done Right (`confidence_intervals_done_right.py`)

**Beyond point estimates.**

**What a CI means:**
- 95% CI is not "there's a 95% chance the true value is in this range."
- It's: "if we repeated the experiment many times, 95% of the CIs would contain the true value."
- Practical interpretation is close enough for most purposes.

**Reporting:**
- Always report CIs, not just point estimates.
- Point estimate without CI is useless.

**Standard CI types:**

**Wald CI (default for proportions):**
```
p̂ ± z_{α/2} × √(p̂(1-p̂)/n)
```
- Symmetric.
- Fine for large n and p not near 0 or 1.

**Wilson CI (better for proportions):**
- Asymmetric.
- Better coverage for small n or extreme p.
- Preferred in modern practice.

**T-based CI (for means):**
```
x̄ ± t_{α/2, df} × SE
```

**Bootstrap CI (for anything):**
- Non-parametric.
- Handles complex metrics.

**Common mistakes:**
- Reporting SE only (users need CI).
- Symmetric CI on asymmetric distributions.
- Ignoring correlation in repeated measures.

**Interpretation guide:**
- CI includes zero → not significant (at α = 1-CI_level).
- CI entirely positive → treatment better.
- CI entirely negative → control better.
- CI narrow → precise estimate.
- CI wide → imprecise; more data would help.

**Rule:** never ship a decision based on p-value alone. Always look at effect size and CI.

---

## Writing Experiment Reports (`writing_experiment_reports.py`)

**Communicating findings.**

**Audience-tailored reports:**

**Executive summary (1 paragraph):**
- Experiment goal.
- Result (ship / kill / iterate).
- Impact estimate.
- Key caveats.

**Technical report (1-3 pages):**
- Full metrics with CIs.
- Segmentation.
- Diagnostic plots.
- Decision rationale.
- Learnings.

**Full documentation (registered doc + amendments + analysis):**
- Complete audit trail.
- Referenced by other reports.

**Standard report structure:**

```markdown
# Experiment: [Name]

## TL;DR
[1-2 sentences: what did we learn, what did we ship]

## Background
[Why we ran this experiment]

## Design
[Hypothesis, metrics, allocation, duration]

## Results

### Primary metric
[Effect size + CI + p-value]

### Secondary metrics
[Table]

### Guardrails
[Pass/fail status]

### Segmentation
[Any notable heterogeneity]

## Diagnostic
[Sanity checks, SRM, distribution]

## Decision
[Ship / kill / iterate + rationale]

## Impact
[Business impact estimate]

## Learnings
[What we learned, applicable to future experiments]

## Follow-ups
[Any next steps]
```

**Best practices:**
- **Report all metrics, not just favorable ones.**
- **Report all pre-registered analyses.**
- **Flag deviations from pre-registration.**
- **Include diagnostic plots (histograms, time trends).**
- **Store in searchable system** (learnings library).

**Anti-patterns:**
- Only reporting the positive findings.
- Not disclosing multiple testing.
- Cherry-picking segments.

**Rule:** if your experiment reports could be published for peer review, they're good enough. If not, they're not.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `analyzing_llm_experiment_data.py` | Full workflow with code |
| `handling_variance_in_llm_outputs.py` | Variance-specific techniques |
| `segmentation_analysis.py` | Who benefited |
| `novelty_and_primacy_effects.py` | Time-based bias |
| `bayesian_vs_frequentist.py` | The debate + practical Bayesian |
| `confidence_intervals_done_right.py` | Beyond point estimates |
| `writing_experiment_reports.py` | Communicating findings |

---

*Previous: [← Running Experiments](../running_experiments/README.md) · Next: [Rollout Strategies →](../rollout_strategies/README.md)*  ·  *Back to [main README](../../README.md)*
