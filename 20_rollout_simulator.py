import random


def main():
    stages = [0.01, 0.05, 0.10, 0.25, 0.50, 1.00]
    baseline_error = 0.02
    treatment_error = 0.023  # slight regression
    threshold_ratio = 3.0

    print(f"Rollout simulation")
    print(f"Baseline error: {baseline_error * 100:.2f}%")
    print(f"Treatment error: {treatment_error * 100:.2f}%")
    print(f"Auto-rollback if treatment error > {threshold_ratio}x baseline")
    print()

    for pct in stages:
        # Simulate observed error with noise
        n = int(10000 * pct)
        errors = sum(1 for _ in range(n) if random.random() < treatment_error)
        observed = errors / n if n else 0
        status = "OK" if observed <= baseline_error * threshold_ratio else "ROLLBACK"
        print(f"  Stage {pct * 100:5.1f}%  n={n:5d}  observed_error={observed*100:.2f}%  [{status}]")
        if status == "ROLLBACK":
            print("  -> Auto-rollback triggered. Reverting to control.")
            break
    else:
        print("  -> Full rollout complete.")


if __name__ == "__main__":
    random.seed(42)
    main()
