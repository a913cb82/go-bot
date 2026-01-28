import asyncio
import logging
import httpx
import socketio
from typing import Any, Dict, Optional, Callable, Awaitable
from go_bot.coords import gtp_to_ogs, ogs_coords_to_int

logger = logging.getLogger(__name__)


class OGSClient:
    @classmethod
    async def login(
        cls,
        username: str,
        password: str,
        base_url: str = "https://online-go.com",
    ) -> "OGSClient":
        """
        Login with username and password (standard or application-specific).
        Uses OGS login endpoint to get authentication cookies.
        """
        async with httpx.AsyncClient(base_url=base_url) as client:
            payload = {
                "username": username,
                "password": password,
            }
            # OGS login endpoint
            resp = await client.post("/api/v0/login", json=payload)
            if resp.status_code == 401:
                raise ValueError(
                    "OGS Login Failed: Invalid username or password. If using an Application Specific Password, ensure it is correct."
                )
            resp.raise_for_status()

            # For OGS, we need the cookies or an API key.
            # If we login via /api/v0/login, we get cookies.
            # However, the rest of our app expects a 'Bearer' token or API Key.
            # OGS allows generating an API key once logged in.
            # But more simply, we can just use the cookies for subsequent requests.
            # Let's adjust OGSClient to support cookie-based auth or fetch the token.

            # Fetch /api/v1/ui/bot/generateAPIKey or similar if needed,
            # but usually bots just use the API Key from the profile.

            # For now, let's assume we can use the cookies from this session.
            # We'll return an OGSClient that uses these cookies.
            return cls(api_key="", base_url=base_url, cookies=client.cookies)

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://online-go.com",
        cookies: Optional[httpx.Cookies] = None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self.client = httpx.AsyncClient(
            base_url=base_url, headers=headers, cookies=cookies
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
        self.on_game_gamedata: Optional[
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

        # If we logged in via cookies, we might not have an api_key for Socket.IO.
        # Socket.IO 'authenticate' event expects the API Key (bot token).
        if not self.api_key:
            logger.info("Fetching API Key for Socket.IO authentication...")
            # This endpoint returns the bot API key if logged in
            resp_key = await self.client.get("/api/v1/ui/bot")
            if resp_key.status_code == 200:
                self.api_key = resp_key.json().get("apikey", "")

            if not self.api_key:
                logger.warning(
                    "Could not fetch API Key. Socket.IO authentication might fail."
                )

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
            if self.on_game_gamedata:
                await self.on_game_gamedata(game_id, data)

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

        logger.info(f"Submitting move {move_gtp} ({pos}) to game {game_id}")
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
        challenge_id = resp.json().get("id")
        logger.info(f"Challenge created SUCCESSFULLY: ID {challenge_id}")
