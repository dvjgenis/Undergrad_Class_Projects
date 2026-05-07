import music21 as m21
import copy
from engine.settings import EngineSettings

ROMAN_TO_CHORD_SYMBOL = {
    "I": "C",
    "ii": "Dm",
    "iii": "Em",
    "IV": "F",
    "V": "G",
    "V7": "G7",
    "vi": "Am",
    "vii°": "Bdim",
    "V/V": "D",
    "V7/V": "D7",
    # Minor mode mappings (C minor reference)
    "i": "Cm",
    "ii°": "Ddim",
    "III": "Eb",
    "iv": "Fm",
    "v": "Gm",
    "VI": "Ab",
    "VII": "Bb",
    "i7": "Cm7",
    "ii°7": "Ddim7",
    "iv7": "Fm7",
}
ROMAN_CANDIDATES_MAJOR = ["I", "ii", "iii", "IV", "V", "vi", "V7", "vii°"]
ROMAN_CANDIDATES_MINOR = ["i", "ii°", "III", "iv", "v", "V", "VI", "VII", "i7", "ii°7", "iv7"]
ROMAN_TO_PCS = {
    "I": {0, 4, 7},
    "ii": {2, 5, 9},
    "iii": {4, 7, 11},
    "IV": {5, 9, 0},
    "V": {7, 11, 2},
    "V7": {7, 11, 2, 5},
    "vi": {9, 0, 4},
    "vii°": {11, 2, 5},
    "V/V": {2, 6, 9},
    "V7/V": {2, 6, 9, 0},
    "i": {0, 3, 7},
    "ii°": {2, 5, 8},
    "III": {3, 7, 10},
    "iv": {5, 8, 0},
    "v": {7, 10, 2},
    "VI": {8, 0, 3},
    "VII": {10, 2, 5},
    "i7": {0, 3, 7, 10},
    "ii°7": {2, 5, 8, 11},
    "iv7": {5, 8, 0, 3},
}
TRANSITION_PENALTIES_CLASSICAL = {
    ("I", "I"): 0.2,
    ("I", "ii"): 0.8,
    ("I", "iii"): 1.2,
    ("I", "IV"): 0.4,
    ("I", "V"): 0.4,
    ("I", "V7"): 0.5,
    ("I", "vi"): 0.5,
    ("ii", "V"): 0.2,
    ("ii", "V7"): 0.2,
    ("ii", "I"): 0.7,
    ("iii", "vi"): 0.3,
    ("iii", "IV"): 0.6,
    ("IV", "I"): 0.4,
    ("IV", "ii"): 0.6,
    ("IV", "V"): 0.2,
    ("IV", "V7"): 0.2,
    ("V", "I"): 0.1,
    ("V7", "I"): 0.0,
    ("V", "vi"): 0.7,
    ("vi", "ii"): 0.5,
    ("vi", "IV"): 0.5,
    ("vi", "V"): 0.5,
}
TRANSITION_PENALTIES_POP = {
    ("I", "V"): 0.3,
    ("I", "IV"): 0.2,
    ("I", "vi"): 0.1,
    ("vi", "IV"): 0.1,
    ("IV", "I"): 0.2,
    ("IV", "V"): 0.1,
    ("V", "I"): 0.2,
    ("V", "vi"): 0.2,
    ("vi", "V"): 0.2,
}
TRANSITION_PENALTIES_MARIACHI = {
    ("I", "IV"): 0.1,
    ("I", "V"): 0.2,
    ("I", "V7"): 0.2,
    ("I", "VI"): 0.5,
    ("I", "VII"): 0.5,
    ("IV", "V"): 0.0,
    ("IV", "V7"): 0.0,
    ("IV", "I"): 0.2,
    ("V", "I"): 0.0,
    ("V7", "I"): 0.0,
    ("VII", "III"): 0.1,
    ("III", "VI"): 0.2,
    ("VI", "VII"): 0.2,
    ("VI", "V"): 0.2,
}
TRANSITION_PENALTIES_MINOR = {
    ("i", "iv"): 0.2,
    ("i", "VI"): 0.2,
    ("iv", "V"): 0.1,
    ("iv", "v"): 0.2,
    ("V", "i"): 0.0,
    ("v", "i"): 0.3,
    ("VII", "III"): 0.2,
    ("ii°", "V"): 0.1,
}
STYLE_TRANSITION_BONUS = {
    "classical": {("ii", "V"): -0.15, ("V", "I"): -0.2, ("IV", "V"): -0.1},
    "pop": {("I", "vi"): -0.1, ("vi", "IV"): -0.1, ("IV", "V"): -0.1},
    "mariachi": {("IV", "V7"): -0.2, ("V7", "I"): -0.25, ("VII", "III"): -0.1},
}


