"""
Genre-nuance detector.

Returns blue-highlighted annotations for things that *look* like theory
violations but are idiomatic in the selected genre.  These are NOT errors;
they are stylistic features the user should be aware of.
"""

from __future__ import annotations

from typing import Sequence

GENRE_NUANCES: dict[str, list[dict]] = {
    "mariachi": [
        {
            "code": "NO_THIRD_IN_CHORD",
            "pattern": lambda pcs: len(pcs) >= 3 and _missing_third(pcs),
            "explanation": (
                "Mariachi harmony often omits the third of the chord, "
                "creating open-fifth sonorities that are characteristic of the style."
            ),
        },
        {
            "code": "PARALLEL_THIRDS_SIXTHS",
            "pattern": lambda intervals: any(i in {3, 4, 8, 9} for i in intervals),
            "explanation": (
                "Parallel thirds and sixths between voices are a defining texture "
                "in mariachi vocal and trumpet writing."
            ),
        },
    ],
    "pop": [
        {
            "code": "POWER_CHORD",
            "pattern": lambda pcs: len(pcs) >= 2 and _is_power_chord(pcs),
            "explanation": (
                "Power chords (root + fifth, no third) are standard in pop/rock "
                "and are not a voicing error."
            ),
        },
        {
            "code": "REPEATED_PROGRESSION",
            "pattern": lambda _: False,
            "explanation": (
                "Repeating a I-V-vi-IV loop is the backbone of pop harmony, "
                "not a sign of weak progression."
            ),
        },
    ],
    "classical": [
        {
            "code": "DOUBLED_THIRD",
            "pattern": lambda pcs: _doubled_third(pcs),
            "explanation": (
                "Doubling the third is generally avoided in strict classical style "
                "but may be acceptable in certain inversions."
            ),
        },
    ],
}


def _missing_third(chord_pcs: Sequence[int]) -> bool:
    if len(chord_pcs) < 3:
        return False
    root = chord_pcs[0]
    third_options = {(root + 3) % 12, (root + 4) % 12}
    return not any(pc in third_options for pc in chord_pcs)


def _is_power_chord(chord_pcs: Sequence[int]) -> bool:
    if len(chord_pcs) < 2:
        return False
    root = chord_pcs[0]
    fifth = (root + 7) % 12
    third_options = {(root + 3) % 12, (root + 4) % 12}
    has_fifth = fifth in set(chord_pcs)
    has_third = any(pc in third_options for pc in chord_pcs)
    return has_fifth and not has_third


def _doubled_third(chord_pcs: Sequence[int]) -> bool:
    if len(chord_pcs) < 4:
        return False
    root = chord_pcs[0]
    third_options = {(root + 3) % 12, (root + 4) % 12}
    count = sum(1 for pc in chord_pcs if pc in third_options)
    return count >= 2


def detect_genre_nuances(
    solution_voices: Sequence[tuple[int, int, int, int]],
    genre: str,
    durations: Sequence[float] | None = None,
    beats_per_measure: int = 4,
) -> list[dict]:
    rules = GENRE_NUANCES.get(genre, [])
    if not rules:
        return []

    annotations: list[dict] = []
    cumulative = 0.0
    for t, voices in enumerate(solution_voices):
        measure = int(cumulative // max(1, beats_per_measure)) + 1
        if durations and t < len(durations):
            cumulative += durations[t]
        else:
            cumulative += 1.0

        pcs = [v % 12 for v in voices]
        intervals = [abs(voices[j] - voices[i]) % 12 for i in range(3) for j in range(i + 1, 4)]

        for rule in rules:
            try:
                triggered = rule["pattern"](pcs) or rule["pattern"](intervals)
            except Exception:
                triggered = False
            if triggered:
                annotations.append(
                    {
                        "time_step": t,
                        "measure": measure,
                        "code": rule["code"],
                        "severity": "nuance",
                        "color": "blue",
                        "explanation": rule["explanation"],
                    }
                )
    return annotations
