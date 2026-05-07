import type { GlobalPlanParams, GlobalSkeleton, SeededRandom } from "./types"

export interface GlobalPlanner {
  planUrsatz(params: GlobalPlanParams): GlobalSkeleton
}

export class DefaultGlobalPlanner implements GlobalPlanner {
  private readonly rng: SeededRandom

  constructor(rng: SeededRandom) {
    this.rng = rng
  }

  planUrsatz(params: GlobalPlanParams): GlobalSkeleton {
    const urlinieOptions = [
      [2, 1, 0], // 3-2-1
      [4, 3, 2, 1, 0], // 5-4-3-2-1
    ]
    const urlinieDegrees = urlinieOptions[Math.floor(this.rng.next() * urlinieOptions.length)]
    const cadenceIndex = Math.max(0, Math.floor(params.lengthInBeats) - 1)
    const midCadenceIndex = Math.max(0, Math.floor(params.lengthInBeats / 2) - 1)

    return {
      keyRoot: params.keyRoot,
      mode: params.mode,
      ursatz: ["I", "V", "I"],
      urlinieDegrees,
      cadenceMap: [
        {
          index: midCadenceIndex,
          type: "HC",
          target: "V",
        },
        {
          index: cadenceIndex,
          type: "PAC",
          target: "I",
        },
      ],
    }
  }
}
