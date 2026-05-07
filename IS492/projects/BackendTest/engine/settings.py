import json
import os
from dataclasses import dataclass


Mood = str
Genre = str
Difficulty = str


@dataclass(frozen=True)
class EngineSettings:
    mood: Mood = "major"             # major | minor
    genre: Genre = "classical"       # classical | pop | mariachi
    difficulty: Difficulty = "intermediate"  # beginner | intermediate | advanced


def _normalize_mood(value: str) -> Mood:
    v = (value or "").strip().lower()
    if v in {"minor", "somber", "sad", "dark"}:
        return "minor"
    return "major"


def _normalize_genre(value: str) -> Genre:
    v = (value or "").strip().lower()
    if v in {"classical", "pop", "mariachi"}:
        return v
    if "rock" in v:
        return "pop"
    if "mariachi" in v or "ranchera" in v:
        return "mariachi"
    return "classical"


def _normalize_difficulty(value: str) -> Difficulty:
    v = (value or "").strip().lower()
    if v in {"beginner", "easy", "simple", "baby"}:
        return "beginner"
    if v in {"advanced", "hard", "complex"}:
        return "advanced"
    return "intermediate"


def engine_settings_from_presets(
    mood: str = "major",
    genre: str = "classical",
    difficulty: str = "intermediate",
) -> EngineSettings:
    """Build EngineSettings from frontend preset values."""
    return EngineSettings(
        mood=_normalize_mood(mood),
        genre=_normalize_genre(genre),
        difficulty=_normalize_difficulty(difficulty),
    )


def _settings_from_text(text: str) -> EngineSettings:
    t = (text or "").lower()
    mood = "minor" if any(k in t for k in ["somber", "sad", "spooky", "dark", "minor"]) else "major"
    if "mariachi" in t or "ranchera" in t:
        genre = "mariachi"
    elif "pop" in t or "rock" in t:
        genre = "pop"
    elif "classical" in t:
        genre = "classical"
    else:
        genre = "classical"

    if any(k in t for k in ["beginner", "easy", "simple", "baby"]):
        difficulty = "beginner"
    elif any(k in t for k in ["advanced", "complex", "virtuosic", "hard"]):
        difficulty = "advanced"
    else:
        difficulty = "intermediate"
    return EngineSettings(mood=mood, genre=genre, difficulty=difficulty)


def load_engine_settings() -> EngineSettings:
    """
    Sources (highest precedence first):
    1) HF_SETTINGS_JSON='{"mood":"minor","genre":"classical","difficulty":"beginner"}'
    2) HF_STYLE_TEXT='make it spooky beginner cello'
    3) HF_MOOD / HF_GENRE / HF_DIFFICULTY
    """
    raw_json = os.getenv("HF_SETTINGS_JSON", "").strip()
    if raw_json:
        try:
            data = json.loads(raw_json)
            return EngineSettings(
                mood=_normalize_mood(str(data.get("mood", "major"))),
                genre=_normalize_genre(str(data.get("genre", "classical"))),
                difficulty=_normalize_difficulty(str(data.get("difficulty", "intermediate"))),
            )
        except Exception:
            pass

    style_text = os.getenv("HF_STYLE_TEXT", "").strip()
    if style_text:
        return _settings_from_text(style_text)

    return EngineSettings(
        mood=_normalize_mood(os.getenv("HF_MOOD", "major")),
        genre=_normalize_genre(os.getenv("HF_GENRE", "classical")),
        difficulty=_normalize_difficulty(os.getenv("HF_DIFFICULTY", "intermediate")),
    )
