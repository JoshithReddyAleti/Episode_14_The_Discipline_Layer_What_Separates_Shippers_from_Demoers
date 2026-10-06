# OWASP LLM Top 10 — Deep Walkthrough

## LLM01 — Prompt Injection
The dominant attack. Direct (user input) and indirect (retrieved content). Mitigate: input filters, spotlighting, dual-LLM, output filters, least-privilege tools.

## LLM02 — Sensitive Information Disclosure
Model reveals PII, credentials, IP. Mitigate: minimize context, output filters, redaction.

## LLM03 — Supply Chain Vulnerabilities
Compromised models, dependencies, training data. Mitigate: model signing, safetensors, verified sources.

## LLM04 — Data and Model Poisoning
Malicious training data. Mitigate: validation, provenance, contamination detection.

## LLM05 — Improper Output Handling
LLM output used unsafely (SQL/shell/HTML). Mitigate: treat all output as untrusted.

## LLM06 — Excessive Agency
Agent has more tool permissions than needed. Mitigate: least privilege, human-in-loop.

## LLM07 — System Prompt Leakage
System prompt exposed. Mitigate: don't put secrets in prompt, monitor for extraction.

## LLM08 — Vector and Embedding Weaknesses
Attacks on vector DBs, retrieval poisoning. Mitigate: content vetting, access controls, adversarial testing.

## LLM09 — Misinformation
Hallucinated content presented as fact. Mitigate: grounding, verification, user disclosure.

## LLM10 — Unbounded Consumption
Cost/resource exhaustion via crafted inputs. Mitigate: rate limits, token budgets, output length limits.

## How to use this list

- Map every LLM feature's risks to categories.
- Document mitigations per feature per category.
- Identify gaps → risk register.
- Every gap is either mitigated or accepted (documented decision).

