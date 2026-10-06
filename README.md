# 🎯 The Discipline Layer — What Separates Shippers From Demoers

> **Episode 14 of the [AI Engineering Roadmap 2026](https://www.linkedin.com/newsletters/ai-engineering-roadmap-2026-7467249724752908288/) Newsletter Series**
>
> *"Episodes 1-13 taught you how to build AI systems, train models, and serve them at scale. This episode is about the disciplines that determine whether your system survives contact with reality: how you handle data, how you engineer prompts, how you defend the system, and how you know your changes actually work."*

---

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Vector DBs](https://img.shields.io/badge/Vector_DBs-HNSW/IVF/PQ-EE4C2C?style=flat-square)
![DSPy](https://img.shields.io/badge/DSPy-Optimization-8A2BE2?style=flat-square)
![Security](https://img.shields.io/badge/OWASP_LLM-Top_10-DA1F26?style=flat-square)
![Stats](https://img.shields.io/badge/A%2FB_Testing-Statistical-2ECC40?style=flat-square)
![Episode](https://img.shields.io/badge/Episode-14-534AB7?style=flat-square)

**[📖 Newsletter](https://www.linkedin.com/newsletters/ai-engineering-roadmap-2026-7467249724752908288/) · [⬅️ Episode 13](https://github.com/JoshithReddyAleti/Episode_13_Fine_Tuning_and_Multimodal_The_Training_Layer) · [🗺️ Roadmap](docs/ROADMAP.md)**

</div>

---

## 🎯 What This Episode Is About

Four disciplines. Each is a specialty on its own. Together they are what separates AI engineers who **ship** systems from engineers who build **demos**.

### Part A — Data Engineering For AI (7 sections)
Vector DB internals deep enough to actually choose and tune (HNSW math, IVF-PQ, quantization, disk-ANN, sharding, hybrid search). Data versioning as a first-class practice (DVC, lakeFS, Delta/Iceberg, lineage). Deduplication at petabyte scale (exact, MinHash/LSH, semantic). Contamination detection so your eval numbers are actually valid. Synthetic data as a discipline. Data pipelines that survive daily reindexing.

### Part B — Prompt Engineering As Engineering (8 sections)
Prompts as code (versioned, tested, deployed). DSPy paradigm — programming instead of prompting, compilation with optimizers. TextGrad and prompt optimization as gradient descent over text. Structured decoding down to grammar internals (Outlines FSM, XGrammar, LMFormatEnforcer, LLGuidance). Prompt compression (LLMLingua) to buy back context and cost. Meta-prompting. Advanced patterns beyond CoT — ToT, GoT, PoT, self-consistency, CoVe, skeleton-of-thought. Prompt management platforms.

### Part C — LLM Security In Depth (8 sections)
OWASP LLM Top 10 as a walkthrough, not a checklist. Prompt injection deep dive with taxonomy (direct, indirect, via docs, via tool output, multi-turn). Defense stack (spotlighting, dual-LLM, instruction hierarchy, sandboxing, least-privilege agents). Data exfiltration attacks and detection. Jailbreaking landscape (role-play, obfuscation, many-shot, automated PAIR/TAP). Model supply-chain security (pickle risks, safetensors, signing, provenance). Red-teaming as a practice with tools (Garak, PyRIT, promptfoo). Security operations.

### Part D — A/B Testing On Stochastic Systems (8 sections)
Statistical foundations (power, MDE, multiple testing, variance reduction/CUPED). Experiment design for LLMs (randomization units, stratification, interference). Running experiments (prompt A/B, model A/B, RAG A/B, agent A/B, shadow testing). Analyzing results (segmentation, novelty/primacy, Bayesian vs frequentist). Rollout strategies (ring deployment, canary analysis, automated rollback). Causal inference when A/B isn't possible. Experimentation platforms at scale.

**By the end:** you can architect a production RAG stack tuned for your recall/QPS budget; build a prompt engineering pipeline with DSPy; run a red-team program with real tools; design and analyze a statistically-sound A/B test on an LLM feature; and defend the system against injection, exfiltration, and jailbreak attacks.

---

## 🏗️ The Repo Structure

```
Episode_14_The_Discipline_Layer_What_Separates_Shippers_from_Demoers/
│
├── README.md                                 # This file
│
├── src/                                      # 31 deep-dive sections + utils
│   │
│   │  ═══════════════ PART A: DATA ENGINEERING FOR AI ═══════════════
│   │
│   ├── data_engineering_foundations/         # Why data eng for AI is different
│   ├── vector_db_internals/                  # HNSW, IVF, PQ, quantization deep
│   ├── data_versioning/                      # DVC, lakeFS, Delta, Iceberg
│   ├── deduplication_at_scale/               # Exact, MinHash/LSH, semantic
│   ├── contamination_detection/              # Test-set leakage detection
│   ├── synthetic_data_engineering/           # As a discipline
│   ├── data_pipelines_for_ai/                # The plumbing
│   │
│   │  ═══════════════ PART B: PROMPT ENGINEERING AS ENGINEERING ═══════════════
│   │
│   ├── prompt_engineering_foundations/       # Prompts as code
│   ├── dspy_deep_dive/                       # Programming instead of prompting
│   ├── textgrad_and_prompt_optimization/     # Gradient-based prompting
│   ├── structured_decoding_deep_dive/        # Outlines, XGrammar, LMFE, LLGuidance
│   ├── prompt_compression/                   # LLMLingua family
│   ├── meta_prompting/                       # Prompts about prompts
│   ├── advanced_prompting_patterns/          # ToT, GoT, PoT, CoVe, SoT
│   ├── prompt_management_platforms/          # At-scale prompt ops
│   │
│   │  ═══════════════ PART C: LLM SECURITY IN DEPTH ═══════════════
│   │
│   ├── llm_security_foundations/             # OWASP LLM Top 10, threat model
│   ├── prompt_injection_deep_dive/           # The dominant attack
│   ├── injection_defenses/                   # Defense stack
│   ├── data_exfiltration/                    # Getting data out
│   ├── jailbreaking/                         # Around alignment
│   ├── model_supply_chain_security/          # Trust the model
│   ├── red_teaming_methodology/              # Adversarial evaluation
│   ├── llm_security_operations/              # Ongoing security
│   │
│   │  ═══════════════ PART D: A/B TESTING ON STOCHASTIC SYSTEMS ═══════════════
│   │
│   ├── ab_testing_foundations/               # Why LLM A/B is harder
│   ├── statistical_foundations/              # Power, MDE, corrections
│   ├── experiment_design_for_llms/           # Randomization, stratification
│   ├── running_experiments/                  # Execution across LLM changes
│   ├── analyzing_experiments/                # Making sense of results
│   ├── rollout_strategies/                   # Deploying winners safely
│   ├── causal_inference_for_ai/              # When A/B isn't possible
│   ├── ab_testing_at_scale/                  # Enterprise experimentation
│   │
│   └── utils/                                # Shared utilities
│       ├── stats_utils.py                    # Power calcs, MDE, CIs
│       ├── security_utils.py                 # Injection detection, filters
│       └── prompt_utils.py                   # Versioning, compression, templates
│
├── discipline_examples/                      # 11 end-to-end runnable labs
│   ├── hnsw_tuning_workshop/                 # Recall vs QPS trade-offs
│   ├── deduplication_pipeline/               # MinHash at scale
│   ├── contamination_detector/               # Full detection pipeline
│   ├── dspy_optimized_pipeline/              # Compile beats manual
│   ├── llmlingua_compression_demo/           # Cost savings measured
│   ├── outlines_structured_generation/       # 100% valid JSON
│   ├── red_team_lab/                         # Garak + PyRIT setup
│   ├── injection_defense_stack/              # Dual-LLM pattern live
│   ├── prompt_ab_testing_framework/          # End-to-end
│   ├── model_ab_testing_platform/            # Compare 3 models
│   └── enterprise_experimentation_ref/       # Reference architecture
│
├── docs/                                     # 20 topical deep-dive docs
├── examples/                                 # 20 focused learning scripts
├── tests/                                    # Pytest suite
├── benchmarks/                               # Reproducible benchmarks
├── infrastructure/                           # K8s, Terraform, monitoring
├── .github/                                  # CI/CD, issue templates
├── .env.example
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── CONTRIBUTING.md
├── CHANGELOG.md
├── SECURITY.md
└── LICENSE
```

---

## 🧭 Part A — Data Engineering For AI (7 sections)

| Section | What It Owns |
|---|---|
| [`src/data_engineering_foundations/`](src/data_engineering_foundations/README.md) | Why AI data is different · data as the product · the AI data lifecycle · org patterns |
| [`src/vector_db_internals/`](src/vector_db_internals/README.md) | Storage · ANN vs exact · flat/HNSW/IVF-PQ · PQ/SQ/BQ · disk-ANN · hybrid BM25+vector · sharding · benchmarking · cost model |
| [`src/data_versioning/`](src/data_versioning/README.md) | Why version · DVC · lakeFS · Delta/Iceberg · snapshots · lineage · reproducibility workflow |
| [`src/deduplication_at_scale/`](src/deduplication_at_scale/README.md) | Why dedup · exact · MinHash/LSH · semantic · document + chunk-level · petabyte pipeline · evaluation |
| [`src/contamination_detection/`](src/contamination_detection/README.md) | Overlap detection · embedding-based · benchmark contamination · canary strings · reporting |
| [`src/synthetic_data_engineering/`](src/synthetic_data_engineering/README.md) | When it wins · quality metrics · pipelines · LLM-generated · augmentation · domain · evaluation |
| [`src/data_pipelines_for_ai/`](src/data_pipelines_for_ai/README.md) | Batch vs streaming · doc processing · incremental indexing · CDC · validation · orchestration · observability |

## 🎨 Part B — Prompt Engineering (8 sections)

| Section | What It Owns |
|---|---|
| [`src/prompt_engineering_foundations/`](src/prompt_engineering_foundations/README.md) | Prompting as discipline · the loop · versioning · eval at scale · org patterns |
| [`src/dspy_deep_dive/`](src/dspy_deep_dive/README.md) | The paradigm · signatures · modules · optimizers · metrics · compilation · vs manual · production |
| [`src/textgrad_and_prompt_optimization/`](src/textgrad_and_prompt_optimization/README.md) | TextGrad · APE · OPRO · PromptBreeder · optimization pipelines |
| [`src/structured_decoding_deep_dive/`](src/structured_decoding_deep_dive/README.md) | JSON mode internals · Outlines · Guidance · XGrammar · LMFormatEnforcer · grammar-based · Instructor · LLGuidance · cost |
| [`src/prompt_compression/`](src/prompt_compression/README.md) | LLMLingua · LongLLMLingua · Selective Context · eval · vs summarization · in production |
| [`src/meta_prompting/`](src/meta_prompting/README.md) | Patterns · LLMs writing prompts · self-reflection · constitutional · pitfalls |
| [`src/advanced_prompting_patterns/`](src/advanced_prompting_patterns/README.md) | ToT · GoT · PoT · self-consistency · CoVe · SoT · analogical · pattern selection |
| [`src/prompt_management_platforms/`](src/prompt_management_platforms/README.md) | Requirements · Humanloop/Langfuse/PromptLayer · DIY · CI/CD · governance |

## 🔐 Part C — LLM Security In Depth (8 sections)

| Section | What It Owns |
|---|---|
| [`src/llm_security_foundations/`](src/llm_security_foundations/README.md) | Threat model · attack surfaces · OWASP LLM Top 10 · security vs safety · SDLC |
| [`src/prompt_injection_deep_dive/`](src/prompt_injection_deep_dive/README.md) | Direct · indirect · via docs · via tools · multi-turn · taxonomy · impact |
| [`src/injection_defenses/`](src/injection_defenses/README.md) | Input filtering · spotlighting · dual-LLM · instruction hierarchy · output filter · sandboxing · least-privilege agents · layers · effectiveness |
| [`src/data_exfiltration/`](src/data_exfiltration/README.md) | Via markdown · via tools · side channels · training data extraction · system prompt extraction · detection · prevention |
| [`src/jailbreaking/`](src/jailbreaking/README.md) | Taxonomy · role-play · obfuscation · many-shot · automated (PAIR/TAP) · detection · robust alignment |
| [`src/model_supply_chain_security/`](src/model_supply_chain_security/README.md) | Malicious weights · backdoors · pickle · signing/verification · safetensors · provenance |
| [`src/red_teaming_methodology/`](src/red_teaming_methodology/README.md) | As practice · manual · automated · tools (Garak, PyRIT, promptfoo) · reporting · agent red-team · program design |
| [`src/llm_security_operations/`](src/llm_security_operations/README.md) | Security monitoring · incident response · security reviews · compliance · vendor assessment |

## 📊 Part D — A/B Testing (8 sections)

| Section | What It Owns |
|---|---|
| [`src/ab_testing_foundations/`](src/ab_testing_foundations/README.md) | Why LLM A/B is harder · lifecycle · vs offline eval · metrics · maturity |
| [`src/statistical_foundations/`](src/statistical_foundations/README.md) | Hypothesis testing · Type I/II · power · calcs · sample size · effect size · MDE · multiple testing · CUPED |
| [`src/experiment_design_for_llms/`](src/experiment_design_for_llms/README.md) | Metrics · randomization units · stratification · traffic allocation · holdout · interference · pre-registration |
| [`src/running_experiments/`](src/running_experiments/README.md) | Platforms · feature flags · prompt A/B · model A/B · RAG A/B · agent A/B · shadow testing |
| [`src/analyzing_experiments/`](src/analyzing_experiments/README.md) | Data · handling variance · segmentation · novelty/primacy · Bayesian vs frequentist · CIs · reports |
| [`src/rollout_strategies/`](src/rollout_strategies/README.md) | Gradual · ring · rollback triggers · prompt vs model rollout · canary analysis · post-launch monitoring |
| [`src/causal_inference_for_ai/`](src/causal_inference_for_ai/README.md) | When A/B fails · observational · quasi-experiments · counterfactual · toolkits |
| [`src/ab_testing_at_scale/`](src/ab_testing_at_scale/README.md) | Platform design · metric stores · governance · democratization · learnings libraries |

---

## 📁 Discipline Examples — End-to-End Runnable Labs

| Lab | What It Demonstrates |
|---|---|
| [`discipline_examples/hnsw_tuning_workshop/`](discipline_examples/hnsw_tuning_workshop/) | Recall@K vs QPS trade-off tuning M, efConstruction, efSearch |
| [`discipline_examples/deduplication_pipeline/`](discipline_examples/deduplication_pipeline/) | MinHash + LSH at scale on ~10M docs |
| [`discipline_examples/contamination_detector/`](discipline_examples/contamination_detector/) | Full pipeline: n-gram + embedding + canary detection |
| [`discipline_examples/dspy_optimized_pipeline/`](discipline_examples/dspy_optimized_pipeline/) | Compile a DSPy program; measure vs manual prompt |
| [`discipline_examples/llmlingua_compression_demo/`](discipline_examples/llmlingua_compression_demo/) | Cost savings + quality measurement on real prompts |
| [`discipline_examples/outlines_structured_generation/`](discipline_examples/outlines_structured_generation/) | 100% schema-valid JSON via FSM constrained decoding |
| [`discipline_examples/red_team_lab/`](discipline_examples/red_team_lab/) | Garak + PyRIT + promptfoo end-to-end |
| [`discipline_examples/injection_defense_stack/`](discipline_examples/injection_defense_stack/) | Dual-LLM + spotlighting + output filter live |
| [`discipline_examples/prompt_ab_testing_framework/`](discipline_examples/prompt_ab_testing_framework/) | Full framework with power calc + rollout |
| [`discipline_examples/model_ab_testing_platform/`](discipline_examples/model_ab_testing_platform/) | Compare 3 models with statistically valid design |
| [`discipline_examples/enterprise_experimentation_ref/`](discipline_examples/enterprise_experimentation_ref/) | Reference architecture for org-wide experimentation |

---

## 📚 Documentation (20 Deep-Dive Docs)

- **Overview:** [`docs/DISCIPLINE_LAYER_OVERVIEW.md`](docs/DISCIPLINE_LAYER_OVERVIEW.md)
- **Part A:** [`DATA_ENGINEERING_TAXONOMY`](docs/DATA_ENGINEERING_TAXONOMY.md) · [`VECTOR_DB_SELECTION_DEEP`](docs/VECTOR_DB_SELECTION_DEEP.md) · [`DATA_VERSIONING_GUIDE`](docs/DATA_VERSIONING_GUIDE.md) · [`DEDUP_PLAYBOOK`](docs/DEDUP_PLAYBOOK.md)
- **Part B:** [`PROMPT_ENGINEERING_TAXONOMY`](docs/PROMPT_ENGINEERING_TAXONOMY.md) · [`DSPY_ADOPTION_GUIDE`](docs/DSPY_ADOPTION_GUIDE.md) · [`STRUCTURED_DECODING_COMPARISON`](docs/STRUCTURED_DECODING_COMPARISON.md) · [`PROMPT_COMPRESSION_GUIDE`](docs/PROMPT_COMPRESSION_GUIDE.md)
- **Part C:** [`OWASP_LLM_TOP_10_DEEP`](docs/OWASP_LLM_TOP_10_DEEP.md) · [`INJECTION_DEFENSE_PLAYBOOK`](docs/INJECTION_DEFENSE_PLAYBOOK.md) · [`RED_TEAMING_PROGRAM_GUIDE`](docs/RED_TEAMING_PROGRAM_GUIDE.md)
- **Part D:** [`AB_TESTING_LLMS_PLAYBOOK`](docs/AB_TESTING_LLMS_PLAYBOOK.md) · [`STATISTICAL_POWER_FOR_LLMS`](docs/STATISTICAL_POWER_FOR_LLMS.md) · [`ROLLOUT_STRATEGIES_GUIDE`](docs/ROLLOUT_STRATEGIES_GUIDE.md)
- **Cross-cutting:** [`CONCEPTS`](docs/CONCEPTS.md) · [`INTERVIEW_PREP`](docs/INTERVIEW_PREP.md) · [`DECISION_FRAMEWORK`](docs/DECISION_FRAMEWORK.md) · [`GLOSSARY`](docs/GLOSSARY.md) · [`ROADMAP`](docs/ROADMAP.md)

---

## ⚡ Quick Start

```bash
git clone https://github.com/JoshithReddyAleti/Episode_14_The_Discipline_Layer_What_Separates_Shippers_from_Demoers.git
cd Episode_14_The_Discipline_Layer_What_Separates_Shippers_from_Demoers

# Pick a discipline to start with — each Part is independent
cat src/vector_db_internals/README.md          # Part A entry point
cat src/dspy_deep_dive/README.md               # Part B entry point
cat src/prompt_injection_deep_dive/README.md   # Part C entry point
cat src/statistical_foundations/README.md      # Part D entry point

# Run a hands-on lab
cat discipline_examples/hnsw_tuning_workshop/README.md

# Verify utilities work
make test
```

---

## 💼 Resume Bullets

> **Option 1:** Architected production RAG stack achieving 95% recall@10 at 8K QPS on 200M-vector Qdrant deployment, tuned HNSW with M=32 / efC=400 / efS=128, added scalar+PQ quantization for 4× memory reduction, hybrid BM25+vector retrieval, and metadata pre-filtering — cutting p99 latency from 340ms to 62ms.

> **Option 2:** Built a DSPy-based prompt engineering pipeline replacing hand-written prompts across 12 LLM features; MIPRO optimization improved task metrics 18-34% vs manual baselines; deployed with prompt versioning, canary rollout, and A/B testing infrastructure integrated with Langfuse.

> **Option 3:** Led red-team program for enterprise AI product using Garak + PyRIT + custom automated adversarial suite; identified 47 injection/exfiltration vulnerabilities pre-launch; shipped dual-LLM defense pattern + instruction hierarchy + output filtering; reduced successful injection rate from 34% baseline to 2.1% post-hardening.

> **Option 4:** Designed statistically-rigorous A/B testing framework for LLM features with proper power calculations (MDE 0.5% at 80% power), CUPED variance reduction (35% variance reduction), multiple-testing correction, and automated rollback triggers. Ran 60+ experiments spanning prompt, model, and RAG changes; institutional learnings library indexed by feature area.

---

## 🎤 Interview Story

> *"When our product hit 5M queries/day, three things broke at once. Prompts were being hand-edited in production without version control (some regressions took weeks to catch). Users were injecting instructions through the CRM notes we retrieved as context — one attacker exfiltrated snippets of our system prompt. And leadership wanted 'quality metrics' but couldn't tell if changes helped or hurt because we had no A/B framework. So I built the discipline layer: prompt versioning with Langfuse + CI checks; dual-LLM injection defense (retrieved content goes to a quarantined model that produces structured summaries, never raw text into the privileged model); and a statistical A/B framework with proper power calcs. In the first quarter we shipped 47 experiments with real learnings. Injection success rate dropped from 34% to 2%. And engineers stopped shipping prompt changes to production Fridays at 5pm without approval. The lesson: LLM features feel like small script changes but they're production systems that need production discipline — same as any DB migration or ranking model change."*

---

## 📚 The Complete AI Engineering Roadmap 2026

| Ep | Topic | Link |
|---|---|---|
| 1 | Understanding LLMs | [Repo](https://github.com/JoshithReddyAleti/Understanding_LLMs_From_The_Inside_Out) |
| 2 | Python for AI | [Repo](https://github.com/JoshithReddyAleti/Python_For_AI_What_Actually_Matters) |
| 3 | Tool calling & validation | [Repo](https://github.com/JoshithReddyAleti/Building_AI_Project-Blueprint_for_Begin) |
| 4 | End-to-end AI project | [Repo](https://github.com/JoshithReddyAleti/Episode_4_Your_First_End_To_End_AI_Project) |
| 5 | RAG & Augmented Generation | [Repo](https://github.com/JoshithReddyAleti/Mastering_RAG_and_Augmented_Generation) |
| 6 | Frameworks & Fine-Tuning | [Repo](https://github.com/JoshithReddyAleti/Episode_6_AI_Frameworks_and_Fine_Tuning_Complete_Guide) |
| 7 | Memory & State | [Repo](https://github.com/JoshithReddyAleti/Episode_7_Memory_and_State_in_AI_Systems) |
| 8 | Evaluation & Governance | [Repo](https://github.com/JoshithReddyAleti/Episode_8_AI_Evaluation_Validation_and_Governance) |
| 9 | Agents | [Repo](https://github.com/JoshithReddyAleti/Episode_9_Agents_When_AI_Systems_Make_Decisions) |
| 10 | Deployment | [Repo](https://github.com/JoshithReddyAleti/Episode_10_Deployment_Taking_AI_Systems_to_Production) |
| 11 | Observability | [Repo](https://github.com/JoshithReddyAleti/Episode_11_Observability_Knowing_What_Your_AI_is_Doing) |
| 12 | Inference & Model Serving | [Repo](https://github.com/JoshithReddyAleti/Episode_12_Inference_and_Model_Serving_The_Systems_Under_the_Model) |
| 13 | Fine-Tuning + Multimodal | [Repo](https://github.com/JoshithReddyAleti/Episode_13_Fine_Tuning_and_Multimodal_The_Training_Layer) |
| **14** | **Data Eng + Prompt Eng + Security + A/B Testing (The Discipline Layer)** | **← You are here** |
| 15+ | Agentic AI Roadmap 2027 | Coming next series |

---

<div align="center">

**The discipline layer is what makes the difference between an AI feature that ships and one that keeps almost-shipping.**

*Four disciplines. 31 sections. All the depth.*

[Episode 13](https://github.com/JoshithReddyAleti/Episode_13_Fine_Tuning_and_Multimodal_The_Training_Layer) · [Newsletter](https://www.linkedin.com/newsletters/ai-engineering-roadmap-2026-7467249724752908288/) · [All Episodes](docs/ROADMAP.md)

</div>
