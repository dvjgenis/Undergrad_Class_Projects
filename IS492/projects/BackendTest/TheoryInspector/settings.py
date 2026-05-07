import os
from dataclasses import dataclass
from pathlib import Path


def _read_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    data: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip().strip('"').strip("'")
    return data


@dataclass(frozen=True)
class LLMSettings:
    leader_model: str = "llama-3.1-8b-instant"
    auditor_model: str = "gpt-4o-mini"
    tutor_model: str = "claude-3-5-sonnet-latest"
    groq_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    use_llm_tutor: bool = False  # TI_USE_LLM_TUTOR: optional LLM enrichment for explanations


def load_llm_settings(env_file: Path) -> LLMSettings:
    env_map = _read_dotenv(env_file)

    def get(name: str, default: str = "") -> str:
        return os.getenv(name, env_map.get(name, default))

    use_llm = (get("TI_USE_LLM_TUTOR", "false").lower() in ("true", "1", "yes"))
    return LLMSettings(
        leader_model=get("TI_LEADER_MODEL", "llama-3.1-8b-instant"),
        auditor_model=get("TI_AUDITOR_MODEL", "gpt-4o-mini"),
        tutor_model=get("TI_TUTOR_MODEL", "claude-3-5-sonnet-latest"),
        groq_api_key=get("GROQ_API_KEY", ""),
        openai_api_key=get("OPENAI_API_KEY", ""),
        anthropic_api_key=get("ANTHROPIC_API_KEY", ""),
        use_llm_tutor=use_llm,
    )

