# 2048 Python-Only Offline Monorepo — Engineering Roadmap

This roadmap details the 50 engineering tickets required to evolve the ~1,000-line pure-Python skeleton into a world-class, zero-network, SOLID backend system.

- **Total Tickets**: 50 (scoped at **3–4 hours each** for an AI programmer)
- **Language & Runtime**: **100% Python** (Python 3.10+ standard library only, zero external runtime dependencies)
- **Hard Constraints**: Strictly **offline-only** (zero network calls, enforced statically and at runtime via `OfflineNetworkGuard`) and strict **SOLID** package boundaries.

---

## Epic 1: Monorepo Architecture, Contracts & Offline Guardrails

### T-01 (tools / monorepo | Est: 3-4 hours)

1. **Title**: Build Zero-Dependency Python Monorepo Workspace Task Runner & Test Harness
2. **Description**: Create a pure-Python monorepo task runner (`tools/workspace.py`) that discovers all `packages/game2048_*` packages, wires `PYTHONPATH` hermetically without touching PyPI, and runs compile checks, unit tests, and E2E suites in one command.
3. **Acceptance criteria**:
   - `python3 tools/workspace.py test` runs all unit and E2E suites with zero warnings and returns exact exit codes.
   - `python3 tools/workspace.py check` compiles all `.py` files with `py_compile` and verifies every package has a valid `pyproject.toml`.
   - Supports filtering by package or suite (`--suite unit`, `--suite e2e`) and outputs a structured JSON summary report.
   - Zero third-party libraries and zero network calls.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Alright mate, first ticket on the board: sort out a proper pure-Python workspace runner under `tools/workspace.py` so nobody's faffing about copying massive `PYTHONPATH` strings by hand. Make it auto-discover all our `packages/game2048_*` packages, run `py_compile` sanity checks, and fire off unit or E2E suites cleanly with zero external installs and zero network calls. Chuck in a JSON summary flag so CI or local scripts can parse the results easy."
5. **Tests to run to prove completion of ticket**:
   - `python3 tools/workspace.py check` exits 0 across all 6 packages.
   - `python3 tools/workspace.py test --suite all` passes every test with zero `ResourceWarning` or error output.

### T-02 (tools / governance | Est: 3-4 hours)

1. **Title**: Implement Python AST-Based SOLID Boundary & Zero-Network Policy Linter
2. **Description**: Build a static analyzer (`tools/arch_lint.py`) using Python's built-in `ast` module that enforces Clean Architecture package boundaries (e.g., `game2048_domain` cannot import `game2048_storage` or `game2048_app`) and bans network-capable imports across production code.
3. **Acceptance criteria**:
   - Reads declarative dependency matrix from `architecture.rules.json`.
   - Parses every `.py` file via `ast.parse` and flags forbidden cross-package imports with exact file path and line number.
   - Bans network imports (`urllib.request`, `http.client`, `requests`, `httpx`, `aiohttp`, `ftplib`, `smtplib`, and raw `socket` outside `network_guard.py`).
   - Exits non-zero on any architectural or offline-policy violation.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Listen bruv, SOLID boundaries only stay clean if we police 'em automatically—otherwise someone's gonna sneak a storage import straight into domain and mash up our clean layering. Write a sharp static linter in `tools/arch_lint.py` using Python's built-in `ast` module backed by `architecture.rules.json`. Block upward package imports AND ban every network library (`urllib.request`, `http.client`, `requests`, `httpx`, raw `socket` outside `network_guard.py`). Give crisp file and line numbers when anything fails."
5. **Tests to run to prove completion of ticket**:
   - `python3 tools/arch_lint.py` exits 0 with zero violations on the clean monorepo.
   - `python3 -m unittest tests/unit/test_arch_lint.py -v` proves synthetic upward imports and forbidden `urllib` imports fail with exact line numbers.

### T-03 (game2048_contracts | Est: 3-4 hours)

1. **Title**: Build Strict Pure-Python Schema Validation & Typed Error Code Registry
2. **Description**: Expand `game2048_contracts` with strict input validation (`validate_command`, `validate_board_matrix`), structured `ValidationIssue` objects, and a standardized machine-readable `ErrorCode` enum shared across backend and client.
3. **Acceptance criteria**:
   - Validates non-empty `request_id`/`player_id`, valid enum values, valid square board matrices, and power-of-two tile invariants (0 or $2^k$).
   - Defines `ErrorCode` enum (`INVALID_INPUT`, `GAME_NOT_FOUND`, `VERSION_CONFLICT`, `INVALID_TRANSITION`, `UNDO_EXHAUSTED`, `IDEMPOTENCY_MISMATCH`, `INTERNAL_ERROR`).
   - `InstructionResponse` carries optional `error_code` alongside human-readable `error`.
   - 100% pure Python stdlib with zero exceptions leaked on malformed input dicts.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Right, we can't rely on loose dicts and raw error strings—that gets proper messy fast. Build a strict pure-Python validation module in `packages/game2048_contracts/src/game2048_contracts/validation.py` plus a canonical `ErrorCode` enum. Validate commands, board matrices (every non-zero tile must be a legit power of two), and required fields, returning clean structured validation issues rather than crashing with ugly `KeyError`s. Keep it dependency-free and rock solid."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_contract_validation.py -v` verifies valid payloads pass and ragged boards, bad tile values (`3`, `-2`), and missing fields fail cleanly.

### T-04 (game2048_observability | Est: 3-4 hours)

1. **Title**: Harden `OfflineNetworkGuard` to Block All Python Socket, Selector & Stdlib HTTP Paths
2. **Description**: Upgrade `OfflineNetworkGuard` in `game2048_observability` to intercept `socket.socket`, `socket.create_connection`, `socket.getaddrinfo`, `urllib.request.urlopen`, and `http.client.HTTPConnection`, with thread-safe re-entrant nesting support.
3. **Acceptance criteria**:
   - Blocks TCP/UDP sockets, DNS lookups (`getaddrinfo`/`gethostbyname`), `urllib.request.urlopen`, and `http.client` connections.
   - Supports nested `with OfflineNetworkGuard():` blocks safely via reference counting and `threading.RLock`.
   - Provides a `is_network_blocked()` status helper for health checks and assertions.
   - Restores all original stdlib references cleanly on outermost context exit.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Our `OfflineNetworkGuard` blocks `socket.socket`, which is a decent start, yeah—but let's lock down every side door too. Upgrade it to block `create_connection`, `getaddrinfo`, `gethostbyname`, `urllib.request.urlopen`, and `http.client.HTTPConnection`, and make it re-entrant and thread-safe so nested `with OfflineNetworkGuard():` blocks don't accidentally unlock the guard early. Chuck in an `is_network_blocked()` helper so health probes can verify isolation at runtime."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_network_guard.py -v` proves DNS, sockets, `urllib`, and `http.client` all raise `NetworkBlockedError`, and nested context exits restore cleanly.

### T-05 (game2048_contracts | Est: 3-4 hours)

1. **Title**: Implement Versioned Envelope Protocol & Legacy Save Schema Upcaster
2. **Description**: Add `schema_version` tracking to wire envelopes and persisted game states, along with a chainable `SchemaMigrator` in `game2048_contracts` to migrate `v1` saves seamlessly into future versions without breaking offline backward compatibility.
3. **Acceptance criteria**:
   - Wire commands, responses, and persisted JSON game states include `schema_version` (default `2`).
   - `SchemaMigrator` upcasts `v1` payloads (without `schema_version` or `error_code`) cleanly to `v2`.
   - Unknown future schema versions raise `UnsupportedSchemaVersionError` clearly.
   - Includes frozen `v1` JSON test fixtures guaranteeing long-term compatibility.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Nobody wants a backend upgrade to brick their saved offline games, init? Add `schema_version` to our contract DTOs and build a clean `SchemaMigrator` pipeline inside `game2048_contracts` that automatically upcasts legacy `v1` payloads to `v2`. Lock a handful of frozen `v1` JSON snapshots into tests so future changes never accidentally break old saves, and reject unknown future versions cleanly."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_schema_migrations.py -v` passes `v1 -> v2` upcasting and rejects `v99` with `UnsupportedSchemaVersionError`.

### T-06 (tools / fixtures | Est: 3-4 hours)

1. **Title**: Create Pure-Python Golden Snapshot & Deterministic Regression Fixture Generator
2. **Description**: Build a Python CLI (`tools/generate_fixtures.py`) that executes deterministic seeded gameplay scenarios against `OfflineRuntime` and writes canonical sorted JSON golden snapshots with `--verify` regression diffing.
3. **Acceptance criteria**:
   - Generates golden snapshots for chain merges, no-op moves, reaching 2048, continuing past 2048, multi-step undo, and locked game-over boards.
   - `--verify` replays all fixtures offline and reports exact field diffs on any mismatch.
   - Byte-for-byte deterministic JSON output (`sort_keys=True`, fixed seeds, stripped volatile timestamps).
   - Runs in under 1 second under `OfflineNetworkGuard`.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Let's lock down our game rules with golden snapshots right from the jump. Build `tools/generate_fixtures.py` in pure Python to run a library of tricky seeded scenarios—double merges, blocked slides, hitting 2048, post-win continue, undo rollbacks, and full deadlocks—and write sorted canonical JSON files. Add a `--verify` mode that replays the lot offline and screams if a single tile or score drifts."
