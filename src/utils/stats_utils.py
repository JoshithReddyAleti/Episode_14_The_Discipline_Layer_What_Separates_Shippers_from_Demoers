"""
stats_utils.py — statistical utilities for LLM A/B testing.

Provides:
- Sample size calculators (proportions and means)
- MDE calculators
- Multiple testing correction (Bonferroni, Holm, FDR)
- CUPED variance reduction
- Confidence interval calculations
- CLI interface

Usage from Python:
    from utils.stats_utils import sample_size_proportion, cuped_adjust
    n = sample_size_proportion(p_baseline=0.10, mde=0.02, alpha=0.05, power=0.80)

Usage from CLI:
    python -m src.utils.stats_utils sample-size --p 0.10 --mde 0.02
    python -m src.utils.stats_utils mde --n 5000 --p 0.10
    python -m src.utils.stats_utils bonferroni --pvals 0.01 0.02 0.03 --alpha 0.05
"""
from __future__ import annotations
import argparse
import math
from typing import List, Tuple


# --- Sample size / power ---

def _z(alpha: float) -> float:
    """Two-sided critical z-value. Approximation via rational function."""
    # Beasley-Springer-Moro
    p = 1 - alpha / 2
    # Simplified inverse normal
    t = math.sqrt(-2 * math.log(1 - p))
    z = t - (2.515517 + 0.802853*t + 0.010328*t*t) / (
        1 + 1.432788*t + 0.189269*t*t + 0.001308*t*t*t
    )
    return z


def _z_power(power: float) -> float:
    """One-sided critical z-value for target power."""
    return _z(2 * (1 - power))


def sample_size_proportion(p_baseline: float, mde: float,
                           alpha: float = 0.05, power: float = 0.80) -> int:
    """Sample size per arm for two-sample proportion test.

    n = 2 * (z_alpha/2 + z_beta)^2 * p_bar * (1 - p_bar) / mde^2
    """
    if not 0 < p_baseline < 1:
        raise ValueError("p_baseline must be in (0, 1)")
    if mde <= 0:
        raise ValueError("mde must be positive")
    z_a = _z(alpha)
    z_b = _z_power(power)
    p_bar = p_baseline + mde / 2
    n = 2 * (z_a + z_b) ** 2 * p_bar * (1 - p_bar) / (mde ** 2)
    return int(math.ceil(n))


def sample_size_mean(sigma: float, mde: float,
                     alpha: float = 0.05, power: float = 0.80) -> int:
    """Sample size per arm for two-sample t-test (approximation using z)."""
    z_a = _z(alpha)
    z_b = _z_power(power)
    n = 2 * (z_a + z_b) ** 2 * sigma ** 2 / (mde ** 2)
    return int(math.ceil(n))


def mde_proportion(n_per_arm: int, p_baseline: float,
                   alpha: float = 0.05, power: float = 0.80) -> float:
    """Minimum detectable effect given fixed sample size."""
    z_a = _z(alpha)
    z_b = _z_power(power)
    return (z_a + z_b) * math.sqrt(2 * p_baseline * (1 - p_baseline) / n_per_arm)


# --- Multiple testing correction ---

def bonferroni(pvals: List[float], alpha: float = 0.05) -> List[bool]:
    """Return rejection decisions with Bonferroni correction."""
    k = len(pvals)
    threshold = alpha / k
    return [p < threshold for p in pvals]


def holm_bonferroni(pvals: List[float], alpha: float = 0.05) -> List[bool]:
    """Holm-Bonferroni step-down. Preserves original order in output."""
    k = len(pvals)
    indexed = sorted(enumerate(pvals), key=lambda x: x[1])
    reject = [False] * k
    for i, (orig_idx, p) in enumerate(indexed):
        if p < alpha / (k - i):
            reject[orig_idx] = True
        else:
            break
    return reject


def benjamini_hochberg(pvals: List[float], q: float = 0.05) -> List[bool]:
    """Benjamini-Hochberg FDR control. Returns rejections in original order."""
    k = len(pvals)
    indexed = sorted(enumerate(pvals), key=lambda x: x[1])
    reject = [False] * k
    # Find largest i such that p_(i) <= (i/k) * q
    threshold_idx = -1
    for i, (_, p) in enumerate(indexed):
        if p <= ((i + 1) / k) * q:
            threshold_idx = i
    if threshold_idx >= 0:
        for i in range(threshold_idx + 1):
            reject[indexed[i][0]] = True
    return reject


