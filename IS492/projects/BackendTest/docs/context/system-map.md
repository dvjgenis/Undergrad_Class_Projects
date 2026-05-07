# HarmonyForge System Map

**The 3-Phase Pipeline**

---

## Phase I: Generation (Logic Core)

| Step | Component | Role |
|------|-----------|------|
| 1 | Parse | `engine/io_handler.py` — MusicXML → melody, chords, meta |
| 2 | Merge | `engine/hierarchical_bridge.py` — Beat-aligned chords |
| 3 | Solve | `engine/core_engine.py` — DAG + Viterbi SATB path |
| 4 | Validate | `engine/core_engine.py` — Red/blue violation codes |

**Output:** Theoretically valid SATB MusicXML with violation annotations.

---

## Phase II: Repair / Refinement (Tactile Sandbox)

| Step | Component | Role |
|------|-----------|------|
| 1 | Render | `harmony-forge-redesign` — VexFlow score display |
| 2 | Edit | User drags notes, changes inversions, adds NCTs |
| 3 | Re-validate | `POST /api/validate` — Updated red/blue highlights |
| 4 | Export | `POST /api/export` — MusicXML or PDF |

**Principle:** Edit-Authority. User applies all changes; AI never touches the score.

---

## Phase III: Explainability (Theory Inspector)

| Step | Component | Role |
|------|-----------|------|
| 1 | Leader | Classifies intent (explanation vs validation) |
| 2 | Auditor | Symbolic tools (intervals, parallels, key, Roman numerals) |
| 3 | RAG | Fusion retrieval from theory chunks |
| 4 | Tutor | Ante-hoc explanation with reasoning steps, severity, sources |

**Endpoint:** `POST /api/theory-inspect`

---

## Data Flow

```
MusicXML (upload) → Engine (solve) → MusicXML (harmonized)
                         ↓
User edits (sandbox) → Validate → Red/Blue highlights
                         ↓
User asks "Why?" → Theory Inspector → Explanation (no edits)
```