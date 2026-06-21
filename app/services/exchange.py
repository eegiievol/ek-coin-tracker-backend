import httpx
import asyncio
from typing import Literal

BASE = "https://api.bybit.com"

Interval = Literal["1m", "5m", "15m", "1h", "4h", "1d", "1w"]

_INTERVAL_MAP = {
    "1m": "1", "5m": "5", "15m": "15",
    "1h": "60", "4h": "240", "1d": "D", "1w": "W",
}


async def fetch_symbols() -> list[dict]:
    """Return all active USDT linear perpetual symbols from Bybit."""
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(
            f"{BASE}/v5/market/instruments-info",
            params={"category": "linear", "status": "Trading", "limit": 1000},
        )
        res.raise_for_status()
        data = res.json()

    return [
        {"symbol": s["symbol"], "baseAsset": s["baseCoin"]}
        for s in data["result"]["list"]
        if s["quoteCoin"] == "USDT" and s["contractType"] == "LinearPerpetual"
    ]


async def fetch_klines(symbol: str, interval: Interval, limit: int) -> list[dict]:
    """Return kline data for a single symbol from Bybit."""
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(
            f"{BASE}/v5/market/kline",
            params={
                "category": "linear",
                "symbol": symbol,
                "interval": _INTERVAL_MAP[interval],
                "limit": limit,
            },
        )
        res.raise_for_status()
        data = res.json()

    # Bybit returns newest-first, reverse for chronological order
    rows = list(reversed(data["result"]["list"]))
    return [
        {
            "open_time": int(k[0]),
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
            "turnover": float(k[6]),  # USDT value
            "close_time": int(k[0]),
        }
        for k in rows
    ]


async def fetch_tickers() -> list[dict]:
    """Return 24h ticker data for all active USDT linear perpetuals."""
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(
            f"{BASE}/v5/market/tickers",
            params={"category": "linear"},
        )
        res.raise_for_status()
        data = res.json()

    return [
        {
            "symbol": t["symbol"],
            "last_price": float(t["lastPrice"]),
            "change_24h_pct": round(float(t["price24hPcnt"]) * 100, 2),
            "high_24h": float(t["highPrice24h"]),
            "low_24h": float(t["lowPrice24h"]),
            "volume_24h": float(t["volume24h"]),
            "turnover_24h": float(t["turnover24h"]),
        }
        for t in data["result"]["list"]
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
