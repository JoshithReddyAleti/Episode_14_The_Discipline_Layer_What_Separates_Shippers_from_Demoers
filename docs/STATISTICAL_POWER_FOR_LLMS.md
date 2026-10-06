# Statistical Power For LLMs

## The formulas

**Sample size (proportion):**
```
n = 2 × (z_{α/2} + z_β)² × p̄(1-p̄) / δ²
```

**Sample size (mean):**
```
n = 2 × (z_{α/2} + z_β)² × σ² / δ²
```

**MDE (proportion):**
```
MDE = (z_{α/2} + z_β) × √(2 × p̄(1-p̄) / n)
```

## LLM-specific gotchas

**Higher variance.** LLM outputs vary at temperature > 0. Measure your baseline variance before power calc.

**Subjective metrics.** LLM-judge scores are noisy. Use multi-judge, aggregation, and CUPED.

**Heavy tails.** Use bootstrap CIs, median-based metrics, or winsorize.

**Multiple related metrics.** Correction (Bonferroni or FDR) needed.

## Variance reduction — CUPED

Variance reduction: `Var(Y_adj) = Var(Y) × (1 - ρ²)`, where ρ is correlation between Y and pre-experiment Y_pre.

- ρ = 0.5 → 25% variance reduction.
- ρ = 0.7 → 50% variance reduction.

Free 25-50% sample size reduction. Table stakes for serious A/B programs.

## Effect size expectations by change type

- Prompt wording tweak: d ≈ 0.05-0.2 (small; need thousands).
- Prompt structure (CoT, examples): d ≈ 0.2-0.5.
- Model change (mini → full): d ≈ 0.3-0.8.
- RAG addition/improvement: d ≈ 0.4-1.0+.

## Multiple testing correction

- **Bonferroni:** α / k. Conservative.
- **Holm-Bonferroni:** step-down. Slightly more powerful.
- **Benjamini-Hochberg (FDR):** most powerful when many tests. Default for exploratory.

Choose BEFORE looking at results.

