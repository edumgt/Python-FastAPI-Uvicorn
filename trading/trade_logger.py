"""
매매 기록 DB 모듈 (Trade Logger)
==================================
SQLite 데이터베이스에 매매 기록, 포트폴리오 일일 스냅샷,
시스템 이벤트 로그를 저장합니다.

필요 패키지: 표준 라이브러리만 사용 (sqlite3)

데이터베이스 파일 위치 (기본): ./data/trading.db

테이블 구조:
    trades          – 체결 기록
    daily_snapshots – 일일 포트폴리오 스냅샷
    system_events   – 시스템 이벤트 (시작/정지/에러)
"""

from __future__ import annotations

import csv
import logging
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterator, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 데이터 모델
# ---------------------------------------------------------------------------

@dataclass
class TradeRecord:
    """체결 기록"""
    symbol: str
    side: str                    # "BUY" | "SELL"
    qty: float
    price: float
    amount: float                # qty × price
    broker: str
    order_id: str
    strategy: str = ""           # 전략명 (예: "MA_CROSS", "RF_MODEL")
    note: str = ""
    executed_at: str = ""        # ISO 8601 (자동 설정)

    def __post_init__(self) -> None:
        if not self.executed_at:
            self.executed_at = datetime.now().isoformat(timespec="seconds")
        if self.amount == 0:
            self.amount = round(self.qty * self.price, 4)


@dataclass
class DailySnapshot:
    """일일 포트폴리오 스냅샷"""
    snapshot_date: str           # "YYYY-MM-DD"
    broker: str
    portfolio_value: float
    cash: float
    daily_pnl: float
    daily_pnl_pct: float
    mdd: float
    trade_count: int
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now().isoformat(timespec="seconds")


@dataclass
class SystemEvent:
    """시스템 이벤트"""
    event_type: str              # "START" | "STOP" | "ERROR" | "WARNING"
    message: str
    detail: str = ""
    occurred_at: str = ""

    def __post_init__(self) -> None:
        if not self.occurred_at:
            self.occurred_at = datetime.now().isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# TradeLogger
# ---------------------------------------------------------------------------

