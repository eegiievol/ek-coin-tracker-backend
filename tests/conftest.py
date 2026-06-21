import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

# Reusable mock payloads matching Binance API shapes

MOCK_SYMBOLS_RESPONSE = {
    "symbols": [
        {"symbol": "BTCUSDT", "baseAsset": "BTC", "quoteAsset": "USDT", "contractType": "PERPETUAL", "status": "TRADING"},
        {"symbol": "ETHUSDT", "baseAsset": "ETH", "quoteAsset": "USDT", "contractType": "PERPETUAL", "status": "TRADING"},
        {"symbol": "SOLUSDT", "baseAsset": "SOL", "quoteAsset": "USDT", "contractType": "PERPETUAL", "status": "TRADING"},
        # Excluded — wrong quote asset
        {"symbol": "BTCUSDC", "baseAsset": "BTC", "quoteAsset": "USDC", "contractType": "PERPETUAL", "status": "TRADING"},
        # Excluded — not perpetual
        {"symbol": "BTCUSDT_241227", "baseAsset": "BTC", "quoteAsset": "USDT", "contractType": "DELIVERY", "status": "TRADING"},
    ]
}

# Binance klines: [openTime, open, high, low, close, volume, closeTime, quoteAssetVolume, ...]
# Oldest-first (chronological)
MOCK_KLINES_RESPONSE = [
    [1781827200000, "62000", "63200", "61800", "63000", "200", 1781913599999, "12400000", 0, 0, 0, 0],
    [1781913600000, "63000", "64100", "62800", "64000", "400", 1781999999999, "25200000", 0, 0, 0, 0],
    [1782000000000, "64000", "64500", "63500", "64200", "300", 1782086399999, "19200000", 0, 0, 0, 0],
]

# Binance 24hr ticker — list of dicts
MOCK_TICKERS_RESPONSE = [
    {
        "symbol": "BTCUSDT", "lastPrice": "64000", "priceChangePercent": "1.5",
        "highPrice": "65000", "lowPrice": "63000",
        "volume": "10000", "quoteVolume": "640000000",
    },
    {
        "symbol": "ETHUSDT", "lastPrice": "3000", "priceChangePercent": "-2.0",
        "highPrice": "3100", "lowPrice": "2950",
        "volume": "50000", "quoteVolume": "150000000",
    },
    {
        "symbol": "SOLUSDT", "lastPrice": "150", "priceChangePercent": "5.0",
        "highPrice": "160", "lowPrice": "145",
        "volume": "200000", "quoteVolume": "30000000",
    },
    # Excluded — not USDT pair
    {
        "symbol": "BTCUSDC", "lastPrice": "64000", "priceChangePercent": "1.0",
        "highPrice": "65000", "lowPrice": "63000",
        "volume": "5000", "quoteVolume": "320000000",
    },
]
