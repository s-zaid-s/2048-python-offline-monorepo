from __future__ import annotations

from typing import Any
from game2048_contracts.schemas import (
    Direction,
    InstructionCommand,
    InstructionResponse,
    InstructionType,
)
from .transport import ClientTransportPort


class Game2048Client:
    def __init__(self, transport: ClientTransportPort) -> None:
        self._transport = transport
        self._seq = 0
        self._local_cache: dict[str, dict[str, Any]] = {}

    def new_game(self, player_id: str, seed: int | None = None) -> InstructionResponse:
        return self._send(InstructionCommand(self._next_id(), player_id, InstructionType.NEW_GAME, seed=seed))

    def move(self, player_id: str, game_id: str, direction: Direction, seed: int | None = None) -> InstructionResponse:
        return self._send(InstructionCommand(self._next_id(), player_id, InstructionType.MOVE, game_id, direction, seed))

    def undo(self, player_id: str, game_id: str) -> InstructionResponse:
        return self._send(InstructionCommand(self._next_id(), player_id, InstructionType.UNDO, game_id))

    def continue_after_win(self, player_id: str, game_id: str) -> InstructionResponse:
        return self._send(InstructionCommand(self._next_id(), player_id, InstructionType.CONTINUE, game_id))

    def leaderboard(self, player_id: str) -> InstructionResponse:
        return self._send(InstructionCommand(self._next_id(), player_id, InstructionType.GET_LEADERBOARD))

    def cached_state(self, game_id: str) -> dict[str, Any] | None:
        return self._local_cache.get(game_id)

    def close(self) -> None:
        self._transport.close()

    def _send(self, cmd: InstructionCommand) -> InstructionResponse:
        res = self._transport.send(cmd)
        if res.ok and res.state:
            self._local_cache[res.state["game_id"]] = res.state
        return res

    def _next_id(self) -> str:
        self._seq += 1
        return f"py-req-{self._seq}"
