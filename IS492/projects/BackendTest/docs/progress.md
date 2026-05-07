# HarmonyForge Progress (RALPH Loop)

**The Pulse** — State tracker for Reasoning, Action, Learning, Progression, History.

---

## RALPH Log

Document solver performance, constraint-handling failures, and context handover points here.

### 2026-03-07: App Run Fix (Next.js uv_interface_addresses)

- **Reasoning:** `make dev` failed: backend "Address already in use"; frontend crashed on `uv_interface_addresses Unknown system error 1` when `os.networkInterfaces()` failed in restricted environments.
- **Action:** Patched `next/dist/lib/get-network-host.js` via patch-package (try-catch around `networkInterfaces()`); added `-H 127.0.0.1` to Next.js dev script; added postinstall for patch-package.
- **Learning:** Next.js calls `os.networkInterfaces()` without error handling; patch-package persists the fix across npm install.
- **Progression:** None.
- **History:** `harmony-forge-redesign/patches/next+16.1.6.patch`, `harmony-forge-redesign/package.json`, `docs/progress.md`

### 2026-03-07: Engine–TheoryInspector Boundary Refactor

- **Reasoning:** Engine imported TheoryInspector for index building; violated Axiomatic Core / LLM layer separation.
- **Action:** Removed `ensure_index_built` from engine. Backend builds index at startup; engine consumes CSV when present or falls back to `knowledge_base/*.txt`. Added ADR 0003, optional LLM Tutor (`TI_USE_LLM_TUTOR`).
- **Learning:** Engine is now fully independent of TheoryInspector. Theory Inspector remains deterministic by default.
- **Progression:** None.
- **History:** `engine/main.py`, `engine/knowledge_rules.py`, `TheoryInspector/orchestrator.py`, `TheoryInspector/settings.py`, `docs/adr/0003-theory-inspector-deterministic-implementation.md`

### 2026-03-07: Week 7/8 GitHub Issues (Milestone 3 & 4)

- **Reasoning:** Address open Week 7/8 issues for M3 and M4; close when done; create follow-ups.
- **Action:** Closed #72 (VexFlow + POUR) with implementation summary. Closed #73 (Engine quality validation) with test run log, quality assessment, refinement recommendations in `docs/Engine-Test-Run-Log.md`. Created #74 (Engine refinement sprint) and #75 (Accessibility: skip link, contrast) labeled Week 7.
- **Learning:** M4 VexFlow scope complete; M3 test log identified parameter tuning and solver improvements as next sprint.
- **Progression:** None.
- **History:** GitHub issues #72–#75, `docs/Engine-Test-Run-Log.md`

### 2026-03-07: MVP Flow

- **Reasoning:** Ensure working MVP: upload → harmonize → sandbox → export.
- **Action:** Added sample lead sheet (`public/sample-lead-sheet.xml`), "Try with sample lead sheet" button on home, live score preview on document page, corrected UploadPromptContent to "MusicXML (.xml)".
- **Learning:** Harmonize pipeline works with melody-only input (chord inference). Engine output renders in VexFlow.
- **Progression:** User can run `make dev` (Node >= 20.9) and test full flow.
- **History:** `harmony-forge-redesign/src/app/page.tsx`, `ScorePreviewPanel.tsx`, `UploadPromptContent.tsx`, `public/sample-lead-sheet.xml`, `README.md`

### 2026-03-07: Note Editor Industry Parity

- **Reasoning:** Align with MuseScore/Flat/Dorico keyboard shortcuts and UX patterns.
- **Action:** Added industry-standard shortcuts: Esc (exit draw), ↑↓ (semitone), ⌘↑↓ (octave), 1–6 (duration), Delete/Backspace (delete). Created `docs/Note-Editor-Feature-Comparison.md`.
- **Learning:** MuseScore uses 1–9 for duration; we use 1–6 (whole→32nd). Arrow pitch + Ctrl octave is universal.
- **Progression:** None.
- **History:** `sandbox/page.tsx`, `docs/Note-Editor-Feature-Comparison.md`

