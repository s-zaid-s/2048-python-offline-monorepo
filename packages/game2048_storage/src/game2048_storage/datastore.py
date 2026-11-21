from __future__ import annotations

import json
from pathlib import Path
from game2048_contracts.schemas import GameStatus
from game2048_domain.models import GameConfig, GameSnapshot, GameState


class InMemoryGameStore:
    def __init__(self) -> None:
        self._records: dict[str, GameState] = {}

    def save(self, state: GameState) -> None:
        self._records[state.game_id] = state

    def load(self, game_id: str) -> GameState | None:
        return self._records.get(game_id)

    def delete(self, game_id: str) -> None:
        self._records.pop(game_id, None)


class JsonFileGameStore:
    def __init__(self, directory: str | Path) -> None:
        self._dir = Path(directory)
        self._dir.mkdir(parents=True, exist_ok=True)

    def save(self, state: GameState) -> None:
        payload = {
            **state.to_dict(),
            "config": {"size": state.config.size, "win_tile": state.config.win_tile, "max_undo": state.config.max_undo},
            "history": [
                {"board": [list(r) for r in h.board], "score": h.score, "moves": h.moves, "status": h.status.value}
                for h in state.history
            ],
        }
        (self._dir / f"{state.game_id}.json").write_text(json.dumps(payload), encoding="utf-8")

    def load(self, game_id: str) -> GameState | None:
        path = self._dir / f"{game_id}.json"
        if not path.exists():
            return None
        d = json.loads(path.read_text(encoding="utf-8"))
        cfg = GameConfig(**d["config"])
        history = tuple(
            GameSnapshot(tuple(tuple(r) for r in h["board"]), h["score"], h["moves"], GameStatus(h["status"]))
            for h in d["history"]
        )
        return GameState(
            game_id=d["game_id"],
            player_id=d["player_id"],
            board=tuple(tuple(r) for r in d["board"]),
            score=d["score"],
            best_score=d["best_score"],
            moves=d["moves"],
            status=GameStatus(d["status"]),
            continued_after_win=d["continued_after_win"],
            version=d["version"],
            config=cfg,
            history=history,
        )

    def delete(self, game_id: str) -> None:
        path = self._dir / f"{game_id}.json"
        if path.exists():
            path.unlink()


class InMemoryLeaderboardStore:
    def __init__(self) -> None:
        self._scores: dict[str, int] = {}

    def update_score(self, player_id: str, score: int) -> int:
        best = max(self._scores.get(player_id, 0), score)
        self._scores[player_id] = best
        return best

    def get_best_score(self, player_id: str) -> int:
        return self._scores.get(player_id, 0)

    def top(self, limit: int = 10) -> list[tuple[str, int]]:
        return sorted(self._scores.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]
