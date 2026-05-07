"""Pydantic schemas for HarmonyForge API."""

from pydantic import BaseModel, Field


# ── Phase 1 & 2: Harmonize ───────────────────────────────────────

class HarmonizeRequest(BaseModel):
    musicxml: str = Field(..., description="MusicXML content of uploaded score")
    instruments: list[str] | None = Field(
        default=None,
        description="Parts to include: alto, tenor, bass. None = all.",
    )
    mood: str = Field(default="major", description="major | minor")
    genre: str = Field(default="classical", description="classical | pop | mariachi")
    difficulty: str = Field(
        default="intermediate",
        description="easy | beginner | intermediate | advanced",
    )


class ViolationItem(BaseModel):
    measure: int
    time_step: int
    code: str
    explanation: str
    severity: str  # "red" | "blue"
    voices: int | tuple[int, int] | None = None


class HarmonizeResponse(BaseModel):
    musicxml: str = Field(..., description="Harmonized MusicXML")
    violations: list[ViolationItem] = Field(default_factory=list)
    success: bool = True


# ── Phase 3: Validate (red/blue highlights) ───────────────────────

class ValidateRequest(BaseModel):
    musicxml: str = Field(..., description="Current score (possibly user-edited)")
    genre: str = Field(
        default="classical",
        description="Genre for blue vs red mapping: classical | pop | mariachi",
    )


class ValidateResponse(BaseModel):
    red: list[ViolationItem] = Field(
        default_factory=list,
        description="Hard violations (highlight in red)",
    )
    blue: list[ViolationItem] = Field(
        default_factory=list,
        description="Genre nuances (highlight in blue)",
    )


# ── Phase 3: Theory Inspect (chatbot) ──────────────────────────────

class TheoryInspectRequest(BaseModel):
    musicxml: str
    score_delta: dict = Field(default_factory=dict)
    user_query: str
    context: dict = Field(default_factory=dict)


# ── Phase 4: Export ────────────────────────────────────────────────

class ExportRequest(BaseModel):
    musicxml: str = Field(..., description="Score to export")
    format: str = Field(default="xml", description="xml | pdf")


# ── Convert (PDF/MIDI → MusicXML) ──────────────────────────────────────────

class ConvertResponse(BaseModel):
    musicxml: str = Field(..., description="Converted MusicXML content")


# ── Presets (for frontend reference) ───────────────────────────────

PRESETS = {
    "mood": ["major", "minor"],
    "genre": ["classical", "pop", "mariachi"],
    "difficulty": ["easy", "intermediate", "advanced"],
    "instruments": ["soprano", "alto", "tenor", "bass"],
}
