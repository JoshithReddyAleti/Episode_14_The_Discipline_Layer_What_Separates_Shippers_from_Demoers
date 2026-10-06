# 🧠 Advanced Prompting Patterns — Beyond Chain-Of-Thought

> *CoT was the discovery of 2022. The 2023-2026 wave gave us ToT, GoT, PoT, self-consistency, CoVe, Skeleton-of-Thought, and more. This section catalogs them and — critically — tells you when each actually helps.*

---

## Tree of Thoughts (`tree_of_thoughts.py`)

**Tree of Thoughts (Yao et al., 2023)** — search over reasoning paths.

**Idea:**
- Standard CoT: single linear chain of reasoning.
- ToT: at each reasoning step, generate multiple candidate next-thoughts.
- Search (BFS/DFS/beam) through the resulting tree.
- Evaluate partial paths to prune bad ones.
- Return the best complete path.

**Structure:**
```
                    problem
                       |
              [thought_1, thought_2, thought_3]
                 /         |          \
              [t1a,t1b]  [t2a,t2b]  [t3a,t3b]
              /  \        /  \        /  \
            ...  ...   ... ...      ... ...
```

**Value function:**
- LLM-judge rates each partial reasoning path.
- Score: "how likely is this reasoning to lead to a correct answer?"
- Prune paths below threshold.

**When ToT wins:**
- Problems where multiple reasoning approaches exist.
- Games (24 game, crosswords) — original ToT paper's benchmarks.
- Math problems with branching structure.

**When ToT loses:**
- Simple linear tasks (CoT is enough).
- Cost-sensitive workloads (ToT costs 5-30× more than CoT).
- Tasks where evaluating partial paths is unreliable.

**Cost:** proportional to `branching_factor^depth`. For b=3, depth=4: ~80 LLM calls per query.

**When to use:** complex reasoning where getting the right answer is worth 10-30× the compute.

---

## Graph of Thoughts (`graph_of_thoughts.py`)

**Graph of Thoughts (Besta et al., 2023)** — generalizes ToT to arbitrary DAGs.

**Beyond ToT:**
- **Merge:** combine multiple partial reasonings into one.
- **Refine:** iteratively improve a specific thought.
- **Aggregate:** synthesize final answer from multiple paths.

**Structure:**
```
       problem
      /   |   \
    T1   T2   T3
     \   /|
      T4  T5    <- T4 merges T1 and T2
       \  /
        T6      <- final synthesis
```

**Operations:**
- **Split** — problem into subproblems.
- **Solve** — subproblem to solution.
- **Merge** — combine subsolutions.
- **Refine** — improve existing thought.

**When to use:**
- Problems with sub-problem structure (mergeable subgoals).
- Aggregation of multiple partial views.
- Iterative refinement of complex objects (e.g., writing a document via section drafting + merging).

**Complexity:** GoT is more general than ToT, but the implementation overhead is higher. Most production teams use it selectively.

---

## Program of Thoughts (`program_of_thoughts.py`)

**Program of Thoughts (Chen et al., 2022)** — use code as the intermediate reasoning representation.

**Idea:**
- Instead of natural-language reasoning, model writes Python code.
- Code is executed.
- Execution output feeds the final answer.

**Example:**
```
Question: If Alice has 3 apples and buys 4 more, then gives half to Bob, how many does she have?

Reasoning (as code):
alice_start = 3
alice_bought = 4
alice_total = alice_start + alice_bought
alice_gave = alice_total // 2
alice_remaining = alice_total - alice_gave
print(alice_remaining)

Executed: 4 (with 1 given to Bob, since 7 // 2 = 3, remaining = 4)
Answer: 4
```

**Why it works:**
- LLMs sometimes make arithmetic errors in natural language reasoning.
- Code execution is deterministic.
- Complex multi-step arithmetic becomes reliable.

**Strengths:**
- Math word problems.
- Data analysis tasks.
- Any task with computational structure.

