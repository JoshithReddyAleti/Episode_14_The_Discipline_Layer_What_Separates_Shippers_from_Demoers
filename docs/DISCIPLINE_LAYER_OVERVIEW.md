# The Discipline Layer — Overview

Episode 14 covers four disciplines that separate production AI systems from prototypes:

1. **Data Engineering For AI** — vector DBs, versioning, dedup, contamination, synthetic data, pipelines.
2. **Prompt Engineering As Engineering** — versioning, DSPy compilation, structured decoding, compression, advanced patterns.
3. **LLM Security In Depth** — OWASP LLM Top 10, injection defenses, exfiltration, jailbreaking, supply chain, red teaming.
4. **A/B Testing On Stochastic Systems** — statistical foundations, experiment design, rollout, causal inference, at-scale.

## How to Read This Episode

- Each part is independent. Start with the one closest to your current pain.
- Section READMEs are the substantive content (research-paper depth).
- Code stubs point back to READMEs; utility modules are functional CLIs.
- Discipline examples are runnable labs demonstrating end-to-end patterns.

## What This Episode Is Not

- Not a survey. Every section takes positions on what works and what doesn't.
- Not an academic reference. Every claim is oriented toward production reality.
- Not comprehensive. Each discipline could be its own book; we cover what you need to make good architectural decisions.

## Suggested Learning Paths

**"I'm building a RAG system":** Part A (vector DBs, dedup, contamination) → Part B (structured decoding, compression) → Part C (indirect injection defenses).

**"I ship LLM features fast":** Part B (DSPy, versioning) → Part D (statistical foundations, running experiments).

**"I own security for AI":** Part C (all sections) → Part A (contamination) → Part D (rollout, canary).

**"I lead an AI platform team":** All four parts, focus on the "at scale" and "org patterns" sections.

