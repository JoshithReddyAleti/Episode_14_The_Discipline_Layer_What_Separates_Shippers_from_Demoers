# 🎛️ Prompt Management Platforms — Prompts At Scale

> *When you have 3 prompts, put them in a text file. When you have 300 across 40 features and 12 teams, you need a platform.*

---

## Prompt Management Requirements (`prompt_management_requirements.py`)

**What a prompt platform must do:**

**1. Versioning.**
- Every change tracked with semantic version + Git SHA.
- Rollback to any prior version.
- Diff between versions.

**2. Evaluation.**
- Run eval sets against a prompt version.
- Store scores tied to the version.
- Block deploys that regress metrics.

**3. Deployment.**
- Environments (dev/staging/prod).
- Approval workflows.
- Rollout controls (gradual, feature-flagged).

**4. Monitoring.**
- Which prompt version served this request?
- Quality metrics per version.
- Cost per version.

**5. Access control.**
- Who can edit? Who can deploy?
- Audit logs.

**6. Collaboration.**
- Non-engineers (PMs, designers) can iterate on prompts.
- Engineers approve prod deploys.
- Discussions and comments.

**7. Templating.**
- Variables, conditionals, includes.
- Reusable snippets across prompts.

**8. Multi-model support.**
- Same prompt runs across providers.
- Per-model tuning.

**9. Cost tracking.**
- Token usage per prompt per model.
- Budget alerts.

**10. Integration.**
- SDK for major languages.
- Feature flag integration.
- Analytics integration.

**Rule:** if you have 50+ prompts or 10+ contributors, you need a platform. Below that, prompts-in-Git usually suffices.

---

## Humanloop, Langfuse, PromptLayer (`humanloop_langfuse_promptlayer.py`)

**The 2026 landscape:**

**Humanloop:**
- **Focus:** enterprise; strong on prompt management + eval + feedback loops.
- **Strengths:** polished UI, RBAC, integrations, model-agnostic.
- **Weaknesses:** cost; enterprise-focused pricing.
- **When to pick:** enterprise environments with governance needs.

**Langfuse:**
- **Focus:** observability + prompt versioning + eval.
- **Strengths:** open-source (self-hostable), fast-moving, developer-friendly, integrated tracing.
- **Weaknesses:** UI less polished than Humanloop; younger.
- **When to pick:** developer-first teams; want self-hosting; already using open-source stack.

**PromptLayer:**
- **Focus:** prompt logging + versioning.
- **Strengths:** simple, cheap, well-documented.
- **Weaknesses:** less feature-rich than the above.
- **When to pick:** smaller teams starting out; simple needs.

**Others in the space:**
- **Portkey** — LLM gateway with prompt management.
- **Helicone** — observability-first, prompt features growing.
- **Vellum** — prompt IDE + management.
- **LangSmith (LangChain)** — integrated with LangChain apps.
- **Weights & Biases Prompts** — for teams already using W&B.

**Selection criteria:**
- Existing stack (already using LangChain? W&B?).
- Deployment model (SaaS vs self-hosted).
- Feature depth (evaluation, deployment, RBAC).
- Cost at scale.
- Vendor lock-in tolerance.

---

## Building A Prompt Platform (`building_a_prompt_platform.py`)

**DIY architecture — reference design:**

```
┌────────────────────────────────────────┐
│           UI (Next.js or similar)      │
│  - Prompt editor                       │
│  - Version history                     │
│  - Eval results                        │
│  - Deploy controls                     │
└────────────┬───────────────────────────┘
             │
┌────────────▼───────────────────────────┐
│          Prompt API (FastAPI)          │
│  - CRUD prompts                        │
│  - Manage versions                     │
│  - Trigger evals                       │
│  - Deploy to environments              │
└─────┬─────────┬──────────┬─────────────┘
      │         │          │
      ▼         ▼          ▼
┌───────┐  ┌────────┐  ┌──────────┐
│Postgres│  │Eval    │  │Deployment│
│Prompts │  │Runner  │  │Service   │
│Versions│  │(Celery)│  │(feature  │
│Deploys │  │        │  │ flags)   │
└───────┘  └────────┘  └──────────┘
      │         │          │
      └─────────┴──────────┘
                │
                ▼
┌────────────────────────────────────────┐
│         Application Services            │
│  Fetches active prompt via SDK          │
│  Logs requests with prompt version      │
└────────────────────────────────────────┘
```

**Core data model:**
```sql
CREATE TABLE prompts (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE prompt_versions (
    id UUID PRIMARY KEY,
    prompt_id UUID REFERENCES prompts(id),
    version VARCHAR NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_by VARCHAR,
    created_at TIMESTAMP,
    UNIQUE(prompt_id, version)
);

CREATE TABLE prompt_deployments (
    id UUID PRIMARY KEY,
    prompt_version_id UUID REFERENCES prompt_versions(id),
    environment VARCHAR NOT NULL,  -- dev, staging, prod
    active BOOLEAN,
    rollout_percent FLOAT,
    deployed_at TIMESTAMP,
    deployed_by VARCHAR
);

CREATE TABLE eval_runs (
    id UUID PRIMARY KEY,
    prompt_version_id UUID REFERENCES prompt_versions(id),
    eval_set_id VARCHAR,
    scores JSONB,
    ran_at TIMESTAMP
);
```

