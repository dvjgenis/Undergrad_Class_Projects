"""
Convert PDF and MIDI to MusicXML for HarmonyForge upload.

- MIDI: music21 (built-in)
- PDF: Audiveris CLI (if installed) or MuseScore CLI (if supports PDF)
"""

import io
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import music21 as m21


def convert_midi_to_musicxml(content: bytes) -> str:
    """
    Convert MIDI bytes to MusicXML string using music21.
    """
    with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tmp:
        tmp.write(content)
        midi_path = tmp.name
    xml_path = midi_path + ".xml"
    try:
        score = m21.converter.parse(midi_path, format="midi")
        score.write("musicxml", fp=xml_path)
        with open(xml_path, encoding="utf-8") as f:
            return f.read()
    finally:
        if os.path.exists(midi_path):
            os.unlink(midi_path)
        if os.path.exists(xml_path):
            os.unlink(xml_path)


def convert_pdf_to_musicxml(content: bytes) -> str:
    """
    Convert PDF bytes to MusicXML using Audiveris or MuseScore CLI.
    Raises ValueError if no converter is available.
    """
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_in:
        tmp_in.write(content)
        pdf_path = tmp_in.name

    try:
        out_dir = tempfile.mkdtemp()
        try:
            # Try Audiveris first (OMR): PATH, then macOS app bundle
            audiveris = shutil.which("audiveris") or shutil.which("Audiveris")
            if not audiveris and os.path.exists("/Applications/Audiveris.app"):
                macos_exe = "/Applications/Audiveris.app/Contents/MacOS/Audiveris"
                if os.path.isfile(macos_exe):
                    audiveris = macos_exe
            if audiveris:
                result = subprocess.run(
                    [
                        audiveris,
                        "-batch",
                        "-export",
                        "-output", out_dir,
                        "-option", "org.audiveris.omr.sheet.BookManager.useSeparateBookFolders=false",
                        pdf_path,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                if result.returncode != 0:
                    raise ValueError(
                        f"Audiveris failed: {result.stderr or result.stdout or 'unknown error'}"
                    )
                # Find generated MusicXML
                xml_files = list(Path(out_dir).rglob("*.xml"))
                if not xml_files:
                    raise ValueError("Audiveris did not produce any MusicXML output")
                return xml_files[0].read_text(encoding="utf-8", errors="replace")

            # Try MuseScore (MuseScore 4+ may support PDF in some configs)
            for cmd in ("mscore", "MuseScore4", "mscore4", "musescore"):
                mscore = shutil.which(cmd)
                if mscore:
                    xml_path = Path(out_dir) / "output.xml"
                    result = subprocess.run(
                        [mscore, "--export-to", str(xml_path), pdf_path],
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )
                    if result.returncode == 0 and xml_path.exists():
                        return xml_path.read_text(encoding="utf-8", errors="replace")
        finally:
            shutil.rmtree(out_dir, ignore_errors=True)

        raise ValueError(
            "PDF conversion requires Audiveris. Install from https://github.com/Audiveris/audiveris "
            "and add it to PATH. Alternatively, convert PDF to MusicXML using an online tool first."
        )
    finally:
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)


def convert_to_musicxml(content: bytes, format_hint: str) -> str:
    """
    Convert content to MusicXML. format_hint: "midi", "pdf", or "xml".
    """
    fmt = (format_hint or "").strip().lower()
    if fmt in ("midi", "mid"):
        return convert_midi_to_musicxml(content)
    if fmt == "pdf":
        return convert_pdf_to_musicxml(content)
    if fmt in ("xml", "musicxml"):
        return content.decode("utf-8", errors="replace")
    raise ValueError(f"Unsupported format: {format_hint}. Use midi, pdf, or xml.")
