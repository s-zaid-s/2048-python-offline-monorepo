from __future__ import annotations

import socket
from types import TracebackType
from typing import Any


class NetworkBlockedError(RuntimeError):
    pass


class OfflineNetworkGuard:
    def __init__(self) -> None:
        self._original_socket: Any = None

    def __enter__(self) -> OfflineNetworkGuard:
        self._original_socket = socket.socket

        def _blocked(*args: Any, **kwargs: Any) -> Any:
            raise NetworkBlockedError("Network calls are strictly forbidden in offline mode.")

        socket.socket = _blocked  # type: ignore[assignment]
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._original_socket is not None:
            socket.socket = self._original_socket
