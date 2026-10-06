# Concepts — Reference For Episode 14

## Data Engineering

**Vector.** Fixed-length array of floats representing content in embedding space.

**Recall@k.** For a query, fraction of true top-k neighbors returned.

**HNSW.** Hierarchical Navigable Small World graph — the workhorse ANN algorithm.

**IVF.** Inverted File Index — coarse quantization via k-means clustering.

**PQ.** Product Quantization — compression by splitting vectors into subspaces, quantizing each.

**BM25.** Best Matching 25 — the classical sparse (keyword) ranking function.

**MinHash.** Hash-based estimation of Jaccard similarity, used for near-duplicate detection.

**LSH.** Locality-Sensitive Hashing — indexing so similar items collide.

**Contamination.** Test data appearing in training data, invalidating benchmarks.

## Prompt Engineering

**Signature (DSPy).** Declarative interface for an LLM task — inputs, outputs, description.

**Optimizer (DSPy).** Algorithm that searches over prompts and demos to maximize a metric.

**Structured decoding.** Constrained generation guaranteeing schema-conformant output.

**FSA/DFA.** Finite State Automaton — used by Outlines to constrain decoding.

**Grammar (CFG).** Context-Free Grammar — used for structured non-JSON outputs.

**LLMLingua.** Token-level prompt compression using a small scorer model.

## Security

**Prompt injection.** Attack where hostile instructions in input override intended behavior.

**Direct injection.** From user input.

**Indirect injection.** From retrieved content (documents, tool output).

**Jailbreak.** Bypassing model's alignment training to produce harmful output.

**Dual-LLM.** Defensive pattern separating privileged (system) and quarantined (untrusted content) LLMs.

**Instruction hierarchy.** Model-level defense treating instructions from different sources with different trust.

**Red team.** Adversarial evaluation function, human + tools.

## A/B Testing

**H₀ / H₁.** Null and alternative hypotheses.

**α.** Type I error rate; probability of false positive under H₀.

**β.** Type II error rate; probability of false negative under H₁.

**Power.** 1 − β; probability of detecting a real effect.

**MDE.** Minimum Detectable Effect — smallest effect the experiment can reliably detect.

**CUPED.** Controlled-Using-Pre-Experiment-Data — variance reduction technique.

**Bonferroni.** Multiple testing correction: α / k.

**FDR / Benjamini-Hochberg.** False Discovery Rate control.

**SUTVA.** Stable Unit Treatment Value Assumption — required for standard A/B validity.

**CI.** Confidence Interval on effect size.

