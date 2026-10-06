# 📐 Statistical Foundations — The Math

> *If you don't understand power, MDE, and multiple testing correction, your A/B tests are theater. This section is the statistical machinery that makes A/B testing actually work — with real formulas, not hand-waving.*

---

## Hypothesis Testing Refresher (`hypothesis_testing_refresher.py`)

**The formal framework.**

**Null hypothesis (H₀):** the treatment has no effect. E.g., "prompt v2 has the same task success rate as v1."

**Alternative hypothesis (H₁):** the treatment has an effect. E.g., "prompt v2 has different task success rate than v1" (two-sided) or "higher" (one-sided).

**Test statistic:** a number computed from the data that measures how far your observation is from H₀. Common ones:
- **z-statistic** (proportions, large samples): `z = (p̂_T - p̂_C) / SE`
- **t-statistic** (means, small samples): `t = (x̄_T - x̄_C) / SE`
- **χ² statistic** (categorical): `χ² = Σ (observed - expected)² / expected`

**p-value:** probability of observing a test statistic as extreme as yours, *if H₀ is true*.
- Small p (< 0.05) → data is unlikely under H₀ → reject H₀.
- Large p → data is compatible with H₀ → fail to reject.

**Common misconception:** p-value is NOT the probability that H₀ is true. It's the probability of the data given H₀.

**Significance level α:** the threshold below which you reject H₀. Standard: 0.05 (5% false positive rate).

**Practical example:**
- Control (v1): 1000 users, 720 succeeded (72%).
- Treatment (v2): 1000 users, 745 succeeded (74.5%).
- Difference: 2.5 pp.
- Standard error: `SE = √(p̂_C(1-p̂_C)/n_C + p̂_T(1-p̂_T)/n_T) = √(0.72×0.28/1000 + 0.745×0.255/1000) ≈ 0.0200`
- z = 0.025 / 0.0200 ≈ 1.25.
- Two-sided p-value ≈ 0.21.
- p > 0.05 → not significant.

**Interpretation:** we can't distinguish v2's effect from noise at this sample size. Not "v2 is equal to v1."

**Rule:** always state your hypothesis and α before running the test. Post-hoc adjustments inflate false positives.

---

## Type I and Type II Errors (`type_1_and_type_2_errors.py`)

**Two ways to be wrong.**

|  | H₀ true (no effect) | H₁ true (effect) |
|---|---|---|
| **Reject H₀** | **Type I error (α)** — false positive | Correct (power) |
| **Fail to reject** | Correct | **Type II error (β)** — false negative |

**Type I error rate (α):** probability of concluding an effect exists when it doesn't.
- Standard: 0.05.
- Lower α (0.01) reduces false positives but requires more data.

**Type II error rate (β):** probability of missing a real effect.
- Standard target: 0.20 (i.e., 80% power).
- Higher β means you'll ship losers as "no effect."

**Trade-off:**
- Fixed sample size: reducing α increases β and vice versa.
- The way to reduce both: larger sample size or smaller variance.

**Concrete costs of each:**
- **Type I (false positive):** ship a change that doesn't help; wasted engineering; possibly regress users.
- **Type II (false negative):** kill a change that would have helped; missed opportunity.

**In LLM A/B testing specifically:**
- Type I: ship a new prompt that isn't actually better → cost, complexity, possible regression on segments.
- Type II: kill a good prompt idea → slower progress, missed quality gains.

**Rule:** choose α and β based on decision cost. High-stakes decisions warrant lower α. Iteration cycles benefit from higher β tolerance (accept more false negatives to move faster).

---

## Statistical Power (`statistical_power.py`)

**Power = 1 - β.** Probability of detecting a real effect if it exists.

**The four-way relationship:**

```
Power ↑ requires:
  ↑ Sample size (n)
  OR ↑ Effect size (δ)
  OR ↑ α (accept more false positives)
  OR ↓ Variance (σ²)
```

**Formula (two-sample proportion test, approximate):**
```
n = 2 × (z_{α/2} + z_β)² × p̄(1-p̄) / δ²
```

