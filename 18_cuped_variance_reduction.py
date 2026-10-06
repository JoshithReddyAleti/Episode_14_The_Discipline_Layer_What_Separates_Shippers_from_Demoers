import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from utils.stats_utils import cuped_adjust


def variance(xs):
    m = sum(xs) / len(xs)
    return sum((x - m) ** 2 for x in xs) / len(xs)


def main():
    random.seed(42)
    n = 5000
    # Simulate: users with pre-experiment behavior correlated with experiment metric
    y_pre = [random.gauss(10.0, 2.0) for _ in range(n)]
    # Experiment metric: correlated with pre (rho ~0.7) plus noise
    y = [0.7 * yp + random.gauss(3.0, 1.4) for yp in y_pre]

    var_y = variance(y)
    y_adj, theta = cuped_adjust(y, y_pre)
    var_adj = variance(y_adj)

    print(f"Sample size: {n}")
    print(f"Var(Y):      {var_y:.4f}")
    print(f"Theta:       {theta:.4f}")
    print(f"Var(Y_adj):  {var_adj:.4f}")
    print(f"Variance reduction: {(1 - var_adj/var_y) * 100:.1f}%")


if __name__ == "__main__":
    main()