**SDK (Python client example):**
```python
class PromptClient:
    def get_prompt(self, name: str, environment: str = "prod") -> str:
        # Fetch active prompt version for name+environment
        # Cache locally for performance
        ...
    
    def log_usage(self, prompt_name: str, prompt_version: str, request_id: str, tokens: dict):
        # Async log for observability
        ...
```

**Build vs buy:**
- **Buy** when: <1 person-year to implement; features you need exist off-shelf; velocity matters.
- **Build** when: unique requirements (regulated environment, custom governance); already have platform team; want to avoid vendor lock-in.
- Most teams: buy first, build later if outgrown.

---

## Prompt CI/CD (`prompt_ci_cd.py`)

**Deploying prompts safely.**

**The pipeline:**

```
Developer edits prompt in dev environment
    ↓
Commit to Git (prompt YAML or text file)
    ↓
CI kicks in:
  - Lint prompt (format, forbidden patterns)
  - Run eval set against candidate prompt
  - Compare to current prod
  - Fail build if metrics regress
    ↓
PR review
    ↓
Merge to main → deploy to staging
    ↓
Manual QA / canary in staging
    ↓
Promotion to prod:
  - Feature-flag gradual rollout (1% → 10% → 50% → 100%)
  - Monitor production metrics
  - Automated rollback if guardrails trigger
    ↓
Full rollout
    ↓
Version tagged in registry
```

**Lint checks:**
- No hard-coded secrets or API keys.
- No PII placeholders leaking real data.
- Format sanity (proper escaping, no accidental prompt injection).
- Length within budget.
- Required sections present (safety, format instructions).

**Eval-based gates:**
- Golden set accuracy >= current - 1%.
- No regression on adversarial set.
- Cost within budget (compression check).
- Latency within budget.

**Feature-flag rollout:**
- LaunchDarkly, Statsig, or homegrown.
- Percentage-based routing.
- Automated rollback triggers on error rate or metric drop.

**Rollback strategy:**
- Every prompt version stored in registry (immutable).
- Rollback = flip the feature flag to previous version.
- Should complete in <60 seconds.

**Prompt vs model deploys:**
- Prompt deploys: fast (registry lookup), easy to rollback.
- Model deploys: slower (weight loading), harder to rollback.
- Same rigor either way.

---

## Prompt Governance (`prompt_governance.py`)

**Who's allowed to change what?**

**Roles:**
- **Author** — anyone with commit access; can propose changes via PR.
- **Reviewer** — team lead, prompt specialist; approves PRs.
- **Deployer** — platform/SRE role; approves prod deploys.
- **Admin** — sets governance rules, manages roles.

**Environment gates:**
- **Dev:** any author, no approval.
- **Staging:** author + reviewer.
- **Prod:** author + reviewer + deployer + eval pass.

**Special content requiring extra approval:**
- Safety-sensitive prompts (content moderation, medical, legal).
- Prompts used by many downstream features.
- Prompts with high traffic (top 10 by volume).

**Audit logging:**
- Every change tracked.
- Who edited what, when.
- Retention: at least 1 year, often 7+ for regulated industries.

**Change management processes (larger orgs):**
- **RFC for major prompt changes.** Describe intent, expected impact, rollback plan.
- **Prompt review committee** — cross-functional review for high-impact prompts.
- **Postmortems** — after incidents, prompt change traced and lessons captured.

**Regulatory considerations:**
- **GDPR/CCPA:** prompts that shape data handling need documentation.
- **HIPAA:** medical-context prompts need extra review.
- **SOC 2 / ISO 27001:** audit trails and access controls required.

**Common failure modes:**
- Prompts changed with no review → regressions ship.
- Governance too heavy → engineers work around it, shadow prompts appear.
- Governance too light → high-stakes prompts changed carelessly.

**Rule:** governance should scale to the stakes. Low-risk features: light-touch. High-risk features (medical advice, financial recommendations, safety filters): heavy governance.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `prompt_management_requirements.py` | What a platform must do |
| `humanloop_langfuse_promptlayer.py` | The 2026 landscape |
| `building_a_prompt_platform.py` | DIY reference design |
| `prompt_ci_cd.py` | Deploy prompts safely |
| `prompt_governance.py` | Approvals, audit |

---

*Previous: [← Advanced Prompting Patterns](../advanced_prompting_patterns/README.md) · Next: [LLM Security Foundations →](../llm_security_foundations/README.md)*  ·  *Back to [main README](../../README.md)*
