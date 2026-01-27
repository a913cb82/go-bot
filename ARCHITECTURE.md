# OGS Bot Architecture

This document outlines the architecture for the AI bot system designed to play on [Online-Go.com (OGS)](https://online-go.com).

## Overview

The system handles multiple concurrent games on OGS using a single bot personality. It bridges OGS's Socket.IO protocol with the Go Text Protocol (GTP) used by engines like KataGo.

## Components

### 1. `OGSClient` (Network & Protocol Layer)
- **Responsibility:** Direct communication with OGS.
- **REST API:** Handles authentication and game seeking (creating/accepting challenges).
- **Socket.IO:** Maintains a persistent connection for real-time updates. It translates OGS move coordinates into a standard format and vice versa.
- **Concurrency:** Uses `asyncio` to manage multiple simultaneous game streams.

### 2. `GameManager` (Orchestration Layer)
- **Responsibility:** Manages the lifecycle of all active games and the bot logic.
- **Game Tracking:** Keeps a mapping of `game_id` to `GameSession`.
- **Bot Logic:** Owns a `Bot` instance (e.g., `GTPBot` or `RandomBot`) and uses it to generate moves for all active sessions.
- **Game Seeking:** Implements logic to actively find or create games to ensure the bot is always playing.

### 3. `GameSession` (State Tracking Layer)
- **Responsibility:** Tracks the state of a single game.
- **Board Logic:** Uses `sgfmill` for:
    - Maintaining the current board state.
    - Converting between OGS coordinates and GTP coordinates (e.g., "Q16").
    - Generating SGFs for game records.
- **Clock:** Monitors game time.

### 4. `Bot` (Logic Layer)
- **Responsibility:** Interface for move generation.
- **Implementations:**
    - `GTPBot`: The primary implementation that manages a subprocess speaking the Go Text Protocol (GTP). It handles engine synchronization for multiple games.
    - `RandomGTP`: A minimal GTP-compliant engine (used for testing) that returns random legal moves via GTP, ensuring the `GTPBot` infrastructure is fully exercised.

## Data Flow

1.  **Start:** `GameManager` connects to OGS via `OGSClient`.
2.  **Event Loop:**
    - `OGSClient` receives a move and notifies `GameManager`.
    - `GameManager` updates the relevant `GameSession`.
    - `GameManager` requests a move from its `Bot`.
    - `Bot` returns the move; `OGSClient` sends it to OGS.

## Technologies

- **Language:** Python 3.10+
- **Asynchrony:** `asyncio` for non-blocking I/O.
- **Networking:** `httpx` and `python-socketio`.
- **Go Library:** `sgfmill` (comprehensive SGF and coordinate handling).
- **Engine:** **KataGo** (targeted for Human SL network integration).
- **Quality:** `ruff`, `mypy`, `pytest`.
