"""
MVP Music Harmonizer Backend
Implements rule-based diatonic third harmonization using music21
"""

from music21 import converter, stream, note, chord, key, interval, pitch, roman
from typing import List, Tuple, Optional
import random
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def parse_melody(musicxml_file_path: str) -> Tuple[stream.Stream, stream.Part, List[Tuple[Optional[int], float, float]], key.Key]:
    """
    Function A: Input Handling & Parsing
    
    Args:
        musicxml_file_path: Path to the MusicXML file
        
    Returns:
        Tuple containing:
        - original_stream: The parsed music21 Stream
        - melody_data_list: List of (midi_pitch, duration) tuples (None for rests)
        - key_signature: The global key signature
    """
    # Load the MusicXML file
    original_stream = converter.parse(musicxml_file_path)
    
    # Extract the first part (primary melody line)
    parts = original_stream.parts
    if not parts:
        raise ValueError("No parts found in the MusicXML file")
    
    melody_part = parts[0]
    
    # Extract melody data while preserving offsets: list of (midi_pitch, duration, offset) tuples
    melody_data_list = []
    for element in melody_part.flatten().notesAndRests:
        if isinstance(element, note.Note):
            melody_data_list.append((element.pitch.midi, element.quarterLength, float(element.offset)))
        elif isinstance(element, note.Rest):
            melody_data_list.append((None, element.quarterLength, float(element.offset)))
        elif isinstance(element, chord.Chord):
            # For chords, take the highest note as the melody
            highest_pitch = max(element.pitches, key=lambda p: p.midi)
            melody_data_list.append((highest_pitch.midi, element.quarterLength, float(element.offset)))
    
    # Identify the global key signature
    key_signature = melody_part.analyze('key')

    return (original_stream, melody_part, melody_data_list, key_signature)