**Weaknesses:**
- Requires a code execution sandbox.
- Model may generate buggy code.
- Not all tasks are naturally expressible in code.

**Widely used in:**
- OpenAI Code Interpreter (Advanced Data Analysis).
- Anthropic Claude's tool use with Python.
- DSPy's ProgramOfThought module.

---

## Self-Consistency (`self_consistency.py`)

**Self-Consistency (Wang et al., 2022)** — sample multiple reasoning paths; take the majority answer.

**Simple pattern:**
```python
def self_consistency(prompt, n_samples=10):
    answers = [llm(prompt, temperature=0.7) for _ in range(n_samples)]
    answer_counts = Counter(extract_final_answer(a) for a in answers)
    return answer_counts.most_common(1)[0][0]
```

**Why it works:**
- Individual samples have variance.
- Correct answer is more likely across independent samples.
- Wrong answers are more scattered (multiple ways to be wrong).

**Empirical results:**
- Improves accuracy 5-15% on many benchmarks (math, commonsense).
- Larger models benefit less (already more consistent).
- Requires diverse sampling (temperature > 0).

**Cost:** proportional to `n_samples`. Typical n=5-20.

**Extensions:**
- **Weighted voting:** each sample's answer weighted by model confidence.
- **Reasoning-path voting:** compare reasoning paths, not just final answers.
- **Selection with judge:** LLM-judge picks best among samples.

**When to use:**
- Tasks with objective correct answers (math, factual QA).
- Situations where cost is justified by accuracy gain.
- Ensembling as a defense against single-sample bad luck.

**When NOT to use:**
- Subjective tasks (multiple valid answers, no majority).
- Very high-cost workloads.
- Simple tasks where model is already reliable.

---

## Chain of Verification (`chain_of_verification.py`)

**Chain of Verification (Dhuliawala et al., 2023)** — model verifies its own facts.

**Pattern:**
1. **Baseline response:** model answers the question.
2. **Verification questions:** model generates specific factual questions from its answer.
3. **Verification answers:** model answers those questions independently.
4. **Final response:** model revises the original answer using the verification results.

**Example:**
```
Q: Name three cities in Michigan and their populations.

Baseline: "Detroit (700K), Grand Rapids (200K), Ann Arbor (120K)"

Verification questions:
1. What is the population of Detroit?
2. What is the population of Grand Rapids?
3. What is the population of Ann Arbor?

Verification answers:
1. Detroit's population is approximately 620K (2020 census).
2. Grand Rapids is approximately 200K.
3. Ann Arbor is approximately 123K.

Final response: "Detroit (620K), Grand Rapids (200K), Ann Arbor (123K)"
```

**Why it works:**
- The verification step decouples fact-checking from initial generation.
- The model may be less influenced by narrative flow when checking isolated facts.
- Catches many hallucinations.

**Empirical results (from the paper):**
- Reduces hallucination rate by 30-60% on factual QA tasks.
- Longer responses (list-format outputs) benefit most.

**Cost:** 2-3× baseline (verification questions + verification answers).

**When to use:**
- Factual generation (biographies, product descriptions, list-answers).
- High-stakes correctness.
- Long-form outputs prone to accumulated hallucination.

---

## Skeleton of Thought (`skeleton_of_thought.py`)

**Skeleton-of-Thought (Ning et al., 2023)** — parallelize generation for latency.

**Idea:**
1. Model generates a **skeleton** — high-level outline / bullet points.
2. Each point is expanded **in parallel** by separate model calls.
3. Results are concatenated.

**Example:**
```
Q: What are the main causes of the French Revolution?

Skeleton:
1. Financial crisis
2. Social inequality
3. Enlightenment ideas
4. Weak monarchy

Parallel expansion:
- "Financial crisis" → [full paragraph]
- "Social inequality" → [full paragraph]
- "Enlightenment ideas" → [full paragraph]
- "Weak monarchy" → [full paragraph]

Final: concatenate paragraphs.
```

