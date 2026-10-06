"""Tests for prompt_utils."""
import pytest
from utils.prompt_utils import (
    render_template, extract_variables, prompt_hash, short_hash,
    estimate_tokens, compress_words, compression_ratio, fingerprint,
)


def test_render_template_basic():
    result = render_template("Hello {name}!", {"name": "world"})
    assert result == "Hello world!"


def test_render_template_missing_var_raises():
    with pytest.raises(KeyError):
        render_template("Hello {name}!", {})


def test_extract_variables():
    vars_found = extract_variables("Dear {name}, your order {order_id} is ready.")
    assert set(vars_found) == {"name", "order_id"}


def test_prompt_hash_stable():
    p = "You are a helpful assistant."
    h1 = prompt_hash(p)
    h2 = prompt_hash(p)
    assert h1 == h2


def test_prompt_hash_different_for_different_prompts():
    assert prompt_hash("A") != prompt_hash("B")


def test_short_hash_length():
    assert len(short_hash("hello")) == 12
    assert len(short_hash("hello", length=8)) == 8


def test_estimate_tokens_scales():
    assert estimate_tokens("") == 0
    short = estimate_tokens("Hello")
    long_ = estimate_tokens("Hello world this is much longer text with many words")
    assert long_ > short


def test_compress_reduces_length():
    text = "The quick brown fox jumps over the lazy dog and continues to jump many times"
    compressed = compress_words(text, keep_ratio=0.5)
    assert len(compressed.split()) < len(text.split())


def test_compression_ratio_less_than_one():
    text = "one two three four five six seven eight nine ten"
    compressed = compress_words(text, keep_ratio=0.5)
    ratio = compression_ratio(text, compressed)
    assert ratio < 1.0


def test_fingerprint_captures_structure():
    fp = fingerprint("You are {role}. Help the {user}.")
    assert "role" in fp.variable_names
    assert "user" in fp.variable_names
    assert fp.token_estimate > 0
    assert fp.length_chars > 0
