import os
from pathlib import Path

from engine.io_handler import (
    parse_xml,
    parse_xml_string,
    export_xml,
    export_xml_string,
    generate_test_input,
)
from engine.core_engine import (
    build_schenkerian_graph_matrix,
    enrich_violations_with_measures,
    solve_harmony,
    validate_solution,
)
from engine.hierarchical_bridge import merge_backend_hierarchical_plan
from engine.settings import EngineSettings, load_engine_settings

INPUT_DIR = "input"
OUTPUT_DIR = "output"
TEST_FILE = os.path.join(INPUT_DIR, "test_melody.musicxml")
RESULT_FILE = os.path.join(OUTPUT_DIR, "satb_result.musicxml")


def _pc_name(pc: int) -> str:
    names = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
    return names[pc % 12]


def main():
    settings = load_engine_settings()
    print(
        f"Settings: mood={settings.mood}, genre={settings.genre}, difficulty={settings.difficulty}"
    )
    # Ensure directories exist
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Check if user provided an input; if not, generate a guaranteed working baseline
    input_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.musicxml') or f.endswith('.xml')]
    
    if not input_files:
        print("No XML found in input folder. Generating baseline test file...")
        generate_test_input(TEST_FILE)
        target_file = TEST_FILE
    else:
        target_file = os.path.join(INPUT_DIR, input_files[0])
        print(f"Found user input: {target_file}")

    # 1. Parse Input
    print("Parsing Melody and Chords...")
    source_score, melody, chords, durations, meta = parse_xml(target_file, settings)
    
    if not melody or not chords:
        print("Error: Could not extract notes and chords from the XML.")
        return

    # 2. Run the Logic Core
    print("Building DAG and solving constraints...")
    try:
        diatonic = set(meta.get("diatonic_pcs", []))
        forbidden_accidentals = set(meta.get("forbidden_accidentals", []))
        tonic_pc = int(meta.get("tonal_center_pc", 0))
        cadence_steps = set(meta.get("cadence_steps", []))
        secondary_steps = set(meta.get("secondary_dominant_steps", []))
        structural_pillars = set(meta.get("structural_pillars", []))
        urlinie_steps = set(meta.get("urlinie_steps", []))
        beat_strengths = list(meta.get("beat_strengths", []))

        print(
            "Analysis: "
            f"key_fifths={meta.get('key_signature_fifths', 0)}, "
            f"tonal_center={_pc_name(tonic_pc)} ({tonic_pc}), "
            f"meter={meta.get('beats_per_measure', 4)}/{meta.get('beat_unit', 4)}, "
            f"c_major_lock={meta.get('global_c_major_lock', False)}, "
            f"c_major_ratio={meta.get('c_major_ratio', 0.0):.2f}"
        )
        print(
            "Structure: "
            f"pillars={sorted(structural_pillars)}, "
            f"urlinie_steps={sorted(urlinie_steps)}, "
            f"cadence_steps={sorted(cadence_steps)}"
        )
        if beat_strengths:
            preview = ", ".join(f"{w:.2f}" for w in beat_strengths[:16])
            suffix = " ..." if len(beat_strengths) > 16 else ""
            print(f"Metric weights: [{preview}]{suffix}")

        print("Phase A: Structural analysis...")
        merged_chords = merge_backend_hierarchical_plan(
            chords,
            durations,
            beats_per_measure=meta.get("beats_per_measure", 4),
            settings=settings,
        )
        allowed_pcs_by_step = {}
        if diatonic:
            raised_fourth = (tonic_pc + 6) % 12
            for t in range(len(merged_chords)):
                allowed = set(diatonic)
                if t in secondary_steps and t in cadence_steps:
                    allowed.add(raised_fourth)
                elif forbidden_accidentals:
                    allowed -= forbidden_accidentals
                allowed_pcs_by_step[t] = allowed
        print("Phase B: Graph-matrix construction...")
        _, graph_stats = build_schenkerian_graph_matrix(
            merged_chords,
            melody,
            max_candidates=180,
            difficulty=settings.difficulty,
            structural_steps=structural_pillars | urlinie_steps,
            allowed_pcs_by_step=allowed_pcs_by_step if allowed_pcs_by_step else None,
        )
        print(
            f"Graph stats: nodes={graph_stats.total_nodes}, "
            f"strict_edges={graph_stats.strict_edges}, soft_edges={graph_stats.soft_edges}"
        )
        print("Phase C: Viterbi shortest-path solving...")
        solution = solve_harmony(
            merged_chords,
            melody,
            difficulty=settings.difficulty,
            structural_pillars=structural_pillars,
            urlinie_steps=urlinie_steps,
            beat_strengths=beat_strengths,
            tonic_pc=tonic_pc,
            diatonic_pcs=diatonic,
            secondary_dominant_steps=secondary_steps,
            cadence_steps=cadence_steps,
        )
        print("Optimal voice leading path found!")
        violations = validate_solution(solution, tonic_pc=tonic_pc)
        violations = enrich_violations_with_measures(
            violations,
            durations,
            beats_per_measure=meta.get("beats_per_measure", 4),
        )
        if violations:
            print(f"Inspector: {len(violations)} rule flags detected for review.")
            for issue in violations[:8]:
                print(f" - m{issue['measure']} t={issue['time_step']} {issue['code']}: {issue['explanation']}")
        else:
            print("Inspector: no hard-rule violations detected.")
        
        # 3. Export Output
        export_xml(solution, source_score, RESULT_FILE)
        print(f"Success! Output saved to {RESULT_FILE}")
        
    except Exception as e:
        print(f"Engine Failed: {e}")


