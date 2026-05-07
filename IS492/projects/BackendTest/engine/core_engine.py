"""
HarmonyForge Logic Core — CSP-based SATB harmonization.

Implements a layered DAG + Viterbi shortest-path solver (HarmonySolver blueprint).
Schenkerian Lite: phrase boundaries, cadence anchors, structural pillars.
Hard rules: voice order, spacing, parallel fifths, tritone resolution.
Soft rules: leading tone, leaps, repeated function.
"""

import itertools
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Set, Tuple


VOICE_RANGES = {
    "bass": (40, 62),      # E2-D4
    "tenor": (48, 67),     # C3-G4
    "alto": (55, 74),      # G3-D5
    "soprano": (60, 81),   # C4-A5
}

# Roman numeral dictionary in C major (simple baseline).
CHORD_DICTIONARY: Dict[str, List[int]] = {
    "I": [0, 4, 7],
    "ii": [2, 5, 9],
    "iii": [4, 7, 11],
    "IV": [5, 9, 0],
    "V": [7, 11, 2],
    "V7": [7, 11, 2, 5],
    "vi": [9, 0, 4],
    "vii°": [11, 2, 5],
    "vii°7": [11, 2, 5, 8],
    "V/V": [2, 6, 9],
    "V7/V": [2, 6, 9, 0],
    # Natural/harmonic minor support (C minor reference set).
    "i": [0, 3, 7],
    "ii°": [2, 5, 8],
    "III": [3, 7, 10],
    "iv": [5, 8, 0],
    "v": [7, 10, 2],
    "VI": [8, 0, 3],
    "VII": [10, 2, 5],
    "i7": [0, 3, 7, 10],
    "ii°7": [2, 5, 8, 11],
    "iv7": [5, 8, 0, 3],
    "vi7": [9, 0, 4, 7],
    "ii7": [2, 5, 9, 0],
    "Imaj7": [0, 4, 7, 11],
    "IVmaj7": [5, 9, 0, 4],
}
PITCHNAME_TO_ROMAN = {
    "C": "I",
    "Cm": "i",
    "Dm": "ii",
    "D": "V/V",
    "D7": "V7/V",
    "Em": "iii",
    "E": "III",
    "F": "IV",
    "Fm": "iv",
    "G": "V",
    "G7": "V7",
    "Gm": "v",
    "Am": "vi",
    "A": "VI",
    "Bdim": "vii°",
    "Cm7": "i7",
    "Dm7": "ii7",
    "Fmaj7": "IVmaj7",
    "Cmaj7": "Imaj7",
}
MAX_COLUMN_CANDIDATES = 180


@dataclass(frozen=True)
class StructuralPlan:
    phrase_boundaries: List[Tuple[int, int]]
    anchor_steps: Set[int]


@dataclass
class ChordNode:
    time_step: int
    bass: int
    tenor: int
    alto: int
    soprano: int
    chord_symbol: str = ""

    @property
    def voices(self) -> Tuple[int, int, int, int]:
        return (self.bass, self.tenor, self.alto, self.soprano)


@dataclass
class GraphBuildStats:
    layer_sizes: List[int]
    total_nodes: int
    strict_edges: int
    soft_edges: int


@dataclass(frozen=True)
class MethodologyProfile:
    name: str
    max_candidates: int
    use_anchor_lock: bool
    strict_first: bool


def _fit_to_range_by_octave(midi_note: int, low: int, high: int) -> int:
    note = midi_note
    while note < low:
        note += 12
    while note > high:
        note -= 12
    # If still impossible due to extreme values, clamp.
    return min(max(note, low), high)


def normalize_chord_symbol(symbol: str) -> str:
    clean = (symbol or "").strip()
    if clean in CHORD_DICTIONARY:
        return clean
    if clean in PITCHNAME_TO_ROMAN:
        mapped = PITCHNAME_TO_ROMAN[clean]
        if mapped in CHORD_DICTIONARY:
            return mapped
    # Tolerate inversions and annotations, e.g. "V6", "V7/ii", "I64".
    if "/" in clean:
        clean = clean.split("/", 1)[0]
    if clean in PITCHNAME_TO_ROMAN:
        mapped = PITCHNAME_TO_ROMAN[clean]
        if mapped in CHORD_DICTIONARY:
            return mapped
    if clean.startswith("V7/V"):
        return "V7/V"
    if clean.startswith("V/V"):
        return "V/V"
    if clean.startswith("V7"):
        return "V7"
    if clean.startswith("Imaj7"):
        return "Imaj7"
    if clean.startswith("IVmaj7"):
        return "IVmaj7"
    if clean.startswith("ii7"):
        return "ii7"
    if clean.startswith("i7"):
        return "i7"
    if clean.startswith("ii°7"):
        return "ii°7"
    if clean.startswith("iv7"):
        return "iv7"
    if clean.startswith("V"):
        return "V"
    if clean.startswith("IV"):
        return "IV"
    if clean.startswith("iii"):
        return "iii"
    if clean.startswith("ii"):
        return "ii"
    if clean.startswith("vi"):
        return "vi"
    if clean.startswith("vii°7"):
        return "vii°7"
    if clean.startswith("vii"):
        return "vii°"
    if clean.startswith("ii°"):
        return "ii°"
    if clean.startswith("iv"):
        return "iv"
    if clean.startswith("v"):
        return "v"
    if clean.startswith("VI"):
        return "VI"
    if clean.startswith("VII"):
        return "VII"
    if clean.startswith("III"):
        return "III"
    if clean.startswith("i"):
        return "i"
    if clean.startswith("I"):
        return "I"
    return "I"


