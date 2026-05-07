Harmonizer (PDF -> MusicXML -> Harmony -> PDF)

Overview

This repository contains a script that converts sheet-music PDFs into a harmonized PDF (harmony line only).

What it does

- Looks in the `input/` directory for PDF files.
- Converts each PDF to MusicXML (tries MuseScore CLI first; falls back to Audiveris if available).
- Uses `music21` to analyze the key and create a diatonic third harmony:
  - If the detected key is major, the harmony is a major third below the melody.
  - If the detected key is minor, the harmony is a minor third below the melody.
- Writes a harmony-only MusicXML and renders it to PDF (via MuseScore CLI).
- Outputs PDFs to the `output/` directory.

Requirements

- Python 3.8+
- music21 (`pip install -r requirements.txt`)
- MuseScore (recommended) installed and on PATH for PDF<->MusicXML conversion and rendering
  - MuseScore CLI commonly available as `mscore`, `musescore`, `MuseScore`, etc.
- Optional: Audiveris (for OCR conversion of complex PDFs). Install separately if you want to use it.

Usage

1. Place your sheet-music PDF(s) into the `input/` folder (create if missing).
2. Run the script:

```bash
python scripts/harmonizer.py
```

3. Look in the `output/` folder for `<originalname>_harmony.pdf` files.

Notes and limitations

- OCR accuracy depends on the quality of the PDF and the OCR tool (MuseScore's PDF import or Audiveris).
- MuseScore must be installed to reliably render MusicXML to PDF. If MuseScore isn't found the script will instruct you to install it.
- This is a rule-based approach (diatonic thirds). It does not perform advanced harmonic analysis or voice-leading beyond simple proximity.

If you'd like, I can:
- Add unit tests and a small sample PDF (if you can provide one), or
- Make the script watch the input folder and auto-process new files.
