from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


class StructuredJsonLogger:
    def __init__(self, service: str = "game2048-backend") -> None:
        self._service = service
        self.records: list[dict[str, Any]] = []

    def _emit(self, level: str, event: str, **fields: Any) -> None:
        self.records.append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "service": self._service,
            "event": event,
            **fields,
        })

    def info(self, event: str, **fields: Any) -> None:
        self._emit("INFO", event, **fields)

    def warning(self, event: str, **fields: Any) -> None:
        self._emit("WARNING", event, **fields)

    def error(self, event: str, **fields: Any) -> None:
        self._emit("ERROR", event, **fields)

    def dump_jsonl(self) -> str:
        return "\n".join(json.dumps(r, sort_keys=True) for r in self.records)
