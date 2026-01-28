import pytest
from unittest.mock import MagicMock
from go_bot.manager import GameManager
from go_bot.session import GameSession
from go_bot.bot import Bot


class MockBot(Bot):
    async def get_move(self, session: GameSession) -> str:
        return "pass"

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass


@pytest.mark.asyncio  # type: ignore
async def test_game_manager_recovery() -> None:
    client = MagicMock()
    client.user_id = 123
    bot = MockBot()
    manager = GameManager(client, bot)

    # Simulate gamedata for an in-progress game
    # 19x19 board, 2 moves already played
    gamedata = {
        "width": 19,
        "height": 19,
        "players": {
            "black": {"id": 123},  # We are black
            "white": {"id": 456},
        },
        "moves": [
            [3, 3, 1000],  # Black D16 (col=3, row=3 in OGS)
            [15, 15, 2000],  # White Q4 (col=15, row=15 in OGS)
        ],
    }

    await manager._handle_game_gamedata("active_1", gamedata)

    assert "active_1" in manager.sessions
    session = manager.sessions["active_1"]
    assert len(session.moves) == 2
    assert session.turn == "black"  # After B, W moves, it's B turn again
    assert manager.my_colors["active_1"] == "black"

    # Check if stones are on board
    # D16 is (3, 3) in OGS
    assert session.board.get(3, 19 - 1 - 3) == "b"
    # Q4 is (15, 15) in OGS
    assert session.board.get(15, 19 - 1 - 15) == "w"
