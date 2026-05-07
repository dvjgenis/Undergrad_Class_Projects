"""
HarmonyForge Unified API
========================

Phase 1 — POST /api/harmonize    : upload MusicXML + presets → harmonized score
Phase 3 — POST /api/validate     : live-edit validation → red/blue annotations
Phase 3 — POST /api/chat         : theory chatbot (RAG, explain & suggest only)
Phase 4 — POST /api/export       : download harmonized score in PDF / XML / MIDI
         GET  /api/health        : readiness probe
"""

from __future__ import annotations

import io
import os
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIR = PROJECT_ROOT / "engine"

sys.path.insert(0, str(ENGINE_DIR))

from api.models import (
    Annotation,
    ChatRequest,
    ChatResponse,
    ExportRequest,
    HarmonizeRequest,
    HarmonizeResponse,
    ValidateRequest,
    ValidateResponse,
)
from api.sessions import SessionStore
from api.genre_nuance import detect_genre_nuances

# ── Engine imports (engine/ uses flat relative imports) ─────────
from io_handler import parse_xml_string, export_xml_string  # type: ignore[import-untyped]
from core_engine import (  # type: ignore[import-untyped]
    build_schenkerian_graph_matrix,
    enrich_violations_with_measures,
    solve_harmony,
    validate_solution,
)
from hierarchical_bridge import merge_backend_hierarchical_plan  # type: ignore[import-untyped]
from settings import EngineSettings  # type: ignore[import-untyped]


