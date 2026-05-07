# HarmonyForge Product Requirements Document (PRD)

**Version:** 1.0  
**Last Updated:** March 2026  
**Sources:** HF LitReview NotebookLM (56 sources), Thematic Analysis (21 participants, 633 codes), SALT Lab Prompt Sheet

---

## 1. Executive Summary

**HarmonyForge** is a human–AI co-creation system for SATB (Soprano, Alto, Tenor, Bass) harmonization that replaces probabilistic “Black Box” music generation with a **Glass Box** architecture: deterministic logic, tactile editing, and ante-hoc explainability. It addresses the **Repair Phase Bottleneck**—where time saved by AI generation is lost to forced auditing—by providing a theoretically valid foundation that musicians can edit with full authority.

**Core Value Proposition:** A “Jumping Pad” that preserves Expressive Sovereignty, reduces Mechanical Toil, and builds Deductive Trust through transparent, rule-based generation and an LLM-driven Theory Inspector.

---

## 2. Problem Statement

### 2.1 The Gigging Musician Bottleneck

- Chamber groups and band ensembles operate under **Time-Crunch** scenarios.
- Arrangements for **Random Ensembles** (e.g., violin substituting for cello) require substantial **Mechanical Toil**: manual transcription, clef transposition, key changes.
- This administrative labor blocks repertoire expansion and collective jamming.

### 2.2 The Reliability Crisis in Generative AI

Current SOTA probabilistic models (e.g., Anticipatory Music Transformer, DeepBach) fail in three ways:

| Failure Mode | Description |
|--------------|-------------|
| **Structural Drift** | Probabilistic guessing leads to parallel fifths, voice-crossing, and other theoretically invalid outputs. |
| **Forced Auditing Loop** | Opaque logic forces musicians to proofread every note, negating efficiency gains. |
| **Loss of Expressive Sovereignty** | Users feel like passive recipients; AI does too much without a “Jumping Pad” for human flair (Louie et al., 2020). |

### 2.3 Evidence from User Research

From 21 musician interviews (633 initial codes, 9 Must Have features):

- **18/21** participants demanded a collaborative phase with manual editing.
- **15/21** preferred algorithmic logic over black-box, pattern-based AI.
- **16/21** identified part availability as a barrier (The Logistical Filter).
- **12/21** described mental exhaustion from transposition and clef reading (The Strenuous Reward).

---

## 3. Solution Overview

### 3.1 Three-Stage Architecture

| Stage | Name | Purpose |
|-------|------|---------|
| **I** | **Logic Core (Generation)** | Deterministic CSP-based SATB harmonization; theoretically valid foundation. |
| **II** | **Tactile Sandbox (Repair)** | Direct-manipulation editor; Edit-Authority; human flair injection. |
| **III** | **Theory Inspector (Explainability)** | LLM-driven ante-hoc explanations; Red Line validation; pedagogical partner. |

### 3.2 Design Principles

- **Glass Box over Black Box** (Liu et al., 2025): Ante-hoc transparency as a socio-technical necessity.
- **Edit-Authority**: User remains primary creative steward; AI provides scaffolding, not automation.
- **Copyright Safety by Design**: Rule-based core; no training on copyrighted datasets (e.g., Lakh MIDI).
- **Musically Honest**: Outputs adhere to canonical music theory (Fux, Aldwell-Schachter, Caplin).

---

## 4. User Personas & Use Cases

### 4.1 Primary Personas

| Persona | Needs | Key Scenario |
|---------|-------|--------------|
| **Gigging Musician** | Fast, reliable arrangements for Random Ensembles; time-crunch. | Violinist must cover cello part for tonight’s gig. |
| **Music Educator / Student** | Theory Inspector as scaffolding partner; learn why, not just what. | Student asks “Why is this note marked red?” |
| **Chamber Ensemble Coordinator** | Repertoire expansion; reduce Mechanical Toil; enable collective jamming. | Add ad-hoc instruments to existing arrangements. |

### 4.2 Core Use Cases

1. **Upload lead sheet** (melody + chords) → receive theoretically valid SATB arrangement.
2. **Edit notes** in Tactile Sandbox (drag, change inversions, add non-chord tones).
3. **Query Theory Inspector** (“Why is this parallel fifth?”) → receive ante-hoc explanation.
4. **Export** MusicXML/PDF for rehearsal and performance.

---

## 5. Must Have Features (MoSCoW)

*Derived from thematic analysis across KriukowTA, ZambranoTA, and Braun-Clarke TA.*

### 5.1 Must Have (9 features)

| # | Feature | Evidence |
|---|---------|----------|
| 1 | **Manual Editing & Repair Workspace** | 18/21 participants; P4: “I like that idea where you can also edit… it’s collaborative.” |
| 2 | **Algorithmic Theory-Based Generation** | P9, P19: “deterministic logic” over probabilistic AI; trust hinges on “laws of music theory.” |
| 3 | **Theory Inspector / Explainability** | P20: “Chatbot will be a way for them to actually learn why the engine made the decisions.” |
| 4 | **Accurate File Export (XML/PDF)** | ZambranoTA; P15: current tools lose symbols or move ranges during export. |
| 5 | **Audio Playback Verification** | Braun-Clarke; musicians who learn by ear need to verify if arrangement “sounds right.” |
| 6 | **Chord Charts & Tablature Output** | Braun-Clarke; critical for gigging, worship, garage band musicians who don’t read staff notation. |
| 7 | **Multi-Instrument Selection** | The Logistical Filter; part availability affects participation. |
| 8 | **Theory Validation (Red Line)** | P9, P11, P19: side-panel explaining harmonic choices (e.g., “Avoided parallel fifths here”). |
| 9 | **Cross-Platform Accessibility** | ZambranoTA; essential for rehearsals. |

