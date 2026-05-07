# AI-as-Consultant Interaction Model

**Date:** March 3, 2025  
**Scope:** Defines how HarmonyForge positions AI as an advisor, not an editor. Supports research framing around **AI-Augmented Creativity** and **Explanatory AI (XAI) for Music**.

---

## 1. Core Principle

**The AI never edits or generates music on behalf of the user.** The user remains the sole creative agent. The AI acts as a **consultant**: it explains, suggests, and educates—but all changes to the score are made by the human.

---

## 2. Research Framing

| Concept | Description |
|--------|-------------|
| **AI-Augmented Creativity** | The AI augments the user's creative process by providing feedback and understanding, without replacing human decision-making. |
| **Explanatory AI (XAI) for Music** | The system explains *why* the algorithmic engine flagged something and *how* to fix it, grounded in music theory sources. |
| **Publishable design** | The interaction model (explain, suggest, advise) is visible and documentable. The generative algorithm (DAG solver, cost weights) can remain proprietary. |

---

## 3. Interaction Boundaries

| AI does | AI does not |
|---------|-------------|
| Explain why a passage was flagged (red/blue) | Edit notes, chords, or voicings |
| Suggest fixes based on theory | Apply changes to the score |
| Retrieve and cite theory sources | Override user edits |
| Answer questions about the current score | Generate harmonies without user approval |
| Provide reasoning steps and severity | Make creative decisions |

---

## 4. Implemented Flow: TheoryInspector

The **TheoryInspector** (`/api/theory-inspect`) embodies the AI-as-Consultant model:

1. **Leader** — Classifies user intent (explanation vs. validation)
2. **Auditor** — Runs deterministic symbolic tools (intervals, parallels, key, Roman numerals)
3. **RAG** — Retrieves grounded theory chunks from Open Music Theory and methodology sources
4. **Tutor** — Returns explanation with reasoning steps, severity, and cited sources

**Output:** Text and structured data. No edits to the score.

---

## 5. User Journey

1. User uploads melody → **Engine** generates harmonies (deterministic, no AI).
2. User sees red/blue flags → **Engine** validates; flags are deterministic.
3. User asks "Why is this flagged?" or "How do I fix it?" → **TheoryInspector** explains and suggests.
4. User edits the score → Human applies changes; AI never touches the score.

---

## 6. Design Rationale

- **Trust:** Users see *why* something was flagged and can verify against cited sources.
- **Control:** The musician retains full creative authority.
- **Education:** Explanations are grounded in real theory, supporting learning.
- **Research:** The interaction design can be published without exposing the solver internals.
