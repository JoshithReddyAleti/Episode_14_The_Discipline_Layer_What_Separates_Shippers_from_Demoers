# 🎯 Red-Teaming Methodology — Adversarial Evaluation As Practice

> *Running Garak once against a model isn't a red team. This section is how a real red-team program works — methodology, tools, reporting, and the org design that makes it stick.*

---

## Red-Teaming As Practice (`red_teaming_as_practice.py`)

**The distinction:**

**"We ran tests" — testing.**
- Static list of adversarial inputs.
- Automated pipeline runs them.
- Metrics captured.
- Necessary but not sufficient.

**"We have a red team" — practice.**
- Dedicated people trying to break the system.
- Creative, adversarial mindset.
- Findings go into product roadmap.
- Continuous cycle, not a one-time event.

**Real red teams:**
- Frontier labs (Anthropic, OpenAI, Google): 10-50+ dedicated red-teamers.
- Enterprise AI teams: 1-5 red-teamers.
- Small teams: shared responsibility with engineering.

**Red team objectives:**
- Identify vulnerabilities before adversaries.
- Test defense-in-depth (can they break each layer?).
- Measure attack success rate under skilled adversary.
- Feed findings into training data, guardrails, architecture.

**Red team ≠ security team.**
- Security engineers build defenses.
- Red team tries to break defenses.
- Adversarial collaboration.

**Bug bounty as force multiplier:**
- Public program for LLM-specific vulnerabilities.
- Payouts scaled by impact (data exfil > jailbreak > minor bypass).
- Anthropic, OpenAI, Google run bounties in 2026.

---

## Manual Red-Teaming (`manual_red_teaming.py`)

**Human creativity — irreplaceable.**

**Why manual matters:**
- Novel attack strategies come from humans.
- Automated tools test known patterns; humans invent new ones.
- Multi-turn, contextual attacks are hard to automate.
- Social engineering / creative framing beyond automated coverage.

**Manual red-team session structure:**

**1. Target definition.**
- Which feature / model / surface is under test?
- What are the goals of an attacker (extract, execute, harm)?

**2. Attacker persona.**
- Who is the attacker? Motivations? Skills?
- Different personas: script kiddie, adversarial researcher, motivated criminal, nation-state.

**3. Attack planning.**
- Hypothesize attacks likely to succeed.
- Prioritize by expected impact.
- Time-box each attempt.

**4. Execution.**
- Try attacks systematically.
- Log every attempt (success / partial / fail).
- Iterate on partial successes.

**5. Analysis.**
- Categorize successful attacks.
- Assess impact and blast radius.
- Recommend fixes.

**6. Reporting.**
- Formal report to engineering.
- Reproducible attack examples.
- Prioritized fix list.

**Session cadence:**
- Weekly focused sessions on new features.
- Quarterly deep-dive on core features.
- Post-incident review after any real attack.

**Skills required:**
- Understanding of LLM behavior.
- Creativity + adversarial mindset.
- Communication (write findings clearly).
- Ethics (handling sensitive discoveries responsibly).

---

## Automated Red-Teaming (`automated_red_teaming.py`)

**Scale attacks with algorithms.**

**Categories:**

**1. Attack templates.**
- Library of known attack patterns.
- Templated with variables (target topic, format).
- Fast, cheap, covers baseline.

**2. LLM-driven attack generation.**
- Attacker LLM generates variations.
- Iteratively refines based on target responses.
- Includes PAIR, TAP.

**3. Gradient-based attacks.**
- White-box (require gradients).
- Optimize adversarial suffixes.
- Includes GCG, AdvPrompter.

**4. Evolutionary attacks.**
- Population of attacks; genetic operations.
- Fitness = success rate on target.
- Discovers novel patterns.

**Automated pipeline:**
```
Attack library (curated + generated)
    ↓
Target LLM interaction (batched, async)
    ↓
Success detection (judge LLM or rules)
    ↓
Successful attacks catalogued
    ↓
Metrics reported (ASR by category)
    ↓
Findings feed engineering + retraining
```

**Cadence:**
- Continuous — every deploy runs the automated suite.
- Pre-launch — full suite before public release.
- Post-launch — monitoring for regressions.

**Cost:**
- Small suite (~100 attacks): $10-50 per run.
- Comprehensive (~10K attacks): $500-5000 per run.
- Continuous testing: budget item, comparable to other CI costs.

---

## Red-Teaming Tools (`red_teaming_tools.py`)

**The 2026 tool landscape:**

**Garak (NVIDIA):**
- Open-source, comprehensive scanner.
- Probes: many categories including injection, jailbreak, toxic content, hallucination, data leakage.
- CLI-first; integrates into CI.
- Growing rapidly in 2025-2026 as the go-to tool.

**PyRIT (Microsoft):**
- Framework for building red-teaming workflows.
- Orchestration for complex multi-turn attacks.
- Integrates with Azure AI Studio.

**Promptfoo:**
- LLM eval framework with red-teaming plugin.
- Test-driven approach: write tests, run against multiple models.
- Good for comparing model safety.

**LLM-Guard:**
- Runtime protection library.
- Doesn't red-team directly but exposes defenses to test.

**Rebuff:**
- Prompt injection detection library.
- Also a testing target.

**Custom tooling:**
- Most mature teams build internal red-team tools.
- Tailored to their attack surface.
- Integrated with their observability stack.

