# 🧬 Synthetic Data Engineering — As A Discipline, Not A Hack

> *"Just generate some synthetic data" is where most projects lose their quality guarantees. This section is the engineering discipline that makes synthetic data actually useful.*

---

## Synthetic Data Use Cases (`synthetic_data_use_cases.py`)

**Legitimate wins:**

**1. Data augmentation for underrepresented cases.**
- Rare edge cases in your production distribution.
- Adversarial examples.
- Cross-language coverage where real data is scarce.

**2. Bootstrapping annotation.**
- Human labelers correct LLM-generated candidates 5-10× faster than authoring from scratch.
- Applied to instruction tuning, preference labeling, evaluation set curation.

**3. Filling capability gaps.**
- Model doesn't know your domain vocabulary.
- Generate synthetic Q&A over your knowledge base to teach it.

**4. Distillation from larger models.**
- Teacher generates outputs; student learns to imitate.
- 70-95% of teacher quality at 10-100× cheaper serving.

**5. Preference generation at scale.**
- LLM-judge produces pairwise preferences from multiple candidate outputs.
- Feeds DPO / IPO / KTO training.

**6. Privacy-preserving data.**
- Real customer data can't leave the boundary; synthetic examples matching the distribution can.

**7. Test-set expansion.**
- Growing your eval set with synthetic edge cases.

**Where synthetic data fails:**
- Tasks requiring human judgment the LLM doesn't have.
- When teacher model has biases you don't want to inherit.
- When filters aren't strong enough (quality collapse).
- When success depends on real user language patterns.

**Rule:** synthetic is a multiplier on the seed. Bad seed → bad synth. Good seed + good filters → high-quality bulk data at 100× throughput.

---

## Synthetic Data Quality Metrics (`synthetic_data_quality_metrics.py`)

**"Is my synthetic data any good?" — measurable answer:**

**1. Diversity metrics.**
- **Semantic diversity:** embed all examples; measure spread (variance, minimum pairwise distance).
- **Lexical diversity:** unique n-grams, type-token ratio.
- **Cluster count:** k-means clustering; how many distinct clusters emerge?
- **Length distribution:** should span short to long, not all similar.

**2. Quality metrics.**
- **Perplexity under a strong model:** flag anomalies (too high = noise; too low = bland).
- **LLM-judge quality score:** rate each example on task-appropriate criteria.
- **Format conformance:** validates schema (JSON parses, expected fields present).
- **Factual correctness:** verify factual claims where automatic verification is possible.

**3. Contamination metrics.**
- Overlap with public benchmarks (see contamination section).
- Overlap with your golden eval set.

**4. Distributional match to production.**
- Length, topic, complexity distribution should approximate real usage.
- Divergence metrics (KL, JS) between synthetic and real distributions.

**5. Downstream impact.**
- The ultimate metric: does training on this synthetic data improve downstream task performance?
- Run an A/B on training with vs without a synthetic subset.

**Dashboard for a synthetic data pipeline:**
- Volume generated per run.
- Filter attrition rate per stage.
- Diversity score.
- Quality score distribution.
- Contamination flag rate.
- Downstream A/B result.

---

## Synthetic Data Pipelines (`synthetic_data_pipelines.py`)

**End-to-end generation pipeline:**

```
Seed dataset (200-500 high-quality expert examples)
    ↓
Diverse prompting (multiple templates, temperatures)
    ↓
Generation via teacher model (batch inference)
    ↓
Format validation (reject malformed)
    ↓
Content filters (perplexity, toxicity, PII, length)
    ↓
LLM-judge quality gate (score, reject below threshold)
    ↓
Diversity check (embed + cluster + prune duplicates)
    ↓
Contamination check (against golden eval)
    ↓
Human spot-check (random 100, reject or accept batch)
    ↓
Version and store
    ↓
A/B on downstream task (before broad adoption)
```

**Batch generation infrastructure:**
- Async parallel calls to teacher API (or in-house model).
- Rate limit awareness.
- Retry logic on failures.
- Cost tracking per generated example.

**Attrition typical:**
- Format validation: 5-15% removed.
- Content filters: 5-20%.
- LLM-judge gate: 10-40%.
- Diversity dedup: 20-50%.
- Contamination: <5% typical.

**Final yield:** 30-60% of generated examples make it to final dataset. Budget accordingly.

**Cost model:**
- Teacher API: $0.005-0.05 per generated example.
- LLM-judge: $0.001-0.01 per judged example.
- Embeddings: $0.0001 per example.
- Compute for filters: minimal.
- **Total per 100K final examples:** $500-5000 typical.

Compare to human-labeled: $1-3 per example = $100K-300K for 100K examples.

---

## LLM-Generated Datasets (`llm_generated_datasets.py`)

**Best practices from the frontier:**

**Diverse prompting.**
- Multiple templates for the same task.
- Temperature 0.7-1.0 (not zero — you want diversity).
- Rotate teacher models (GPT-4, Claude, Gemini, Qwen) to reduce model-specific quirks.

**Task decomposition.**
- Generate the input first (query, question, instruction).
- Then generate the output (with a different prompt or same call).
- Rate the (input, output) pair for quality.

**Constrained generation.**
- Use JSON mode / structured decoding to enforce schema.
- Higher yield than freeform.

**Self-consistency filtering.**
- Generate 3-5 candidate outputs.
- Keep only those where multiple candidates agree.
- Rejects "creative" outputs likely to be inconsistent.

**Judge-based filtering.**
- LLM-judge with a rubric.
- Multi-judge (2-3 different models) for robustness.
- Discard examples any judge scores low.

