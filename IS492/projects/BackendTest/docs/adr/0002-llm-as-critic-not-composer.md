# ADR 0002: LLM as Critic, Not Composer

**Status:** Accepted  
**Date:** March 2026  
**Context:** ComposerX Reviewer Agent (Deng et al., 2024), Zhou et al. (2024), AI-as-Consultant model

---

## Decision

The LLM layer (Theory Inspector) is **solely a critic and tutor**. It explains, suggests, and educates. It **never** edits or generates music on behalf of the user.

---

## Rationale

### LLM Strengths and Weaknesses

- **LLMs excel at reasoning** — explaining why a passage was flagged, citing theory.
- **LLMs fail at generation** — token prediction produces structural drift (parallel fifths, voice-crossing).

### Edit-Authority

The user remains the sole creative agent. AI provides scaffolding, not automation. See Cococo (Louie et al., 2020) — Expressive Sovereignty.

### Research Framing

- **AI-Augmented Creativity:** AI augments the process without replacing human decision-making.
- **Explanatory AI (XAI) for Music:** Explains *why* the engine flagged something and *how* to fix it.

---

## Consequences

- **Input to LLM:** JSON score deltas (error codes, measure, voices) + MusicXML for context.
- **Output:** Text and structured data. No edits to the score.
- **Implementation:** `TheoryInspector/` — Leader → Auditor → RAG → Tutor. Auditor runs symbolic tools; Tutor returns explanations with sources.