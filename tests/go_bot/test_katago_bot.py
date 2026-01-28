import pytest
import os
import asyncio
from unittest.mock import AsyncMock, MagicMock
from pytest_mock import MockerFixture
from go_bot.bot import KataGoBot
from itertools import cycle


@pytest.mark.asyncio  # type: ignore
async def test_katago_bot_initialization(mocker: MockerFixture) -> None:
    # Mock subprocess.create_subprocess_exec
    mock_exec = mocker.patch("asyncio.create_subprocess_exec", new_callable=AsyncMock)
    mock_process = AsyncMock()
    mock_exec.return_value = mock_process

    # Mock std streams
    mock_process.stdin = AsyncMock()
    mock_process.stdin.drain = AsyncMock()
    mock_process.stdin.write = MagicMock()

    mock_process.stdout = AsyncMock()
    # Return standard successful GTP response sequence indefinitely
    mock_process.stdout.readline.side_effect = cycle([b"= \n", b"\n"])

    mock_process.stderr = AsyncMock()
    mock_process.stderr.readline.return_value = b""

    katago_path = "/usr/bin/katago"
    config_path = "/path/to/config.cfg"
    model_path = "/path/to/model.bin.gz"
    human_model_path = "/path/to/human_model.bin.gz"

    # Test with default rank (5k)
    bot = KataGoBot(katago_path, config_path, model_path, human_model_path)
    await bot.start()

    expected_args_default = [
        katago_path,
        "gtp",
        "-config",
        config_path,
        "-model",
        model_path,
        "-human-model",
        human_model_path,
        "-override-config",
        "humanSLProfile=rank_5k",
    ]
    mock_exec.assert_called_with(
        katago_path,
        *expected_args_default[1:],
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await bot.stop()

    # Test with specific ranks
    ranks = ["30k", "15k", "1k", "1d", "9d"]
    for rank in ranks:
        bot = KataGoBot(
            katago_path, config_path, model_path, human_model_path, rank=rank
        )
        await bot.start()

        expected_args_rank = [
            katago_path,
            "gtp",
            "-config",
            config_path,
            "-model",
            model_path,
            "-human-model",
            human_model_path,
            "-override-config",
            f"humanSLProfile=rank_{rank}",
        ]
        mock_exec.assert_called_with(
            katago_path,
            *expected_args_rank[1:],
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await bot.stop()


def test_human_cfg_generation() -> None:
    # Verify that the fetch script generates a config with correct keys
    # We can just check the content of the file we generated in the previous step
    config_path = "models/human.cfg"
    if not os.path.exists(config_path):
        pytest.skip("models/human.cfg not found")

    with open(config_path, "r") as f:
        content = f.read()

    assert "humanSLProfile = rank_5k" in content
    assert "humanSLChosenMoveProp = 1.0" in content
    assert "humanSLChosenMoveIgnorePass = true" in content
    assert "maxVisits = 40" in content
    assert "ignorePreRootHistory = false" in content
    assert "rootNumSymmetriesToSample = 2" in content
    assert "useNoisePruning = false" in content