def run_harmonize_pipeline(
    musicxml: str,
    settings: EngineSettings,
    instruments: list[str] | None = None,
) -> tuple[str, list[dict]]:
    """
    API entry point: harmonize from MusicXML string, return (musicxml_string, violations).
    instruments: list of part names to include (e.g. ["alto","tenor","bass"]). None = all.
    """
    # Index building is the backend's responsibility. Engine consumes CSV when present,
    # or falls back to knowledge_base/*.txt parsing. No TheoryInspector import.
    source_score, melody, chords, durations, meta = parse_xml_string(musicxml, settings)
    if not melody or not chords:
        raise ValueError("Could not extract melody and chords from the XML.")

    diatonic = set(meta.get("diatonic_pcs", []))
    forbidden_accidentals = set(meta.get("forbidden_accidentals", []))
    tonic_pc = int(meta.get("tonal_center_pc", 0))
    cadence_steps = set(meta.get("cadence_steps", []))
    secondary_steps = set(meta.get("secondary_dominant_steps", []))
    structural_pillars = set(meta.get("structural_pillars", []))
    urlinie_steps = set(meta.get("urlinie_steps", []))
    beat_strengths = list(meta.get("beat_strengths", []))
    beats_per_measure = meta.get("beats_per_measure", 4)

    merged_chords = merge_backend_hierarchical_plan(
        chords, durations, beats_per_measure=beats_per_measure, settings=settings
    )
    allowed_pcs_by_step = {}
    if diatonic:
        raised_fourth = (tonic_pc + 6) % 12
        for t in range(len(merged_chords)):
            allowed = set(diatonic)
            if t in secondary_steps and t in cadence_steps:
                allowed.add(raised_fourth)
            elif forbidden_accidentals:
                allowed -= forbidden_accidentals
            allowed_pcs_by_step[t] = allowed

    solution = solve_harmony(
        merged_chords,
        melody,
        difficulty=settings.difficulty,
        structural_pillars=structural_pillars,
        urlinie_steps=urlinie_steps,
        beat_strengths=beat_strengths,
        tonic_pc=tonic_pc,
        diatonic_pcs=diatonic,
        secondary_dominant_steps=secondary_steps,
        cadence_steps=cadence_steps,
    )
    violations = validate_solution(solution, tonic_pc=tonic_pc)
    violations = enrich_violations_with_measures(
        violations, durations, beats_per_measure=beats_per_measure
    )
    out_xml = export_xml_string(solution, source_score, instruments=instruments)
    return out_xml, violations


if __name__ == "__main__":
    main()