"""
Phase 4 export: MusicXML string to XML or PDF.
"""

import io
import tempfile
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import music21 as m21


def export_to_xml(musicxml: str) -> str:
    """Return MusicXML as-is (already valid XML)."""
    return musicxml


def export_to_pdf(musicxml: str) -> bytes:
    """
    Export score to PDF via music21 + MuseScore/lilypond if available.
    """
    import os

    score = m21.converter.parse(musicxml)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = tmp.name
    try:
        score.write("pdf", fp=pdf_path)
        with open(pdf_path, "rb") as f:
            return f.read()
    except Exception as e:
        raise ValueError(
            f"PDF export failed: {e}. "
            "Install MuseScore and add it to PATH, or use format=xml."
        ) from e
    finally:
        if Path(pdf_path).exists():
            os.unlink(pdf_path)
