"""
리스크 관리 모듈 (Risk Manager)
==================================
일일 손실 한도, MDD(최대낙폭) 한도, 포지션 사이징,
시스템 정지 메커니즘을 제공합니다.

사용 예시::

    from trading.risk_manager import RiskManager
    rm = RiskManager(
        daily_loss_limit=0.02,   # 일일 손실 2% 초과 시 정지
        max_mdd_limit=0.10,      # MDD 10% 초과 시 정지
        max_position_pct=0.20,   # 단일 종목 최대 20%
    )
    rm.update_portfolio_value(10_000_000)
    if not rm.can_trade():
        print("거래 금지 상태:", rm.stop_reason)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 데이터 모델
# ---------------------------------------------------------------------------

@dataclass
class RiskSnapshot:
    """현재 리스크 상태 스냅샷"""
    timestamp: datetime
    portfolio_value: float
    peak_value: float
    daily_start_value: float
    daily_pnl: float
    daily_pnl_pct: float
    mdd: float                      # 현재 MDD
    trade_count_today: int
    is_halted: bool
    halt_reason: str


@dataclass
class PositionSizeResult:
    """포지션 사이징 결과"""
    symbol: str
    allowed_pct: float      # 허용 비중 (0.0 ~ 1.0)
    allowed_value: float    # 허용 금액 (원/$)
    suggested_qty: float    # 제안 수량
    price: float


# ---------------------------------------------------------------------------
# RiskManager
# ---------------------------------------------------------------------------

class RiskManager:
    """
    자동매매 리스크 관리 클래스

    Parameters
    ----------
    daily_loss_limit : float
        일일 최대 손실 비율 (기본 2%). 초과 시 당일 거래 중단.
    max_mdd_limit : float
        최대 낙폭(MDD) 한도 (기본 10%). 초과 시 시스템 전체 정지.
    max_position_pct : float
        단일 종목 최대 비중 (기본 20%).
    max_trades_per_day : int
        일일 최대 거래 건수 (기본 50).
    cooldown_seconds : float
        동일 종목 재거래 최소 대기 시간 (초, 기본 60).

    Examples
    --------
    >>> rm = RiskManager(daily_loss_limit=0.02, max_mdd_limit=0.10)
    >>> rm.set_portfolio_value(10_000_000)   # 초기 자산 설정
    >>> rm.update_portfolio_value(9_800_000) # 현재 자산 업데이트

    >>> if rm.can_trade():
    ...     size = rm.position_size("AAPL", price=450.0)
    ...     print(f"허용 수량: {size.suggested_qty}")
    """

    def __init__(
        self,
        daily_loss_limit: float = 0.02,
        max_mdd_limit: float = 0.10,
        max_position_pct: float = 0.20,
        max_trades_per_day: int = 50,
        cooldown_seconds: float = 60.0,
    ) -> None:
        self.daily_loss_limit   = daily_loss_limit
        self.max_mdd_limit      = max_mdd_limit
        self.max_position_pct   = max_position_pct
        self.max_trades_per_day = max_trades_per_day
        self.cooldown_seconds   = cooldown_seconds

        self._portfolio_value:    float = 0.0
        self._peak_value:         float = 0.0
        self._daily_start_value:  float = 0.0
        self._daily_date:         date  = date.today()
        self._trade_count_today:  int   = 0
        self._last_trade_time:    dict  = {}   # symbol → datetime
        self._is_halted:          bool  = False
        self._halt_reason:        str   = ""

    # ------------------------------------------------------------------
    # 자산 업데이트
    # ------------------------------------------------------------------

    def set_portfolio_value(self, value: float) -> None:
        """초기 자산 설정 (봇 최초 시작 시 1회 호출)"""
        self._portfolio_value   = value
        self._peak_value        = value
        self._daily_start_value = value
        self._daily_date        = date.today()
        logger.info("초기 자산 설정: %,.0f", value)

    def update_portfolio_value(self, value: float) -> None:
        """
        현재 자산 값 업데이트 및 리스크 체크

        Parameters
        ----------
        value : float  현재 포트폴리오 평가금액
        """
        self._reset_daily_if_needed()
        self._portfolio_value = value

        # 고점 갱신
        if value > self._peak_value:
            self._peak_value = value

        # 일일 손실 체크
        daily_pnl_pct = self._calc_daily_pnl_pct()
        if daily_pnl_pct <= -self.daily_loss_limit:
            self._halt(
                f"일일 손실 한도 초과: {daily_pnl_pct*100:.2f}% "
                f"(한도: -{self.daily_loss_limit*100:.1f}%)"
            )

        # MDD 체크
        mdd = self._calc_mdd()
        if mdd >= self.max_mdd_limit:
            self._halt(
                f"MDD 한도 초과: {mdd*100:.2f}% "
                f"(한도: {self.max_mdd_limit*100:.1f}%)"
            )

    def _reset_daily_if_needed(self) -> None:
        """날짜가 바뀌면 일일 지표 초기화"""
        today = date.today()
        if today != self._daily_date:
            self._daily_start_value = self._portfolio_value
            self._daily_date        = today
            self._trade_count_today = 0
            # 일일 정지는 다음 날 해제 (MDD 정지는 유지)
            if "일일 손실" in self._halt_reason:
                self._resume("새 거래일 시작 – 일일 정지 해제")
            logger.info("새 거래일 시작: %s", today)

    # ------------------------------------------------------------------
    # 리스크 지표 계산
    # ------------------------------------------------------------------

    def _calc_daily_pnl_pct(self) -> float:
        """일일 수익률 (음수: 손실)"""
        if self._daily_start_value == 0:
            return 0.0
        return (self._portfolio_value - self._daily_start_value) / self._daily_start_value

    def _calc_mdd(self) -> float:
        """현재 고점 대비 낙폭 (양수: 낙폭)"""
        if self._peak_value == 0:
            return 0.0
        return (self._peak_value - self._portfolio_value) / self._peak_value

    # ------------------------------------------------------------------
    # 거래 가능 여부
    # ------------------------------------------------------------------

    def can_trade(self, symbol: Optional[str] = None) -> bool:
        """
        현재 거래 가능 여부 확인

        Parameters
        ----------
        symbol : str | None  쿨다운 체크할 종목코드 (None 이면 생략)

        Returns
        -------
        bool  True → 거래 가능
        """
        if self._is_halted:
            return False

        if self._trade_count_today >= self.max_trades_per_day:
            logger.warning("일일 최대 거래 건수 도달: %d", self.max_trades_per_day)
            return False

        if symbol and not self._check_cooldown(symbol):
            return False

        return True

    def _check_cooldown(self, symbol: str) -> bool:
        """쿨다운 체크 (True → 거래 가능)"""
        last = self._last_trade_time.get(symbol)
        if last is None:
            return True
        elapsed = (datetime.now() - last).total_seconds()
        if elapsed < self.cooldown_seconds:
            logger.info(
                "[%s] 쿨다운 중: %.0f초 남음",
                symbol, self.cooldown_seconds - elapsed,
            )
            return False
        return True

    # ------------------------------------------------------------------
    # 거래 등록
    # ------------------------------------------------------------------

    def record_trade(self, symbol: str) -> None:
        """
        체결 기록 (거래 카운트 증가, 쿨다운 시작)

        Parameters
        ----------
        symbol : str  종목코드
        """
        self._trade_count_today += 1
        self._last_trade_time[symbol] = datetime.now()
        logger.info(
            "거래 기록: %s | 오늘 거래 수: %d/%d",
            symbol, self._trade_count_today, self.max_trades_per_day,
        )

    # ------------------------------------------------------------------
    # 포지션 사이징
    # ------------------------------------------------------------------

    def position_size(
        self,
        symbol: str,
        price: float,
        target_pct: Optional[float] = None,
    ) -> PositionSizeResult:
        """
        포지션 사이징 계산

        Parameters
        ----------
        symbol     : 종목코드
        price      : 현재가
        target_pct : 목표 비중 (None 이면 max_position_pct 사용)

        Returns
        -------
        PositionSizeResult
        """
        pct = min(target_pct or self.max_position_pct, self.max_position_pct)
        allowed_value = self._portfolio_value * pct
        suggested_qty = allowed_value / price if price > 0 else 0

        return PositionSizeResult(
            symbol=symbol,
            allowed_pct=pct,
            allowed_value=round(allowed_value, 2),
            suggested_qty=int(suggested_qty),  # 정수 수량 (소수주 불가 시)
            price=price,
        )

    # ------------------------------------------------------------------
    # 시스템 정지 / 재개
    # ------------------------------------------------------------------

    def _halt(self, reason: str) -> None:
        if not self._is_halted:
            self._is_halted   = True
            self._halt_reason = reason
            logger.critical("🚨 거래 시스템 정지: %s", reason)

    def _resume(self, reason: str = "") -> None:
        self._is_halted   = False
        self._halt_reason = ""
        logger.info("✅ 거래 시스템 재개: %s", reason)

    def force_halt(self, reason: str = "수동 정지") -> None:
        """외부에서 강제 정지 호출"""
        self._halt(reason)

    def force_resume(self) -> None:
        """외부에서 강제 재개 호출 (주의: MDD 초과 상태에서도 재개됨)"""
        self._resume("수동 재개")

    # ------------------------------------------------------------------
    # 상태 조회
    # ------------------------------------------------------------------

    @property
    def stop_reason(self) -> str:
        """정지 이유 (정지 중이 아니면 빈 문자열)"""
        return self._halt_reason

    def get_snapshot(self) -> RiskSnapshot:
        """현재 리스크 상태 스냅샷 반환"""
        return RiskSnapshot(
            timestamp=datetime.now(),
            portfolio_value=self._portfolio_value,
            peak_value=self._peak_value,
            daily_start_value=self._daily_start_value,
            daily_pnl=self._portfolio_value - self._daily_start_value,
            daily_pnl_pct=self._calc_daily_pnl_pct(),
            mdd=self._calc_mdd(),
            trade_count_today=self._trade_count_today,
            is_halted=self._is_halted,
            halt_reason=self._halt_reason,
        )

    def print_status(self) -> None:
        """현재 리스크 상태 출력"""
        s = self.get_snapshot()
        status = "🔴 정지" if s.is_halted else "🟢 정상"
        print(f"\n{'─'*55}")
        print(f"  [{status}] 리스크 모니터 – {s.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'─'*55}")
        print(f"  총 자산        : {s.portfolio_value:>15,.0f}")
        print(f"  고점           : {s.peak_value:>15,.0f}")
        print(f"  일일 손익      : {s.daily_pnl:>+15,.0f}  ({s.daily_pnl_pct*100:+.2f}%)")
        print(f"  MDD            : {s.mdd*100:>14.2f}%  (한도: {self.max_mdd_limit*100:.1f}%)")
        print(f"  오늘 거래 수   : {s.trade_count_today:>14}건  (한도: {self.max_trades_per_day}건)")
        if s.is_halted:
            print(f"  정지 사유      : {s.halt_reason}")
        print(f"{'─'*55}\n")


# ---------------------------------------------------------------------------
# 예제 실행
# ---------------------------------------------------------------------------

def _demo() -> None:
    print("=== RiskManager 데모 ===\n")

    rm = RiskManager(
        daily_loss_limit=0.02,    # 일일 2% 손실 한도
        max_mdd_limit=0.10,       # MDD 10% 한도
        max_position_pct=0.20,    # 단일 종목 20% 한도
        max_trades_per_day=5,
    )
    rm.set_portfolio_value(10_000_000)

    # 거래 시뮬레이션
    scenarios = [
        (10_050_000, "소폭 상승"),
        (9_980_000,  "소폭 하락"),
        (9_850_000,  "일일 1.5% 손실"),
        (9_750_000,  "일일 2.5% 손실 → 정지 예상"),
    ]

    for value, desc in scenarios:
        rm.update_portfolio_value(value)
        snap = rm.get_snapshot()
        print(
            f"  {desc:<22} | 자산: {value:,} | "
            f"일손익: {snap.daily_pnl_pct*100:+.2f}% | "
            f"MDD: {snap.mdd*100:.2f}% | "
            f"거래가능: {'✅' if not snap.is_halted else '🚫'}"
        )
        if snap.is_halted:
            print(f"    ↳ 정지 사유: {snap.halt_reason}")
            break

    # 포지션 사이징
    rm2 = RiskManager()
    rm2.set_portfolio_value(10_000_000)
    size = rm2.position_size("AAPL", price=150.0)
    print(f"\n  포지션 사이징 – AAPL @ $150.0")
    print(f"    허용 비중: {size.allowed_pct*100:.0f}%  허용 금액: {size.allowed_value:,.0f}  수량: {size.suggested_qty}주")


if __name__ == "__main__":
    _demo()
