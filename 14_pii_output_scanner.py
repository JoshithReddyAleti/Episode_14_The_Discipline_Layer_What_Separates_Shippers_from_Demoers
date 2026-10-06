import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from utils.security_utils import contains_pii

OUTPUTS = [
    "The user's email is alice@example.com.",
    "Please call 555-123-4567 for support.",
    "My API key is sk-1234567890abcdefghijklmnopqrstuv.",
    "The weather is sunny today.",
    "SSN redacted: XXX-XX-XXXX.",
]


def main():
    for text in OUTPUTS:
        r = contains_pii(text)
        status = "FLAGGED" if r.flagged else "clean"
        print(f"[{status}] {text}")
        for reason in r.reasons:
            print(f"    - {reason}")


if __name__ == "__main__":
    main()