def detect_structure(
    chords: Sequence[str],
    structural_pillars: Optional[Set[int]] = None,
    urlinie_steps: Optional[Set[int]] = None,
) -> StructuralPlan:
    """Phase A: lightweight phrase + cadence anchors for hierarchical solving."""
    total = len(chords)
    if total == 0:
        return StructuralPlan([], set())

    normalized = [normalize_chord_symbol(c) for c in chords]
    boundaries: List[Tuple[int, int]] = []
    i = 0
    while i < total:
        j = min(i + 8, total)
        boundaries.append((i, j - 1))
        i = j

    anchors: Set[int] = {0, total - 1}
    for t in range(total - 1):
        if normalized[t].startswith("V") and normalized[t + 1] == "I":
            anchors.add(t)
            anchors.add(t + 1)
    for _, end in boundaries:
        anchors.add(end)

    if structural_pillars:
        anchors.update(i for i in structural_pillars if 0 <= i < total)
    if urlinie_steps:
        anchors.update(i for i in urlinie_steps if 0 <= i < total)

    return StructuralPlan(boundaries, anchors)


def is_valid_voicing(
    bass: int,
    tenor: int,
    alto: int,
    soprano: int,
    chord_pcs: Sequence[int],
    strict_spelling: bool = True,
    allow_non_chord_soprano: bool = False,
    allowed_pcs: Optional[Set[int]] = None,
    structural_bass_pcs: Optional[Set[int]] = None,
) -> bool:
    if not (
        VOICE_RANGES["bass"][0] <= bass <= VOICE_RANGES["bass"][1]
        and VOICE_RANGES["tenor"][0] <= tenor <= VOICE_RANGES["tenor"][1]
        and VOICE_RANGES["alto"][0] <= alto <= VOICE_RANGES["alto"][1]
        and VOICE_RANGES["soprano"][0] <= soprano <= VOICE_RANGES["soprano"][1]
    ):
        return False

    # SATB ordering and spacing.
    if not (bass < tenor < alto < soprano):
        return False
    if soprano - alto > 12 or alto - tenor > 19 or tenor - bass > 19:
        return False

    pcs = [v % 12 for v in (bass, tenor, alto, soprano)]
    lower_pcs = [bass % 12, tenor % 12, alto % 12]
    soprano_pc = soprano % 12
    required = set(chord_pcs)
    present = set(pcs)

    if allowed_pcs is not None and any(pc not in allowed_pcs for pc in pcs):
        return False

    # Lower voices define harmonic support and must stay chordal.
    if any(pc not in required for pc in lower_pcs):
        return False

    # At structural pillars, bass should support Urlinie by root or 1st inversion.
    if structural_bass_pcs is not None and (bass % 12) not in structural_bass_pcs:
        return False

    covered = set(lower_pcs)
    if soprano_pc in required:
        covered.add(soprano_pc)

    if strict_spelling:
        if allow_non_chord_soprano:
            required_coverage = min(len(required), 3 if soprano_pc not in required else 4)
            if len(covered.intersection(required)) < required_coverage:
                return False
        else:
            if not required.issubset(present):
                return False
    elif len(covered.intersection(required)) < min(3, len(required)):
        return False

    # Avoid doubled leading tone in this C-major baseline.
    if pcs.count(11) > 1:
        return False
    return True


def _iter_lower_voice_space() -> itertools.product:
    return itertools.product(
        range(VOICE_RANGES["bass"][0], VOICE_RANGES["bass"][1] + 1),
        range(VOICE_RANGES["tenor"][0], VOICE_RANGES["tenor"][1] + 1),
        range(VOICE_RANGES["alto"][0], VOICE_RANGES["alto"][1] + 1),
    )


def _vertical_penalty(node: ChordNode, chord_pcs: Sequence[int]) -> float:
    """
    Rank columns before graph solving so we keep musically plausible nodes while
    controlling combinatorial growth.
    """
    b, t, a, s = node.voices
    penalties = 0.0

    # Prefer moderate upper spacing.
    penalties += max(0, (s - a) - 8) * 0.25
    penalties += max(0, (a - t) - 8) * 0.25
    penalties += max(0, (t - b) - 14) * 0.2

    # Prefer bass near root and avoid doubled thirds in triads.
    triad = list(chord_pcs[:3]) if len(chord_pcs) >= 3 else list(chord_pcs)
    if triad:
        root = triad[0]
        third = triad[1] if len(triad) > 1 else None
        if b % 12 != root:
            penalties += 0.8
        if third is not None:
            count_third = sum(1 for v in node.voices if v % 12 == third)
            if count_third > 1:
                penalties += 1.0 + (count_third - 2) * 0.5

    return penalties


def _build_candidate_pass(
    time_step: int,
    chord_symbol: str,
    melody_note: int,
    chord_pcs: Sequence[int],
    locked: Tuple[int, int, int, int] | None,
    *,
    strict_spelling: bool,
    allow_non_chord_soprano: bool,
    allowed_pcs: Optional[Set[int]] = None,
    structural_bass_pcs: Optional[Set[int]] = None,
) -> List[ChordNode]:
    nodes: List[ChordNode] = []
    for bass, tenor, alto in _iter_lower_voice_space():
        if is_valid_voicing(
            bass,
            tenor,
            alto,
            melody_note,
            chord_pcs,
            strict_spelling=strict_spelling,
            allow_non_chord_soprano=allow_non_chord_soprano,
            allowed_pcs=allowed_pcs,
            structural_bass_pcs=structural_bass_pcs,
        ):
            node = ChordNode(time_step, bass, tenor, alto, melody_note, chord_symbol)
            if locked is None or node.voices == locked:
                nodes.append(node)
    return nodes


