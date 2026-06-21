from unittest.mock import AsyncMock, patch, MagicMock
from .conftest import MOCK_SYMBOLS_RESPONSE


def make_mock_response(json_data):
    mock = MagicMock()
    mock.json.return_value = json_data
    mock.raise_for_status = MagicMock()
    return mock


def test_symbols_returns_usdt_perpetuals_only(client):
    mock_response = make_mock_response(MOCK_SYMBOLS_RESPONSE)
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("app.services.exchange.httpx.AsyncClient", return_value=mock_client):
        res = client.get("/api/symbols")

    assert res.status_code == 200
    data = res.json()
    assert data["count"] == 3
    symbols = [s["symbol"] for s in data["symbols"]]
    assert "BTCUSDT" in symbols
    assert "ETHUSDT" in symbols
    assert "SOLUSDT" in symbols
    assert "BTCUSDC" not in symbols  # excluded — wrong quote asset


def test_symbols_response_shape(client):
    mock_response = make_mock_response(MOCK_SYMBOLS_RESPONSE)
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("app.services.exchange.httpx.AsyncClient", return_value=mock_client):
        res = client.get("/api/symbols")

    first = res.json()["symbols"][0]
    assert "symbol" in first
    assert "baseAsset" in first


def test_symbols_returns_502_on_api_failure(client):
    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("Bybit unreachable")
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("app.services.exchange.httpx.AsyncClient", return_value=mock_client):
        res = client.get("/api/symbols")

    assert res.status_code == 502
