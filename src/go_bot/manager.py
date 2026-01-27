import asyncio
import logging
from typing import Dict, Any
from go_bot.client import OGSClient
from go_bot.session import GameSession
from go_bot.bot import Bot
from go_bot.coords import int_to_ogs_coords, str_to_ogs

logger = logging.getLogger(__name__)


class GameManager:
    def __init__(self, client: OGSClient, bot: Bot):
        self.client = client
        self.bot = bot
        self.sessions: Dict[str, GameSession] = {}
        self.my_colors: Dict[str, str] = {}  # game_id -> "black" or "white"

        # Wire up client callbacks
        self.client.on_game_started = self._handle_game_started
        self.client.on_game_move = self._handle_game_move

    async def _handle_game_started(self, data: Dict[str, Any]) -> None:
        game_id = str(data["game_id"])
        board_size = data.get("width", 19)

        # Determine our color
        # In gameStarted, we usually see "black": { "id": ... } and "white": { "id": ... }
        black_id = data.get("black", {}).get("id")
        white_id = data.get("white", {}).get("id")

        if black_id == self.client.user_id:
            self.my_colors[game_id] = "black"
        elif white_id == self.client.user_id:
            self.my_colors[game_id] = "white"
        else:
            logger.warning(
                f"Joined game {game_id} but user_id {self.client.user_id} not found in players."
            )
            return

        logger.info(
            f"Game started: {game_id} ({board_size}x{board_size}) as {self.my_colors[game_id]}"
        )

        if game_id not in self.sessions:
            self.sessions[game_id] = GameSession(game_id, board_size)
            await self.client.join_game(game_id)

    async def _handle_game_move(self, game_id: str, data: Dict[str, Any]) -> None:
        if game_id not in self.sessions:
            return

        session = self.sessions[game_id]
        move_data = data.get("move")
        color = data.get("color")

        if move_data is None or color is None:
            return

        row, col = -1, -1
        if isinstance(move_data, list):
            row, col = move_data[0], move_data[1]
        elif isinstance(move_data, int):
            row, col = int_to_ogs_coords(move_data, session.board_size)
        elif isinstance(move_data, str):
            row, col = str_to_ogs(move_data)

        session.apply_move(color, row, col)

        # Only consider move if it's our turn
        if session.turn == self.my_colors.get(game_id):
            await self._consider_move(session)

    async def _consider_move(self, session: GameSession) -> None:
        # Avoid moving if we are already thinking for this session
        # (GameManager is a singleton-bot owner, but Bot might have its own lock)
        try:
            # Check if it's the bot's turn (this is a placeholder,
            # we should really know our color in each session)
            move_gtp = await self.bot.get_move(session)
            await self.client.submit_move(session.game_id, move_gtp, session.board_size)
        except Exception as e:
            logger.error(f"Error generating move for {session.game_id}: {e}")

    async def run_forever(self) -> None:
        """Main loop for the bot."""
        await self.client.connect()
        await self.bot.start()

        try:
            while True:
                # Active seeking: if no games, create a challenge
                if not self.sessions:
                    await self.client.create_challenge()

                await asyncio.sleep(60)
        finally:
            await self.bot.stop()
            await self.client.disconnect()
