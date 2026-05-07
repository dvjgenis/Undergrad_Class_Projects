# HarmonyForge

**Human–AI co-creation for SATB harmonization.** A Glass Box system that replaces probabilistic music generation with deterministic logic, tactile editing, and ante-hoc explainability.

---

## Overview

HarmonyForge addresses the **Repair Phase Bottleneck**: time saved by AI generation is lost to forced auditing of opaque outputs. It provides:

- **Logic Core** — CSP-based SATB harmonization (HarmonySolver blueprint)
- **Tactile Sandbox** — Edit-Authority; musicians add Human Flair
- **Theory Inspector** — LLM-driven explanations, Red Line validation (ComposerX Reviewer Agent pattern)

See [`docs/PRD.md`](docs/PRD.md) for full requirements and design.

---

## Quick Start

### Full stack (frontend + backend)

**Requirements:** Node.js >= 20.9, Python 3.10+

```bash
# One-time setup (use same Python that runs make dev — e.g. pyenv 3.12)
make install
# or: python3 -m pip install -r requirements.txt
npm install
cd harmony-forge-redesign && npm install && cd ..

# Run both (single server: frontend proxies API to backend)
make dev
# or: npm run dev
```

**Single server:** Open **http://localhost:3000** only. The frontend proxies `/api/*` and `/health` to the backend. No need to visit port 8000. Upload **MusicXML** (.xml), **PDF** (.pdf), or **MIDI** (.mid, .midi). PDF and MIDI are converted to MusicXML automatically. Or click **Try XML sample** / **Try MIDI sample**.

### Backend only

```bash
pip install -r requirements.txt
make dev-backend
# or: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Endpoints:** `/api/convert` (PDF/MIDI→XML), `/api/harmonize`, `/api/validate`, `/api/theory-inspect`, `/api/export`, `/api/presets`, `/health`

**PDF conversion** requires [Audiveris](https://github.com/Audiveris/audiveris) on PATH. **MIDI** uses music21 (built-in).

**Theory Inspector** runs deterministically (RAG + symbolic tools) without API keys. To enable optional LLM enrichment: copy `.env.example` to `.env`, add `ANTHROPIC_API_KEY` (or OpenAI/Groq), and set `TI_USE_LLM_TUTOR=true`. See [`docs/Theory-Inspector-Integration.md`](docs/Theory-Inspector-Integration.md).

See [`API_INTEGRATION.md`](API_INTEGRATION.md) for request/response formats.

---

## Project Structure

| Path | Role |
|------|------|
| `harmony-forge-redesign/` | Next.js frontend — upload, harmonize, sandbox, Theory Inspector |
| `engine/` | Logic Core — CSP solver, voice-leading, validation |
| `backend/` | FastAPI app, schemas, validate/export services |
| `TheoryInspector/` | RAG + symbolic tools, Leader→Auditor→RAG→Tutor flow |
| `api/` | Alternative API (session-based, `/api/chat`) |
| `docs/` | PRD, ADRs, context, plan, progress |
| `eval/` | HER calculator, telemetry (Repair Efficiency, CSI, SUS, NPS) |
| `tools/` | LangGraph, RAG techniques, UI/UX resources |

**Canonical API:** `backend.main:app` — use this for frontend integration.

---

## Makefile (The Commander)

Use these commands for execution and evaluation. Do not rely on ad-hoc commands:

| Command | Purpose |
|---------|---------|
| `make dev` | Full stack (frontend + backend) |
| `make dev-backend` | Backend only |
| `make dev-frontend` | Frontend only |
| `make test-solver` | Engine/solver tests |
| `make calc-her` | Harmonic Error Rate (music21) |
| `make eval-telemetry` | Telemetry scripts info |
| `make health` | Health check (backend must be running) |

---

## Documentation

| Path | Purpose |
|------|---------|
| **docs/PRD.md** | Product requirements, Must Have features |
| **docs/adr/** | Architectural Decision Records |
| **docs/context/** | System map, product spec |
| **docs/plan.md** | Implementation blueprint |
| **docs/progress.md** | RALPH loop state tracker |
| **docs/Algorithmic-Backend-Architecture.md** | Solver, validation codes |
| **docs/Theory-Inspector-Integration.md** | Theory Inspector, env vars, LLM setup |
| **docs/AI-as-Consultant-Interaction-Model.md** | Theory Inspector boundaries |

---

## Cursor Rules

`.cursor/rules/` enforces the Glass Box methodology:

- **architecture.mdc** — Strict separation of Axiomatic Core and LLM layers
- **frontend_sandbox.mdc** — Tactile Sandbox (Next.js, VexFlow)
- **backend_logic.mdc** — Engine (CSP solver)
- **ai_council.mdc** — Theory Inspector (LLM agents)
- **evaluation.mdc** — HER, telemetry