def generate_harmony_part(
    melody_data: List[Tuple[Optional[int], float, float]],
    key_signature: key.Key,
    melody_part: stream.Part,
    chordified: Optional[stream.Stream] = None,
    instrument_range: Tuple[int, int] = (36, 60),
    stochastic_temp: float = 0.0,
    random_seed: Optional[int] = None
) -> stream.Part:
    """
    Function B: Harmonization Logic
    
    Implements diatonic third harmonization with voice leading constraints.
    
    Args:
        melody_data: List of (midi_pitch, duration) tuples from parse_melody
        key_signature: The key signature for diatonic context
        instrument_range: Tuple of (min_midi, max_midi) for the harmony part
        
    Returns:
        A music21.Part containing the harmony line
    """
    harmony_part = stream.Part()
    harmony_part.id = "Harmony"
    
    # Get the scale pitches for the key
    scale = key_signature.getScale()
    scale_pitches = [p.midi % 12 for p in scale.pitches]  # Pitch classes

    previous_harmony_midi = None
    previous_melody_midi = None

    if random_seed is not None:
        random.seed(random_seed)

    # prepare chord map if chordified provided (list of (chord_obj, offset, dur))
    chord_map = []
    if chordified is None:
        try:
            chordified = melody_part.getContextByClass(stream.Score) if False else None
        except Exception:
            chordified = None
    if chordified is not None:
        chord_list = list(chordified.recurse().getElementsByClass(chord.Chord))
        for c in chord_list:
            chord_map.append((c, float(c.offset), float(c.quarterLength)))

    def find_chord_at_offset(offset: float) -> Optional[chord.Chord]:
        if not chord_map:
            return None
        for c, o, d in chord_map:
            if o <= offset < (o + d):
                return c
        # fallback: nearest chord
        nearest = min(chord_map, key=lambda t: abs(t[1] - offset))
        return nearest[0]

    # Helper: check if pitch class is diatonic
    def is_diatonic(midi_val: int) -> bool:
        return (midi_val % 12) in scale_pitches

    for melody_midi, duration, offset in melody_data:
        # Handle rests
        if melody_midi is None:
            harmony_part.insert(offset, note.Rest(quarterLength=duration))
            continue

        candidates = []  # list of tuples (midi, diatonic_flag, accidental_penalty)

        # Consider both minor and major thirds below as primary options
        for semitones in (3, 4):
            base_candidate = melody_midi - semitones
            # try octave equivalents
            for octave_shift in range(-2, 3):
                cand = base_candidate + (octave_shift * 12)
                if not (instrument_range[0] <= cand <= instrument_range[1]):
                    continue
                # exact diatonic
                if is_diatonic(cand):
                    candidates.append((cand, True, 0))
                else:
                    # allow small accidental adjustment (±1 semitone) to reach diatonic pitch
                    for adj in (-1, 1):
                        adj_cand = cand + adj
                        if instrument_range[0] <= adj_cand <= instrument_range[1] and is_diatonic(adj_cand):
                            # accidental_penalty = 1 for small chromatic alteration
                            candidates.append((adj_cand, True, 1))
                    # also keep the non-diatonic candidate as last resort with penalty
                    candidates.append((cand, False, 2))

        # If no candidates found below, try thirds above (mirroring) as backup
        if not candidates:
            for semitones in (3, 4):
                base_candidate = melody_midi + semitones
                for octave_shift in range(-2, 3):
                    cand = base_candidate + (octave_shift * 12)
                    if not (instrument_range[0] <= cand <= instrument_range[1]):
                        continue
                    if is_diatonic(cand):
                        candidates.append((cand, True, 0))
                    else:
                        for adj in (-1, 1):
                            adj_cand = cand + adj
                            if instrument_range[0] <= adj_cand <= instrument_range[1] and is_diatonic(adj_cand):
                                candidates.append((adj_cand, True, 1))
                        candidates.append((cand, False, 2))

        # If still no candidates, add a rest
        if not candidates:
            harmony_part.insert(offset, note.Rest(quarterLength=duration))
            continue

        # Score candidates: combine accidental penalty, voice-leading, chord-fit, and parallel-interval penalties
        chord_at_offset = find_chord_at_offset(offset)

        def score_candidate(cand_tuple):
            midi_val, diatonic_flag, acc_pen = cand_tuple
            # base score from accidental penalty (0 best)
            score = acc_pen * 100

            # chord fit: if candidate is a member of the underlying chord, boost it
            if chord_at_offset is not None:
                try:
                    chord_pcs = chord_at_offset.pitchClasses
                    if (midi_val % 12) in chord_pcs:
                        score -= 200
                except Exception:
                    pass

            # voice-leading distance penalty
            if previous_harmony_midi is None:
                # prefer middle of range for first note
                middle = (instrument_range[0] + instrument_range[1]) / 2
                score += abs(midi_val - middle)
            else:
                dist = abs(midi_val - previous_harmony_midi)
                score += dist
                if dist > 12:
                    score += 50

            # parallel fifth/octave penalty: detect if previous interval was perfect 5th/oct and current would also be
            if previous_harmony_midi is not None and previous_melody_midi is not None:
                prev_interval = abs(previous_harmony_midi - previous_melody_midi)
                curr_interval = abs(midi_val - melody_midi)
                # 7 semitones = perfect 5th, 12 = octave
                if prev_interval in (7, 12) and curr_interval in (7, 12):
                    # movement direction
                    melody_move = melody_midi - previous_melody_midi
                    harmony_move = midi_val - previous_harmony_midi
                    if melody_move * harmony_move > 0:
                        # parallel perfect 5th or octave -> heavy penalty
                        score += 1000

            # small stochastic perturbation to escape local minima (if requested)
            if stochastic_temp and stochastic_temp > 0:
                score += random.uniform(-stochastic_temp, stochastic_temp)

            return score

        chosen = min(candidates, key=score_candidate)
        chosen_harmony = chosen[0]

        # Create the harmony note and insert it at the same offset as the melody
        harmony_note = note.Note(midi=chosen_harmony, quarterLength=duration)
        harmony_part.insert(offset, harmony_note)

        # update previous trackers
        previous_harmony_midi = chosen_harmony
        previous_melody_midi = melody_midi
    
    return harmony_part