Where:
- `n` = sample size per arm
- `z_{α/2}` = critical z-value for α (e.g., 1.96 for α=0.05 two-sided)
- `z_β` = critical z-value for β (e.g., 0.84 for β=0.20, giving 80% power)
- `p̄` = average proportion
- `δ` = detectable difference (effect size)

**For continuous outcomes (means):**
```
n = 2 × (z_{α/2} + z_β)² × σ² / δ²
```

**Concrete example (LLM A/B):**
- Baseline task success rate: 72%.
- Want to detect a 2 pp improvement (72% → 74%).
- α = 0.05 (two-sided), Power = 80%.
- p̄ ≈ 0.73, δ = 0.02.
- z_{0.025} = 1.96, z_{0.20} = 0.84.
- n = 2 × (1.96 + 0.84)² × 0.73 × 0.27 / 0.02² = 2 × 7.84 × 0.197 / 0.0004 ≈ **7,725 per arm**.
- **Total: ~15,450 users needed.**

**If you only had 1000 per arm and observed 2 pp uplift:**
- p-value would be ~0.21 (as above).
- You'd miss the real effect (Type II error).
- **Not because there's no effect — because you're underpowered.**

**Rule:** **run the power calculation BEFORE the experiment.** Every A/B test should start with "what sample size do we need?" If you can't get that sample size, either reduce ambition (accept larger MDE), extend duration, or don't run the test.

**Underpowered experiments are worse than no experiments:**
- Waste traffic and engineering.
- Ambiguous results lead to bad decisions.
- Establish false negatives that block future exploration.

---

## Power Calculations For LLMs (`power_calculations_for_llms.py`)

**LLM-specific gotchas.**

**Problem 1: variance from stochasticity.**
- LLMs sample from a distribution. Same input → different outputs.
- Variance on a per-query basis is higher than for deterministic features.
- Need to account for this in σ².

**Solution:**
- For continuous metrics (LLM-judge score 0-10), measure variance on your baseline before the experiment.
- Use that variance in the power calc.

**Problem 2: subjective quality metrics.**
- LLM-judge score is noisy (judge itself has variance).
- Human evaluation is noisier (inter-annotator disagreement).
- Effective variance is higher than raw metric suggests.

**Solution:**
- Use multiple judges; average.
- Use CUPED (below) to reduce variance.
- Aggregate at higher levels (session-level, not query-level).

**Problem 3: heavy tails.**
- LLM output quality has heavy tails (a few queries with wildly wrong answers).
- CLT breaks down; simple z-tests can be misleading.

**Solution:**
- Use bootstrap for CIs.
- Winsorize outliers (cap at 99th percentile).
- Focus on medians / percentiles when tails matter.

**Problem 4: multiple related metrics.**
- Prompt change affects accuracy, latency, cost, satisfaction.
- Testing each at α=0.05 → high family-wise error rate.

**Solution:**
- Pre-designate one primary metric.
- Bonferroni or FDR correction for secondaries.
- (See multiple testing section.)

**LLM-specific power calc example:**
- Metric: LLM-judge quality score (0-10 scale).
- Baseline mean: 7.2, SD: 1.8 (measured on golden set).
- Want to detect a 0.2-point improvement.
- α=0.05, power=80%.
- n = 2 × (1.96+0.84)² × 1.8² / 0.2² = 2 × 7.84 × 3.24 / 0.04 = **~1270 per arm**.
- **Total: ~2540 samples**.

Very different sample sizes for different metrics — plan accordingly.

---

## Sample Size Estimation (`sample_size_estimation.py`)

**Practical calculators.**

**Python code (proportion test):**
```python
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

# Baseline 72%, target 74%
p0, p1 = 0.72, 0.74
effect_size = proportion_effectsize(p1, p0)

analysis = NormalIndPower()
n = analysis.solve_power(
    effect_size=effect_size,
    alpha=0.05,
    power=0.80,
    alternative='two-sided',
    ratio=1.0,
)
print(f"Sample per arm: {int(n)}")
# Output: ~7500-7800 (varies by exact effect_size definition)
```