class TradeLogger:
    """
    SQLite 기반 매매 기록 저장소

    Parameters
    ----------
    db_path : str  데이터베이스 파일 경로 (기본: data/trading.db)

    Examples
    --------
    >>> logger_db = TradeLogger("data/trading.db")
    >>> logger_db.log_trade(TradeRecord(
    ...     symbol="SPY", side="BUY", qty=1, price=450.0,
    ...     amount=450.0, broker="alpaca", order_id="abc-123",
    ... ))
    >>> trades = logger_db.get_trades(days=7)
    >>> print(trades)
    """

    _DDL = """
    CREATE TABLE IF NOT EXISTS trades (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol       TEXT    NOT NULL,
        side         TEXT    NOT NULL,
        qty          REAL    NOT NULL,
        price        REAL    NOT NULL,
        amount       REAL    NOT NULL,
        broker       TEXT    NOT NULL,
        order_id     TEXT,
        strategy     TEXT,
        note         TEXT,
        executed_at  TEXT    NOT NULL
    );
    CREATE TABLE IF NOT EXISTS daily_snapshots (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        snapshot_date    TEXT NOT NULL,
        broker           TEXT NOT NULL,
        portfolio_value  REAL,
        cash             REAL,
        daily_pnl        REAL,
        daily_pnl_pct    REAL,
        mdd              REAL,
        trade_count      INTEGER,
        created_at       TEXT NOT NULL,
        UNIQUE(snapshot_date, broker)
    );
    CREATE TABLE IF NOT EXISTS system_events (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type  TEXT NOT NULL,
        message     TEXT NOT NULL,
        detail      TEXT,
        occurred_at TEXT NOT NULL
    );
    """

    def __init__(self, db_path: str = "data/trading.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with self._conn() as conn:
            for stmt in self._DDL.strip().split(";"):
                stmt = stmt.strip()
                if stmt:
                    conn.execute(stmt)
        logger.info("DB 초기화 완료: %s", self.db_path)

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # 매매 기록
    # ------------------------------------------------------------------

    def log_trade(self, record: TradeRecord) -> int:
        """
        체결 기록 저장

        Returns
        -------
        int  삽입된 행 ID
        """
        sql = """
            INSERT INTO trades
                (symbol, side, qty, price, amount, broker, order_id, strategy, note, executed_at)
            VALUES
                (:symbol, :side, :qty, :price, :amount, :broker, :order_id, :strategy, :note, :executed_at)
        """
        with self._conn() as conn:
            cur = conn.execute(sql, asdict(record))
            row_id = cur.lastrowid

        logger.info(
            "체결 기록 저장: [%s] %s %s %.4f x %.4f",
            record.broker, record.symbol, record.side, record.qty, record.price,
        )
        return row_id

    def get_trades(
        self,
        days: Optional[int] = None,
        symbol: Optional[str] = None,
        broker: Optional[str] = None,
    ) -> list[dict]:
        """
        체결 기록 조회

        Parameters
        ----------
        days   : 최근 N일치 (None 이면 전체)
        symbol : 종목 필터
        broker : 브로커 필터

        Returns
        -------
        list[dict]
        """
        conditions = []
        params: list = []

        if days is not None:
            conditions.append("executed_at >= datetime('now', ?)")
            params.append(f"-{days} days")
        if symbol:
            conditions.append("symbol = ?")
            params.append(symbol)
        if broker:
            conditions.append("broker = ?")
            params.append(broker)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        sql   = f"SELECT * FROM trades {where} ORDER BY executed_at DESC"

        with self._conn() as conn:
            rows = conn.execute(sql, params).fetchall()

        return [dict(r) for r in rows]

    def get_daily_stats(self, symbol: Optional[str] = None) -> dict:
        """
        오늘 거래 통계

        Returns
        -------
        dict  {"count", "buy_count", "sell_count", "total_amount", "realized_pnl"}
        """
        today = date.today().isoformat()
        base_sql = "SELECT * FROM trades WHERE date(executed_at) = ?"
        params: list = [today]
        if symbol:
            base_sql += " AND symbol = ?"
            params.append(symbol)

        with self._conn() as conn:
            rows = [dict(r) for r in conn.execute(base_sql, params).fetchall()]

        buys  = [r for r in rows if r["side"] == "BUY"]
        sells = [r for r in rows if r["side"] == "SELL"]

        buy_cost   = sum(r["amount"] for r in buys)
        sell_rev   = sum(r["amount"] for r in sells)
        realized   = sell_rev - buy_cost   # 단순 근사

        return {
            "count":         len(rows),
            "buy_count":     len(buys),
            "sell_count":    len(sells),
            "total_amount":  round(buy_cost + sell_rev, 4),
            "realized_pnl":  round(realized, 4),
        }

    # ------------------------------------------------------------------
    # 일일 스냅샷
    # ------------------------------------------------------------------

    def save_daily_snapshot(self, snapshot: DailySnapshot) -> None:
        """
        일일 포트폴리오 스냅샷 저장 (날짜+브로커 기준 UPSERT)
        """
        sql = """
            INSERT INTO daily_snapshots
                (snapshot_date, broker, portfolio_value, cash,
                 daily_pnl, daily_pnl_pct, mdd, trade_count, created_at)
            VALUES
                (:snapshot_date, :broker, :portfolio_value, :cash,
                 :daily_pnl, :daily_pnl_pct, :mdd, :trade_count, :created_at)
            ON CONFLICT(snapshot_date, broker) DO UPDATE SET
                portfolio_value = excluded.portfolio_value,
                cash            = excluded.cash,
                daily_pnl       = excluded.daily_pnl,
                daily_pnl_pct   = excluded.daily_pnl_pct,
                mdd             = excluded.mdd,
                trade_count     = excluded.trade_count,
                created_at      = excluded.created_at
        """
        with self._conn() as conn:
            conn.execute(sql, asdict(snapshot))

        logger.info(
            "스냅샷 저장: %s [%s] 자산=%,.0f 손익=%+,.0f",
            snapshot.snapshot_date, snapshot.broker,
            snapshot.portfolio_value, snapshot.daily_pnl,
        )

    def get_snapshots(self, days: int = 30, broker: Optional[str] = None) -> list[dict]:
        """최근 N일 스냅샷 조회"""
        where  = "WHERE snapshot_date >= date('now', ?) "
        params: list = [f"-{days} days"]
        if broker:
            where += "AND broker = ? "
            params.append(broker)

        sql = f"SELECT * FROM daily_snapshots {where} ORDER BY snapshot_date DESC"
        with self._conn() as conn:
            rows = conn.execute(sql, params).fetchall()

        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # 시스템 이벤트
    # ------------------------------------------------------------------

    def log_event(self, event: SystemEvent) -> None:
        """시스템 이벤트 저장"""
        sql = """
            INSERT INTO system_events (event_type, message, detail, occurred_at)
            VALUES (:event_type, :message, :detail, :occurred_at)
        """
        with self._conn() as conn:
            conn.execute(sql, asdict(event))

        logger.info("이벤트 기록: [%s] %s", event.event_type, event.message)

    # ------------------------------------------------------------------
    # 내보내기
    # ------------------------------------------------------------------

    def export_trades_csv(self, filepath: str = "data/trades_export.csv") -> Path:
        """
        전체 체결 기록을 CSV 파일로 내보내기

        Returns
        -------
        Path  저장된 파일 경로
        """
        records = self.get_trades()
        path    = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        if not records:
            logger.warning("내보낼 데이터 없음")
            return path

        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)

        logger.info("CSV 내보내기 완료: %s (%d행)", path, len(records))
        return path

    def print_summary(self, days: int = 30) -> None:
        """최근 N일 매매 요약 출력"""
        trades = self.get_trades(days=days)
        if not trades:
            print("기록 없음")
            return

        from collections import defaultdict
        by_symbol: dict = defaultdict(lambda: {"count": 0, "buy": 0, "sell": 0})
        for t in trades:
            sym = t["symbol"]
            by_symbol[sym]["count"] += 1
            if t["side"] == "BUY":
                by_symbol[sym]["buy"] += t["amount"]
            else:
                by_symbol[sym]["sell"] += t["amount"]

        print(f"\n{'─'*60}")
        print(f"  최근 {days}일 매매 요약 (총 {len(trades)}건)")
        print(f"{'─'*60}")
        print(f"  {'종목':<10} {'거래수':>6} {'매수금액':>14} {'매도금액':>14} {'손익(근사)':>12}")
        print(f"{'─'*60}")
        for sym, data in sorted(by_symbol.items()):
            pnl = data["sell"] - data["buy"]
            print(
                f"  {sym:<10} {data['count']:>6} "
                f"{data['buy']:>14,.0f} {data['sell']:>14,.0f} {pnl:>+12,.0f}"
            )
        print(f"{'─'*60}\n")


