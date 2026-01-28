# Implementation Plan: OGS AI Bot

This plan breaks down the development of the OGS bot into logical phases, following the architecture defined in `ARCHITECTURE.md`.

## Phase 1: Core Logic & Board Representation
- [x] Initialize project structure (package layout in `src/`).
- [x] Integrate `sgfmill` for board state and coordinate translation.
- [x] Implement `GameSession` to track game state (board, moves, turn).
- [x] Create a simple `random_gtp.py` script that acts as a GTP-compliant engine.
- [x] **Test:** Unit tests for move validation and coordinate conversion (OGS <-> GTP).

## Phase 2: Bot Interface & GTP Support
- [x] Define the `Bot` abstract base class (standardizing on GTP-like interaction).
- [x] Implement `GTPBot` to manage a subprocess.
- [x] Implement GTP synchronization logic (sending `play` sequences to catch up the engine state).
- [x] **Test:** Integration test between `GameSession` and `GTPBot` using the `random_gtp.py` engine.

## Phase 3: OGS Connectivity (The Network Layer)
- [x] Implement `OGSClient` using `httpx` for REST (authentication, challenges).
- [x] Implement Socket.IO integration for real-time game events.
- [x] Implement coordinate parsing for OGS's specific move formats.
- [x] **Test:** Mocked OGS server tests to verify event handling and move submission.

## Phase 4: Orchestration (The GameManager)
- [x] Implement `GameManager` to route events from `OGSClient` to `GameSessions`.
- [x] Implement game-seeking logic (periodically checking for/creating challenges).
- [x] Implement basic error handling and reconnection logic.
- [x] **Test:** End-to-end "Dry Run" where the bot logs moves without submitting them to OGS.
- [x] **Verification:** Verified core Go logic (Capture, Ko, Suicide, Pass) via `sgfmill` integration. Handicap/scoring deferred to engine.

## Phase 5: KataGo Human SL Integration
- [ ] Configure `GTPBot` specifically for KataGo's Human SL network weights.
- [ ] Optimize engine synchronization for high-concurrency games.
- [ ] Finalize configuration management (API keys, engine paths).

## Phase 6: Refinement & Monitoring
- [ ] Add logging for game outcomes and engine performance.
- [ ] Implement graceful shutdown (finishing current games before exiting).
- [ ] CI/CD: Ensure `ruff` and `mypy` pass on every commit.
