import tempfile
import unittest
from game2048_domain.models import GameState
from game2048_observability.metrics import InMemoryMetricsRegistry
from game2048_storage.cache import CachedGameRepository, LruTtlCache
from game2048_storage.datastore import InMemoryLeaderboardStore, JsonFileGameStore


class TestStorageAndCache(unittest.TestCase):
    def test_lru_eviction_and_write_through_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = JsonFileGameStore(tmp)
            cache = LruTtlCache(max_size=1, default_ttl_seconds=60.0)
            metrics = InMemoryMetricsRegistry()
            repo = CachedGameRepository(store, cache, metrics)

            s1 = GameState("g1", "p1", ((2, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)), score=16)
            s2 = GameState("g2", "p1", ((4, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)), score=32)
            repo.save(s1)
            self.assertEqual(repo.load("g1").score, 16)
            repo.save(s2)
            self.assertEqual(cache.stats()["evictions"], 1)
            self.assertEqual(repo.load("g1").score, 16)

    def test_leaderboard_ordering(self) -> None:
        lb = InMemoryLeaderboardStore()
        lb.update_score("alice", 500)
        lb.update_score("bob", 1200)
        lb.update_score("alice", 300)
        self.assertEqual(lb.get_best_score("alice"), 500)
        self.assertEqual(lb.top(2), [("bob", 1200), ("alice", 500)])
