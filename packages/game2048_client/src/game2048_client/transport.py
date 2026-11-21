from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Protocol

from game2048_contracts.schemas import (
    InstructionCommand,
    InstructionResponse,
    command_to_dict,
    response_from_dict,
)


class ClientTransportPort(Protocol):
    def send(self, command: InstructionCommand) -> InstructionResponse: ...
    def close(self) -> None: ...


class InProcessTransport:
    def __init__(self, handler: object) -> None:
        self._handler = handler

    def send(self, command: InstructionCommand) -> InstructionResponse:
        return self._handler.handle(command)  # type: ignore[attr-defined]

    def close(self) -> None:
        return None


class StdioSubprocessTransport:
    def __init__(self, python_paths: list[str] | None = None) -> None:
        env = os.environ.copy()
        if python_paths:
            env["PYTHONPATH"] = os.pathsep.join(python_paths)
        self._proc = subprocess.Popen(
            [sys.executable, "-m", "game2048_app.bootstrap"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

    def send(self, command: InstructionCommand) -> InstructionResponse:
        assert self._proc.stdin is not None and self._proc.stdout is not None
        self._proc.stdin.write(json.dumps(command_to_dict(command)) + "\n")
        self._proc.stdin.flush()
        line = self._proc.stdout.readline()
        return response_from_dict(json.loads(line))

    def close(self) -> None:
        for stream in (self._proc.stdin, self._proc.stdout, self._proc.stderr):
            if stream and not stream.closed:
                stream.close()
        self._proc.wait(timeout=5)
