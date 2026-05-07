"""
Phase 3 validation: map engine violations to red (hard) vs blue (genre nuance).
"""

import sys
from pathlib import Path

# Ensure engine is importable when running from project root
_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from engine.io_handler import parse_satb_score_to_solution
from engine.core_engine import validate_solution, enrich_violations_with_measures

# Codes that are always red (theory violations)
RED_CODES = {"VOICE_ORDER", "SPACING", "TRITONE_RESOLUTION_IMPROPER"}

# Codes that are red in classical but blue (nuance) in pop/mariachi
SOFT_CODES_BLUE_IN_POP_MARIACHI = {
    "PARALLEL_PERFECT",
    "LEADING_TONE_UNRESOLVED",
    "LARGE_LEAP",
    "REPEATED_FUNCTION",
    "TRITONE_RESOLUTION_SUBOPTIMAL",
}


def _to_red_or_blue(violation: dict, genre: str) -> str:
    code = violation.get("code", "")
    severity = violation.get("severity", "soft")
    genre_lower = (genre or "classical").strip().lower()

    if code in RED_CODES:
        return "red"
    if code in SOFT_CODES_BLUE_IN_POP_MARIACHI:
        if genre_lower in ("pop", "mariachi"):
            return "blue"  # Genre nuance
        return "red" if severity == "hard" else "blue"
    return "red" if severity == "hard" else "blue"


def validate_score(musicxml: str, genre: str = "classical") -> tuple[list[dict], list[dict]]:
    """
    Validate SATB score and return (red_violations, blue_violations).
    """
    solution, meta = parse_satb_score_to_solution(musicxml)
    if solution is None:
        return [], []  # Cannot validate; return empty

    tonic_pc = meta.get("tonic_pc", 0)
    durations = meta.get("durations", [1.0] * len(solution))
    beats_per_measure = meta.get("beats_per_measure", 4)

    raw = validate_solution(solution, tonic_pc=tonic_pc)
    enriched = enrich_violations_with_measures(
        raw, durations, beats_per_measure=beats_per_measure
    )

    red_list = []
    blue_list = []
    for v in enriched:
        v_copy = dict(v)
        v_copy["severity"] = _to_red_or_blue(v, genre)
        item = {
            "measure": v_copy.get("measure", 1),
            "time_step": v_copy.get("time_step", 0),
            "code": v_copy.get("code", ""),
            "explanation": v_copy.get("explanation", ""),
            "severity": v_copy["severity"],
            "voices": v_copy.get("voices"),
        }
        if v_copy["severity"] == "red":
            red_list.append(item)
        else:
            blue_list.append(item)

    return red_list, blue_list
