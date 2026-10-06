# 🚨 LLM Security Operations — Ongoing Security

> *Security isn't a launch checklist. It's a daily operation. This section covers the running of security for a deployed LLM system.*

---

## Security Monitoring For LLMs (`security_monitoring_for_llms.py`)

**Extending Episode 11's observability to security.**

**What to monitor:**

**Input signals:**
- Injection detection classifier scores.
- Jailbreak attempt detection.
- Unusual query patterns per user.
- Encoded content in inputs (Base64, unusual language, high entropy).
- Volume spikes per user/IP.

**Model behavior signals:**
- Refusal rate (below normal = jailbreak may be working).
- Refusal rate (above normal = false positives, or attack in progress).
- Output length distribution.
- Content moderation flags per session.

**Output signals:**
- PII in output (unexpected).
- System-prompt-like content in output.
- Structured data in unexpected outputs.
- URLs to external unknown domains.
- Content that matches known exfil patterns.

**Tool call signals:**
- External tool call frequency.
- Anomalous tool parameters.
- Failed tool calls (permission denied — sign of attack).
- Rate of tool calls per session.

**Cross-user signals:**
- Same content appearing across many users (indirect injection spread).
- Coordinated attack from multiple accounts.
- Data appearing in wrong context.

**Alerting thresholds:**
- Static thresholds for known patterns.
- Anomaly detection for baseline drift.
- Multi-signal correlation (compound alerts).

**SIEM integration:**
- Ship all signals to security operations center.
- Correlate with other security events.
- Analyst review for high-severity alerts.

**Retention:**
- Detailed logs: 30-90 days.
- Aggregated metrics: 1+ year.
- Forensic archive for critical events.

---

## Incident Response For LLM Attacks (`incident_response_for_llm_attacks.py`)

**When something happens, what do you do?**

**IR playbook for LLM incidents:**

**Detection:**
- Alert triggered (monitoring detects attack).
- Or: user report / bug bounty.
- Or: external notification (researcher disclosure).

**Triage (0-60 minutes):**
- Confirm incident (not false positive).
- Assess severity (blast radius, ongoing?).
- Assemble response team.
- Notify appropriate leadership.

**Containment (0-4 hours):**
- Block attacker (rate limit, account suspension, IP block).
- Feature flag disable if affecting many users.
- Patch obvious vulnerabilities (temporary filters).
- Preserve forensic data.

**Eradication (4-72 hours):**
- Root cause analysis.
- Fix underlying vulnerability.
- Test the fix (verify attack no longer succeeds).
- Deploy fix with monitoring.

**Recovery (12-72 hours):**
- Restore normal operations.
- Un-block if attacker is contained.
- Verify no residual harm.

**Lessons learned (1-2 weeks):**
- Postmortem meeting.
- Document findings.
- Update playbooks.
- Update training data / red-team suite.
- Communicate to relevant stakeholders.

**Communication:**
- Internal: engineering, security, leadership.
- External: users (if data affected), regulators (if required), press (if public-facing).
- Timing: transparency vs operational security tradeoff.

**Regulatory obligations:**
- GDPR: 72-hour notification for personal data breach.
- HIPAA: 60-day notification.
- SEC: material cybersecurity incidents.
- State breach notification laws.

---

## Security Reviews For AI Features (`security_reviews_for_ai_features.py`)

**Every new feature reviewed.**

**Review triggers:**
- New feature that uses LLM.
- Change to existing LLM feature (prompt, tool set, model).
- New data source integrated.
- New third-party AI dependency.

**Review artifacts:**

**Threat model.**
- Assets: what data / systems / actions are involved?
- Adversaries: who might attack?
- Attack scenarios: how might they attack?
- Mitigations: what defenses are in place?
- Residual risk: what's accepted?

**Data flow diagram.**
- Where does user input come from?
- Where does it flow?
- Where does LLM output go?
- Where is sensitive data?

**Attack surface analysis.**
- Public vs internal.
- Authenticated vs anonymous.
- Read-only vs write.
- Tool access.

**Test results.**
- Red-team results.
- Automated attack suite.
- Manual penetration test.

**Sign-offs:**
- Security engineering: architecturally sound?
- ML engineering: model behavior understood?
- Compliance: regulatory requirements met?
- Product: business risk acceptable?

**Approval gates:**
- Low-risk features: security engineer sign-off.
- Medium-risk: security review board.
- High-risk: CISO or executive sign-off.

