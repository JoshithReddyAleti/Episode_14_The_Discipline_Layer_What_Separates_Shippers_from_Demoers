import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from utils.prompt_utils import fingerprint

PROMPTS = {
    "v1": "You are a helpful assistant. Answer concisely.",
    "v2": "You are a helpful assistant. Answer concisely and cite sources.",
    "v3": "You are a helpful assistant.\nAnswer concisely and cite sources.",
}


def main():
    print(f"{'Version':<8} {'Hash':<14} {'Tokens':<8} {'Chars':<8}")
    print("-" * 40)
    for name, text in PROMPTS.items():
        fp = fingerprint(text)
        print(f"{name:<8} {fp.version_hash:<14} {fp.token_estimate:<8} {fp.length_chars:<8}")


if __name__ == "__main__":
    main()
