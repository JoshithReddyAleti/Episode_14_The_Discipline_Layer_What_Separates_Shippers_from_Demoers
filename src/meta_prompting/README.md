# 🪞 Meta-Prompting — Prompts About Prompts

> *Prompts that talk about prompts, or that ask the model to write its own prompts, or that critique the previous output. A family of patterns useful when leveraged correctly, dangerous when they collapse.*

---

## Meta-Prompt Patterns (`meta_prompt_patterns.py`)

**What "meta-prompting" covers:**

**1. Prompts-as-code.**
- Prompts that include structured, code-like instructions.
- "Follow these steps exactly: 1) ... 2) ... 3) ..."
- Higher reliability than freeform instructions.

**2. Prompts generating prompts.**
- Ask an LLM: "Generate a good prompt for classifying customer sentiment."
- Use the generated prompt on the actual task.
- Widely used in APE, OPRO, DSPy.

**3. Self-reflection.**
- "Here is your draft answer. Critique it. Then produce a final answer."
- Multi-step generation with the model as its own reviewer.

**4. Chain-of-verification.**
- "Answer the question. List the facts you relied on. Verify each fact. Correct the answer if needed."
- Reduces hallucination on factual tasks.

**5. Constitutional AI-style.**
- "Given these principles, revise the response to align with them."
- Model applies value/style constraints as a second pass.

**6. Debate patterns.**
- Two personas argue; a third synthesizes.
- Improves quality on subjective or complex questions.

**Value proposition:**
- Higher output quality for complex tasks.
- Better factuality via self-checking.
- Value/safety alignment through constitutional passes.

**Cost:**
- 2-5× more LLM calls per user query.
- Higher latency.
- More complex prompt engineering.

---

## Prompt Generation By LLM (`prompt_generation_by_llm.py`)

**Machines writing prompts for machines.**

**Simple pattern:**
```python
def generate_prompt_for_task(task_description, examples):
    return llm(f"""
You are a prompt engineer. Given a task and examples, write a prompt that will elicit correct behavior from an LLM.

Task: {task_description}

Examples:
{format_examples(examples)}

Prompt:
""")
```

**Iterative refinement:**
1. Generate a candidate prompt.
2. Test on validation examples.
3. If failures, ask LLM to analyze and refine.
4. Iterate until satisfactory.

**This is the core of APE and similar methods.**

**Guidelines for prompt-generation prompts:**
- Show examples of the task (few-shot).
- Show examples of good prompts vs bad prompts (meta-few-shot).
- Constrain the output format (JSON with prompt field).
- Specify tone, length, style requirements.

**Meta-safety concerns:**
- Generated prompts can inherit issues from the training data.
- "Best" prompts by metric may exploit reward loopholes.
- Always human-review generated prompts before production.

---

## Self-Reflection Prompts (`self_reflection_prompts.py`)

**Model critiquing its own output.**

**Pattern:**
```
Step 1 — Draft:
Q: {question}
A: [model produces initial answer]

Step 2 — Critique:
"Here is your answer: {draft}
What are 3 issues with this answer?"
[model produces critique]

Step 3 — Refine:
"Here is your answer: {draft}
Here are issues: {critique}
Produce an improved answer."
[model produces refined answer]
```

**Empirical results:**
- Improves quality on **complex** tasks (math, multi-step reasoning) by 5-15%.
- **Neutral or negative** on simple tasks (adds noise without adding value).
- **Cost:** 3× the LLM calls.

**When to use:**
- Complex reasoning where errors are common.
- Long-form generation where consistency matters.
- Tasks with objective quality criteria.

**When NOT to use:**
- Simple lookup or classification.
- Tasks where the model tends to over-critique (creative writing).
- Cost-sensitive high-volume workloads.

**Failure modes:**
- **Sycophancy in critique:** model finds fake issues to appear thorough.
- **Second-guessing correct answers:** correct answer changed to a wrong one during "refinement."
- **Over-refinement:** each pass makes the answer marginally better but bloats output.

