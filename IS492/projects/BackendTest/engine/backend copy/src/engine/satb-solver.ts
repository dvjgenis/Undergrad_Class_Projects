export interface VoiceLeadingContext {
  previousChord: Chord | null
  previousMelody: number | null
  measurePosition: number
  phrasePosition: number
  instrumentVariation: number
  previousVoices?: number[]
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
}

const SATB_RANGES = {
  soprano: { min: 60, max: 84 }, // C4 to C6
  alto: { min: 55, max: 76 }, // G3 to E5
  tenor: { min: 48, max: 67 }, // C3 to G4
  bass: { min: 40, max: 60 }, // E2 to C4
}

export function voiceChordPolyphonic(
  melodyPitch: number,
  chordRoot: number,
  chordThird: number,
  chordFifth: number,
  inversion: 0 | 1 | 2 | 3,
  context: VoiceLeadingContext,
  inputNotes: number[],
  isSeventh = false,
  chordSeventh: number | null = null,
): number[] {
  const soprano = melodyPitch
  const sopranoOctave = Math.floor(soprano / 12)

  // Strict SATB ranges
  const altoMin = SATB_RANGES.alto.min
  const altoMax = SATB_RANGES.alto.max
  const tenorMin = SATB_RANGES.tenor.min
  const tenorMax = SATB_RANGES.tenor.max
  const bassMin = SATB_RANGES.bass.min
  const bassMax = SATB_RANGES.bass.max

  let altoTone: number, tenorTone: number, bassTone: number

  // Try to avoid doubling notes that are already in the input
  const inputPitchClasses = new Set(inputNotes.map((n) => n % 12))
  const chordTones = [chordRoot, chordThird, chordFifth]
  if (chordSeventh !== null) chordTones.push(chordSeventh)
  void inputPitchClasses

  // Determine doubling based on inversion and chord type
  const doublingStrategy = getDoublingStrategy(
    inversion,
    chordRoot,
    chordThird,
    chordFifth,
    isSeventh,
    chordSeventh,
  )

  // Voice the chord based on inversion
  if (inversion === 0) {
    // Root position: double the root
    bassTone = findClosestPitch(chordRoot, sopranoOctave - 2, bassMin, bassMax)
    const availableForAlto = doublingStrategy.alto || chordThird
    const availableForTenor = doublingStrategy.tenor || chordFifth
    altoTone = findClosestPitch(availableForAlto, sopranoOctave - 1, altoMin, altoMax)
    tenorTone = findClosestPitch(availableForTenor, sopranoOctave - 1, tenorMin, tenorMax)
  } else if (inversion === 1) {
    // First inversion: don't double the bass (third), double root or fifth
    bassTone = findClosestPitch(chordThird, sopranoOctave - 2, bassMin, bassMax)
    const availableForAlto = doublingStrategy.alto || chordFifth
    const availableForTenor = doublingStrategy.tenor || chordRoot
    altoTone = findClosestPitch(availableForAlto, sopranoOctave - 1, altoMin, altoMax)
    tenorTone = findClosestPitch(availableForTenor, sopranoOctave - 1, tenorMin, tenorMax)
  } else if (inversion === 2) {
    // Second inversion: double the bass (fifth)
    bassTone = findClosestPitch(chordFifth, sopranoOctave - 2, bassMin, bassMax)
    const availableForAlto = doublingStrategy.alto || chordRoot
    const availableForTenor = doublingStrategy.tenor || chordThird
    altoTone = findClosestPitch(availableForAlto, sopranoOctave - 1, altoMin, altoMax)
    tenorTone = findClosestPitch(availableForTenor, sopranoOctave - 1, tenorMin, tenorMax)
  } else {
    // Third inversion (7th chords): bass is the seventh
    bassTone = findClosestPitch(chordSeventh!, sopranoOctave - 2, bassMin, bassMax)
    altoTone = findClosestPitch(chordRoot, sopranoOctave - 1, altoMin, altoMax)
    tenorTone = findClosestPitch(chordThird, sopranoOctave - 1, tenorMin, tenorMax)
  }

  // Apply voice leading with strict SATB rules
  if (context.previousChord) {
    const prevVoices = context.previousChord.voices

    // Apply voice leading prioritizing: oblique > contrary/stepwise > small leaps
    altoTone = applyVoiceLeadingToVoice(
      altoTone,
      prevVoices[1],
      chordRoot,
      chordThird,
      chordFifth,
      altoMin,
      altoMax,
      false,
      chordSeventh,
    )
    tenorTone = applyVoiceLeadingToVoice(
      tenorTone,
      prevVoices[2],
      chordRoot,
      chordThird,
      chordFifth,
      tenorMin,
      tenorMax,
      false,
      chordSeventh,
    )
    bassTone = applyVoiceLeadingToVoice(
      bassTone,
      prevVoices[3],
      chordRoot,
      chordThird,
      chordFifth,
      bassMin,
      bassMax,
      true,
      chordSeventh,
    )

    // Handle tendency tones (7th resolving down, leading tone resolving up)
    if (isSeventh && chordSeventh !== null) {
      // 7th of chord should resolve down by step
      const prevBass = prevVoices[3]
      if (prevBass !== -1 && (prevBass % 12) === chordSeventh) {
        // Previous chord had this 7th, resolve it down
        const resolution = (chordSeventh - 1 + 12) % 12
        bassTone = findClosestPitch(resolution, Math.floor(bassTone / 12), bassMin, bassMax)
      }
    }

    // Check for leading tone (7th scale degree) - should resolve up
    const leadingTone = (chordRoot + 11) % 12 // 7th scale degree
    if (
      context.previousChord.root === leadingTone &&
      (context.previousChord.quality === "dominant7" || context.previousChord.quality === "major")
    ) {
      // Previous was V or V7, leading tone should resolve up to tonic
      for (let i = 0; i < prevVoices.length; i++) {
        if (prevVoices[i] !== -1 && (prevVoices[i] % 12) === leadingTone) {
          // This voice had leading tone, should resolve up
          const resolution = chordRoot
          if (i === 0) {
            // Soprano - already handled by melody
          } else if (i === 1) {
            altoTone = findClosestPitch(resolution, Math.floor(altoTone / 12), altoMin, altoMax)
          } else if (i === 2) {
            tenorTone = findClosestPitch(resolution, Math.floor(tenorTone / 12), tenorMin, tenorMax)
          }
        }
      }
    }

    // Check spacing (no interval > octave between adjacent voices)
    const voices = [soprano, altoTone, tenorTone, bassTone]
    const adjustedVoices = enforceSpacing(voices)

    // Avoid parallel motion (P5, P8, direct fifths/octaves)
    const finalVoices = avoidParallelMotion(
      adjustedVoices,
      prevVoices,
      [chordRoot, chordThird, chordFifth, chordSeventh].filter((t) => t !== null) as number[],
    )

    altoTone = finalVoices[1]
    tenorTone = finalVoices[2]
    bassTone = finalVoices[3]
  } else {
    // First chord - just check spacing
    const voices = [soprano, altoTone, tenorTone, bassTone]
    const adjustedVoices = enforceSpacing(voices)
    altoTone = adjustedVoices[1]
    tenorTone = adjustedVoices[2]
    bassTone = adjustedVoices[3]
  }

  return [soprano, altoTone, tenorTone, bassTone]
}

