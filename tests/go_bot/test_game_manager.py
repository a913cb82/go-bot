import pytest
import asyncio
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


@pytest.mark.asyncio  # type: ignore  # type: ignore
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


@pytest.mark.asyncio  # type: ignore  # type: ignore
async def test_game_manager_run_forever(mocker) -> None:
    client = MagicMock()
    client.connect = AsyncMock()
    client.disconnect = AsyncMock()
    client.create_challenge = AsyncMock()
    client.user_id = 123

    bot = MagicMock(spec=Bot)
    bot.start = AsyncMock()
    bot.stop = AsyncMock()

    manager = GameManager(client, bot)

    # We want to run run_forever but break out of it.
    mocker.patch("asyncio.sleep", side_effect=[None, asyncio.CancelledError()])

    try:
        await manager.run_forever()
    except asyncio.CancelledError:
        pass

    client.connect.assert_called_once()
    bot.start.assert_called_once()
    client.create_challenge.assert_called()

    # Ensure cleanup is called
    bot.stop.assert_called_once()
    client.disconnect.assert_called_once()


@pytest.mark.asyncio  # type: ignore  # type: ignore
async def test_game_manager_malformed_events(mocker) -> None:
    client = MagicMock()
    client.user_id = 123
    bot = MockBot()
    manager = GameManager(client, bot)

    # 1. Game Started with missing/wrong user ID
    # Neither black nor white matches our user_id
    bad_start_data = {
        "game_id": 999,
        "width": 19,
        "black": {"id": 888},
        "white": {"id": 777},
    }
    await manager._handle_game_started(bad_start_data)
    assert "999" not in manager.sessions

    # 2. Move for unknown game
    await manager._handle_game_move("unknown_id", {"move": 10, "color": "black"})
    # Should just log warning and return

    # 3. Move with missing data
    manager.sessions["valid_id"] = GameSession("valid_id", 19)
    await manager._handle_game_move("valid_id", {"color": "black"})  # Missing move
    await manager._handle_game_move("valid_id", {"move": 10})  # Missing color

    # 4. Unknown move format (e.g. dict?)
    await manager._handle_game_move(
        "valid_id", {"move": {"weird": "format"}, "color": "black"}
    )
    # Should not crash, just default to -1, -1 which is pass

    # Verify pass was applied for the weird format
    session = manager.sessions["valid_id"]
    assert len(session.moves) == 1
    assert session.moves[0] == ("black", -1, -1)

    # 5. Test Error in _consider_move
    # Force bot to raise exception
    # Patch the get_move method on the bot instance
    mocker.patch.object(bot, "get_move", side_effect=Exception("Bot exploded"))

    # Set turn so consider_move is called
    manager.my_colors["valid_id"] = "black"
    session.turn = "black"

    # Should log error but not crash
    await manager._consider_move(session)
    # If we are here, it caught the exception