### 2026-03-07: Tactile Sandbox Gaps (Remaining Editor Features)

- **Reasoning:** PRD Must Have #5 (Audio Playback) and Core Use Case 2 (drag, add notes) required parity with MuseScore/Noteflight.
- **Action:** Implemented: (1) Real playback via Tone.js; (2) Drag-to-move notes (vertical = pitch); (3) Add notes (draw mode, N key, context menu); (4) Cut/Copy/Paste with clipboard; (5) Multi-select (shift-click); bulk pitch/duration/delete for multi-select.
- **Learning:** Tone.js works with MusicXML→scheduled notes. VexFlow drag needs onNotePitchDrag callback. Draw mode uses partIndex from click Y. Paste inserts at measure 0 start.
- **Progression:** None.
- **History:** `harmony-forge-redesign/src/lib/playback.ts`, `musicxml-editor.ts`, `VexFlowScoreRenderer.tsx`, `ScoreCanvas.tsx`, `sandbox/page.tsx`, `useScoreEditorStore.ts`, `SandboxContextMenu.tsx`

### 2026-03-07: PDF/MIDI Input Support

- **Reasoning:** Users may have scores in PDF or MIDI; need conversion to MusicXML for harmonize flow.
- **Action:** Added `POST /api/convert`, `backend/services/convert.py` (MIDI via music21, PDF via Audiveris). Frontend accepts .pdf, .mid, .midi; calls convert API when needed. "Try MIDI sample" button.
- **Learning:** music21 MIDI→MusicXML works with temp files. PDF requires Audiveris (OMR) on PATH.
- **Progression:** None.
- **History:** `backend/services/convert.py`, `backend/main.py`, `backend/schemas.py`, `harmony-forge-redesign/src/app/page.tsx`, `api.ts`, `DropzoneCopy.tsx`, `UploadPromptContent.tsx`, `API_INTEGRATION.md`, `public/sample-lead-sheet.mid`

### 2026-03-07: Dev Environment & Single-Server Integration

- **End goal:** App runs without errors; frontend and backend fully integrated on one server; users see a responsive UI (no white screen).
- **Approach:** Fix Python deps, unify on port 3000 via Next.js proxy, fix Next.js/Tailwind resolution, add loading UX during compilation.
- **Steps done:**
  1. **Cursor rules:** Updated `architecture.mdc` to Senior Context Engineer Protocol; created `testing.mdc`.
  2. **GitHub issues (Week 8):** Created #76 (RAG taxonomy per genre), #77 (push to GitHub before Spring break), #78 (Spring break tasks for Muawiz and Yiren).
  3. **Port conflicts:** Added `make dev-clean` to kill processes on 8000, 3000, 3001.
  4. **Single-server:** Next.js rewrites proxy `/api/*` and `/health` to backend; frontend uses same-origin (`API_BASE = ""`); `wait-on` ensures backend is up before frontend starts; backend `/health` accepts GET and HEAD.
  5. **Python deps:** Added `make install`; README updated for `ModuleNotFoundError: No module named 'fastapi'` (pyenv vs system Python mismatch).
  6. **Tailwind resolution:** Next.js was resolving from project root (`BackendTest`) instead of `harmony-forge-redesign`. Changed `dev:frontend` to `(cd harmony-forge-redesign && npm run dev)`; removed `turbopack.root` (it caused wrong module resolution).
  7. **Loading UX:** Added `harmony-forge-redesign/src/app/loading.tsx` — spinner and "Loading HarmonyForge…" while page compiles.