5. **Tests to run to prove completion of ticket**:
   - `python3 tools/generate_fixtures.py --generate` produces identical SHA-256 hashes across back-to-back runs.
   - `python3 tools/generate_fixtures.py --verify` exits 0 against the live engine.

---

## Epic 2: Core 2048 Rules Engine & Domain Modeling

### T-07 (game2048_domain | Est: 3-4 hours)

1. **Title**: Support Configurable Board Geometries (3x3 to 8x8) & Custom Win Targets
2. **Description**: Extend `GameConfig`, `InstructionCommand`, and `BoardEngine` to support validated square grids from `3x3` up to `8x8`, custom power-of-two `win_tile` targets, and configurable `initial_tiles` count.
3. **Acceptance criteria**:
   - `GameConfig` validates `3 <= size <= 8`, `win_tile >= 8` (power of two), and `1 <= initial_tiles <= size * size - 1`.
   - `NEW_GAME` accepts optional `config` overrides and persists them across saves and reloads.
   - All 4 slide directions, score calculations, win checks, and deadlock checks pass across 3×3, 4×4, 5×5, and 6×6 grids.
   - Invalid configurations return `ErrorCode.INVALID_INPUT` without mutating storage.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Right, time to flex Open/Closed in `game2048_domain`. Let players start 3×3 blitz boards or huge 6×6 marathons with custom win targets (like 512 or 4096) and configurable starting tile counts. Validate `GameConfig` strictly—no weird sizes or non-power-of-two targets—and wire config overrides all the way from `NEW_GAME` through storage serialization. Pure Python, zero hacks."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_board_geometry.py -v` passes 3×3, 4×4, 5×5, and 6×6 rules + invalid config rejection.

### T-08 (game2048_domain | Est: 3-4 hours)

1. **Title**: Implement Multi-Step Undo Stack with Per-Game Undo Budget & Anti-Cheese Scoring
2. **Description**: Upgrade `UNDO` mechanics to support `steps: int` (undoing 1..N moves), configurable `max_undos_per_game`, tracked `undos_used`, and strict leaderboard integrity so undoing can never inflate player scores.
3. **Acceptance criteria**:
   - Supports `steps >= 1` up to available history and remaining undo budget.
   - Returns `ErrorCode.UNDO_EXHAUSTED` when history is empty or per-game undo budget is spent.
   - Accurately restores board, score, move count, and game status (`WON` / `GAME_OVER` -> `IN_PROGRESS`).
   - Emits `game.undo` structured log and increments `game.undos.total` metric.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Single-step silent undo is a bit basic, mate—let's make it proper solid. Upgrade `BoardEngine.undo` and `GameApplicationService` so players can roll back `steps` moves at once, track `undos_used` against a configurable `max_undos_per_game` cap, and get a clean `UNDO_EXHAUSTED` error if they're tapped out. Double-check scores and status roll back cleanly so nobody can cheese the leaderboard by spamming undo."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_undo_budget.py -v` verifies multi-step rollback, exhausted budget error, and score/leaderboard accuracy.

### T-09 (game2048_domain | Est: 3-4 hours)

1. **Title**: Create Pluggable Tile Spawn Policies (Classic 90/10, Fair Bag & Adversarial)
2. **Description**: Implement a Strategy-Pattern `SpawnPolicyRegistry` supporting `classic` (90% `2`, 10% `4`), `fair_bag` (deterministic shuffled bag of nine `2`s and one `4`), and `adversarial` (chooses the empty cell and tile value minimizing immediate merges).
3. **Acceptance criteria**:
   - `SpawnPolicyPort` extended cleanly with optional board context and serializable policy state.
   - `FairBagSpawnPolicy` guarantees exact 9:1 tile distribution per 10 spawns and survives save/reload.
   - `AdversarialSpawnPolicy` selects the placement yielding the fewest adjacent equal tiles offline.
   - Selectable per game via `GameConfig.spawn_policy`.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Let's show off proper Strategy Pattern here—don't hardcode `90/10` forever. Build a `SpawnPolicyRegistry` in `game2048_domain` with three pluggable policies: `classic`, `fair_bag` (shuffled bag of nine 2s and one 4 so RNG never feels rigged), and `adversarial` (proper ruthless mode that drops tiles where they block merges). Make sure `fair_bag` state serializes cleanly so reloads stay 100% deterministic."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_spawn_policies.py -v` validates 10,000-spawn distributions for classic & fair_bag and asserts adversarial avoids merging cells.

### T-10 (game2048_domain | Est: 3-4 hours)

1. **Title**: Extract Pluggable `MergeRulePort` with Classic & Fibonacci 2048 Modes
2. **Description**: Decouple tile merging from `BoardEngine` via a `MergeRulePort` protocol (OCP) and deliver two concrete strategies: `ClassicMergeRule` (`a == b -> 2a`) and `FibonacciMergeRule` (adjacent Fibonacci numbers merge to `a + b`, e.g., `1+1=2`, `1+2=3`, `2+3=5`).
3. **Acceptance criteria**:
   - `MergeRulePort` defines `can_merge(a, b)`, `merge_value(a, b)`, and `valid_tile(v)`.
   - `BoardEngine` uses `MergeRulePort` for both `_merge_left` and `has_valid_moves`.
   - `FibonacciMergeRule` handles asymmetric merges in both orders (`1+2=3` and `2+1=3`) and never double-merges in one turn.
   - All classic 2048 unit and E2E tests pass unchanged.
4. **Prompts to give the ai programmer (modern london english)**:
   > "If someone asks for Fibonacci 2048 tomorrow, we shouldn't be ripping up `BoardEngine`. Extract a crisp `MergeRulePort` interface and build `ClassicMergeRule` plus `FibonacciMergeRule`. Watch out for the subtle bit: Fibonacci merges `1+2->3` AND `2+1->3` (and `1+1->2`), so both sliding and deadlock detection have to lean on the injected rule cleanly. Keep classic mode 100% untouched and green."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_merge_rules.py -v` verifies Fibonacci row `[1, 2, 3, 5]` slides LEFT to `[3, 8, 0, 0]` with score delta `11`, plus deadlock checks.

### T-11 (game2048_domain | Est: 3-4 hours)

1. **Title**: Implement Serializable PRNG State & Bit-Exact Cross-Restart Replay
2. **Description**: Store the exact JSON-serializable internal state of `DeterministicRng` inside `GameState` so saving to disk, restarting the Python process, and continuing play yields byte-identical tile spawns to an uninterrupted run.
3. **Acceptance criteria**:
   - `DeterministicRng` implements `export_state() -> dict` and `from_state(dict) -> DeterministicRng` using Python's `random.Random.getstate()`/`setstate()`.
   - `GameState` persists `rng_state` and advances it on every spawned tile.
   - Saving after move 15, recreating `OfflineRuntime` from disk, and playing 35 more moves matches 50 straight moves identically.
   - Corrupted `rng_state` payloads fail safely with a clean validation error.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Right now spinning up a fresh RNG per move without storing RNG state means restarts can drift—allow that nonsense. Upgrade `DeterministicRng` to export and restore JSON-safe state inside `GameState` using Python's built-in `random.Random` state tuples. Prove with a test that playing 15 moves, saving to disk, rebooting the runtime, and playing 35 more moves gives the exact same board as 50 moves straight through."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_rng_replay.py -v` asserts bit-exact equivalence across process restart and tests corrupted RNG state rejection.

### T-12 (game2048_domain | Est: 3-4 hours)

1. **Title**: Enforce Explicit Lifecycle State Machine & Optimistic Concurrency Control
2. **Description**: Introduce `GameLifecycleGuard` (governing `IN_PROGRESS`, `WON`, `GAME_OVER`, `ARCHIVED`) and `expected_version` optimistic locking on mutating commands to reject stale or conflicting updates cleanly.
3. **Acceptance criteria**:
   - Adds `ARCHIVE` instruction and formal transition table rejecting illegal transitions with `ErrorCode.INVALID_TRANSITION`.
   - Commands specifying `expected_version` fail with `ErrorCode.VERSION_CONFLICT` if `state.version != expected_version`.
   - Rejected conflicts never mutate cache, datastore, or leaderboard.
   - Metrics track `requests.conflicts` and `requests.invalid_transitions`.
