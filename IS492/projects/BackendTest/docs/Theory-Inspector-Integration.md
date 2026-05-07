# Theory Inspector & AI Integration

**Status:** Infrastructure ready. Runs deterministically without API keys.

---

## Overview

The Theory Inspector provides ante-hoc explainability for voice-leading violations. It uses:

1. **Deterministic path (default):** RAG retrieval + symbolic tools → template-based explanations. No API calls.
2. **Optional LLM enrichment:** When `TI_USE_LLM_TUTOR=true` and API keys are set, the Tutor enriches explanations with an LLM. Explanation-only; never edits the score.

---

## Environment Variables

Copy `.env.example` to `.env` and add keys when ready:

| Variable | Purpose |
|----------|---------|
| `GROQ_API_KEY` | Groq (Llama) for Tutor enrichment |
| `OPENAI_API_KEY` | OpenAI (GPT) for Tutor enrichment |
| `ANTHROPIC_API_KEY` | Anthropic (Claude) for Tutor enrichment |
| `TI_USE_LLM_TUTOR` | `true` to enable LLM enrichment (default: `false`) |
| `TI_TUTOR_MODEL` | Model for Tutor (e.g. `claude-3-5-sonnet-latest`) |
| `TI_CHROMA_DIR` | ChromaDB vector index path |

**Without keys:** Theory Inspector works fully. Explanations use RAG chunks + symbolic analysis.

---

## API

### `POST /api/theory-inspect`

Request:
```json
{
  "musicxml": "<score>",
  "user_query": "Why is this parallel fifth?",
  "context": { "genre": "classical" },
  "score_delta": { "error_codes": ["PARALLEL_PERFECT"], "measure": 3 }
}
```

- `score_delta` improves RAG when violations exist. Frontend passes it from `/api/validate` results.

### `GET /api/ti-status`

Returns LLM availability (for UI hints):
```json
{
  "llm_enabled": false,
  "llm_available": false,
  "providers": { "anthropic": false, "openai": false, "groq": false },
  "mode": "deterministic"
}
```

---

## Frontend Integration

- **TheoryInspectorPanel** in sandbox: Chat UI, sends `theoryInspect` with `musicxml`, `user_query`, `context`, `score_delta`.
- **Violations** → `score_delta.error_codes` and `measure` for better retrieval.
- **ChatFAB** and context menu "Ask Theory Inspector" open the panel.

---

## Enabling LLM (When Keys Are Available)

1. Add keys to `.env`: `ANTHROPIC_API_KEY=sk-...` (or OpenAI/Groq).
2. Set `TI_USE_LLM_TUTOR=true`.
3. Restart backend. `/api/ti-status` will report `llm_available: true`.
