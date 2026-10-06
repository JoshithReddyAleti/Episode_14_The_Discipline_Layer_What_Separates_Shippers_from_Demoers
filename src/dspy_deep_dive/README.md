# 🎼 DSPy — Programming, Not Prompting

> *DSPy (Stanford, 2023) is the paradigm shift: stop writing prompts, start writing programs that get compiled into prompts. Once you internalize this, hand-written prompt engineering feels like assembly language.*

---

## The DSPy Paradigm (`the_dspy_paradigm.py`)

**Traditional prompting:**
```python
prompt = f"""You are a helpful assistant. Answer the question below concisely.

Question: {question}

Answer:"""
response = llm(prompt)
```

Hand-crafted, fragile, model-specific, hard to optimize systematically.

**DSPy paradigm:**
```python
class QA(dspy.Signature):
    """Answer questions concisely and accurately."""
    question: str = dspy.InputField()
    answer: str = dspy.OutputField()

qa_program = dspy.Predict(QA)
result = qa_program(question="...")
```

The `Signature` declares *what*. DSPy figures out *how* — including the actual prompt text — via compilation.

**Why this matters:**
- **Portability across models.** Same DSPy program compiles to different prompts optimized for each model.
- **Optimization.** The compiler can search over prompt formulations, few-shot examples, and demonstrations to maximize a metric.
- **Composability.** Programs compose like functions. Multi-step reasoning becomes multi-module DSPy programs.
- **Reproducibility.** The compiled prompt + training examples are versioned artifacts.

**The mental model:** DSPy is to prompting what PyTorch is to backpropagation. You describe the computation abstractly; the framework handles the details.

---

## DSPy Signatures (`dspy_signatures.py`)

**Signatures = declarative interfaces.**

**Simple:**
```python
class Summarize(dspy.Signature):
    """Summarize the article into 2-3 sentences."""
    article: str = dspy.InputField()
    summary: str = dspy.OutputField(desc="2-3 sentence summary")
```

**Multi-field:**
```python
class Triage(dspy.Signature):
    """Triage a support ticket."""
    ticket_content: str = dspy.InputField()
    customer_tier: str = dspy.InputField(desc="one of: free, pro, enterprise")
    
    category: str = dspy.OutputField(desc="one of: billing, technical, feature-request")
    priority: str = dspy.OutputField(desc="one of: low, medium, high, critical")
    reasoning: str = dspy.OutputField(desc="brief explanation of category and priority")
```

**Behind the scenes:**
- DSPy generates the prompt.
- Adds format instructions for structured output.
- Adds few-shot examples if any are configured.
- Parses the model's output back into the declared fields.

**Signature = contract. The program's behavior is bound by the fields' names and descriptions.**

**Signatures with typed outputs:**
```python
from typing import Literal

class Classify(dspy.Signature):
    """Classify sentiment."""
    text: str = dspy.InputField()
    sentiment: Literal["positive", "negative", "neutral"] = dspy.OutputField()
```

The compiler produces constrained output prompts and/or uses structured decoding.

---

## DSPy Modules (`dspy_modules.py`)

**Modules = composable pieces.**

**Built-in modules:**

**`dspy.Predict(Signature)`:**
- Simplest: given the signature, produce output.
- One LLM call, no reasoning steps shown.

**`dspy.ChainOfThought(Signature)`:**
- Adds explicit "let's think step by step" reasoning.
- Two-part output: reasoning + final answer.
- Higher quality for reasoning tasks.

**`dspy.ReAct(Signature, tools=[...])`:**
- Reasoning + Acting.
- Model can call tools during its reasoning.
- Multi-turn interaction with the environment.

**`dspy.ProgramOfThought(Signature)`:**
- Uses code as the intermediate reasoning representation.
- Model writes code, executes it, uses output.
- Strong for math and computational reasoning.

**Composing modules:**
```python
class RAGProgram(dspy.Module):
    def __init__(self):
        self.retrieve = dspy.Retrieve(k=5)
        self.answer = dspy.ChainOfThought("context, question -> answer")
    
    def forward(self, question):
        passages = self.retrieve(question).passages
        prediction = self.answer(context=passages, question=question)
        return prediction
```

Now this is a full RAG pipeline expressed as a DSPy program. Every piece can be optimized independently.