4. **Prompts to give the ai programmer (modern london english)**:
   > "In a proper backend, two stale moves racing each other will corrupt the board if you don't guard versions. Add optional `expected_version` optimistic locking to commands plus an explicit `GameLifecycleGuard` covering `IN_PROGRESS`, `WON`, `GAME_OVER`, and `ARCHIVED`. If someone sends a stale version, bounce it politely with `VERSION_CONFLICT` and bump `requests.conflicts`—never overwrite newer state."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_lifecycle_concurrency.py -v` verifies stale version rejection, archive lockouts, and metric increments.

### T-13 (game2048_domain | Est: 3-4 hours)

1. **Title**: Build Pure-Python Heuristic Hint Engine & Move Legalizer (`GET_HINT`)
2. **Description**: Implement an offline, side-effect-free `HintEngine` service that evaluates legal directions via weighted board heuristics (empty cells, corner anchoring, monotonicity, smoothness, merge score) and exposes `GET_HINT`.
3. **Acceptance criteria**:
   - `legal_directions(board)` returns exact list of directions that change the board.
   - `HintEngine.recommend(state)` scores each legal move without mutating state or spawning tiles, returning recommended direction + heuristic breakdown.
   - Returns `recommended=None` cleanly on `GAME_OVER` boards.
   - Executes in <2ms on 4×4 boards offline.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Players love a smart hint when they're boxed in—let's build a rapid pure-Python `HintEngine` in `game2048_domain`. Add a `GET_HINT` action that simulates all four directions purely in memory (no mutating state, no spawning tiles), scores each legal move on empty squares, monotonicity, corner weight, and merge gain, and hands back the best move with a crisp rationale. Keep it sub-2ms and 100% side-effect free."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_hint_engine.py -v` confirms `GET_HINT` never picks a no-op move, handles game-over cleanly, and leaves `state.version` untouched.

### T-14 (game2048_domain | Est: 3-4 hours)

1. **Title**: Add Move Combo Statistics, Efficiency Metrics & Detailed Turn Telemetry to `GameState`
2. **Description**: Enrich `GameState` and `MoveOutcome` with rich gameplay stats: total merges, largest single-move combo, empty-cell ratio, no-op attempt count, and exact list of merged coordinates/values for rich UIs and analytics.
3. **Acceptance criteria**:
   - `MoveOutcome` records `merges: tuple[MergeEvent, ...]` (row, col, new_value) and `spawned: SpawnEvent | None`.
   - `GameState` tracks `total_merges`, `best_move_score`, and `noop_attempts`.
   - All new stats serialize cleanly in `to_dict()` and roll back properly on `UNDO`.
   - Zero performance regression on engine move execution.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Let's give our domain engine proper rich turn telemetry so CLIs, bots, and replay debuggers know *exactly* what merged and where the new tile landed. Add `MergeEvent` and `SpawnEvent` details to `MoveOutcome` and track `total_merges`, `best_move_score`, and `noop_attempts` on `GameState`. Make sure `UNDO` restores these counters cleanly too—no half-baked stats."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_turn_telemetry.py -v` verifies exact merge coordinates, spawned tile coordinates, and rollback accuracy on undo.

### T-15 (tests / domain | Est: 3-4 hours)

1. **Title**: Author Pure-Python Property-Based Invariant & Fuzz Test Suite for 2048 Rules
2. **Description**: Write a zero-dependency randomized property-based test suite (`tests/unit/test_invariants.py`) that executes 500+ full seeded games verifying mathematical invariants on every single move.
3. **Acceptance criteria**:
   - Asserts tile sum conservation: `sum(after) == sum(before) + spawned_tile` on every valid move.
   - Asserts monotonic score (`score_after >= score_before`), valid power-of-two tiles, and `2 <= non_zero_tiles <= size*size`.
   - Asserts `has_valid_moves(board) == bool(legal_directions(board))` on every board state.
   - Prints exact reproducing seed and move number on any failure; completes in <3 seconds offline.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Handcrafted unit tests are calm, bruv, but sneaky corner cases hide in random sequences. Build a pure-Python property-based fuzz suite in `tests/unit/test_invariants.py` that hammers `BoardEngine` through 500 full seeded games and asserts every mathematical invariant on every single move—tile sum conservation, score monotonicity, legal-move parity, and zero network calls. If anything trips, print the exact seed so we can reproduce it in a heartbeat."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_invariants.py -v` executes 500 full seeded games (~50,000+ moves) with 0 failures under `OfflineNetworkGuard`.

---

## Epic 3: Simulated Datastores, Multi-Tier Caching & Request Journaling

### T-16 (game2048_storage | Est: 3-4 hours)

1. **Title**: Implement Offline SQLite Datastore Adapters (`SqliteGameStore` & `SqliteLeaderboardStore`)
2. **Description**: Build production-grade local persistence adapters using Python's stdlib `sqlite3` (WAL mode, indexed tables, schema migrations, atomic transactions) implementing `GameStorePort` and `LeaderboardPort`.
3. **Acceptance criteria**:
   - Uses only Python stdlib `sqlite3` with WAL journaling, foreign keys, and parameterized SQL.
   - Implements `GameStorePort` and `LeaderboardPort` with full LSP interchangeability.
   - Provides atomic `save_game_and_score()` transaction helper so game state and leaderboard never diverge.
   - Passes a unified store contract test suite shared by InMemory, JsonFile, and SQLite adapters.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Let's level up our offline datastores using Python's built-in `sqlite3`—still 100% offline, zero external packages. Build `SqliteGameStore` and `SqliteLeaderboardStore` in `game2048_storage/sqlite_store.py` with WAL mode, indexed columns, and clean parameterized queries. Then write a shared store contract test suite running the exact same tests against InMemory, JsonFile, and SQLite to prove Liskov Substitution is watertight."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_store_contracts.py -v` passes all contract assertions across all 3 store implementations.
   - Verify state persists cleanly after closing and reopening the SQLite connection under `OfflineNetworkGuard`.

### T-17 (game2048_storage | Est: 3-4 hours)

1. **Title**: Harden `JsonFileGameStore` with Atomic Write-Rename & Corrupt-File Quarantine
2. **Description**: Upgrade `JsonFileGameStore` so saves write to a sibling `.tmp` file, `os.fsync`, and atomically `os.replace` onto the target path, with checksum verification and corrupt-file quarantine on load.
3. **Acceptance criteria**:
   - Never leaves half-written `.json` files on simulated write failures.
   - Stores SHA-256 content digest in file envelope and verifies integrity on `load()`.
   - Moves corrupted files into a local `.quarantine/` directory and raises a clean `CorruptStateError`.
   - Supports `list_game_ids(player_id=None)` offline directory scanning.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Right now `JsonFileGameStore.save` writes straight over the file—if a crash hits mid-write, the player's save is toast. Harden it with atomic write-to-temp + `fsync` + `os.replace`, wrap payloads with a SHA-256 integrity hash, and quarantine any mangled files into `.quarantine/` with a crisp `CorruptStateError` instead of blowing up unpredictably."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_json_store_durability.py -v` simulates failed writes, corrupted bytes, and quarantine recovery cleanly.

### T-18 (game2048_storage | Est: 3-4 hours)

1. **Title**: Build Multi-Tier L1/L2 Cache Coordinator (Write-Through & Write-Behind)
2. **Description**: Extend `game2048_storage.cache` with a two-tier `MultiTierCache` combining fast in-memory L1 LRU with a local SQLite/file L2 cache tier, supporting automatic L2->L1 promotion and configurable write-through vs write-behind flush modes.
3. **Acceptance criteria**:
   - `MultiTierCache` checks L1 -> L2 -> backing store, promoting L2 hits straight back into L1.
   - Supports `write_through` (immediate persistence) and `write_behind` (batched dirty queue with explicit `flush()`).
   - Independent TTL and capacity limits per tier.
   - Reports granular L1 hits, L2 hits, misses, promotions, and pending dirty count in `stats()`.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Time to make our caching architecture proper world-class. Build `MultiTierCache` in `game2048_storage` pairing our fast in-memory L1 LRU with a local disk/SQLite L2 cache tier. When L1 misses and L2 hits, promote the entry back into L1 automatically. Support both write-through and buffered write-behind with an explicit `flush()` on shutdown, and expose per-tier hit ratios in metrics."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_multitier_cache.py -v` verifies L2->L1 promotion, independent TTL expiry, and write-behind `flush()` durability.

### T-19 (game2048_storage | Est: 3-4 hours)

