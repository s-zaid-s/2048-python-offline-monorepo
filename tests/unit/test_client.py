import unittest
from game2048_app.bootstrap import build_offline_runtime
from game2048_client.client import Game2048Client
from game2048_client.transport import InProcessTransport
from game2048_contracts.schemas import Direction


class TestOfflineClient(unittest.TestCase):
    def test_in_process_client_updates_local_cache(self) -> None:
        rt = build_offline_runtime()
        client = Game2048Client(InProcessTransport(rt.service))
        created = client.new_game("alice", seed=10)
        self.assertTrue(created.ok)
        gid = created.state["game_id"]
        moved = client.move("alice", gid, Direction.LEFT, seed=11)
        self.assertTrue(moved.ok)
        self.assertEqual(client.cached_state(gid)["version"], moved.state["version"])
        client.close()
