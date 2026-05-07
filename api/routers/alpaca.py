"""Alpaca Trader API 라우터"""
from __future__ import annotations

import dataclasses
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/alpaca", tags=["Alpaca Trader"])

_trader = None  # AlpacaTrader instance


def _get():
    if _trader is None:
        raise HTTPException(
            status_code=503,
            detail="AlpacaTrader가 설정되지 않았습니다. POST /api/alpaca/configure 를 먼저 호출하세요.",
        )
    return _trader


# -------------------------------------------------------------------
# 요청 모델
# -------------------------------------------------------------------
class ConfigureReq(BaseModel):
    api_key: str
    secret_key: str
    paper: bool = True


class MarketOrderReq(BaseModel):
    symbol: str
    qty: float
    side: str   # "buy" | "sell"


class LimitOrderReq(BaseModel):
    symbol: str
    qty: float
    side: str
    limit_price: float


class SymbolReq(BaseModel):
    symbol: str


# -------------------------------------------------------------------
# 엔드포인트
# -------------------------------------------------------------------
@router.post("/configure")
def configure(req: ConfigureReq):
    global _trader
    try:
        from trading.alpaca_client import AlpacaTrader
        _trader = AlpacaTrader(api_key=req.api_key, secret_key=req.secret_key, paper=req.paper)
        return {"status": "ok", "paper": req.paper}
    except ImportError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/account")
def get_account():
    result = _get().get_account()
    return dataclasses.asdict(result)


@router.get("/positions")
def get_positions():
    return [dataclasses.asdict(p) for p in _get().get_positions()]


@router.get("/positions/{symbol}")
def get_position(symbol: str):
    pos = _get().get_position(symbol)
    if pos is None:
        return {"symbol": symbol, "position": None}
    return dataclasses.asdict(pos)


@router.post("/orders/market")
def market_order(req: MarketOrderReq):
    result = _get().market_order(req.symbol, req.qty, req.side)
    return dataclasses.asdict(result)


@router.post("/orders/limit")
def limit_order(req: LimitOrderReq):
    result = _get().limit_order(req.symbol, req.qty, req.side, req.limit_price)
    return dataclasses.asdict(result)


@router.delete("/orders")
def cancel_all_orders():
    _get().cancel_all_orders()
    return {"status": "ok", "message": "전체 미체결 주문 취소"}


@router.delete("/positions/{symbol}")
def close_position(symbol: str):
    _get().close_position(symbol)
    return {"status": "ok", "symbol": symbol}


@router.delete("/positions")
def close_all_positions():
    _get().close_all_positions()
    return {"status": "ok", "message": "전체 포지션 청산"}


@router.get("/bars/{symbol}")
def get_bars(symbol: str, days: int = 60, timeframe: str = "1Day"):
    df = _get().get_bars(symbol, days=days, timeframe=timeframe)
    df = df.reset_index()
    df["timestamp"] = df["timestamp"].astype(str)
    return {"symbol": symbol, "timeframe": timeframe, "data": df.to_dict(orient="records")}


@router.get("/signals/ma/{symbol}")
def ma_signal(symbol: str, fast: int = 5, slow: int = 20):
    return _get().ma_cross_signal(symbol, fast=fast, slow=slow)


@router.get("/signals/rsi/{symbol}")
def rsi_signal(symbol: str, period: int = 14, oversold: float = 30.0, overbought: float = 70.0):
    return _get().rsi_signal(symbol, period=period, oversold=oversold, overbought=overbought)
