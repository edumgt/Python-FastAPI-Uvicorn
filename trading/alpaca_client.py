"""
Alpaca Markets API 연동 모듈
==============================
Alpaca Paper / Live Trading REST API + 과거 데이터 조회

필요 패키지:
    pip install alpaca-py

환경변수 설정 (.env):
    ALPACA_API_KEY=<your_api_key>
    ALPACA_SECRET_KEY=<your_secret_key>

Paper Trading(모의투자) URL : https://paper-api.alpaca.markets
Live Trading URL            : https://api.alpaca.markets
공식 문서                    : https://docs.alpaca.markets/docs/getting-started
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

# ---------------------------------------------------------------------------
# 선택적 임포트 – alpaca-py 미설치 환경에서도 모듈 로드 가능
# ---------------------------------------------------------------------------
try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame
    _ALPACA_AVAILABLE = True
except ImportError:
    _ALPACA_AVAILABLE = False


# ---------------------------------------------------------------------------
# 데이터 모델
# ---------------------------------------------------------------------------

@dataclass
class OrderResult:
    """주문 결과"""
    order_id: str
    symbol: str
    qty: float
    side: str          # "buy" | "sell"
    order_type: str    # "market" | "limit"
    limit_price: Optional[float] = None
    status: str = "submitted"


@dataclass
class PositionInfo:
    """포지션 정보"""
    symbol: str
    qty: float
    avg_entry_price: float
    current_price: float
    unrealized_pl: float
    unrealized_plpc: float   # 수익률 (소수, 예: 0.05 = 5%)
    side: str                # "long" | "short"


@dataclass
class AccountInfo:
    """계좌 정보"""
    account_id: str
    cash: float
    portfolio_value: float
    buying_power: float
    equity: float
    daytrade_count: int
    status: str


# ---------------------------------------------------------------------------
# AlpacaTrader 클래스
# ---------------------------------------------------------------------------

class AlpacaTrader:
    """
    Alpaca Markets 자동매매 클라이언트

    Parameters
    ----------
    api_key : str | None
        Alpaca API Key (없으면 환경변수 ALPACA_API_KEY 사용)
    secret_key : str | None
        Alpaca Secret Key (없으면 환경변수 ALPACA_SECRET_KEY 사용)
    paper : bool
        True → Paper Trading (모의투자), False → Live Trading

    Examples
    --------
    >>> trader = AlpacaTrader(paper=True)
    >>> account = trader.get_account()
    >>> print(account.cash)

    >>> df = trader.get_bars("AAPL", days=30)
    >>> signal = trader.ma_cross_signal("AAPL")
    >>> if signal["signal"] == "BUY":
    ...     trader.market_order("AAPL", qty=1, side="buy")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        paper: bool = True,
    ) -> None:
        if not _ALPACA_AVAILABLE:
            raise ImportError(
                "alpaca-py 패키지가 설치되지 않았습니다.\n"
                "설치 명령: pip install alpaca-py"
            )

        self.api_key = api_key or os.getenv("ALPACA_API_KEY", "")
        self.secret_key = secret_key or os.getenv("ALPACA_SECRET_KEY", "")
        self.paper = paper

        if not self.api_key or not self.secret_key:
            raise ValueError(
                "ALPACA_API_KEY 와 ALPACA_SECRET_KEY 를 환경변수로 설정하거나 "
                "인자로 전달하세요."
            )

        self._trading = TradingClient(self.api_key, self.secret_key, paper=self.paper)
        self._data = StockHistoricalDataClient(self.api_key, self.secret_key)

    # ------------------------------------------------------------------
    # 계좌 / 포지션 조회
    # ------------------------------------------------------------------

    def get_account(self) -> AccountInfo:
        """계좌 정보 조회"""
        acc = self._trading.get_account()
        return AccountInfo(
            account_id=str(acc.id),
            cash=float(acc.cash),
            portfolio_value=float(acc.portfolio_value),
            buying_power=float(acc.buying_power),
            equity=float(acc.equity),
            daytrade_count=acc.daytrade_count,
            status=str(acc.status),
        )

    def get_positions(self) -> list[PositionInfo]:
        """보유 포지션 전체 조회"""
        return [
            PositionInfo(
                symbol=p.symbol,
                qty=float(p.qty),
                avg_entry_price=float(p.avg_entry_price),
                current_price=float(p.current_price),
                unrealized_pl=float(p.unrealized_pl),
                unrealized_plpc=float(p.unrealized_plpc),
                side=str(p.side),
            )
            for p in self._trading.get_all_positions()
        ]

    def get_position(self, symbol: str) -> Optional[PositionInfo]:
        """특정 종목 포지션 조회 (없으면 None)"""
        try:
            p = self._trading.get_open_position(symbol)
            return PositionInfo(
                symbol=p.symbol,
                qty=float(p.qty),
                avg_entry_price=float(p.avg_entry_price),
                current_price=float(p.current_price),
                unrealized_pl=float(p.unrealized_pl),
                unrealized_plpc=float(p.unrealized_plpc),
                side=str(p.side),
            )
        except Exception:
            return None

    # ------------------------------------------------------------------
    # 주문
    # ------------------------------------------------------------------

    def market_order(self, symbol: str, qty: float, side: str) -> OrderResult:
        """
        시장가 주문

        Parameters
        ----------
        symbol : str   종목 코드 (예: "AAPL", "TSLA")
        qty    : float 수량
        side   : str   "buy" 또는 "sell"
        """
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        req = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=order_side,
            time_in_force=TimeInForce.GTC,
        )
        o = self._trading.submit_order(req)
        return OrderResult(
            order_id=str(o.id),
            symbol=o.symbol,
            qty=float(o.qty),
            side=str(o.side),
            order_type="market",
            status=str(o.status),
        )

    def limit_order(
        self, symbol: str, qty: float, side: str, limit_price: float
    ) -> OrderResult:
        """
        지정가 주문

        Parameters
        ----------
        symbol      : str   종목 코드
        qty         : float 수량
        side        : str   "buy" 또는 "sell"
        limit_price : float 지정가
        """
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        req = LimitOrderRequest(
            symbol=symbol,
            qty=qty,
            side=order_side,
            time_in_force=TimeInForce.GTC,
            limit_price=limit_price,
        )
        o = self._trading.submit_order(req)
        return OrderResult(
            order_id=str(o.id),
            symbol=o.symbol,
            qty=float(o.qty),
            side=str(o.side),
            order_type="limit",
            limit_price=float(o.limit_price),
            status=str(o.status),
        )

    def cancel_all_orders(self) -> None:
        """미체결 주문 전체 취소"""
        self._trading.cancel_orders()

    def close_position(self, symbol: str) -> None:
        """특정 종목 포지션 전량 청산"""
        self._trading.close_position(symbol)

    def close_all_positions(self) -> None:
        """전체 포지션 청산"""
        self._trading.close_all_positions(cancel_orders=True)

    # ------------------------------------------------------------------
    # 데이터 조회
    # ------------------------------------------------------------------

    def get_bars(
        self,
        symbol: str,
        days: int = 60,
        timeframe: str = "1Day",
    ) -> pd.DataFrame:
        """
        과거 OHLCV 데이터 조회

        Parameters
        ----------
        symbol    : str  종목 코드
        days      : int  최근 N일치 데이터
        timeframe : str  "1Min" | "1Hour" | "1Day"

        Returns
        -------
        pd.DataFrame  컬럼: Open, High, Low, Close, Volume
        """
        tf_map = {
            "1Min":  TimeFrame.Minute,
            "1Hour": TimeFrame.Hour,
            "1Day":  TimeFrame.Day,
        }
        tf = tf_map.get(timeframe, TimeFrame.Day)

        req = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=tf,
            start=datetime.now() - timedelta(days=days),
        )
        bars = self._data.get_stock_bars(req)
        df = bars.df

        # MultiIndex(symbol, timestamp) → timestamp 만 사용
        if isinstance(df.index, pd.MultiIndex):
            df = df.xs(symbol, level="symbol")

        df.index.name = "timestamp"
        return df[["open", "high", "low", "close", "volume"]].rename(
            columns={
                "open": "Open", "high": "High", "low": "Low",
                "close": "Close", "volume": "Volume",
            }
        )

    # ------------------------------------------------------------------
    # 신호 생성
    # ------------------------------------------------------------------

    def ma_cross_signal(
        self, symbol: str, fast: int = 5, slow: int = 20
    ) -> dict:
        """
        MA 크로스오버 신호 생성

        Returns
        -------
        dict  {"symbol", "signal"("BUY"|"SELL"|"HOLD"), "price", "MA{fast}", "MA{slow}"}
        """
        df = self.get_bars(symbol, days=max(slow * 3, 90))
        df[f"MA{fast}"]  = df["Close"].rolling(fast).mean()
        df[f"MA{slow}"] = df["Close"].rolling(slow).mean()
        df = df.dropna()

        latest = df.iloc[-1]
        prev   = df.iloc[-2]

        if (prev[f"MA{fast}"] <= prev[f"MA{slow}"]) and (latest[f"MA{fast}"] > latest[f"MA{slow}"]):
            signal = "BUY"
        elif (prev[f"MA{fast}"] >= prev[f"MA{slow}"]) and (latest[f"MA{fast}"] < latest[f"MA{slow}"]):
            signal = "SELL"
        else:
            signal = "HOLD"

        return {
            "symbol":       symbol,
            "signal":       signal,
            "price":        round(float(latest["Close"]), 4),
            f"MA{fast}":    round(float(latest[f"MA{fast}"]), 4),
            f"MA{slow}":   round(float(latest[f"MA{slow}"]), 4),
        }

    def rsi_signal(
        self,
        symbol: str,
        period: int = 14,
        oversold: float = 30.0,
        overbought: float = 70.0,
    ) -> dict:
        """
        RSI 기반 신호 생성

        Returns
        -------
        dict  {"symbol", "signal", "price", "rsi"}
        """
        df = self.get_bars(symbol, days=period * 5)
        close = df["Close"]
        delta = close.diff()
        gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
        loss = (-delta).clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
        rsi = 100 - 100 / (1 + gain / loss)

        current_rsi  = float(rsi.iloc[-1])
        prev_rsi     = float(rsi.iloc[-2])
        current_price = float(close.iloc[-1])

        if prev_rsi >= oversold and current_rsi < oversold:
            signal = "BUY"
        elif prev_rsi <= overbought and current_rsi > overbought:
            signal = "SELL"
        else:
            signal = "HOLD"

        return {
            "symbol": symbol,
            "signal": signal,
            "price":  round(current_price, 4),
            "rsi":    round(current_rsi, 2),
        }


