# Injection Defense Playbook

## The 9-layer stack (defense in depth)

1. **Input filtering** — pattern, classifier, LLM detector.
2. **Spotlighting** — delimiters, encoding, datamarking of untrusted content.
3. **Instruction hierarchy** — model-level (GPT-4+, Claude, others).
4. **Dual-LLM pattern** — privileged (P-LLM) reads user; quarantined (Q-LLM) reads untrusted content, produces structured output only.
5. **Least-privilege tools** — blast radius reduction.
6. **Output filtering** — egress PII, sensitive-content, format checks.
7. **Sandboxing** — code execution, tool call, output rendering all constrained.
8. **Monitoring** — anomaly detection, session-level pattern detection.
9. **Incident response** — playbooks, on-call, communication.

## Investment priority

1. Least-privilege tools (highest ROI — architectural).
2. Dual-LLM (for indirect injection surface).
3. Output filtering (catches many upstream failures).
4. Monitoring (know what's happening).
5. Input filtering (baseline).
6. Everything else.

## Layer selection per surface

| Surface | Recommended layers |
|---|---|
| Public chatbot (read-only) | 1, 2, 6, 8, 9 |
| Public RAG bot | 1, 2, 3, 4, 6, 8, 9 |
| Internal agent with tools | 1, 2, 3, 4, 5, 6, 7, 8, 9 |
| Autonomous agent | All 9 + human review |

## Measurement

- Attack Success Rate (ASR) on published + custom attack corpus.
- False Positive Rate (FPR) on legitimate inputs.
- Time to detect + time to remediate.

Targets:
- Public: <5% ASR on public attacks, <1% on skilled adversaries.
- Internal high-stakes: <1% ASR, every incident triggers response.
- Autonomous: <0.1% or human-in-loop.

