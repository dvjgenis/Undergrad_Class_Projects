import type {
  GlobalSkeleton,
  HarmonicPlanningContext,
  Note,
  PhraseStructure,
  PlannedChord,
  SeededRandom,
} from "./types"

export interface HarmonicPlanner {
  buildPlannedChords(
    context: HarmonicPlanningContext,
    skeleton: GlobalSkeleton,
    phrases: PhraseStructure[],
    rng: SeededRandom,
  ): PlannedChord[]
}

export class DefaultHarmonicPlanner implements HarmonicPlanner {
  buildPlannedChords(
    context: HarmonicPlanningContext,
    skeleton: GlobalSkeleton,
    phrases: PhraseStructure[],
    rng: SeededRandom,
  ): PlannedChord[] {
    const planned: PlannedChord[] = []
    const measureLength = Math.max(1, context.divisions * context.beatsPerMeasure)
    const totalDuration = context.melodyNotes.reduce(
      (sum, note) => sum + note.duration,
      0,
    )
    const totalMeasures = Math.max(1, Math.ceil(totalDuration / measureLength))

    const slotPlans = buildSlotPlans(
      totalMeasures,
      measureLength,
      skeleton,
      phrases,
      context,
      rng,
    )

    for (let i = 0; i < context.melodyNotes.length; i++) {
      const note = context.melodyNotes[i]
      const slotIndex = Math.min(
        slotPlans.length - 1,
        Math.floor(note.offset / measureLength),
      )
      planned.push({
        ...slotPlans[slotIndex],
        beatIndex: i,
      })
    }

    if (shouldLogPlan()) {
      console.log("[v0] Hierarchical slot plan:", {
        urlinie: skeleton.urlinieDegrees,
        totalMeasures,
        slots: slotPlans.map((slot, index) => ({
          measure: index + 1,
          function: slot.function,
          romanNumeral: slot.romanNumeral,
          cadenceRole: slot.cadenceRole,
          urlinieDegree: slot.constraints?.mustContainScaleDegree?.[0],
        })),
      })
    }

    return planned
  }
}

