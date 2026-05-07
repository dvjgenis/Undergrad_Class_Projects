"""
Load music theory rules from knowledge_base for use in harmonization.
Incorporates rules from MusicTheory (Open Music Theory) and Methodology sources
into engine behavior: explanations, penalty weights, and severity.

Rules aligned with knowledge_base:
- VOICE_ORDER: voice crossing (soprano > alto > tenor > bass)
- SPACING: octave limits between adjacent voices
- PARALLEL_PERFECT: parallel fifths/octaves
- LEADING_TONE_UNRESOLVED: leading tone resolution to tonic
- REPEATED_FUNCTION, LARGE_LEAP: engine-specific
- CADENCE_GRAVITY, DOMINANT_FUNCTION: harmonic progression (io_handler, hierarchical_bridge)
"""

import csv
import re
from pathlib import Path
from typing import Optional

# Align with TheoryInspector ingest RULE_PATTERNS and ERROR_CODE_HINTS
RULE_PATTERNS = {
    "PARALLEL_PERFECT": [
        r"parallel\s+fifth",
        r"parallel\s+octave",
        r"parallel\s+perfect",
    ],
    "LEADING_TONE_UNRESOLVED": [
        r"leading\s+tone",
        r"tendency\s+tone",
    ],
    "VOICE_ORDER": [
        r"voice\s+crossing",
        r"crossing\s+voices",
    ],
    "SPACING": [
        r"spacing",
        r"close\s+position",
        r"open\s+position",
    ],
    "CADENCE_GRAVITY": [
        r"cadence",
        r"authentic\s+cadence",
        r"half\s+cadence",
    ],
    "DOMINANT_FUNCTION": [
        r"dominant",
        r"predominant",
        r"tonic",
        r"roman\s+numeral",
    ],
    "TRITONE_RESOLUTION_IMPROPER": [
        r"tritone\s+resolution",
        r"diminished\s+seventh",
        r"augmented\s+fourth",
        r"diminished\s+fifth",
    ],
    "TRITONE_RESOLUTION_SUBOPTIMAL": [
        r"tritone\s+resolution",
        r"contrary\s+motion",
    ],
}

ERROR_CODE_HINTS = {
    "parallel": "PARALLEL_PERFECT",
    "fifth": "PARALLEL_PERFECT",
    "octave": "PARALLEL_PERFECT",
    "leading tone": "LEADING_TONE_UNRESOLVED",
    "voice crossing": "VOICE_ORDER",
    "spacing": "SPACING",
    "cadence": "CADENCE_GRAVITY",
    "dominant": "DOMINANT_FUNCTION",
    "tritone": "TRITONE_RESOLUTION_IMPROPER",
    "tritone resolution": "TRITONE_RESOLUTION_IMPROPER",
}

# Engine-specific codes (validation + cost)
ENGINE_CODES = {
    "VOICE_ORDER",
    "SPACING",
    "PARALLEL_PERFECT",
    "LEADING_TONE_UNRESOLVED",
    "REPEATED_FUNCTION",
    "LARGE_LEAP",
    "TRITONE_RESOLUTION_IMPROPER",
    "TRITONE_RESOLUTION_SUBOPTIMAL",
}

# Fallback explanations (used when knowledge_base has no match)
FALLBACK_EXPLANATIONS = {
    "VOICE_ORDER": "Voices must remain in SATB register order to keep the chord stack readable and singable.",
    "SPACING": "Voice spacing exceeds SATB chord-harmony limits, which can weaken blend and tuning clarity.",
    "LARGE_LEAP": "A large leap can sound unstable in block harmony; stepwise or small-motion voice leading is preferred.",
    "PARALLEL_PERFECT": "Parallel fifths/octaves are heavily discouraged in the classical filter and raise transition cost.",
    "LEADING_TONE_UNRESOLVED": "Leading tone should resolve upward to tonic at phrase-critical moments.",
    "REPEATED_FUNCTION": "Repeated harmonic function may reduce forward motion; keep if intentionally sustained.",
    "CADENCE_GRAVITY": "Cadences provide structural closure; phrase endings typically resolve to tonic.",
    "DOMINANT_FUNCTION": "Dominant-tonic relationships are central to tonal harmony.",
    "TRITONE_RESOLUTION_IMPROPER": "Tritones in diminished seventh chords must resolve: A4 outward to sixth, d5 inward to third. Both voices should move by step in contrary motion.",
    "TRITONE_RESOLUTION_SUBOPTIMAL": "Tritone resolution by similar motion is acceptable but contrary motion is preferred in Schenkerian voice leading.",
}

# Severity -> penalty weight multiplier for cost calculation
CRITICAL_PENALTY = 12.0
STYLISTIC_PENALTY = 5.0


def _error_code_for_chunk(chunk: str) -> str:
    c = chunk.lower()
    for code, patterns in RULE_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, c):
                return code
    for key, code in ERROR_CODE_HINTS.items():
        if key in c:
            return code
    return "GENERAL_THEORY"