export function getDoublingStrategy(
  inversion: number,
  root: number,
  third: number,
  fifth: number,
  isSeventh: boolean,
  seventh: number | null,
): { alto?: number; tenor?: number } {
  if (isSeventh && seventh !== null) {
    // 7th chords: don't double any tone, use all four chord tones
    return {}
  }

  if (inversion === 0) {
    // Root position: double the root
    return { alto: root, tenor: root }
  } else if (inversion === 1) {
    // First inversion: don't double the bass (third), double root or fifth
    return { alto: root, tenor: fifth }
  } else if (inversion === 2) {
    // Second inversion: double the bass (fifth)
    return { alto: fifth, tenor: fifth }
  }

  return {}
}

export function enforceSpacing(voices: number[]): number[] {
  const adjusted = [...voices]

  // Check Soprano-Alto spacing
  if (adjusted[0] !== -1 && adjusted[1] !== -1) {
    const interval = adjusted[0] - adjusted[1]
    if (interval > 12) {
      // Too wide, move alto up an octave
      adjusted[1] += 12
    } else if (interval < 0) {
      // Voices crossed, fix
      adjusted[1] = adjusted[0] - 12
    }
  }

  // Check Alto-Tenor spacing
  if (adjusted[1] !== -1 && adjusted[2] !== -1) {
    const interval = adjusted[1] - adjusted[2]
    if (interval > 12) {
      adjusted[2] += 12
    } else if (interval < 0) {
      adjusted[2] = adjusted[1] - 12
    }
  }

  // Check Tenor-Bass spacing
  if (adjusted[2] !== -1 && adjusted[3] !== -1) {
    const interval = adjusted[2] - adjusted[3]
    if (interval > 12) {
      adjusted[3] += 12
    } else if (interval < 0) {
      adjusted[3] = adjusted[2] - 12
    }
  }

  return adjusted
}

