"""Trade Logger API 라우터"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from trading.trade_logger import TradeLogger, TradeRecord, DailySnapshot, SystemEvent

router = APIRouter(prefix="/api/logger", tags=["Trade Logger"])

_db = TradeLogger("data/trading.db")


# -------------------------------------------------------------------
# 요청 모델
# -------------------------------------------------------------------
class LogTradeReq(BaseModel):
    symbol: str
    side: str
    qty: float
    price: float
    broker: str
    order_id: str = ""
    strategy: str = ""
    note: str = ""


class SaveSnapshotReq(BaseModel):
    snapshot_date: str
    broker: str
    portfolio_value: float
    cash: float
    daily_pnl: float
    daily_pnl_pct: float
    mdd: float
    trade_count: int


class LogEventReq(BaseModel):
    event_type: str
    message: str
    detail: str = ""


class ExportReq(BaseModel):
    filepath: str = "data/trades_export.csv"


# -------------------------------------------------------------------
# 엔드포인트
# -------------------------------------------------------------------
@router.post("/trades")
def log_trade(req: LogTradeReq):
    record = TradeRecord(
        symbol=req.symbol,
        side=req.side.upper(),
        qty=req.qty,
        price=req.price,
        amount=round(req.qty * req.price, 4),
        broker=req.broker,
        order_id=req.order_id,
        strategy=req.strategy,
        note=req.note,
    )
    row_id = _db.log_trade(record)
    return {"status": "ok", "id": row_id}


@router.get("/trades")
def get_trades(days: Optional[int] = None, symbol: Optional[str] = None, broker: Optional[str] = None):
    return _db.get_trades(days=days, symbol=symbol, broker=broker)


@router.get("/daily-stats")
def daily_stats(symbol: Optional[str] = None):
    return _db.get_daily_stats(symbol=symbol)


@router.post("/snapshots")
def save_snapshot(req: SaveSnapshotReq):
    snap = DailySnapshot(
        snapshot_date=req.snapshot_date,
        broker=req.broker,
        portfolio_value=req.portfolio_value,
        cash=req.cash,
        daily_pnl=req.daily_pnl,
        daily_pnl_pct=req.daily_pnl_pct,
        mdd=req.mdd,
        trade_count=req.trade_count,
    )
    _db.save_daily_snapshot(snap)
    return {"status": "ok"}


@router.get("/snapshots")
def get_snapshots(days: int = 30, broker: Optional[str] = None):
    return _db.get_snapshots(days=days, broker=broker)


@router.post("/events")
def log_event(req: LogEventReq):
    event = SystemEvent(event_type=req.event_type, message=req.message, detail=req.detail)
    _db.log_event(event)
    return {"status": "ok"}


@router.post("/export-csv")
def export_csv(req: ExportReq):
    path = _db.export_trades_csv(req.filepath)
    return {"status": "ok", "filepath": str(path)}