**Persona diversity.**
- Generate outputs "as X-type user" (novice / expert / hostile / non-native English) to widen distribution.
- Prevents mode collapse to model's default voice.

**Domain-aware seeding.**
- Include domain-specific terminology and examples in generation prompts.
- Cite domain sources to anchor factuality.

**Anti-patterns:**
- Generating from a single template → homogeneous data.
- Skipping quality filters → noisy data.
- Not de-duplicating → weighted examples.
- Not measuring downstream impact → don't know if it helped.

---

## Augmentation at Scale (`augmentation_at_scale.py`)

**Beyond one-off generation.**

**Common augmentation patterns:**

**1. Back-translation.**
- Translate EN → FR → EN.
- Yields paraphrases while preserving meaning.
- Works for many pairs (EN↔FR, EN↔ES, EN↔DE typically clean).

**2. LLM paraphrasing.**
- Prompt: "rewrite this as if it were said by a different person."
- Faster than back-translation, higher variance.

**3. Template expansion.**
- Start with slot-filling templates: "How do I [ACTION] a [OBJECT]?"
- Enumerate slot values.
- Generate coverage of realistic combinations.

**4. Adversarial augmentation.**
- Typos, misspellings.
- Word substitution with synonyms.
- Formatting variations.
- Sentence reordering.

**5. Format augmentation.**
- Same content in JSON, XML, YAML, markdown.
- Different prompt phrasings ("Explain X", "What is X?", "Tell me about X").

**Applied to instruction data:**
- Each original example → 3-10 augmented versions.
- Increases robustness to input variation.
- Diminishing returns past 5× augmentation.

**Applied to preference data:**
- Rewrite chosen/rejected pairs in different styles.
- Keep the preference relationship intact.

**Warning:** augmentation is not a substitute for real data volume. Augmenting 100 examples 10× gives you 100-flavor data, not 1000-flavor data. The diversity ceiling is set by the seed.

---

## Domain-Specific Synth (`domain_specific_synth.py`)

**Legal, medical, financial, technical — high-value domains where synthetic data needs extra care.**

**Extra requirements:**

**1. Domain-grounded generation.**
- Prompt the teacher with domain-specific documents (RAG-style).
- Generate Q&A anchored to source citations.
- Verify factuality via retrieval-based grounding.

**2. Expert review.**
- Human experts (physicians, lawyers, CPAs) sample-review generated content.
- Higher cost per review but higher confidence.
- Typical: expert reviews 10-20% of a synthetic corpus before use.

**3. Regulatory-aware filters.**
- Medical: no unlicensed medical advice patterns.
- Legal: no unlicensed practice of law patterns.
- Financial: no unlicensed investment advice.
- Automated detection via classifiers + human review.

**4. Jurisdictional awareness.**
- Legal domain: US vs EU vs UK law differ.
- Generation should be jurisdiction-scoped and labeled.

**5. Confidentiality preservation.**
- Never use real customer data as prompt input in a way that leaks it.
- If using real data as seed, ensure teacher API doesn't retain it (privacy tier).

**6. Higher quality thresholds.**
- Standard LLM-judge score threshold: 4.0/5.
- Domain: 4.5/5 or higher.
- Reject more aggressively.

**Real-world example (medical Q&A):**
- 500 expert-authored seed Q&A pairs.
- Teacher generates 20K candidate expansions with retrieval grounding.
- 40% pass automated filters.
- Physician spot-reviews random 10%; approves 85% of those.
- Final: ~7K high-quality synthetic Q&A pairs at ~$4K total cost.
- Human-only equivalent: ~$100K.

---

## Evaluating Synth Impact (`evaluating_synth_impact.py`)

**The final metric: did the synthetic data actually help?**

**A/B design:**
- **Arm A:** train on real data only.
- **Arm B:** train on real + synthetic.
- Same eval set. Same hyperparameters.
- Report performance delta.

**What to measure:**
- Task-specific benchmarks (primary).
- Regression suite (secondary — did we lose anything?).
- Distributional coverage (did we fill gaps?).
- Cost/time to comparable quality (secondary metric — synthetic often wins on this).

**Isolation studies:**
- Vary synthetic proportion (0%, 25%, 50%, 100%).
- Find the sweet spot.
- Often peaks at 30-70% synthetic in mixed datasets.

**Longitudinal:**
- Track quality over multiple generation batches.
- Did quality drift as generation pipeline evolved?
- Especially important as base teacher model changes.

**Failure modes to catch:**
- **Mode collapse:** synth data all sounds the same → decreased diversity.
- **Style drift:** model starts producing teacher-model style outputs.
- **Reward hacking:** synth data optimized to pass filters but not good.
- **Contamination creep:** teacher was trained on your eval; synth inherits that.

**Rule:** every synthetic dataset gets an A/B before it becomes a core training input. No exceptions.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `synthetic_data_use_cases.py` | When it wins |
| `synthetic_data_quality_metrics.py` | Measuring it |
| `synthetic_data_pipelines.py` | Generate → filter → validate |
| `llm_generated_datasets.py` | Best practices |
| `augmentation_at_scale.py` | Beyond one-off |
| `domain_specific_synth.py` | Legal, medical, finance |
| `evaluating_synth_impact.py` | A/B on downstream task |

---

*Previous: [← Contamination Detection](../contamination_detection/README.md) · Next: [Data Pipelines →](../data_pipelines_for_ai/README.md)*  ·  *Back to [main README](../../README.md)*