def generate_column(
    time_step: int,
    chord_symbol: str,
    melody_note: int,
    locked_voicings: Dict[int, Tuple[int, int, int, int]] | None = None,
    max_candidates: Optional[int] = None,
    structural_step: bool = False,
    allowed_pcs: Optional[Set[int]] = None,
) -> List[ChordNode]:
    chord_symbol = normalize_chord_symbol(chord_symbol)
    chord_pcs = CHORD_DICTIONARY.get(chord_symbol, CHORD_DICTIONARY["I"])
    structural_bass_pcs: Optional[Set[int]] = None
    if structural_step and chord_pcs:
        root = chord_pcs[0]
        third = chord_pcs[1] if len(chord_pcs) > 1 else chord_pcs[0]
        structural_bass_pcs = {root % 12, third % 12}
    locked = (locked_voicings or {}).get(time_step)

    candidates = _build_candidate_pass(
        time_step,
        chord_symbol,
        melody_note,
        chord_pcs,
        locked,
        strict_spelling=True,
        allow_non_chord_soprano=False,
        allowed_pcs=allowed_pcs,
        structural_bass_pcs=structural_bass_pcs,
    )

    # Relax 1: allow soprano non-chord tone, preserve lower-voice harmony.
    if not candidates:
        candidates = _build_candidate_pass(
            time_step,
            chord_symbol,
            melody_note,
            chord_pcs,
            locked,
            strict_spelling=True,
            allow_non_chord_soprano=True,
            allowed_pcs=allowed_pcs,
            structural_bass_pcs=structural_bass_pcs,
        )

    # Relax 2: partial chord coverage in worst-case overconstrained moments.
    if not candidates:
        candidates = _build_candidate_pass(
            time_step,
            chord_symbol,
            melody_note,
            chord_pcs,
            locked,
            strict_spelling=False,
            allow_non_chord_soprano=True,
            allowed_pcs=allowed_pcs,
            structural_bass_pcs=structural_bass_pcs,
        )

    # Remove duplicate voicings and trim to manageable layer width.
    unique_nodes: Dict[Tuple[int, int, int, int], ChordNode] = {}
    for node in candidates:
        unique_nodes.setdefault(node.voices, node)
    ranked = sorted(unique_nodes.values(), key=lambda n: _vertical_penalty(n, chord_pcs))
    cap = MAX_COLUMN_CANDIDATES if max_candidates is None else max_candidates
    if cap > 0 and locked is None and len(ranked) > cap:
        return ranked[:cap]
    return ranked


def _is_parallel_perfect(a0: int, a1: int, b0: int, b1: int) -> bool:
    int0 = (a1 - a0) % 12
    int1 = (b1 - b0) % 12
    moved = a0 != b0 and a1 != b1
    same_direction = (b0 - a0) * (b1 - a1) > 0
    return moved and same_direction and int0 in (0, 7) and int1 == int0


# Tritone resolution (Schenkerian: A4 out, d5 in)
DIM_CHORDS = frozenset({"vii°", "vii°7", "ii°", "ii°7"})
RESOLUTION_TARGETS = frozenset({"I", "i", "V"})


def _is_tritone(pc1: int, pc2: int) -> bool:
    """True if pc1 and pc2 form a tritone (6 semitones)."""
    return (pc1 - pc2) % 12 == 6 or (pc2 - pc1) % 12 == 6


def _check_tritone_resolution(
    prev_voices: Tuple[int, int, int, int],
    curr_voices: Tuple[int, int, int, int],
    voice_pairs: List[Tuple[int, int]],
) -> Optional[str]:
    """
    Check tritone pairs. Returns:
    - "improper" if resolution violates rules (red)
    - "suboptimal" if similar motion when contrary preferred (blue)
    - None if proper or no tritone pairs
    """
    improper = False
    suboptimal = False
    for i, j in voice_pairs:
        a_i, a_j = prev_voices[i] % 12, prev_voices[j] % 12
        b_i, b_j = curr_voices[i] % 12, curr_voices[j] % 12
        if not _is_tritone(a_i, a_j):
            continue
        move_i = prev_voices[i] - curr_voices[i]
        move_j = prev_voices[j] - curr_voices[j]
        step_i = abs(move_i) <= 2
        step_j = abs(move_j) <= 2
        contrary = (move_i > 0 and move_j < 0) or (move_i < 0 and move_j > 0)
        same_dir = (move_i > 0 and move_j > 0) or (move_i < 0 and move_j < 0)
        # Proper: both stepwise, contrary motion
        if step_i and step_j and contrary:
            continue  # OK
        # Improper: large leaps or neither voice resolves by step
        if not step_i or not step_j:
            improper = True
        # Suboptimal: similar motion (acceptable but less preferred)
        elif same_dir:
            suboptimal = True
    if improper:
        return "improper"
    if suboptimal:
        return "suboptimal"
    return None


