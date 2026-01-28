import pytest
from unittest.mock import AsyncMock, MagicMock
from pytest_mock import MockerFixture
from go_bot.bot import KataGoBot
from go_bot.session import GameSession
from go_bot.coords import gtp_to_ogs
from itertools import cycle


@pytest.mark.asyncio  # type: ignore
async def test_human_sl_rank_simulation(mocker: MockerFixture) -> None:
    # Mock subprocess
    mock_exec = mocker.patch("asyncio.create_subprocess_exec", new_callable=AsyncMock)
    mock_process = AsyncMock()
    mock_exec.return_value = mock_process

    mock_process.stdin = AsyncMock()
    mock_process.stdin.drain = AsyncMock()
    mock_process.stdin.write = MagicMock()
    mock_process.stdout = AsyncMock()
    mock_process.stderr = AsyncMock()
    mock_process.stderr.readline.return_value = b""

    # Setup infinite successful responses
    # Pattern: = Q16\n\n (success)
    mock_process.stdout.readline.side_effect = cycle([b"= Q16\n", b"\n"])

    katago_path = "/usr/bin/katago"
    config_path = "models/human.cfg"
    model_path = "models/main_model.bin.gz"
    human_model_path = "models/human_model.bin.gz"

    ranks_to_test = ["30k", "10k", "1d", "9d"]

    for rank in ranks_to_test:
        print(f"Simulating game with rank: {rank}")
        bot = KataGoBot(
            katago_path, config_path, model_path, human_model_path, rank=rank
        )
        await bot.start()

        # Verify rank override in args
        expected_override = f"humanSLProfile=rank_{rank}"
        args = mock_exec.call_args[0]
        assert expected_override in args

        # Play a few moves
        session = GameSession(f"game_{rank}", 19)

        # Genmove 1 (Black)
        move1 = await bot.get_move(session)
        # Apply the bot's move to the session
        # We need to convert GTP coord back to OGS/session coord if we want to use apply_move with ints
        # But apply_move takes (color, row, col).

        row1, col1 = gtp_to_ogs(move1, 19)
        # Assuming black played first
        session.apply_move("black", row1, col1)

        # Apply move and Genmove 2 (White)
        # Simulate opponent move (white)
        session.apply_move("white", 3, 3)  # D16

        # Genmove 3 (Black again)
        await bot.get_move(session)

        await bot.stop()
