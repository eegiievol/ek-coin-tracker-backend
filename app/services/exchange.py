import httpx
import asyncio
from typing import Literal

BASE = "https://fapi.binance.com"

Interval = Literal["1m", "5m", "15m", "1h", "4h", "1d", "1w"]


async def fetch_symbols() -> list[dict]:
    """Return all active USDT perpetual futures symbols from Binance."""
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(f"{BASE}/fapi/v1/exchangeInfo")
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
    """Return kline data for a single symbol from Binance."""
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(
            f"{BASE}/fapi/v1/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit},
        )
        res.raise_for_status()
        raw = res.json()

    return [
        {
            "open_time": int(k[0]),
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
            "turnover": float(k[7]),   # quoteAssetVolume = USDT value
            "close_time": int(k[6]),
        }
        for k in raw
    ]


async def fetch_tickers() -> list[dict]:
    """Return 24h ticker data for all active USDT perpetuals from Binance."""
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(f"{BASE}/fapi/v1/ticker/24hr")
        res.raise_for_status()
        data = res.json()

    return [
        {
            "symbol": t["symbol"],
            "last_price": float(t["lastPrice"]),
            "change_24h_pct": round(float(t["priceChangePercent"]), 2),
            "high_24h": float(t["highPrice"]),
            "low_24h": float(t["lowPrice"]),
            "volume_24h": float(t["volume"]),
            "turnover_24h": float(t["quoteVolume"]),
        }
        for t in data
        if t["symbol"].endswith("USDT")
    ]


async def fetch_klines_multi(
    symbols: list[str], interval: Interval, limit: int
) -> dict[str, list[dict]]:
    """Fetch klines for multiple symbols concurrently."""

    async def _fetch(sym: str):
        try:
            return sym, await fetch_klines(sym, interval, limit)
        except Exception:
            return sym, None

    results = await asyncio.gather(*[_fetch(s) for s in symbols])
    return {sym: data for sym, data in results if data is not None}