**Cadence:**
- Initial review before launch.
- Re-review on significant changes.
- Annual review of established features.

**Common failure modes:**
- Reviews skipped for velocity — technical debt accumulates.
- Reviews become paperwork — no meaningful assessment.
- Reviewers lack LLM expertise — miss LLM-specific issues.

---

## Compliance And LLM Security (`compliance_and_llm_security.py`)

**Building on Episode 8's governance.**

**Frameworks touching LLM security:**

**NIST AI RMF (Risk Management Framework):**
- Voluntary but influential.
- Structured approach to AI risk.
- Sections on security explicitly called out.

**EU AI Act (2024, enforced from 2025-2026):**
- Risk-tiered obligations.
- High-risk AI systems: extensive documentation, testing, monitoring.
- General-purpose AI (foundation models): specific obligations.
- Security requirements built in.

**ISO/IEC 42001 (2023):**
- AI management system standard.
- Includes security controls.
- Increasingly required for enterprise contracts.

**SOC 2 with AI supplement:**
- Trust criteria applied to AI systems.
- Security controls documented and audited.

**Industry-specific:**
- **HIPAA:** PHI in LLM context requires safeguards.
- **PCI-DSS:** payment card data in AI systems.
- **SOX:** financial reporting AI subject to controls.
- **FINRA:** financial services AI oversight.

**Practical implementation:**

**Documentation:**
- Model cards for every deployed model.
- Data cards for training/RAG data.
- Risk assessments per feature.
- Incident reports.

**Controls:**
- Access controls (who can deploy, edit prompts, access models).
- Change management (approval workflows).
- Audit logging (immutable, tamper-evident).
- Data handling per applicable regulations.

**Testing evidence:**
- Red-team reports.
- Security review sign-offs.
- Penetration test results.
- Continuous monitoring metrics.

**Regulatory reporting:**
- Data breach notifications.
- High-risk AI system registration (EU).
- Incident reports where required.

**Rule:** compliance is not security, but non-compliance blocks security investment. Meet the baseline; then exceed it where risk warrants.

---

## Vendor Security Assessment (`vendor_security_assessment.py`)

**Third-party AI in your stack.**

**Vendor categories:**
- Foundation model providers (OpenAI, Anthropic, Google, etc.).
- Vector DB providers.
- Prompt management platforms.
- Observability platforms.
- Fine-tuning services.
- Data annotation vendors.

**Assessment criteria:**

**Security posture:**
- SOC 2 Type II report (recent).
- ISO 27001 certification.
- Security whitepaper.
- Vulnerability disclosure program.

**Data handling:**
- Data residency (where is data stored?).
- Data retention (how long?).
- Data usage (is your data used for training?).
- Encryption in transit and at rest.
- Access controls on their side.

**Model security:**
- How do they defend against injection, jailbreak, extraction?
- Training data provenance.
- Model artifact security.
- Update / patch cadence.

**Operational:**
- Incident response process.
- Notification SLAs.
- Uptime and reliability.
- Sub-processors and their security.

**Contractual:**
- Data processing agreement (DPA).
- Business associate agreement (BAA) for HIPAA.
- SLA with security obligations.
- Right to audit.
- Termination and data return clauses.

**Ongoing:**
- Regular re-assessments (annually).
- Monitor security news for vendor incidents.
- Track vendor changes (acquisitions, ownership changes).

**Data governance:**
- **Data classification** determines what can go to which vendors.
- **Redaction / tokenization** before external services.
- **Zero-data-retention** tiers where available.
- **Regional deployment** for data residency.

**Red flags:**
- No security documentation.
- Vague privacy policy.
- Data used for their training with no opt-out.
- No SOC 2 or equivalent.
- History of security incidents without transparent response.

**Rule:** every third-party AI dependency inherits security responsibility. Assess before onboarding; monitor throughout use; have exit plans.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `security_monitoring_for_llms.py` | Extends Episode 11 |
| `incident_response_for_llm_attacks.py` | IR playbook for LLM incidents |
| `security_reviews_for_ai_features.py` | Pre-launch and ongoing |
| `compliance_and_llm_security.py` | Ties to Episode 8 |
| `vendor_security_assessment.py` | Third-party AI |

---

*Previous: [← Red-Teaming Methodology](../red_teaming_methodology/README.md) · Next: [A/B Testing Foundations →](../ab_testing_foundations/README.md)*  ·  *Back to [main README](../../README.md)*