# ---------------------------------------------------------------------------
# 예제 실행
# ---------------------------------------------------------------------------

def _demo() -> None:
    import os
    import tempfile
    db_path = os.path.join(tempfile.gettempdir(), "demo_trading.db")
    db = TradeLogger(db_path)

    print("=== TradeLogger 데모 ===\n")

    # 시스템 시작 이벤트
    db.log_event(SystemEvent("START", "자동매매 봇 시작됨", "paper=True, broker=alpaca"))

    # 체결 기록
    trades = [
        TradeRecord("SPY",  "BUY",  1,  450.0, 0, "alpaca", "ord-001", "MA_CROSS"),
        TradeRecord("AAPL", "BUY",  2,  175.0, 0, "alpaca", "ord-002", "MA_CROSS"),
        TradeRecord("MSFT", "BUY",  1,  380.0, 0, "alpaca", "ord-003", "RF_MODEL"),
        TradeRecord("AAPL", "SELL", 2,  182.0, 0, "alpaca", "ord-004", "MA_CROSS", note="익절"),
        TradeRecord("SPY",  "SELL", 1,  448.0, 0, "alpaca", "ord-005", "MA_CROSS", note="손절"),
    ]
    for t in trades:
        db.log_trade(t)

    # 일일 스냅샷
    db.save_daily_snapshot(DailySnapshot(
        snapshot_date=date.today().isoformat(),
        broker="alpaca",
        portfolio_value=100_250.0,
        cash=82_500.0,
        daily_pnl=250.0,
        daily_pnl_pct=0.0025,
        mdd=0.005,
        trade_count=5,
    ))

    # 요약 출력
    db.print_summary(days=7)

    # CSV 내보내기
    csv_path = db.export_trades_csv(
        os.path.join(tempfile.gettempdir(), "trades_export.csv")
    )
    print(f"CSV 저장: {csv_path}")

    # 오늘 통계
    stats = db.get_daily_stats()
    print(f"오늘 통계: {stats}")


if __name__ == "__main__":
    _demo()
