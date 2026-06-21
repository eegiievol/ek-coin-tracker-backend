import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

# Reusable mock payloads that match Bybit API shapes

MOCK_SYMBOLS_RESPONSE = {
    "result": {
        "list": [
            {"symbol": "BTCUSDT", "baseCoin": "BTC", "quoteCoin": "USDT", "contractType": "LinearPerpetual"},
            {"symbol": "ETHUSDT", "baseCoin": "ETH", "quoteCoin": "USDT", "contractType": "LinearPerpetual"},
            {"symbol": "SOLUSDT", "baseCoin": "SOL", "quoteCoin": "USDT", "contractType": "LinearPerpetual"},
            # Should be excluded — wrong quote asset
            {"symbol": "BTCUSDC", "baseCoin": "BTC", "quoteCoin": "USDC", "contractType": "LinearPerpetual"},
        ]
    }
}

MOCK_KLINES_RESPONSE = {
    "result": {
        "list": [
            # Bybit returns newest-first: [startTime, open, high, low, close, volume, turnover]
            ["1782000000000", "64000", "64500", "63500", "64200", "300", "19200000"],
            ["1781913600000", "63000", "64100", "62800", "64000", "400", "25200000"],
            ["1781827200000", "62000", "63200", "61800", "63000", "200", "12400000"],
        ]
    }
}

MOCK_TICKERS_RESPONSE = {
    "result": {
        "list": [
            {
                "symbol": "BTCUSDT", "lastPrice": "64000", "price24hPcnt": "0.015",
                "highPrice24h": "65000", "lowPrice24h": "63000",
                "volume24h": "10000", "turnover24h": "640000000",
            },
            {
                "symbol": "ETHUSDT", "lastPrice": "3000", "price24hPcnt": "-0.02",
                "highPrice24h": "3100", "lowPrice24h": "2950",
                "volume24h": "50000", "turnover24h": "150000000",
            },
            {
                "symbol": "SOLUSDT", "lastPrice": "150", "price24hPcnt": "0.05",
                "highPrice24h": "160", "lowPrice24h": "145",
                "volume24h": "200000", "turnover24h": "30000000",
            },
            # Should be excluded — not USDT pair
            {
                "symbol": "BTCUSDC", "lastPrice": "64000", "price24hPcnt": "0.01",
                "highPrice24h": "65000", "lowPrice24h": "63000",
                "volume24h": "5000", "turnover24h": "320000000",
            },
        ]
    }
}
