export type HarmonicFunction = "Tonic" | "Predominant" | "Dominant"
export type PhraseType = "Antecedent" | "Consequent"
export type CadenceType = "PAC" | "IAC" | "HC" | "DC"

export interface SeededRandom {
  next(): number
  reset?(seed: number): void
}

export interface Note {
  pitch: number
  duration: number
  offset: number
}

export interface Chord {
  root: number
  quality:
    | "major"
    | "minor"
    | "diminished"
    | "augmented"
    | "dominant7"
    | "major7"
    | "minor7"
    | "halfDim7"
    | "dim7"
  inversion: 0 | 1 | 2 | 3
  voices: number[]
  romanNumeral?: string
  function?: "tonic" | "predominant" | "dominant" | "tonicProlongation"
  isSecondaryDominant?: boolean
  isBorrowed?: boolean
  isIncomplete?: boolean
}

export interface GlobalSkeleton {
  keyRoot: number
  mode: "major" | "minor"
  ursatz: Array<"I" | "V" | "I6" | "V7" | "I64">
  urlinieDegrees: number[]
  cadenceMap: CadencePoint[]
}

export interface CadencePoint {
  index: number
  type: CadenceType
  target: "I" | "V"
}

export interface PhraseStructure {
  phraseId: string
  type: PhraseType
  lengthInBeats: number
  functionalRegions: FunctionalRegion[]
}

export interface FunctionalRegion {
  function: HarmonicFunction
  startBeat: number
  endBeat: number
  cadence?: CadenceType
}

export interface PlannedChord {
  beatIndex: number
  function: HarmonicFunction
  romanNumeral?: string
  inversionPreference?: 0 | 1 | 2 | 3
  cadenceRole?: CadenceType
  resolvedChord?: Chord
  chordRoot?: number
  quality?: Chord["quality"]
  constraints?: {
    mustContainScaleDegree?: number[]
    avoidParallels?: boolean
    maxLeap?: number
  }
}

export interface HarmonicPlanningContext {
  melodyNotes: Note[]
  melodicLines?: Note[][]
  keyRoot: number
  scale: number[]
  mode: "major" | "minor"
  isPolyphonic: boolean
  divisions: number
  beatsPerMeasure: number
}

export interface GlobalPlanParams {
  keyRoot: number
  mode: "major" | "minor"
  lengthInBeats: number
  rng: SeededRandom
}

export interface HierarchicalEngine {
  harmonize(
    melodyXml: string,
    instruments: string[],
  ): Promise<{ harmonyOnlyXML: string; combinedXML: string }>
}
