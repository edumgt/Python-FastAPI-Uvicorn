# Day 137 – 자동매매 로직

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (중급)

---

## 🎯 학습 목표

- 실시간 매매 신호 생성 로직 설계
- 포지션 상태 관리(진입·청산·리밸런싱)
- 손절(Stop-Loss)·익절(Take-Profit) 조건 구현
- 모의투자 주문 시뮬레이터 구축

---

## 📖 이론 (08:00 – 10:00)

### 1. 자동매매 시스템 구성
```
데이터 수집 → 지표 계산 → 신호 판단 → 주문 실행 → 리스크 관리
```

### 2. 포지션 관리 상태 머신
```
[FLAT] --[매수 신호]--> [LONG] --[매도 신호 or 손절/익절]--> [FLAT]
```

### 3. 손절·익절 전략
```python
# 고정 비율 방식
stop_loss   = entry_price * (1 - 0.05)   # 5% 손절
take_profit = entry_price * (1 + 0.10)  # 10% 익절

# ATR 기반 방식
stop_loss   = entry_price - 2 * atr
take_profit = entry_price + 3 * atr
```

---

## 🧪 LAB 1 – 신호 생성기 클래스 (10:00 – 12:00)

```python
# signal_generator.py
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum

class Signal(Enum):
    BUY  = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

@dataclass
class SignalResult:
    signal: Signal
    reason: str
    strength: float  # 0.0 ~ 1.0

class MACrossSignalGenerator:
    """MA 크로스오버 신호 생성기"""

    def __init__(self, fast: int = 5, slow: int = 20):
        self.fast = fast
        self.slow = slow

    def generate(self, df: pd.DataFrame) -> pd.Series:
        ma_fast = df["Close"].rolling(self.fast).mean()
        ma_slow = df["Close"].rolling(self.slow).mean()
        prev_diff = (ma_fast - ma_slow).shift(1)
        curr_diff = ma_fast - ma_slow
        signals = pd.Series(Signal.HOLD, index=df.index)
        signals[(prev_diff < 0) & (curr_diff >= 0)] = Signal.BUY
        signals[(prev_diff > 0) & (curr_diff <= 0)] = Signal.SELL
        return signals

class RSISignalGenerator:
    """RSI 과매수·과매도 신호 생성기"""

    def __init__(self, period: int = 14, oversold: float = 30,
                 overbought: float = 70):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def _rsi(self, close: pd.Series) -> pd.Series:
        delta = close.diff()
        gain, loss = delta.clip(lower=0), (-delta).clip(lower=0)
        avg_gain = gain.ewm(alpha=1/self.period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/self.period, adjust=False).mean()
        return 100 - 100 / (1 + avg_gain / avg_loss)

    def generate(self, df: pd.DataFrame) -> pd.Series:
        rsi = self._rsi(df["Close"])
        prev_rsi = rsi.shift(1)
        signals = pd.Series(Signal.HOLD, index=df.index)
        signals[(prev_rsi >= self.oversold) & (rsi < self.oversold)] = Signal.BUY
        signals[(prev_rsi <= self.overbought) & (rsi > self.overbought)] = Signal.SELL
        return signals
```

---

## 🧪 LAB 2 – 포지션 관리 & 손절·익절 (13:00 – 15:00)

