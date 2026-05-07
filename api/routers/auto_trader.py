"""Auto Trader API 라우터"""
from __future__ import annotations

import dataclasses
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/auto-trader", tags=["Auto Trader"])

_trader = None  # AutoTrader instance


def _get():
    if _trader is None:
        raise HTTPException(
            status_code=503,
            detail="AutoTrader가 설정되지 않았습니다. POST /api/auto-trader/configure 를 먼저 호출하세요.",
        )
    return _trader


# -------------------------------------------------------------------
# 요청 모델
# -------------------------------------------------------------------
class ConfigureReq(BaseModel):
    broker: str = "kiwoom"
    paper: bool = True
    simulate: bool = True
    fast_ma: int = 5
    slow_ma: int = 20
    order_qty: float = 1
    dry_run: bool = True


class RunOnceReq(BaseModel):
    watchlist: list[str]
    delay: float = 0.3


# -------------------------------------------------------------------
# 엔드포인트
# -------------------------------------------------------------------
@router.post("/configure")
def configure(req: ConfigureReq):
    global _trader
    try:
        from trading.auto_trader import AutoTrader
        _trader = AutoTrader(
            broker=req.broker,
            paper=req.paper,
            simulate=req.simulate,
            fast_ma=req.fast_ma,
            slow_ma=req.slow_ma,
            order_qty=req.order_qty,
            dry_run=req.dry_run,
        )
        return {"status": "ok", "broker": req.broker, "dry_run": req.dry_run}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/run-once")
def run_once(req: RunOnceReq):
    trader = _get()
    results = trader.run_once(req.watchlist, delay=req.delay)
    return [
        {
            "symbol": r.symbol,
            "signal": r.signal.value,
            "price": r.price,
            "reason": r.reason,
            "indicators": r.indicators,
        }
        for r in results
    ]


@router.get("/history")
def history():
    trader = _get()
    return [dataclasses.asdict(r) for r in trader.history]


@router.delete("/history")
def clear_history():
    _get().history.clear()
    return {"status": "ok", "message": "체결 내역 초기화"}
