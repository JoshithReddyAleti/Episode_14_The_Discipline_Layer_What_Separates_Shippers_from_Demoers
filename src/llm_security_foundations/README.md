# 🛡️ LLM Security Foundations

> *"LLM security" is not "software security with an LLM sticker." It's a discipline of its own — the threat model, attack surface, and defense stack are different. This section is the foundation.*

---

## The LLM Threat Model (`the_llm_threat_model.py`)

**What are the actual risks?**

**1. Data leakage.**
- LLM emits training data verbatim (memorization attacks).
- LLM emits system prompt or context in output (extraction).
- LLM sends data outbound via tools (exfiltration).
- Retrieved context is exposed to the user beyond intent.

**2. Unauthorized actions.**
- Injection tricks the agent into executing unwanted operations.
- Confused deputy — LLM performs an action the user isn't authorized for.
- Cross-user contamination in multi-tenant systems.

**3. Content harms.**
- Model produces harmful content (violence, illegal, harassing).
- Model produces incorrect content presented as fact (hallucination in critical domains).
- Manipulation of users via generated content.

**4. Reputation and compliance.**
- Model outputs violating brand voice or company policy.
- Model advice creating legal liability (unlicensed practice, financial harm).
- Failure to comply with content regulation.

**5. Availability.**
- Model context saturation via injected content (context flood attacks).
- Amplification of costs via crafted inputs (long generations, tool calls).
- DoS through resource-expensive queries.

**6. Model supply chain.**
- Loaded model has backdoors or was compromised.
- Malicious pickle files in model weights.
- Tampered tokenizer or config.

**7. Interaction with legacy security concerns.**
- LLM outputs used as input to SQL / shell / code execution.
- LLM-facilitated phishing.
- LLM as an attack tool (writing exploits).

**Threat actors:**
- **End users** trying to bypass guardrails.
- **Malicious insiders** with system access.
- **Third parties** whose content is retrieved.
- **Nation-state or organized attackers** with specific goals.

**Rule:** every threat model must map: **who** wants **what**, **how** they might achieve it, **what** defenses reduce risk, and **what** residual risk is accepted.

---

## LLM Attack Surfaces (`llm_attack_surfaces.py`)

**Where attackers actually hit.**

**1. The user-facing prompt.**
- Direct injection attempts.
- Jailbreaks.
- Social engineering of the model.

**2. Retrieved content (RAG).**
- **Indirect injection** — attacker publishes content that will be retrieved.
- Content includes injection payload.
- LLM treats the payload as instructions.
- **The dominant attack surface in 2025-2026.**

**3. Tool outputs.**
- LLM calls a tool; tool returns malicious data.
- LLM treats tool output as instruction.
- Cascading actions triggered.

**4. System prompt / hidden context.**
- Extraction attempts — reveal the system prompt via prompt injection.
- System prompt often contains sensitive info (API keys, patterns, policies).

**5. Fine-tuning data.**
- Poisoned examples inserted into training data.
- Model behaves normally on most inputs, harmful on triggers.

**6. Model weights / supply chain.**
- Backdoored base model.
- Malicious deserialization in .pkl files.

**7. Integration endpoints.**
- Auth token misuse.
- API abuse without rate limits.
- Injection into logs or downstream systems.

**8. Observability layer.**
- Logging PII to less-protected systems.
- Trace data used maliciously.

**Attack surface prioritization (2026):**
- Indirect injection (RAG): most exploited.
- Direct injection: high volume, often defended.
- Data extraction: medium volume, high impact.
- Supply chain: low volume, catastrophic impact.

---

## OWASP LLM Top 10 (`owasp_llm_top_10.py`)

**The OWASP LLM Top 10 (2025 version) walkthrough:**

**LLM01 — Prompt Injection.**
- Direct and indirect.
- Mitigation: input filtering, spotlighting, dual-LLM, output filtering.

**LLM02 — Sensitive Information Disclosure.**
- Model reveals PII, credentials, IP from training or context.
- Mitigation: content filters, output scanning, redaction, minimize context.

**LLM03 — Supply Chain Vulnerabilities.**
- Compromised base models, dependencies, training data.
- Mitigation: model signing, verified sources, safetensors.

**LLM04 — Data and Model Poisoning.**
- Malicious training or fine-tuning data.
- Mitigation: data validation, provenance tracking, contamination detection.