export function voiceChord(
  melodyPitch: number,
  chordRoot: number,
  chordThird: number,
  chordFifth: number,
  inversion: 0 | 1 | 2,
  context: VoiceLeadingContext,
): number[] {
  const soprano = melodyPitch
  const sopranoOctave = Math.floor(soprano / 12)

  // Use strict SATB ranges
  const altoMin = SATB_RANGES.alto.min
  const altoMax = SATB_RANGES.alto.max
  const tenorMin = SATB_RANGES.tenor.min
  const tenorMax = SATB_RANGES.tenor.max
  const bassMin = SATB_RANGES.bass.min
  const bassMax = SATB_RANGES.bass.max

  let altoTone: number, tenorTone: number, bassTone: number

  // Apply doubling rules
  const doublingStrategy = getDoublingStrategy(inversion, chordRoot, chordThird, chordFifth, false, null)

  if (inversion === 0) {
    // Root position: double the root
    bassTone = findClosestPitch(chordRoot, sopranoOctave - 2, bassMin, bassMax)
    altoTone = findClosestPitch(doublingStrategy.alto || chordThird, sopranoOctave - 1, altoMin, altoMax)
    tenorTone = findClosestPitch(doublingStrategy.tenor || chordFifth, sopranoOctave - 1, tenorMin, tenorMax)
  } else if (inversion === 1) {
    // First inversion: don't double the bass (third)
    bassTone = findClosestPitch(chordThird, sopranoOctave - 2, bassMin, bassMax)
    altoTone = findClosestPitch(doublingStrategy.alto || chordFifth, sopranoOctave - 1, altoMin, altoMax)
    tenorTone = findClosestPitch(doublingStrategy.tenor || chordRoot, sopranoOctave - 1, tenorMin, tenorMax)
  } else {
    // Second inversion: double the bass (fifth)
    bassTone = findClosestPitch(chordFifth, sopranoOctave - 2, bassMin, bassMax)
    altoTone = findClosestPitch(doublingStrategy.alto || chordRoot, sopranoOctave - 1, altoMin, altoMax)
    tenorTone = findClosestPitch(doublingStrategy.tenor || chordThird, sopranoOctave - 1, tenorMin, tenorMax)
  }

  if (context.previousChord) {
    const prevVoices = context.previousChord.voices

    // Apply voice leading with motion priority
    altoTone = applyVoiceLeadingToVoice(altoTone, prevVoices[1], chordRoot, chordThird, chordFifth, altoMin, altoMax)
    tenorTone = applyVoiceLeadingToVoice(
      tenorTone,
      prevVoices[2],
      chordRoot,
      chordThird,
      chordFifth,
      tenorMin,
      tenorMax,
    )
    bassTone = applyVoiceLeadingToVoice(
      bassTone,
      prevVoices[3],
      chordRoot,
      chordThird,
      chordFifth,
      bassMin,
      bassMax,
      true,
    )

    // Enforce spacing
    const voices = [soprano, altoTone, tenorTone, bassTone]
    const spacedVoices = enforceSpacing(voices)

    // Avoid parallel motion
    const adjustedVoices = avoidParallelMotion(spacedVoices, prevVoices, [chordRoot, chordThird, chordFifth])
    altoTone = adjustedVoices[1]
    tenorTone = adjustedVoices[2]
    bassTone = adjustedVoices[3]
  } else {
    // First chord - just check spacing
    const voices = [soprano, altoTone, tenorTone, bassTone]
    const spacedVoices = enforceSpacing(voices)
    altoTone = spacedVoices[1]
    tenorTone = spacedVoices[2]
    bassTone = spacedVoices[3]
  }

  return [soprano, altoTone, tenorTone, bassTone]
}

export function findClosestPitch(
  pitchClass: number,
  targetOctave: number,
  minMidi: number,
  maxMidi: number,
): number {
  let pitch = targetOctave * 12 + pitchClass

  while (pitch < minMidi) pitch += 12
  while (pitch > maxMidi) pitch -= 12

  return pitch
}

