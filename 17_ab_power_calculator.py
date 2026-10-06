import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from utils.stats_utils import sample_size_proportion, mde_proportion


def main():
    print("=== A/B Power Calculator ===")
    print()
    print("Scenario 1: Given baseline p and desired MDE, compute sample size.")
    print("  Baseline p=0.72, MDE=0.02, alpha=0.05, power=0.80:")
    n = sample_size_proportion(0.72, 0.02, 0.05, 0.80)
    print(f"    -> {n} per arm, {2*n} total")
    print()
    print("Scenario 2: Given sample size, compute MDE.")
    print("  n=5000 per arm, baseline p=0.10:")
    m = mde_proportion(5000, 0.10, 0.05, 0.80)
    print(f"    -> MDE = {m:.4f} absolute ({m/0.10*100:.1f}% relative)")


if __name__ == "__main__":
    main()
