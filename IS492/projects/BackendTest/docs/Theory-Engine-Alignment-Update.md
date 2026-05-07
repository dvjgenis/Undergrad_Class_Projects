# Theory–Engine Alignment Update: Tritone Resolution in Diminished Seventh Chords

**Date:** March 2, 2025  
**Scope:** Schenkerian voice-leading constraints for vii°7 resolution in SATB; RAG–deterministic solver alignment.

---

## 1. RAG-Sourced Theory (Brave Search + Milne Publishing)

### Tritone Resolution Rules for Diminished Seventh Chords in SATB

**Fully-diminished seventh chords** (vii°7, ii°7) contain **two interlocking tritones**:
- **Tritone 1:** Root–fifth (scale degrees 7̂–4̂)
- **Tritone 2:** Third–seventh (2̂–6̂)

**Resolution conventions (Schenkerian / Common Practice):**

| Tritone Form | Resolution | Motion |
|--------------|------------|--------|
| **Augmented fourth (A4)** | Outward to sixth (m6 or M6) | Contrary motion preferred |
| **Augmented fourth (A4)** | Similar motion to perfect fourth | Acceptable, often upper voices only |
| **Diminished fifth (d5)** | Inward to third (m3 or M3) | Contrary motion preferred |
| **Diminished fifth (d5)** | Similar motion to perfect fifth | Less common; not parallel fifths |

**Tendency tones:**
- 7̂ (leading tone) → 1̂ (up by step)
- 6̂ (chordal seventh) → 5̂ (down by step)
- 4̂ → 3̂ (down by step)
- 2̂ → 1̂ or 3̂

**Summary:** *"A4 will resolve out, d5 in"* (MusicTheoryManual). Contrary motion is preferred; similar motion is acceptable but suboptimal.

---

## 2. Engine Deterministic Solver Alignment

### Current Implementation

The engine uses a **layered DAG + Viterbi shortest-path** solver:
- **Nodes:** Valid SATB voicings per chord column
- **Edges:** Weighted by `calculate_transition_cost()`
- **Path selection:** Minimizes sum of transition costs

### Viterbi Weightings (Relevant to Tritone)

| Factor | Implementation | RAG Alignment |
|--------|----------------|---------------|
| Leading tone | Penalty ~5× if 7̂ not → 1̂ | ✅ Aligns with tendency-tone rule |
| Parallel perfects | Penalty ~10× | ✅ Avoids parallel fifths in resolution |
| Step vs. leap | `step_weight` 0.15–0.25, `leap_weight` 1.1–1.8 | ✅ Encourages stepwise resolution |
| Common tones | Bonus (negative cost) | ✅ Supports smooth voice leading |
| **Tritone pairs** | Penalty in `calculate_transition_cost()`; validation in `validate_solution()` | ✅ Implemented |

### Implementation (Mar 2025)

The solver now explicitly handles tritone resolution:
1. **Validation:** `validate_solution()` detects vii°7→I, vii°→I, ii°7→V transitions and flags improper/suboptimal tritone pairs.
2. **Viterbi penalty:** `calculate_transition_cost()` adds penalty for improper (~12×) and suboptimal (~2×) tritone resolution in dim→resolution transitions.
3. **Codes:** `TRITONE_RESOLUTION_IMPROPER` (red), `TRITONE_RESOLUTION_SUBOPTIMAL` (blue).

---

## 3. Auditor Flow: Red vs. Blue

| Severity | Meaning | Example |
|----------|---------|---------|
| **Red** | Structural violation | Improper tritone resolution (e.g., both voices leap, wrong intervals) |
| **Blue** | Stylistic nuance | Suboptimal but acceptable (e.g., similar motion when contrary preferred) |

**Current codes:** `VOICE_ORDER`, `SPACING` = always red; `PARALLEL_PERFECT`, `LEADING_TONE_UNRESOLVED`, `LARGE_LEAP`, `REPEATED_FUNCTION` = red in classical, blue in pop/mariachi.

**Implemented:** `TRITONE_RESOLUTION_IMPROPER` (red), `TRITONE_RESOLUTION_SUBOPTIMAL` (blue).

---

## 4. Auditor Update (Completed)

1. ✅ **Extended `validate_solution()`** to detect vii°7→I, vii°→I, ii°7→V transitions.
2. ✅ **Check tritone pairs** — improper → red, suboptimal → blue.
3. ✅ **RULE_PATTERNS / ERROR_CODE_HINTS** in `ingest.py` and `knowledge_rules.py`.
4. Theory chunks: RAG retrieval uses existing tritone-related chunks (DOMINANT_FUNCTION, etc.) plus ERROR_CODE_HINTS for `TRITONE_RESOLUTION_IMPROPER`.
5. ✅ **Tritone penalty in `calculate_transition_cost()`** — improper ~12×, suboptimal ~2×.

---

## 5. GitHub Issues

**Search:** `Tritone Resolution BackendTest`, `Viterbi weightings BackendTest`  
**Result:** No open issues found. (Search was broad; if using a specific repo, qualify with `repo:owner/BackendTest`.)

---

## 6. References

- Milne Publishing, *Fundamentals, Function, and Form*: Ch. 17 (vii°), Ch. 20 (Fully-diminished Seventh Chords)
- MusicTheoryManual: "A4 will resolve out, d5 in"
- Open Music Theory: tritone, diminished seventh, voice leading
- Engine: `core_engine.py` (`validate_solution`, `calculate_transition_cost`), `backend/services/validate.py`
