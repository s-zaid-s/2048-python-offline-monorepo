from __future__ import annotations

import random
from game2048_contracts.schemas import Direction, GameStatus
from .models import Board, GameConfig, GameSnapshot, GameState, MoveOutcome
from .ports import RngPort, SpawnPolicyPort


class DeterministicRng:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def random(self) -> float:
        return self._rng.random()

    def choice(self, seq: list[tuple[int, int]]) -> tuple[int, int]:
        return self._rng.choice(seq)


class ClassicSpawnPolicy:
    def __init__(self, four_probability: float = 0.1) -> None:
        self._four_probability = four_probability

    def next_tile(self, rng: RngPort) -> int:
        return 4 if rng.random() < self._four_probability else 2


class BoardEngine:
    def __init__(self, spawn_policy: SpawnPolicyPort | None = None) -> None:
        self._spawn_policy = spawn_policy or ClassicSpawnPolicy()

    def create_board(self, config: GameConfig, rng: RngPort) -> Board:
        board = tuple(tuple(0 for _ in range(config.size)) for _ in range(config.size))
        board = self._spawn_tile(board, rng)
        return self._spawn_tile(board, rng)

    def apply_move(self, state: GameState, direction: Direction, rng: RngPort) -> tuple[GameState, MoveOutcome]:
        if state.status == GameStatus.GAME_OVER:
            return state, MoveOutcome(state.board, False, 0, False, True)
        if state.status == GameStatus.WON and not state.continued_after_win:
            return state, MoveOutcome(state.board, False, 0, False, False)

        slid_board, score_delta = self._slide_board(state.board, direction)
        if slid_board == state.board:
            return state, MoveOutcome(state.board, False, 0, False, not self.has_valid_moves(state.board))

        next_board = self._spawn_tile(slid_board, rng)
        new_score = state.score + score_delta
        new_best = max(state.best_score, new_score)
        max_tile = max(max(row) for row in next_board)
        won_now = (not state.continued_after_win) and (max_tile >= state.config.win_tile)
        game_over = not self.has_valid_moves(next_board)

        if game_over and not won_now:
            next_status = GameStatus.GAME_OVER
        elif won_now:
            next_status = GameStatus.WON
        else:
            next_status = GameStatus.IN_PROGRESS

        snapshot = GameSnapshot(state.board, state.score, state.moves, state.status)
        history = (state.history + (snapshot,))[-state.config.max_undo :]
        next_state = GameState(
            game_id=state.game_id,
            player_id=state.player_id,
            board=next_board,
            score=new_score,
            best_score=new_best,
            moves=state.moves + 1,
            status=next_status,
            continued_after_win=state.continued_after_win,
            version=state.version + 1,
            config=state.config,
            history=history,
        )
        return next_state, MoveOutcome(next_board, True, score_delta, won_now, game_over)

    def undo(self, state: GameState) -> GameState:
        if not state.history:
            return state
        prev = state.history[-1]
        return GameState(
            game_id=state.game_id,
            player_id=state.player_id,
            board=prev.board,
            score=prev.score,
            best_score=state.best_score,
            moves=prev.moves,
            status=prev.status,
            continued_after_win=state.continued_after_win,
            version=state.version + 1,
            config=state.config,
            history=state.history[:-1],
        )

    def has_valid_moves(self, board: Board) -> bool:
        n = len(board)
        for r in range(n):
            for c in range(n):
                val = board[r][c]
                if val == 0:
                    return True
                if r + 1 < n and board[r + 1][c] == val:
                    return True
                if c + 1 < n and board[r][c + 1] == val:
                    return True
        return False

    def _slide_board(self, board: Board, direction: Direction) -> tuple[Board, int]:
        rows = [list(r) for r in board]
        if direction == Direction.RIGHT:
            rows = [list(reversed(r)) for r in rows]
        elif direction == Direction.UP:
            rows = [list(col) for col in zip(*rows)]
        elif direction == Direction.DOWN:
            rows = [list(reversed(col)) for col in zip(*rows)]

        total_delta = 0
        merged_rows: list[list[int]] = []
        for row in rows:
            merged, delta = self._merge_left(row)
            merged_rows.append(merged)
            total_delta += delta

        if direction == Direction.RIGHT:
            merged_rows = [list(reversed(r)) for r in merged_rows]
        elif direction == Direction.UP:
            merged_rows = [list(col) for col in zip(*merged_rows)]
        elif direction == Direction.DOWN:
            merged_rows = [list(reversed(r)) for r in merged_rows]
            merged_rows = [list(col) for col in zip(*merged_rows)]

        return tuple(tuple(row) for row in merged_rows), total_delta

    @staticmethod
    def _merge_left(row: list[int]) -> tuple[list[int], int]:
        non_zero = [x for x in row if x != 0]
        result: list[int] = []
        score_delta = 0
        i = 0
        while i < len(non_zero):
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                merged_val = non_zero[i] * 2
                result.append(merged_val)
                score_delta += merged_val
                i += 2
            else:
                result.append(non_zero[i])
                i += 1
        result.extend([0] * (len(row) - len(result)))
        return result, score_delta

    def _spawn_tile(self, board: Board, rng: RngPort) -> Board:
        empties = [(r, c) for r, row in enumerate(board) for c, val in enumerate(row) if val == 0]
        if not empties:
            return board
        r, c = rng.choice(empties)
        grid = [list(row) for row in board]
        grid[r][c] = self._spawn_policy.next_tile(rng)
        return tuple(tuple(row) for row in grid)
