from fastapi import APIRouter, HTTPException
from ..services.exchange import fetch_tickers

router = APIRouter(prefix="/api/tickers", tags=["tickers"])


@router.get("")
async def get_tickers(limit: int = 100):
    """24h ticker data sorted by USDT turnover descending."""
    try:
        tickers = await fetch_tickers()
        tickers.sort(key=lambda t: t["turnover_24h"], reverse=True)
        return {"count": len(tickers[:limit]), "tickers": tickers[:limit]}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
