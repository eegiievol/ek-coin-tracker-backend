from unittest.mock import AsyncMock, patch, MagicMock
from .conftest import MOCK_TICKERS_RESPONSE


def make_mock_client(json_data):
    mock_response = MagicMock()
    mock_response.json.return_value = json_data
    mock_response.raise_for_status = MagicMock()
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


def test_tickers_excludes_non_usdt(client):
    with patch("app.services.exchange.httpx.AsyncClient", return_value=make_mock_client(MOCK_TICKERS_RESPONSE)):
        res = client.get("/api/tickers")

    symbols = [t["symbol"] for t in res.json()["tickers"]]
    assert "BTCUSDC" not in symbols


def test_tickers_sorted_by_turnover_descending(client):
    with patch("app.services.exchange.httpx.AsyncClient", return_value=make_mock_client(MOCK_TICKERS_RESPONSE)):
        res = client.get("/api/tickers")

    tickers = res.json()["tickers"]
    turnovers = [t["turnover_24h"] for t in tickers]
    assert turnovers == sorted(turnovers, reverse=True)


def test_tickers_response_shape(client):
    with patch("app.services.exchange.httpx.AsyncClient", return_value=make_mock_client(MOCK_TICKERS_RESPONSE)):
        res = client.get("/api/tickers")

    ticker = res.json()["tickers"][0]
    for field in ("symbol", "last_price", "change_24h_pct", "high_24h", "low_24h", "volume_24h", "turnover_24h"):
        assert field in ticker, f"Missing field: {field}"


def test_tickers_change_pct_converted_from_decimal(client):
    with patch("app.services.exchange.httpx.AsyncClient", return_value=make_mock_client(MOCK_TICKERS_RESPONSE)):
        res = client.get("/api/tickers")

    tickers = {t["symbol"]: t for t in res.json()["tickers"]}
    # Bybit sends 0.015 → should be stored as 1.5%
    assert tickers["BTCUSDT"]["change_24h_pct"] == 1.5
    # Bybit sends -0.02 → should be -2.0%
    assert tickers["ETHUSDT"]["change_24h_pct"] == -2.0


def test_tickers_limit_param(client):
    with patch("app.services.exchange.httpx.AsyncClient", return_value=make_mock_client(MOCK_TICKERS_RESPONSE)):
        res = client.get("/api/tickers?limit=1")

    assert res.json()["count"] == 1
    assert len(res.json()["tickers"]) == 1


def test_tickers_returns_502_on_failure(client):
    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("connection error")
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("app.services.exchange.httpx.AsyncClient", return_value=mock_client):
        res = client.get("/api/tickers")

    assert res.status_code == 502
