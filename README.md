# 2048 Python-Only Offline Monorepo

A strictly offline, zero-network-call **pure-Python monorepo** built with **SOLID** principles and zero third-party runtime dependencies (Python 3.10+ standard library only).

## Key Capabilities
- **Guaranteed Zero-Network Execution**: `game2048_observability.network_guard.OfflineNetworkGuard` intercepts `socket.socket` during tests and offline runs to guarantee zero network calls.
- **Complete 2048 Domain Rules**: Configurable square grid (default 4×4), deterministic seeded 90%/10% (`2`/`4`) spawning, single-merge-per-tile sliding in all 4 directions, no-op move rejection, score & best-score tracking, win detection (`2048`) with `CONTINUE` mode, game-over detection, and multi-turn `UNDO` stack.
- **Production Backend Patterns (Simulated Offline)**:
  - Append-only **Request Journal** (`InMemoryRequestJournal`) recording every incoming player instruction and outcome.
  - **LRU/TTL Cache** + **Write-Through Repository** (`CachedGameRepository`) with hit/miss/eviction telemetry.
  - **Simulated Datastores** (`InMemoryGameStore`, `JsonFileGameStore`, `InMemoryLeaderboardStore`).
  - **Structured JSON Logging** with correlation IDs and **In-Memory Metrics** (counters, gauges, timings).
- **Decoupled Python Client SDK**: `game2048_client` offers both `InProcessTransport` (direct offline testing) and `StdioSubprocessTransport` (process-isolated local stdio IPC, zero sockets).

## Monorepo Layout
```text
├── roadmap.md                         # 50-ticket Python roadmap (3–4h each, London English prompts)
├── docs/ARCHITECTURE.md               # SOLID design, offline guarantees & end-to-end flow
├── packages/
│   ├── game2048_contracts/            # Wire DTOs, command/response envelopes & payload validation
│   ├── game2048_domain/               # Pure 2048 models, SOLID Protocol ports & BoardEngine
│   ├── game2048_observability/        # Structured JSON logger, metrics registry & OfflineNetworkGuard
│   ├── game2048_storage/              # LRU/TTL cache, write-through repo, datastores & request journal
│   ├── game2048_app/                  # Application service, DI bootstrap & stdio IPC runner
│   └── game2048_client/               # Offline Python client SDK + in-process & stdio transports
└── tests/
    ├── unit/                          # Unit tests for rules, cache, datastores & client SDK
    └── e2e/                           # Full offline E2E suite running under OfflineNetworkGuard
```

## Running Tests Offline
```bash
PYTHONPATH=packages/game2048_contracts/src:packages/game2048_domain/src:packages/game2048_observability/src:packages/game2048_storage/src:packages/game2048_app/src:packages/game2048_client/src \
  python3 -m unittest discover -s tests -t . -v
```
