# ADR 0001: Axiomatic Logic Over Stochastic Generation

**Status:** Accepted  
**Date:** March 2026  
**Context:** HarmonyForge PRD, user research (21 participants, 633 codes)

---

## Decision

The Logic Core uses **deterministic constraint-satisfaction** (CSP, layered DAG + Viterbi) for SATB harmonization. We do **not** use probabilistic/neural models (e.g., Anticipatory Music Transformer, DeepBach) for generation.

---

## Rationale

### Structural Drift

Probabilistic models produce parallel fifths, voice-crossing, and other theoretically invalid outputs. Musicians must proofread every note, negating efficiency gains (the "Forced Auditing Loop").

### User Evidence

- **15/21** participants preferred algorithmic logic over black-box, pattern-based AI.
- Trust hinges on "laws of music theory" (P9, P19).

### Copyright Safety

Rule-based core; no training on copyrighted datasets (e.g., Lakh MIDI).

---

## Consequences

- **Engine:** Python CSP solver in `engine/`. Hard rules (voice order, spacing, tritone resolution) and soft rules (leading tone, leaps) are explicit and auditable.
- **Latency:** Deterministic solve is predictable; no sampling variance.
- **Explainability:** Violations map to known codes; Theory Inspector can cite theory sources.