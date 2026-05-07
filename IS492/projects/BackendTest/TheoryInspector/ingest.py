import csv
import re
from pathlib import Path

from .config import TheoryInspectorConfig


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


def _domain_for_source(path: Path) -> str:
    p = str(path).lower()
    if "musictheory/open-music-theory" in p:
        return "tutor"
    if "methodology/" in p:
        return "auditor"
    return "auditor"


def _historical_context(path: Path) -> str:
    p = str(path).lower()
    if "open-music-theory" in p:
        return "Pedagogical survey of Common Practice and broader tonal repertoire"
    if "schenker" in p:
        return "Schenkerian tonal hierarchy and common-practice structure"
    if "trends" in p or "composerx" in p or "musicair" in p:
        return "Modern algorithmic composition systems and interactive AI workflows"
    return "Common Practice Period and tonal theory"


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
    if code in {"PARALLEL_PERFECT", "VOICE_ORDER", "SPACING"}:
        return "Critical"
    if code in {"LEADING_TONE_UNRESOLVED", "CADENCE_GRAVITY", "DOMINANT_FUNCTION"}:
        return "Stylistic"
    return "Stylistic"


def _rule_id(source_file: str, code: str, idx: int) -> str:
    base = Path(source_file).stem.lower().replace(" ", "_")
    return f"{base}:{code}:{idx}"


def _sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.strip())
    parts = re.split(r"(?<=[\.\!\?])\s+", normalized)
    return [p.strip() for p in parts if len(p.strip()) > 25]


def _semantic_rule_chunks(text: str) -> list[str]:
    """
    Rule-per-chunk strategy:
    - Detect sentences that explicitly mention a theory rule.
    - Include local context (previous + next sentence).
    """
    sents = _sentences(text)
    chunks: list[str] = []
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
    # Fallback when no explicit rule sentence is found.
    if not chunks:
        paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        chunks = paras[:8]
    # De-duplicate while preserving order.
    seen = set()
    deduped = []
    for c in chunks:
        key = c[:200]
        if key in seen:
            continue
        seen.add(key)
        deduped.append(c)
    return deduped


def build_chunks_index(config: TheoryInspectorConfig) -> Path:
    config.index_dir.mkdir(parents=True, exist_ok=True)
    txt_files = sorted(config.knowledge_base_dir.rglob("*.txt"))
    rows = []
    chunk_id = 0
    for fp in txt_files:
        text = fp.read_text(encoding="utf-8", errors="ignore")
        domain = _domain_for_source(fp)
        source_file = str(fp.relative_to(config.project_root))
        historical = _historical_context(fp)
        semantic_chunks = _semantic_rule_chunks(text)
        for local_idx, chunk in enumerate(semantic_chunks, start=1):
            chunk_id += 1
            error_code = _error_code_for_chunk(chunk)
            rule_id = _rule_id(source_file, error_code, local_idx)
            severity = _severity_for_code(error_code)
            rows.append(
                {
                    "chunk_id": str(chunk_id),
                    "rule_id": rule_id,
                    "domain": domain,
                    "source_file": source_file,
                    "error_code": error_code,
                    "historical_context": historical,
                    "severity": severity,
                    "difficulty": "beginner" if domain == "tutor" else "intermediate",
                    "text": chunk,
                }
            )

    with config.chunks_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "chunk_id",
                "rule_id",
                "domain",
                "source_file",
                "error_code",
                "historical_context",
                "severity",
                "difficulty",
                "text",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    return config.chunks_csv

