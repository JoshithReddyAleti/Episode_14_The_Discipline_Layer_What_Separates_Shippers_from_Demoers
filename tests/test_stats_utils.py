"""Tests for stats_utils."""
from utils.stats_utils import (
    sample_size_proportion, sample_size_mean, mde_proportion,
    bonferroni, holm_bonferroni, benjamini_hochberg,
    cuped_adjust, wilson_ci,
)


def test_sample_size_proportion_sanity():
    """Sample size increases as MDE shrinks."""
    n1 = sample_size_proportion(0.10, 0.05)
    n2 = sample_size_proportion(0.10, 0.02)
    n3 = sample_size_proportion(0.10, 0.01)
    assert n1 < n2 < n3


def test_sample_size_reasonable_range():
    """Standard scenario yields expected ballpark."""
    n = sample_size_proportion(0.10, 0.02, alpha=0.05, power=0.80)
    # Expect several thousand per arm
    assert 1500 < n < 10000


def test_mde_inverse_of_sample_size():
    """MDE at a given n should be close to the MDE that yielded n."""
    n = sample_size_proportion(0.10, 0.02, alpha=0.05, power=0.80)
    mde_back = mde_proportion(n, 0.10, alpha=0.05, power=0.80)
    # Should be close to 0.02
    assert 0.018 < mde_back < 0.022


def test_bonferroni_conservative():
    """Bonferroni threshold is alpha / k."""
    pvals = [0.01, 0.03, 0.06]
    rej = bonferroni(pvals, alpha=0.05)
    # Threshold = 0.05/3 = 0.0167; only p=0.01 rejects
    assert rej == [True, False, False]


def test_holm_at_least_as_powerful_as_bonferroni():
    """Holm-Bonferroni rejects at least as many as Bonferroni."""
    pvals = [0.001, 0.02, 0.03, 0.04, 0.5]
    b = bonferroni(pvals, 0.05)
    h = holm_bonferroni(pvals, 0.05)
    for bi, hi in zip(b, h):
        # If Bonferroni rejects, Holm also rejects
        if bi:
            assert hi


def test_bh_more_rejections_than_bonferroni_on_dense_tests():
    """BH FDR is more powerful when many tests are borderline significant."""
    pvals = [0.001, 0.008, 0.020, 0.031, 0.042]
    b = sum(bonferroni(pvals, 0.05))
    bh = sum(benjamini_hochberg(pvals, 0.05))
    assert bh >= b


def test_cuped_reduces_variance():
    """Adjusted metric has lower variance when correlation is nonzero."""
    import random
    random.seed(42)
    y_pre = [random.gauss(0, 1) for _ in range(1000)]
    y = [0.7 * yp + random.gauss(0, 0.8) for yp in y_pre]

    var_y = sum((yi - sum(y)/len(y))**2 for yi in y) / len(y)
    y_adj, theta = cuped_adjust(y, y_pre)
    var_adj = sum((yi - sum(y_adj)/len(y_adj))**2 for yi in y_adj) / len(y_adj)

    assert var_adj < var_y
    assert 0.5 < theta < 0.9  # roughly the true beta


def test_wilson_ci_contains_point_estimate():
    """CI should span around p_hat."""
    lo, hi = wilson_ci(50, 100, alpha=0.05)
    assert lo < 0.5 < hi
    assert 0 <= lo < hi <= 1


def test_sample_size_mean_sanity():
    """Sample size for continuous outcomes scales with variance."""
    n1 = sample_size_mean(sigma=1.0, mde=0.1)
    n2 = sample_size_mean(sigma=2.0, mde=0.1)
    # 4x variance -> 4x sample size
    assert 3.5 < (n2 / n1) < 4.5