export function applyVoiceLeadingToVoice(
  currentPitch: number,
  previousPitch: number,
  chordRoot: number,
  chordThird: number,
  chordFifth: number,
  minRange: number,
  maxRange: number,
  allowLeaps = false,
  chordSeventh: number | null = null,
): number {
  if (previousPitch === -1) {
    // No previous pitch, just constrain to range
    while (currentPitch < minRange) currentPitch += 12
    while (currentPitch > maxRange) currentPitch -= 12
    return currentPitch
  }

  const interval = Math.abs(currentPitch - previousPitch)
  const currentPC = currentPitch % 12
  const previousPC = previousPitch % 12

  // Priority 1: Oblique motion (common tone retention) - best
  if (currentPC === previousPC) {
    // Same pitch class - keep same or move to adjacent octave if needed
    while (currentPitch < minRange) currentPitch += 12
    while (currentPitch > maxRange) currentPitch -= 12
    return currentPitch
  }

  // Priority 2: Stepwise motion (2nd) - very good
  const stepwiseInterval = Math.abs(currentPC - previousPC)
  if (stepwiseInterval === 1 || stepwiseInterval === 11) {
    // Stepwise motion - keep it
    while (currentPitch < minRange) currentPitch += 12
    while (currentPitch > maxRange) currentPitch -= 12
    return currentPitch
  }

  // Priority 3: Small leaps (3rd, 4th) - acceptable
  if (interval <= 5) {
    while (currentPitch < minRange) currentPitch += 12
    while (currentPitch > maxRange) currentPitch -= 12
    return currentPitch
  }

  // Priority 4: Large leaps - try to minimize
  if (interval > (allowLeaps ? 12 : 7)) {
    const chordTones = [chordRoot, chordThird, chordFifth]
    if (chordSeventh !== null) chordTones.push(chordSeventh)
    const previousOctave = Math.floor(previousPitch / 12)

    let bestPitch = currentPitch
    let bestScore = -Infinity

    for (const tone of chordTones) {
      for (let octave = previousOctave - 1; octave <= previousOctave + 1; octave++) {
        const candidate = octave * 12 + tone
        if (candidate >= minRange && candidate <= maxRange) {
          const distance = Math.abs(candidate - previousPitch)
          const candidatePC = candidate % 12

          // Score: prefer stepwise, then small leaps, then common tones
          let score = 0
          if (candidatePC === previousPC) score = 100 // Common tone
          else if (Math.abs(candidatePC - previousPC) === 1 || Math.abs(candidatePC - previousPC) === 11) score = 80 // Stepwise
          else if (distance <= 5) score = 60 // Small leap
          else score = 40 - distance // Large leap (penalized)

          if (score > bestScore) {
            bestScore = score
            bestPitch = candidate
          }
        }
      }
    }

    currentPitch = bestPitch
  }

  while (currentPitch < minRange) currentPitch += 12
  while (currentPitch > maxRange) currentPitch -= 12

  return currentPitch
}

export function avoidParallelMotion(
  currentVoices: number[],
  previousVoices: number[],
  chordTones: number[],
): number[] {
  const adjusted = [...currentVoices]

  for (let i = 0; i < currentVoices.length; i++) {
    if (currentVoices[i] === -1 || previousVoices[i] === -1) continue

    for (let j = i + 1; j < currentVoices.length; j++) {
      if (currentVoices[j] === -1 || previousVoices[j] === -1) continue

      const currentInterval = Math.abs(currentVoices[i] - currentVoices[j]) % 12
      const previousInterval = Math.abs(previousVoices[i] - previousVoices[j]) % 12

      // Check for parallel perfect intervals (P5 or P8)
      if ((currentInterval === 7 || currentInterval === 0) && currentInterval === previousInterval) {
        const currentMotion = currentVoices[i] - previousVoices[i]
        const otherMotion = currentVoices[j] - previousVoices[j]

        // Both voices moving in same direction = parallel motion
        if ((currentMotion > 0 && otherMotion > 0) || (currentMotion < 0 && otherMotion < 0)) {
          const lowerVoiceOctave = Math.floor(adjusted[j] / 12)

          // Try to fix by changing the lower voice
          for (const tone of chordTones) {
            const candidate = lowerVoiceOctave * 12 + tone
            const newInterval = Math.abs(adjusted[i] - candidate) % 12

            if (newInterval !== currentInterval && newInterval !== 7 && newInterval !== 0) {
              adjusted[j] = candidate
              console.log(
                `[v0] Avoided parallel ${currentInterval === 7 ? "fifth" : "octave"} between voices ${i} and ${j}`,
              )
              break
            }
          }
        }
      }

      // Check for direct fifths/octaves (similar motion into P5 or P8)
      if (currentInterval === 7 || currentInterval === 0) {
        const currentMotion = currentVoices[i] - previousVoices[i]
        const otherMotion = currentVoices[j] - previousVoices[j]

        // Both voices moving in same direction into a perfect interval
        if ((currentMotion > 0 && otherMotion > 0) || (currentMotion < 0 && otherMotion < 0)) {
          const prevInterval = Math.abs(previousVoices[i] - previousVoices[j]) % 12
          if (prevInterval !== 7 && prevInterval !== 0) {
            // Previous interval was not perfect, but we're moving into one
            // This is a direct fifth/octave - generally avoid
            const lowerVoiceOctave = Math.floor(adjusted[j] / 12)

            for (const tone of chordTones) {
              const candidate = lowerVoiceOctave * 12 + tone
              const newInterval = Math.abs(adjusted[i] - candidate) % 12

              if (newInterval !== 7 && newInterval !== 0) {
                adjusted[j] = candidate
                console.log(
                  `[v0] Avoided direct ${currentInterval === 7 ? "fifth" : "octave"} between voices ${i} and ${j}`,
                )
                break
              }
            }
          }
        }
      }
    }
  }

  return adjusted
}
