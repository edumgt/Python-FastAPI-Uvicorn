"""Kiwoom Trader API 라우터 (시뮬레이션 모드 기본)"""
from __future__ import annotations

import dataclasses
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from trading.kiwoom_client import KiwoomTrader

router = APIRouter(prefix="/api/kiwoom", tags=["Kiwoom Trader"])

_trader: Optional[KiwoomTrader] = None


def _get() -> KiwoomTrader:
    global _trader
    if _trader is None:
        _trader = KiwoomTrader(simulate=True)
        _trader.login()
    return _trader


# -------------------------------------------------------------------
# 요청 모델
# -------------------------------------------------------------------
class ConfigureReq(BaseModel):
    account_no: str = ""
    simulate: bool = True


class OrderReq(BaseModel):
    symbol: str
    qty: int


class LimitOrderReq(BaseModel):
    symbol: str
    qty: int
    price: int


class SignalReq(BaseModel):
    fast: int = 5
    slow: int = 20


# -------------------------------------------------------------------
# 엔드포인트
# -------------------------------------------------------------------
@router.post("/configure")
def configure(req: ConfigureReq):
    global _trader
    _trader = KiwoomTrader(account_no=req.account_no or None, simulate=req.simulate)
    _trader.login()
    return {"status": "ok", "simulate": req.simulate}


@router.post("/login")
def login():
    result = _get().login()
    return {"success": result}


@router.get("/price/{symbol}")
def get_price(symbol: str):
    price = _get().get_current_price(symbol)
    return {"symbol": symbol, "price": price}


@router.get("/ohlcv/{symbol}")
def get_ohlcv(symbol: str, days: int = 60):
    df = _get().get_ohlcv(symbol, days=days)
    if df.empty:
        return {"symbol": symbol, "data": []}
    df = df.reset_index()
    df["Date"] = df["Date"].astype(str)
    return {"symbol": symbol, "data": df.to_dict(orient="records")}


@router.get("/account")
def get_account():
    info = _get().get_account_info()
    d = dataclasses.asdict(info)
    return d


@router.post("/market-buy")
def market_buy(req: OrderReq):
    result = _get().market_buy(req.symbol, req.qty)
    return dataclasses.asdict(result)


@router.post("/market-sell")
def market_sell(req: OrderReq):
    result = _get().market_sell(req.symbol, req.qty)
    return dataclasses.asdict(result)


@router.post("/limit-buy")
def limit_buy(req: LimitOrderReq):
    result = _get().limit_buy(req.symbol, req.qty, req.price)
    return dataclasses.asdict(result)


@router.post("/limit-sell")
def limit_sell(req: LimitOrderReq):
    result = _get().limit_sell(req.symbol, req.qty, req.price)
    return dataclasses.asdict(result)


@router.get("/signal/{symbol}")
def ma_signal(symbol: str, fast: int = 5, slow: int = 20):
    return _get().ma_cross_signal(symbol, fast=fast, slow=slow)