1. **Title**: Implement Cache Stampede Protection, Versioned Keys & Tag-Based Invalidation
2. **Description**: Harden `game2048_storage.cache` with per-key single-flight locking to prevent thundering-herd reloads, schema-versioned key prefixes, and O(k) tag-based bulk invalidation (e.g., evict all cached games for a `player_id`).
3. **Acceptance criteria**:
   - Single-flight loader ensures N concurrent cache misses for the same `game_id` invoke backing store `load()` exactly once.
   - Tag index (`tags={'player:p1'}`) supports instant `invalidate_tag('player:p1')`.
   - All cache operations are thread-safe under `threading.RLock`.
   - Includes pluggable eviction policies (`LRU`, `LFU`, `FIFO`) implementing `CachePort`.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Cache invalidation and stampedes are where production backends catch fire, so let's engineer them properly. Add per-key single-flight locking to `CachedGameRepository` so 20 concurrent threads missing the same key only hit the datastore once, add versioned key prefixes, and wire up tag-based invalidation so we can clear a player's entire cache in one call. Chuck in LFU and FIFO cache variants behind `CachePort` too for benchmarking."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_cache_hardening.py -v` proves 12 concurrent threads on a cold key execute exactly 1 backing store read and verifies tag invalidation.

### T-20 (game2048_storage | Est: 3-4 hours)

1. **Title**: Build Durable Append-Only Request Journal (WAL) with CRC32 Checksums & Compaction
2. **Description**: Implement `FileRequestJournal` writing fsync'd newline-delimited JSON records with monotonic sequence IDs and `zlib.crc32` checksums, crash-safe truncated-tail recovery, checkpointing, and journal compaction.
3. **Acceptance criteria**:
   - Appends every incoming request + response metadata with `seq`, UTC timestamp, and `crc32` checksum.
   - Detects and safely quarantines a half-written trailing line on startup recovery.
   - `compact(checkpoint_seq)` archives older entries behind a verified state snapshot.
   - `replay_into(service)` reconstructs identical `GameStore` and `LeaderboardStore` state from an empty datastore.
4. **Prompts to give the ai programmer (modern london english)**:
   > "An in-memory journal vanishes the second the process stops—let's build a real offline WAL. Create `FileRequestJournal` in `game2048_storage` writing append-only JSONL with monotonic sequence IDs and `zlib.crc32` checksums. Handle simulated crash recovery (truncated last line), add log compaction behind checkpoints, and write a replay utility proving you can wipe the datastore, replay the journal, and get the exact same boards and leaderboard back."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_durable_journal.py -v` verifies CRC32 tamper detection, truncated-line recovery, compaction, and full state reconstruction.

### T-21 (game2048_app | Est: 3-4 hours)

1. **Title**: Implement Idempotency Store & Duplicate Instruction Deduplication
2. **Description**: Add `IdempotencyPort` (with InMemory and SQLite adapters) and wire deduplication into `GameApplicationService` so retried requests with the same `request_id` return the original response without re-executing moves.
3. **Acceptance criteria**:
   - Same `request_id` + identical canonical command hash returns cached `InstructionResponse` without touching `BoardEngine`.
   - Same `request_id` + different payload returns `ErrorCode.IDEMPOTENCY_MISMATCH`.
   - Records expire cleanly via configurable TTL and purge routine.
   - Metrics increment `requests.idempotent_hits` and `requests.idempotent_mismatches`.
4. **Prompts to give the ai programmer (modern london english)**:
   > "If a client retries a `MOVE` with the same `request_id`, executing it twice would spawn an extra tile and ruin the match. Build an `IdempotencyStore` (both in-memory and SQLite-backed) and plug it straight into `GameApplicationService`. Same `request_id` + same command hash = hand back the exact original reply without touching the board. Same `request_id` + sneaky different payload = reject with `IDEMPOTENCY_MISMATCH`. Proper production hygiene."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_idempotency.py -v` confirms retried `MOVE` executes once, returns identical response, and flags payload mismatches.

### T-22 (game2048_storage | Est: 3-4 hours)

1. **Title**: Build Offline CQRS Read-Model Projections for Player Analytics & Rich Leaderboards
2. **Description**: Implement an offline event projection pipeline (`ProjectionEngine`) consuming journal/domain events to maintain materialized read models: top-N leaderboards, player win rates, highest tile reached, games played, and average score.
3. **Acceptance criteria**:
   - Defines `ProjectionPort` (`apply(event)`, `rebuild(events)`, `snapshot()`).
   - Ships `LeaderboardProjection` and `PlayerStatsProjection` with deterministic tie-breaking.
   - Full `rebuild()` from request journal produces byte-identical read models to incremental live updates.
   - Exposes `GET_PLAYER_STATS` instruction in `game2048_app`.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Let's wire up clean CQRS read models without making it over-engineered. Build a `ProjectionEngine` in `game2048_storage` that maintains `LeaderboardProjection` and `PlayerStatsProjection` (games played, wins, max tile, average score, total merges). Expose `GET_PLAYER_STATS` in `game2048_app`, and prove in tests that rebuilding projections from scratch from the request journal gives the exact same numbers as live updates."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_projections.py -v` compares live projections against full journal rebuild and asserts 100% equality.

### T-23 (game2048_storage | Est: 3-4 hours)

1. **Title**: Build Offline Cache Policy Simulator & Journal Workload Benchmarker
2. **Description**: Create a pure-Python simulation module (`tools/cache_simulator.py`) that replays recorded `.jsonl` request journals against `LRU`, `LFU`, and `FIFO` caches across multiple capacities to quantify hit rates and eviction behavior.
3. **Acceptance criteria**:
   - Replays any local `.jsonl` journal across configurable capacities (e.g., 16, 64, 256, 1024).
   - Compares `LRU`, `LFU`, and `FIFO` hit ratios, eviction counts, and estimated datastore read savings.
   - Outputs clean Markdown comparison tables and machine-readable JSON offline.
   - 100% deterministic and zero external dependencies.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Don't guess cache capacities—measure 'em! Build `tools/cache_simulator.py` in pure Python to replay any local `.jsonl` request journal against our LRU, LFU, and FIFO cache implementations across different sizes (16, 64, 256, 1024). Spit out a crisp Markdown comparison table plus JSON showing hit rates, evictions, and datastore reads saved. Pure offline data-driven engineering."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_cache_simulator.py -v` verifies deterministic simulation output and verifies LRU outperforms FIFO on hot-working-set traces.

---

## Epic 4: Observability, Structured Logging, Monitoring & Health Diagnostics

### T-24 (game2048_observability | Est: 3-4 hours)

1. **Title**: Upgrade Structured Logger with Rotating Local JSONL Files, Contextvars & Redaction
2. **Description**: Enhance `StructuredJsonLogger` with Python `contextvars` automatic `correlation_id` propagation, size-based local file rotation (zero network), log-level filtering, and pluggable field redaction filters.
3. **Acceptance criteria**:
   - Uses `contextvars.ContextVar` so deep domain/storage calls automatically inherit the active `correlation_id` and `request_id`.
   - Supports local rotating `.jsonl` file sinks with configurable `max_bytes` and `backup_count`.
   - Configurable redaction filter masks sensitive keys (e.g., `token`, `secret`) before serialization.
   - Thread-safe writes verified under concurrent local workers.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Right now our logger only stores records in a Python list—let's make it proper production-grade offline logging. Upgrade `StructuredJsonLogger` with `contextvars` so `correlation_id` and `request_id` flow automatically into every nested component, add size-based local JSONL file rotation, configurable minimum log levels, and a field-redaction filter. Make sure concurrent threads never interleave broken JSON lines."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_structured_logger.py -v` tests `contextvars` inheritance, file rotation rollover, redaction, and valid JSONL under multithreading.

### T-25 (game2048_observability | Est: 3-4 hours)

1. **Title**: Implement Dimensional Metrics Registry with P50/P95/P99 Histograms & OpenMetrics Export
2. **Description**: Upgrade `InMemoryMetricsRegistry` to support dimensional tags/labels, exact P50/P95/P99 latency percentiles, sliding-window throughput rates, and offline OpenMetrics/Prometheus text snapshot export.
3. **Acceptance criteria**:
   - Supports labeled counters, gauges, and histograms (e.g., `action='MOVE'`, `tier='L1'`).
   - Computes exact `p50`, `p95`, `p99`, `min`, `max`, and `count` using pure Python stdlib.
   - `export_openmetrics()` generates valid Prometheus/OpenMetrics text format offline.
   - Exposed via `GET_METRICS` instruction in `game2048_app`.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Averages hide tail latency spikes, bruv—we want proper P50, P95, and P99 percentiles. Upgrade `InMemoryMetricsRegistry` to support labeled metrics, thread-safe updates via `RLock`, percentile histograms, and an offline `export_openmetrics()` text exporter (strictly returning a string or writing a local file—no HTTP server!). Wire up `GET_METRICS` so clients and monitoring tools can pull snapshots anytime."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_metrics_percentiles.py -v` validates P50/P95/P99 accuracy on known datasets and verifies OpenMetrics syntax.

### T-26 (game2048_observability | Est: 3-4 hours)

