import pytest
import respx
import httpx
from unittest.mock import AsyncMock
from go_bot.client import OGSClient
from pytest_mock import MockerFixture


@pytest.mark.asyncio  # type: ignore
async def test_ogs_client_connect_full(mocker: MockerFixture) -> None:
    # Mock socketio.AsyncClient
    mock_sio = mocker.patch("socketio.AsyncClient", autospec=True).return_value
    mock_sio.connect = AsyncMock()
    mock_sio.disconnect = AsyncMock()
    mock_sio.emit = AsyncMock()

    client = OGSClient(api_key="test_key")

    with respx.mock(base_url="https://online-go.com") as respx_mock:
        respx_mock.get("/api/v1/me").mock(
            return_value=httpx.Response(200, json={"id": 123, "username": "test_bot"})
        )

        await client.connect()

        assert client.user_id == 123
        assert client.username == "test_bot"
        mock_sio.connect.assert_called()

        await client.disconnect()
        mock_sio.disconnect.assert_called()


@pytest.mark.asyncio  # type: ignore
async def test_ogs_client_create_challenge() -> None:
    client = OGSClient(api_key="test_key")

    with respx.mock(base_url="https://online-go.com") as respx_mock:
        respx_mock.post("/api/v1/challenges").mock(
            return_value=httpx.Response(201, json={"id": "challenge_456"})
        )

        try:
            await client.create_challenge(board_size=19)
            assert respx_mock.calls.last.request.method == "POST"
            # Check content as bytes
            assert b"board_size" in respx_mock.calls.last.request.content
            assert b"19" in respx_mock.calls.last.request.content
        finally:
            await client.client.aclose()


@pytest.mark.asyncio  # type: ignore
async def test_ogs_client_socket_events(mocker: MockerFixture) -> None:
    mock_sio = mocker.patch("socketio.AsyncClient", autospec=True).return_value
    client = OGSClient(api_key="test_key")

    mock_sio.emit = AsyncMock()
    await client.submit_move("456", "Q16", 19)
    mock_sio.emit.assert_called_with("game/move", {"game_id": "456", "move": 72})
