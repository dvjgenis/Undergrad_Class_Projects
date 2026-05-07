# HarmonyForge API – Frontend Integration Guide

This document describes the backend API for the 4-phase harmonization workflow.

- **PRD:** `docs/PRD.md` — Product requirements, Must Have features
- **Architecture:** `docs/Algorithmic-Backend-Architecture.md` — Solver, validation codes

## Base URL

```
http://localhost:8000
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Start the server from project root:**

```bash
cd /path/to/BackendTest
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Convert (PDF/MIDI → MusicXML)

### `POST /api/convert`

Convert PDF or MIDI to MusicXML. Use when the user uploads `.pdf`, `.mid`, or `.midi` before the harmonize flow.

**Request:** `multipart/form-data` with `file` (PDF, MID, or MIDI)

**Response:**

```json
{
  "musicxml": "<xml>...</xml>"
}
```

| Format | Converter | Notes |
|--------|-----------|-------|
| MIDI (.mid, .midi) | music21 | Built-in, always available |
| PDF (.pdf) | Audiveris | Requires [Audiveris](https://github.com/Audiveris/audiveris) installed and on PATH |

---

## Phase 1 & 2: Upload & Harmonize

### `POST /api/harmonize`

Upload MusicXML, select presets, and receive harmonized sheet music.

**Request body:**

```json
{
  "musicxml": "<xml>...</xml>",
  "instruments": ["alto", "tenor", "bass"],
  "mood": "major",
  "genre": "classical",
  "difficulty": "intermediate"
}
```

| Field        | Type     | Required | Description                                                                 |
|-------------|----------|----------|-----------------------------------------------------------------------------|
| `musicxml`  | string   | yes      | Full MusicXML content of the uploaded score                                 |
| `instruments` | string[] | no       | Parts to include: `alto`, `tenor`, `bass`. Omit or `null` = all parts       |
| `mood`      | string   | no       | `major` \| `minor` (default: `major`)                                      |
| `genre`     | string   | no       | `classical` \| `pop` \| `mariachi` (default: `classical`)                  |
| `difficulty`| string   | no       | `easy` \| `intermediate` \| `advanced` (default: `intermediate`)            |

**Response:**

```json
{
  "musicxml": "<xml>...</xml>",
  "violations": [
    {
      "measure": 2,
      "time_step": 4,
      "code": "PARALLEL_PERFECT",
      "explanation": "Parallel fifths/octaves...",
      "severity": "red",
      "voices": [0, 2]
    }
  ],
  "success": true
}
```

---

## Phase 3: Edit & Validate (Red/Blue Highlights)

### `POST /api/validate`

Validate the current (possibly user-edited) score. Returns violations for red (theory violations) and blue (genre nuances) highlighting.

**Request body:**

```json
{
  "musicxml": "<xml>...</xml>",
  "genre": "classical"
}
```

| Field    | Type   | Required | Description                                                          |
|----------|--------|----------|----------------------------------------------------------------------|
| `musicxml` | string | yes    | Current score (with or without user edits)                           |
| `genre`  | string | no       | `classical` \| `pop` \| `mariachi` – used for red vs blue mapping   |

**Response:**

```json
{
  "red": [
    {
      "measure": 2,
      "time_step": 4,
      "code": "VOICE_ORDER",
      "explanation": "Voices must remain in SATB register order...",
      "severity": "red",
      "voices": null
    }
  ],
  "blue": [
    {
      "measure": 3,
      "time_step": 6,
      "code": "PARALLEL_PERFECT",
      "explanation": "Parallel fifths/octaves...",
      "severity": "blue",
      "voices": [0, 2]
    }
  ]
}
```

- **Red**: Real music theory violations (e.g. voice order, spacing, parallel fifths in classical).
- **Blue**: Stylistic nuances that look like violations but are acceptable in the genre (e.g. mariachi without thirds).

---

## Phase 3: Theory Chatbot

### `POST /api/theory-inspect`

Chat endpoint for explanations and suggestions. The AI does not edit or generate music; it only explains and suggests. See `docs/AI-as-Consultant-Interaction-Model.md` for the full interaction model.

**Request body:**

```json
{
  "musicxml": "<xml>...</xml>",
  "score_delta": { "error_codes": ["PARALLEL_PERFECT"], "measure": 2 },
  "user_query": "Why is this flagged? How can I fix it?",
  "context": { "genre": "classical", "mood": "major" }
}
```

| Field        | Type   | Required | Description                                      |
|--------------|--------|----------|--------------------------------------------------|
| `musicxml`   | string | yes      | Current score                                   |
| `score_delta`| object | no       | Optional context (e.g. error codes, measure)   |
| `user_query` | string | yes      | User question                                   |
| `context`    | object | no       | Extra context (genre, mood, etc.)               |

**Response:** RAG-based explanation with reasoning steps and sources.

---

## Phase 4: Export

### `POST /api/export`

Export the score as XML or PDF.

**Request body:**

```json
{
  "musicxml": "<xml>...</xml>",
  "format": "xml"
}
```

| Field    | Type   | Required | Description                    |
|----------|--------|----------|--------------------------------|
| `musicxml` | string | yes    | Score to export               |
| `format` | string | no       | `xml` \| `pdf` (default: `xml`) |

**Response:**

- `format=xml`: `Content-Type: application/xml`, body = MusicXML string
- `format=pdf`: `Content-Type: application/pdf`, body = PDF bytes

**Note:** PDF export requires MuseScore or LilyPond installed and on `PATH`.

---

## Presets

### `GET /api/presets`

Returns available preset options for the frontend.

**Response:**

```json
{
  "mood": ["major", "minor"],
  "genre": ["classical", "pop", "mariachi"],
  "difficulty": ["easy", "intermediate", "advanced"],
  "instruments": ["soprano", "alto", "tenor", "bass"]
}
```

---

## Health Check

### `GET /health`

Returns `{"status": "ok"}`.

---

## Violation Codes (for highlighting)

| Code                     | Typical severity | Description                                      |
|--------------------------|------------------|--------------------------------------------------|
| `VOICE_ORDER`            | red              | Voices out of SATB order                         |
| `SPACING`                | red              | Excessive spacing between voices                 |
| `PARALLEL_PERFECT`       | red/blue         | Parallel fifths/octaves (blue in pop/mariachi)   |
| `LEADING_TONE_UNRESOLVED`| red/blue         | Leading tone not resolved (blue in pop/mariachi) |
| `LARGE_LEAP`             | red/blue         | Large leap in a voice                            |
| `REPEATED_FUNCTION`      | red/blue         | Repeated harmonic function                      |

---

## CORS

CORS is enabled for all origins to support frontend development.

---

## Tools Integration

The backend leverages modules from the `tools/` folder:

- **LangGraph** (`tools/langgraph/`): Used by TheoryInspector for the Leader → Auditor → RAG → Tutor orchestration when available. The local package is preferred over pip-installed LangGraph.
- **RAG techniques**: TheoryInspector uses **fusion retrieval** (vector + BM25 via Reciprocal Rank Fusion) for theory chunk retrieval, improving relevance for both semantic and keyword queries.
- **Auditor tools**: The theory tools (interval analysis, parallel motion detection, etc.) are wired to real SATB data extracted from the user's score via `score_delta` and `musicxml`.