**Latency win:**
- Serial generation: 4 paragraphs × 2s each = 8s.
- Skeleton + parallel: 0.5s skeleton + max(2s each) = 2.5s.
- ~3× latency reduction on long outputs.

**Quality trade-off:**
- Coherence may suffer (independent parallel drafts).
- No cross-referencing between sections.
- Requires post-hoc coherence check for high-quality output.

**When to use:**
- Long structured outputs (lists, reports, articles).
- Latency-sensitive user-facing features.
- Cases where section independence is acceptable.

---

## Analogical Reasoning (`analogical_reasoning.py`)

**Analogical Reasoning (Yasunaga et al., 2023)** — prompt the model to first recall analogous problems.

**Pattern:**
```
Q: {novel_problem}

Step 1 (recall): "Think of similar problems you know. Describe 2-3 relevant examples."

Step 2 (adapt): "Based on those analogous problems, solve the current problem."

Step 3 (answer): "State the final answer."
```

**Why it works:**
- Explicitly activating relevant prior knowledge.
- Model uses analogous cases as informal training examples.
- Especially effective on math and code problems.

**Empirical results:**
- Comparable to or better than manual few-shot examples.
- No need to hand-craft examples for every task.

**When to use:**
- Novel problems where the model's knowledge is relevant but not immediately activated.
- Domains where the model has broad but shallow knowledge.
- When manual few-shot curation is expensive.

**Limitations:**
- Model may "recall" plausible but wrong analogies.
- Effectiveness depends on the base model's breadth.

---

## Prompting Pattern Selection (`prompting_pattern_selection.py`)

**Which pattern for which task?**

**Decision framework:**

**Simple classification, extraction, format-conversion:**
- Zero-shot or few-shot.
- No CoT needed.

**Moderate reasoning (1-3 steps):**
- Chain-of-Thought.
- Cost-effective; strong baseline.

**Complex reasoning with multiple valid paths:**
- Tree of Thoughts.
- Self-consistency as a cheaper alternative.

**Math and computational tasks:**
- Program of Thoughts.
- Reliable arithmetic via code execution.

**Factual generation prone to hallucination:**
- Chain of Verification.
- Especially for list-format outputs.

**Long-form structured outputs, latency-sensitive:**
- Skeleton of Thought.
- Parallelize by structure.

**Complex sub-problem structure:**
- Graph of Thoughts.
- When you need merge/refine operations.

**Novel problems in domains with broad model knowledge:**
- Analogical Reasoning.

**High-quality single-answer tasks:**
- Self-consistency (ensemble).

**Safety-sensitive:**
- Constitutional prompting (from meta_prompting section).

**Rule:** match pattern to task structure. Adding sophisticated patterns to simple tasks costs money without gain.

**Anti-patterns:**
- Applying ToT to a simple classification task.
- Using CoT on tasks where it doesn't help (recent research shows CoT hurts on some pattern-matching tasks).
- Stacking patterns (CoT + self-consistency + verification) without measuring.

**Rule of thumb:** start with the simplest pattern that could work. Add complexity only when metrics justify it. Measure everything.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `tree_of_thoughts.py` | ToT deep dive |
| `graph_of_thoughts.py` | GoT — merge, refine, aggregate |
| `program_of_thoughts.py` | PoT — code as reasoning |
| `self_consistency.py` | Sampling + voting |
| `chain_of_verification.py` | CoVe — self-verify facts |
| `skeleton_of_thought.py` | Parallel decoding |
| `analogical_reasoning.py` | Learn from analogous examples |
| `prompting_pattern_selection.py` | Which pattern for which task |

---

*Previous: [← Meta Prompting](../meta_prompting/README.md) · Next: [Prompt Management Platforms →](../prompt_management_platforms/README.md)*  ·  *Back to [main README](../../README.md)*