def _normalize_figure_to_roman(figure: str) -> str:
    fig = (figure or "").strip()
    if fig.startswith("V7/V"):
        return "V7/V"
    if fig.startswith("V/V"):
        return "V/V"
    if fig in ROMAN_TO_CHORD_SYMBOL:
        return fig
    # Handle pitch-name symbols if present in source score.
    rev = {v: k for k, v in ROMAN_TO_CHORD_SYMBOL.items()}
    if fig in rev:
        return rev[fig]
    return "I"


def _candidate_set(settings: EngineSettings):
    if settings.genre == "mariachi" and settings.mood == "major":
        return ["I", "ii", "iii", "IV", "V", "V7", "vi", "VII", "III", "VI"]
    return ROMAN_CANDIDATES_MINOR if settings.mood == "minor" else ROMAN_CANDIDATES_MAJOR


def _transition_penalties(settings: EngineSettings):
    if settings.mood == "minor":
        base = dict(TRANSITION_PENALTIES_MINOR)
    elif settings.genre == "pop":
        base = dict(TRANSITION_PENALTIES_POP)
    elif settings.genre == "mariachi":
        base = dict(TRANSITION_PENALTIES_MARIACHI)
    else:
        base = dict(TRANSITION_PENALTIES_CLASSICAL)

    # Keep a classical fallback floor for unknown transitions.
    for k, v in TRANSITION_PENALTIES_CLASSICAL.items():
        base.setdefault(k, v + 0.2)
    return base


def _difficulty_candidate_limit(settings: EngineSettings) -> int:
    if settings.difficulty == "beginner":
        return 2
    if settings.difficulty == "advanced":
        return 5
    return 3


def _melody_fit_penalty(roman: str, pcs: list[int], settings: EngineSettings) -> float:
    chord_pcs = ROMAN_TO_PCS.get(roman, ROMAN_TO_PCS["I"])
    misses = sum(1 for pc in pcs if pc not in chord_pcs)
    if misses == 0:
        return 0.0
    # Intonation-first behavior: if melody sits outside the harmony, penalize heavily.
    base = 0.9 * misses
    if settings.difficulty == "beginner":
        base += 0.5 * misses
    return base


def _diatonic_pcs_for_center(tonic_pc: int, mood: str) -> set[int]:
    if mood == "minor":
        # Harmonic-minor aware scale degrees from tonic.
        degrees = [0, 2, 3, 5, 7, 8, 11]
    else:
        degrees = [0, 2, 4, 5, 7, 9, 11]
    return {(tonic_pc + d) % 12 for d in degrees}


def _c_major_diatonic_ratio(melody_pitches: list[int]) -> float:
    if not melody_pitches:
        return 0.0
    c_major = {0, 2, 4, 5, 7, 9, 11}
    in_scale = sum(1 for m in melody_pitches if (m % 12) in c_major)
    return in_scale / max(1, len(melody_pitches))


def _tonal_center_from_score(score, melody_pitches, settings: EngineSettings) -> tuple[int, int]:
    key_sigs = score.recurse().getElementsByClass(m21.key.KeySignature)
    sharps = int(key_sigs[0].sharps) if key_sigs else 0
    signature_tonic_pc = None
    if key_sigs:
        try:
            mode = "minor" if settings.mood == "minor" else "major"
            signature_tonic_pc = int(key_sigs[0].asKey(mode).tonic.pitchClass)
        except Exception:
            signature_tonic_pc = None

    final_note_pc = int(melody_pitches[-1] % 12) if melody_pitches else 0
    if signature_tonic_pc is None:
        return final_note_pc, sharps
    if final_note_pc in {signature_tonic_pc, (signature_tonic_pc + 7) % 12}:
        return signature_tonic_pc, sharps
    return final_note_pc, sharps


def _metric_weight_for_beat(beat: int, beats_per_measure: int) -> float:
    if beats_per_measure == 4:
        return 1.35 if (beat % beats_per_measure) in {0, 2} else 1.0
    return 1.25 if (beat % beats_per_measure) == 0 else 1.0


