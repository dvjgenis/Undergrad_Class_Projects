import type { GlobalSkeleton, Note, PhraseStructure, SeededRandom } from "./types"

export interface PhraseBuilder {
  buildPhrases(
    melody: Note[],
    global: GlobalSkeleton,
    rng: SeededRandom,
  ): PhraseStructure[]
}

export class DefaultPhraseBuilder implements PhraseBuilder {
  buildPhrases(
    melody: Note[],
    global: GlobalSkeleton,
    rng: SeededRandom,
  ): PhraseStructure[] {
    void rng
    const totalBeats = melody.reduce((sum, note) => sum + note.duration, 0)
    const halfBeats = Math.max(1, Math.floor(totalBeats / 2))

    const antecedent: PhraseStructure = {
      phraseId: "phrase-1",
      type: "Antecedent",
      lengthInBeats: halfBeats,
      functionalRegions: [
        {
          function: "Tonic",
          startBeat: 0,
          endBeat: Math.max(0, Math.floor(halfBeats * 0.4) - 1),
        },
        {
          function: "Predominant",
          startBeat: Math.floor(halfBeats * 0.4),
          endBeat: Math.max(0, Math.floor(halfBeats * 0.7) - 1),
        },
        {
          function: "Dominant",
          startBeat: Math.floor(halfBeats * 0.7),
          endBeat: Math.max(0, halfBeats - 1),
          cadence: "HC",
        },
      ],
    }

    const consequent: PhraseStructure = {
      phraseId: "phrase-2",
      type: "Consequent",
      lengthInBeats: totalBeats - halfBeats,
      functionalRegions: [
        {
          function: "Tonic",
          startBeat: halfBeats,
          endBeat: Math.max(halfBeats, Math.floor(halfBeats + (totalBeats - halfBeats) * 0.4) - 1),
        },
        {
          function: "Predominant",
          startBeat: Math.floor(halfBeats + (totalBeats - halfBeats) * 0.4),
          endBeat: Math.max(halfBeats, Math.floor(halfBeats + (totalBeats - halfBeats) * 0.7) - 1),
        },
        {
          function: "Dominant",
          startBeat: Math.floor(halfBeats + (totalBeats - halfBeats) * 0.7),
          endBeat: Math.max(halfBeats, totalBeats - 1),
          cadence: "PAC",
        },
      ],
    }

    return totalBeats <= 4 ? [consequent] : [antecedent, consequent]
  }
}
