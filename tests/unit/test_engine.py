import unittest
from game2048_contracts.schemas import Direction, GameStatus
from game2048_domain.engine import BoardEngine, DeterministicRng
from game2048_domain.models import GameConfig, GameState


class TestBoardEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = BoardEngine()

    def test_single_merge_per_tile_all_directions(self) -> None:
        st = GameState("g1", "p1", ((2, 2, 2, 2), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)))
        nxt, out = self.engine.apply_move(st, Direction.LEFT, DeterministicRng(1))
        self.assertTrue(out.moved)
        self.assertEqual(out.score_delta, 8)
        self.assertEqual(nxt.board[0][:2], (4, 4))

        st_d = GameState("g2", "p1", ((2, 0, 0, 0), (2, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)))
        nxt_d, out_d = self.engine.apply_move(st_d, Direction.DOWN, DeterministicRng(1))
        self.assertEqual(nxt_d.board[3][0], 4)
        self.assertEqual(out_d.score_delta, 4)

    def test_noop_move_does_not_spawn_tile(self) -> None:
        board = ((2, 4, 8, 16), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0))
        st = GameState("g3", "p1", board)
        nxt, out = self.engine.apply_move(st, Direction.UP, DeterministicRng(2))
        self.assertFalse(out.moved)
        self.assertEqual(nxt.board, board)

    def test_win_undo_and_game_over(self) -> None:
        st = GameState("g4", "p1", ((1024, 1024, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)), config=GameConfig())
        won, out = self.engine.apply_move(st, Direction.LEFT, DeterministicRng(3))
        self.assertTrue(out.won_now)
        self.assertEqual(won.status, GameStatus.WON)
        self.assertEqual(self.engine.undo(won).board, st.board)
        locked = ((2, 4, 2, 4), (4, 2, 4, 2), (2, 4, 2, 4), (4, 2, 4, 2))
        self.assertFalse(self.engine.has_valid_moves(locked))
