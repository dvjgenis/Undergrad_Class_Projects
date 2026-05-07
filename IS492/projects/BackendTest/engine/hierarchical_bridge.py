from dataclasses import dataclass
from typing import List, Sequence
from engine.settings import EngineSettings


@dataclass
class FunctionalRegion:
    function: str
    start_beat: int
    end_beat: int
    cadence: str | None = None


@dataclass
class PhraseStructure:
    phrase_id: str
    phrase_type: str
    regions: List[FunctionalRegion]


FUNCTION_TO_ROMAN_CLASSICAL = {
    "Tonic": ["I", "vi", "iii"],
    "Predominant": ["ii", "IV"],
    "Dominant": ["V", "V7", "vii°", "V/V", "V7/V"],
}
FUNCTION_TO_ROMAN_POP = {
    "Tonic": ["I", "vi"],
    "Predominant": ["IV", "ii"],
    "Dominant": ["V", "V7"],
}
FUNCTION_TO_ROMAN_MARIACHI = {
    "Tonic": ["I", "vi", "III"],
    "Predominant": ["IV", "ii", "VI"],
    "Dominant": ["V", "V7", "VII"],
}
FUNCTION_TO_ROMAN_MINOR = {
    "Tonic": ["i", "VI", "III"],
    "Predominant": ["ii°", "iv"],
    "Dominant": ["V", "V7", "v"],
}