```python
# position_manager.py
import yfinance as yf
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Trade:
    entry_date: object
    entry_price: float
    stop_loss: float
    take_profit: float
    shares: int = 1
    exit_date: Optional[object] = None
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    exit_reason: str = ""

class PositionManager:
    """포지션 진입·청산 관리"""

    def __init__(self, stop_pct: float = 0.05, tp_pct: float = 0.10,
                 capital: float = 10_000_000):
        self.stop_pct = stop_pct
        self.tp_pct   = tp_pct
        self.capital  = capital
        self.position: Optional[Trade] = None
        self.trades: list[Trade] = []
        self.equity   = capital

    def enter(self, date, price: float) -> None:
        shares = int(self.equity * 0.95 / price)  # 95% 투자
        self.position = Trade(
            entry_date=date,
            entry_price=price,
            stop_loss=price * (1 - self.stop_pct),
            take_profit=price * (1 + self.tp_pct),
            shares=shares,
        )

    def exit(self, date, price: float, reason: str) -> None:
        if self.position is None:
            return
        p = self.position
        p.exit_date  = date
        p.exit_price = price
        p.pnl        = (price - p.entry_price) * p.shares
        p.exit_reason = reason
        self.equity  += p.pnl
        self.trades.append(p)
        self.position = None

    def check_exit(self, date, current_price: float) -> bool:
        if self.position is None:
            return False
        if current_price <= self.position.stop_loss:
            self.exit(date, current_price, "STOP_LOSS")
            return True
        if current_price >= self.position.take_profit:
            self.exit(date, current_price, "TAKE_PROFIT")
            return True
        return False


# 시뮬레이션
import yfinance as yf
import numpy as np

df = yf.download("AAPL", period="2y", auto_adjust=True)[["Close"]]
df.columns = ["Close"]
df["MA5"]  = df["Close"].rolling(5).mean()
df["MA20"] = df["Close"].rolling(20).mean()
df = df.dropna()

pm = PositionManager(stop_pct=0.05, tp_pct=0.10)
for date, row in df.iterrows():
    price = float(row["Close"])
    # 손절·익절 체크
    if pm.position:
        if pm.check_exit(date, price):
            continue
    # 매수 신호
    if pm.position is None and row["MA5"] > row["MA20"]:
        pm.enter(date, price)
    # 매도 신호
    elif pm.position and row["MA5"] < row["MA20"]:
        pm.exit(date, price, "SIGNAL")

trade_df = pd.DataFrame([{
    "진입일": t.entry_date.date(), "진입가": t.entry_price,
    "청산일": t.exit_date.date() if t.exit_date else None,
    "청산가": t.exit_price, "수익": t.pnl, "이유": t.exit_reason
} for t in pm.trades])

if not trade_df.empty:
    print(trade_df.to_string(index=False))
    wins = trade_df[trade_df["수익"] > 0]
    print(f"\n총 거래: {len(trade_df)}회 | 승률: {len(wins)/len(trade_df)*100:.1f}%")
    print(f"최종 자산: {pm.equity:,.0f}원 (수익률 {(pm.equity/pm.capital-1)*100:.2f}%)")
```

---

## 🧪 LAB 3 – 자동매매 스케줄러 시뮬레이션 (15:00 – 17:00)

```python
# scheduler_sim.py
# 실제 자동매매에서는 APScheduler, cron 등을 사용
# 여기서는 "매일 장 마감 후 신호 확인" 시뮬레이션

import yfinance as yf
import pandas as pd
import numpy as np

def daily_signal_check(symbol: str) -> dict:
    """매일 실행될 신호 확인 함수"""
    df = yf.download(symbol, period="3mo", auto_adjust=True)[["Close"]].squeeze()
    close = df if isinstance(df, pd.Series) else df["Close"]
    close.name = "Close"
    close = close.dropna()

    ma5  = close.rolling(5).mean()
    ma20 = close.rolling(20).mean()
    rsi  = (lambda c, p=14: 100 - 100/(1 + c.diff().clip(lower=0).ewm(alpha=1/p,adjust=False).mean() /
            (-c.diff()).clip(lower=0).ewm(alpha=1/p, adjust=False).mean()))(close)

    current = float(close.iloc[-1])
    ma5_now, ma20_now = float(ma5.iloc[-1]), float(ma20.iloc[-1])
    rsi_now = float(rsi.iloc[-1])

    if ma5_now > ma20_now and rsi_now < 70:
        signal = "매수 고려"
    elif ma5_now < ma20_now and rsi_now > 30:
        signal = "매도 고려"
    else:
        signal = "관망"

    return {
        "종목": symbol, "현재가": current,
        "MA5": round(ma5_now, 2), "MA20": round(ma20_now, 2),
        "RSI14": round(rsi_now, 2), "신호": signal,
    }

watchlist = ["AAPL", "MSFT", "NVDA", "005930.KS"]
print("=== 오늘의 매매 신호 ===")
for symbol in watchlist:
    try:
        result = daily_signal_check(symbol)
        print(f"[{result['종목']}] 현재가:{result['현재가']:.2f}  "
              f"RSI:{result['RSI14']:.1f}  신호:{result['신호']}")
    except Exception as e:
        print(f"[{symbol}] 오류: {e}")
```

---

## 📝 과제 (17:00 – 18:00)

1. 손절(5%)·익절(10%) 설정 대신 ATR 기반 동적 손절가를 `PositionManager`에 추가하세요.
2. 여러 종목에 동시에 포지션을 취하는 다종목 포트폴리오 관리 로직을 구현하세요.
3. 자동매매 일지(CSV): 날짜·매매방향·가격·수량·잔고를 기록하는 기능을 추가하세요.

---

## ✅ 체크리스트

- [ ] 신호 생성기 클래스 구현 성공
- [ ] 포지션 관리 + 손절·익절 로직 구현 성공
- [ ] 거래 내역 분석 (승률·평균 수익) 완료
- [ ] 일일 신호 확인 스케줄러 시뮬레이션 완료
- [ ] 과제 제출

---

## 📚 참고자료

- [KIS Open API – 모의투자 주문](https://apiportal.koreainvestment.com)
- [APScheduler 공식 문서](https://apscheduler.readthedocs.io)
- [Investopedia – Stop-Loss](https://www.investopedia.com/terms/s/stop-lossorder.asp)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day137+auto+trading