def _difficulty_profile(difficulty: str) -> Dict[str, float]:
    d = (difficulty or "intermediate").lower()
    if d == "beginner":
        return {
            "step_weight": 0.15,
            "leap_weight": 1.8,
            "common_tone_bonus": -0.5,
            "repeat_function_penalty": 0.1,
        }
    if d == "advanced":
        return {
            "step_weight": 0.25,
            "leap_weight": 1.1,
            "common_tone_bonus": -1.2,
            "repeat_function_penalty": 0.35,
        }
    return {
        "step_weight": 0.2,
        "leap_weight": 1.4,
        "common_tone_bonus": -0.9,
        "repeat_function_penalty": 0.2,
    }


def _methodology_profiles(difficulty: str) -> List[MethodologyProfile]:
    """
    Blend methodologies with deterministic profile retries:
    - HarmonySolver-like: wider vertical search
    - SchenkComposer-like: stronger anchor lock
    - ProGress-like: phrase-consistent fallback
    """
    d = (difficulty or "intermediate").lower()
    if d == "beginner":
        return [
            MethodologyProfile("harmonysolver-strict", 220, True, True),
            MethodologyProfile("schenkcomposer-anchor", 180, True, False),
            MethodologyProfile("progress-stable", 140, False, False),
        ]
    if d == "advanced":
        return [
            MethodologyProfile("harmonysolver-wide", 280, True, True),
            MethodologyProfile("schenkcomposer-wide", 240, True, False),
            MethodologyProfile("progress-flex", 180, False, False),
        ]
    return [
        MethodologyProfile("harmonysolver-balanced", 240, True, True),
        MethodologyProfile("schenkcomposer-balanced", 200, True, False),
        MethodologyProfile("progress-balanced", 160, False, False),
    ]


def _solution_quality_score(
    path: Sequence[ChordNode],
    *,
    difficulty: str,
    beat_strengths: Optional[Sequence[float]],
    tonic_pc: int,
    diatonic_pcs: Optional[Set[int]],
) -> float:
    if len(path) <= 1:
        return 0.0
    total = 0.0
    for t in range(1, len(path)):
        total += calculate_transition_cost(
            path[t - 1],
            path[t],
            strict_rules=False,
            difficulty=difficulty,
            tonic_pc=tonic_pc,
            metric_weight=(beat_strengths[t] if beat_strengths and t < len(beat_strengths) else 1.0),
            diatonic_pcs=diatonic_pcs,
        )
    # Add validation-derived penalties so we choose globally cleaner paths.
    for v in validate_solution(path, tonic_pc=tonic_pc):
        severity = str(v.get("severity", "soft"))
        code = str(v.get("code", ""))
        if severity == "hard":
            total += 100.0
        elif code in {"PARALLEL_PERFECT", "LEADING_TONE_UNRESOLVED"}:
            total += 8.0
        else:
            total += 2.0
    return total


def _repair_local_violations(
    path: List[ChordNode],
    *,
    chords: Sequence[str],
    melody: Sequence[int],
    difficulty: str,
    tonic_pc: int,
    diatonic_pcs: Optional[Set[int]],
    beat_strengths: Optional[Sequence[float]],
    structural_steps: Set[int],
    allowed_pcs_by_step: Optional[Dict[int, Set[int]]],
    max_candidates: int,
    user_locked: Optional[Dict[int, Tuple[int, int, int, int]]],
) -> List[ChordNode]:
    """
    ComposerX-style repair pass:
    re-solve local windows around key soft violations while keeping the rest fixed.
    """
    n = len(path)
    if n <= 2:
        return path
    focus_codes = {"PARALLEL_PERFECT", "LEADING_TONE_UNRESOLVED", "LARGE_LEAP"}
    violations = validate_solution(path, tonic_pc=tonic_pc)
    focus_steps = sorted(
        {
            int(v.get("time_step", -1))
            for v in violations
            if str(v.get("code", "")) in focus_codes and 0 <= int(v.get("time_step", -1)) < n
        }
    )
    if not focus_steps:
        return path

    best = path
    best_score = _solution_quality_score(
        best,
        difficulty=difficulty,
        beat_strengths=beat_strengths,
        tonic_pc=tonic_pc,
        diatonic_pcs=diatonic_pcs,
    )
    for step in focus_steps[:4]:
        start = max(0, step - 2)
        end = min(n - 1, step + 2)
        local_locked = {t: best[t].voices for t in range(n) if t < start or t > end}
        if user_locked:
            local_locked.update(user_locked)
        try:
            local_layers = _build_layers(
                chords,
                melody,
                locked_voicings=local_locked,
                max_candidates=max_candidates,
                structural_steps=structural_steps,
                allowed_pcs_by_step=allowed_pcs_by_step,
            )
            local_path = _shortest_path_dag(
                local_layers,
                strict_rules=False,
                difficulty=difficulty,
                beat_strengths=beat_strengths,
                tonic_pc=tonic_pc,
                diatonic_pcs=diatonic_pcs,
            )
        except RuntimeError:
            continue
        local_score = _solution_quality_score(
            local_path,
            difficulty=difficulty,
            beat_strengths=beat_strengths,
            tonic_pc=tonic_pc,
            diatonic_pcs=diatonic_pcs,
        )
        if local_score < best_score:
            best = local_path
            best_score = local_score
    return best


