import pytest
from unittest.mock import AsyncMock, MagicMock
from go_bot.manager import GameManager
from go_bot.session import GameSession
from go_bot.bot import Bot


class MockBot(Bot):
    async def get_move(self, session: GameSession) -> str:
        return "Q16"

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass


@pytest.mark.asyncio  # type: ignore
async def test_game_manager_routing() -> None:
    client = MagicMock()
    client.user_id = 123
    client.on_game_started = None
    client.on_game_move = None
    client.join_game = AsyncMock()
    client.submit_move = AsyncMock()

    bot = MockBot()
    manager = GameManager(client, bot)

    # Simulate game start
    game_started_data = {
        "game_id": 456,
        "width": 19,
        "black": {"id": 123},  # We are black
        "white": {"id": 789},
    }
    await manager._handle_game_started(game_started_data)

    assert "456" in manager.sessions
    assert manager.my_colors["456"] == "black"
    client.join_game.assert_called_with("456")

    # Simulate move by opponent (white)
    # Since we are black, we might have moved first, but let's assume opponent moved.
    # Wait, if we are black, it's our turn at start.
    # But usually we get gamedata or move event.

    # Test turn logic
    session = manager.sessions["456"]
    assert session.turn == "black"

    # Trigger consider_move
    await manager._consider_move(session)
    client.submit_move.assert_called_with("456", "Q16", 19)

    # Simulate opponent move
    move_data = {
        "game_id": 456,
        "move": [3, 3],  # D16
        "color": "white",
    }
    # Reset mock to check for next call
    client.submit_move.reset_mock()
    await manager._handle_game_move("456", move_data)

    assert session.turn == "black"  # It's our turn again
    client.submit_move.assert_called()