app = FastAPI(
    title="HarmonyForge API",
    version="0.2.0",
    description="Backend for the four-phase HarmonyForge workflow.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = SessionStore()

# ── TheoryInspector (lazy init to keep startup fast) ────────────
_inspector = None


def _get_inspector():
    global _inspector
    if _inspector is not None:
        return _inspector
    try:
        from TheoryInspector.config import TheoryInspectorConfig
        from TheoryInspector.ingest import build_chunks_index
        from TheoryInspector.retriever import TheoryRetriever
        from TheoryInspector.tools_registry import MusicTheoryTools
        from TheoryInspector.orchestrator import TheoryInspectorOrchestrator
        from TheoryInspector.settings import load_llm_settings

        cfg = TheoryInspectorConfig.from_project_root(PROJECT_ROOT)
        if not cfg.chunks_csv.exists():
            build_chunks_index(cfg)
        chroma_dir = Path(os.getenv("TI_CHROMA_DIR", str(cfg.chroma_dir)))
        retriever = TheoryRetriever(cfg.chunks_csv, chroma_dir)
        llm_settings = load_llm_settings(cfg.env_file)
        _inspector = TheoryInspectorOrchestrator(retriever, MusicTheoryTools(), llm_settings)
    except Exception:
        _inspector = None
    return _inspector


# ── Helpers ─────────────────────────────────────────────────────

def _run_engine(musicxml: str, mood: str, genre: str, difficulty: str, instruments: list[str]):
    """Run the full harmonization pipeline and return (xml_str, solution, violations, nuances, meta)."""
    settings = EngineSettings(mood=mood, genre=genre, difficulty=difficulty)
    source_score, melody, chords, durations, meta = parse_xml_string(musicxml, settings)

    if not melody or not chords:
        raise HTTPException(status_code=422, detail="Could not extract notes from the MusicXML.")

    diatonic = set(meta.get("diatonic_pcs", []))
    forbidden_accidentals = set(meta.get("forbidden_accidentals", []))
    tonic_pc = int(meta.get("tonal_center_pc", 0))
    cadence_steps = set(meta.get("cadence_steps", []))
    secondary_steps = set(meta.get("secondary_dominant_steps", []))
    structural_pillars = set(meta.get("structural_pillars", []))
    urlinie_steps = set(meta.get("urlinie_steps", []))
    beat_strengths = list(meta.get("beat_strengths", []))

    merged_chords = merge_backend_hierarchical_plan(
        chords, durations,
        beats_per_measure=meta.get("beats_per_measure", 4),
        settings=settings,
    )

    allowed_pcs_by_step = {}
    if diatonic:
        raised_fourth = (tonic_pc + 6) % 12
        for t in range(len(merged_chords)):
            allowed = set(diatonic)
            if t in secondary_steps and t in cadence_steps:
                allowed.add(raised_fourth)
            elif forbidden_accidentals:
                allowed -= forbidden_accidentals
            allowed_pcs_by_step[t] = allowed

    build_schenkerian_graph_matrix(
        merged_chords, melody,
        max_candidates=180,
        difficulty=settings.difficulty,
        structural_steps=structural_pillars | urlinie_steps,
        allowed_pcs_by_step=allowed_pcs_by_step or None,
    )

    solution = solve_harmony(
        merged_chords, melody,
        difficulty=settings.difficulty,
        structural_pillars=structural_pillars,
        urlinie_steps=urlinie_steps,
        beat_strengths=beat_strengths,
        tonic_pc=tonic_pc,
        diatonic_pcs=diatonic,
        secondary_dominant_steps=secondary_steps,
        cadence_steps=cadence_steps,
    )

    raw_violations = validate_solution(solution, tonic_pc=tonic_pc)
    violations = enrich_violations_with_measures(
        raw_violations, durations,
        beats_per_measure=meta.get("beats_per_measure", 4),
    )

    voice_tuples = [n.voices for n in solution]
    nuances = detect_genre_nuances(
        voice_tuples, genre, durations,
        beats_per_measure=meta.get("beats_per_measure", 4),
    )

    harmonized_xml = export_xml_string(solution, source_score, instruments=instruments)
    return harmonized_xml, solution, violations, nuances, meta


def _violations_to_annotations(violations: list[dict]) -> list[Annotation]:
    return [
        Annotation(
            time_step=v.get("time_step", 0),
            measure=v.get("measure", 0),
            voice=v.get("voice"),
            code=v.get("code", "UNKNOWN"),
            severity=v.get("severity", "hard"),
            color="red",
            explanation=v.get("explanation", ""),
        )
        for v in violations
    ]


def _nuances_to_annotations(nuances: list[dict]) -> list[Annotation]:
    return [
        Annotation(
            time_step=n.get("time_step", 0),
            measure=n.get("measure", 0),
            voice=n.get("voice"),
            code=n.get("code", "UNKNOWN"),
            severity="nuance",
            color="blue",
            explanation=n.get("explanation", ""),
        )
        for n in nuances
    ]


# ── Phase 1: Harmonize ─────────────────────────────────────────

@app.post("/api/harmonize", response_model=HarmonizeResponse)
def harmonize(req: HarmonizeRequest):
    """Upload MusicXML + presets, receive harmonized score with annotations."""
    harmonized_xml, _, violations, nuances, meta = _run_engine(
        musicxml=req.musicxml,
        mood=req.mood,
        genre=req.genre,
        difficulty=req.difficulty,
        instruments=req.instruments,
    )
    sess = store.create(
        original_xml=req.musicxml,
        harmonized_xml=harmonized_xml,
        instruments=req.instruments,
        mood=req.mood,
        genre=req.genre,
        difficulty=req.difficulty,
        meta=meta,
    )
    return HarmonizeResponse(
        session_id=sess.session_id,
        musicxml=harmonized_xml,
        violations=_violations_to_annotations(violations),
        nuances=_nuances_to_annotations(nuances),
        meta=meta,
    )


# ── Phase 3: Live Validation ───────────────────────────────────

@app.post("/api/validate", response_model=ValidateResponse)
def validate_score(req: ValidateRequest):
    """Re-validate a user-edited score and return red/blue annotations."""
    sess = store.get(req.session_id) if req.session_id else None
    genre = req.genre or (sess.genre if sess else "classical")
    mood = req.mood or (sess.mood if sess else "major")
    difficulty = req.difficulty or (sess.difficulty if sess else "intermediate")

    _, _, violations, nuances, _ = _run_engine(
        musicxml=req.musicxml,
        mood=mood,
        genre=genre,
        difficulty=difficulty,
        instruments=sess.instruments if sess else ["soprano", "alto", "tenor", "bass"],
    )
    if sess:
        store.update(req.session_id, harmonized_xml=req.musicxml)

    return ValidateResponse(
        violations=_violations_to_annotations(violations),
        nuances=_nuances_to_annotations(nuances),
    )


# ── Phase 3: Theory Chatbot ────────────────────────────────────

@app.post("/api/chat", response_model=ChatResponse)
def theory_chat(req: ChatRequest):
    """
    Theory chatbot powered by RAG.
    Explains music theory laws/principles and suggests fixes.
    Never generates or modifies music directly.
    """
    inspector = _get_inspector()
    if inspector is None:
        return ChatResponse(
            reply="Theory Inspector is not available. Please ensure the knowledge base is indexed.",
            sources=[],
            reasoning_steps=["Inspector initialization failed."],
        )

    sess = store.get(req.session_id)
    musicxml = req.musicxml or (sess.harmonized_xml if sess else "")
    context = dict(req.context)
    if sess:
        context.setdefault("genre", sess.genre)
        context.setdefault("mood", sess.mood)
        context.setdefault("difficulty", sess.difficulty)

    result = inspector.run(
        musicxml=musicxml,
        score_delta=context,
        user_query=req.message,
        context=context,
    )

    explanation = result.get("explanation", {})
    return ChatResponse(
        reply=explanation.get("text", "I couldn't find a specific answer. Try rephrasing your question."),
        sources=explanation.get("sources", []),
        reasoning_steps=explanation.get("reasoning_steps", []),
    )


# ── Phase 4: Export ─────────────────────────────────────────────

@app.post("/api/export")
def export_score(req: ExportRequest):
    """Export the harmonized score as MusicXML, PDF, or MIDI."""
    sess = store.get(req.session_id)
    if not sess or not sess.harmonized_xml:
        raise HTTPException(status_code=404, detail="Session not found or no harmonized score available.")

    import music21 as m21

    fmt = req.format.lower().strip()
    if fmt in ("musicxml", "xml"):
        return Response(
            content=sess.harmonized_xml,
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=harmony.musicxml"},
        )

    score = m21.converter.parse(sess.harmonized_xml)

    if fmt == "midi":
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tmp:
            tmp_path = tmp.name
        score.write("midi", fp=tmp_path)
        with open(tmp_path, "rb") as f:
            data = f.read()
        os.unlink(tmp_path)
        return Response(
            content=data,
            media_type="audio/midi",
            headers={"Content-Disposition": "attachment; filename=harmony.mid"},
        )

    if fmt == "pdf":
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp_path = tmp.name
            score.write("lily.pdf", fp=tmp_path)
            with open(tmp_path, "rb") as f:
                data = f.read()
            os.unlink(tmp_path)
            return Response(
                content=data,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=harmony.pdf"},
            )
        except Exception:
            raise HTTPException(
                status_code=501,
                detail="PDF export requires LilyPond to be installed on the server.",
            )

    raise HTTPException(status_code=400, detail=f"Unsupported format: {fmt}. Use musicxml, midi, or pdf.")


# ── Health ──────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    inspector_ready = _get_inspector() is not None
    return {
        "status": "ok",
        "engine": True,
        "inspector": inspector_ready,
    }