# --- CUPED variance reduction ---

def cuped_adjust(y: List[float], y_pre: List[float]) -> Tuple[List[float], float]:
    """Apply CUPED adjustment. Returns (adjusted_y, theta)."""
    if len(y) != len(y_pre):
        raise ValueError("y and y_pre must have same length")
    n = len(y)
    mean_y_pre = sum(y_pre) / n
    mean_y = sum(y) / n
    cov = sum((yi - mean_y) * (yp - mean_y_pre) for yi, yp in zip(y, y_pre)) / n
    var_y_pre = sum((yp - mean_y_pre) ** 2 for yp in y_pre) / n
    theta = cov / var_y_pre if var_y_pre > 0 else 0.0
    adjusted = [yi - theta * (yp - mean_y_pre) for yi, yp in zip(y, y_pre)]
    return adjusted, theta


# --- Confidence intervals ---

def wilson_ci(successes: int, n: int, alpha: float = 0.05) -> Tuple[float, float]:
    """Wilson score CI for a proportion (better than Wald near 0 or 1)."""
    if n == 0:
        return (0.0, 0.0)
    z = _z(alpha)
    p_hat = successes / n
    denom = 1 + z ** 2 / n
    center = (p_hat + z ** 2 / (2 * n)) / denom
    half = z * math.sqrt(p_hat * (1 - p_hat) / n + z ** 2 / (4 * n ** 2)) / denom
    return (center - half, center + half)


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="LLM A/B testing statistical utilities")
    sub = parser.add_subparsers(dest="cmd", required=True)

    ss = sub.add_parser("sample-size", help="Compute per-arm sample size (proportion)")
    ss.add_argument("--p", type=float, required=True, help="baseline proportion")
    ss.add_argument("--mde", type=float, required=True, help="minimum detectable effect")
    ss.add_argument("--alpha", type=float, default=0.05)
    ss.add_argument("--power", type=float, default=0.80)

    md = sub.add_parser("mde", help="Compute MDE given sample size (proportion)")
    md.add_argument("--n", type=int, required=True, help="sample size per arm")
    md.add_argument("--p", type=float, required=True, help="baseline proportion")
    md.add_argument("--alpha", type=float, default=0.05)
    md.add_argument("--power", type=float, default=0.80)

    bf = sub.add_parser("bonferroni", help="Bonferroni correction")
    bf.add_argument("--pvals", type=float, nargs="+", required=True)
    bf.add_argument("--alpha", type=float, default=0.05)

    bh = sub.add_parser("fdr", help="Benjamini-Hochberg FDR correction")
    bh.add_argument("--pvals", type=float, nargs="+", required=True)
    bh.add_argument("--q", type=float, default=0.05)

    ci = sub.add_parser("wilson-ci", help="Wilson 95% CI for a proportion")
    ci.add_argument("--successes", type=int, required=True)
    ci.add_argument("--n", type=int, required=True)
    ci.add_argument("--alpha", type=float, default=0.05)

    args = parser.parse_args()

    if args.cmd == "sample-size":
        n = sample_size_proportion(args.p, args.mde, args.alpha, args.power)
        print(f"Sample size per arm: {n}")
        print(f"Total sample: {2 * n}")
    elif args.cmd == "mde":
        m = mde_proportion(args.n, args.p, args.alpha, args.power)
        print(f"MDE: {m:.4f} (absolute)")
        print(f"MDE: {m/args.p*100:.2f}% (relative)")
    elif args.cmd == "bonferroni":
        rej = bonferroni(args.pvals, args.alpha)
        for p, r in zip(args.pvals, rej):
            print(f"  p={p:.4f}  {'REJECT' if r else 'keep'}")
    elif args.cmd == "fdr":
        rej = benjamini_hochberg(args.pvals, args.q)
        for p, r in zip(args.pvals, rej):
            print(f"  p={p:.4f}  {'REJECT' if r else 'keep'}")
    elif args.cmd == "wilson-ci":
        lo, hi = wilson_ci(args.successes, args.n, args.alpha)
        p_hat = args.successes / args.n if args.n else 0.0
        print(f"  p_hat: {p_hat:.4f}")
        print(f"  {int((1-args.alpha)*100)}% CI: ({lo:.4f}, {hi:.4f})")


if __name__ == "__main__":
    main()
