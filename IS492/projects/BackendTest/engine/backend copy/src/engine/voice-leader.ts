import type { Chord, Note, PlannedChord, SeededRandom } from "./types"
import { voiceChord } from "./satb-solver"

export interface VoiceLeader {
  realize(
    melody: Note[],
    chords: PlannedChord[],
    rng: SeededRandom,
  ): Chord[]
}

export class DefaultVoiceLeader implements VoiceLeader {
  realize(
    melody: Note[],
    chords: PlannedChord[],
    rng: SeededRandom,
  ): Chord[] {
    void rng
    const realized: Chord[] = []

    let previousChord: Chord | null = null

    for (let i = 0; i < chords.length; i++) {
      const plan = chords[i]
      const melodyNote = melody[i]

      if (!melodyNote) {
        continue
      }

      // If a resolved chord is provided, preserve it verbatim (no-op pipeline).
      if (plan.resolvedChord && plan.resolvedChord.voices?.length) {
        realized.push(plan.resolvedChord)
        previousChord = plan.resolvedChord
        continue
      }

      // Otherwise, attempt a minimal SATB realization using the plan.
      if (plan.chordRoot === undefined || !plan.quality) {
        continue
      }

      const chordRoot = plan.chordRoot
      const chordThird = (chordRoot + (plan.quality === "major" || plan.quality === "dominant7" || plan.quality === "major7" ? 4 : 3)) % 12
      const chordFifth = (chordRoot + (plan.quality === "diminished" || plan.quality === "halfDim7" || plan.quality === "dim7" ? 6 : plan.quality === "augmented" ? 8 : 7)) % 12
      const inversion = plan.inversionPreference ?? 0

      const voices = voiceChord(
        melodyNote.pitch,
        chordRoot,
        chordThird,
        chordFifth,
        inversion,
        {
          previousChord,
          previousMelody: melody[i - 1]?.pitch ?? null,
          measurePosition: i % 4,
          phrasePosition: i,
          instrumentVariation: 0,
        },
      )

      const resolved: Chord = {
        root: chordRoot,
        quality: plan.quality,
        inversion: inversion as 0 | 1 | 2 | 3,
        voices,
        romanNumeral: plan.romanNumeral,
      }

      realized.push(resolved)
      previousChord = resolved
    }

    return realized
  }
}
