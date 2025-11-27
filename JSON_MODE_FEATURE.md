# JSON Output Mode

JSON mode now relies on Strands' `FactOutput` structured-output model to emit a richer response catalog. Each JSON document includes:

1. `query` – the original user question.
2. `sources` – a list of articles with metadata (`id`, `title`, `url`, `last_modified`, `word_count`).
3. `facts` – atomic facts, each with `fact`, `source_ids`, and a `category` (`definition`, `history`, `application`, `technical`, `other`).
4. `people`, `places`, `events`, `ideas` – cataloged entities that summarize the named people, locations, historical events, and abstract ideas uncovered during research, each linked back to source IDs.
5. `relations` – explicit relationships between those entities (e.g., "Founding Fathers" ↔ "Declaration of Independence" in 1776) with optional dates and supporting sources.
6. `summary` – an optional synopsis that ties the structured insights together.

The JSON prompt now instructs the LLM to populate those sections, including identifying the people/places/events/ideas and spelling out how they’re connected. The agent passes `structured_output_model=FactOutput` for both synchronous and streaming queries so Strands enforces the schema; if the LLM doesn’t follow the contract, the request surfaces a clear error instead of falling back to auxiliary data. This guarantees valid, auditable JSON without the legacy fact accumulator.
