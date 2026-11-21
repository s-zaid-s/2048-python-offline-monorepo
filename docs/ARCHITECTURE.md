# Architecture & SOLID Design

## End-to-End Offline Request Flow
```text
[game2048_client.Game2048Client]
       │ (InProcessTransport OR StdioSubprocessTransport — ZERO network sockets)
       ▼
[game2048_app.service.GameApplicationService]
       ├── 1. Validate command DTO -> game2048_contracts.schemas
       ├── 2. Load state via L1 Write-Through Cache -> CachedGameRepository -> GameStore
       ├── 3. Apply pure 2048 rules -> game2048_domain.engine.BoardEngine
       ├── 4. Persist updated state, refresh cache & update LeaderboardStore
       ├── 5. Append audit entry -> RequestJournalStore
       ├── 6. Emit structured JSON logs (correlation_id) + latency/counter metrics
       └── 7. Return deterministic InstructionResponse envelope
```

## SOLID Principles Applied
1. **Single Responsibility (SRP)**:
   - `BoardEngine` only evaluates pure 2048 transitions.
   - `LruTtlCache` only handles bounded eviction and TTL expiry.
   - `InMemoryRequestJournal` only appends immutable audit entries.
   - `GameApplicationService` only orchestrates application workflow.
2. **Open/Closed (OCP)**:
   - Tile spawning (`SpawnPolicyPort`), persistence (`GameStorePort`), caching (`CachePort`), and client transports (`ClientTransportPort`) are open for new implementations without modifying existing orchestration code.
3. **Liskov Substitution (LSP)**:
   - `InMemoryGameStore`, `JsonFileGameStore`, and `CachedGameRepository` are strictly interchangeable wherever `GameStorePort` is required.
   - `InProcessTransport` and `StdioSubprocessTransport` are interchangeable behind `ClientTransportPort`.
4. **Interface Segregation (ISP)**:
   - Ports are split into small, focused `typing.Protocol` interfaces (`RngPort`, `SpawnPolicyPort`, `CachePort`, `GameStorePort`, `LeaderboardPort`, `RequestJournalPort`, `LoggerPort`, `MetricsPort`).
5. **Dependency Inversion (DIP)**:
   - Core business logic and services depend exclusively on abstract `Protocol` ports; concrete adapters are wired solely in `game2048_app.bootstrap`.

## Package Dependency Direction
```text
game2048_contracts  (zero internal deps)
       ▲
game2048_domain     (depends only on contracts)
       ▲
game2048_observability & game2048_storage (depend on domain/contracts)
       ▲
game2048_app        (composition root wiring all concrete adapters)
       ▲
game2048_client     (depends on contracts; optionally wraps app via transport)
```
