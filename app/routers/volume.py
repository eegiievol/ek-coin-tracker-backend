from fastapi import APIRouter, HTTPException, Query
from typing import Annotated
from ..services.exchange import fetch_klines, fetch_klines_multi, Interval

router = APIRouter(prefix="/api/volume", tags=["volume"])


@router.get("/klines")
async def get_klines(
    symbol: str,
    interval: Interval = "1d",
    limit: Annotated[int, Query(ge=1, le=1500)] = 100,
):
    """Raw kline data for a single symbol."""
    try:
        data = await fetch_klines(symbol.upper(), interval, limit)
        return {"symbol": symbol.upper(), "interval": interval, "data": data}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/change")
async def get_volume_change(
    symbols: Annotated[str, Query(description="Comma-separated symbols, e.g. BTCUSDT,ETHUSDT")],
    interval: Interval = "1d",
    limit: Annotated[int, Query(ge=2, le=1500)] = 100,
):
    """
    Volume percentage change over time for multiple symbols.
    Each symbol's volume is expressed as % change relative to its first candle.
    Response is a time-series array suitable for charting.
    """
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    if not symbol_list:
        raise HTTPException(status_code=400, detail="Provide at least one symbol")
    if len(symbol_list) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 symbols per request")

    try:
        klines_map = await fetch_klines_multi(symbol_list, interval, limit)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    if not klines_map:
        raise HTTPException(status_code=404, detail="No data returned for given symbols")

    # Build time-series: each point has a timestamp + pct_change per symbol
    anchor_sym = next(iter(klines_map))
    anchor_series = klines_map[anchor_sym]
    series: list[dict] = []

    for i, candle in enumerate(anchor_series):
        point: dict = {"open_time": candle["open_time"]}
        for sym, data in klines_map.items():
            if not data:
                continue
            base_vol = data[0]["volume"]
            cur_vol = data[i]["volume"] if i < len(data) else data[-1]["volume"]
            point[sym] = round(((cur_vol - base_vol) / base_vol * 100) if base_vol else 0, 2)
        series.append(point)

    return {
        "interval": interval,
        "limit": limit,
        "symbols": list(klines_map.keys()),
        "series": series,
    }
