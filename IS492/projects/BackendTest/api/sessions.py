from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Session:
    session_id: str
    original_xml: str = ""
    harmonized_xml: str = ""
    instruments: list[str] = field(default_factory=list)
    mood: str = "major"
    genre: str = "classical"
    difficulty: str = "intermediate"
    meta: dict[str, Any] = field(default_factory=dict)


class SessionStore:
    def __init__(self) -> None:
        self._store: dict[str, Session] = {}

    def create(self, original_xml: str, **kwargs: Any) -> Session:
        sid = uuid.uuid4().hex[:12]
        sess = Session(session_id=sid, original_xml=original_xml, **kwargs)
        self._store[sid] = sess
        return sess

    def get(self, session_id: str) -> Session | None:
        return self._store.get(session_id)

    def update(self, session_id: str, **kwargs: Any) -> Session | None:
        sess = self._store.get(session_id)
        if sess is None:
            return None
        for k, v in kwargs.items():
            if hasattr(sess, k):
                setattr(sess, k, v)
        return sess
