# ✍️ Prompt Engineering Foundations — Prompts As Code

> *Prompts written in Notion pages by product managers, edited in production by engineers on Friday afternoons, with no version control, no eval, and no rollback. That's how most teams do prompt engineering. This section is what production prompt engineering actually looks like.*

---

## Prompting As A Discipline (`prompting_as_a_discipline.py`)

**The maturity ladder:**

**Level 0 — Ad-hoc.** Prompts written inline in code, no separation, no history. Every LLM feature has its own hand-crafted prompt no one else understands.

**Level 1 — Externalized.** Prompts pulled out into text files or a `prompts/` directory. At least you can find them.

**Level 2 — Versioned.** Prompts in Git. Reviewed via PRs. But no evaluation on change.

**Level 3 — Tested.** Every prompt has an eval set. PRs blocked without passing evals. Regressions caught pre-deployment.

**Level 4 — Deployed like code.** Feature-flagged rollouts. A/B testing. Rollback capability. Metrics tied to prompt versions.

**Level 5 — Compiled/optimized.** DSPy or equivalent frameworks that treat prompts as programs to be optimized against metrics. Most teams don't reach here yet.

**In 2026, level 3-4 is table stakes for anything production. Level 5 is emerging.**

**Why prompts need production discipline:**
- Prompt changes can flip a feature from working to broken instantly.
- LLM behavior is stochastic; small prompt changes can have large output changes.
- Prompt regressions are hard to detect from user-facing metrics alone (may be subtle).
- Multiple teams sharing prompts need coordination.

---

## The Prompt Engineering Loop (`the_prompt_engineering_loop.py`)

**Systematic prompt iteration:**

```
1. Task specification
   - What input does the model receive?
   - What output do we want?
   - What are edge cases and failure modes?

2. Golden eval set
   - 50-500 (input, expected_output) examples.
   - Cover normal, edge, adversarial cases.
   - Held constant across iterations.

3. Baseline prompt (minimum viable)
   - Simplest prompt that could work.
   - Zero-shot or few-shot.

4. Measure
   - Run baseline on eval set.
   - Automated metrics: exact match, F1, LLM-as-judge, task-specific.

5. Analyze failures
   - Categorize errors: hallucination, format, missing info, off-topic.
   - Which category is dominant?

6. Prompt iteration
   - Targeted change to fix the dominant failure category.
   - One change per iteration if possible.

7. Re-measure
   - Did the fix work? Did it break something else?

8. Commit + version
   - New prompt version in Git.
   - Eval results attached to the commit.

9. Deploy behind a flag
   - Shadow test or A/B before broad rollout.

10. Monitor in production
    - Traffic-level metrics.
    - Sampled human review.
    - Loop back to step 5 as new failure modes emerge.
```

**Iteration cost:**
- Rapid loop (steps 4-7): 10-30 minutes if tooling is good.
- Slow loop (steps 4-7): hours to days if you're manually testing.

**The tooling delta is enormous.** Teams with proper prompt eval infrastructure iterate 10-50× faster than teams doing it manually.

---

## Prompt Versioning (`prompt_versioning.py`)

**Git for prompts, at minimum.**

**Storage patterns:**

**1. Prompts as code files.**
```
prompts/
  customer_support/
    triage.md
    response_v1.md
    response_v2.md
```
- Simple, readable.
- Git handles versioning.

**2. Prompt libraries in code.**
```python
# prompts.py
CUSTOMER_TRIAGE = """
You are a support triage system.
Given the ticket below, classify as one of: {categories}.

Ticket: {ticket_content}

Output only the category name.
"""
```
- Type-safe.
- IDE support.
- Easy to test.

**3. Externalized prompt registry.**
- Prompts stored in a database or service (Langfuse, Humanloop, PromptLayer).
- Fetched at runtime.
- Enables prompt changes without code deploys.
- Enables non-engineers to edit.

**Trade-offs:**
- Code-first: strong versioning, poor accessibility for non-engineers.
- Registry: accessibility win, but adds a service dependency and possible drift.

