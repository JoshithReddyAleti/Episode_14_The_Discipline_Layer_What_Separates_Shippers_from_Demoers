# 🔬 Causal Inference For AI — Beyond A/B When You Must

> *A/B testing is the gold standard. Sometimes you can't run one. This section is what to do when your only data is observational — and how to be honest about the caveats.*

---

## When A/B Isn't Possible (`when_ab_isnt_possible.py`)

**Legitimate reasons.**

**1. Ethical concerns.**
- Testing a safer feature on some users means others get less safety.
- Medical / regulated contexts.
- Can't withhold potentially better treatment from users.

**2. Regulatory blocks.**
- Some jurisdictions require equal treatment.
- Some regulated products can't A/B specific features.

**3. Business constraints.**
- Contract requires all customers on same version.
- SLA doesn't permit variation.

**4. Selection bias impossible to avoid.**
- Users self-select into the "treatment" (e.g., new feature is opt-in).
- Randomization impossible.

**5. Interference too high.**
- Users interact heavily; treatment leaks.
- E.g., collaborative tools.

**6. Rare events.**
- Outcomes take months to observe.
- Business can't wait for full A/B duration.

**7. Historical questions.**
- "Did last year's model change cause the improvement?" — no A/B to run.

**When A/B **isn't** an excuse:**
- "We don't have time" (usually a bad reason).
- "Users will complain" (design a fair experiment).
- "Engineering is too complex" (invest in the platform).

**Rule:** A/B first. Causal inference is the fallback, with much weaker guarantees.

---

## Observational Studies (`observational_studies.py`)

**Analyzing non-randomized data.**

**The fundamental problem: confounders.**
- People who use feature X are different from those who don't.
- They may have better outcomes for reasons unrelated to X.
- Correlation ≠ causation.

**Example:**
- Users who use "chat memory" feature have 20% higher retention.
- Is memory causing retention?
- Or: engaged users retain more AND opt into new features?
- Confounder: engagement itself.

**Techniques to reduce confounding:**

**1. Propensity score matching.**
- Model: probability of receiving treatment given covariates.
- Match treated with control users of similar propensity.
- Analyze matched pairs.

**2. Regression adjustment.**
- Include covariates in regression.
- Interpret treatment coefficient as effect after controlling.

**3. Inverse probability weighting (IPW).**
- Weight observations by inverse of their propensity.
- Creates pseudo-population balanced on covariates.

**4. Doubly robust methods.**
- Combine propensity modeling and regression.
- Consistent if either model is correct.

**Assumptions:**
- **No unmeasured confounders (strong).**
- **Positivity** — every user has non-zero probability of any treatment.

**Warning:** these methods reduce measurable confounding but can't eliminate unmeasured confounders.

**Report:**
- Explicitly list controlled variables.
- Discuss potential unmeasured confounders.
- Sensitivity analysis (how much unmeasured confounding could change the conclusion?).

**Rule:** observational conclusions are hypotheses, not confirmations. Follow up with A/B when possible.

---

## Quasi-Experiments (`quasi_experiments.py`)

**When you have a natural experiment.**

**Difference-in-Differences (DiD):**
- Compare change in treatment group before → after with change in control group before → after.
- Effect = (Treatment_post - Treatment_pre) - (Control_post - Control_pre).
- Assumes parallel trends absent treatment.

**Example:**
- Feature launched in US only (business reasons).
- Compare US metric change vs non-US metric change.
- Attribute difference to the feature.

**Regression Discontinuity (RDD):**
- Some threshold determines treatment (e.g., users with >100 logins get feature).
- Compare users just above and just below the threshold.
- Assumes they're similar except for treatment.

**Example:**
- Enterprise tier (>$10K MRR) gets a new agent feature.
- Compare $9.5K-$10K MRR customers vs $10K-$10.5K MRR customers.
- Attribute difference to the feature.

**Synthetic Control:**
- Construct a "synthetic" control from weighted combination of untreated units.
- Compare treated to synthetic control.
- Used for large-scale changes (whole markets, countries).