def harmonize_melody(
    input_musicxml_path: str,
    output_musicxml_path: str,
    instrument_range: Tuple[int, int] = (36, 60)
) -> None:
    """
    Main Orchestrating Function
    
    Coordinates the entire harmonization process from input to output.
    
    Args:
        input_musicxml_path: Path to input MusicXML file
        output_musicxml_path: Path for output MusicXML file
        instrument_range: MIDI range for harmony part (default: bass range)
    """
    print(f"🎵 Starting harmonization process...")
    print(f"📂 Input file: {input_musicxml_path}")
    
    # Step 1: Parse the input melody
    print("📖 Parsing melody...")
    original_stream, melody_part, melody_data, key_signature = parse_melody(input_musicxml_path)
    print(f"🎼 Key signature detected: {key_signature}")
    print(f"🎶 Melody notes extracted: {len(melody_data)} notes/rests")
    
    # Step 2: Generate harmony part
    print("🎹 Generating harmony part...")
    # Create a chordified version of the score to get underlying chord context
    try:
        chordified = original_stream.chordify()
    except Exception:
        chordified = None

    harmony_part = generate_harmony_part(
        melody_data,
        key_signature,
        melody_part,
        chordified=chordified,
        instrument_range=instrument_range,
        stochastic_temp=0.0,
        random_seed=42,
    )
    print(f"✨ Harmony part created with {len(harmony_part.flatten().notesAndRests)} elements")
    
    # Step 3: Create a score that contains ONLY the harmony part
    print("🎼 Creating harmony-only score...")
    output_score = stream.Score()
    harmony_part.id = "Harmony"
    # Copy key signature, time signature, clef, and tempo from the original melody part
    melody_part = original_stream.parts[0]
    # Key/Time/Clef/Metronome: insert at offset 0 in harmony part
    # Copy explicit KeySignature if present, else insert analyzed key
    try:
        # prefer an actual KeySignature object from the part
        ks = None
        ks_list = [e for e in melody_part.recurse() if e.__class__.__name__ == 'KeySignature']
        if ks_list:
            ks = ks_list[0]
            harmony_part.insert(0, ks)
        else:
            harmony_part.insert(0, key_signature)
    except Exception:
        # fallback
        harmony_part.insert(0, key_signature)

    # TimeSignature
    try:
        ts_list = melody_part.recurse().getElementsByClass('TimeSignature')
        if ts_list:
            harmony_part.insert(0, ts_list[0])
    except Exception:
        pass

    # Clef
    try:
        clefs = melody_part.recurse().getElementsByClass('Clef')
        if clefs:
            harmony_part.insert(0, clefs[0])
    except Exception:
        pass

    # Tempo / Metronome
    try:
        mm = melody_part.recurse().getElementsByClass('MetronomeMark')
        if mm:
            harmony_part.insert(0, mm[0])
    except Exception:
        pass

    output_score.append(harmony_part)

    # Step 4: Write harmony-only MusicXML
    print(f"💾 Writing harmony MusicXML to: {output_musicxml_path}")
    output_score.write('musicxml', fp=output_musicxml_path)
    print("✅ Harmony MusicXML written!")