def calculate_transition_cost(
    node_a: ChordNode,
    node_b: ChordNode,
    strict_rules: bool = True,
    difficulty: str = "intermediate",
    tonic_pc: int = 0,
    metric_weight: float = 1.0,
    diatonic_pcs: Optional[Set[int]] = None,
) -> float:
    a = node_a.voices
    b = node_b.voices
    profile = _difficulty_profile(difficulty)

    # Hard floor: keep voice identity and avoid impossible jumps.
    if not (b[0] < b[1] < b[2] < b[3]):
        return float("inf")
    leap_cap = 14 if strict_rules else 19
    for i in range(4):
        if abs(b[i] - a[i]) > leap_cap:
            return float("inf")

    # Soft costs.
    cost = 0.0
    for i in range(4):
        leap = abs(b[i] - a[i])
        if leap == 0:
            cost -= 0.4
        elif leap > 4:
            cost += leap * profile["leap_weight"]
        else:
            cost += leap * profile["step_weight"]

    # Schenkerian prolongation: prefer holding harmony on weak beats.
    if node_a.chord_symbol == node_b.chord_symbol:
        if metric_weight < 1.2:
            cost -= 0.8
        else:
            cost += profile["repeat_function_penalty"]
    elif metric_weight < 1.2:
        cost += 0.8

    # Tonal consistency: make out-of-key tones very expensive if a diatonic set exists.
    if diatonic_pcs is not None:
        chromatic_count = sum(1 for pc in (v % 12 for v in b) if pc not in diatonic_pcs)
        if chromatic_count > 0:
            cost += chromatic_count * 5.0 * metric_weight

    # Penalty: parallel perfects (knowledge_base-informed weight)
    parallel_penalty = 0.0
    for i in range(3):
        for j in range(i + 1, 4):
            if _is_parallel_perfect(a[i], a[j], b[i], b[j]):
                w = 10.0
                try:
                    from .knowledge_rules import get_penalty_weight
                    w = get_penalty_weight("PARALLEL_PERFECT")
                except ImportError:
                    pass
                parallel_penalty += w
    cost += parallel_penalty * metric_weight

    # Penalty: unresolved leading tones (knowledge_base-informed weight)
    leading_pc = (tonic_pc - 1) % 12
    unresolved = 0
    for i in range(4):
        if a[i] % 12 == leading_pc and b[i] % 12 != tonic_pc:
            unresolved += 1
    lt_weight = 5.0
    try:
        from .knowledge_rules import get_penalty_weight
        lt_weight = get_penalty_weight("LEADING_TONE_UNRESOLVED")
    except ImportError:
        pass
    cost += unresolved * lt_weight * metric_weight

    # Reward common tones between adjacent sonorities to stabilize perceived intonation.
    common_tones = len({v % 12 for v in a}.intersection({v % 12 for v in b}))
    cost += profile["common_tone_bonus"] * common_tones

    # Reward parsimonious Alto/Tenor movement.
    for i in (1, 2):
        inner_move = abs(b[i] - a[i])
        if inner_move <= 2:
            cost -= 0.9
        elif inner_move > 5:
            cost += 1.5

    # Penalize abrupt harmonic-root jumps in bass function.
    root_a = CHORD_DICTIONARY.get(node_a.chord_symbol, CHORD_DICTIONARY["I"])[0]
    root_b = CHORD_DICTIONARY.get(node_b.chord_symbol, CHORD_DICTIONARY["I"])[0]
    root_motion = min((root_b - root_a) % 12, (root_a - root_b) % 12)
    if root_motion >= 6:
        cost += 1.4

    # Penalty: improper/suboptimal tritone resolution (dim→I/V)
    if node_a.chord_symbol in DIM_CHORDS and node_b.chord_symbol in RESOLUTION_TARGETS:
        chord_pcs = set(CHORD_DICTIONARY.get(node_a.chord_symbol, []))
        voice_pairs: List[Tuple[int, int]] = []
        for i in range(3):
            for j in range(i + 1, 4):
                if a[i] % 12 in chord_pcs and a[j] % 12 in chord_pcs:
                    if _is_tritone(a[i] % 12, a[j] % 12):
                        voice_pairs.append((i, j))
        if voice_pairs:
            result = _check_tritone_resolution(a, b, voice_pairs)
            if result == "improper":
                tritone_weight = 8.0
                try:
                    from .knowledge_rules import get_penalty_weight
                    tritone_weight = get_penalty_weight("TRITONE_RESOLUTION_IMPROPER")
                except ImportError:
                    pass
                cost += tritone_weight * metric_weight
            elif result == "suboptimal":
                cost += 2.0 * metric_weight

    # Guard against accidental NaN/inf propagation in non-strict mode.
    if not math.isfinite(cost):
        return float("inf")

    return cost


def _build_layers(
    chords: Sequence[str],
    melody: Sequence[int],
    locked_voicings: Dict[int, Tuple[int, int, int, int]] | None = None,
    max_candidates: Optional[int] = None,
    structural_steps: Optional[Set[int]] = None,
    allowed_pcs_by_step: Optional[Dict[int, Set[int]]] = None,
) -> List[List[ChordNode]]:
    layers: List[List[ChordNode]] = []
    for t in range(len(chords)):
        column = generate_column(
            t,
            chords[t],
            melody[t],
            locked_voicings=locked_voicings,
            max_candidates=max_candidates,
            structural_step=t in (structural_steps or set()),
            allowed_pcs=(allowed_pcs_by_step or {}).get(t),
        )
        if not column:
            raise ValueError(f"No valid voicings at t={t} for {chords[t]}")
        layers.append(column)
    return layers