def _build_phrases(total_beats: int) -> List[PhraseStructure]:
    if total_beats <= 4:
        return [
            PhraseStructure(
                phrase_id="phrase-1",
                phrase_type="Consequent",
                regions=[
                    FunctionalRegion("Tonic", 0, max(0, total_beats // 3 - 1)),
                    FunctionalRegion(
                        "Predominant",
                        max(0, total_beats // 3),
                        max(0, (2 * total_beats) // 3 - 1),
                    ),
                    FunctionalRegion("Dominant", max(0, (2 * total_beats) // 3), total_beats - 1, "PAC"),
                ],
            )
        ]

    half = total_beats // 2
    return [
        PhraseStructure(
            phrase_id="phrase-1",
            phrase_type="Antecedent",
            regions=[
                FunctionalRegion("Tonic", 0, max(0, int(half * 0.4) - 1)),
                FunctionalRegion("Predominant", int(half * 0.4), max(0, int(half * 0.7) - 1)),
                FunctionalRegion("Dominant", int(half * 0.7), max(0, half - 1), "HC"),
            ],
        ),
        PhraseStructure(
            phrase_id="phrase-2",
            phrase_type="Consequent",
            regions=[
                FunctionalRegion("Tonic", half, max(half, half + int((total_beats - half) * 0.35) - 1)),
                FunctionalRegion(
                    "Predominant",
                    half + int((total_beats - half) * 0.35),
                    max(half, half + int((total_beats - half) * 0.7) - 1),
                ),
                FunctionalRegion(
                    "Dominant",
                    half + int((total_beats - half) * 0.7),
                    total_beats - 1,
                    "PAC",
                ),
            ],
        ),
    ]


def _function_for_beat(phrases: Sequence[PhraseStructure], beat_index: int) -> str:
    for phrase in phrases:
        for region in phrase.regions:
            if region.start_beat <= beat_index <= region.end_beat:
                return region.function
    return "Tonic"


def _cadence_for_beat(phrases: Sequence[PhraseStructure], beat_index: int) -> str | None:
    for phrase in phrases:
        for region in phrase.regions:
            if region.end_beat == beat_index and region.cadence:
                return region.cadence
    return None


def _normalize_roman(chord: str) -> str:
    c = (chord or "").strip()
    if c.startswith("V7/V"):
        return "V7/V"
    if c.startswith("V/V"):
        return "V/V"
    if c.startswith("ii°"):
        return "ii°"
    if c.startswith("iv"):
        return "iv"
    if c.startswith("v"):
        return "v"
    if c.startswith("VI"):
        return "VI"
    if c.startswith("VII"):
        return "VII"
    if c.startswith("III"):
        return "III"
    if c.startswith("i"):
        return "i"
    if c.startswith("V7"):
        return "V7"
    if c.startswith("V"):
        return "V"
    if c.startswith("IV"):
        return "IV"
    if c.startswith("iii"):
        return "iii"
    if c.startswith("ii"):
        return "ii"
    if c.startswith("vi"):
        return "vi"
    if c.startswith("vii"):
        return "vii°"
    if c.startswith("I"):
        return "I"
    return "I"


def _choose_for_function(function_name: str, current: str, settings: EngineSettings) -> str:
    if settings.mood == "minor":
        candidates = FUNCTION_TO_ROMAN_MINOR.get(function_name, ["i"])
    elif settings.genre == "pop":
        candidates = FUNCTION_TO_ROMAN_POP.get(function_name, ["I"])
    elif settings.genre == "mariachi":
        candidates = FUNCTION_TO_ROMAN_MARIACHI.get(function_name, ["I"])
    else:
        candidates = FUNCTION_TO_ROMAN_CLASSICAL.get(function_name, ["I"])
    current_n = _normalize_roman(current)
    if current_n in candidates:
        return current_n
    # Keep harmonic rhythm stable with function-first default.
    return candidates[0]


def merge_backend_hierarchical_plan(
    chords: Sequence[str],
    durations: Sequence[float],
    beats_per_measure: int,
    settings: EngineSettings,
    *,
    keep_user_harmony_weight: float = 0.7,
) -> List[str]:
    """
    Merge backend-copy hierarchical architecture with current Python engine:
    - global/phrase functional regions
    - cadence pressure (HC/PAC)
    - preserve user-provided harmony where possible
    """
    if not chords:
        return []

    total_beats = max(1, int(round(sum(durations)))) if durations else len(chords)
    phrases = _build_phrases(total_beats)

    planned: List[str] = []
    beat_cursor = 0.0
    for i, c in enumerate(chords):
        beat_index = int(beat_cursor)
        beat_cursor += durations[i] if i < len(durations) else 1.0

        fn = _function_for_beat(phrases, beat_index)
        cadence = _cadence_for_beat(phrases, beat_index)

        if cadence == "HC":
            planned.append("V")
            continue
        if cadence == "PAC":
            # Strong cadence landing.
            planned.append("i" if settings.mood == "minor" else "I")
            continue

        user_norm = _normalize_roman(c)
        fn_choice = _choose_for_function(fn, user_norm, settings)

        # Weighted blend: mostly keep user symbols, correct only when non-functional.
        if user_norm == fn_choice:
            planned.append(user_norm)
        else:
            planned.append(user_norm if keep_user_harmony_weight >= 0.5 else fn_choice)

    # Apply late dominant -> tonic gestures at phrase ends.
    for phrase in phrases:
        for region in phrase.regions:
            if region.cadence in {"HC", "PAC"}:
                end = min(len(planned) - 1, region.end_beat)
                if end > 0:
                    planned[end - 1] = "V7"
                    planned[end] = ("i" if settings.mood == "minor" else "I") if region.cadence == "PAC" else "V"

    # Use measure-level harmonic rhythm guard (max ~2 changes per bar).
    if beats_per_measure > 0:
        out = planned[:]
        beat_cursor = 0.0
        measure_map: dict[int, List[int]] = {}
        for i, d in enumerate(durations if durations else [1.0] * len(planned)):
            m = int(beat_cursor // beats_per_measure)
            measure_map.setdefault(m, []).append(i)
            beat_cursor += d
        for idxs in measure_map.values():
            if len(idxs) <= 2:
                continue
            first = out[idxs[0]]
            pivot = out[idxs[min(len(idxs) - 1, max(1, len(idxs) // 2))]]
            for local_idx, global_idx in enumerate(idxs):
                out[global_idx] = first if local_idx < max(1, len(idxs) // 2) else pivot
        planned = out

        # Classical major Schenkerian pillars:
        # m1 -> I, m2 -> I/vi, final bar -> V to I cadence.
        if settings.genre == "classical" and settings.mood == "major":
            ordered_measures = sorted(measure_map.keys())
            if ordered_measures:
                m1 = measure_map.get(ordered_measures[0], [])
                for idx in m1:
                    planned[idx] = "I"
            if len(ordered_measures) >= 2:
                m2 = measure_map.get(ordered_measures[1], [])
                for idx in m2:
                    if planned[idx] not in {"I", "vi"}:
                        planned[idx] = "I"
            if len(ordered_measures) >= 4:
                m_last = measure_map.get(ordered_measures[-1], [])
                if m_last:
                    planned[m_last[-1]] = "I"
                    if len(m_last) >= 2:
                        planned[m_last[-2]] = "V"

    return planned
