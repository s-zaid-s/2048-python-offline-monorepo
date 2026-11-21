import socket
import tempfile
import unittest
from pathlib import Path
from game2048_app.bootstrap import build_offline_runtime
from game2048_client.client import Game2048Client
from game2048_client.transport import InProcessTransport, StdioSubprocessTransport
from game2048_contracts.schemas import Direction
from game2048_observability.network_guard import NetworkBlockedError, OfflineNetworkGuard


class TestOfflineEndToEndFlow(unittest.TestCase):
    def test_full_game_flow_under_network_guard(self) -> None:
        with OfflineNetworkGuard(), tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(NetworkBlockedError):
                socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            rt = build_offline_runtime(storage_dir=tmp)
            client = Game2048Client(InProcessTransport(rt.service))
            created = client.new_game("player-1", seed=42)
            self.assertTrue(created.ok)
            gid = created.state["game_id"]

            for idx, d in enumerate([Direction.LEFT, Direction.DOWN, Direction.RIGHT, Direction.UP], start=1):
                res = client.move("player-1", gid, d, seed=idx)
                self.assertTrue(res.ok)

            self.assertTrue(client.undo("player-1", gid).ok)
            self.assertTrue(client.leaderboard("player-1").ok)
            self.assertEqual(len(rt.journal.list_all()), 7)
            self.assertGreaterEqual(rt.metrics.snapshot()["counters"]["cache.hit"], 4)
            self.assertIn("instruction.handled", rt.logger.dump_jsonl())
            client.close()

    def test_stdio_subprocess_client_offline(self) -> None:
        root = Path(__file__).resolve().parents[2]
        pkgs = [
            "game2048_contracts",
            "game2048_domain",
            "game2048_observability",
            "game2048_storage",
            "game2048_app",
            "game2048_client",
        ]
        paths = [str(root / "packages" / p / "src") for p in pkgs]
        with OfflineNetworkGuard():
            client = Game2048Client(StdioSubprocessTransport(python_paths=paths))
            try:
                res = client.new_game("ipc-player", seed=7)
                self.assertTrue(res.ok)
                mv = client.move("ipc-player", res.state["game_id"], Direction.LEFT, seed=8)
                self.assertTrue(mv.ok)
            finally:
                client.close()