def _count_possible_edges(layers: List[List[ChordNode]], difficulty: str = "intermediate") -> Tuple[int, int]:
    strict_edges = 0
    soft_edges = 0
    for t in range(1, len(layers)):
        for prev in layers[t - 1]:
            for curr in layers[t]:
                if calculate_transition_cost(prev, curr, strict_rules=True) != float("inf"):
                    strict_edges += 1
                elif (
                    calculate_transition_cost(
                        prev, curr, strict_rules=False, difficulty=difficulty
                    )
                    != float("inf")
                ):
                    soft_edges += 1
    return strict_edges, soft_edges


def build_schenkerian_graph_matrix(
    chords: Sequence[str],
    melody: Sequence[int],
    locked_voicings: Dict[int, Tuple[int, int, int, int]] | None = None,
    max_candidates: Optional[int] = None,
    difficulty: str = "intermediate",
    structural_steps: Optional[Set[int]] = None,
    allowed_pcs_by_step: Optional[Dict[int, Set[int]]] = None,
) -> Tuple[List[List[ChordNode]], GraphBuildStats]:
    """
    Builds the layered DAG (SingleLevelGraph-like matrix):
    - Y-axis: per-time-step valid voicing nodes
    - X-axis: implicit edges via transition constraints
    - Z-axis anchors handled by caller via locked_voicings
    """
    normalized_melody = [
        _fit_to_range_by_octave(n, VOICE_RANGES["soprano"][0], VOICE_RANGES["soprano"][1])
        for n in melody
    ]
    layers = _build_layers(
        chords,
        normalized_melody,
        locked_voicings=locked_voicings,
        max_candidates=max_candidates,
        structural_steps=structural_steps,
        allowed_pcs_by_step=allowed_pcs_by_step,
    )
    strict_edges, soft_edges = _count_possible_edges(layers, difficulty=difficulty)
    stats = GraphBuildStats(
        layer_sizes=[len(layer) for layer in layers],
        total_nodes=sum(len(layer) for layer in layers),
        strict_edges=strict_edges,
        soft_edges=soft_edges,
    )
    return layers, stats


def _shortest_path_dag(
    layers: List[List[ChordNode]],
    strict_rules: bool = True,
    difficulty: str = "intermediate",
    beat_strengths: Optional[Sequence[float]] = None,
    tonic_pc: int = 0,
    diatonic_pcs: Optional[Set[int]] = None,
) -> List[ChordNode]:
    costs: List[List[Tuple[float, int | None]]] = [
        [(float("inf"), None) for _ in layer] for layer in layers
    ]
    for i in range(len(layers[0])):
        costs[0][i] = (0.0, None)

    for t in range(1, len(layers)):
        prev_layer = layers[t - 1]
        curr_layer = layers[t]
        for curr_idx, curr_node in enumerate(curr_layer):
            best_cost = float("inf")
            best_prev = None
            for prev_idx, prev_node in enumerate(prev_layer):
                prev_cost = costs[t - 1][prev_idx][0]
                if prev_cost == float("inf"):
                    continue
                edge_cost = calculate_transition_cost(
                    prev_node,
                    curr_node,
                    strict_rules=strict_rules,
                    difficulty=difficulty,
                    tonic_pc=tonic_pc,
                    metric_weight=(beat_strengths[t] if beat_strengths and t < len(beat_strengths) else 1.0),
                    diatonic_pcs=diatonic_pcs,
                )
                candidate = prev_cost + edge_cost
                if candidate < best_cost:
                    best_cost = candidate
                    best_prev = prev_idx
            costs[t][curr_idx] = (best_cost, best_prev)

    end_cost = float("inf")
    end_idx = None
    for idx, (c, _) in enumerate(costs[-1]):
        if c < end_cost:
            end_cost = c
            end_idx = idx
    if end_idx is None or end_cost == float("inf"):
        raise RuntimeError("Graph disconnected: no admissible SATB path.")

    path: List[ChordNode] = []
    current = end_idx
    for t in range(len(layers) - 1, -1, -1):
        path.insert(0, layers[t][current])
        prev = costs[t][current][1]
        current = 0 if prev is None else prev
    return path


