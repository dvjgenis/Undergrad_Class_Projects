from dataclasses import dataclass
from typing import Any

from .retriever import TheoryRetriever
from .score_extractor import extract_tool_inputs
from .settings import LLMSettings
from .tools_registry import MusicTheoryTools


def _enrich_explanation_with_llm(
    base_text: str,
    user_query: str,
    tool_outputs: dict[str, Any],
    snippets: list[str],
    error_code: str,
    llm_settings: LLMSettings,
) -> str | None:
    """
    Optionally enrich explanation with LLM. Returns enriched text or None if disabled/failed.
    LLM receives only context; never MusicXML or edit instructions. Explanation-only.
    """
    if not llm_settings.use_llm_tutor:
        return None
    context = (
        f"User asked: {user_query}\n"
        f"Error code: {error_code}\n"
        f"Tool outputs: {list(tool_outputs.keys())}\n"
        f"Theory excerpts: {' '.join(s[:150] for s in snippets[:2])}\n"
        f"Base explanation: {base_text}"
    )
    prompt = (
        "You are a music theory tutor. Given the context below, provide a concise, "
        "pedagogical explanation (2-4 sentences) for why this passage was flagged. "
        "Cite the theory excerpts. Do NOT suggest specific note changes or edit the score. "
        "Explain only.\n\n" + context
    )
    try:
        if llm_settings.anthropic_api_key and "claude" in llm_settings.tutor_model.lower():
            import anthropic
            client = anthropic.Anthropic(api_key=llm_settings.anthropic_api_key)
            r = client.messages.create(
                model=llm_settings.tutor_model,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            if r.content and len(r.content) > 0:
                return r.content[0].text
        elif llm_settings.openai_api_key and ("gpt" in llm_settings.tutor_model.lower() or "o1" in llm_settings.tutor_model.lower()):
            from openai import OpenAI
            client = OpenAI(api_key=llm_settings.openai_api_key)
            r = client.chat.completions.create(
                model=llm_settings.tutor_model,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            if r.choices and r.choices[0].message.content:
                return r.choices[0].message.content
        elif llm_settings.groq_api_key and "llama" in llm_settings.tutor_model.lower():
            from groq import Groq
            client = Groq(api_key=llm_settings.groq_api_key)
            r = client.chat.completions.create(
                model=llm_settings.tutor_model,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            if r.choices and r.choices[0].message.content:
                return r.choices[0].message.content
    except Exception:
        pass
    return None


@dataclass
class InspectorState:
    musicxml: str
    score_delta: dict[str, Any]
    user_query: str
    context: dict[str, Any]
    intent: str = "EXPLANATION"
    tool_outputs: dict[str, Any] | None = None
    retrieved: list[dict[str, Any]] | None = None
    explanation: dict[str, Any] | None = None


def _leader_node(state: InspectorState) -> InspectorState:
    q = (state.user_query or "").lower()
    if any(k in q for k in ["why", "explain", "red", "flag"]):
        state.intent = "EXPLANATION"
    elif any(k in q for k in ["check", "validate", "is this correct"]):
        state.intent = "VALIDATION"
    else:
        state.intent = "EXPLANATION"
    return state


def _auditor_node(state: InspectorState, tools: MusicTheoryTools) -> InspectorState:
    inputs = extract_tool_inputs(state.musicxml, state.score_delta)
    interval_result = tools.analyze_intervals(
        inputs["voice1"], inputs["voice2"], inputs["measure_range"]
    )
    parallel_result = tools.detect_parallel_motion(
        inputs["chord_a"], inputs["chord_b"]
    )
    key_result = tools.estimate_key_context(inputs["measure_range"])
    rn_result = tools.get_roman_numeral_analysis(inputs["measures"])
    state.tool_outputs = {
        interval_result.tool: {"status": interval_result.status, **interval_result.payload},
        parallel_result.tool: {"status": parallel_result.status, **parallel_result.payload},
        key_result.tool: {"status": key_result.status, **key_result.payload},
        rn_result.tool: {"status": rn_result.status, **rn_result.payload},
    }
    return state


def _rag_node(state: InspectorState, retriever: TheoryRetriever) -> InspectorState:
    error_codes = state.score_delta.get("error_codes", [])
    code = error_codes[0] if error_codes else None
    domain = "tutor" if state.intent == "EXPLANATION" else "auditor"
    query = f"{state.user_query} {code or ''} voice leading harmony"
    state.retrieved = retriever.search(query, top_k=3, domain=domain, error_code=code)
    if not state.retrieved:
        state.retrieved = retriever.search(query, top_k=3, domain=domain)
    return state


def _tutor_node(state: InspectorState, llm_settings: LLMSettings | None = None) -> InspectorState:
    tool_outputs = state.tool_outputs or {}
    retrieved = state.retrieved or []
    snippets = [r.get("text", "")[:220] for r in retrieved]
    sources = [r.get("source_file", "") for r in retrieved]
    error_codes = state.score_delta.get("error_codes", [])
    code = error_codes[0] if error_codes else "GENERAL_THEORY"

    reasoning_steps = [
        f"Step 1: Parsed request intent as {state.intent}.",
        f"Step 2: Checked symbolic tool outputs: {', '.join(tool_outputs.keys())}.",
        f"Step 3: Retrieved {len(retrieved)} grounded theory chunks for {code}.",
    ]
    # Incorporate retrieved theory into explanation (PRD: ante-hoc explainability)
    if snippets:
        excerpt = snippets[0].strip()
        explanation_text = (
            f"This flag is grounded in deterministic symbolic analysis. "
            f"From music theory: {excerpt}"
            + ("..." if len(snippets[0]) > 217 else "")
        )
    else:
        explanation_text = (
            "This flag is grounded in deterministic symbolic analysis and supported by theory sources. "
            "Review the cited excerpts for the rule rationale and stylistic context."
        )
    # Optional LLM enrichment (TI_USE_LLM_TUTOR=true); explanation-only, never edits
    if llm_settings:
        enriched = _enrich_explanation_with_llm(
            explanation_text, state.user_query, tool_outputs, snippets, code, llm_settings
        )
        if enriched:
            explanation_text = enriched
            reasoning_steps.append("Step 4: Enriched with LLM tutor (explanation only).")
    state.explanation = {
        "reasoning_steps": reasoning_steps,
        "text": explanation_text,
        "severity": "major" if code in {"PARALLEL_PERFECT", "VOICE_ORDER"} else "minor",
        "sources": sources,
        "snippets": snippets,
    }
    return state


class TheoryInspectorOrchestrator:
    def __init__(self, retriever: TheoryRetriever, tools: MusicTheoryTools, llm_settings: LLMSettings) -> None:
        self.retriever = retriever
        self.tools = tools
        self.llm_settings = llm_settings
        self._graph = self._build_langgraph_if_available()

    def _build_langgraph_if_available(self):
        """
        LangGraph optional wiring. If package is unavailable, fallback to deterministic flow.
        """
        try:
            from langgraph.graph import END, StateGraph  # type: ignore
        except Exception:
            return None
        graph = StateGraph(InspectorState)
        graph.add_node("leader", _leader_node)
        graph.add_node("auditor", lambda s: _auditor_node(s, self.tools))
        graph.add_node("rag", lambda s: _rag_node(s, self.retriever))
        graph.add_node("tutor", lambda s: _tutor_node(s, self.llm_settings))
        graph.set_entry_point("leader")
        graph.add_edge("leader", "auditor")
        graph.add_edge("auditor", "rag")
        graph.add_edge("rag", "tutor")
        graph.add_edge("tutor", END)
        return graph.compile()

    def run(
        self,
        *,
        musicxml: str,
        score_delta: dict[str, Any],
        user_query: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        state = InspectorState(
            musicxml=musicxml,
            score_delta=score_delta,
            user_query=user_query,
            context=context,
        )
        if self._graph is not None:
            state = self._graph.invoke(state)
        else:
            state = _leader_node(state)
            state = _auditor_node(state, self.tools)
            state = _rag_node(state, self.retriever)
            state = _tutor_node(state, self.llm_settings)
        return {
            "explanation": state.explanation or {},
            "tool_outputs": state.tool_outputs or {},
            "retrieved": state.retrieved or [],
            "models": {
                "leader": self.llm_settings.leader_model,
                "auditor": self.llm_settings.auditor_model,
                "tutor": self.llm_settings.tutor_model,
            },
        }