**Modern practice:** hybrid — canonical prompts in Git, mirror to registry for non-engineer visibility. Only Git is source of truth.

**Every prompt version should record:**
- Semantic version (v1, v2, v3).
- Git commit SHA (immutable pointer).
- Change description.
- Eval scores at the time of the change.
- Author.
- Approval status (dev / staging / prod).

---

## Prompt Evaluation At Scale (`prompt_evaluation_at_scale.py`)

**Building on Episode 8's evaluation foundations.**

**Layered eval pipeline for prompts:**

**Layer 1: Format/schema validation.**
- Output parses as JSON? Correct fields present? Types match?
- Fast (milliseconds). Deterministic. Blocking gate.

**Layer 2: Deterministic checks.**
- Exact match against known correct answer.
- Regex patterns present or absent.
- Length within bounds.

**Layer 3: Task-specific metrics.**
- F1 for classification.
- ROUGE/BLEU for text generation (if applicable).
- Custom metrics per task.

**Layer 4: LLM-as-judge.**
- Rubric-based scoring.
- Pairwise comparison to baseline.
- Cost: $0.001-0.01 per example depending on model.

**Layer 5: Human evaluation.**
- Random samples for high-confidence signal.
- Expert review for domain-heavy tasks.
- Cost: $2-20 per example.

**Layer 6: Production A/B.**
- Real users, real metrics.
- Ultimate signal.

**Prompt-specific challenges:**
- **Non-determinism:** same prompt + same input can give different outputs at temperature >0. Run multiple samples for statistical significance.
- **Small effect sizes:** prompt changes often shift metrics 1-3%. Need large enough eval sets (500+ examples) to detect.
- **Interaction effects:** prompt changes may work well with one model, poorly with another.

**Tooling:**
- **Langfuse** — prompt versioning + eval + tracing.
- **Humanloop** — enterprise prompt platform.
- **PromptLayer** — logging + eval.
- **Promptfoo** — CLI-first eval tool.
- **DIY** — custom eval framework, common in mature shops.

---

## Prompt Engineering Org Patterns (`prompt_engineering_org_patterns.py`)

**Who owns prompts?**

**Pattern 1: Engineers own everything.**
- Engineers write, maintain, deploy prompts.
- Fine for early-stage.
- Doesn't scale — engineers become bottleneck for content changes.

**Pattern 2: Prompt engineer role.**
- Dedicated role sitting between engineering and product.
- Owns prompt libraries, evals, iteration.
- Common at LLM-native companies.

**Pattern 3: Content/PM ownership with engineering review.**
- Product managers or content designers write prompts.
- Engineers review PRs, own infrastructure.
- Scales well but requires strong tooling.

**Pattern 4: Federated with platform team.**
- Platform team owns prompt infrastructure (registry, eval framework, deploy pipeline).
- Product teams own their prompts.
- Best pattern for large orgs.

**Governance:**
- **Approval gates:** prod-facing prompt changes require sign-off.
- **Style guide:** consistency across the org (voice, format, safety patterns).
- **Reusable snippets:** common patterns (safety, formatting, structured output) live in shared modules.
- **Deprecation policy:** removing old prompt versions.

**Common failure modes:**
- No one owns prompts → prompts rot.
- Engineers own but content changes daily → engineering velocity destroyed.
- No governance → 47 different prompts do the same thing across teams.
- No shared eval infrastructure → each team reinvents evaluation.

**Rule:** prompt engineering is a real function. Treat it like one.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `prompting_as_a_discipline.py` | Not magic — the maturity ladder |
| `the_prompt_engineering_loop.py` | Systematic iteration |
| `prompt_versioning.py` | Git for prompts |
| `prompt_evaluation_at_scale.py` | Ties to Episode 8 |
| `prompt_engineering_org_patterns.py` | Who owns prompts |

---

*Previous: [← Data Pipelines](../data_pipelines_for_ai/README.md) · Next: [DSPy Deep Dive →](../dspy_deep_dive/README.md)*  ·  *Back to [main README](../../README.md)*