**Instrumental Variables (IV):**
- Find a variable that affects treatment but not outcome directly.
- Use IV to estimate causal effect.
- Rare in AI contexts.

**Prerequisites:**
- Data at multiple time points or across groups.
- Some source of exogenous variation.
- Understanding of the domain to identify the natural experiment.

**Rule:** quasi-experiments require creativity and domain knowledge. When available, they're much stronger than pure observational studies.

---

## Counterfactual Analysis (`counterfactual_analysis.py`)

**"What would have happened otherwise?"**

**The counterfactual framework:**
- Every unit has potential outcomes: Y(1) if treated, Y(0) if not.
- **We only observe one.** Individual treatment effect = Y(1) - Y(0) is unobservable.
- Average Treatment Effect (ATE) = E[Y(1) - Y(0)] is estimable under conditions.

**Applications in AI:**

**1. Model comparison.**
- "What would our error rate be if we used model B instead of A?"
- Requires assumptions about how outcomes relate to model.

**2. Feature attribution.**
- "How much of user X's satisfaction is due to feature Y?"
- Difficult; often approximate.

**3. Debugging.**
- "Why did the model fail on this input?"
- Counterfactual explanations: minimal change to input that would have changed output.

**Counterfactual reasoning tools:**
- **DoWhy (Microsoft):** structured causal inference in Python.
- **CausalPy:** Bayesian causal inference.
- **EconML (Microsoft):** heterogeneous treatment effects.

**Example: DoWhy workflow:**
```python
import dowhy
from dowhy import CausalModel

# 1. Model
model = CausalModel(
    data=df,
    treatment="used_feature",
    outcome="satisfaction",
    common_causes=["user_tier", "tenure", "prior_engagement"],
)

# 2. Identify
identified_estimand = model.identify_effect()

# 3. Estimate
estimate = model.estimate_effect(
    identified_estimand,
    method_name="backdoor.propensity_score_matching",
)

# 4. Refute
refutation = model.refute_estimate(
    identified_estimand,
    estimate,
    method_name="random_common_cause",
)
```

**Rule:** counterfactual estimates require strong assumptions. Report the assumptions. Sensitivity analysis shows robustness.

---

## Causal Inference Toolkits (`causal_inference_toolkits.py`)

**The 2026 landscape.**

**DoWhy (Microsoft):**
- Framework for causal inference.
- Standardizes the four-step workflow (model, identify, estimate, refute).
- Broad method support.
- Good starting point.

**EconML (Microsoft):**
- Focus on heterogeneous treatment effects (HTE).
- Machine-learning-driven effect estimation.
- Great for finding subgroups with different effects.

**CausalML (Uber):**
- Similar goals to EconML.
- Uplift modeling emphasis.

**CausalPy:**
- Bayesian approach.
- Interpretable and rigorous.
- Newer but growing.

**Causal Impact (Google):**
- Time-series causal inference.
- Uses Bayesian structural time-series.
- Excellent for marketing/launch analysis.

**pymc-causal:**
- Bayesian causal inference in PyMC.
- Advanced users; strong statistical rigor.

**When to use each:**
- **General analysis:** DoWhy.
- **HTE / subgroup effects:** EconML or CausalML.
- **Time-series:** CausalImpact.
- **Bayesian preferred:** CausalPy, pymc-causal.

**Rule:** causal inference libraries make the math accessible but don't remove the need for causal reasoning. Use with domain expertise, not as black boxes.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `when_ab_isnt_possible.py` | Selection bias, ethics, regulation |
| `observational_studies.py` | Confounders |
| `quasi_experiments.py` | Diff-in-diff, RDD, synthetic control |
| `counterfactual_analysis.py` | What if |
| `causal_inference_toolkits.py` | DoWhy, EconML, CausalPy |

---

*Previous: [← Rollout Strategies](../rollout_strategies/README.md) · Next: [A/B Testing At Scale →](../ab_testing_at_scale/README.md)*  ·  *Back to [main README](../../README.md)*