**Fix:** ground the critique in specific criteria, not open-ended "what's wrong."

---

## Constitutional AI Prompting (`constitutional_ai_prompting.py`)

**Anthropic's Constitutional AI pattern applied at prompt level.**

**Original CAI (training-time):**
- Model trained on principles ("be helpful, harmless, honest").
- Self-critique via principle-based prompting.
- RL from AI feedback (RLAIF).

**Prompt-time application:**
1. Model produces initial response.
2. Model is prompted: "Given these principles, does the response violate any?"
   - Principles: "Do not fabricate. Do not give unsafe advice. Respect user privacy."
3. Model is prompted: "Revise the response to align with all principles."

**Use cases:**
- Safety-critical applications where safety training alone may miss cases.
- Domain-specific principles (medical safety guidelines, legal disclaimers).
- Brand voice enforcement.

**Advantages over training-time only:**
- Principles can be updated without retraining.
- Auditable — you can see what principle triggered a revision.
- Per-application customization.

**Costs:**
- 2× calls (draft + revision).
- Principle-drift: model may over-apply principles, making outputs bland.

**Real example (medical Q&A):**
- Principles: "Never diagnose. Always recommend consulting a professional. Cite sources for medical claims."
- Draft: model produces answer.
- Principle check: model flags "I said 'you have condition X' — violates 'never diagnose.'"
- Revision: model rewrites to "consult a healthcare provider about symptoms of X."

---

## Meta-Prompting Pitfalls (`meta_prompting_pitfalls.py`)

**Where it breaks.**

**1. Infinite regress.**
- Model asked to critique its critique of its critique...
- Diminishing returns; eventually noise.
- Cap at 1-2 refinement rounds typically.

**2. Hallucinated critiques.**
- Model asked to critique makes up issues that aren't there.
- Then "fixes" the imaginary issues, introducing real ones.
- **Fix:** ground critique in specific evaluable criteria.

**3. Sycophantic revision.**
- Model treats critique as authoritative even if it's wrong.
- Correct answers get "improved" into wrong ones.
- **Fix:** allow the refinement step to reject critique ("if the critique is wrong, keep the original").

**4. Confused personas.**
- Model in "critique" mode inherits opinions from a persona in "draft" mode.
- Multi-persona debate can produce ideological loops.
- **Fix:** clear delineation between passes.

**5. Cost explosion.**
- Each meta-layer multiplies cost.
- Complex multi-pass systems can be 5-10× more expensive.
- **Fix:** measure quality improvement per additional pass; stop when marginal.

**6. Latency compound.**
- Sequential LLM calls compound latency.
- Even 3 sequential 2-second calls = 6 seconds user-visible.
- **Fix:** parallelize where independent; reserve serial for genuine dependencies.

**7. Debugging complexity.**
- When a multi-step meta-prompted system produces a bad output, hard to identify which step failed.
- **Fix:** log all intermediate steps; sample-review for regression.

**When meta-prompting genuinely helps:**
- Complex reasoning that benefits from a checking pass.
- Safety-critical content where principle-based revision catches errors.
- Cases where the "draft" is stochastic but the "refine" step converges.

**When it doesn't:**
- Simple tasks that a single well-crafted prompt handles.
- Tasks where the model's first answer is already reliable.
- Cost-sensitive workloads.

**Rule:** measure. Meta-prompting is a hypothesis to test against a strong single-prompt baseline. If it doesn't win by enough, skip it.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `meta_prompt_patterns.py` | The pattern family |
| `prompt_generation_by_llm.py` | LLMs writing prompts |
| `self_reflection_prompts.py` | Model critiques itself |
| `constitutional_ai_prompting.py` | Principle-guided revision |
| `meta_prompting_pitfalls.py` | Failure modes |

---

*Previous: [← Prompt Compression](../prompt_compression/README.md) · Next: [Advanced Prompting Patterns →](../advanced_prompting_patterns/README.md)*  ·  *Back to [main README](../../README.md)*
