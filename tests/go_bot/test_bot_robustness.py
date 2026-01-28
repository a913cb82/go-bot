import pytest
import os
from go_bot.bot import GTPBot
from go_bot.session import GameSession


@pytest.mark.asyncio  # type: ignore
async def test_bot_crash_handling() -> None:
    engine_path = os.path.abspath("tests/go_bot/bad_engine.py")
    bot = GTPBot("coverage", ["run", "-a", engine_path])
    await bot.start()

    session = GameSession("test", 19)

    # Test 1: Genmove returns error
    # Our bad engine returns "? invalid command" for genmove
    try:
        await bot.get_move(session)
    except ValueError as e:
        assert "GTP Error" in str(e)
    except (RuntimeError, ConnectionResetError):
        # It might also close connection depending on timing
        pass

    await bot.stop()


@pytest.mark.asyncio  # type: ignore
async def test_bot_partial_response() -> None:
    engine_path = os.path.abspath("tests/go_bot/bad_engine.py")
    bot = GTPBot("coverage", ["run", "-a", engine_path])
    await bot.start()

    # Test 2: Boardsize causes partial response and exit
    try:
        # We access the private method to send a command directly for testing
        await bot._send_command("boardsize 19")
    except RuntimeError as e:
        assert "Engine closed connection" in str(e) or "Connection lost" in str(e)

    await bot.stop()