def _severity_for_code(code: str) -> str:
    if code in {"PARALLEL_PERFECT", "VOICE_ORDER", "SPACING", "TRITONE_RESOLUTION_IMPROPER"}:
        return "Critical"
    if code in {"LEADING_TONE_UNRESOLVED", "CADENCE_GRAVITY", "DOMINANT_FUNCTION", "TRITONE_RESOLUTION_SUBOPTIMAL"}:
        return "Stylistic"
    return "Stylistic"


def _sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.strip())
    parts = re.split(r"(?<=[\.\!\?])\s+", normalized)
    return [p.strip() for p in parts if len(p.strip()) > 25]


def _semantic_rule_chunks(text: str) -> list[str]:
    sents = _sentences(text)
    chunks = []
    for i, s in enumerate(sents):
        s_l = s.lower()
        matched = False
        for pats in RULE_PATTERNS.values():
            if any(re.search(p, s_l) for p in pats):
                matched = True
                break
        if matched:
            left = sents[i - 1] if i - 1 >= 0 else ""
            right = sents[i + 1] if i + 1 < len(sents) else ""
            block = " ".join(x for x in [left, s, right] if x).strip()
            if block:
                chunks.append(block)
    if not chunks:
        paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        chunks = paras[:8]
    seen = set()
    deduped = []
    for c in chunks:
        key = c[:200]
        if key in seen:
            continue
        seen.add(key)
        deduped.append(c)
    return deduped


def _load_from_chunks_csv(project_root: Path) -> dict[str, list[dict]]:
    """Load rules from TheoryInspector chunks CSV if it exists."""
    csv_path = project_root / "TheoryInspector" / "index" / "theory_chunks.csv"
    if not csv_path.exists():
        return {}
    by_code: dict[str, list[dict]] = {}
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get("error_code", "GENERAL_THEORY")
            by_code.setdefault(code, []).append({
                "text": row.get("text", ""),
                "severity": row.get("severity", "Stylistic"),
                "source_file": row.get("source_file", ""),
            })
    return by_code


def _load_from_knowledge_base(project_root: Path) -> dict[str, list[dict]]:
    """Parse knowledge_base/*.txt directly when chunks CSV is unavailable."""
    kb_dir = project_root / "knowledge_base"
    if not kb_dir.exists():
        return {}
    by_code: dict[str, list[dict]] = {}
    for fp in sorted(kb_dir.rglob("*.txt")):
        try:
            text = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for chunk in _semantic_rule_chunks(text):
            code = _error_code_for_chunk(chunk)
            severity = _severity_for_code(code)
            by_code.setdefault(code, []).append({
                "text": chunk[:500],
                "severity": severity,
                "source_file": str(fp.relative_to(project_root)),
            })
    return by_code


def _get_project_root() -> Path:
    """Resolve project root (parent of engine/)."""
    return Path(__file__).resolve().parent.parent


_rules_cache: Optional[dict[str, list[dict]]] = None


def _get_rules() -> dict[str, list[dict]]:
    global _rules_cache
    if _rules_cache is not None:
        return _rules_cache
    root = _get_project_root()
    _rules_cache = _load_from_chunks_csv(root)
    if not _rules_cache:
        _rules_cache = _load_from_knowledge_base(root)
    return _rules_cache


def explain_rule_violation(code: str) -> str:
    """
    Return a theory-grounded explanation for a violation code.
    Uses knowledge_base content when available; falls back to built-in text.
    """
    rules = _get_rules()
    chunks = rules.get(code, [])
    if chunks:
        # Prefer Open Music Theory (pedagogical) or first available
        for c in chunks:
            src = c.get("source_file", "")
            if "open-music-theory" in src.lower() or "musictheory" in src.lower():
                text = (c.get("text") or "").strip()
                if len(text) > 30:
                    return text[:400] + ("..." if len(text) > 400 else "")
        text = (chunks[0].get("text") or "").strip()
        if len(text) > 30:
            return text[:400] + ("..." if len(text) > 400 else "")
    return FALLBACK_EXPLANATIONS.get(code, "Rule violation detected by theory inspector.")


def get_rule_severity(code: str) -> str:
    """Return Critical or Stylistic based on knowledge_base and engine defaults."""
    rules = _get_rules()
    chunks = rules.get(code, [])
    if chunks:
        sev = chunks[0].get("severity", "Stylistic")
        if sev in ("Critical", "Stylistic"):
            return sev
    return _severity_for_code(code)


def get_penalty_weight(code: str) -> float:
    """
    Return penalty weight for use in transition cost.
    Critical rules (VOICE_ORDER, SPACING, PARALLEL_PERFECT) get higher weight.
    """
    sev = get_rule_severity(code)
    return CRITICAL_PENALTY if sev == "Critical" else STYLISTIC_PENALTY


# Index building is the backend's responsibility (backend/main.py). Engine never
# imports TheoryInspector. When CSV is missing, _get_rules() falls back to
# _load_from_knowledge_base() which parses knowledge_base/*.txt directly.