**Custom modules:** subclass `dspy.Module`, put logic in `forward`. All sub-modules become optimizable pieces.

---

## DSPy Optimizers (`dspy_optimizers.py`)

**The magic:** given a program, a training set, and a metric, DSPy finds better prompts and few-shot examples.

**BootstrapFewShot:**
- Runs the program on training examples.
- Keeps successful traces as few-shot demos.
- Compiles the demos into the prompt.

**BootstrapFewShotWithRandomSearch:**
- Same but tries multiple demo combinations.
- Picks the best-performing set.
- Higher compute cost, higher quality.

**MIPRO (Multi-prompt Instruction Proposal and Optimization) v1/v2:**
- Uses a strong LLM to propose prompt variations.
- Bayesian optimization over the prompt + demo space.
- Best quality among common DSPy optimizers.
- Higher compute cost (dozens to hundreds of program runs).

**COPRO (Compilation via Optimization for Prompts):**
- Similar space to MIPRO.
- Different optimization strategy.

**Ensembles:**
- Compile multiple optimized programs.
- Vote or aggregate at inference.

**Choosing an optimizer:**
- **Small budget, quick win:** BootstrapFewShot.
- **Medium budget, better quality:** BootstrapFewShotWithRandomSearch.
- **Larger budget, best quality:** MIPRO v2.

**Optimizer cost:**
- BootstrapFewShot: ~10-50 program runs.
- BootstrapFewShotWithRandomSearch: ~50-200 program runs.
- MIPRO v2: ~100-500 program runs (LLM calls dominant).

Cost per compilation: $10-500 depending on program complexity and API pricing.

---

## DSPy Metrics (`dspy_metrics.py`)

**The optimization target.**

**Simple metrics:**
```python
def exact_match(gold, pred, trace=None):
    return gold.answer.strip().lower() == pred.answer.strip().lower()
```

**Task-specific:**
```python
def support_triage_metric(gold, pred, trace=None):
    category_correct = gold.category == pred.category
    priority_close = abs(priority_rank[gold.priority] - priority_rank[pred.priority]) <= 1
    return category_correct and priority_close
```

**LLM-as-judge metrics:**
```python
class Judge(dspy.Signature):
    question: str = dspy.InputField()
    correct_answer: str = dspy.InputField()
    proposed_answer: str = dspy.InputField()
    is_correct: bool = dspy.OutputField()

judge = dspy.Predict(Judge)

def judged_metric(gold, pred, trace=None):
    return judge(
        question=gold.question,
        correct_answer=gold.answer,
        proposed_answer=pred.answer,
    ).is_correct
```

**Multi-criteria metrics:**
```python
def multi_criterion(gold, pred, trace=None):
    correctness = 1 if exact_match_check(gold, pred) else 0
    format_ok = 1 if format_check(pred) else 0
    concise = 1 if len(pred.answer.split()) <= 100 else 0
    return (correctness * 0.6 + format_ok * 0.2 + concise * 0.2)
```

**Rule:** the optimizer will find whatever the metric rewards. Design your metric like you're designing a reward function — because you are.

---

## Compiling DSPy Programs (`compiling_dspy_programs.py`)

**End-to-end example:**

```python
import dspy

# Configure the LM
lm = dspy.LM(model="openai/gpt-4o-mini")
dspy.settings.configure(lm=lm)

# Define the program
class SupportBot(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought("question -> answer")
    
    def forward(self, question):
        return self.generate(question=question)

# Training data
trainset = [
    dspy.Example(question="How do I reset my password?", answer="Go to settings → security → reset.").with_inputs("question"),
    # ... more examples
]

devset = [
    dspy.Example(question="...", answer="...").with_inputs("question"),
    # ... more examples
]

# Metric
def accuracy(gold, pred, trace=None):
    return exact_match(gold.answer, pred.answer)

# Optimizer
from dspy.teleprompt import BootstrapFewShotWithRandomSearch

optimizer = BootstrapFewShotWithRandomSearch(
    metric=accuracy,
    max_bootstrapped_demos=4,
    max_labeled_demos=4,
    num_candidate_programs=10,
)

# Compile
optimized_bot = optimizer.compile(SupportBot(), trainset=trainset, valset=devset)

# Save
optimized_bot.save("./compiled_support_bot.json")

# Later: load and use
loaded_bot = SupportBot()
loaded_bot.load("./compiled_support_bot.json")
prediction = loaded_bot(question="How do I export my data?")
```