function shouldLogPlan(): boolean {
  const env = (globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env
  return env?.DEBUG_HIERARCHICAL_PLAN === "true"
}

function buildSlotPlans(
  totalMeasures: number,
  measureLength: number,
  skeleton: GlobalSkeleton,
  phrases: PhraseStructure[],
  context: HarmonicPlanningContext,
  rng: SeededRandom,
): PlannedChord[] {
  const slots: PlannedChord[] = []

  for (let measureIndex = 0; measureIndex < totalMeasures; measureIndex++) {
    const beatPosition = measureIndex * measureLength + Math.floor(measureLength / 2)
    const functionHint = resolveFunctionForBeat(phrases, beatPosition) ?? "Tonic"
    const cadenceRole = resolveCadenceRole(phrases, beatPosition)
    const urlinieDegree = resolveUrlinieDegree(skeleton, measureIndex, totalMeasures)

    const representativeNote = findRepresentativeNote(context.melodyNotes, beatPosition)
    const melodyPitch = representativeNote?.pitch ?? -1
    const melodyScaleDegree = melodyPitch >= 0
      ? context.scale.indexOf((melodyPitch - context.keyRoot + 1200) % 12)
      : -1

    const enforcedFunction = cadenceRole ? enforceCadenceFunction(cadenceRole, functionHint) : functionHint
    const cadenceDegree = resolveCadenceDegree(cadenceRole)
    const degree = cadenceDegree ?? selectChordDegreeForFunction(
      melodyScaleDegree,
      enforcedFunction,
      rng,
    )

    const chordRoot = (context.keyRoot + context.scale[degree]) % 12
    const quality = getChordQuality(degree, context.mode === "major")
    const inversionPreference = resolveInversionPreference(melodyPitch, chordRoot, quality)

    slots.push({
      beatIndex: measureIndex,
      function: enforcedFunction,
      romanNumeral: getRomanNumeral(degree, quality, context.mode === "major", inversionPreference),
      inversionPreference,
      cadenceRole,
      chordRoot,
      quality,
      constraints: urlinieDegree !== null ? { mustContainScaleDegree: [urlinieDegree] } : undefined,
    })
  }

  return slots
}

function resolveUrlinieDegree(
  skeleton: GlobalSkeleton,
  measureIndex: number,
  totalMeasures: number,
): number | null {
  if (!skeleton.urlinieDegrees.length) return null
  if (totalMeasures <= 1) return skeleton.urlinieDegrees[skeleton.urlinieDegrees.length - 1] ?? null

  const progress = measureIndex / (totalMeasures - 1)
  const stepIndex = Math.min(
    skeleton.urlinieDegrees.length - 1,
    Math.floor(progress * (skeleton.urlinieDegrees.length - 1)),
  )

  return skeleton.urlinieDegrees[stepIndex] ?? null
}

function findRepresentativeNote(
  melody: Note[],
  beatPosition: number,
): Note | undefined {
  return melody.find((note) => note.offset <= beatPosition && note.offset + note.duration > beatPosition)
}

function enforceCadenceFunction(
  cadenceRole: "PAC" | "IAC" | "HC" | "DC",
  fallback: "Tonic" | "Predominant" | "Dominant",
): "Tonic" | "Predominant" | "Dominant" {
  if (cadenceRole === "HC") return "Dominant"
  if (cadenceRole === "PAC" || cadenceRole === "IAC") return "Tonic"
  return fallback
}

function resolveCadenceDegree(
  cadenceRole: "PAC" | "IAC" | "HC" | "DC" | undefined,
): number | null {
  if (!cadenceRole) return null
  if (cadenceRole === "HC") return 4 // V
  if (cadenceRole === "PAC" || cadenceRole === "IAC") return 0 // I
  if (cadenceRole === "DC") return 6 // vii° or dominant substitute
  return null
}

function resolveFunctionForBeat(
  phrases: PhraseStructure[],
  beatIndex: number,
): "Tonic" | "Predominant" | "Dominant" | null {
  for (const phrase of phrases) {
    for (const region of phrase.functionalRegions) {
      if (beatIndex >= region.startBeat && beatIndex <= region.endBeat) {
        return region.function
      }
    }
  }
  return null
}

function resolveCadenceRole(
  phrases: PhraseStructure[],
  beatIndex: number,
): "PAC" | "IAC" | "HC" | "DC" | undefined {
  for (const phrase of phrases) {
    for (const region of phrase.functionalRegions) {
      if (beatIndex === region.endBeat && region.cadence) {
        return region.cadence
      }
    }
  }
  return undefined
}

function selectChordDegreeForFunction(
  melodyScaleDegree: number,
  functionHint: "Tonic" | "Predominant" | "Dominant",
  rng: SeededRandom,
): number {
  const functionDegrees: Record<string, number[]> = {
    Tonic: [0, 2, 5],
    Predominant: [1, 3, 5],
    Dominant: [4, 6],
  }

  const candidates = functionDegrees[functionHint] || [0]

  if (melodyScaleDegree >= 0) {
    const compatible = candidates.filter((degree) => {
      return degree === melodyScaleDegree
        || (degree + 2) % 7 === melodyScaleDegree
        || (degree + 4) % 7 === melodyScaleDegree
    })

    if (compatible.length > 0) {
      return compatible[Math.floor(rng.next() * compatible.length)]
    }
  }

  return candidates[Math.floor(rng.next() * candidates.length)]
}

function getChordQuality(scaleDegree: number, isMajorKey: boolean): "major" | "minor" | "diminished" | "augmented" {
  if (isMajorKey) {
    if (scaleDegree === 0 || scaleDegree === 3 || scaleDegree === 4) return "major"
    if (scaleDegree === 6) return "diminished"
    return "minor"
  }

  if (scaleDegree === 0 || scaleDegree === 3) return "minor"
  if (scaleDegree === 2 || scaleDegree === 5 || scaleDegree === 6) return "major"
  if (scaleDegree === 1) return "diminished"
  if (scaleDegree === 4) return "major"
  return "minor"
}

function resolveInversionPreference(
  melodyPitch: number,
  chordRoot: number,
  quality: "major" | "minor" | "diminished" | "augmented",
): 0 | 1 | 2 {
  if (melodyPitch < 0) return 0
  const melodyPitchClass = melodyPitch % 12
  const third = (chordRoot + (quality === "major" ? 4 : 3)) % 12
  const fifth = (chordRoot + (quality === "diminished" ? 6 : quality === "augmented" ? 8 : 7)) % 12

  if (melodyPitchClass === third) return 1
  if (melodyPitchClass === fifth) return 2
  return 0
}

function getRomanNumeral(
  scaleDegree: number,
  quality: "major" | "minor" | "diminished" | "augmented",
  isMajorKey: boolean,
  inversion: 0 | 1 | 2,
): string {
  const romanNumerals = isMajorKey
    ? ["I", "ii", "iii", "IV", "V", "vi", "vii°"]
    : ["i", "ii°", "III", "iv", "v", "VI", "VII"]

  let numeral = romanNumerals[scaleDegree] || "I"
  if (quality === "augmented") {
    numeral = numeral.replace("I", "I+").replace("i", "i+")
  }

  if (inversion === 1) numeral += "6"
  if (inversion === 2) numeral += "64"

  return numeral
}
