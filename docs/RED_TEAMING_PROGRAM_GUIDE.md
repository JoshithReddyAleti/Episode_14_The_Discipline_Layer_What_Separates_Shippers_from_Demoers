# Red-Teaming Program Guide

## The distinction

**"We ran tests" ≠ "We have a red team."**

Tests are automated, static. Red teams are humans with adversarial intent.

## Program elements

- **Continuous automated testing** — every deploy runs the automated suite (Garak, PyRIT, custom).
- **Weekly manual sessions** — 4-8 hours focused on new features.
- **Quarterly campaigns** — deep dives on specific surfaces.
- **Pre-launch reviews** — blocking gate for high-stakes features.
- **Post-incident forensics** — learnings feed back into methods.
- **Bug bounty** — external force multiplier.
- **Third-party assessment** — annual by external firm.

## Team composition

- Red team lead — sets strategy.
- Red-team engineers — do the testing.
- Security liaison — coordinates with sec eng.
- Product liaison — coordinates with product/eng.

Reports independently from product engineering. Ideally to CISO or head of AI safety.

## Tooling stack

- **Garak** — comprehensive scanner (broad coverage).
- **PyRIT** — orchestration for custom attacks.
- **Promptfoo** — LLM eval + red-team plugin.
- **Custom** — internal tools for domain-specific attacks.

## Reporting

Severity levels:
- **Critical:** cross-user data exfil, system prompt with sensitive content, unauthorized real-world action. Fix SLA: 24h.
- **High:** single-user data exfil, safety filter bypass, reproducible jailbreaks. Fix SLA: 1 week.
- **Medium:** minor bypass, non-material system prompt reveal. Fix SLA: sprint.
- **Low:** nuisance. Fix SLA: backlog.

## Metrics

- ASR trending down over time.
- Coverage % of attack surface actively tested.
- Time from finding to fix.
- New attack discovery rate.

