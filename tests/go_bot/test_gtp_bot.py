import pytest
import os
from go_bot.bot import GTPBot
from go_bot.session import GameSession


@pytest.mark.asyncio
async def test_gtp_bot_integration() -> None:
    # Use the absolute path to ensure the engine is found
    engine_path = os.path.abspath("src/go_bot/random_gtp.py")
    bot = GTPBot(engine_path)

    await bot.start()
    try:
        session = GameSession("test_game", 9)
        session.apply_move("black", 4, 4)  # E5 in 9x9 is (4,4)

        move = await bot.get_move(session)
        assert move is not None
        assert isinstance(move, str)
        # RandomBot should return a valid coord or pass
        assert move.lower() == "pass" or (len(move) >= 2 and move[0].isalpha())

        # Test synchronization with multiple sessions
        session2 = GameSession("test_game_2", 13)
        session2.apply_move("black", 0, 0)  # A13

        move2 = await bot.get_move(session2)
        assert move2 is not None

    finally:
        await bot.stop()
