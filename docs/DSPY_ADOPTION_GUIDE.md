# DSPy Adoption Guide

## When DSPy wins

- Task has a clear automatable metric.
- Training examples exist (10-100 often enough).
- Task will run at scale (compilation cost amortizes).
- Portability across models needed.
- Iterating on prompts often.

## When manual prompting still wins

- No clear metric (creative writing, subjective quality).
- No training examples.
- One-off usage.
- Need precise control over exact wording (marketing, brand).

## Adoption path

**Week 1:** Prototype — DSPy Predict for one task.

**Week 2:** Add ChainOfThought; write eval metric.

**Week 3:** Try BootstrapFewShotWithRandomSearch; compare to hand-crafted prompt.

**Week 4:** MIPRO for the top-1 task; ship if wins by margin.

**Month 2:** Migrate 3-5 more tasks. Establish compilation cadence.

**Month 3+:** DSPy as default for anything with a metric; hand-crafted only for exceptions.

## Common gotchas

- **Bad metric = bad compilation.** Optimizer finds hacks. Test your metric first.
- **Compiled artifact must be versioned.** Treat like model weights.
- **Recompile on base model changes.** Compiled prompts are model-specific.
- **Cost budget for compilation.** MIPRO uses 100-500 program runs.

## Empirical wins (community-reported)

- 8-25% improvement over strong baseline prompts on task metrics.
- Larger gains on complex multi-step tasks.
- Break-even vs manual iteration at iteration 3-5.

