# 🧩 Structured Decoding — Making Output Valid, Always

> *"The LLM sometimes returns invalid JSON" is a class of bug that shouldn't exist anymore. Structured decoding makes format compliance a guarantee, not a hope. Every serious LLM feature in 2026 uses it.*

---

## JSON Mode Provider Internals (`json_mode_provider_internals.py`)

**OpenAI, Anthropic, and other providers now offer "JSON mode" — different implementations, different guarantees.**

**OpenAI's `response_format={"type": "json_object"}`:**
- Guarantees output is valid JSON (parseable).
- Does *not* guarantee schema conformance (unless combined with function calling / structured outputs).

**OpenAI's `response_format={"type": "json_schema", "json_schema": {...}}` (structured outputs):**
- Guarantees output matches provided JSON schema.
- Uses constrained decoding under the hood.
- 100% schema compliance if the model can generate anything at all.

**Anthropic's approach:**
- Tool use with strict input schema.
- Prompt-guided JSON output for freeform structured tasks.
- No explicit "JSON mode" as of 2026; tool use is the primary structured mechanism.

**Google Gemini:**
- `response_schema` parameter for structured outputs.
- Similar guarantees to OpenAI's json_schema.

**How constrained decoding works (implementation sketch):**
1. At each decoding step, the model produces logits over all vocabulary tokens.
2. A **grammar or schema checker** determines which tokens are *legal* at this point in the output.
3. Illegal tokens have their logits set to -infinity (masked out).
4. Softmax over remaining tokens → sample.
5. Update grammar state; repeat.

The output *cannot* violate the schema because illegal tokens are never sampled.

**Trade-offs:**
- **Guarantees:** 100% schema compliance.
- **Cost:** slight latency overhead (5-20% typically) from grammar checking.
- **Quality:** sometimes lower than unconstrained (model may not "want" to produce schema-conforming output, sampling from the constrained subset can lead to weird choices).

---

## Outlines Deep Dive (`outlines_deep_dive.py`)

**Outlines** — Python library for constrained decoding, model-agnostic. Compiles regex/JSON schemas to **finite state automata (FSAs)**, uses FSA state to determine allowed tokens.

**The idea:**
- Convert schema → regex.
- Convert regex → deterministic finite automaton (DFA).
- DFA tracks the state of what's been generated.
- At each token position, DFA reveals allowed tokens.
- Sample from allowed tokens only.

**Example:**
```python
from outlines import models, generate
import outlines

model = models.transformers("microsoft/Phi-3-mini-4k-instruct")

# JSON schema
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string", "format": "email"},
    },
    "required": ["name", "age"],
}

generator = generate.json(model, schema)
result = generator("Generate a user profile")
# result is guaranteed to be a valid Python dict matching the schema
```

**Key components:**
- **Schema → FSA compiler.** Understands JSON Schema, regex, Pydantic models.
- **Tokenizer-aware constraint.** Maps FSA transitions to sets of allowed tokens (BPE-aware).
- **Runtime state machine.** Tracks position; provides allowed-token mask at each step.

**Strengths:**
- Model-agnostic (works with any HF model or via API).
- Fast (FSA operations are cheap).
- Supports regex, JSON schema, Pydantic, custom grammars.

**Weaknesses:**
- Some very complex JSON schemas can be slow to compile.
- Requires token-level access; harder to use with closed API models.

---

## Guidance Deep Dive (`guidance_deep_dive.py`)

**Guidance (Microsoft)** — the pioneering library for structured LLM generation.

**Model:**
- Template-based generation with embedded control flow.
- Model completes designated slots; template handles the rest.

**Example:**
```python
import guidance

model = guidance.models.OpenAI("gpt-4o-mini")

program = guidance.chat("""
Generate a user profile:
Name: {{gen 'name' max_tokens=10 stop='\\n'}}
Age: {{select 'age' options=['10', '20', '30', '40', '50']}}
Email: {{gen 'email' regex='[^@]+@[^@]+\\.[a-z]+'}}
""")

output = program(model=model)
print(output['name'], output['age'], output['email'])
```

**Constructs:**
- `{{gen 'var' ...}}` — model generates text into named variable.
- `{{select 'var' options=[...]}}` — model picks from options.
- `{{#if ...}}...{{/if}}` — conditional branches based on prior generation.
- `{{gen 'var' regex='...'}}` — constrained by regex.

