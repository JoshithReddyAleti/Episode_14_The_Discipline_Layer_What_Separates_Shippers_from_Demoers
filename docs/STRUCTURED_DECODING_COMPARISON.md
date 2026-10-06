# Structured Decoding — Library Comparison

| Library | Approach | Overhead | Best for |
|---|---|---|---|
| OpenAI structured outputs | Provider-side FSA | 0-5% | GPT-4-class API users |
| Anthropic tool use | Schema in tool def | 0-10% | Claude API users |
| Google response_schema | Provider FSA | 0-5% | Gemini API users |
| Outlines | Regex/JSON → DFA (Python) | 3-10% | Local HF models |
| XGrammar | CFG via PDA, cached masks | 1-5% | High-throughput local |
| LLGuidance | Rust CFG engine | 1-5% | vLLM/frontier serving |
| LMFormatEnforcer | Per-token filter | 5-15% | Broad framework support |
| Guidance | Template DSL | 5-20% | Complex templated flows |
| Instructor | Pydantic + provider API | 0-10% | Type-safe Python |

## Decision guide

- **OpenAI/Anthropic/Google API:** use their native structured outputs.
- **Type-safe Python + APIs:** Instructor.
- **Local model, JSON:** Outlines (mature) or XGrammar (fastest).
- **Custom grammar (SQL, DSL):** XGrammar or LLGuidance.
- **Broad framework support:** LMFormatEnforcer.
- **Complex templated multi-step:** Guidance.

## Guarantees

- 100% schema compliance when the model can produce anything matching the schema.
- Model still chooses content within the constrained set.
- Grammar mis-specification (too restrictive) can cause weird outputs.

## Quality impact

- Generally positive when format is a real failure mode.
- Occasionally negative when schema is over-restrictive.
- Fix: loosen where possible; add "notes" or "reasoning" fields.