- **Fix (2026-03-07):** Patched Next.js `get-network-host.js` (patch-package) to catch `os.networkInterfaces()` failures; added `-H 127.0.0.1` to dev script. App now starts successfully.
- **History:** `Makefile`, `package.json`, `harmony-forge-redesign/next.config.ts`, `harmony-forge-redesign/src/lib/api.ts`, `backend/main.py`, `harmony-forge-redesign/src/app/loading.tsx`, `harmony-forge-redesign/src/app/page.tsx`, `harmony-forge-redesign/src/app/document/page.tsx`, `README.md`

### Format

- **Reasoning:** What was the hypothesis or problem?
- **Action:** What was done?
- **Learning:** What was discovered?
- **Progression:** Next steps.
- **History:** Timestamp, files touched.

---

## Example Entry

**Date:** YYYY-MM-DD

**Reasoning:** Solver hit performance bottleneck on Schenkerian hierarchy evaluation for long phrases.

**Action:** Profiled `_build_layers()`; identified column candidate explosion.

**Learning:** `MAX_COLUMN_CANDIDATES` cap is reached at phrase boundaries; need pruning heuristic.

**Progression:** Add cadence-anchor pruning before full DAG build.

**History:** `engine/core_engine.py`, `engine/hierarchical_bridge.py`

---

## Context Handover

When performing a "Context Bankruptcy" reset, summarize:

1. Current state of VexFlow tactile sandbox
2. Theory Inspector sidebar files to pin for fresh session
3. Blockers or open questions

---

## State Handover (2026-03-07)

### Current Status

| Area | State | Notes |
|------|-------|------|
| **Engine–TheoryInspector boundary** | ✅ Done | Engine has no LLM calls; TI builds index at startup. ADR 0003. |
| **Tactile Sandbox (VexFlow)** | ✅ Done | Note-level editing, playback, drag, draw, multi-select, cut/copy/paste, keyboard shortcuts. #72 closed. |
| **Engine quality validation** | ✅ Done | Test run log in `docs/Engine-Test-Run-Log.md`. #73 closed. |
| **MVP flow** | ✅ Done | Upload → harmonize → sandbox → export. Sample lead sheet, PDF/MIDI convert. |
| **Single-server dev** | ✅ Done | One port (3000), proxy to backend. App runs via `make dev`. Patched Next.js `get-network-host.js` for `uv_interface_addresses` crash in restricted envs; `-H 127.0.0.1` for dev. |
| **Logic Core refinement** | 🔄 Next | #74: parameter tuning, cadence-anchor pruning, scale heuristic. |
| **Accessibility (POUR)** | 🔄 Next | #75: skip link, contrast audit, focus rings. |
| **Theory Inspector** | 🔄 Ongoing | Leader → Auditor → RAG → Tutor; score_delta passed for RAG. |
| **Export** | 🔄 Ongoing | MusicXML, PDF (MuseScore/LilyPond on PATH). |

### Key Paths

- **Engine:** `engine/main.py`, `engine/core_engine.py`, `engine/io_handler.py`
- **Frontend sandbox:** `harmony-forge-redesign/src/app/sandbox/page.tsx`, `VexFlowScoreRenderer.tsx`, `useScoreEditorStore.ts`
- **Theory Inspector:** `TheoryInspector/orchestrator.py`, `harmony-forge-redesign/src/components/organisms/TheoryInspectorPanel.tsx`
- **Dev integration:** `package.json` (dev:frontend), `harmony-forge-redesign/next.config.ts` (rewrites), `harmony-forge-redesign/src/app/loading.tsx`
- **Docs:** `docs/PRD.md`, `docs/Algorithmic-Backend-Architecture.md`, `docs/Engine-Test-Run-Log.md`

### Open GitHub Issues (Week 7–8)

- **#74** (M3): Engine refinement sprint — parameter tuning, solver improvements
- **#75** (M4): Accessibility — skip link, contrast verification
- **#76** (M3): RAG taxonomy per genre (smaller context)
- **#77** (M6): Push to GitHub before Spring break
- **#78** (M6): Spring break tasks for Muawiz and Yiren