**Strengths:**
- Elegant template language.
- Fine-grained control over generation flow.
- Works with local models and (some) APIs.

**Weaknesses:**
- Custom DSL learning curve.
- Some features require local model (token-level access).

**Current status (2026):** less popular than Outlines and Instructor for pure structured output; still strong for complex templated generation.

---

## XGrammar (`xgrammar.py`)

**XGrammar (2024)** — fast context-free grammar–based constrained decoding.

**Key innovation:**
- Precomputes token acceptance masks per grammar state.
- Uses **pushdown automata** (PDA) for CFG state tracking.
- **10-100× faster** than naive grammar-based decoding.
- Integrated into vLLM, TensorRT-LLM, MLC-LLM.

**Why fast:**
- Token mask computation is the bottleneck in constrained decoding.
- XGrammar caches masks aggressively.
- Uses vectorized operations for mask computation.

**API:**
```python
import xgrammar

grammar_str = """
root ::= object
object ::= "{" ws pairs? ws "}"
pairs ::= pair (ws "," ws pair)*
pair ::= string ws ":" ws value
value ::= object | array | string | number | "true" | "false" | "null"
string ::= "\"" chars? "\""
chars ::= char+
char ::= [a-zA-Z0-9 ]
number ::= [0-9]+
array ::= "[" ws value? (ws "," ws value)* ws "]"
ws ::= [ \t\n]*
"""

compiler = xgrammar.GrammarCompiler(tokenizer_info)
grammar = compiler.compile_grammar(grammar_str)
matcher = xgrammar.GrammarMatcher(grammar)

# During decoding:
allowed_mask = matcher.get_next_token_bitmask()
# Mask logits, sample, feed back to matcher.accept_token(sampled_token)
```

**When to use:**
- Custom grammars (not just JSON).
- Very high throughput requirements.
- Latency-sensitive constrained decoding.

---

## LMFormatEnforcer (`lmformatenforcer.py`)

**LMFormatEnforcer** — token-level output filter, works with many inference frameworks.

**Approach:**
- Post-decode filter at each step.
- For each candidate next token, checks if accepting it keeps the output schema-valid.
- Rejects tokens that would violate schema.

**Support:**
- HuggingFace Transformers.
- vLLM.
- LangChain.
- LlamaCPP.
- ExLlama.

**Example:**
```python
from lmformatenforcer import JsonSchemaParser
from lmformatenforcer.integrations.transformers import build_transformers_prefix_allowed_tokens_fn

schema = {"type": "object", "properties": {"answer": {"type": "string"}}}
parser = JsonSchemaParser(schema)
prefix_fn = build_transformers_prefix_allowed_tokens_fn(tokenizer, parser)

output = model.generate(
    input_ids=input_ids,
    prefix_allowed_tokens_fn=prefix_fn,
)
```

**Strengths:**
- Broad framework support.
- Simple integration.
- Works well with JSON schema.

**Weaknesses:**
- Slower than XGrammar or Outlines FSA for complex schemas.
- Per-token filtering can be a bottleneck.

---

## Grammar-Based Generation (`grammar_based_generation.py`)

**When JSON isn't enough.**

**Grammar formats:**

**EBNF (Extended Backus-Naur Form):**
```
expression = term { "+" term | "-" term }
term = factor { "*" factor | "/" factor }
factor = number | "(" expression ")"
number = digit { digit }
digit = "0" | "1" | "2" | ... | "9"
```

