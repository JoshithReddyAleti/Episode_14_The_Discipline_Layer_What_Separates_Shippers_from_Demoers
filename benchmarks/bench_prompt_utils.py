"""Benchmark prompt utilities."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils.prompt_utils import estimate_tokens, prompt_hash, compress_words, fingerprint


SAMPLE = "The quick brown fox jumps over the lazy dog. " * 50


def bench(name, fn, n=10000):
    t0 = time.time()
    for _ in range(n):
        fn(SAMPLE)
    t1 = time.time()
    per = (t1 - t0) * 1_000_000 / n
    print(f"{name}: {n} calls in {(t1-t0)*1000:.2f} ms ({per:.2f} us/call)")


if __name__ == "__main__":
    print("=== Prompt utility throughput ===")
    bench("estimate_tokens", estimate_tokens)
    bench("prompt_hash", prompt_hash)
    bench("compress_words (keep=0.5)", lambda s: compress_words(s, 0.5), n=1000)
    bench("fingerprint", fingerprint, n=1000)