### 5.2 Should Have

- Timbre-preserving playback (80s synths, custom choir).
- Expressive markings (slurs, accents, crescendos, bowing) during edit phase.
- Mode toggling: Strict Mode (pedagogical) vs Creative Mode (minimal interruption).

### 5.3 Could Have

- Stylist agent: “Make this cadence more Brahms-ian.”
- Chord charts and guitar/ukulele tablature.

---

## 6. Technical Architecture

### 6.1 Logic Core (Generation)

- **Blueprint:** HarmonySolver (Dajda et al., 2020)—CSP over layered graphs for functional SATB.
- **Structure:** SchenkComposer-inspired Global Planning (Hahn et al., 2023)—Schenkerian hierarchy for cadential planning; “Schenkerian Lite” to avoid latency.
- **Implementation:** Backtracking constraint solver (Python); layered DAG + Viterbi shortest path; hard rules (parallel fifths, voice ranges) + soft rules (voice-leading penalties).
- **Input:** Lead sheet (melody + chords); MusicXML/MIDI.
- **Output:** Theoretically valid SATB MusicXML.

### 6.2 Tactile Sandbox (Repair)

- **Stack:** Next.js, React, Tailwind CSS; VexFlow or OpenSheetMusicDisplay for notation.
- **Capabilities:** Note-level direct manipulation; drag notes, change inversions, add NCTs.
- **Principle:** Edit-Authority; user overrides deterministic logic with Human Flair.

### 6.3 Theory Inspector (Explainability)

- **Blueprint:** ComposerX Reviewer Agent (Deng et al., 2024); Zhou et al. (2024)—LLMs excel at reasoning, fail at generation.
- **Agents:** Auditor (validation), Tutor (explanations), Stylist (creative translation).
- **Implementation:** OpenAI GPT-4o; LangChain/LangGraph; score-delta analysis.
- **UI:** Red Line validation; side-panel chatbot; ante-hoc explanations.

---

## 7. Success Criteria & Metrics

### 7.1 Quantitative

| Metric | Target | Method |
|--------|--------|--------|
| **Repair Efficiency** | Significant reduction vs baseline (notation editor + raw GPT-4 MIDI) | Timed within-subjects study |
| **Harmonic Error Rate (HER)** | 0% parallel fifths, voice-crossing | music21 (Python) |
| **Latency-Utility Threshold** | < 4 minutes to performance-ready | Custom telemetry |
| **NPS** | Positive (adoption likelihood) | Survey |

### 7.2 Qualitative

| Metric | Method |
|--------|--------|
| **Perceived Agency** | Thematic coding (Edit-Authority, Expressive Sovereignty) |
| **Creativity Support Index (CSI)** | Tchemeube et al. (2025)—Results Worth Effort |
| **SUS (adapted)** | Interpretability and Agency sub-scales |
| **Pedagogical Growth** | Pre/post tests for Theory Inspector effectiveness |

---

## 8. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| **Theory Inspector “Nagging”** | Mode Toggling: Strict vs Creative; Tutor speaks only when prompted in Creative Mode. |
| **Robotic rigidity of axiomatic output** | Timbre-preserving playback; Stylist agent for decorations; user adds Human Flair. |
| **Schenkerian complexity / latency** | Schenkerian Lite: cadential planning only; foreground to user. |
| **LLM latency** | LangGraph; delta-analysis on changed measures only. |

---

## 9. Out of Scope (Explicitly Excluded)

- Full Schenkerian recursive analysis in real-time.
- Audio synthesis / waveform generation (symbolic only).
- Training on copyrighted datasets.
- Full automation without user edit phase.

---

## 10. References (Key Sources from HF LitReview)

- **HarmonySolver:** Dajda et al. (2020)—CSP, layered graphs, SATB.
- **SchenkComposer:** Hahn et al. (2023)—Schenkerian hierarchy, PCFG.
- **ComposerX:** Deng et al. (2024)—Reviewer Agent, multi-agent orchestration.
- **Cococo:** Louie et al. (2020)—Expressive Sovereignty, Edit-Authority.
- **Glass Box:** Liu et al. (2025)—Ante-hoc explainability.
- **MusicAIR:** Liao et al. (2025)—Deterministic over deep learning.
- **Zhou et al. (2024):** LLMs as theorists, not generators.
- **Tchemeube et al. (2025):** CSI for Repair Phase evaluation.

---

## Appendix: Research Questions

- **Main RQ:** To what extent does replacing probabilistic generation with deterministic logic and explainable critique enhance musician agency and trust when arranging lead sheets for non-standard ensembles?
- **RQ1:** How do limitations in part availability affect musicians’ participation and satisfaction?
- **RQ2:** What are current manual practices and pain points for adapting music?
- **RQ3:** How do musicians perceive algorithmic/AI tools in the arrangement process?
- **RQ4:** What features and guardrails are required for a human-centric music arrangement tool?
