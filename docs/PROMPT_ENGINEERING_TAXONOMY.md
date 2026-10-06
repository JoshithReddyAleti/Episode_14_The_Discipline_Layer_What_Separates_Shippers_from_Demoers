# Prompt Engineering Taxonomy

## The maturity ladder

- **Level 0:** Prompts inline in code, no separation.
- **Level 1:** Externalized to files.
- **Level 2:** Versioned in Git.
- **Level 3:** Tested with eval sets.
- **Level 4:** Deployed like code (canary, A/B, rollback).
- **Level 5:** Compiled/optimized via DSPy or equivalent.

In 2026, level 3-4 is table stakes for production. Level 5 is emerging.

## Technique landscape

**Foundation:** zero-shot, few-shot, system prompt engineering.

**Reasoning:**
- Chain-of-Thought (CoT).
- Self-consistency (sample + vote).
- Chain-of-Verification (CoVe).

**Structured:**
- Tree-of-Thoughts (ToT).
- Graph-of-Thoughts (GoT).
- Program-of-Thoughts (PoT).

**Latency:**
- Skeleton-of-Thought (SoT — parallel decoding).

**Grounded:**
- Analogical prompting.
- Constitutional prompting.

**Optimization:**
- DSPy compilation.
- TextGrad.
- APE, OPRO, PromptBreeder.

**Compression:**
- LLMLingua, LongLLMLingua, Selective Context.

**Structured output:**
- Outlines, XGrammar, LMFormatEnforcer, LLGuidance.
- Instructor (Pydantic + LLM).
- Provider structured outputs (OpenAI, Anthropic, Google).

## Pattern selection

- Simple classification/extraction → zero-shot or few-shot.
- Reasoning (1-3 steps) → CoT.
- Complex reasoning, multiple paths → ToT or self-consistency.
- Math/computation → PoT.
- Factual generation → CoVe.
- Long structured output → SoT.
- Complex subproblem structure → GoT.
- High-quality single-answer → self-consistency.
- Safety-sensitive → constitutional.

## Anti-patterns

- Meta-prompting for simple tasks (cost without gain).
- Applying ToT where CoT would suffice.
- Stacking patterns without measuring.
- Not versioning prompts.
- No eval gate on prompt PRs.