1. **Title**: Build Offline Distributed-Style Span Tracer for End-to-End Request Breakdown
2. **Description**: Create a lightweight pure-Python `OfflineTracer` (`start_span(name)`) recording nested timing spans (`service.handle` -> `cache.load` -> `engine.apply_move` -> `store.save` -> `journal.append`) exportable as Chrome Trace JSON.
3. **Acceptance criteria**:
   - Context-manager API (`with tracer.span('engine.apply_move'):`) records parent-child span hierarchy and microsecond durations.
   - Stores bounded ring-buffer of recent traces in memory (constant memory footprint).
   - Exports traces locally to Chrome Trace Event JSON format for offline flamegraph inspection.
   - Zero overhead when disabled via `NullTracer` (Null Object pattern).
4. **Prompts to give the ai programmer (modern london english)**:
   > "When a move takes longer than expected, we want to see *exactly* whether it was cache, SQLite, or the engine. Build a sleek pure-Python `OfflineTracer` in `game2048_observability` with a `with tracer.span(...)` context manager that captures nested spans in a bounded ring buffer and exports Chrome Trace JSON locally. Include a zero-cost `NullTracer` following the Null Object pattern so tracing can be toggled cleanly."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_offline_tracer.py -v` verifies parent-child span linking, ring-buffer bounding, and valid Chrome Trace JSON output.

### T-27 (game2048_app | Est: 3-4 hours)

1. **Title**: Implement Offline Health Check, Readiness Probe & Self-Diagnostic Doctor CLI
2. **Description**: Add a `HEALTH_CHECK` instruction probing every subsystem (engine sanity, cache R/W, datastore ping, journal writability, active `OfflineNetworkGuard`) plus a `tools/doctor.py` diagnostic CLI.
3. **Acceptance criteria**:
   - Reports per-component status (`UP`, `DEGRADED`, `DOWN`) and overall readiness.
   - Failing cache degrades system to `DEGRADED` (still playable via backing store); failing datastore reports `DOWN`.
   - Explicitly verifies `OfflineNetworkGuard.is_network_blocked()` status.
   - `python3 tools/doctor.py` runs full offline diagnostics and prints a crisp checklist.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Every world-class backend needs a proper health probe—even offline. Wire up a `HEALTH_CHECK` command in `game2048_app` that tests the engine, cache, datastore, journal, and confirms network isolation is active, returning per-component `UP`/`DEGRADED`/`DOWN` statuses. Remember: a broken cache should report `DEGRADED` (still playable), whereas a broken datastore is `DOWN`. Wrap it in a handy `tools/doctor.py` CLI too."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_health_check.py -v` tests healthy `UP`, broken-cache `DEGRADED`, and broken-store `DOWN` states.
   - `python3 tools/doctor.py` exits 0 on a healthy workspace.

### T-28 (game2048_observability | Est: 3-4 hours)

1. **Title**: Build Offline Anomaly Detection & Alerting Engine for Telemetry and Journals
2. **Description**: Create a rule-based `AlertEngine` (`game2048_observability.alerts`) evaluating metrics snapshots and request journals offline to raise alerts on impossible score jumps, cache thrashing, error bursts, and P99 latency spikes.
3. **Acceptance criteria**:
   - Pluggable `AlertRulePort` interface with cooldown/deduplication windows.
   - Ships 4 built-in rules: `ScoreSpikeAnomalyRule`, `CacheThrashRule`, `ErrorRateSpikeRule`, and `P99LatencyRule`.
   - Emits structured `AlertEvent` records to local JSONL or in-memory collector.
   - Zero false positives on normal healthy baseline gameplay.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Collecting metrics is only half the job—we want automated alerting when things go sideways. Build a clean `AlertEngine` in `game2048_observability` with pluggable `AlertRulePort` rules and cooldown timers. Ship four built-in rules: impossible score jumps (anti-cheat), cache thrashing, error-rate spikes, and P99 latency blowouts. Keep it super clean and extensible."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_alerts.py -v` proves every rule triggers on synthetic faults and stays silent on normal gameplay fixtures.

### T-29 (game2048_observability | Est: 3-4 hours)

1. **Title**: Build Live Offline ANSI Terminal Monitoring Dashboard in Pure Python
2. **Description**: Create a zero-dependency pure-Python ANSI terminal dashboard (`tools/monitor_dashboard.py`) displaying live offline telemetry: moves/sec, P50/P95/P99 latency, L1/L2 cache hit rates, journal depth, active alerts, and recent structured logs.
3. **Acceptance criteria**:
   - Separates pure rendering function `render_dashboard(metrics, logs, alerts) -> str` from terminal loop for deterministic unit testing.
   - Color-codes threshold warnings (amber/red) using pure ANSI escape sequences (no `curses` or third-party TUI libs needed).
   - Can run live against a local JSONL/metrics directory or render a single `--once` snapshot.
   - Handles `KeyboardInterrupt` cleanly restoring terminal state.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Let's make monitoring proper visual without dragging in bulky third-party TUI libraries. Build `tools/monitor_dashboard.py` in pure Python using clean ANSI escape codes to show live moves/sec, P50/P95/P99 latencies, L1/L2 cache hit rates, journal size, active alerts, and the last 5 structured log lines. Keep `render_dashboard(...) -> str` completely pure so we can snapshot-test it cleanly without needing an interactive TTY."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_monitor_dashboard.py -v` asserts deterministic rendering output and amber/red threshold highlighting.

---

## Epic 5: Application Pipeline, Middleware & Python Client SDK Ecosystem

### T-30 (game2048_app | Est: 3-4 hours)

1. **Title**: Refactor `GameApplicationService` Around Composable Command Middleware Pipeline
2. **Description**: Extract cross-cutting concerns out of `GameApplicationService.handle()` into an onion-style `CommandMiddlewarePort` pipeline (validation, correlation, metrics timing, tracing, idempotency, journaling, error boundary) for textbook SRP/OCP.
3. **Acceptance criteria**:
   - Defines `CommandMiddlewarePort` (`process(cmd, next_fn) -> InstructionResponse`).
   - Ships standalone middlewares: `ValidationMiddleware`, `CorrelationMiddleware`, `MetricsMiddleware`, `TracingMiddleware`, `IdempotencyMiddleware`, `JournalMiddleware`, and `ErrorBoundaryMiddleware`.
   - Core command handlers live in focused per-action handler classes (`NewGameHandler`, `MoveHandler`, `UndoHandler`, etc.).
   - Middleware execution order is explicitly configurable in `bootstrap.py`.
4. **Prompts to give the ai programmer (modern london english)**:
   > "`GameApplicationService` is starting to wear too many hats—time to clean it up with textbook SRP and OCP. Refactor `game2048_app` around a clean onion-style middleware pipeline (`Validation`, `Correlation`, `Metrics`, `Tracing`, `Idempotency`, `Journal`, `ErrorBoundary`) and split `_dispatch` into focused command handlers via a handler registry. Make sure every existing test stays 100% green."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_middleware_pipeline.py -v` verifies onion execution order, short-circuiting on validation failure, and error-boundary safety.

### T-31 (game2048_app | Est: 3-4 hours)

1. **Title**: Implement Offline Per-Player Rate Limiter (Token Bucket) & Quota Guard Middleware
2. **Description**: Create a pure-Python `TokenBucketRateLimiter` middleware (`game2048_app.rate_limit`) with an injectable clock to simulate backend abuse protection and burst throttling cleanly offline.
3. **Acceptance criteria**:
   - Enforces configurable per-player rate (`refill_per_sec`) and burst capacity (`bucket_size`).
   - Rejects throttled instructions with `ErrorCode.RATE_LIMITED` and `retry_after_ms` metadata.
   - Accepts injectable `ClockPort` so unit tests advance virtual time instantaneously without `time.sleep`.
   - Increments `requests.rate_limited` metric counter.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Even offline, mimicking real backend protections makes this system next-level. Build a pure-Python `TokenBucketRateLimiter` middleware in `game2048_app` with configurable burst and refill rates per `player_id`. When someone spams moves past the limit, reject with `RATE_LIMITED` and `retry_after_ms`. Use an injectable `ClockPort` so our tests simulate time jumps in microseconds rather than sitting through real `time.sleep` calls."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_rate_limiter.py -v` verifies burst allowance, throttling beyond quota, and exact refill recovery using a fake clock.

### T-32 (game2048_app | Est: 3-4 hours)

