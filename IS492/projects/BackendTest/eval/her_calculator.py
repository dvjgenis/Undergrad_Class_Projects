#!/usr/bin/env python3
"""
Harmonic Error Rate (HER) Calculator for HarmonyForge.

Uses music21 to benchmark SATB output against PRD targets:
- 0% parallel fifths
- 0% voice-crossing

Usage:
    make calc-her
    # or: python eval/her_calculator.py path/to/score.xml
"""

import sys
from pathlib import Path

# Add project root for imports
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


def calc_her(musicxml_path: str | Path) -> dict:
    """
    Compute Harmonic Error Rate for a MusicXML SATB score.

    Returns dict with:
        - parallel_fifths: count
        - voice_crossing: count
        - total_errors: sum
        - her_percent: 0.0 if no errors (target)
    """
    try:
        import music21
    except ImportError:
        return {
            "error": "music21 not installed. Run: pip install music21",
            "parallel_fifths": None,
            "voice_crossing": None,
            "her_percent": None,
        }

    path = Path(musicxml_path)
    if not path.exists():
        return {"error": f"File not found: {path}", "her_percent": None}

    score = music21.converter.parse(str(path))
    parallel_fifths = 0
    voice_crossing = 0

    # Simplified checks: iterate parts, compare consecutive chords
    parts = [p for p in score.parts if p.flatten().notes]
    if len(parts) < 2:
        return {
            "parallel_fifths": 0,
            "voice_crossing": 0,
            "total_errors": 0,
            "her_percent": 0.0,
            "note": "Fewer than 2 parts; skipping interval checks",
        }

    # Count parallel fifths between adjacent pairs of voices
    # (Full implementation would use music21.interval analysis)
    for i, p1 in enumerate(parts):
        for p2 in parts[i + 1 :]:
            notes1 = list(p1.flatten().notes)
            notes2 = list(p2.flatten().notes)
            n = min(len(notes1), len(notes2))
            for j in range(n - 1):
                int1 = music21.interval.Interval(notes1[j], notes1[j + 1])
                int2 = music21.interval.Interval(notes2[j], notes2[j + 1])
                if int1.name in ("P5", "P-5") and int2.name in ("P5", "P-5"):
                    parallel_fifths += 1
                # Voice crossing: lower part above higher part
                if notes1[j].pitch.midi < notes2[j].pitch.midi and notes1[j + 1].pitch.midi > notes2[j + 1].pitch.midi:
                    voice_crossing += 1
                elif notes1[j].pitch.midi > notes2[j].pitch.midi and notes1[j + 1].pitch.midi < notes2[j + 1].pitch.midi:
                    voice_crossing += 1

    total = parallel_fifths + voice_crossing
    total_chords = sum(len(list(p.flatten().notes)) - 1 for p in parts) // max(len(parts), 1) if parts else 0
    her_percent = (total / total_chords * 100) if total_chords else 0.0

    return {
        "parallel_fifths": parallel_fifths,
        "voice_crossing": voice_crossing,
        "total_errors": total,
        "her_percent": round(her_percent, 2),
        "target_met": total == 0,
    }


def main():
    path = None
    if len(sys.argv) >= 2:
        path = sys.argv[1]
    else:
        # Default: use first XML in output/ or input/
        for d in ("output", "input"):
            folder = _root / d
            if folder.exists():
                xmls = list(folder.glob("*.xml"))
                if xmls:
                    path = str(xmls[0])
                    break
    if not path:
        print("Usage: python eval/her_calculator.py <path/to/score.xml>")
        print("   or: make calc-her (uses output/*.xml or input/*.xml)")
        sys.exit(1)

    result = calc_her(path)
    if "error" in result:
        print(result["error"])
        sys.exit(1)

    print(f"HER for {path}")
    print(f"  Parallel fifths: {result['parallel_fifths']}")
    print(f"  Voice crossing:  {result['voice_crossing']}")
    print(f"  Total errors:   {result['total_errors']}")
    print(f"  HER %:          {result['her_percent']}")
    print(f"  Target met:     {result['target_met']}")
    sys.exit(0 if result["target_met"] else 1)


if __name__ == "__main__":
    main()