def _functional_prior_penalty(
    rn: str,
    beat: int,
    beats_per_measure: int,
    total_beats: int,
    settings: EngineSettings,
) -> float:
    """
    Methodology blend prior:
    - strong beats favor tonic/predominant/dominant anchors
    - phrase-end positions favor dominant->tonic cadence gravity
    """
    pos = beat % max(1, beats_per_measure)
    strong = pos in {0, 2} if beats_per_measure == 4 else pos == 0
    is_phrase_end = beat >= max(0, total_beats - 2)

    if settings.mood == "minor":
        tonic = {"i", "VI", "III"}
        predominant = {"ii°", "iv"}
        dominant = {"V", "V7", "v"}
    else:
        tonic = {"I", "vi", "iii"}
        predominant = {"ii", "IV"}
        dominant = {"V", "V7", "vii°", "V/V", "V7/V"}

    penalty = 0.0
    if strong and rn not in tonic.union(predominant).union(dominant):
        penalty += 0.8
    if is_phrase_end:
        if beat == total_beats - 2 and rn not in dominant:
            penalty += 0.7
        if beat == total_beats - 1 and rn not in tonic:
            penalty += 1.0
    return penalty


def _phrase_structural_indices(offsets: list[float], beats_per_measure: int, phrase_measures: int = 4) -> tuple[set[int], set[int]]:
    pillars: set[int] = set()
    cadence_steps: set[int] = set()
    if not offsets:
        return pillars, cadence_steps
    phrase_map: dict[int, list[int]] = {}
    phrase_span = max(1, beats_per_measure * phrase_measures)
    for i, off in enumerate(offsets):
        phrase_id = int(off // phrase_span)
        phrase_map.setdefault(phrase_id, []).append(i)
    for idxs in phrase_map.values():
        if not idxs:
            continue
        pillars.add(idxs[0])
        pillars.add(idxs[-1])
        cadence_steps.add(idxs[-1])
    return pillars, cadence_steps


def _estimate_urlinie_steps(melody_pitches: list[int], offsets: list[float], beats_per_measure: int) -> set[int]:
    steps: set[int] = set()
    if not melody_pitches or not offsets:
        return steps
    phrase_map: dict[int, list[int]] = {}
    phrase_span = max(1, beats_per_measure * 4)
    for i, off in enumerate(offsets):
        phrase_id = int(off // phrase_span)
        phrase_map.setdefault(phrase_id, []).append(i)

    for idxs in phrase_map.values():
        if not idxs:
            continue
        first, last = idxs[0], idxs[-1]
        steps.add(first)
        steps.add(last)
        apex = max(idxs, key=lambda i: melody_pitches[i])
        if apex < last:
            prev = melody_pitches[apex]
            steps.add(apex)
            for j in range(apex + 1, last + 1):
                if melody_pitches[j] <= prev:
                    steps.add(j)
                    prev = melody_pitches[j]
    return steps


def _secondary_dominant_steps(harmony_events, offsets: list[float], beats_per_measure: int) -> set[int]:
    if not harmony_events or not offsets:
        return set()
    sec_offsets = {
        float(off)
        for off, fig in harmony_events
        if "V/V" in str(fig) or "V7/V" in str(fig)
    }
    if not sec_offsets:
        return set()
    cadence_steps = _phrase_structural_indices(offsets, beats_per_measure)[1]
    return {i for i, off in enumerate(offsets) if off in sec_offsets and i in cadence_steps}


def _enforce_harmonic_rhythm(
    beat_progression, beat_to_pcs, beats_per_measure, style="classical"
):
    """
    Limit harmonic churn to at most two changes per measure while preserving
    cadence-friendly late-beat motion.
    """
    if not beat_progression:
        return beat_progression

    out = list(beat_progression)
    start_beat = min(beat_to_pcs.keys())
    end_beat = max(beat_to_pcs.keys())
    total_measures = (end_beat // beats_per_measure) + 1

    for m in range(total_measures):
        measure_start = m * beats_per_measure
        measure_beats = [b for b in range(measure_start, measure_start + beats_per_measure)]
        local = [out[b - start_beat] for b in measure_beats if start_beat <= b <= end_beat]
        if len(local) <= 1:
            continue

        # Keep first half stable; allow one late change.
        first = local[0]
        split_idx = min(len(local) - 1, max(2, beats_per_measure // 2))
        second = local[split_idx]
        if style == "pop":
            # Pop often keeps longer chord pads.
            split_idx = min(len(local) - 1, max(3, beats_per_measure - 1))
            second = local[split_idx]
        elif style == "mariachi":
            # Mariachi allows a slightly earlier dominant lift.
            split_idx = min(len(local) - 1, max(1, beats_per_measure // 2))
            second = local[split_idx]

        for i in range(len(local)):
            chosen = first if i < split_idx else second
            out[(measure_start + i) - start_beat] = chosen

    return out


def _enforce_phrase_cadences(
    beat_progression, beat_to_pcs, beats_per_measure, settings: EngineSettings, phrase_measures=4
):
    """Force weak cadential gravity near phrase ends: ... V -> I."""
    if not beat_progression:
        return beat_progression

    out = list(beat_progression)
    start_beat = min(beat_to_pcs.keys())
    end_beat = max(beat_to_pcs.keys())
    total_measures = (end_beat // beats_per_measure) + 1

    phrase_ends = set(range(phrase_measures - 1, total_measures, phrase_measures))
    phrase_ends.add(total_measures - 1)  # always cadence at the final bar

    for m_end in sorted(phrase_ends):
        final_beat = (m_end + 1) * beats_per_measure - 1
        prev_beat = final_beat - 1
        if final_beat < start_beat or final_beat > end_beat:
            continue

        final_idx = final_beat - start_beat
        tonic_target = "I" if settings.mood == "major" else "i"
        out[final_idx] = tonic_target
        if prev_beat >= start_beat:
            prev_idx = prev_beat - start_beat
            prev_pcs = beat_to_pcs.get(prev_beat, [])
            # Prefer V7 if melody supports chordal 7th (F) or chord tones.
            if any(pc in ROMAN_TO_PCS["V7"] for pc in prev_pcs):
                out[prev_idx] = "V7"
            else:
                out[prev_idx] = "V"
    return out


def _infer_chords_from_melody(
    melody_pitches,
    note_offsets,
    beats_per_measure,
    settings: EngineSettings,
):
    """Infer beat-level functional progression when XML has no harmony symbols."""
    if not melody_pitches:
        return []

    # Build beat buckets, then infer one harmonic function per beat.
    beat_to_pcs = {}
    for midi, off in zip(melody_pitches, note_offsets):
        beat = int(off)
        beat_to_pcs.setdefault(beat, []).append(midi % 12)

    sorted_beats = sorted(beat_to_pcs.keys())
    if not sorted_beats:
        return ["I"] * len(melody_pitches)
    total_beats = max(sorted_beats) + 1

    transition_penalties = _transition_penalties(settings)
    candidates_universe = _candidate_set(settings)
    candidate_limit = _difficulty_candidate_limit(settings)
    layers = []
    for beat in sorted_beats:
        pcs = beat_to_pcs[beat]
        candidates = []
        for rn in candidates_universe:
            coverage = sum(1 for pc in pcs if pc in ROMAN_TO_PCS[rn])
            if coverage > 0:
                candidates.append((rn, coverage))
        candidates.sort(key=lambda x: x[1], reverse=True)
        candidates = [rn for rn, _ in candidates[:candidate_limit]]
        if not candidates:
            candidates = ["I"]
        layers.append(candidates)

    dp = []
    for t, layer in enumerate(layers):
        state = {}
        for rn in layer:
            if t == 0:
                # Bias start on tonic/subdominant.
                tonic_choices = {"I", "vi", "IV"} if settings.mood == "major" else {"i", "VI", "iv"}
                metric = _metric_weight_for_beat(sorted_beats[t], beats_per_measure)
                start_bias = 0.0 if rn in tonic_choices else 0.8 * metric
                state[rn] = (start_bias, None)
                continue
            best_cost = float("inf")
            best_prev = None
            for prev_rn, (prev_cost, _) in dp[t - 1].items():
                trans = transition_penalties.get((prev_rn, rn), 1.1)
                trans += STYLE_TRANSITION_BONUS.get(settings.genre, {}).get((prev_rn, rn), 0.0)
                repeat = 0.45 if (settings.difficulty == "advanced" and prev_rn == rn) else (0.2 if prev_rn == rn else 0.0)
                fit = _melody_fit_penalty(rn, beat_to_pcs[sorted_beats[t]], settings)
                prior = _functional_prior_penalty(
                    rn,
                    sorted_beats[t],
                    beats_per_measure,
                    total_beats,
                    settings,
                )
                metric = _metric_weight_for_beat(sorted_beats[t], beats_per_measure)
                cost = prev_cost + ((trans + repeat + fit + prior) * metric)
                if cost < best_cost:
                    best_cost = cost
                    best_prev = prev_rn
            state[rn] = (best_cost, best_prev)
        dp.append(state)

    # Prefer ending on tonic.
    tonic_target = "I" if settings.mood == "major" else "i"
    final_rn = min(
        dp[-1].keys(),
        key=lambda rn: dp[-1][rn][0] + (0.0 if rn == tonic_target else 0.9),
    )
    beat_progression = [final_rn]
    for t in range(len(dp) - 1, 0, -1):
        beat_progression.append(dp[t][beat_progression[-1]][1] or "I")
    beat_progression.reverse()

    beat_progression = _enforce_harmonic_rhythm(
        beat_progression,
        beat_to_pcs,
        beats_per_measure=beats_per_measure,
        style=settings.genre,
    )
    beat_progression = _enforce_phrase_cadences(
        beat_progression,
        beat_to_pcs,
        beats_per_measure=beats_per_measure,
        settings=settings,
    )

    beat_map = {beat: rn for beat, rn in zip(sorted_beats, beat_progression)}
    expanded = [beat_map.get(int(off), "I") for off in note_offsets]
    return expanded

def generate_test_input(filepath: str):
    """Generates a perfectly formatted baseline XML to ensure the engine runs."""
    score = m21.stream.Score()
    part = m21.stream.Part()
    
    # C Major scale with basic chords
    notes = [("E5", "C"), ("F5", "F"), ("D5", "G"), ("C5", "C")]
    for pitch_str, chord_sym in notes:
        n = m21.note.Note(pitch_str, type='quarter')
        c = m21.harmony.ChordSymbol(chord_sym)
        part.append(c)
        part.append(n)
        
    score.append(part)
    score.write('musicxml', fp=filepath)
    print(f"Generated test input at {filepath}")

def parse_xml(filepath: str, settings: EngineSettings):
    """Extracts melody, harmony, and durations from input XML."""
    score = m21.converter.parse(filepath)
    melody_pitches = []
    chord_symbols = []
    durations = []

    flat = score.flatten()
    ts = score.recurse().getElementsByClass(m21.meter.TimeSignature)
    beats_per_measure = int(ts[0].numerator) if ts else 4
    beat_unit = int(ts[0].denominator) if ts else 4
    style = settings.genre
    harmony_events = sorted(
        [(h.offset, h.figure) for h in flat.getElementsByClass(m21.harmony.ChordSymbol)],
        key=lambda item: item[0],
    )
    melody_part = score.parts[0] if score.parts else flat
    note_and_rest_events = sorted(
        [n for n in melody_part.flatten().notesAndRests],
        key=lambda n: n.offset,
    )

    current_chord = "I"
    h_idx = 0
    offsets = []
    for event in note_and_rest_events:
        if not isinstance(event, m21.note.Note):
            continue
        while h_idx < len(harmony_events) and harmony_events[h_idx][0] <= event.offset:
            current_chord = _normalize_figure_to_roman(harmony_events[h_idx][1])
            h_idx += 1
        melody_pitches.append(event.pitch.midi)
        durations.append(float(event.quarterLength))
        offsets.append(float(event.offset))
        chord_symbols.append(current_chord)

    tonal_center_pc, key_signature_fifths = _tonal_center_from_score(score, melody_pitches, settings)
    c_major_ratio = _c_major_diatonic_ratio(melody_pitches)
    global_c_major_lock = (
        settings.genre == "classical"
        and settings.mood == "major"
        and c_major_ratio >= 0.90
    )
    if global_c_major_lock:
        tonal_center_pc = 0
    diatonic_pcs = sorted(_diatonic_pcs_for_center(tonal_center_pc, settings.mood))
    forbidden_accidentals = [8, 3, 6, 1] if global_c_major_lock else []
    beat_strengths = [
        _metric_weight_for_beat(int(off), beats_per_measure)
        for off in offsets
    ]
    structural_pillars, cadence_steps = _phrase_structural_indices(offsets, beats_per_measure)
    urlinie_steps = _estimate_urlinie_steps(melody_pitches, offsets, beats_per_measure)
    secondary_dom_steps = _secondary_dominant_steps(harmony_events, offsets, beats_per_measure)

    # If no explicit harmony in input, infer a functional progression from melody.
    if not harmony_events:
        chord_symbols = _infer_chords_from_melody(
            melody_pitches,
            offsets,
            beats_per_measure=beats_per_measure,
            settings=settings,
        )

    meta = {
        "beats_per_measure": beats_per_measure,
        "beat_unit": beat_unit,
        "style": style,
        "genre": settings.genre,
        "mood": settings.mood,
        "difficulty": settings.difficulty,
        "has_explicit_harmony": bool(harmony_events),
        "key_signature_fifths": key_signature_fifths,
        "tonal_center_pc": tonal_center_pc,
        "c_major_ratio": c_major_ratio,
        "global_c_major_lock": global_c_major_lock,
        "diatonic_pcs": diatonic_pcs,
        "forbidden_accidentals": forbidden_accidentals,
        "beat_strengths": beat_strengths,
        "structural_pillars": sorted(structural_pillars),
        "urlinie_steps": sorted(urlinie_steps),
        "cadence_steps": sorted(cadence_steps),
        "secondary_dominant_steps": sorted(secondary_dom_steps),
    }
    return score, melody_pitches, chord_symbols, durations, meta

def export_xml(solution_nodes, source_score, output_filepath: str):
    """
    Preserve original melody/format and add generated Alto/Tenor/Bass voices.
    """
    score = copy.deepcopy(source_score)
    source_part = score.parts[0] if score.parts else score.flatten()

    alto_part = m21.stream.Part()
    tenor_part = m21.stream.Part()
    bass_part = m21.stream.Part()
    alto_part.partName = "Alto"
    tenor_part.partName = "Tenor"
    bass_part.partName = "Bass"

    alto_part.append(m21.clef.TrebleClef())
    tenor_part.append(m21.clef.BassClef())
    bass_part.append(m21.clef.BassClef())

    note_cursor = 0
    for event in source_part.flatten().notesAndRests:
        ql = float(event.quarterLength)
        if isinstance(event, m21.note.Rest):
            alto_part.append(m21.note.Rest(quarterLength=ql))
            tenor_part.append(m21.note.Rest(quarterLength=ql))
            bass_part.append(m21.note.Rest(quarterLength=ql))
            continue

        if note_cursor >= len(solution_nodes):
            # Defensive fallback: pad trailing events as rests.
            alto_part.append(m21.note.Rest(quarterLength=ql))
            tenor_part.append(m21.note.Rest(quarterLength=ql))
            bass_part.append(m21.note.Rest(quarterLength=ql))
            continue

        node = solution_nodes[note_cursor]
        note_cursor += 1
        # voices are stored as (bass, tenor, alto, soprano)
        alto_part.append(m21.note.Note(node.voices[2], quarterLength=ql))
        tenor_part.append(m21.note.Note(node.voices[1], quarterLength=ql))
        bass_part.append(m21.note.Note(node.voices[0], quarterLength=ql))

    # Keep the original melody/staff exactly as imported; append harmony parts.
    score.append(alto_part)
    score.append(tenor_part)
    score.append(bass_part)
    score.write("musicxml", fp=output_filepath)


# ── SATB extraction for validation (Phase 3) ─────────────────────

def parse_satb_score_to_solution(xml_string: str):
    """
    Parse a SATB MusicXML score into ChordNode list for validation.
    Returns (solution: list, meta: dict) or (None, meta) if parsing fails.
    """
    from engine.core_engine import ChordNode

    import tempfile
    import os

    with tempfile.NamedTemporaryFile(suffix=".musicxml", delete=False, mode="w", encoding="utf-8") as tmp:
        tmp.write(xml_string)
        tmp_path = tmp.name
    try:
        score = m21.converter.parse(tmp_path)
    finally:
        os.unlink(tmp_path)

    parts = score.parts if score.parts else []
    if len(parts) < 4:
        return None, {"error": "Score must have at least 4 parts (SATB) for validation"}

    name_to_idx = {}
    for i, p in enumerate(parts):
        name = (getattr(p, "partName", None) or getattr(p, "id", "") or "").lower()
        if "soprano" in name or "melody" in name or i == 0:
            name_to_idx["soprano"] = i
        elif "alto" in name or i == 1:
            name_to_idx["alto"] = i
        elif "tenor" in name or i == 2:
            name_to_idx["tenor"] = i
        elif "bass" in name or i == 3:
            name_to_idx["bass"] = i
    if len(name_to_idx) < 4:
        name_to_idx = {"soprano": 0, "alto": 1, "tenor": 2, "bass": 3}

    flat = score.flatten()
    harmony_events = sorted(
        [(h.offset, h.figure) for h in flat.getElementsByClass(m21.harmony.ChordSymbol)],
        key=lambda x: x[0],
    )

    notes_by_part = {}
    for role, idx in name_to_idx.items():
        part = parts[idx]
        notes_by_part[role] = list(part.flatten().notesAndRests)

    n_notes = min(len(notes_by_part[r]) for r in ["soprano", "alto", "tenor", "bass"])
    if n_notes == 0:
        return None, {"error": "No aligned notes found"}

    solution = []
    durations = []
    h_idx = 0
    current_chord = "I"
    for i in range(n_notes):
        sop = notes_by_part["soprano"][i]
        alt = notes_by_part["alto"][i]
        ten = notes_by_part["tenor"][i]
        bas = notes_by_part["bass"][i]
        if isinstance(sop, m21.note.Rest) or isinstance(alt, m21.note.Rest) or isinstance(ten, m21.note.Rest) or isinstance(bas, m21.note.Rest):
            continue
        off = float(getattr(sop, "offset", i * 1.0))
        ql = float(getattr(sop, "quarterLength", 1.0))
        while h_idx < len(harmony_events) and harmony_events[h_idx][0] <= off:
            current_chord = _normalize_figure_to_roman(harmony_events[h_idx][1])
            h_idx += 1
        solution.append(
            ChordNode(
                time_step=len(solution),
                bass=bas.pitch.midi,
                tenor=ten.pitch.midi,
                alto=alt.pitch.midi,
                soprano=sop.pitch.midi,
                chord_symbol=current_chord,
            )
        )
        durations.append(ql)

    ts = score.recurse().getElementsByClass(m21.meter.TimeSignature)
    beats_per_measure = int(ts[0].numerator) if ts else 4
    tonic_pc = 0
    if harmony_events:
        first_chord = harmony_events[0][1]
        if "C" in first_chord or "I" in first_chord:
            tonic_pc = 0
    meta = {"beats_per_measure": beats_per_measure, "tonic_pc": tonic_pc, "durations": durations}
    return solution, meta


# ── String-based helpers for API layer ──────────────────────────

def parse_xml_string(xml_string: str, settings: EngineSettings):
    """Same as parse_xml but accepts MusicXML as a string."""
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".musicxml", delete=False, mode="w", encoding="utf-8") as tmp:
        tmp.write(xml_string)
        tmp_path = tmp.name
    try:
        return parse_xml(tmp_path, settings)
    finally:
        os.unlink(tmp_path)


def export_xml_string(solution_nodes, source_score, instruments: list[str] | None = None) -> str:
    """Return harmonized MusicXML as a string instead of writing to file."""
    import tempfile, os
    score = copy.deepcopy(source_score)
    source_part = score.parts[0] if score.parts else score.flatten()

    voice_map: dict[str, m21.stream.Part] = {}
    for name in ["alto", "tenor", "bass"]:
        if instruments and name not in instruments:
            continue
        part = m21.stream.Part()
        part.partName = name.capitalize()
        part.append(m21.clef.TrebleClef() if name == "alto" else m21.clef.BassClef())
        voice_map[name] = part

    note_cursor = 0
    for event in source_part.flatten().notesAndRests:
        ql = float(event.quarterLength)
        if isinstance(event, m21.note.Rest):
            for part in voice_map.values():
                part.append(m21.note.Rest(quarterLength=ql))
            continue
        if note_cursor >= len(solution_nodes):
            for part in voice_map.values():
                part.append(m21.note.Rest(quarterLength=ql))
            continue
        node = solution_nodes[note_cursor]
        note_cursor += 1
        voice_midi = {"alto": node.voices[2], "tenor": node.voices[1], "bass": node.voices[0]}
        for name, part in voice_map.items():
            part.append(m21.note.Note(voice_midi[name], quarterLength=ql))

    for part in voice_map.values():
        score.append(part)

    with tempfile.NamedTemporaryFile(suffix=".musicxml", delete=False, mode="w") as tmp:
        tmp_path = tmp.name
    score.write("musicxml", fp=tmp_path)
    try:
        with open(tmp_path, "r", encoding="utf-8") as f:
            return f.read()
    finally:
        os.unlink(tmp_path)