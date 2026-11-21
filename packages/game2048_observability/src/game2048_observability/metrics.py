from __future__ import annotations

from collections import defaultdict
from typing import Any


class InMemoryMetricsRegistry:
    def __init__(self) -> None:
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = {}
        self._timings_ms: dict[str, list[float]] = defaultdict(list)

    def inc(self, name: str, value: int = 1) -> None:
        self._counters[name] += value

    def gauge(self, name: str, value: float) -> None:
        self._gauges[name] = value

    def observe_ms(self, name: str, ms: float) -> None:
        self._timings_ms[name].append(ms)

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "timings_avg_ms": {
                k: round(sum(v) / len(v), 4) for k, v in self._timings_ms.items() if v
            },
        }