**What the compiled artifact contains:**
- Optimized instruction (the prompt text).
- Selected few-shot demonstrations.
- Any hyperparameters set during optimization.
- Version pointer to the DSPy version.

**Deployment:** the compiled JSON is a versioned artifact. Deploy it like a model artifact. Version it. Test it. A/B it.

---

## DSPy vs Manual Prompting (`dspy_vs_manual_prompting.py`)

**Honest comparison.**

**DSPy wins when:**
- Task has a clear, automatable metric.
- Training examples are available (even 10-100 is often enough).
- You'll run the task at scale (compilation cost amortizes).
- You need portability across models.
- You're iterating on prompts often (compilation replaces manual tuning).

**Manual prompting wins when:**
- Task has no clear metric (e.g., creative writing, subjective quality).
- No training examples exist.
- One-off usage (compilation cost doesn't amortize).
- You need very specific control over prompt wording (marketing tone, brand voice).

**Empirical wins from DSPy compilation (from papers and community reports):**
- 8-25% improvement over strong baseline prompts on task metrics.
- Larger gains on complex multi-step tasks.
- Smaller gains where baseline was already near-optimal.

**Compilation cost vs manual iteration:**
- Manual: 30 min - 2 hours per iteration; 5-20 iterations = 3-40 hours.
- DSPy: 30 min to write program + 30 min to compile = ~1 hour total.
- Break-even often at iteration 3-5.

**Rule:** if you're going to iterate on a prompt more than a few times, and you have a metric, use DSPy.

**Anti-patterns:**
- Using DSPy for a one-off task (overhead not worth it).
- Not writing a good metric (optimizer finds hacks).
- Not versioning the compiled artifact (loses reproducibility).

---

## DSPy Production Patterns (`dspy_production_patterns.py`)

**Deploying DSPy in production.**

**1. Artifact versioning.**
- Compiled program saved as JSON.
- Stored in artifact registry (S3, HF Hub).
- Version tagged.
- Metadata: training set version, compilation hyperparameters, eval scores.

**2. Fresh compilation cadence.**
- Recompile when:
  - Base model changes (new LLM version).
  - Training data updated.
  - Metric changes.
- Typical cadence: monthly to quarterly.

**3. A/B testing DSPy vs baseline.**
- Deploy compiled program alongside baseline.
- A/B test on real traffic.
- Compare on production metrics.

**4. Caching and latency.**
- DSPy programs may make multiple LLM calls per query (multi-hop, ReAct).
- Cache intermediate results where safe.
- Consider parallelization for independent sub-tasks.

**5. Monitoring.**
- Log inputs, intermediate reasoning, outputs.
- Track quality drift (metric on sampled traffic).
- Alert on regression.

**6. Fallback strategy.**
- If DSPy program fails (e.g., LLM API errors), fallback to a simple baseline prompt.
- Prevents complete outages.

**Real-world adoption (2026):**
- LLM-native startups: growing adoption for anything with a metric.
- Enterprise: slower adoption; DSPy sits between "we do it manually" and "we don't do LLM features."
- Research: high adoption.

**Rule:** treat compiled DSPy programs like ML models. Same versioning, testing, deployment, and monitoring discipline.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `the_dspy_paradigm.py` | The shift from prompts to programs |
| `dspy_signatures.py` | Declarative interfaces |
| `dspy_modules.py` | Composable pieces |
| `dspy_optimizers.py` | BootstrapFewShot, MIPRO, COPRO |
| `dspy_metrics.py` | The optimization target |
| `compiling_dspy_programs.py` | End-to-end example |
| `dspy_vs_manual_prompting.py` | Honest comparison |
| `dspy_production_patterns.py` | Artifact versioning, monitoring |

---

*Previous: [← Prompt Engineering Foundations](../prompt_engineering_foundations/README.md) · Next: [TextGrad and Prompt Optimization →](../textgrad_and_prompt_optimization/README.md)*  ·  *Back to [main README](../../README.md)*
