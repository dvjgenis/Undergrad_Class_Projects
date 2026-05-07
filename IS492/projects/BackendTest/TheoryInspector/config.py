from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TheoryInspectorConfig:
    project_root: Path
    knowledge_base_dir: Path
    inspector_dir: Path
    index_dir: Path
    chunks_csv: Path
    chroma_dir: Path
    env_file: Path
    tools_dir: Path

    @staticmethod
    def from_project_root(project_root: Path) -> "TheoryInspectorConfig":
        inspector_dir = project_root / "TheoryInspector"
        index_dir = inspector_dir / "index"
        tools_dir = project_root / "tools"
        return TheoryInspectorConfig(
            project_root=project_root,
            knowledge_base_dir=project_root / "knowledge_base",
            inspector_dir=inspector_dir,
            index_dir=index_dir,
            chunks_csv=index_dir / "theory_chunks.csv",
            chroma_dir=index_dir / "chroma_db",
            env_file=project_root / ".env",
            tools_dir=tools_dir,
        )

