from __future__ import annotations

from pydantic import BaseModel, Field


# ── Phase 1: Upload + Settings ──────────────────────────────────

class HarmonizeRequest(BaseModel):
    musicxml: str
    instruments: list[str] = Field(
        default_factory=lambda: ["soprano", "alto", "tenor", "bass"],
        description="Voices/instruments to generate (soprano is the input melody).",
    )
    mood: str = "major"
    genre: str = "classical"
    difficulty: str = "intermediate"


class HarmonizeResponse(BaseModel):
    session_id: str
    musicxml: str
    violations: list[Annotation]
    nuances: list[Annotation]
    meta: dict


# ── Phase 3: Validation / Live Edit ─────────────────────────────

class Annotation(BaseModel):
    time_step: int
    measure: int = 0
    voice: int | None = None
    code: str
    severity: str
    color: str  # "red" = violation, "blue" = genre nuance
    explanation: str


HarmonizeResponse.model_rebuild()


class ValidateRequest(BaseModel):
    session_id: str
    musicxml: str
    mood: str = "major"
    genre: str = "classical"
    difficulty: str = "intermediate"


class ValidateResponse(BaseModel):
    violations: list[Annotation]
    nuances: list[Annotation]


# ── Phase 3: Chat ───────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str
    message: str
    musicxml: str = ""
    context: dict = Field(default_factory=dict)


class ChatResponse(BaseModel):
    reply: str
    sources: list[str] = Field(default_factory=list)
    reasoning_steps: list[str] = Field(default_factory=list)


# ── Phase 4: Export ─────────────────────────────────────────────

class ExportRequest(BaseModel):
    session_id: str
    format: str = "musicxml"
