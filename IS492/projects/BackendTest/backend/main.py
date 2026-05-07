"""
HarmonyForge unified backend API for 4-phase frontend integration.
"""

import os
import sys
from pathlib import Path

# Run from project root so engine + TheoryInspector are importable
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
os.chdir(_root)

# Use local LangGraph from tools folder when available (before TheoryInspector imports)
_langgraph_path = _root / "tools" / "langgraph" / "libs" / "langgraph"
if _langgraph_path.exists():
    _lib_path = str(_langgraph_path)
    if _lib_path not in sys.path:
        sys.path.insert(0, _lib_path)

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from backend.schemas import (
    HarmonizeRequest,
    HarmonizeResponse,
    ViolationItem,
    ValidateRequest,
    ValidateResponse,
    TheoryInspectRequest,
    ExportRequest,
    ConvertResponse,
    PRESETS,
)
from backend.services.validate import validate_score
from backend.services.export import export_to_xml, export_to_pdf
from backend.services.convert import convert_to_musicxml

# Engine
from engine.main import run_harmonize_pipeline
from engine.settings import engine_settings_from_presets

# TheoryInspector
from TheoryInspector.config import TheoryInspectorConfig
from TheoryInspector.ingest import build_chunks_index
from TheoryInspector.orchestrator import TheoryInspectorOrchestrator
from TheoryInspector.retriever import TheoryRetriever
from TheoryInspector.settings import load_llm_settings
from TheoryInspector.tools_registry import MusicTheoryTools

app = FastAPI(
    title="HarmonyForge API",
    version="0.1.0",
    description="Backend for 4-phase harmonization workflow: upload → harmonize → edit & validate → export",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TheoryInspector setup
_ti_cfg = TheoryInspectorConfig.from_project_root(_root)
if not _ti_cfg.chunks_csv.exists():
    build_chunks_index(_ti_cfg)
_chroma_dir = Path(os.getenv("TI_CHROMA_DIR", str(_ti_cfg.chroma_dir)))
_ti_retriever = TheoryRetriever(_ti_cfg.chunks_csv, _chroma_dir)
_ti_llm = load_llm_settings(_ti_cfg.env_file)
_ti_orchestrator = TheoryInspectorOrchestrator(_ti_retriever, MusicTheoryTools(), _ti_llm)


# ── Convert (PDF/MIDI → MusicXML) ──────────────────────────────────────────

@app.post("/api/convert", response_model=ConvertResponse)
async def convert(file: UploadFile = File(...)):
    """
    Convert PDF or MIDI to MusicXML. Accepts .pdf, .mid, .midi.
    Returns MusicXML string for use in harmonize flow.
    """
    ext = (Path(file.filename or "").suffix or "").lower()
    format_map = {".pdf": "pdf", ".mid": "midi", ".midi": "midi"}
    fmt = format_map.get(ext)
    if not fmt:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {ext}. Use .pdf, .mid, or .midi.",
        )
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        musicxml = convert_to_musicxml(content, fmt)
        if not musicxml.strip() or "<" not in musicxml:
            raise HTTPException(status_code=400, detail="Conversion produced invalid MusicXML")
        return ConvertResponse(musicxml=musicxml)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Phase 1 & 2: Harmonize ───────────────────────────────────────

@app.post("/api/harmonize", response_model=HarmonizeResponse)
def harmonize(req: HarmonizeRequest):
    """
    Phase 1→2: Upload music, select presets, return harmonized sheet music.
    """
    try:
        settings = engine_settings_from_presets(
            mood=req.mood,
            genre=req.genre,
            difficulty=req.difficulty,
        )
        instruments = None
        if req.instruments:
            instruments = [p for p in req.instruments if p.lower() in ("alto", "tenor", "bass")]
            if not instruments:
                instruments = None
        musicxml, violations = run_harmonize_pipeline(
            req.musicxml, settings, instruments=instruments
        )
        items = []
        for v in violations:
            severity = "red" if v.get("severity") == "hard" else "blue"
            items.append(
                ViolationItem(
                    measure=v.get("measure", 1),
                    time_step=v.get("time_step", 0),
                    code=v.get("code", ""),
                    explanation=v.get("explanation", ""),
                    severity=severity,
                    voices=v.get("voices"),
                )
            )
        return HarmonizeResponse(musicxml=musicxml, violations=items, success=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Phase 3: Validate (red/blue highlights) ───────────────────────

@app.post("/api/validate", response_model=ValidateResponse)
def validate(req: ValidateRequest):
    """
    Phase 3: Validate (possibly edited) score. Returns red (violations) and blue (nuances).
    """
    try:
        red_list, blue_list = validate_score(req.musicxml, genre=req.genre)
        return ValidateResponse(
            red=[ViolationItem(**r) for r in red_list],
            blue=[ViolationItem(**b) for b in blue_list],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Phase 3: Theory Inspect (chatbot) ──────────────────────────────

@app.post("/api/theory-inspect")
def theory_inspect(req: TheoryInspectRequest):
    """
    Phase 3: Chatbot for explanations and suggestions. AI never edits music.
    """
    return _ti_orchestrator.run(
        musicxml=req.musicxml,
        score_delta=req.score_delta,
        user_query=req.user_query,
        context=req.context,
    )


# ── Phase 4: Export ───────────────────────────────────────────────

@app.post("/api/export")
def export(req: ExportRequest):
    """
    Phase 4: Export score as XML or PDF.
    """
    fmt = (req.format or "xml").strip().lower()
    try:
        if fmt == "pdf":
            data = export_to_pdf(req.musicxml)
            return Response(content=data, media_type="application/pdf")
        else:
            xml_str = export_to_xml(req.musicxml)
            return Response(content=xml_str, media_type="application/xml")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Presets (for frontend) ──────────────────────────────────────────

@app.get("/api/presets")
def get_presets():
    """Return available preset options for the frontend."""
    return PRESETS


@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}


@app.get("/api/ti-status")
def ti_status():
    """
    Theory Inspector status: LLM availability and configuration.
    Use to show UI hints when keys are not yet configured.
    """
    has_anthropic = bool(_ti_llm.anthropic_api_key and _ti_llm.anthropic_api_key.strip())
    has_openai = bool(_ti_llm.openai_api_key and _ti_llm.openai_api_key.strip())
    has_groq = bool(_ti_llm.groq_api_key and _ti_llm.groq_api_key.strip())
    llm_available = _ti_llm.use_llm_tutor and (has_anthropic or has_openai or has_groq)
    return {
        "llm_enabled": _ti_llm.use_llm_tutor,
        "llm_available": llm_available,
        "providers": {
            "anthropic": has_anthropic,
            "openai": has_openai,
            "groq": has_groq,
        },
        "mode": "deterministic" if not llm_available else "llm_enriched",
    }
