# Day 132 – RSI (상대강도지수)

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (중급)

---

## 🎯 학습 목표

- RSI(Relative Strength Index) 계산 원리 이해
- pandas로 RSI 직접 구현
- 과매수(overbought)·과매도(oversold) 매매 신호 탐지
- RSI 다이버전스(divergence) 개념 이해

---

## 📖 이론 (08:00 – 10:00)

### 1. RSI 계산 공식
```
RSI = 100 - (100 / (1 + RS))
RS  = 평균 상승폭 / 평균 하락폭
```

- 기간: 보통 14일 사용
- 범위: 0 ~ 100
- **70 이상**: 과매수 → 매도 고려
- **30 이하**: 과매도 → 매수 고려
- **50 기준**: 상승(50 이상) / 하락(50 이하) 추세 구분

### 2. 계산 단계
```python
delta = close.diff()
gain  = delta.clip(lower=0)     # 상승분만
loss  = (-delta).clip(lower=0)  # 하락분만 (양수로 변환)

# Wilder의 지수이동평균 (EWM with alpha=1/period)
avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

rs  = avg_gain / avg_loss
rsi = 100 - (100 / (1 + rs))
```

### 3. RSI 다이버전스
- **강세 다이버전스**: 가격은 신저점, RSI는 상승 → 반등 신호
- **약세 다이버전스**: 가격은 신고점, RSI는 하락 → 하락 신호

---

## 🧪 LAB 1 – RSI 직접 구현 (10:00 – 12:00)

```python
# rsi.py
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """RSI 계산 함수"""
    delta = close.diff()
    gain  = delta.clip(lower=0)
    loss  = (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    rs  = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df = yf.download("AAPL", period="1y", auto_adjust=True)[["Close"]]
df.columns = ["Close"]
df["RSI14"] = compute_rsi(df["Close"], 14)

print("=== RSI 기초 통계 ===")
print(df["RSI14"].describe().round(2))

# 매매 신호 날짜 출력
overbought = df[df["RSI14"] > 70]
oversold   = df[df["RSI14"] < 30]
print(f"\n과매수(RSI>70): {len(overbought)}일")
print(f"과매도(RSI<30): {len(oversold)}일")
```

---

## 🧪 LAB 2 – RSI 매매 신호 시각화 (13:00 – 15:00)

```python
# rsi_chart.py
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain, loss = delta.clip(lower=0), (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    return 100 - (100 / (1 + avg_gain / avg_loss))

df = yf.download("005930.KS", period="1y", auto_adjust=True)[["Close"]]
df.columns = ["Close"]
df["RSI14"] = compute_rsi(df["Close"])
df = df.dropna()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8),
                                gridspec_kw={"height_ratios": [2, 1]},
                                sharex=True)

# 주가 차트
ax1.plot(df.index, df["Close"], linewidth=1.5, color="steelblue")
ax1.set_title("삼성전자 – 주가 & RSI(14)", fontsize=13)
ax1.set_ylabel("Price (KRW)")
ax1.grid(alpha=0.3)

# RSI 차트
ax2.plot(df.index, df["RSI14"], linewidth=1.5, color="purple")
ax2.axhline(y=70, color="red",   linestyle="--", linewidth=1, label="과매수(70)")
ax2.axhline(y=30, color="green", linestyle="--", linewidth=1, label="과매도(30)")
ax2.axhline(y=50, color="gray",  linestyle=":",  linewidth=0.8)
ax2.fill_between(df.index, 70, 100, alpha=0.08, color="red")
ax2.fill_between(df.index, 0, 30,  alpha=0.08, color="green")
ax2.set_ylim(0, 100)
ax2.set_ylabel("RSI")
ax2.legend(loc="upper right")
ax2.grid(alpha=0.3)

# 과매도 구간에 매수 마커 표시
buy_signals = df[df["RSI14"] < 30]
ax1.scatter(buy_signals.index, buy_signals["Close"],
            marker="^", color="lime", s=100, zorder=5, label="매수 신호")
ax1.legend()

plt.tight_layout()
plt.savefig("rsi_chart.png", dpi=150)
plt.show()
```

---

## 🧪 LAB 3 – RSI 기반 전략 수익률 계산 (15:00 – 17:00)

```python
# rsi_strategy.py
import yfinance as yf
import pandas as pd
import numpy as np

def compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain, loss = delta.clip(lower=0), (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    return 100 - (100 / (1 + avg_gain / avg_loss))

df = yf.download("AAPL", period="5y", auto_adjust=True)[["Close"]]
df.columns = ["Close"]
df["RSI14"] = compute_rsi(df["Close"])
df = df.dropna()

# 전략: RSI < 30 → 매수, RSI > 70 → 매도
position = 0
signals = []
for i, row in df.iterrows():
    if row["RSI14"] < 30 and position == 0:
        position = 1   # 매수
    elif row["RSI14"] > 70 and position == 1:
        position = 0   # 매도
    signals.append(position)

df["Position"] = signals
df["Position"] = df["Position"].shift(1)  # 신호 다음날 실행
df["Daily_Return"]    = df["Close"].pct_change()
df["Strategy_Return"] = df["Daily_Return"] * df["Position"]

df["Cum_BH"]  = (1 + df["Daily_Return"]).cumprod()
df["Cum_RSI"] = (1 + df["Strategy_Return"]).cumprod()
df = df.dropna()

print(f"Buy & Hold 수익률: {(df['Cum_BH'].iloc[-1]-1)*100:.2f}%")
print(f"RSI 전략 수익률:   {(df['Cum_RSI'].iloc[-1]-1)*100:.2f}%")
print(f"보유 비율: {df['Position'].mean()*100:.1f}% (현금 보유 {(1-df['Position'].mean())*100:.1f}%)")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df.index, df["Cum_BH"],  label="Buy & Hold")
ax.plot(df.index, df["Cum_RSI"], label="RSI 전략")
ax.set_title("RSI 전략 vs Buy & Hold (5년)")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("rsi_strategy.png", dpi=150)
plt.show()
```

---

## 📝 과제 (17:00 – 18:00)

1. RSI 기간(period)을 9·14·21로 바꾸면서 전략 수익률이 어떻게 달라지는지 비교하세요.
2. 과매수/과매도 임계값을 70/30 대신 80/20으로 변경했을 때의 거래 횟수와 수익률을 비교하세요.
3. RSI + MA20 복합 조건(RSI < 35 AND Close > MA20)으로 필터링한 매수 신호를 구현하세요.

---

## ✅ 체크리스트

- [ ] RSI 계산 공식 이해 및 직접 구현 성공
- [ ] 과매수·과매도 신호 탐지 및 차트 시각화 완료
- [ ] RSI 기반 전략 수익률 계산 성공
- [ ] RSI 기간 파라미터 실험 완료
- [ ] 과제 제출

---

## 📚 참고자료

- [Investopedia – RSI](https://www.investopedia.com/terms/r/rsi.asp)
- [RSI 계산 원리 (Wilder)](https://school.stockcharts.com/doku.php?id=technical_indicators:relative_strength_index_rsi)
