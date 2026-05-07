from pathlib import Path

from TheoryInspector.config import TheoryInspectorConfig
from TheoryInspector.ingest import build_chunks_index


def main() -> None:
    cfg = TheoryInspectorConfig.from_project_root(Path(__file__).resolve().parent.parent)
    out = build_chunks_index(cfg)
    print(f"Built chunks index: {out}")


if __name__ == "__main__":
    main()

