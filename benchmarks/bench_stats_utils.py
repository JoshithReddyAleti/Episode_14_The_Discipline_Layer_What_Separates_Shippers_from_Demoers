"""Benchmark stats utilities."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils.stats_utils import sample_size_proportion, bonferroni, benjamini_hochberg


def bench_sample_size():
    scenarios = [
        (0.10, 0.01), (0.10, 0.02), (0.10, 0.05),
        (0.50, 0.01), (0.50, 0.02), (0.50, 0.05),
        (0.05, 0.005), (0.05, 0.01), (0.05, 0.02),
    ]
    print(f"{'p':>6} {'MDE':>6} {'n_per_arm':>10}")
    for p, mde in scenarios:
        n = sample_size_proportion(p, mde)
        print(f"{p:6.2f} {mde:6.3f} {n:>10}")


def bench_corrections():
    pvals = [i * 0.01 for i in range(1, 21)]
    t0 = time.time()
    for _ in range(1000):
        bonferroni(pvals)
    t1 = time.time()
    print(f"Bonferroni 20 pvals x 1000: {(t1-t0)*1000:.2f} ms")
    t0 = time.time()
    for _ in range(1000):
        benjamini_hochberg(pvals)
    t1 = time.time()
    print(f"BH FDR 20 pvals x 1000: {(t1-t0)*1000:.2f} ms")


if __name__ == "__main__":
    print("=== Sample size scenarios ===")
    bench_sample_size()
    print()
    print("=== Correction timing ===")
    bench_corrections()
