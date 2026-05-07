import os
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .config import TheoryInspectorConfig
from .ingest import build_chunks_index
from .orchestrator import TheoryInspectorOrchestrator
from .retriever import TheoryRetriever
from .settings import load_llm_settings
from .tools_registry import MusicTheoryTools


class InspectRequest(BaseModel):
    musicxml: str
    score_delta: dict = Field(default_factory=dict)
    user_query: str
    context: dict = Field(default_factory=dict)


app = FastAPI(title="Theory Inspector API", version="0.1.0")

_cfg = TheoryInspectorConfig.from_project_root(Path(__file__).resolve().parent.parent)
if not _cfg.chunks_csv.exists():
    build_chunks_index(_cfg)
_chroma_dir = Path(os.getenv("TI_CHROMA_DIR", str(_cfg.chroma_dir)))
_retriever = TheoryRetriever(_cfg.chunks_csv, _chroma_dir)
_llm_settings = load_llm_settings(_cfg.env_file)
_orchestrator = TheoryInspectorOrchestrator(_retriever, MusicTheoryTools(), _llm_settings)


@app.post("/api/theory-inspect")
def theory_inspect(req: InspectRequest):
    return _orchestrator.run(
        musicxml=req.musicxml,
        score_delta=req.score_delta,
        user_query=req.user_query,
        context=req.context,
    )
