from __future__ import annotations

import json
import sys
from dataclasses import dataclass

from game2048_contracts.schemas import command_from_dict, response_to_dict
from game2048_domain.engine import BoardEngine
from game2048_observability.logger import StructuredJsonLogger
from game2048_observability.metrics import InMemoryMetricsRegistry
from game2048_observability.network_guard import OfflineNetworkGuard
from game2048_storage.cache import CachedGameRepository, LruTtlCache
from game2048_storage.datastore import InMemoryGameStore, InMemoryLeaderboardStore, JsonFileGameStore
from game2048_storage.journal import InMemoryRequestJournal
from .service import GameApplicationService


@dataclass
class OfflineRuntime:
    service: GameApplicationService
    cache: LruTtlCache
    leaderboard: InMemoryLeaderboardStore
    journal: InMemoryRequestJournal
    logger: StructuredJsonLogger
    metrics: InMemoryMetricsRegistry


def build_offline_runtime(storage_dir: str | None = None) -> OfflineRuntime:
    logger = StructuredJsonLogger()
    metrics = InMemoryMetricsRegistry()
    cache = LruTtlCache(max_size=256, default_ttl_seconds=300.0)
    backing = JsonFileGameStore(storage_dir) if storage_dir else InMemoryGameStore()
    repo = CachedGameRepository(backing, cache, metrics)
    leaderboard = InMemoryLeaderboardStore()
    journal = InMemoryRequestJournal()
    service = GameApplicationService(BoardEngine(), repo, leaderboard, journal, logger, metrics)
    return OfflineRuntime(service, cache, leaderboard, journal, logger, metrics)


def run_stdio_loop(storage_dir: str | None = None) -> None:
    runtime = build_offline_runtime(storage_dir=storage_dir)
    with OfflineNetworkGuard():
        for raw_line in sys.stdin:
            line = raw_line.strip()
            if not line:
                continue
            cmd = command_from_dict(json.loads(line))
            res = runtime.service.handle(cmd)
            sys.stdout.write(json.dumps(response_to_dict(res)) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_stdio_loop()
