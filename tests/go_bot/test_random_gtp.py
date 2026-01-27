import pytest
import os
from go_bot.bot import GTPBot
from go_bot.session import GameSession


@pytest.mark.asyncio  # type: ignore
async def test_random_gtp_edge_cases() -> None:
    # Use 'coverage run' to wrap the engine execution
    engine_path = os.path.abspath("src/go_bot/random_gtp.py")
    # We use -a to append to the current .coverage file
    bot = GTPBot("coverage", ["run", "-a", engine_path])
    await bot.start()

    try:
        # 1. Test No Valid Moves (Full Board)
        # We'll use a small board to fill it up quickly
        size = 3
        session = GameSession("full_board", size)

        # Fill board such that every empty spot is suicide for white
        # . B .
        # B . B
        # . B .
        # White playing in any . is suicide (assuming no captures possible)
        # We'll just fill most of the board with black.
        size = 5
        session = GameSession("suicide_fill", size)
        for r in range(size):
            for c in range(size):
                if (r + c) % 2 != 0:
                    session.apply_move("black", r, c)

        # Now every empty spot (r+c even) is surrounded by black.
        # White move to any empty spot is suicide.
        move = await bot.get_move(session)
        assert move.lower() == "pass"

        # 2. Test Suicide & Ko implicitly
        # (Already partially covered by the fact that genmove filters legal moves)

        # Test Ko specifically
        session_ko = GameSession("ko", 5)
        # Setup Ko
        ko_moves = [
            (0, 1, "black"),
            (0, 2, "white"),
            (1, 0, "black"),
            (1, 3, "white"),
            (2, 1, "black"),
            (2, 2, "white"),
            (1, 2, "black"),
            (1, 1, "white"),  # White captures (1,2)
        ]
        for r, c, color in ko_moves:
            session_ko.apply_move(color, r, c)

        # Black cannot capture back immediately at (1,1) due to Ko
        move_ko = await bot.get_move(session_ko)
        assert move_ko.upper() != "B4"  # (1,1) in 5x5 is B4

    finally:
        await bot.stop()


@pytest.mark.asyncio  # type: ignore
async def test_random_gtp_illegal_play_command() -> None:
    # Test that 'play' with an illegal move returns an error and doesn't crash
    engine_path = os.path.abspath("src/go_bot/random_gtp.py")
    bot = GTPBot("coverage", ["run", "-a", engine_path])
    await bot.start()

    try:
        # Play out of bounds or invalid format
        with pytest.raises(ValueError, match="GTP Error"):
            await bot._send_command("play black Z99")

        await bot._send_command("play white A1")
        with pytest.raises(ValueError, match="GTP Error"):
            await bot._send_command("play black A1")  # Occupied

        # Check engine is still alive
        response = await bot._send_command("name")
        assert response == "RandomGTP"
    finally:
        await bot.stop()
