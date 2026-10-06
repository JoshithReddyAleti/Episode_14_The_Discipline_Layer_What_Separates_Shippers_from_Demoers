# 🏃 Running Experiments — Execution Across LLM Changes

> *Design is on paper. Running is where things break. This section is the practical execution of A/B tests across the four kinds of LLM changes.*

---

## A/B Testing Platforms (`ab_testing_platforms.py`)

**The 2026 landscape.**

**Statsig:**
- Fastest-growing in 2024-2026.
- Free tier attractive; strong SDK.
- Feature flags + experimentation + analytics.
- Strong for LLM-native startups.

**LaunchDarkly:**
- Enterprise incumbent for feature flags.
- Experimentation as add-on.
- Best-in-class for feature flag operations.

**Split:**
- Strong experimentation platform.
- Analytics integration.
- Enterprise-focused.

**Optimizely:**
- Historically strong for web A/B.
- Extending to server-side / LLM use cases.

**Amplitude Experiment / Mixpanel Experiments:**
- If you already use their analytics.
- Less powerful than dedicated platforms.

**GrowthBook (open source):**
- Self-hostable.
- Statistical rigor.
- Growing quickly.

**In-house platforms:**
- Larger orgs (Netflix, Airbnb, Uber, Meta) run their own.
- Custom to their scale.

**Choosing:**
- **Small team, LLM-heavy:** Statsig or GrowthBook.
- **Enterprise with existing FF investment:** LaunchDarkly + separate analytics.
- **All-in-one analytics:** Amplitude/Mixpanel Experiments.
- **Building at scale:** consider building on top of open-source.