**For continuous outcomes:**
```python
from statsmodels.stats.power import TTestIndPower

# LLM-judge mean 7.2, SD 1.8, detect 0.2 point diff
effect_size_d = 0.2 / 1.8  # Cohen's d

analysis = TTestIndPower()
n = analysis.solve_power(
    effect_size=effect_size_d,
    alpha=0.05,
    power=0.80,
    alternative='two-sided',
)
print(f"Sample per arm: {int(n)}")
```

**Duration estimation:**
```
duration_days = (2 × n_per_arm) / daily_traffic_in_experiment
```

**If duration > 2 weeks:**
- Consider novelty/primacy effects.
- Consider drift.
- Consider whether the change is worth the wait.

**Sequential testing** (advanced):
- Group Sequential Design or always-valid inference.
- Peek at results while controlling false positive rate.
- Complex; use tools like `abtest` or `sequential-testing`.

**Rule:** always compute sample size before the test. Never "let's just run it and see."

---

## Effect Size Estimation (`effect_size_estimation.py`)

**"How big a change should we expect?"**

**Effect size** = expected size of the improvement in absolute or relative terms.

**Sources for estimation:**

**1. Offline eval.**
- Run new prompt/model on golden set.
- Measure difference in offline metric.
- **Discount:** online effect typically 30-70% of offline effect.

**2. Prior experiments.**
- Look at recent A/B results for similar changes.
- Base rate for "prompt change" magnitude.
- Base rate for "model upgrade" magnitude.

**3. Business requirement.**
- Minimum useful improvement.
- Below this, not worth shipping regardless of statistical significance.

**Effect size categories (rules of thumb):**

