import type {
  Chord,
  HarmonicPlanningContext,
  HierarchicalEngine,
  Note,
  PlannedChord,
  SeededRandom,
} from "./types"
import type { GlobalPlanner } from "./global-planner"
import type { PhraseBuilder } from "./phrase-builder"
import type { HarmonicPlanner } from "./harmonic-planner"
import type { VoiceLeader } from "./voice-leader"

type AnalysisResult = HarmonicPlanningContext & {
  melodyXml: string
  xmlDoc?: Document
  fifths?: string
}

export class SchenkerianEngine implements HierarchicalEngine {
  private readonly globalPlanner: GlobalPlanner
  private readonly phraseBuilder: PhraseBuilder
  private readonly harmonicPlanner: HarmonicPlanner
  private readonly voiceLeader: VoiceLeader
  private readonly rng: SeededRandom
  private readonly parseAndAnalyzeAdapter?: (xml: string) => AnalysisResult
  private readonly renderXmlAdapter?: (
    analysis: AnalysisResult,
    voicedChords: Chord[],
    instruments: string[],
  ) => { harmonyOnlyXML: string; combinedXML: string }

  constructor(params: {
    globalPlanner: GlobalPlanner
    phraseBuilder: PhraseBuilder
    harmonicPlanner: HarmonicPlanner
    voiceLeader: VoiceLeader
    rng: SeededRandom
    adapters?: {
      parseAndAnalyze?: (xml: string) => AnalysisResult
      renderXml?: (
        analysis: AnalysisResult,
        voicedChords: Chord[],
        instruments: string[],
      ) => { harmonyOnlyXML: string; combinedXML: string }
    }
  }) {
    this.globalPlanner = params.globalPlanner
    this.phraseBuilder = params.phraseBuilder
    this.harmonicPlanner = params.harmonicPlanner
    this.voiceLeader = params.voiceLeader
    this.rng = params.rng
    this.parseAndAnalyzeAdapter = params.adapters?.parseAndAnalyze
    this.renderXmlAdapter = params.adapters?.renderXml
  }

  async harmonize(
    melodyXml: string,
    instruments: string[],
  ): Promise<{ harmonyOnlyXML: string; combinedXML: string }> {
    const analysis = this.parseAndAnalyze(melodyXml)
    const { melodyNotes, keyRoot, mode } = analysis

    const skeleton = this.globalPlanner.planUrsatz({
      keyRoot,
      mode,
      lengthInBeats: this.totalBeats(melodyNotes),
      rng: this.rng,
    })

    const phrases = this.phraseBuilder.buildPhrases(
      melodyNotes,
      skeleton,
      this.rng,
    )

    const plannedChords = this.harmonicPlanner.buildPlannedChords(
      analysis,
      skeleton,
      phrases,
      this.rng,
    )

    const voicedChords = this.voiceLeader.realize(
      melodyNotes,
      plannedChords,
      this.rng,
    )

    return this.renderXml(analysis, voicedChords, instruments)
  }

  private parseAndAnalyze(xml: string): AnalysisResult {
    if (!this.parseAndAnalyzeAdapter) {
      // TODO: Delegate to existing MusicXML parsing + key detection.
      throw new Error("SchenkerianEngine.parseAndAnalyze not implemented")
    }

    return this.parseAndAnalyzeAdapter(xml)
  }

  private totalBeats(melody: Note[]): number {
    return melody.reduce((sum, note) => sum + note.duration, 0)
  }

  private renderXml(
    analysis: AnalysisResult,
    voicedChords: Chord[],
    instruments: string[],
  ): { harmonyOnlyXML: string; combinedXML: string } {
    if (!this.renderXmlAdapter) {
      // TODO: Delegate to existing MusicXML renderers.
      throw new Error("SchenkerianEngine.renderXml not implemented")
    }

    return this.renderXmlAdapter(analysis, voicedChords, instruments)
  }

  // Optional: map planned chords to SATB solver inputs as needed.
  private mapPlannedToSolver(_planned: PlannedChord[]): PlannedChord[] {
    return _planned
  }
}