**Must-haves for LLM A/B:**
- Server-side experimentation (client-side won't cut it).
- Support for prompt/model as experiment variables.
- Metric flexibility (custom quality metrics).
- CUPED or other variance reduction.
- Multi-armed and factorial designs.

---

## Feature Flag Integration (`feature_flag_integration.py`)

**Treat prompts / models as feature flags.**

**Pattern:**
```python
def handle_query(user_id, query):
    # Fetch active variant for user
    variant = feature_flags.get_variant("chat_prompt_v3_experiment", user_id)
    
    if variant == "control":
        prompt = load_prompt("chat_prompt_v2")
    elif variant == "treatment":
        prompt = load_prompt("chat_prompt_v3")
    
    response = llm.complete(prompt, query)
    
    # Log for analytics
    analytics.log(
        experiment="chat_prompt_v3_experiment",
        variant=variant,
        user_id=user_id,
        response_quality=score(response),
    )
    
    return response
```

**Assignment must be:**
- **Deterministic.** Same user + experiment → same variant every time.
- **Random.** Users evenly assigned across variants.
- **Sticky.** No mid-session variant switching.

**Standard implementation:**
```python
def assign_variant(user_id, experiment_id, allocation):
    hash_input = f"{user_id}:{experiment_id}"
    hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
    percentile = (hash_value % 10000) / 100.0  # 0-100
    
    cumulative = 0
    for variant, pct in allocation.items():
        cumulative += pct
        if percentile < cumulative:
            return variant
```

**Anti-patterns:**
- Non-deterministic assignment (different variant on re-visit).
- Client-side assignment (users can force a variant).
- Not logging assignment (can't analyze after the fact).

---

## Prompt A/B Testing (`prompt_ab_testing.py`)

**The most common LLM A/B.**

**What varies:**
- Prompt wording.
- System prompt structure.
- Few-shot examples.
- Prompt template variables.

**What stays constant:**
- Model version.
- Temperature and other decoding params.
- Downstream processing.

**Considerations:**

**Same model matters.**
- Different models react differently to same prompt.
- Fix model version for the duration of the test.
- Pin to specific API version (e.g., `gpt-4o-2024-08-06`, not `gpt-4o`).

**Non-determinism.**
- Even with same prompt+model, outputs vary.
- Use temperature 0 for lower variance where quality allows.
- Larger samples to average out.

**Prompt sensitivity by task:**
- Classification: usually low sensitivity → smaller effects, larger samples needed.
- Open-ended generation: high sensitivity → often clear differences.

**Rollback:**
- Prompt changes are fastest to roll back (just flip the flag).
- Take advantage: rollback bar can be lower.

**Typical duration:** 1-2 weeks. Prompt changes tend to have observable effects quickly.

---

## Model A/B Testing (`model_ab_testing.py`)

**Comparing underlying models.**

**Scenarios:**
- Upgrade from mini → full model.
- Switch between providers.
- Compare open-source alternatives.
- Custom fine-tune vs base model.

**Considerations:**

**Cost implications.**
- Different models have very different costs.
- Cost metrics are as important as quality metrics.
- Cost-quality trade-offs may drive decisions.

**Latency implications.**
- Different models have different response times.
- Guardrail: latency P95 must not regress by more than X.

**Behavioral differences.**
- Different models have different tendencies.
- Refusal rates.
- Verbosity.
- Format compliance.

**Testing protocol:**
- Same prompts, same tasks, different models.
- Log all output for analysis.
- Metrics tracked per model: quality, cost, latency.

**Rollback:**
- Model changes harder to roll back than prompts (server-side infrastructure).
- Should have dual-serving capability during transition.
- Blue-green deployment pattern.

**Typical duration:** 2-4 weeks. Model changes benefit from longer observation to catch edge cases.

---

## RAG A/B Testing (`rag_ab_testing.py`)

**Retrieval changes.**

**What varies:**
- Embedding model.
- Chunking strategy.
- Retrieval top-k.
- Reranker model.
- Hybrid search weights.
- Retrieval filters.

**Isolation is hard.**
- Changing one retrieval component affects downstream.
- Model may recover from bad retrieval (or not).
- Users may not notice differences.

**Testing protocol:**
- End-to-end A/B (retrieval + LLM), measure user metrics.
- Isolate retrieval quality separately (offline recall@k on golden set).
- Correlate offline retrieval metric with A/B outcome.

**Metrics:**
- User-facing: task success, satisfaction.
- Retrieval-specific: was the answer grounded in retrieved chunks?
- Cost: retrieval + generation total.

**Segment analysis important.**
- Different query types benefit from different retrieval strategies.
- Segment by query length, topic, complexity.

**Typical duration:** 2-4 weeks. Retrieval changes have varied impact across query distribution.

---

## Agent A/B Testing (`agent_ab_testing.py`)

**The hardest case.**

**Why agents are hard:**
- Multi-turn interactions.
- Tool use adds complexity.
- Success depends on multiple steps.
- User behavior interacts with agent behavior.
- Variance is enormous.

**What varies:**
- Agent orchestration prompt.
- Tool set.
- Model behind the agent.
- Planning strategy.

**Metrics:**
- **Task success rate** — end-to-end.
- **Time to task completion.**
- **Turns to task completion.**
- **Tool use efficiency.**
- **User satisfaction.**
- **Cost per task.**

**Sample size challenges:**
- Session-level randomization → small effective sample.
- High variance per session.
- Need thousands of sessions per arm.

**Metric complications:**
- What counts as "task completion" is ambiguous.
- Users abandon for many reasons.
- Success requires long conversation.

**Practical approach:**
- Simulator-based testing (before human A/B).
- Small human A/B (100-500 users) for feasibility.
- Full A/B if simulator + small A/B look promising.

**Typical duration:** 4-8 weeks. Agent changes take longer to evaluate due to variance and long tasks.

---

## Shadow Testing Patterns (`shadow_testing_patterns.py`)

**Test without user impact.**

**Concept:**
- Send real traffic to both production (visible) and shadow (hidden) systems.
- Compare outputs offline.
- No user sees the shadow output.

**Uses:**
- Testing new model / prompt safely before A/B.
- Detecting regressions before they hit users.
- Building baseline data.

**Implementation:**
```python
def handle_query(user_id, query):
    prod_response = production_llm.complete(query)
    shadow_response = shadow_llm.complete(query)  # Async
    
    # User sees only production
    return_to_user(prod_response)
    
    # Log both for offline comparison
    async_log(
        query=query,
        prod=prod_response,
        shadow=shadow_response,
    )
```

**Advantages:**
- **Zero user risk** — users see only production.
- **Real traffic distribution.**
- **Can compare offline.**

**Disadvantages:**
- Double the inference cost during shadow period.
- No user feedback signal (users didn't interact with shadow).
- Can only measure output quality, not user response.

**Typical use pattern:**
- Shadow test for 1-2 weeks → confirms no gross regressions.
- Then A/B test for user feedback signal.
- Then rollout.

**Anti-patterns:**
- Shadowing without offline comparison plan.
- Shadowing forever without ever A/B-ing.
- Comparing on non-representative traffic.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `ab_testing_platforms.py` | Statsig, Split, LaunchDarkly, etc. |
| `feature_flag_integration.py` | Prompt as feature |
| `prompt_ab_testing.py` | Specifically for prompts |
| `model_ab_testing.py` | Comparing models |
| `rag_ab_testing.py` | Retrieval changes |
| `agent_ab_testing.py` | The hardest case |
| `shadow_testing_patterns.py` | Test without user impact |

---

*Previous: [← Experiment Design](../experiment_design_for_llms/README.md) · Next: [Analyzing Experiments →](../analyzing_experiments/README.md)*  ·  *Back to [main README](../../README.md)*