**Small (Cohen's d = 0.2):**
- Prompt wording tweak.
- Small model version update.
- Requires large samples (thousands).

**Medium (d = 0.5):**
- Significant prompt restructure.
- Meaningful RAG improvement.
- Moderate samples (hundreds to thousands).

**Large (d = 0.8+):**
- Model family upgrade.
- Major feature addition.
- Small samples may suffice (tens to hundreds).

**LLM change effect sizes typically:**
- Prompt wording change: d = 0.05-0.2 (small).
- Prompt structure change (CoT, examples): d = 0.2-0.5.
- Model change (mini → full): d = 0.3-0.8.
- RAG addition/improvement: d = 0.4-1.0+.

**Anti-pattern:** running an experiment powered to detect d = 0.5 on a change that likely has d = 0.1. You'll conclude "no effect" when there is one.

---

## MDE — Minimum Detectable Effect (`mde_minimum_detectable_effect.py`)

**"Given my sample size, what's the smallest effect I could detect?"**

**Inverse of the power calculation.**

**Formula (proportions):**
```
MDE = (z_{α/2} + z_β) × √(2 × p̄(1-p̄) / n)
```

**Example:**
- Fixed sample size: 5000 per arm.
- p̄ = 0.73.
- α=0.05, power=80%.
- MDE = (1.96 + 0.84) × √(2 × 0.73 × 0.27 / 5000) = 2.80 × √0.0000789 ≈ **0.0248 = 2.48 pp**.

Interpretation: with 5000 users per arm, you can reliably detect a 2.5 pp change or larger.

**Practical use:**
- Before running: "we can detect changes ≥ X" — is that useful?
- If MDE > minimum useful effect → not worth running.
- If MDE ≤ minimum useful effect → run the test.

**MDE-driven decisions:**

**Feature that needs 1% MDE to ship:**
- Compute required sample size.
- If sample size unattainable → don't run this test.

**MDE for LLM guardrails:**
- Latency P95 must not regress by more than 100ms.
- Compute sample needed to detect 100ms change.
- Design test around that.

**Anti-pattern:** running underpowered tests that "detect" a real effect only when it's much larger than actual, misleading in both directions.

**MDE curves:**
- Plot MDE as a function of sample size.
- Useful for planning: "we can hit 2 pp MDE by day 14 given traffic."

---

## Multiple Testing Correction (`multiple_testing_correction.py`)

**The problem:** with many tests, some will show "significance" by chance.

**Family-wise error rate (FWER):** probability of at least one false positive across all tests.

If you test 20 metrics at α=0.05 each, FWER = 1 - (0.95)²⁰ ≈ 0.64. **64% chance of at least one false positive.**

**Corrections:**

**Bonferroni (conservative):**
- New α per test: α / k (where k = number of tests).
- Testing 20 metrics: α_per_test = 0.0025.
- Very conservative; loses power.

**Holm-Bonferroni (better):**
- Sort p-values ascending: p₁ ≤ p₂ ≤ ...
- Compare p_i to α / (k - i + 1).
- Slightly more powerful than Bonferroni.

**Benjamini-Hochberg (FDR — false discovery rate):**
- Controls expected proportion of false positives among rejections.
- Less conservative; higher power.
- Standard when testing many metrics.

**FDR algorithm:**
1. Sort p-values ascending: p₁ ≤ p₂ ≤ ... ≤ p_k.
2. Find largest i such that p_i ≤ (i / k) × q (q = desired FDR level, e.g., 0.05).
3. Reject H₀ for all tests with p ≤ p_i.

**When to use which:**
- **Bonferroni:** small number of tests; want strong control.
- **Holm-Bonferroni:** slightly larger sets.
- **FDR (Benjamini-Hochberg):** exploratory analysis with many metrics.

**LLM-specific application:**
- Primary metric: no correction needed (single test).
- Secondary metrics (5-20): FDR correction.
- Segmentation analyses: FDR.

**Rule:** decide correction strategy BEFORE looking at results. Choosing after peeking is p-hacking.

---

## Variance Reduction Techniques (`variance_reduction_techniques.py`)

**Making experiments more efficient.**

**Why variance reduction matters:**
- Sample size ∝ variance.
- Halve variance → halve sample size (or halve MDE for same sample size).
- For LLM A/B, sample cost is high → variance reduction has real ROI.

**CUPED (Controlled Using Pre-Experiment Data) — Deng et al., Microsoft:**

**The idea:**
- Use pre-experiment data (Y_pre) to reduce variance in experiment metric (Y).
- Adjusted metric: Y_adj = Y - θ × (Y_pre - E[Y_pre])
- θ chosen to minimize Var(Y_adj).
- Optimal θ = Cov(Y, Y_pre) / Var(Y_pre).

**Variance reduction:**
- Var(Y_adj) = Var(Y) × (1 - ρ²)
- where ρ = correlation between Y and Y_pre.
- ρ = 0.5 → 25% variance reduction.
- ρ = 0.7 → 50% variance reduction.

**Practical implementation:**
```python
import numpy as np

# Y_pre: user's metric value in pre-experiment period
# Y: user's metric value during experiment
theta = np.cov(Y, Y_pre)[0, 1] / np.var(Y_pre)
Y_adj = Y - theta * (Y_pre - np.mean(Y_pre))

# Use Y_adj in the t-test instead of Y
```

**Typical LLM A/B gains from CUPED:**
- 20-50% variance reduction on user-level metrics.
- Requires: users had activity pre-experiment and it correlates with current activity.
- Doesn't work for new users or one-off queries.

**Other variance reduction techniques:**

**Stratification:**
- Segment users by known important covariates (user type, region).
- Analyze within strata; combine.
- Reduces variance when strata have different means.

**Regression adjustment:**
- Regress Y on treatment + covariates.
- Effect estimate from coefficient.
- Standard practice in econometrics.

**Blocking:**
- Match treatment/control on covariates.
- Powerful with small samples.

**Rule:** for any significant LLM A/B program, CUPED is table stakes. It's essentially a free 25-50% sample size reduction. Most experimentation platforms support it.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `hypothesis_testing_refresher.py` | p-values done right |
| `type_1_and_type_2_errors.py` | The trade-off |
| `statistical_power.py` | The under-appreciated concept |
| `power_calculations_for_llms.py` | Concrete formulas + LLM gotchas |
| `sample_size_estimation.py` | How long to run |
| `effect_size_estimation.py` | What's a meaningful change |
| `mde_minimum_detectable_effect.py` | MDE math and decisions |
| `multiple_testing_correction.py` | Bonferroni, FDR |
| `variance_reduction_techniques.py` | CUPED and friends |

---

*Previous: [← A/B Testing Foundations](../ab_testing_foundations/README.md) · Next: [Experiment Design →](../experiment_design_for_llms/README.md)*  ·  *Back to [main README](../../README.md)*