1. **Title**: Harden Offline Stdio JSON-Lines IPC Loop with Framing, Timeouts & Graceful Shutdown
2. **Description**: Upgrade `run_stdio_loop` in `game2048_app.bootstrap` and `StdioSubprocessTransport` in `game2048_client` with protocol version headers, malformed-JSON resilience, per-request timeout handling, stderr capture, and clean EOF drain.
3. **Acceptance criteria**:
   - Malformed JSON on stdin returns a structured `INVALID_INPUT` JSON response instead of crashing the worker loop.
   - Backend diagnostic prints never corrupt stdout JSON frames (redirected cleanly to stderr or structured logger).
   - `StdioSubprocessTransport` supports configurable per-request `timeout_seconds` raising `TransportTimeoutError`.
   - Cleanly closes all pipes and reaps child processes with zero `ResourceWarning`s.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Let's bulletproof our local stdio IPC bridge between `game2048_client` and `game2048_app`. If a client sends dodgy JSON, don't crash the loop—reply with a clean `INVALID_INPUT` envelope and keep rolling. Add per-request timeouts on `StdioSubprocessTransport`, route all backend warnings away from stdout so frames stay spotless, and verify zero zombie processes or open-pipe warnings on shutdown."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_stdio_ipc.py -v` verifies malformed JSON recovery, timeout errors, multi-request streaming, and clean process teardown.

### T-33 (game2048_client | Est: 3-4 hours)

1. **Title**: Build Fluent `Game2048Client` SDK, `GameSession` Handle & Typed Exception Hierarchy
2. **Description**: Upgrade `game2048_client` into an ergonomic Python SDK featuring context-managed `GameSession` handles (`.left()`, `.right()`, `.up()`, `.down()`, `.undo()`, `.hint()`), typed exceptions mapped from `ErrorCode`, and automatic resource cleanup.
3. **Acceptance criteria**:
   - `with client.start_session('alice', seed=42) as session:` supports fluent directional moves and automatic version tracking.
   - Typed exceptions (`Game2048Error`, `GameNotFoundError`, `VersionConflictError`, `ValidationError`, `RateLimitedError`, `TransportError`) mapped cleanly from `ErrorCode`.
   - Supports both `raise_on_error=True` (ergonomic) and raw `InstructionResponse` inspection modes.
   - Full type annotations passing strict static typing checks.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Make `game2048_client` a proper pleasure for Python devs to use. Build a context-managed `GameSession` wrapper (`session.left()`, `session.down()`, `session.undo()`, `session.hint()`) that tracks `game_id` and `version` automatically, plus a crisp typed exception hierarchy mapped straight from `ErrorCode` so callers can catch `VersionConflictError` or `GameNotFoundError` cleanly instead of parsing strings."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_client_sdk.py -v` covers fluent session gameplay, every typed exception class, and `with` context cleanup.

### T-34 (game2048_client | Est: 3-4 hours)

1. **Title**: Implement Offline Local Python Worker Process Pool (`SubprocessWorkerPoolTransport`)
2. **Description**: Create a multi-process offline transport (`SubprocessWorkerPoolTransport`) managing N local Python backend subprocesses with consistent-hashing affinity by `game_id`, automatic crash respawn, and thread-safe request multiplexing.
3. **Acceptance criteria**:
   - Consistent hash on `game_id` pins each game to a dedicated worker subprocess to maximize L1 cache hit locality.
   - Automatically detects dead worker processes, fails in-flight calls cleanly, and spawns a fresh replacement worker.
   - Exposes pool telemetry (`active_workers`, `restarts`, `requests_per_worker`).
   - Strictly local OS stdio pipes—zero network sockets.
4. **Prompts to give the ai programmer (modern london english)**:
   > "One backend subprocess is sweet for light play, but for heavy offline simulations we want multi-core parallelism without thrashing cache locality. Build `SubprocessWorkerPoolTransport` in `game2048_client` managing N local Python workers pinned by `game_id` hash so each worker's L1 cache stays red-hot. If a worker dies mid-flight, respawn a clean replacement automatically and keep the pool humming—strictly stdio pipes, zero sockets."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_worker_pool.py -v` tests sticky `game_id` routing, 50 concurrent games across 4 workers, and automatic crash respawn.

### T-35 (game2048_client | Est: 3-4 hours)

1. **Title**: Build Client-Side Resilience Layer (Idempotent Retries, Backoff & Circuit Breaker)
2. **Description**: Add composable client resilience decorators in `game2048_client`: retry-with-backoff preserving `request_id` (leveraging backend idempotency), a 3-state `CircuitBreaker` (`CLOSED`, `OPEN`, `HALF_OPEN`), and client-side version-safe LRU caching.
3. **Acceptance criteria**:
   - Retries transient transport errors up to `max_retries` reusing the exact `request_id` so moves never double-execute.
   - Never retries permanent domain errors (`ValidationError`, `GameNotFoundError`).
   - `CircuitBreaker` opens after consecutive failures and probes recovery in `HALF_OPEN` using an injectable clock.
   - Client cache refuses to overwrite a higher `state.version` with an older out-of-order response.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Let's wrap `game2048_client` in proper resilience decorators. Add an idempotent `RetryTransport` (reusing the exact same `request_id` so the backend's idempotency layer prevents double moves!), a 3-state `CircuitBreaker` (`CLOSED`/`OPEN`/`HALF_OPEN`) with an injectable clock, and a version-guarded LRU client cache so out-of-order reads never stomp newer states. Clean Decorator Pattern all the way."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_client_resilience.py -v` proves idempotent retry safety, domain-error pass-through, circuit breaker transitions, and version monotonicity.

### T-36 (game2048_app / plugins | Est: 3-4 hours)

1. **Title**: Design Extensible Python Plugin Registry & Lifecycle Hook System
2. **Description**: Implement a type-safe `PluginRegistry` allowing third-party or internal Python extensions (custom spawn rules, custom telemetry exporters, anti-cheat hooks, custom middlewares) to register via `PluginPort` with isolated error handling.
3. **Acceptance criteria**:
   - Defines `PluginPort` with `name`, `version`, `on_register(runtime)`, `on_command_completed(cmd, res)`, and `on_shutdown()`.
   - Supports configurable `fail_open=True` isolation so a misbehaving analytics plugin never crashes gameplay.
   - Ships two reference plugins: `SlowMoveAuditPlugin` and `HighTileMilestonePlugin`.
   - Demonstrates OCP and DIP cleanly with zero hardcoded plugin references in core packages.
4. **Prompts to give the ai programmer (modern london english)**:
   > "A genuinely extensible backend lets devs plug in new behaviour without hacking core modules. Build a `PluginRegistry` in `game2048_app` with `on_register`, `on_command_completed`, and `on_shutdown` lifecycle hooks plus fail-open error isolation so a dodgy plugin can't crash an active match. Ship two neat sample plugins (`SlowMoveAuditPlugin` and `HighTileMilestonePlugin`) to prove the pattern works cleanly."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_plugins.py -v` tests lifecycle ordering, duplicate plugin rejection, and fail-open exception isolation.

---

## Epic 6: Offline Python CLI, Replay Debugger, AI Bots & Analytics Tools

### T-37 (packages/game2048_cli | Est: 3-4 hours)

1. **Title**: Build Playable Offline Terminal 2048 CLI Package (`game2048_cli`)
2. **Description**: Create a new monorepo package `packages/game2048_cli` powered exclusively by `game2048_client`, featuring ANSI-colored 2048 tiles, keyboard/WASD controls, undo (`u`), hint (`h`), continue (`c`), leaderboard view (`l`), and live cache/score HUD.
3. **Acceptance criteria**:
   - Pure `render_board(state, hud_metrics) -> str` renderer separated from raw TTY input for full unit testability.
   - Distinct ANSI tile colors for `2` through `4096+`, clean box-drawing grid, and `WON`/`GAME_OVER` banners.
   - Supports both in-process and stdio-subprocess transport modes via `--ipc` flag.
   - Zero external packages; 100% offline.
4. **Prompts to give the ai programmer (modern london english)**:
   > "You can't build a world-class 2048 backend and not let people have a proper bash at playing it! Create a new monorepo package `packages/game2048_cli` in pure Python talking exclusively through `game2048_client`. Give each tile power its own slick ANSI colour, wire up WASD/arrows, `u` for undo, `h` for hint, `c` to keep playing past 2048, and a compact HUD showing score and cache hits. Keep `render_board` completely pure for unit testing."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_cli_renderer.py -v` verifies grid layout, ANSI formatting, banners, and key-to-command dispatch.

### T-38 (packages/game2048_cli | Est: 3-4 hours)

1. **Title**: Build Offline Request Journal Inspector & Time-Travel Replay Debugger
2. **Description**: Add a pure-Python replay and audit CLI (`game2048_cli.replay`) that reads local `.jsonl` request journals, filters by `game_id`/`player_id`/`correlation_id`, verifies CRC32 integrity, and steps forward/backward through any game turn-by-turn.
3. **Acceptance criteria**:
   - Reconstructs complete state timeline for any recorded `game_id` deterministically.
   - Supports `step_forward()`, `step_backward()`, `seek(move_index)`, and `diff_turns(a, b)` highlighting merged & spawned cells.
   - Verifies journal CRC32 checksums and highlights tampered or failed entries.
   - Asserts final replayed board and score match the persisted datastore snapshot.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Debugging a weird merge at move 350 by eyeballing raw JSON is proper long. Build a Time-Travel Replay Debugger & Journal Inspector inside `game2048_cli.replay`. Let devs filter local `.jsonl` journals by `game_id`, `player_id`, or `correlation_id`, verify CRC32 integrity, and scrub forward/backward move-by-move with exact tile diffs showing what merged and where the new tile popped up."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_replay_debugger.py -v` verifies forward/backward seeking, cell diffing, checksum error reporting, and final hash parity.

