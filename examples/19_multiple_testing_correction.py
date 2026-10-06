import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from utils.stats_utils import bonferroni, benjamini_hochberg


def main():
    pvals = [0.001, 0.008, 0.020, 0.031, 0.045, 0.056, 0.089, 0.203]
    print(f"P-values: {pvals}")
    print()
    print("Bonferroni (alpha=0.05):")
    for p, r in zip(pvals, bonferroni(pvals, 0.05)):
        print(f"  p={p:.3f}  {'REJECT' if r else 'keep'}")
    print()
    print("Benjamini-Hochberg FDR (q=0.05):")
    for p, r in zip(pvals, benjamini_hochberg(pvals, 0.05)):
        print(f"  p={p:.3f}  {'REJECT' if r else 'keep'}")


if __name__ == "__main__":
    main()
