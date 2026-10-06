"""
security_utils.py — LLM security utilities.

Provides:
- Prompt injection heuristic detection
- Canary string detection (contamination check)
- PII pattern detection in outputs
- Encoding detection (Base64, hex)
- Simple filter chain composition
- CLI interface

Usage:
    from utils.security_utils import detect_injection, contains_pii
    if detect_injection(user_input).flagged:
        block()
"""
from __future__ import annotations
import argparse
import base64
import re
from dataclasses import dataclass, field
from typing import List, Callable


# --- Detection results ---

@dataclass
class DetectionResult:
    flagged: bool
    reasons: List[str] = field(default_factory=list)
    score: float = 0.0


# --- Injection detection ---

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)",
    r"disregard\s+(all\s+)?(previous|prior|above)",
    r"you\s+are\s+(now\s+)?dan\b",
    r"do\s+anything\s+now",
    r"pretend\s+(to\s+be|you\s+are)",
    r"forget\s+(everything|your\s+(rules|instructions|training))",
    r"</?(system|instructions|prompt)>",
    r"reveal\s+(your|the)\s+(system|initial|original)\s+prompt",
    r"repeat\s+everything\s+(above|before)",
    r"you\s+are\s+(now\s+)?(unrestricted|unfiltered|jailbroken)",
]


def detect_injection(text: str) -> DetectionResult:
    """Heuristic detection of common prompt injection patterns."""
    if not text:
        return DetectionResult(flagged=False)
    reasons: List[str] = []
    text_lower = text.lower()
    for pat in INJECTION_PATTERNS:
        if re.search(pat, text_lower):
            reasons.append(f"pattern:{pat}")
    if len(reasons) > 0:
        return DetectionResult(flagged=True, reasons=reasons, score=min(1.0, 0.3 * len(reasons)))
    return DetectionResult(flagged=False)


# --- Encoding detection ---

def is_likely_base64(text: str, min_len: int = 40) -> bool:
    """Heuristic: is this text a Base64-encoded blob?"""
    if len(text) < min_len:
        return False
    if not re.fullmatch(r"[A-Za-z0-9+/=\s]+", text):
        return False
    stripped = re.sub(r"\s", "", text)
    if len(stripped) % 4 != 0:
        return False
    try:
        base64.b64decode(stripped, validate=True)
        return True
    except Exception:
        return False


def detect_encoding(text: str) -> DetectionResult:
    """Flag likely encoded content that may hide instructions."""
    reasons: List[str] = []
    # Base64 blobs
    for m in re.finditer(r"[A-Za-z0-9+/=]{40,}", text):
        if is_likely_base64(m.group()):
            reasons.append("base64_blob")
            break
    # Hex blobs
    if re.search(r"\b(?:[0-9a-fA-F]{2}\s*){20,}\b", text):
        reasons.append("hex_blob")
    if reasons:
        return DetectionResult(flagged=True, reasons=reasons, score=0.5)
    return DetectionResult(flagged=False)


# --- PII detection ---

PII_PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone_us": r"\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b(?:\d[ -]?){13,19}\b",
    "api_key_openai": r"sk-[a-zA-Z0-9]{20,}",
    "api_key_generic": r"[a-zA-Z0-9_-]*(api[_-]?key|token|secret)[a-zA-Z0-9_-]*[:=]\s*['\"]?[a-zA-Z0-9_-]{20,}",
}


def contains_pii(text: str) -> DetectionResult:
    """Detect common PII patterns in output text."""
    reasons: List[str] = []
    for name, pat in PII_PATTERNS.items():
        if re.search(pat, text, re.IGNORECASE):
            reasons.append(f"pii:{name}")
    if reasons:
        return DetectionResult(flagged=True, reasons=reasons, score=1.0)
    return DetectionResult(flagged=False)


# --- Canary detection ---

def detect_canary(text: str, canary: str) -> DetectionResult:
    """Detect if a canary string appears (indicating contamination/leak)."""
    if canary and canary in text:
        return DetectionResult(flagged=True, reasons=[f"canary:{canary[:20]}"], score=1.0)
    return DetectionResult(flagged=False)


# --- Filter chain ---

Filter = Callable[[str], DetectionResult]


def apply_filters(text: str, filters: List[Filter]) -> DetectionResult:
    """Apply a chain of filters; combines results."""
    combined = DetectionResult(flagged=False)
    for f in filters:
        result = f(text)
        if result.flagged:
            combined.flagged = True
            combined.reasons.extend(result.reasons)
            combined.score = max(combined.score, result.score)
    return combined


def default_input_filter_chain() -> List[Filter]:
    """Standard chain for user input."""
    return [detect_injection, detect_encoding]


def default_output_filter_chain() -> List[Filter]:
    """Standard chain for LLM output."""
    return [contains_pii]


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="LLM security utilities")
    sub = parser.add_subparsers(dest="cmd", required=True)

    inj = sub.add_parser("scan-injection", help="Scan text for injection patterns")
    inj.add_argument("--text", type=str, required=True)

    pii = sub.add_parser("scan-pii", help="Scan text for PII")
    pii.add_argument("--text", type=str, required=True)

    enc = sub.add_parser("scan-encoding", help="Scan text for suspicious encoding")
    enc.add_argument("--text", type=str, required=True)

    can = sub.add_parser("scan-canary", help="Scan text for a canary string")
    can.add_argument("--text", type=str, required=True)
    can.add_argument("--canary", type=str, required=True)

    fc = sub.add_parser("full-scan", help="Run all input filters")
    fc.add_argument("--text", type=str, required=True)

    args = parser.parse_args()

    def show(name: str, r: DetectionResult):
        status = "FLAGGED" if r.flagged else "clean"
        print(f"{name}: {status}  score={r.score:.2f}")
        for reason in r.reasons:
            print(f"    - {reason}")

    if args.cmd == "scan-injection":
        show("injection", detect_injection(args.text))
    elif args.cmd == "scan-pii":
        show("pii", contains_pii(args.text))
    elif args.cmd == "scan-encoding":
        show("encoding", detect_encoding(args.text))
    elif args.cmd == "scan-canary":
        show("canary", detect_canary(args.text, args.canary))
    elif args.cmd == "full-scan":
        show("full", apply_filters(args.text, default_input_filter_chain()))


if __name__ == "__main__":
    main()
