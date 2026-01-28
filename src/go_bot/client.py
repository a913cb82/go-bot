import asyncio
import logging
import httpx
import socketio
from typing import Any, Dict, Optional, Callable, Awaitable
from go_bot.coords import gtp_to_ogs, ogs_coords_to_int

logger = logging.getLogger(__name__)


class OGSClient:
    def __init__(self, api_key: str, base_url: str = "https://online-go.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url, headers={"Authorization": f"Bearer {api_key}"}
        )
        self.sio = socketio.AsyncClient()
        self.user_id: Optional[int] = None
        self.username: Optional[str] = None

        # Callbacks
        self.on_game_started: Optional[
            Callable[[Dict[str, Any]], Awaitable[None]]
        ] = None
        self.on_game_move: Optional[
            Callable[[str, Dict[str, Any]], Awaitable[None]]
        ] = None
        self.on_game_ended: Optional[
            Callable[[str, Dict[str, Any]], Awaitable[None]]
        ] = None

        self._setup_socket_events()

    def _setup_socket_events(self) -> None:
        @self.sio.on("connect")  # type: ignore
        async def on_connect() -> None:
            logger.info("Socket.IO connected")
            # Authenticate socket
            await self.sio.emit("authenticate", {"api_key": self.api_key})

        @self.sio.on("disconnect")  # type: ignore
        async def on_disconnect() -> None:
            logger.info("Socket.IO disconnected")

        @self.sio.on("notification")  # type: ignore
        async def on_notification(data: Dict[str, Any]) -> None:
            logger.debug(f"Notification: {data}")

        @self.sio.on("gameStarted")  # type: ignore
        async def on_game_started(data: Dict[str, Any]) -> None:
            if self.on_game_started:
                await self.on_game_started(data)

    async def _handle_game_move(self, game_id: str, data: Dict[str, Any]) -> None:
        if self.on_game_move:
            await self.on_game_move(game_id, data)

    async def connect(self) -> None:
        """Fetch user info and connect Socket.IO."""
        # Get user profile
        resp = await self.client.get("/api/v1/me")
        resp.raise_for_status()
        data = resp.json()
        self.user_id = data["id"]
        self.username = data["username"]
        logger.info(f"Logged in as {self.username} ({self.user_id})")

        # Connect Socket.IO
        await self.sio.connect(
            f"{self.base_url}", transports=["websocket"], socketio_path="/socket.io"
        )

    async def disconnect(self) -> None:
        await asyncio.gather(self.client.aclose(), self.sio.disconnect())

    async def join_game(self, game_id: str) -> None:
        """Connect to a specific game's events."""
        await self.sio.emit("game/connect", {"game_id": game_id})

        @self.sio.on(f"game/{game_id}/move")  # type: ignore
        async def on_move(data: Dict[str, Any]) -> None:
            await self._handle_game_move(game_id, data)

        @self.sio.on(f"game/{game_id}/gamedata")  # type: ignore
        async def on_gamedata(data: Dict[str, Any]) -> None:
            pass

        @self.sio.on(f"game/{game_id}/phase")  # type: ignore
        async def on_phase(data: str) -> None:
            # phase is just a string? or dict? Usually string "play", "finished"
            # Docs are sparse, let's assume if it's "finished" we trigger end
            if data == "finished" or (
                isinstance(data, dict) and data.get("phase") == "finished"
            ):
                # We need more data for outcome, but at least we know it ended
                if self.on_game_ended:
                    await self.on_game_ended(game_id, {"phase": "finished"})

    async def submit_move(self, game_id: str, move_gtp: str, board_size: int) -> None:
        """Submit a move to OGS."""
        row, col = gtp_to_ogs(move_gtp, board_size)
        pos = ogs_coords_to_int(row, col, board_size)

        await self.sio.emit("game/move", {"game_id": game_id, "move": pos})

    async def create_challenge(
        self, board_size: int = 19, time_control: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create an open challenge."""
        payload = {
            "game": {
                "rules": "japanese",
                "handicap": 0,
                "board_size": board_size,
                "komi": 6.5,
                "ranked": True,
            },
            "time_control": time_control
            or {"system": "byoyomi", "main_time": 600, "period_time": 30, "periods": 5},
        }
        resp = await self.client.post("/api/v1/challenges", json=payload)
        resp.raise_for_status()
        logger.info(f"Challenge created: {resp.json().get('id')}")
