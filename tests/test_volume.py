from unittest.mock import AsyncMock, patch, MagicMock
from .conftest import MOCK_KLINES_RESPONSE


def make_mock_response(json_data):
    mock = MagicMock()
    mock.json.return_value = json_data
    mock.raise_for_status = MagicMock()
    return mock


def make_mock_client(json_data):
    mock_response = make_mock_response(json_data)
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


# --- /api/volume/klines ---

def test_klines_returns_chronological_order(client):
    with patch("app.services.exchange.httpx.AsyncClient", return_value=make_mock_client(MOCK_KLINES_RESPONSE)):
        res = client.get("/api/volume/klines?symbol=BTCUSDT&interval=1d&limit=3")

    assert res.status_code == 200
    data = res.json()["data"]
    # Binance returns oldest-first already — verify chronological order preserved
    assert data[0]["open_time"] < data[1]["open_time"] < data[2]["open_time"]


def test_klines_response_shape(client):
    with patch("app.services.exchange.httpx.AsyncClient", return_value=make_mock_client(MOCK_KLINES_RESPONSE)):
        res = client.get("/api/volume/klines?symbol=BTCUSDT&interval=1d&limit=3")

    candle = res.json()["data"][0]
    for field in ("open_time", "open", "high", "low", "close", "volume"):
        assert field in candle, f"Missing field: {field}"


def test_klines_invalid_limit_rejected(client):
    res = client.get("/api/volume/klines?symbol=BTCUSDT&interval=1d&limit=9999")
    assert res.status_code == 422


def test_klines_invalid_interval_rejected(client):
    res = client.get("/api/volume/klines?symbol=BTCUSDT&interval=3d&limit=10")
    assert res.status_code == 422


# --- /api/volume/change ---

def test_volume_change_starts_at_zero(client):
    with patch("app.services.exchange.httpx.AsyncClient", return_value=make_mock_client(MOCK_KLINES_RESPONSE)):
        res = client.get("/api/volume/change?symbols=BTCUSDT&interval=1d&limit=3")

    assert res.status_code == 200
    series = res.json()["series"]
    assert series[0]["BTCUSDT"] == 0.0


def test_volume_change_calculates_correctly(client):
    with patch("app.services.exchange.httpx.AsyncClient", return_value=make_mock_client(MOCK_KLINES_RESPONSE)):
        res = client.get("/api/volume/change?symbols=BTCUSDT&interval=1d&limit=3")

    series = res.json()["series"]
    # Klines reversed to chronological: volumes are [200, 400, 300]
    # base = 200, second = 400 → (400-200)/200*100 = 100%
    assert series[1]["BTCUSDT"] == 100.0
    # third = 300 → (300-200)/200*100 = 50%
    assert series[2]["BTCUSDT"] == 50.0


def test_volume_change_empty_symbols_rejected(client):
    res = client.get("/api/volume/change?symbols=&interval=1d&limit=10")
    assert res.status_code == 400


def test_volume_change_too_many_symbols_rejected(client):
    syms = ",".join([f"COIN{i}USDT" for i in range(51)])
    res = client.get(f"/api/volume/change?symbols={syms}&interval=1d&limit=10")
    assert res.status_code == 400


def test_volume_change_multiple_symbols(client):
    with patch("app.services.exchange.httpx.AsyncClient", return_value=make_mock_client(MOCK_KLINES_RESPONSE)):
        res = client.get("/api/volume/change?symbols=BTCUSDT,ETHUSDT&interval=1d&limit=3")

    assert res.status_code == 200
    data = res.json()
    assert "BTCUSDT" in data["symbols"]
    assert "ETHUSDT" in data["symbols"]
    assert "BTCUSDT" in data["series"][0]
    assert "ETHUSDT" in data["series"][0]
