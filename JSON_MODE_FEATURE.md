# JSON Output Mode

The JSON output mode now relies entirely on Strands' structured output support via the `FactOutput` Pydantic model. Instead of managing our own fact accumulator, the agent simply asks the LLM to emit a validated JSON document that includes:

1. `query` – the original user question.
2. `sources` – a list of articles with `id`, `title`, `url`, `last_modified`, and `word_count`.
3. `facts` – an array of extracted facts, each with the `fact` text, supporting `source_ids`, and a `category` (definition/history/application/technical/other).
4. `summary` – an optional final synopsis of the findings.

The JSON prompt clearly instructs the model to follow this schema, and the agent passes `structured_output_model=FactOutput` so Strands enforces the contract. If the LLM fails to obey (e.g., it doesn't produce valid JSON), the request surface raises an error rather than silently falling back to a secondary pipeline. This keeps the public API’s promise of guaranteed, type-safe JSON intact while simplifying the internal tooling.
