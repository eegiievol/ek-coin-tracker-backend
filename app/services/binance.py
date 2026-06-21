import httpx
import os
from typing import Literal

# Use testnet locally if BINANCE_TESTNET=true, production otherwise
_TESTNET = os.getenv("BINANCE_TESTNET", "false").lower() == "true"
FAPI_BASE = "https://testnet.binancefuture.com" if _TESTNET else "https://fapi.binance.com"

Interval = Literal["1m", "5m", "15m", "1h", "4h", "1d", "1w"]


async def fetch_symbols() -> list[dict]:
    """Return all active USDT-M perpetual futures symbols."""
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(f"{FAPI_BASE}/fapi/v1/exchangeInfo")
        res.raise_for_status()
        data = res.json()

    return [
        {"symbol": s["symbol"], "baseAsset": s["baseAsset"]}
        for s in data["symbols"]
        if s["contractType"] == "PERPETUAL"
        and s["quoteAsset"] == "USDT"
        and s["status"] == "TRADING"
    ]


async def fetch_klines(symbol: str, interval: Interval, limit: int) -> list[dict]:
    """Return kline data for a single symbol."""
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(
            f"{FAPI_BASE}/fapi/v1/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit},
        )
        res.raise_for_status()
        raw = res.json()

    return [
        {
            "open_time": k[0],
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
            "close_time": k[6],
        }
        for k in raw
    ]


async def fetch_klines_multi(
    symbols: list[str], interval: Interval, limit: int
) -> dict[str, list[dict]]:
    """Fetch klines for multiple symbols concurrently."""
    import asyncio

    async def _fetch(sym: str):
        try:
            return sym, await fetch_klines(sym, interval, limit)
        except Exception:
            return sym, None

    results = await asyncio.gather(*[_fetch(s) for s in symbols])
    return {sym: data for sym, data in results if data is not None}
