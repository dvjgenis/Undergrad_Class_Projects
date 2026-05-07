# Algorithmic Backend Architecture

**Date:** March 4, 2025  
**Scope:** Complete specification of the HarmonyForge BackendTest engine and API.  
**PRD:** See `docs/PRD.md` for product requirements and Must Have features.

---

## 1. Overview

The backend is a **deterministic hierarchical constraint-satisfaction solver** for SATB harmonization. It does not use neural networks; it uses a layered DAG + Viterbi shortest-path algorithm grounded in Schenkerian and Common Practice theory.

**Pipeline:** MusicXML → Parse → Structural Analysis → DAG Build → Viterbi Solve → Validate → Export

---

## 2. Core Components

| Component | Location | Role |
|-----------|----------|------|
| **Parser** | `engine/io_handler.py` | `parse_xml()`, `parse_xml_string()` — MusicXML → melody, chords, durations, meta |
| **Structural Analysis** | `engine/core_engine.py` | `detect_structure()` — phrase boundaries, cadence anchors (V→I), pillars |
| **Chord Inference** | `engine/hierarchical_bridge.py` | `merge_backend_hierarchical_plan()` — merge chords with beat-level logic |
| **Graph Builder** | `engine/core_engine.py` | `_build_layers()`, `generate_column()` — build SATB voicing columns per chord |
| **Solver** | `engine/core_engine.py` | `_shortest_path_dag()`, `solve_harmony()` — Viterbi shortest path |
| **Validator** | `engine/core_engine.py` | `validate_solution()` — rule checks, red/blue flags |
| **Exporter** | `engine/io_handler.py` | `export_xml()`, `export_xml_string()` — solution → MusicXML |

---

## 3. Solver Architecture

### 3.1 Layered DAG

- **Layers:** One per time step (chord column).
- **Nodes:** Valid SATB voicings per chord (bass, tenor, alto, soprano).
- **Edges:** Weighted by `calculate_transition_cost()`.
- **Path:** Shortest path from first to last layer minimizes total cost.

### 3.2 Transition Cost Factors

| Factor | Effect |
|--------|--------|
| Voice ordering | Hard floor: B < T < A < S |
| Leap cap | Hard floor: 14 semitones (strict) / 19 (relaxed) |
| Step vs. leap | Stepwise motion preferred; large leaps penalized |
| Parallel perfects | ~10× penalty |
| Unresolved leading tone | ~5× penalty |
| Tritone resolution | ~12× (improper), ~2× (suboptimal) for dim→I/V |
| Common tones | Bonus (negative cost) |
| Root motion | Penalty for abrupt bass jumps |
| Metric weight | Stronger penalties on strong beats |

### 3.3 Validation Codes

| Code | Severity | Red in classical | Blue in pop/mariachi |
|------|----------|------------------|----------------------|
| VOICE_ORDER | hard | ✓ | ✓ |
| SPACING | hard | ✓ | ✓ |
| TRITONE_RESOLUTION_IMPROPER | hard | ✓ | ✓ |
| PARALLEL_PERFECT | soft | ✓ | blue |
| LEADING_TONE_UNRESOLVED | soft | ✓ | blue |
| LARGE_LEAP | soft | ✓ | blue |
| REPEATED_FUNCTION | soft | ✓ | blue |
| TRITONE_RESOLUTION_SUBOPTIMAL | soft | ✓ | blue |

---

## 4. API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/harmonize` | POST | Upload MusicXML → harmonized score + violations |
| `/api/validate` | POST | Validate (possibly edited) score → red/blue annotations |
| `/api/theory-inspect` | POST | TheoryInspector chatbot — explain, suggest (no edits) |
| `/api/export` | POST | Export score to MusicXML or PDF |
| `/api/presets` | GET | Return available mood, genre, difficulty |

---

## 5. TheoryInspector (AI-as-Consultant)

- **Flow:** Leader → Auditor → RAG → Tutor
- **Leader:** Classifies intent (explanation vs. validation)
- **Auditor:** Symbolic tools (intervals, parallels, key, Roman numerals)
- **RAG:** Fusion retrieval (vector + BM25) from theory chunks
- **Tutor:** Returns explanation with reasoning steps, severity, sources. Default: deterministic (template + RAG). Optional: `TI_USE_LLM_TUTOR=true` enables LLM enrichment (explanation-only).
- **AI never edits:** See `docs/AI-as-Consultant-Interaction-Model.md`

---

## 6. Knowledge Base

- **Sources:** Open Music Theory, methodology PDFs (HarmonySolver, SchenkComposer, ProGress)
- **Index:** `TheoryInspector/index/theory_chunks.csv`, ChromaDB for vector search
- **Rules:** `engine/knowledge_rules.py` — RULE_PATTERNS, ERROR_CODE_HINTS, penalty weights

---

## 7. Supported Chord Types

| Chord | Symbol | Notes (C) |
|-------|--------|-----------|
| Major | I, IV, V | 0-4-7, 5-9-0, 7-11-2 |
| Minor | i, ii, iii, vi | 0-3-7, 2-5-9, etc. |
| Dominant 7 | V7, V7/V | 7-11-2-5, etc. |
| Diminished | vii°, ii° | 11-2-5, 2-5-8 |
| Diminished 7 | vii°7, ii°7 | 11-2-5-8, 2-5-8-11 |
| Secondary dominants | V/V, V7/V | 2-6-9, 2-6-9-0 |

---

## 8. Presets

| Preset | Values |
|--------|--------|
| mood | major, minor |
| genre | classical, pop, mariachi |
| difficulty | beginner, intermediate, advanced |

---

## 9. References

- `docs/Theory-Engine-Alignment-Update.md` — Tritone resolution, RAG alignment
- `docs/AI-as-Consultant-Interaction-Model.md` — AI interaction boundaries
- `API_INTEGRATION.md` — Request/response formats for frontend