**LLM05 — Improper Output Handling.**
- LLM output used unsafely (SQL, shell, HTML rendering).
- Mitigation: treat all output as untrusted, validate/escape before use.

**LLM06 — Excessive Agency.**
- Agent has more tool permissions than needed.
- Mitigation: least privilege, human-in-the-loop for high-impact actions.

**LLM07 — System Prompt Leakage.**
- System prompt (with policies, keys, patterns) exposed.
- Mitigation: minimize sensitive content in system prompt, don't rely on secrecy.

**LLM08 — Vector and Embedding Weaknesses.**
- Attacks on vector DBs, embedding manipulation, retrieval poisoning.
- Mitigation: content vetting, access controls, adversarial testing.

**LLM09 — Misinformation.**
- Hallucinated or biased content presented as fact.
- Mitigation: grounding via retrieval, verification, user disclosure.

**LLM10 — Unbounded Consumption.**
- Cost or resource exhaustion via crafted inputs.
- Mitigation: rate limits, token budgets, output length limits.

**Each item has:**
- Attack scenarios.
- Concrete mitigations.
- Detection strategies.
- Reference to research and known incidents.

**Rule:** every LLM feature should map its risks to OWASP LLM Top 10 categories. Missing coverage on any = documented risk decision.

---

## Security vs Safety (`security_vs_safety.py`)

**Two different disciplines. Often confused.**

**Security:**
- Adversary trying to break the system.
- Protects against unauthorized access, actions, disclosure.
- Traditional infosec disciplines applied to LLMs.
- Metrics: attacks blocked, incidents detected, mean time to detect.

**Safety:**
- User potentially harmed by well-intentioned system.
- Protects against harmful outputs, biased outputs, incorrect outputs in high-stakes contexts.
- More common in alignment research.
- Metrics: harm-classifier rates, human review flag rates, downstream harm indicators.

**Overlap:**
- Jailbreaking (security concern) enabling harmful output (safety concern).
- Injection (security) inducing biased responses (safety).

**Different tooling:**
- Security: WAFs, input filters, sandboxing, red teams.
- Safety: content classifiers, RLHF/RLAIF training, constitutional AI, human review.

**Different orgs:**
- Security often owned by security engineering.
- Safety often owned by ML/AI or policy teams.
- Collaboration critical; disjoint programs miss cross-cutting issues.

**Rule:** security is against adversaries. Safety is against harm. You need both, and they must coordinate.

---

## Secure Development Lifecycle For AI (`secure_development_lifecycle_ai.py`)

**AI SDL — the practices:**

**Design phase:**
- Threat model per feature.
- Data flow diagrams showing PII / sensitive content flow.
- Trust boundaries identified.
- Security review before implementation.

**Development phase:**
- Prompt engineering with safety patterns.
- Input validation on all LLM inputs.
- Output validation on all LLM outputs.
- Defense-in-depth (multiple layers).
- Least-privilege tool grants.
- Testing includes injection, jailbreak, extraction.

**Integration phase:**
- Security testing (red team).
- Regression testing on known attacks.
- Performance testing under attack (DoS resilience).
- Third-party security review for high-stakes features.

**Deployment phase:**
- Gradual rollout with monitoring.
- Auto-rollback triggers on security metrics.
- Incident response ready.

**Operations phase:**
- Continuous monitoring.
- Regular red team exercises.
- Bug bounty for LLM vulnerabilities.
- Threat intelligence (new attack patterns).

**Retirement phase:**
- Data scrubbing.
- Model deprovisioning.
- Audit log retention per policy.

**Team composition:**
- **Security engineer** who understands LLMs.
- **ML/AI engineer** who understands security.
- **Product security reviewer** for cross-cutting concerns.
- **Red team** — internal or external.

**Common failures:**
- Security review happens after launch instead of before.
- No LLM-specific attack knowledge in the security team.
- Safety and security programs run in isolation.
- No red team investment.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `the_llm_threat_model.py` | What's actually at risk |
| `llm_attack_surfaces.py` | Where attackers hit |
| `owasp_llm_top_10.py` | Full walkthrough |
| `security_vs_safety.py` | Different disciplines |
| `secure_development_lifecycle_ai.py` | The AI SDL |

---

*Previous: [← Prompt Management Platforms](../prompt_management_platforms/README.md) · Next: [Prompt Injection Deep Dive →](../prompt_injection_deep_dive/README.md)*  ·  *Back to [main README](../../README.md)*
