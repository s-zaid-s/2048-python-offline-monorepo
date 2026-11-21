from __future__ import annotations

import time
import uuid
from dataclasses import replace

from game2048_contracts.schemas import (
    GameStatus,
    InstructionCommand,
    InstructionResponse,
    InstructionType,
)
from game2048_domain.engine import BoardEngine, DeterministicRng
from game2048_domain.models import GameConfig, GameState
from game2048_domain.ports import (
    GameStorePort,
    LeaderboardPort,
    LoggerPort,
    MetricsPort,
    RequestJournalPort,
)


class GameApplicationService:
    def __init__(
        self,
        engine: BoardEngine,
        game_store: GameStorePort,
        leaderboard: LeaderboardPort,
        journal: RequestJournalPort,
        logger: LoggerPort,
        metrics: MetricsPort,
    ) -> None:
        self._engine = engine
        self._games = game_store
        self._leaderboard = leaderboard
        self._journal = journal
        self._logger = logger
        self._metrics = metrics

    def handle(self, cmd: InstructionCommand) -> InstructionResponse:
        start = time.perf_counter()
        corr_id = cmd.correlation_id or f"corr-{uuid.uuid4().hex[:10]}"
        self._metrics.inc("requests.total")
        self._metrics.inc(f"requests.action.{cmd.action.value.lower()}")

        try:
            response = self._dispatch(cmd, corr_id)
            self._journal.append({
                "request_id": cmd.request_id,
                "correlation_id": corr_id,
                "player_id": cmd.player_id,
                "game_id": cmd.game_id or (response.state["game_id"] if response.state else None),
                "action": cmd.action.value,
                "direction": cmd.direction.value if cmd.direction else None,
                "ok": response.ok,
                "score_delta": response.score_delta,
                "error": response.error,
            })
            self._logger.info("instruction.handled", correlation_id=corr_id, action=cmd.action.value, ok=response.ok)
            return response
        except Exception as exc:  # noqa: BLE001
            self._metrics.inc("requests.errors")
            self._logger.error("instruction.failed", correlation_id=corr_id, error=str(exc))
            return InstructionResponse(cmd.request_id, corr_id, False, error=str(exc))
        finally:
            self._metrics.observe_ms("requests.latency_ms", (time.perf_counter() - start) * 1000.0)

    def _dispatch(self, cmd: InstructionCommand, corr_id: str) -> InstructionResponse:
        if cmd.action == InstructionType.GET_LEADERBOARD:
            top = [{"player_id": p, "score": s} for p, s in self._leaderboard.top(10)]
            return InstructionResponse(cmd.request_id, corr_id, True, leaderboard=top)

        if cmd.action == InstructionType.NEW_GAME:
            rng = DeterministicRng(cmd.seed)
            config = GameConfig()
            game_id = cmd.game_id or f"game-{uuid.uuid4().hex[:8]}"
            board = self._engine.create_board(config, rng)
            best = self._leaderboard.get_best_score(cmd.player_id)
            state = GameState(game_id=game_id, player_id=cmd.player_id, board=board, best_score=best, config=config)
            self._games.save(state)
            return InstructionResponse(cmd.request_id, corr_id, True, state=state.to_dict())

        if not cmd.game_id:
            return InstructionResponse(cmd.request_id, corr_id, False, error="game_id is required")

        state = self._games.load(cmd.game_id)
        if state is None:
            return InstructionResponse(cmd.request_id, corr_id, False, error=f"game not found: {cmd.game_id}")

        if cmd.action == InstructionType.GET_STATE:
            return InstructionResponse(cmd.request_id, corr_id, True, state=state.to_dict())

        if cmd.action == InstructionType.UNDO:
            reverted = self._engine.undo(state)
            self._games.save(reverted)
            return InstructionResponse(cmd.request_id, corr_id, True, state=reverted.to_dict())

        if cmd.action == InstructionType.CONTINUE:
            if state.status == GameStatus.WON:
                state = replace(state, status=GameStatus.IN_PROGRESS, continued_after_win=True, version=state.version + 1)
                self._games.save(state)
            return InstructionResponse(cmd.request_id, corr_id, True, state=state.to_dict())

        if cmd.action == InstructionType.MOVE:
            if cmd.direction is None:
                return InstructionResponse(cmd.request_id, corr_id, False, error="direction is required for MOVE")
            rng = DeterministicRng(cmd.seed)
            next_state, outcome = self._engine.apply_move(state, cmd.direction, rng)
            if outcome.moved:
                best = self._leaderboard.update_score(next_state.player_id, next_state.score)
                next_state = replace(next_state, best_score=best)
                self._games.save(next_state)
                self._metrics.gauge("game.last_score", float(next_state.score))
            return InstructionResponse(
                cmd.request_id, corr_id, True, state=next_state.to_dict(), moved=outcome.moved, score_delta=outcome.score_delta
            )

        return InstructionResponse(cmd.request_id, corr_id, False, error=f"unsupported action: {cmd.action}")
