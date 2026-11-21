from __future__ import annotations

import time
from collections import OrderedDict
from typing import Any

from game2048_domain.models import GameState
from game2048_domain.ports import CachePort, GameStorePort, MetricsPort


class LruTtlCache:
    def __init__(self, max_size: int = 256, default_ttl_seconds: float = 300.0) -> None:
        self._max_size = max_size
        self._default_ttl = default_ttl_seconds
        self._items: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, key: str) -> Any | None:
        entry = self._items.get(key)
        if entry is None:
            self._misses += 1
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._items[key]
            self._misses += 1
            return None
        self._items.move_to_end(key)
        self._hits += 1
        return value

    def set(self, key: str, value: Any, ttl_seconds: float | None = None) -> None:
        ttl = self._default_ttl if ttl_seconds is None else ttl_seconds
        expires_at = time.monotonic() + ttl
        if key in self._items:
            self._items.move_to_end(key)
        self._items[key] = (value, expires_at)
        while len(self._items) > self._max_size:
            self._items.popitem(last=False)
            self._evictions += 1

    def delete(self, key: str) -> None:
        self._items.pop(key, None)

    def stats(self) -> dict[str, int]:
        return {
            "size": len(self._items),
            "hits": self._hits,
            "misses": self._misses,
            "evictions": self._evictions,
        }


class CachedGameRepository:
    def __init__(self, backing_store: GameStorePort, cache: CachePort, metrics: MetricsPort) -> None:
        self._store = backing_store
        self._cache = cache
        self._metrics = metrics

    def save(self, state: GameState) -> None:
        self._store.save(state)
        self._cache.set(self._key(state.game_id), state)
        self._metrics.inc("cache.write_through")

    def load(self, game_id: str) -> GameState | None:
        cached = self._cache.get(self._key(game_id))
        if cached is not None:
            self._metrics.inc("cache.hit")
            return cached
        self._metrics.inc("cache.miss")
        loaded = self._store.load(game_id)
        if loaded is not None:
            self._cache.set(self._key(game_id), loaded)
        return loaded

    def delete(self, game_id: str) -> None:
        self._store.delete(game_id)
        self._cache.delete(self._key(game_id))

    @staticmethod
    def _key(game_id: str) -> str:
        return f"game:{game_id}"