**GBNF (llama.cpp's format):**
- Similar to EBNF, tuned for token-level constraints.
- Used by llama.cpp for constrained inference.

**Use cases beyond JSON:**
- **DSLs** (SQL queries, math expressions, function calls).
- **Structured code snippets** (specific programming language subsets).
- **Custom formats** (log entries with strict schema, config files).

**Example: constrained SQL:**
```
query = "SELECT " column_list " FROM " table
column_list = column ( ", " column )*
column = "id" | "name" | "email" | "created_at"
table = "users" | "orders" | "products"
```

The model can only produce queries that select from an allowed column list and allowed tables. Zero SQL injection possible.

**When to use:**
- Model is generating structured data that isn't JSON.
- You need to constrain content beyond format (e.g., only certain SQL tables).
- You want to prevent freeform generation entirely.

---

## Pydantic + Instructor (`pydantic_instructor.py`)

**Instructor** — Pydantic + LLM APIs. The most ergonomic way to get typed outputs.

**Example:**
```python
from pydantic import BaseModel, Field
from instructor import from_openai
from openai import OpenAI

class UserProfile(BaseModel):
    name: str
    age: int = Field(..., ge=0, le=150)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")

client = from_openai(OpenAI())

result: UserProfile = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=UserProfile,
    messages=[{"role": "user", "content": "Generate a user profile for Alice."}],
)

print(result.name, result.age)  # typed access
```

**How it works:**
- Instructor converts the Pydantic model to a JSON schema.
- Uses OpenAI's structured outputs (or function calling for other providers).
- Validates the response against the Pydantic model.
- Retries on validation failure (built-in retry logic).

**Strengths:**
- Type safety end-to-end.
- IDE autocomplete on the result.
- Validation via Pydantic's rich constraints.
- Works with multiple providers.

**Weaknesses:**
- Adds a layer over the raw API.
- Retry logic can mask model quality issues.

**In 2026:** Instructor is the default for typed structured outputs in Python. If you're not using it (or an equivalent), you're doing manual JSON parsing and validation.

---

## LLGuidance (`llguidance.py`)

**LLGuidance (2024+)** — the latest wave of constrained decoding libraries, focused on speed and expressiveness.

**Key features:**
- Rust-based grammar engine.
- CFG and Lark grammar support.
- Very low overhead compared to Python-based tools.
- Integrated with vLLM and other high-throughput inference.

**Why it matters:**
- Constrained decoding is now table stakes; performance is the differentiator.
- LLGuidance and XGrammar are pushing latency overhead below 5% in many cases.

**Example:**
```python
import llguidance

grammar = llguidance.LarkGrammar("""
start: object
object: "{" [pair (","  pair)*] "}"
pair: STRING ":" value
value: STRING | NUMBER | object | array
...
""")

# Use with vLLM or other integrations
```

**Frontier trend:** constrained decoding is moving from "trade quality for correctness" to "correctness at near-zero cost." As libraries mature, using constrained decoding will be the default even for tasks that don't strictly need it.

---

## Structured Decoding Performance (`structured_decoding_performance.py`)

**The cost story.**

**Latency overhead by library (2026 numbers, approximate):**
| Library | Overhead vs unconstrained |
|---|---|
| OpenAI structured outputs | 0-5% |
| Anthropic tool use | 0-10% |
| XGrammar (local) | 1-5% |
| LLGuidance (local) | 1-5% |
| Outlines | 3-10% |
| LMFormatEnforcer | 5-15% |
| Guidance | 5-20% depending on template |

**Throughput impact:**
- Batch throughput often unaffected (parallel decoding).
- Single-query latency: as above.

**Quality impact:**
- **Generally positive** for tasks where format matters (parsing failures were driving errors).
- **Sometimes negative** if the model is "forced" into an unnatural format — it may produce awkward or incomplete outputs.
- **Solution:** ensure the schema matches what the model naturally wants to produce.

**When constrained decoding hurts quality:**
- Schema requires fields the model doesn't have info for.
- Enum options don't cover the natural answer.
- Format is too restrictive for the model's reasoning.

**Rule:** if you find your model producing worse outputs under constraint, the constraint is likely mis-specified. Loosen where possible; add "reasoning" or "notes" fields where the model needs room.

---

## Files in This Directory

| File | What It Covers |
|---|---|
| `json_mode_provider_internals.py` | OpenAI, Anthropic, Google differences |
| `outlines_deep_dive.py` | FSM approach |
| `guidance_deep_dive.py` | The library |
| `xgrammar.py` | Fast grammars |
| `lmformatenforcer.py` | Token-level filtering |
| `grammar_based_generation.py` | EBNF, GBNF, custom grammars |
| `pydantic_instructor.py` | Type-safe outputs |
| `llguidance.py` | Latest developments |
| `structured_decoding_performance.py` | The cost |

---

*Previous: [← TextGrad and Prompt Optimization](../textgrad_and_prompt_optimization/README.md) · Next: [Prompt Compression →](../prompt_compression/README.md)*  ·  *Back to [main README](../../README.md)*
