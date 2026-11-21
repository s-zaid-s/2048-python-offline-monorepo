from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class Direction(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class InstructionType(str, Enum):
    NEW_GAME = "NEW_GAME"
    MOVE = "MOVE"
    UNDO = "UNDO"
    CONTINUE = "CONTINUE"
    GET_STATE = "GET_STATE"
    GET_LEADERBOARD = "GET_LEADERBOARD"


class GameStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    WON = "WON"
    GAME_OVER = "GAME_OVER"


@dataclass(frozen=True)
class InstructionCommand:
    request_id: str
    player_id: str
    action: InstructionType
    game_id: str | None = None
    direction: Direction | None = None
    seed: int | None = None
    correlation_id: str | None = None


@dataclass(frozen=True)
class InstructionResponse:
    request_id: str
    correlation_id: str
    ok: bool
    state: dict[str, Any] | None = None
    leaderboard: list[dict[str, Any]] | None = None
    moved: bool | None = None
    score_delta: int = 0
    error: str | None = None


def command_to_dict(cmd: InstructionCommand) -> dict[str, Any]:
    return {
        "request_id": cmd.request_id,
        "player_id": cmd.player_id,
        "action": cmd.action.value,
        "game_id": cmd.game_id,
        "direction": cmd.direction.value if cmd.direction else None,
        "seed": cmd.seed,
        "correlation_id": cmd.correlation_id,
    }


def command_from_dict(data: dict[str, Any]) -> InstructionCommand:
    return InstructionCommand(
        request_id=str(data["request_id"]),
        player_id=str(data["player_id"]),
        action=InstructionType(data["action"]),
        game_id=data.get("game_id"),
        direction=Direction(data["direction"]) if data.get("direction") else None,
        seed=data.get("seed"),
        correlation_id=data.get("correlation_id"),
    )


def response_to_dict(res: InstructionResponse) -> dict[str, Any]:
    return {
        "request_id": res.request_id,
        "correlation_id": res.correlation_id,
        "ok": res.ok,
        "state": res.state,
        "leaderboard": res.leaderboard,
        "moved": res.moved,
        "score_delta": res.score_delta,
        "error": res.error,
    }


def response_from_dict(data: dict[str, Any]) -> InstructionResponse:
    return InstructionResponse(
        request_id=str(data["request_id"]),
        correlation_id=str(data["correlation_id"]),
        ok=bool(data["ok"]),
        state=data.get("state"),
        leaderboard=data.get("leaderboard"),
        moved=data.get("moved"),
        score_delta=int(data.get("score_delta", 0)),
        error=data.get("error"),
    )
