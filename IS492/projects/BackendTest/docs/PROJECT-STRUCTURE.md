# HarmonyForge Project Structure

**PRD:** `docs/PRD.md` | **Context:** `docs/context/system-map.md` | **ADRs:** `docs/adr/`

---

## Canonical Entry Point

**Use `backend.main:app`** for frontend integration:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints: `/api/harmonize`, `/api/validate`, `/api/theory-inspect`, `/api/export`, `/api/presets`, `/health`.

---

## Two API Implementations

| Module | Entry | Theory Endpoint | Sessions |
|--------|-------|-----------------|----------|
| **backend/main.py** | `backend.main:app` | `/api/theory-inspect` | No |
| **api/app.py** | `api.app:app` | `/api/chat` | Yes |

**Recommendation:** Use `backend.main` — it matches `API_INTEGRATION.md` and is the documented integration path. The `api/` module provides session-based state for alternative frontend flows.

---

## Core Directories

| Path | Role |
|------|------|
| `engine/` | Logic Core — `core_engine.py` (CSP solver), `io_handler.py`, `hierarchical_bridge.py`, `knowledge_rules.py` |
| `backend/` | FastAPI app, Pydantic schemas, `services/validate.py`, `services/export.py` |
| `TheoryInspector/` | RAG retriever, symbolic tools, Leader→Auditor→RAG→Tutor orchestration |
| `api/` | Alternative API with session store |
| `docs/` | PRD, ADRs, context, plan, progress |
| `eval/` | HER calculator, telemetry (Repair Efficiency, CSI, SUS, NPS) |
| `knowledge_base/` | Open Music Theory, methodology PDFs (ingested by TheoryInspector) |

---

## Pipeline Flow

1. **Parse** — `io_handler.parse_xml_string()` → melody, chords, meta
2. **Merge** — `hierarchical_bridge.merge_backend_hierarchical_plan()` → beat-aligned chords
3. **Solve** — `core_engine.solve_harmony()` → SATB path
4. **Validate** — `core_engine.validate_solution()` → violations
5. **Export** — `io_handler.export_xml_string()` → MusicXML
