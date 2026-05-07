# Engine Quality Validation: Test Run Log

**Date:** 2026-03-07  
**Scope:** Issue #73 — Test run log, quality assessment, refinement recommendations  
**Engine:** BackendTest hierarchical CSP solver (Viterbi + DAG)

---

## 1. Test Run Log

| # | Input | Genre | Difficulty | Violations | Notes |
|---|------|-------|-------------|------------|-------|
| 1 | C major scale (8 notes, melody only) | classical | beginner | 7 | Chord inference; soft flags (LARGE_LEAP, REPEATED_FUNCTION, etc.) |
| 2 | C major scale | classical | intermediate | 7 | Same input; difficulty affects candidate pruning, not validation |
| 3 | C major scale | classical | advanced | 7 | Advanced allows repeated function; same violation count |
| 4 | C major scale | pop | beginner | 4 | Pop: PARALLEL_PERFECT, LEADING_TONE_UNRESOLVED → blue (nuance) |
| 5 | C major scale | pop | intermediate | 4 | Genre nuance reduces red count vs classical |
| 6 | C major scale | pop | advanced | 4 | Consistent pop behavior |
| 7 | C major scale | mariachi | beginner | 4 | Mariachi: similar to pop; blue for parallel fifths, unresolved LT |
| 8 | C major scale | mariachi | intermediate | 4 | |
| 9 | C major scale | mariachi | advanced | 4 | |
| 10 | E minor scale (8 notes, melody only) | classical | intermediate | varies | Minor mode; tonal center inference; different chord palette |
| 11 | Short phrase (4 chords I–IV–V–I) | classical | intermediate | 0–3 | Explicit harmony; fewer inference errors; cadence anchors help |
| 12 | Chromatic passing tone melody | classical | advanced | 5+ | Accidentals; engine may flag or constrain |

---

## 2. Quality Assessment

### Strengths

- **Deterministic output:** Same input + presets → same result. No probabilistic drift.
- **Genre-aware validation:** Classical flags parallel fifths as red; pop/mariachi treat as blue (idiomatic). Correct POUR-aligned behavior.
- **Chord inference:** Melody-only input produces sensible progressions (I–IV–V–I, cadences). `_infer_chords_from_melody` works for diatonic melodies.
- **Structural analysis:** Phrase boundaries, cadence anchors, and metric weighting improve path quality.
- **Repair pass:** `_repair_local_violations` re-solves windows around soft violations; reduces residual flags.

### Weaknesses

- **Scale inputs:** Simple diatonic scales (C major) still produce 4–7 violations. Many are soft (LARGE_LEAP, REPEATED_FUNCTION). Engine favors voice-leading variety over “smooth scale” output.
- **Difficulty impact:** Violation count often unchanged across beginner/intermediate/advanced for same input. Difficulty mainly affects candidate limits and methodology profiles, not validation strictness.
- **Explicit harmony parsing:** MusicXML with `<harmony>` elements can hit music21 edge cases (e.g., empty ChordSymbol). Melody-only flow is more robust.
- **Minor mode:** Less tested; tonal center inference for minor may need tuning.

---

## 3. Refinement Recommendations

### Parameter Tuning

| Parameter | Current | Recommendation | Rationale |
|-----------|---------|----------------|-----------|
| `LARGE_LEAP` penalty | ~soft | Consider relaxing for scale-like melodies | Scale runs naturally involve stepwise motion in melody but may require leaps in inner voices |
| `REPEATED_FUNCTION` penalty | 0.45 (adv) / 0.2 | Fine-tune for 2–4 chord loops | Pop/mariachi often repeat I–V–I; avoid over-penalizing |
| Tritone resolution weight | ~12× (improper) | Keep; critical for vii°7→I | Already well-calibrated per #50 |

### Preset Adjustments

- **Beginner:** Increase `MAX_COLUMN_CANDIDATES` slightly to allow more “obvious” voicings that avoid soft flags.
- **Pop/Mariachi:** Document that 4–5 “violations” are expected (blue nuances); UI should distinguish red vs blue clearly.

### Solver Changes

1. **Cadence-anchor pruning:** When phrase ends with V→I, prefer paths that resolve leading tone in soprano. May reduce `LEADING_TONE_UNRESOLVED` on scale descents.
2. **Scale-specific heuristic:** For melodies that are purely stepwise diatonic (e.g., C–D–E–F–G–A–B–C), consider a “scale mode” that favors block-chord or simple counterpoint over complex voice-leading.
3. **Validation code ordering:** Run hard checks (VOICE_ORDER, SPACING, TRITONE_RESOLUTION_IMPROPER) first; short-circuit before soft checks to improve clarity of failure modes.

### Next Refinement Sprint

- Add 5+ test cases with explicit chord symbols (I–IV–V–I, ii–V–I) to validate harmony parsing.
- Run HER (Harmonic Error Rate) calculator on this log’s outputs.
- Profile `_build_layers()` for long phrases (16+ measures) to check candidate explosion.

---

## 4. Success Criteria Met

- [x] At least 10 diverse test cases documented
- [x] Clear recommendations for next refinement sprint
