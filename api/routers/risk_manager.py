"""Risk Manager API 라우터"""
from __future__ import annotations

import dataclasses
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from trading.risk_manager import RiskManager

router = APIRouter(prefix="/api/risk", tags=["Risk Manager"])

# -------------------------------------------------------------------
# 싱글턴 인스턴스
# -------------------------------------------------------------------
_rm: Optional[RiskManager] = None


def _get() -> RiskManager:
    global _rm
    if _rm is None:
        _rm = RiskManager()
    return _rm


def _snap_dict(snap) -> dict:
    d = dataclasses.asdict(snap)
    d["timestamp"] = snap.timestamp.isoformat()
    return d


# -------------------------------------------------------------------
# 요청 모델
# -------------------------------------------------------------------
class ConfigureReq(BaseModel):
    daily_loss_limit: float = 0.02
    max_mdd_limit: float = 0.10
    max_position_pct: float = 0.20
    max_trades_per_day: int = 50
    cooldown_seconds: float = 60.0


class ValueReq(BaseModel):
    value: float


class PositionSizeReq(BaseModel):
    symbol: str
    price: float
    target_pct: Optional[float] = None


class RecordTradeReq(BaseModel):
    symbol: str


class HaltReq(BaseModel):
    reason: str = "수동 정지"


# -------------------------------------------------------------------
# 엔드포인트
# -------------------------------------------------------------------
@router.post("/configure")
def configure(req: ConfigureReq):
    global _rm
    _rm = RiskManager(
        daily_loss_limit=req.daily_loss_limit,
        max_mdd_limit=req.max_mdd_limit,
        max_position_pct=req.max_position_pct,
        max_trades_per_day=req.max_trades_per_day,
        cooldown_seconds=req.cooldown_seconds,
    )
    return {"status": "ok", "message": "RiskManager 설정 완료"}


@router.post("/set-portfolio")
def set_portfolio(req: ValueReq):
    _get().set_portfolio_value(req.value)
    return {"status": "ok", "portfolio_value": req.value}


@router.post("/update-portfolio")
def update_portfolio(req: ValueReq):
    rm = _get()
    rm.update_portfolio_value(req.value)
    return _snap_dict(rm.get_snapshot())


@router.get("/snapshot")
def snapshot():
    return _snap_dict(_get().get_snapshot())


@router.get("/can-trade")
def can_trade(symbol: Optional[str] = None):
    rm = _get()
    return {"can_trade": rm.can_trade(symbol), "stop_reason": rm.stop_reason}


@router.post("/position-size")
def position_size(req: PositionSizeReq):
    result = _get().position_size(req.symbol, req.price, req.target_pct)
    return dataclasses.asdict(result)


@router.post("/record-trade")
def record_trade(req: RecordTradeReq):
    _get().record_trade(req.symbol)
    return {"status": "ok", "symbol": req.symbol}


@router.post("/halt")
def halt(req: HaltReq):
    _get().force_halt(req.reason)
    return {"status": "halted", "reason": req.reason}


@router.post("/resume")
def resume():
    _get().force_resume()
    return {"status": "resumed"}
