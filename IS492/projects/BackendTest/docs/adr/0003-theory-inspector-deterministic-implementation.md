# ADR 0003: Theory Inspector Deterministic Implementation

**Status:** Accepted  
**Date:** March 2026  
**Context:** Architecture audit (engine vs Theory Inspector separation)

---

## Decision

The Theory Inspector's main execution path is **fully deterministic** by default. No LLM API calls are made in the default flow. The Tutor uses RAG-retrieved theory chunks + template formatting to produce explanations.

---

## Rationale

### Current Implementation

| Node | Implementation | LLM? |
|------|----------------|------|
| Leader | Keyword-based intent classification | No |
| Auditor | Symbolic tools (intervals, parallels, key, Roman numerals) | No |
| RAG | ChromaDB + BM25 fusion retrieval | No |
| Tutor | Template + RAG snippets → explanation text | No (optional LLM available) |

### Benefits

- **Glass Box integrity:** No stochastic token prediction in the critical path.
- **Latency:** Deterministic flow is fast and predictable.
- **Cost:** No API charges when LLM is disabled.
- **Offline:** Works without API keys.

---

## Consequences

- **LLMSettings** exist for optional Tutor enrichment. When `TI_USE_LLM_TUTOR=true` and API keys are set, the Tutor may call an LLM to enrich explanations. The LLM receives only context (tool outputs, retrieved chunks, user query) and returns text—never MusicXML or edits.
- **Fallback:** If LLM is unavailable or disabled, template + RAG suffices.