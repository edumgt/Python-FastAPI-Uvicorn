"""
자동매매 오케스트레이터 (AutoTrader)
======================================
Alpaca(미국) 또는 키움증권(한국) 클라이언트를 공통 인터페이스로 감싸
신호 생성 → 포지션 확인 → 주문 실행을 일관된 방식으로 처리합니다.

사용 예시::

    # Alpaca Paper Trading (미국 주식)
    from trading import AutoTrader
    trader = AutoTrader(broker="alpaca", paper=True)
    trader.run_once(watchlist=["AAPL", "MSFT", "NVDA"])

    # 키움증권 (국내 주식, 시뮬레이션)
    trader = AutoTrader(broker="kiwoom", simulate=True)
    trader.run_once(watchlist=["005930", "000660"])
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# ---------------------------------------------------------------------------
# 공통 데이터 모델
# ---------------------------------------------------------------------------

class Signal(Enum):
    BUY  = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class SignalResult:
    symbol: str
    signal: Signal
    price: float
    reason: str
    indicators: dict = field(default_factory=dict)  # MA, RSI 등 보조 정보


@dataclass
class TradeRecord:
    """체결 기록"""
    symbol: str
    side: str
    qty: float
    price: float
    broker: str
    order_id: str
    note: str = ""


# ---------------------------------------------------------------------------
# AutoTrader
# ---------------------------------------------------------------------------

class AutoTrader:
    """
    공통 자동매매 오케스트레이터

    Parameters
    ----------
    broker : str
        "alpaca" (미국 주식) 또는 "kiwoom" (국내 주식)
    paper : bool
        Alpaca Paper Trading 사용 여부 (broker="alpaca" 일 때만 유효)
    simulate : bool
        키움증권 시뮬레이션 모드 (broker="kiwoom" 일 때만 유효)
    fast_ma : int
        단기 이동평균 기간 (기본 5일)
    slow_ma : int
        장기 이동평균 기간 (기본 20일)
    order_qty : float | int
        1회 주문 수량 (기본 1)
    dry_run : bool
        True → 신호만 생성, 실제 주문 없음
    """

    def __init__(
        self,
        broker: str = "alpaca",
        paper: bool = True,
        simulate: bool = True,
        fast_ma: int = 5,
        slow_ma: int = 20,
        order_qty: float = 1,
        dry_run: bool = False,
    ) -> None:
        self.broker     = broker.lower()
        self.fast_ma    = fast_ma
        self.slow_ma    = slow_ma
        self.order_qty  = order_qty
        self.dry_run    = dry_run
        self.history: list[TradeRecord] = []

        if self.broker == "alpaca":
            from trading.alpaca_client import AlpacaTrader
            self._client = AlpacaTrader(paper=paper)
        elif self.broker == "kiwoom":
            from trading.kiwoom_client import KiwoomTrader
            self._client = KiwoomTrader(simulate=simulate)
            self._client.login()
        else:
            raise ValueError(f"지원하지 않는 브로커: {broker}. 'alpaca' 또는 'kiwoom' 사용")

    # ------------------------------------------------------------------
    # 신호 생성
    # ------------------------------------------------------------------

    def get_signal(self, symbol: str) -> SignalResult:
        """MA 크로스 신호를 가져와 SignalResult 로 변환"""
        raw = self._client.ma_cross_signal(symbol, fast=self.fast_ma, slow=self.slow_ma)
        return SignalResult(
            symbol=symbol,
            signal=Signal(raw.get("signal", "HOLD")),
            price=float(raw.get("price", 0)),
            reason=f"MA{self.fast_ma}/MA{self.slow_ma} 크로스",
            indicators={
                f"MA{self.fast_ma}": raw.get(f"MA{self.fast_ma}"),
                f"MA{self.slow_ma}": raw.get(f"MA{self.slow_ma}"),
            },
        )

    # ------------------------------------------------------------------
    # 주문 실행
    # ------------------------------------------------------------------

    def execute(self, result: SignalResult) -> Optional[TradeRecord]:
        """
        신호에 따라 주문 실행

        Returns
        -------
        TradeRecord | None   체결 기록 (HOLD 또는 dry_run 이면 None)
        """
        if result.signal == Signal.HOLD:
            return None

        side = "buy" if result.signal == Signal.BUY else "sell"
        logger.info(
            "[%s] %s 신호 → %s %s주 @ %.4f (dry_run=%s)",
            self.broker.upper(),
            result.symbol,
            side.upper(),
            self.order_qty,
            result.price,
            self.dry_run,
        )

        if self.dry_run:
            return TradeRecord(
                symbol=result.symbol,
                side=side,
                qty=self.order_qty,
                price=result.price,
                broker=self.broker,
                order_id="DRY_RUN",
                note="dry_run 모드 – 실제 주문 없음",
            )

        try:
            if self.broker == "alpaca":
                order = self._client.market_order(result.symbol, self.order_qty, side)
                record = TradeRecord(
                    symbol=result.symbol,
                    side=side,
                    qty=self.order_qty,
                    price=result.price,
                    broker="alpaca",
                    order_id=order.order_id,
                )
            else:  # kiwoom
                qty = int(self.order_qty)
                if side == "buy":
                    order = self._client.market_buy(result.symbol, qty)
                else:
                    order = self._client.market_sell(result.symbol, qty)
                record = TradeRecord(
                    symbol=result.symbol,
                    side=side,
                    qty=qty,
                    price=result.price,
                    broker="kiwoom",
                    order_id=order.order_no,
                )

            self.history.append(record)
            return record

        except Exception as exc:
            logger.error("[%s] 주문 실패: %s", result.symbol, exc)
            return None

    # ------------------------------------------------------------------
    # 메인 실행 루프
    # ------------------------------------------------------------------

    def run_once(self, watchlist: list[str], delay: float = 0.5) -> list[SignalResult]:
        """
        감시 목록 전체에 대해 신호 확인 → 주문 실행 1회 수행

        Parameters
        ----------
        watchlist : list[str]  종목 코드 목록
        delay     : float      종목 간 API 호출 간격(초)

        Returns
        -------
        list[SignalResult]  신호 결과 목록
        """
        results: list[SignalResult] = []
        logger.info("=== AutoTrader 신호 확인 시작 (종목 수: %d) ===", len(watchlist))

        for symbol in watchlist:
            try:
                sig = self.get_signal(symbol)
                results.append(sig)
                record = self.execute(sig)
                ma_fast = sig.indicators.get(f"MA{self.fast_ma}", "N/A")
                ma_slow = sig.indicators.get(f"MA{self.slow_ma}", "N/A")
                logger.info(
                    "  [%s] 신호: %-4s | 가격: %10.4f | MA%d: %s | MA%d: %s%s",
                    symbol,
                    sig.signal.value,
                    sig.price,
                    self.fast_ma, ma_fast,
                    self.slow_ma, ma_slow,
                    f" → 주문ID: {record.order_id}" if record else "",
                )
            except Exception as exc:
                logger.warning("  [%s] 처리 오류: %s", symbol, exc)
            time.sleep(delay)

        logger.info("=== 완료 (거래 %d건) ===", sum(1 for r in results if r.signal != Signal.HOLD))
        return results

    def print_summary(self) -> None:
        """체결 내역 요약 출력"""
        if not self.history:
            print("체결 내역 없음")
            return
        print(f"\n{'─'*60}")
        print(f"{'브로커':<10} {'종목':<10} {'방향':<6} {'수량':>6} {'가격':>12} {'주문ID'}")
        print(f"{'─'*60}")
        for r in self.history:
            print(
                f"{r.broker:<10} {r.symbol:<10} {r.side:<6} "
                f"{r.qty:>6} {r.price:>12.4f} {r.order_id}"
            )
        print(f"{'─'*60}")
        print(f"총 {len(self.history)}건 체결\n")


# ---------------------------------------------------------------------------
# 예제 실행
# ---------------------------------------------------------------------------

def _demo_alpaca() -> None:
    """Alpaca Paper Trading 데모"""
    print("=== Alpaca Paper Trading 자동매매 데모 ===\n")
    trader = AutoTrader(
        broker="alpaca",
        paper=True,
        fast_ma=5,
        slow_ma=20,
        order_qty=1,
        dry_run=True,   # 실제 주문 없이 신호만 확인
    )
    trader.run_once(watchlist=["AAPL", "MSFT", "NVDA", "TSLA", "AMZN"])
    trader.print_summary()


def _demo_kiwoom() -> None:
    """키움증권 시뮬레이션 데모"""
    print("=== 키움증권 자동매매 데모 (시뮬레이션) ===\n")
    trader = AutoTrader(
        broker="kiwoom",
        simulate=True,
        fast_ma=5,
        slow_ma=20,
        order_qty=1,
        dry_run=False,  # 시뮬레이션 주문 실행
    )
    trader.run_once(watchlist=["005930", "000660", "035420"])
    trader.print_summary()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="자동매매 오케스트레이터 데모")
    parser.add_argument(
        "--broker",
        choices=["alpaca", "kiwoom"],
        default="kiwoom",
        help="사용할 브로커 (기본: kiwoom)",
    )
    args = parser.parse_args()

    if args.broker == "alpaca":
        _demo_alpaca()
    else:
        _demo_kiwoom()