# Example usage
if __name__ == "__main__":
    # New CLI: process all PDFs in `input/` and write harmony-only PDFs to `output/`
    BASE_DIR = Path(__file__).resolve().parents[1]
    INPUT_DIR = BASE_DIR / 'input'
    OUTPUT_DIR = BASE_DIR / 'output'
    TMP_DIR = Path(tempfile.mkdtemp(prefix='harmonizer_'))

    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    def find_musescore_executable() -> Optional[str]:
        # Common names for MuseScore CLI on different installs
        candidates = ['mscore', 'musescore', 'MuseScore', 'MuseScore3', 'MuseScore4', 'mscore3', 'mscore4']
        for name in candidates:
            path = shutil.which(name)
            if path:
                return path
        return None

    def convert_pdf_to_musicxml(pdf_path: Path, out_musicxml: Path) -> bool:
        """Try converting PDF to MusicXML using MuseScore or Audiveris (if available).
        Returns True on success.
        """
        # Try MuseScore first (it can open PDF and export MusicXML if the plugin is installed)
        ms_path = find_musescore_executable()
        if ms_path:
            try:
                # MuseScore CLI: input -> -o output
                subprocess.run([ms_path, str(pdf_path), '-o', str(out_musicxml)], check=True)
                return True
            except subprocess.CalledProcessError:
                print(f"⚠️  MuseScore failed to convert {pdf_path}")

        # Try Audiveris if MuseScore not available or failed
        audiveris = shutil.which('audiveris')
        if audiveris:
            try:
                # Audiveris usage (batch): audiveris -batch -export -output outdir file.pdf
                outdir = out_musicxml.parent
                subprocess.run([audiveris, '-batch', '-export', '-output', str(outdir), str(pdf_path)], check=True)
                # Audiveris may write a .xml or .musicxml file with same basename
                generated = list(outdir.glob(pdf_path.stem + '*.xml'))
                if generated:
                    # Move/rename first found to desired path
                    shutil.move(str(generated[0]), str(out_musicxml))
                    return True
            except subprocess.CalledProcessError:
                print(f"⚠️  Audiveris failed to convert {pdf_path}")

        print("❌ No PDF->MusicXML converter succeeded. Install MuseScore or Audiveris and try again.")
        return False

    def render_musicxml_to_pdf(musicxml_path: Path, output_pdf: Path) -> bool:
        ms_path = find_musescore_executable()
        if not ms_path:
            print("⚠️  MuseScore not found; cannot render MusicXML to PDF. Please install MuseScore.")
            return False
        try:
            subprocess.run([ms_path, str(musicxml_path), '-o', str(output_pdf)], check=True)
            return True
        except subprocess.CalledProcessError:
            print(f"⚠️  MuseScore failed to render {musicxml_path} -> {output_pdf}")
            return False

    # Process MusicXML files (if user exported them manually) and PDFs
    musicxml_files = list(INPUT_DIR.glob('*.musicxml')) + list(INPUT_DIR.glob('*.xml'))
    pdf_files = list(INPUT_DIR.glob('*.pdf'))

    if not musicxml_files and not pdf_files:
        print(f"No PDFs or MusicXML files found in '{INPUT_DIR}'. Drop your sheet music PDFs there and run this script, or export MusicXML from MuseScore and place the .musicxml file in the input folder.")

    # First process any musicxml files (no conversion needed)
    for mx in musicxml_files:
        print(f"\nProcessing MusicXML: {mx.name}")
        harmony_musicxml = TMP_DIR / (mx.stem + '_harmony.musicxml')
        try:
            harmonize_melody(str(mx), str(harmony_musicxml), instrument_range=(36, 72))
        except Exception as e:
            print(f"Error during harmonization: {e}")
            continue
        out_pdf = OUTPUT_DIR / (mx.stem + '_harmony.pdf')
        rendered = render_musicxml_to_pdf(harmony_musicxml, out_pdf)
        if rendered:
            print(f"✅ Output written: {out_pdf}")
        else:
            print(f"❌ Failed to render PDF for {mx.name}")

    # Then try PDFs (attempt conversion to MusicXML first)
    for pdf in pdf_files:
        print(f"\nProcessing PDF: {pdf.name}")
        temp_musicxml = TMP_DIR / (pdf.stem + '.musicxml')
        success = convert_pdf_to_musicxml(pdf, temp_musicxml)
        if not success:
            print(f"Skipping {pdf.name} due to conversion failure.")
            continue

        # Harmonize and write harmony-only MusicXML to temp
        harmony_musicxml = TMP_DIR / (pdf.stem + '_harmony.musicxml')
        try:
            harmonize_melody(str(temp_musicxml), str(harmony_musicxml), instrument_range=(36, 72))
        except Exception as e:
            print(f"Error during harmonization: {e}")
            continue

        # Render harmony-only MusicXML to PDF in output folder
        out_pdf = OUTPUT_DIR / (pdf.stem + '_harmony.pdf')
        rendered = render_musicxml_to_pdf(harmony_musicxml, out_pdf)
        if rendered:
            print(f"✅ Output written: {out_pdf}")
        else:
            print(f"❌ Failed to render PDF for {pdf.name}")

    # Cleanup temp dir
    try:
        shutil.rmtree(TMP_DIR)
    except Exception:
        pass