# ---------------------------------------------------------------------------
# 예제 실행 (직접 실행 시)
# ---------------------------------------------------------------------------

def _demo() -> None:
    """
    Paper Trading 데모
    실행 전 .env 또는 환경변수에 ALPACA_API_KEY / ALPACA_SECRET_KEY 설정 필요
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    trader = AlpacaTrader(paper=True)

    print("=== 계좌 정보 ===")
    acc = trader.get_account()
    print(f"  자산: ${acc.portfolio_value:,.2f}  |  현금: ${acc.cash:,.2f}")
    print(f"  상태: {acc.status}")

    print("\n=== 종목 신호 확인 ===")
    watchlist = ["AAPL", "MSFT", "NVDA", "TSLA"]
    for sym in watchlist:
        try:
            sig = trader.ma_cross_signal(sym)
            rsi = trader.rsi_signal(sym)
            print(
                f"  [{sym}] 현재가: ${sig['price']:,.2f} | "
                f"MA크로스: {sig['signal']} | RSI: {rsi['rsi']:.1f} ({rsi['signal']})"
            )
        except Exception as exc:
            print(f"  [{sym}] 오류: {exc}")

    print("\n=== 포지션 현황 ===")
    positions = trader.get_positions()
    if positions:
        for pos in positions:
            pl_pct = pos.unrealized_plpc * 100
            print(
                f"  {pos.symbol}: {pos.qty}주 @ ${pos.avg_entry_price:.2f} | "
                f"평가손익: ${pos.unrealized_pl:,.2f} ({pl_pct:+.2f}%)"
            )
    else:
        print("  보유 포지션 없음")


if __name__ == "__main__":
    _demo()