### T-39 (packages/game2048_bots | Est: 3-4 hours)

1. **Title**: Build Pure-Python Offline AI Bot Library (Random, Corner Heuristic & Expectimax)
2. **Description**: Create a new monorepo package `packages/game2048_bots` defining a `PlayerAgentPort` protocol and three offline Python bots (`RandomLegalBot`, `CornerHeuristicBot`, and depth-limited `ExpectimaxBot`) driving the backend via `Game2048Client`.
3. **Acceptance criteria**:
   - `PlayerAgentPort` (`choose_move(state_dict) -> Direction | None`) enables plug-and-play custom bots.
   - `CornerHeuristicBot` outperforms `RandomLegalBot` by >5x average score on fixed seeds.
   - `ExpectimaxBot` (configurable depth 2–3 + transposition cache) achieves high tiles deterministically offline.
   - Includes `play_full_game(client, agent, seed)` runner returning rich match summary.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Let's put our backend through its paces by unleashing Python AI bots on it! Spin up `packages/game2048_bots` with a clean `PlayerAgentPort` interface and three built-in offline bots: `RandomLegalBot`, `CornerHeuristicBot`, and a sharp depth-limited `ExpectimaxBot` with a local transposition table. Drive everything through `Game2048Client` so every bot turn exercises caching, journaling, and scoring end-to-end."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_bots.py -v` proves `CornerHeuristicBot` beats `RandomLegalBot` across 10 fixed seeds and every bot terminates cleanly.

### T-40 (packages/game2048_bots | Est: 3-4 hours)

1. **Title**: Build Offline Multi-Bot Tournament & Simulation Orchestrator
2. **Description**: Create a Python tournament runner (`game2048_bots.tournament`) that runs N bots across M deterministic seeds in parallel via `SubprocessWorkerPoolTransport`, compiling win rates, 2048 rates, score percentiles, and backend latency stats.
3. **Acceptance criteria**:
   - Executes configurable tournament specs (`agents`, `seeds`, `board_size`, `spawn_policy`, `workers`) completely offline.
   - Computes mean, median, max score, highest tile reached, and 2048 win percentage per bot.
   - Captures combined backend throughput and cache hit ratio during the tournament.
   - Exports deterministic Markdown and JSON tournament reports locally.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Now we've got bots and a worker pool, let's build an offline tournament engine (`game2048_bots.tournament`)! Feed it a list of bots, seeds, and board configs, run matches across our local Python worker pool, and spit out a tidy Markdown + JSON tournament report comparing average/median scores, 2048 win rates, max tiles, and backend cache hit ratios. Proper engineering flex."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_tournament.py -v` runs a 2-bot × 6-seed offline tournament and validates deterministic report generation.

### T-41 (game2048_storage / audit | Est: 3-4 hours)

1. **Title**: Build Offline Anti-Cheat & Deterministic Move Transcript Verifier
2. **Description**: Implement `TranscriptVerifier` (`game2048_app.verifier`) that takes a player's submitted transcript (initial seed, config, move sequence, claimed final score/board) and independently validates authenticity in a clean ephemeral offline engine.
3. **Acceptance criteria**:
   - Replays every move deterministically in an isolated in-memory engine with zero side effects on production stores.
   - Pinpoints exact turn index and mismatch reason if score, tile, or move legality was tampered with.
   - Emits a local SHA-256 verification certificate JSON for authentic high-score transcripts.
   - Supports classic, custom grid, and Fibonacci rule variants.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Because our engine is 100% deterministic, we can verify any high-score claim offline with zero trust needed. Build `TranscriptVerifier` in `game2048_app` that takes a seed, config, move list, and claimed final score, replays it in a clean ephemeral engine, and catches any dodgy score edits or illegal moves right down to the exact turn number. Spit out a local SHA-256 verification receipt for legit runs."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_transcript_verifier.py -v` passes authentic runs and catches tampered scores, altered tiles, and forged moves at the exact turn.

### T-42 (tools / reporting | Est: 3-4 hours)

1. **Title**: Build Offline Leaderboard, Player Stats & Audit Report Exporter (JSON / CSV / Markdown)
2. **Description**: Create a pure-Python reporting utility (`tools/export_report.py`) that extracts leaderboard rankings, player stats, cache performance, and journal audit metrics into clean JSON, RFC-4180 CSV, and aligned Markdown tables.
3. **Acceptance criteria**:
   - Uses Python's built-in `csv` and `json` modules—zero external dependencies.
   - Properly escapes special characters in CSV and aligns numeric columns in Markdown tables.
   - Includes top-N leaderboard, win rate, highest tile, cache hit ratio, and total journaled requests.
   - Deterministic output suitable for version-controlled snapshots.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Let's make it dead easy to export clean offline reports straight from our datastores and metrics. Build `tools/export_report.py` in pure Python using stdlib `csv` and `json` to output top leaderboards, player win rates, highest tiles, and cache hit efficiency in JSON, properly-escaped CSV, or crisp Markdown tables. Clean, deterministic, zero third-party deps."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/unit/test_report_exporter.py -v` validates JSON schema, CSV quoting edge cases, and aligned Markdown table output.

---

## Epic 7: E2E Testing, Chaos Engineering, Performance, Docs & Air-Gapped Release

### T-43 (tests / e2e | Est: 3-4 hours)

1. **Title**: Build Comprehensive Offline End-to-End Lifecycle & Restart-Durability Suite
2. **Description**: Expand `tests/e2e/` with exhaustive end-to-end user journeys covering `NEW_GAME`, valid/no-op `MOVE`, `UNDO`, reaching `2048` (`WON`), `CONTINUE`, `GAME_OVER`, `GET_LEADERBOARD`, `GET_PLAYER_STATS`, `GET_METRICS`, and `HEALTH_CHECK` across both InProcess and Stdio transports.
3. **Acceptance criteria**:
   - Runs every scenario under active `OfflineNetworkGuard` across InMemory, JsonFile, and SQLite backing stores.
   - Explicitly tests kill-and-restart durability: closes subprocess, launches a fresh process against the same storage dir, and resumes mid-game seamlessly.
   - Verifies journal sequence continuity, cache hits, and correlation ID presence in logs.
   - Leaves zero temp files or lingering child processes.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Let's prove the entire system works seamlessly from end to end across every transport and datastore. Expand `tests/e2e/test_full_journeys.py` to test full game lifecycles—including hitting 2048, continuing past it, undoing, deadlocking, pulling stats/metrics/health—and killing + restarting the subprocess backend mid-game against SQLite and JSON stores to prove rock-solid disk durability. Keep `OfflineNetworkGuard` clamped on throughout."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/e2e/test_full_journeys.py -v` passes all E2E matrices with zero warnings in under 5 seconds.

### T-44 (tests / e2e | Est: 3-4 hours)

1. **Title**: Build Offline Chaos & Fault-Injection Resilience Test Suite
2. **Description**: Create injectable fault decorators (`FaultInjectingCache`, `FaultInjectingStore`, `FaultInjectingJournal`) and a deterministic chaos suite (`tests/e2e/test_chaos_resilience.py`) simulating cache outages, disk errors, and `SIGKILL` worker crashes.
3. **Acceptance criteria**:
   - Simulated cache outage degrades smoothly to backing store with zero lost moves.
   - Simulated mid-flight worker `SIGKILL` triggers `SubprocessWorkerPoolTransport` respawn + idempotent retry with zero duplicate spawns.
   - Simulated disk-write exception leaves prior persisted save intact (verifying atomic write-rename).
   - 100% deterministic via fixed fault seeds.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Time to break things on purpose so they never break by surprise, init? Build clean Decorator-Pattern fault injectors (`FaultInjectingCache`, `FaultInjectingStore`) and write a deterministic chaos suite in `tests/e2e/test_chaos_resilience.py`. Nuke the cache, `SIGKILL` a worker subprocess mid-turn, and trigger a mid-write disk exception—then assert zero corrupted saves, zero lost scores, and automatic recovery."
5. **Tests to run to prove completion of ticket**:
   - `python3 -m unittest tests/e2e/test_chaos_resilience.py -v` passes all fault-injection and worker-crash recovery tests deterministically.

### T-45 (tools / perf | Est: 3-4 hours)

