import inspect
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ToolResult:
    tool: str
    status: str
    payload: dict[str, Any]


def _annotation_to_json_type(ann: Any) -> str:
    txt = str(ann)
    if "int" in txt:
        return "integer"
    if "float" in txt:
        return "number"
    if "bool" in txt:
        return "boolean"
    if "list" in txt or "tuple" in txt:
        return "array"
    if "dict" in txt:
        return "object"
    return "string"


def theory_tool(name: str | None = None) -> Callable:
    def _decorator(fn: Callable) -> Callable:
        fn._theory_tool = True  # type: ignore[attr-defined]
        fn._theory_tool_name = name or fn.__name__  # type: ignore[attr-defined]
        return fn

    return _decorator


class MusicTheoryTools:
    """
    Deterministic tool registry wrapper.
    Replace placeholders with full music21-based implementations.
    """

    @theory_tool()
    def analyze_intervals(self, voice1: list[int], voice2: list[int], measure_range: tuple[int, int]) -> ToolResult:
        intervals = [abs(b - a) % 12 for a, b in zip(voice1, voice2)]
        return ToolResult(
            tool="analyze_intervals",
            status="OK",
            payload={
                "measure_range": measure_range,
                "interval_classes": intervals,
            },
        )

    @theory_tool()
    def detect_parallel_motion(self, chord_a: list[int], chord_b: list[int]) -> ToolResult:
        if len(chord_a) != len(chord_b):
            return ToolResult(
                "detect_parallel_motion",
                "WARNING",
                {"parallel": False, "reason": "size_mismatch"},
            )
        parallels = []
        for i in range(len(chord_a)):
            for j in range(i + 1, len(chord_a)):
                int_a = (chord_a[j] - chord_a[i]) % 12
                int_b = (chord_b[j] - chord_b[i]) % 12
                same_dir = (chord_b[i] - chord_a[i]) * (chord_b[j] - chord_a[j]) > 0
                if same_dir and int_a in {0, 7} and int_b == int_a:
                    parallels.append((i, j, int_a))
        # Enharmonic ambiguity can occur without spelling context in MIDI-space.
        status = "WARNING" if parallels else "OK"
        return ToolResult(
            tool="detect_parallel_motion",
            status=status,
            payload={
                "parallel": bool(parallels),
                "pairs": parallels,
                "ambiguity": "Enharmonic spelling unavailable; treat as musical warning if context differs.",
            },
        )

    @theory_tool()
    def get_roman_numeral_analysis(self, measures: list[int]) -> ToolResult:
        # Placeholder deterministic mapping; to be replaced with full symbolic analysis.
        labels = ["I" if m % 4 in {0, 1} else "V" for m in measures]
        return ToolResult("get_roman_numeral_analysis", "OK", {"labels": labels})

    @theory_tool()
    def estimate_key_context(self, measure_window: tuple[int, int]) -> ToolResult:
        # Placeholder deterministic response.
        return ToolResult(
            tool="estimate_key_context",
            status="OK",
            payload={"window": measure_window, "key": "C major", "confidence": 0.9},
        )

    def get_tool_schemas(self) -> list[dict[str, Any]]:
        schemas = []
        for _, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if not getattr(method, "_theory_tool", False):
                continue
            sig = inspect.signature(method)
            properties = {}
            required = []
            for name, param in sig.parameters.items():
                if name == "self":
                    continue
                properties[name] = {"type": _annotation_to_json_type(param.annotation)}
                if param.default is inspect._empty:
                    required.append(name)
            schemas.append(
                {
                    "name": getattr(method, "_theory_tool_name", method.__name__),
                    "description": (method.__doc__ or "").strip() or f"Theory tool: {method.__name__}",
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                }
            )
        return schemas

