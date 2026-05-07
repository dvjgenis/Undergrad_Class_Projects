"""
Extract SATB and analysis data from MusicXML for TheoryInspector tools.
Uses engine's parse_satb_score_to_solution when available.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Ensure engine is importable
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


def extract_tool_inputs(musicxml: str, score_delta: dict[str, Any]) -> dict[str, Any]:
    """
    Extract voice data and context from musicxml + score_delta for auditor tools.
    Returns dict with: chord_a, chord_b, measure_range, voices_for_interval, etc.
    """
    try:
        from engine.io_handler import parse_satb_score_to_solution
    except ImportError:
        return _fallback_inputs(score_delta)

    solution, meta = parse_satb_score_to_solution(musicxml)
    if not solution or len(solution) < 2:
        return _fallback_inputs(score_delta)

    beats_per_measure = meta.get("beats_per_measure", 4)
    durations = meta.get("durations", [1.0] * len(solution))
    measure = score_delta.get("measure", 1)
    error_codes = score_delta.get("error_codes", [])

    # Map measure to time_step
    cumulative = 0.0
    step_to_measure = {}
    for i, d in enumerate(durations):
        m = int(cumulative // beats_per_measure) + 1
        step_to_measure[i] = m
        cumulative += d
    measure_to_steps = {}
    for s, m in step_to_measure.items():
        measure_to_steps.setdefault(m, []).append(s)
    steps_in_measure = measure_to_steps.get(measure, [0, 1])[:2]
    if len(steps_in_measure) < 2:
        steps_in_measure = [0, min(1, len(solution) - 1)]

    t_a, t_b = steps_in_measure[0], min(steps_in_measure[1], len(solution) - 1)
    node_a = solution[t_a]
    node_b = solution[t_b]
    chord_a = list(node_a.voices)  # (bass, tenor, alto, soprano)
    chord_b = list(node_b.voices)

    # For interval analysis: compare two voices (e.g. bass vs soprano) at chord_a
    voice1 = [chord_a[0], chord_b[0]]  # bass
    voice2 = [chord_a[3], chord_b[3]]   # soprano

    return {
        "chord_a": chord_a,
        "chord_b": chord_b,
        "measure_range": (measure, measure + 1),
        "voice1": voice1,
        "voice2": voice2,
        "measures": list(measure_to_steps.keys())[:8],
    }


def _fallback_inputs(score_delta: dict[str, Any]) -> dict[str, Any]:
    """Fallback when parsing fails or score is not SATB."""
    measure = score_delta.get("measure", 1)
    return {
        "chord_a": [48, 55, 60, 64],
        "chord_b": [50, 57, 62, 65],
        "measure_range": (measure, measure + 1),
        "voice1": [48, 50],
        "voice2": [64, 65],
        "measures": [1, 2, 3, 4],
    }