def solve_harmony(
    chords: Sequence[str],
    melody: Sequence[int],
    locked_voicings: Dict[int, Tuple[int, int, int, int]] | None = None,
    max_candidates: Optional[int] = 180,
    difficulty: str = "intermediate",
    structural_pillars: Optional[Set[int]] = None,
    urlinie_steps: Optional[Set[int]] = None,
    beat_strengths: Optional[Sequence[float]] = None,
    tonic_pc: int = 0,
    diatonic_pcs: Optional[Set[int]] = None,
    secondary_dominant_steps: Optional[Set[int]] = None,
    cadence_steps: Optional[Set[int]] = None,
) -> List[ChordNode]:
    """
    Hierarchical CSP/DAG solver:
    1) detect phrase/cadence anchors (background),
    2) solve full foreground graph once,
    3) lock anchor voicings and re-solve for consistency.
    """
    if len(chords) != len(melody):
        raise ValueError("Chord and melody lengths must match.")
    if not chords:
        return []

    # Keep melodic contour class while ensuring soprano feasibility.
    normalized_melody = [
        _fit_to_range_by_octave(n, VOICE_RANGES["soprano"][0], VOICE_RANGES["soprano"][1])
        for n in melody
    ]

    structure = detect_structure(
        chords,
        structural_pillars=structural_pillars,
        urlinie_steps=urlinie_steps,
    )
    allowed_pcs_by_step: Dict[int, Set[int]] = {}
    if diatonic_pcs:
        raised_fourth = (tonic_pc + 6) % 12  # e.g., F# in C major for V/V
        for t in range(len(chords)):
            allowed = set(diatonic_pcs)
            if (
                secondary_dominant_steps
                and cadence_steps
                and t in secondary_dominant_steps
                and t in cadence_steps
            ):
                allowed.add(raised_fourth)
            allowed_pcs_by_step[t] = allowed

    profiles = _methodology_profiles(difficulty)
    if max_candidates is not None and max_candidates > 0:
        profiles = [
            MethodologyProfile(
                p.name,
                max(max_candidates, p.max_candidates),
                p.use_anchor_lock,
                p.strict_first,
            )
            for p in profiles
        ]

    best_path: Optional[List[ChordNode]] = None
    best_score = float("inf")

    for profile in profiles:
        try:
            base_layers = _build_layers(
                chords,
                normalized_melody,
                max_candidates=profile.max_candidates,
                structural_steps=structure.anchor_steps,
                allowed_pcs_by_step=allowed_pcs_by_step if allowed_pcs_by_step else None,
            )
            if profile.strict_first:
                first_pass = _shortest_path_dag(
                    base_layers,
                    strict_rules=True,
                    difficulty=difficulty,
                    beat_strengths=beat_strengths,
                    tonic_pc=tonic_pc,
                    diatonic_pcs=diatonic_pcs,
                )
            else:
                first_pass = _shortest_path_dag(
                    base_layers,
                    strict_rules=False,
                    difficulty=difficulty,
                    beat_strengths=beat_strengths,
                    tonic_pc=tonic_pc,
                    diatonic_pcs=diatonic_pcs,
                )
        except RuntimeError:
            continue

        candidate = first_pass
        if profile.use_anchor_lock:
            anchor_locked: Dict[int, Tuple[int, int, int, int]] = {
                t: first_pass[t].voices for t in structure.anchor_steps if 0 <= t < len(first_pass)
            }
            merged_locked = dict(anchor_locked)
            if locked_voicings:
                merged_locked.update(locked_voicings)
            try:
                refined_layers = _build_layers(
                    chords,
                    normalized_melody,
                    locked_voicings=merged_locked,
                    max_candidates=profile.max_candidates,
                    structural_steps=structure.anchor_steps,
                    allowed_pcs_by_step=allowed_pcs_by_step if allowed_pcs_by_step else None,
                )
                candidate = _shortest_path_dag(
                    refined_layers,
                    strict_rules=profile.strict_first,
                    difficulty=difficulty,
                    beat_strengths=beat_strengths,
                    tonic_pc=tonic_pc,
                    diatonic_pcs=diatonic_pcs,
                )
            except RuntimeError:
                candidate = first_pass

        score = _solution_quality_score(
            candidate,
            difficulty=difficulty,
            beat_strengths=beat_strengths,
            tonic_pc=tonic_pc,
            diatonic_pcs=diatonic_pcs,
        )
        if score < best_score:
            best_score = score
            best_path = candidate

    if best_path is None:
        raise RuntimeError("Graph disconnected: no admissible SATB path across methodology profiles.")
    repaired = _repair_local_violations(
        best_path,
        chords=chords,
        melody=normalized_melody,
        difficulty=difficulty,
        tonic_pc=tonic_pc,
        diatonic_pcs=diatonic_pcs,
        beat_strengths=beat_strengths,
        structural_steps=structure.anchor_steps,
        allowed_pcs_by_step=allowed_pcs_by_step if allowed_pcs_by_step else None,
        max_candidates=max(p.max_candidates for p in profiles),
        user_locked=locked_voicings,
    )
    return repaired


def solve_harmony_infill(
    chords: Sequence[str],
    melody: Sequence[int],
    base_solution: Sequence[ChordNode],
    user_locks: Dict[int, Tuple[int, int, int, int]],
    radius: int = 8,
    max_candidates: Optional[int] = 180,
    difficulty: str = "intermediate",
) -> List[ChordNode]:
    """
    Tactile-sandbox repair phase:
    - user_locks are exact SATB nodes set by drag edits
    - only a local window around edits is re-solved (infilling)
    """
    if len(chords) != len(melody):
        raise ValueError("Chord and melody lengths must match.")
    if not chords:
        return []
    if not base_solution:
        return solve_harmony(
            chords,
            melody,
            locked_voicings=user_locks,
            max_candidates=max_candidates,
            difficulty=difficulty,
        )

    n = len(chords)
    anchors = {i: base_solution[i].voices for i in range(n)}
    anchors.update(user_locks)

    edited_steps = sorted(user_locks.keys())
    if not edited_steps:
        return list(base_solution)
    start = max(0, min(edited_steps) - radius)
    end = min(n - 1, max(edited_steps) + radius)

    local_locked: Dict[int, Tuple[int, int, int, int]] = {}
    # lock outside window to preserve existing harmonization
    for t in range(0, start):
        local_locked[t] = anchors[t]
    for t in range(end + 1, n):
        local_locked[t] = anchors[t]
    # lock user edits inside window
    for t, v in user_locks.items():
        local_locked[t] = v

    return solve_harmony(
        chords,
        melody,
        locked_voicings=local_locked,
        max_candidates=max_candidates,
        difficulty=difficulty,
    )


