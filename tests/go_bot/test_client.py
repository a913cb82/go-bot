import pytest
import respx
import httpx
from go_bot.client import OGSClient


@pytest.mark.asyncio  # type: ignore
async def test_ogs_client_connect() -> None:
    client = OGSClient(api_key="test_key")

    # Mock /api/v1/me
    with respx.mock(base_url="https://online-go.com") as respx_mock:
        respx_mock.get("/api/v1/me").mock(
            return_value=httpx.Response(200, json={"id": 123, "username": "test_bot"})
        )

        try:
            # Manually trigger the parts we can test easily
            resp = await client.client.get("/api/v1/me")
            data = resp.json()
            assert data["id"] == 123
            assert data["username"] == "test_bot"
        finally:
            await client.client.aclose()


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
