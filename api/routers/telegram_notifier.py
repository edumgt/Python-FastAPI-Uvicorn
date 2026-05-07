"""Telegram Notifier API 라우터"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from trading.telegram_notifier import TelegramNotifier

router = APIRouter(prefix="/api/telegram", tags=["Telegram Notifier"])

# 기본값: dry_run=True (실제 전송 없이 콘솔 출력만)
_notifier: Optional[TelegramNotifier] = None


def _get() -> TelegramNotifier:
    global _notifier
    if _notifier is None:
        _notifier = TelegramNotifier(dry_run=True)
    return _notifier


# -------------------------------------------------------------------
# 요청 모델
# -------------------------------------------------------------------
class ConfigureReq(BaseModel):
    token: str = ""
    chat_id: str = ""
    dry_run: bool = True


class SendReq(BaseModel):
    message: str


class SendTradeReq(BaseModel):
    symbol: str
    side: str
    qty: float
    price: float
    broker: str = ""
    order_id: str = ""
    note: str = ""


class SendSignalReq(BaseModel):
    symbol: str
    signal: str
    price: float
    indicators: Optional[dict] = None


class SendErrorReq(BaseModel):
    context: str
    error_message: str = ""


class SendStatusReq(BaseModel):
    status: str
    detail: str = ""


class SendSummaryReq(BaseModel):
    broker: str
    portfolio_value: float
    daily_pnl: float
    trade_count: int
    positions: Optional[list] = None


# -------------------------------------------------------------------
# 엔드포인트
# -------------------------------------------------------------------
@router.post("/configure")
def configure(req: ConfigureReq):
    global _notifier
    _notifier = TelegramNotifier(
        token=req.token or None,
        chat_id=req.chat_id or None,
        dry_run=req.dry_run,
    )
    return {"status": "ok", "dry_run": req.dry_run}


@router.post("/send")
def send(req: SendReq):
    ok = _get().send(req.message)
    return {"success": ok}


@router.post("/send-trade")
def send_trade(req: SendTradeReq):
    ok = _get().send_trade(
        symbol=req.symbol,
        side=req.side,
        qty=req.qty,
        price=req.price,
        broker=req.broker,
        order_id=req.order_id,
        note=req.note,
    )
    return {"success": ok}


@router.post("/send-signal")
def send_signal(req: SendSignalReq):
    ok = _get().send_signal(
        symbol=req.symbol,
        signal=req.signal,
        price=req.price,
        indicators=req.indicators,
    )
    return {"success": ok}


@router.post("/send-error")
def send_error(req: SendErrorReq):
    exc = Exception(req.error_message) if req.error_message else None
    ok = _get().send_error(req.context, exc=exc)
    return {"success": ok}


@router.post("/send-status")
def send_status(req: SendStatusReq):
    ok = _get().send_system_status(req.status, req.detail)
    return {"success": ok}


@router.post("/send-summary")
def send_summary(req: SendSummaryReq):
    ok = _get().send_daily_summary(
        broker=req.broker,
        portfolio_value=req.portfolio_value,
        daily_pnl=req.daily_pnl,
        trade_count=req.trade_count,
        positions=req.positions,
    )
    return {"success": ok}
