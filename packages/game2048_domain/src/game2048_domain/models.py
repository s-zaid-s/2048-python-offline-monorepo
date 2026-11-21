from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from game2048_contracts.schemas import GameStatus

Board = tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class GameConfig:
    size: int = 4
    win_tile: int = 2048
    max_undo: int = 20


@dataclass(frozen=True)
class GameSnapshot:
    board: Board
    score: int
    moves: int
    status: GameStatus


@dataclass(frozen=True)
class GameState:
    game_id: str
    player_id: str
    board: Board
    score: int = 0
    best_score: int = 0
    moves: int = 0
    status: GameStatus = GameStatus.IN_PROGRESS
    continued_after_win: bool = False
    version: int = 1
    config: GameConfig = field(default_factory=GameConfig)
    history: tuple[GameSnapshot, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "game_id": self.game_id,
            "player_id": self.player_id,
            "board": [list(row) for row in self.board],
            "score": self.score,
            "best_score": self.best_score,
            "moves": self.moves,
            "status": self.status.value,
            "continued_after_win": self.continued_after_win,
            "version": self.version,
            "max_tile": max(max(row) for row in self.board),
            "undo_available": len(self.history),
        }


@dataclass(frozen=True)
class MoveOutcome:
    board: Board
    moved: bool
    score_delta: int
    won_now: bool
    game_over: bool