**Selection:**
- **Starting out:** Garak (broad coverage, low effort).
- **Growing:** PyRIT (orchestration for custom attacks).
- **Comparing models:** Promptfoo.
- **Enterprise:** custom + one of the above.

---

## Red-Team Reporting (`red_team_reporting.py`)

**Findings → fixes.**

**Report structure:**

**1. Executive summary.**
- Attack surface tested.
- Number of successful attacks.
- Severity distribution.
- Overall risk assessment.

**2. Findings (one per issue).**
- Description of the attack.
- Reproducible example (input → output).
- Assessed severity (Critical / High / Medium / Low).
- Impact and blast radius.
- Recommended fix.
- Reference to related CVE / OWASP category.

**3. Metrics.**
- Attack success rate by category.
- Trends vs previous reports.

**4. Recommendations.**
- Prioritized fix list.
- Longer-term architectural changes.
- Training data additions.

**5. Appendices.**
- Full attack corpus tested.
- Detailed logs.

**Severity criteria:**

**Critical:**
- Data exfil across users.
- Full system prompt leak with sensitive content.
- Unauthorized action with material real-world impact.
- Trigger for auto-rollback.

**High:**
- Single-user data exfil.
- Bypass of critical safety filters.
- Reproducible jailbreaks on well-known attacks.

**Medium:**
- Bypass of some content filters.
- System prompt reveal without material impact.
- Minor safety edge cases.

**Low:**
- Nuisance behavior.
- Content that violates style but not safety.

**Fix SLAs (typical):**
- Critical: fix within 24 hours.
- High: fix within 1 week.
- Medium: fix within sprint.
- Low: backlog.

---

## Red-Teaming Agents (`red_teaming_agents.py`)

**Agents are the hardest red-teaming target.**

**Why harder than single-shot LLM:**
- Multi-turn interactions expand attack surface.
- Tool use amplifies impact.
- State/memory can be poisoned.
- Cross-tool attacks compound.

**Agent-specific attack categories:**

**1. Tool weaponization.**
- Inject into agent context; make it use tools maliciously.
- Test: can attacker make agent send emails, execute code, transfer funds?

**2. Memory poisoning.**
- If agent has long-term memory, inject false facts.
- Test: can attacker make agent believe/act on incorrect info?

**3. Cross-user contamination.**
- In multi-tenant agents, can one user affect another's session?

**4. Recursion / loops.**
- Can attacker make agent infinitely loop, consume resources?

**5. Prompt escalation across steps.**
- Attack builds across multiple agent steps.

**Testing methodology:**
- Simulated agent environment.
- Attacker controls one input source (email, doc, web).
- Measure: what percentage of attacks result in unauthorized action?

**Defenses to validate:**
- Least-privilege tool grants working.
- Dual-LLM pattern effective.
- Human-in-the-loop for high-impact actions.
- Tool call review.

**2026 reality:** most agent red-teaming is manual. Automated agent-attack tools are emerging but immature.

---

## Red-Teaming Program Design (`red_teaming_program_design.py`)

**Building the function.**

**Roles:**
- **Red team lead** — sets strategy, priorities.
- **Red-team engineers** — do the testing.
- **Security liaison** — coordinates with security team.
- **Product liaison** — coordinates with product/engineering.

**Reporting structure:**
- Ideally independent from product engineering.
- Reports to CISO or head of AI safety.
- Not blocked or overridden by product velocity.

**Program elements:**

**1. Continuous automated testing.**
- Every deploy runs automated suite.
- Metrics tracked.

**2. Weekly manual sessions.**
- Focused on new features or high-risk areas.
- 4-8 hours per session.

**3. Quarterly campaigns.**
- Deep-dive on a specific surface.
- Multiple people, multiple days.
- Comprehensive report.

**4. Pre-launch reviews.**
- Any new feature undergoes red-team review before launch.
- Blocking gate for high-stakes features.

**5. Post-incident forensics.**
- Any real attack triggers deep investigation.
- Findings feed back into red-team methods.

**6. External engagement.**
- Bug bounty for LLM issues.
- Third-party red-team firms for periodic assessment.
- Public red-team competitions.

**Metrics for the program:**
- ASR (attack success rate) — should trend down over time.
- Time from finding to fix.
- Coverage — % of attack surface actively tested.
- New attack discovery rate.

**Common failure modes:**
- Red team without authority — findings ignored.
- Red team seen as "QA" — treated as blockers not partners.
- No dedicated headcount — spread across security/ML who don't do it.
- No tooling investment — manual-only doesn't scale.

**Rule:** a red-team program is a long-term investment. In 2026, any enterprise AI deployment without one is under-defended.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `red_teaming_as_practice.py` | Not just running tests |
| `manual_red_teaming.py` | Human creativity |
| `automated_red_teaming.py` | At scale |
| `red_teaming_tools.py` | Garak, PyRIT, promptfoo |
| `red_team_reporting.py` | Findings → fixes |
| `red_teaming_agents.py` | Agent-specific |
| `red_teaming_program_design.py` | Building the function |

---

*Previous: [← Model Supply Chain Security](../model_supply_chain_security/README.md) · Next: [LLM Security Operations →](../llm_security_operations/README.md)*  ·  *Back to [main README](../../README.md)*
