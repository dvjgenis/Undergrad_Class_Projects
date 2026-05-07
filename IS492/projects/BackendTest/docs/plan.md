# HarmonyForge Implementation Plan

**The Blueprint** — Active implementation steps. Do not proceed on LLM-layer work until architectural separation is explicitly listed.

---

## Architectural Separation (Mandatory)

Before any LLM or Theory Inspector work:

- [x] The LLM receives **JSON-based score deltas** from the logic engine (error codes, measure, voices).
- [x] The LLM **never generates MusicXML** or edits the score.
- [x] API calls (OpenAI, Anthropic, GROQ) are restricted to `TheoryInspector/` and backend routes that invoke it.
- [x] `engine/` contains **no** LLM calls.

---

## Completed

- **Tactile Sandbox:** VexFlow note-level rendering; red/blue violation highlights; playback (Tone.js); drag, draw, multi-select, cut/copy/paste; keyboard shortcuts (MuseScore parity). #72 closed.
- **Engine quality validation:** Test run log, quality assessment, refinement recommendations. `docs/Engine-Test-Run-Log.md`. #73 closed.
- **MVP flow:** Upload → harmonize → sandbox → export; sample lead sheet; PDF/MIDI convert.

---

## Current Priorities

1. **Logic Core:** Refinement sprint (#74) — parameter tuning, cadence-anchor pruning, scale heuristic; align validation codes with RAG.
2. **Accessibility:** Skip link, contrast audit, focus rings (#75).
3. **Theory Inspector:** Leader → Auditor → RAG → Tutor flow; fuse retrieval (vector + BM25).
4. **Export:** MusicXML, PDF (MuseScore/LilyPond on PATH).

---

## Makefile Anchors

Use `make test-solver` for engine tests and `make calc-her` for Harmonic Error Rate. See `Makefile` and `.cursorrules`.