def validate_solution(solution: Sequence[ChordNode], tonic_pc: int = 0) -> List[dict]:
    """
    Explainability hook focused on practical chordal stability/intonation checks.
    """
    violations: List[dict] = []
    if not solution:
        return violations

    for t, node in enumerate(solution):
        b, te, a, s = node.voices
        if not (b < te < a < s):
            violations.append(
                {"time_step": t, "code": "VOICE_ORDER", "voices": None, "severity": "hard"}
            )
        if s - a > 12 or a - te > 19 or te - b > 19:
            violations.append(
                {"time_step": t, "code": "SPACING", "voices": None, "severity": "hard"}
            )
        if t > 0:
            prev = solution[t - 1].voices
            for i in range(4):
                if abs(node.voices[i] - prev[i]) > 14:
                    violations.append(
                        {
                            "time_step": t,
                            "code": "LARGE_LEAP",
                            "voices": i,
                            "severity": "soft",
                        }
                    )

    for t in range(1, len(solution)):
        a = solution[t - 1].voices
        b = solution[t].voices

        for i in range(3):
            for j in range(i + 1, 4):
                if _is_parallel_perfect(a[i], a[j], b[i], b[j]):
                    violations.append(
                        {"time_step": t, "code": "PARALLEL_PERFECT", "voices": (i, j), "severity": "soft"}
                    )

        for i in range(4):
            leading_pc = (tonic_pc - 1) % 12
            if a[i] % 12 == leading_pc and b[i] % 12 != tonic_pc:
                violations.append(
                    {"time_step": t, "code": "LEADING_TONE_UNRESOLVED", "voices": i, "severity": "soft"}
                )

        if solution[t - 1].chord_symbol == solution[t].chord_symbol:
            violations.append(
                {"time_step": t, "code": "REPEATED_FUNCTION", "voices": None, "severity": "soft"}
            )

        # Tritone resolution (vii°7→I, vii°→I, ii°7→V)
        prev_sym = solution[t - 1].chord_symbol
        curr_sym = solution[t].chord_symbol
        if prev_sym in DIM_CHORDS and curr_sym in RESOLUTION_TARGETS:
            prev_v = solution[t - 1].voices
            curr_v = solution[t].voices
            chord_pcs = set(CHORD_DICTIONARY.get(prev_sym, []))
            voice_pairs: List[Tuple[int, int]] = []
            for i in range(3):
                for j in range(i + 1, 4):
                    if prev_v[i] % 12 in chord_pcs and prev_v[j] % 12 in chord_pcs:
                        if _is_tritone(prev_v[i] % 12, prev_v[j] % 12):
                            voice_pairs.append((i, j))
            if voice_pairs:
                result = _check_tritone_resolution(prev_v, curr_v, voice_pairs)
                if result == "improper":
                    violations.append(
                        {
                            "time_step": t,
                            "code": "TRITONE_RESOLUTION_IMPROPER",
                            "voices": voice_pairs[0],
                            "severity": "hard",
                        }
                    )
                elif result == "suboptimal":
                    violations.append(
                        {
                            "time_step": t,
                            "code": "TRITONE_RESOLUTION_SUBOPTIMAL",
                            "voices": voice_pairs[0],
                            "severity": "soft",
                        }
                    )

    return violations


def explain_rule_violation(code: str) -> str:
    """Use knowledge_base-grounded explanations when available."""
    try:
        from .knowledge_rules import explain_rule_violation as _kb_explain
        return _kb_explain(code)
    except ImportError:
        try:
            from engine.knowledge_rules import explain_rule_violation as _kb_explain
            return _kb_explain(code)
        except ImportError:
            pass
    except ImportError:
        pass
    fallbacks = {
        "VOICE_ORDER": "Voices must remain in SATB register order to keep the chord stack readable and singable.",
        "SPACING": "Voice spacing exceeds SATB chord-harmony limits, which can weaken blend and tuning clarity.",
        "LARGE_LEAP": "A large leap can sound unstable in block harmony; stepwise or small-motion voice leading is preferred.",
        "PARALLEL_PERFECT": "Parallel fifths/octaves are heavily discouraged in the classical filter and raise transition cost.",
        "LEADING_TONE_UNRESOLVED": "Leading tone should resolve upward to tonic at phrase-critical moments.",
        "REPEATED_FUNCTION": "Repeated harmonic function may reduce forward motion; keep if intentionally sustained.",
        "TRITONE_RESOLUTION_IMPROPER": "Tritones in diminished seventh chords must resolve: A4 outward to sixth, d5 inward to third. Both voices should move by step in contrary motion.",
        "TRITONE_RESOLUTION_SUBOPTIMAL": "Tritone resolution by similar motion is acceptable but contrary motion is preferred in Schenkerian voice leading.",
    }
    return fallbacks.get(code, "Rule violation detected by theory inspector.")


def enrich_violations_with_measures(
    violations: Sequence[dict],
    durations: Sequence[float],
    beats_per_measure: int,
) -> List[dict]:
    if beats_per_measure <= 0:
        beats_per_measure = 4
    cumulative = 0.0
    measure_by_step = {}
    for i, d in enumerate(durations):
        measure_by_step[i] = int(cumulative // beats_per_measure) + 1
        cumulative += d
    enriched = []
    for v in violations:
        step = int(v.get("time_step", 0))
        ev = dict(v)
        ev["measure"] = measure_by_step.get(step, 1)
        ev["explanation"] = explain_rule_violation(str(v.get("code", "")))
        enriched.append(ev)
    return enriched