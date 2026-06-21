from fastapi import APIRouter, HTTPException
from ..services.exchange import fetch_symbols

router = APIRouter(prefix="/api/symbols", tags=["symbols"])


@router.get("")
async def get_symbols():
    """List all active USDT-M perpetual futures symbols."""
    try:
        symbols = await fetch_symbols()
        return {"count": len(symbols), "symbols": symbols}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
