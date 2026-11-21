from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class InMemoryRequestJournal:
    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def append(self, record: dict[str, Any]) -> None:
        self._entries.append({
            "seq": len(self._entries) + 1,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            **record,
        })

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._entries)
