import hashlib
from collections import Counter

DOCS = [
    "The quick brown fox jumps over the lazy dog.",
    "The quick brown fox jumps over the lazy dog.",  # exact duplicate
    "The quick brown fox jumps over the lazy DOG.",  # near duplicate
    "A completely different sentence about pandas.",
    "Yet another distinct document.",
]


def main():
    hashes = [hashlib.sha256(d.encode()).hexdigest() for d in DOCS]
    counts = Counter(hashes)
    exact_dups = sum(1 for c in counts.values() if c > 1)
    unique = len(counts)
    print(f"Total documents: {len(DOCS)}")
    print(f"Unique (exact dedup): {unique}")
    print(f"Exact duplicate groups: {exact_dups}")
    print(f"Dedup rate: {(len(DOCS) - unique) / len(DOCS) * 100:.1f}%")


if __name__ == "__main__":
    main()
