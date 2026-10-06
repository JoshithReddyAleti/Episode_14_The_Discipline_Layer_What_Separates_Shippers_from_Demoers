"""
prompt_utils.py — utilities for prompt engineering discipline.

Provides:
- Prompt template rendering
- Prompt version hashing
- Rough token estimation
- Approximate compression ratio (word-level heuristic like LLMLingua-lite)
- Prompt fingerprinting for A/B analysis
- CLI interface

Usage:
    from utils.prompt_utils import render_template, estimate_tokens, prompt_hash
    prompt = render_template("Hello {name}", {"name": "world"})
    tokens = estimate_tokens(prompt)
"""
from __future__ import annotations
import argparse
import hashlib
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


# --- Templating ---

def render_template(template: str, variables: Dict[str, str]) -> str:
    """Simple {name} substitution. Raises on missing variables."""
    def replace(match):
        key = match.group(1)
        if key not in variables:
            raise KeyError(f"Missing template variable: {key}")
        return str(variables[key])
    return re.sub(r"\{(\w+)\}", replace, template)


def extract_variables(template: str) -> List[str]:
    """Return list of variable names in a template."""
    return re.findall(r"\{(\w+)\}", template)


# --- Hashing / versioning ---

def prompt_hash(prompt: str, algorithm: str = "sha256") -> str:
    """Stable hash of a prompt, for versioning."""
    normalized = prompt.strip()
    h = hashlib.new(algorithm)
    h.update(normalized.encode("utf-8"))
    return h.hexdigest()


def short_hash(prompt: str, length: int = 12) -> str:
    """Short version hash for display."""
    return prompt_hash(prompt)[:length]


# --- Token estimation ---

def estimate_tokens(text: str) -> int:
    """Rough token count (chars / 4 heuristic; tiktoken-style would be exact).

    Under-estimates for code, over-estimates for very short strings.
    """
    if not text:
        return 0
    # Roughly 4 chars per token for English
    char_count = len(text)
    word_count = len(text.split())
    # Blend: token count is roughly max of char/4 and word*1.3
    return max(int(char_count / 4), int(word_count * 1.3))


# --- Compression (word-frequency heuristic) ---

def compress_words(text: str, keep_ratio: float = 0.4) -> str:
    """Drop low-info words based on frequency. Placeholder for LLMLingua-style compression."""
    if keep_ratio >= 1.0:
        return text
    words = text.split()
    if not words:
        return text
    # Score words by inverse frequency (rarer = more informative)
    counts: Dict[str, int] = {}
    for w in words:
        w_norm = w.lower().strip(".,!?;:()[]{}")
        counts[w_norm] = counts.get(w_norm, 0) + 1
    scored = [
        (i, w, 1.0 / counts[w.lower().strip(".,!?;:()[]{}")])
        for i, w in enumerate(words)
    ]
    # Keep top `keep_ratio` fraction
    scored.sort(key=lambda x: -x[2])
    keep_n = max(1, int(len(words) * keep_ratio))
    kept = sorted(scored[:keep_n], key=lambda x: x[0])
    return " ".join(w for _, w, _ in kept)


def compression_ratio(original: str, compressed: str) -> float:
    """Ratio of compressed to original tokens (< 1 means compression)."""
    orig = estimate_tokens(original)
    comp = estimate_tokens(compressed)
    if orig == 0:
        return 1.0
    return comp / orig


# --- Fingerprinting for A/B ---

@dataclass
class PromptFingerprint:
    version_hash: str
    token_estimate: int
    variable_names: List[str]
    length_chars: int


def fingerprint(prompt: str) -> PromptFingerprint:
    """Structural fingerprint of a prompt for A/B tracking."""
    return PromptFingerprint(
        version_hash=short_hash(prompt),
        token_estimate=estimate_tokens(prompt),
        variable_names=extract_variables(prompt),
        length_chars=len(prompt),
    )


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="Prompt engineering utilities")
    sub = parser.add_subparsers(dest="cmd", required=True)

    rn = sub.add_parser("render", help="Render a template with variables")
    rn.add_argument("--template", type=str, required=True)
    rn.add_argument("--var", action="append", default=[], help="KEY=VALUE (repeatable)")

    hs = sub.add_parser("hash", help="Hash a prompt for versioning")
    hs.add_argument("--prompt", type=str, required=True)

    tk = sub.add_parser("tokens", help="Estimate token count")
    tk.add_argument("--text", type=str, required=True)

    cp = sub.add_parser("compress", help="Word-frequency compression demo")
    cp.add_argument("--text", type=str, required=True)
    cp.add_argument("--keep", type=float, default=0.4, help="Fraction of words to keep")

    fp = sub.add_parser("fingerprint", help="Structural fingerprint of a prompt")
    fp.add_argument("--prompt", type=str, required=True)

    args = parser.parse_args()

    if args.cmd == "render":
        vars_dict = dict(v.split("=", 1) for v in args.var)
        print(render_template(args.template, vars_dict))
    elif args.cmd == "hash":
        print(f"sha256:{prompt_hash(args.prompt)}")
        print(f"short:{short_hash(args.prompt)}")
    elif args.cmd == "tokens":
        print(f"Estimated tokens: {estimate_tokens(args.text)}")
    elif args.cmd == "compress":
        compressed = compress_words(args.text, args.keep)
        ratio = compression_ratio(args.text, compressed)
        print(f"Original ({estimate_tokens(args.text)} tokens): {args.text}")
        print(f"Compressed ({estimate_tokens(compressed)} tokens): {compressed}")
        print(f"Ratio: {ratio:.2%}")
    elif args.cmd == "fingerprint":
        fp_result = fingerprint(args.prompt)
        print(f"Version hash: {fp_result.version_hash}")
        print(f"Token estimate: {fp_result.token_estimate}")
        print(f"Variables: {fp_result.variable_names}")
        print(f"Length (chars): {fp_result.length_chars}")


if __name__ == "__main__":
    main()