1. **Title**: Build High-Throughput Offline Load & Latency Benchmark Suite
2. **Description**: Create a pure-Python benchmark suite (`tools/benchmark.py`) measuring moves/sec throughput and P50/P95/P99 latency across cold-cache vs warm-cache, InMemory vs SQLite, and single-process vs multi-worker pools.
3. **Acceptance criteria**:
   - Executes warm-up followed by 5,000+ offline moves across concurrent simulated players.
   - Prints comparative latency & throughput table (InProcess vs Stdio Pool; Cold vs Warm Cache).
   - Supports `--p95-budget-ms` regression gate that exits non-zero if latency regresses.
   - Saves timestamped local JSON benchmark snapshots for trend tracking.
4. **Prompts to give the ai programmer (modern london english)**:
   > "We called this a world-class backend—let's put real numbers on the board! Build `tools/benchmark.py` in pure Python to warm up the runtime, blast 5,000+ offline moves across concurrent players, and compare InProcess vs multi-worker Stdio, cold vs warm cache, and InMemory vs SQLite. Print a clean P50/P95/P99 + moves/sec table and add a `--p95-budget-ms` flag to catch perf regressions automatically."
5. **Tests to run to prove completion of ticket**:
   - `python3 tools/benchmark.py --moves 2000 --workers 2` completes offline under `OfflineNetworkGuard`, prints latency table, and exits 0.

### T-46 (tools / perf | Est: 3-4 hours)

1. **Title**: Build `tracemalloc` Memory Leak & Long-Running Session Soak Harness
2. **Description**: Create an automated offline soak harness (`tools/soak_test.py`) using Python's built-in `tracemalloc` and `gc` modules to run thousands of continuous games while asserting bounded memory growth, bounded cache/buffer sizes, and zero leaked file descriptors.
3. **Acceptance criteria**:
   - Samples `tracemalloc.get_traced_memory()` at fixed intervals across thousands of game lifecycles.
   - Verifies `LruTtlCache`, tracer ring buffers, and compacted journals stay strictly within configured bounds.
   - Asserts zero unclosed file descriptors or leaked subprocess pipes.
   - Provides a fast `--fast` mode (<10s) and configurable extended soak mode.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Nothing kills a long-lived backend sneakier than a slow memory leak in a cache or journal list. Build an offline soak harness in `tools/soak_test.py` powered by Python's built-in `tracemalloc` and `gc`. Churn through thousands of full games, verify heap growth stays flat once caches hit max capacity, and assert zero leaked file descriptors or open pipes. Include a quick `--fast` flag for routine test runs."
5. **Tests to run to prove completion of ticket**:
   - `python3 tools/soak_test.py --fast` passes bounded-memory and zero-FD-leak assertions cleanly.

### T-47 (tools / docs | Est: 3-4 hours)

1. **Title**: Build Zero-Dependency Python AST Documentation & Protocol Reference Generator
2. **Description**: Write a pure-Python documentation generator (`tools/gen_docs.py`) using `inspect`/`ast` to auto-generate up-to-date `docs/PROTOCOL.md` and `docs/API_REFERENCE.md` directly from dataclasses, `Protocol` ports, and docstrings.
3. **Acceptance criteria**:
   - Documents every `InstructionType`, `ErrorCode`, wire DTO schema, and `Protocol` port signature automatically.
   - Includes `--check` mode that exits non-zero if committed docs have drifted from source code.
   - Generates clean, readable Markdown with zero external doc frameworks (no Sphinx/MkDocs downloads needed).
   - 100% deterministic output.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Stale docs are worse than no docs, bruv. Build a zero-dependency Python generator (`tools/gen_docs.py`) using `ast`/`inspect` that extracts every `InstructionType`, `ErrorCode`, dataclass schema, and `Protocol` port across our packages and writes fresh `docs/PROTOCOL.md` and `docs/API_REFERENCE.md`. Add a `--check` flag so we can catch out-of-sync docs straight in our offline checks."
5. **Tests to run to prove completion of ticket**:
   - `python3 tools/gen_docs.py` generates complete Markdown reference docs.
   - `python3 tools/gen_docs.py --check` exits 0 immediately after generation and exits 1 when a doc line is manually edited.

### T-48 (docs / adr | Est: 3-4 hours)

1. **Title**: Author Architectural Decision Records (ADRs), Offline Runbook & ADR Validator
2. **Description**: Create a formal `docs/adr/` directory with at least 6 Architectural Decision Records, an offline operations troubleshooting `docs/RUNBOOK.md`, and a Python validator (`tools/check_adrs.py`) that checks numbering/metadata and updates the ADR index.
3. **Acceptance criteria**:
   - Ships 6 ADRs covering: (1) Pure-Python stdlib-only monorepo layout, (2) Zero-network `OfflineNetworkGuard`, (3) Stdio JSON-lines IPC vs sockets, (4) Multi-tier LRU/SQLite caching strategy, (5) Append-only CRC32 request journal & idempotency, (6) SOLID Ports & Adapters architecture.
   - Ships `docs/RUNBOOK.md` covering corrupt save quarantine recovery, WAL journal replay, cache inspection, and worker crash diagnostics.
   - `python3 tools/check_adrs.py` validates frontmatter, sequential IDs, and keeps `docs/adr/README.md` in sync.
4. **Prompts to give the ai programmer (modern london english)**:
   > "World-class engineering isn't just tidy code—it's leaving crystal-clear records of *why* every big architectural call was made. Write 6 punchy ADRs under `docs/adr/` covering our pure-Python offline split, `OfflineNetworkGuard`, stdio IPC, multi-tier caching, WAL journaling + idempotency, and SOLID ports, plus a practical `docs/RUNBOOK.md`. Add `tools/check_adrs.py` to validate numbering and auto-check the ADR index."
5. **Tests to run to prove completion of ticket**:
   - `python3 tools/check_adrs.py` exits 0 and confirms all 6 ADRs and `docs/adr/README.md` are valid and synced.

### T-49 (tools / release | Est: 3-4 hours)

1. **Title**: Build Air-Gapped Offline Release Packager & SHA-256 Integrity Manifest Tool
2. **Description**: Create a pure-Python release builder (`tools/package_release.py`) that runs preflight gates, strips caches/junk, packages the monorepo into a reproducible offline `.zip` archive, and generates a verifiable `MANIFEST.sha256`.
3. **Acceptance criteria**:
   - Blocks packaging if `arch_lint.py` or unit/E2E tests fail.
   - Excludes `__pycache__`, `.pyc`, temp directories, and build artifacts cleanly.
   - Writes deterministic ZIP timestamps and a `MANIFEST.sha256` covering every packaged file.
   - `--verify <archive>` validates every file hash offline and flags any byte-level tampering.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Let's build a proper air-gapped release packager in `tools/package_release.py` using Python's built-in `zipfile` and `hashlib`. Before cutting an archive, make it verify the SOLID arch linter and test suite are green, strip out all `__pycache__` junk, pack a reproducible `.zip`, and write a `MANIFEST.sha256`. Add a `--verify` flag so anyone unpacking it offline can confirm not a single byte was messed with."
5. **Tests to run to prove completion of ticket**:
   - `python3 tools/package_release.py --out /tmp/dist-test` creates reproducible archive + `MANIFEST.sha256`.
   - `python3 tools/package_release.py --verify /tmp/dist-test` exits 0 on intact bundle and exits 1 if any byte is modified.

### T-50 (tools / certification | Est: 3-4 hours)

1. **Title**: Build Master Offline Acceptance Certification Gate & Zero-Network Audit Sign-Off
2. **Description**: Create the capstone pure-Python certification runner (`tools/certify.py`) executing every quality gate in sequence—AST SOLID linter, `py_compile`, unit/property tests, E2E journeys, chaos resilience, benchmark smoke, soak smoke, doc/ADR sync, and zero-network audit—outputting `CERTIFICATION_REPORT.md`.
3. **Acceptance criteria**:
   - Executes every monorepo verification gate strictly inside `OfflineNetworkGuard`.
   - Runs both static AST network-import scan and runtime network-isolation verification.
   - Produces a detailed `CERTIFICATION_REPORT.md` summarizing gate status, test counts, latency P95, and cache hit ratio.
   - Exits 0 only when 100% of gates pass with zero warnings.
4. **Prompts to give the ai programmer (modern london english)**:
   > "Final ticket, mate—let's bring the whole ting home! Build `tools/certify.py` in pure Python as our master offline acceptance gate. Wire it up to run every single check end-to-end inside `OfflineNetworkGuard`: AST SOLID boundary lint, compile checks, unit + property fuzz tests, full E2E journeys, chaos fault recovery, fast benchmark + soak smoke, doc/ADR sync, and a strict zero-network audit. Spit out a clean `CERTIFICATION_REPORT.md` so we can stamp this backend certified world-class."
5. **Tests to run to prove completion of ticket**:
   - `python3 tools/certify.py` executes every gate offline with zero network calls, exits 0, and generates `CERTIFICATION_REPORT.md`.

---
