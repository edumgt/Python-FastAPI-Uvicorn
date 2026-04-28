# Day 133 – MACD (이동평균 수렴·발산)

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (중급)

---

## 🎯 학습 목표

- MACD 계산 구조(MACD선·시그널선·히스토그램) 이해
- pandas로 MACD 직접 구현
- MACD 매매 신호(크로스오버, 제로선 돌파) 탐지
- MACD + RSI 복합 전략 설계

---

## 📖 이론 (08:00 – 10:00)

### 1. MACD 구성 요소
| 구성 요소 | 계산 | 의미 |
|-----------|------|------|
| MACD선 | EMA(12) - EMA(26) | 단기-장기 추세 차이 |
| 시그널선 | MACD의 EMA(9) | MACD 평활화 |
| 히스토그램 | MACD선 - 시그널선 | 추세 강도 및 방향 |

```python
macd   = ema12 - ema26
signal = macd.ewm(span=9, adjust=False).mean()
hist   = macd - signal
```

### 2. 매매 신호
- **MACD 크로스오버**: MACD선이 시그널선을 **상향** 돌파 → 매수
- **MACD 크로스언더**: MACD선이 시그널선을 **하향** 돌파 → 매도
- **제로선 돌파**: MACD가 0 위로 상승 → 상승추세 확인
- **히스토그램 전환**: 음수→양수 전환 → 모멘텀 전환 신호

### 3. 표준 파라미터
- 단기 EMA: 12일
- 장기 EMA: 26일
- 시그널: 9일
- 표기: MACD(12,26,9)

---

## 🧪 LAB 1 – MACD 구현 (10:00 – 12:00)

```python
# macd.py
import yfinance as yf
import pandas as pd

def compute_macd(close: pd.Series,
                 fast: int = 12, slow: int = 26,
                 signal: int = 9) -> pd.DataFrame:
    """MACD, 시그널선, 히스토그램 계산"""
    ema_fast   = close.ewm(span=fast,   adjust=False).mean()
    ema_slow   = close.ewm(span=slow,   adjust=False).mean()
    macd_line  = ema_fast - ema_slow
    signal_line= macd_line.ewm(span=signal, adjust=False).mean()
    histogram  = macd_line - signal_line
    return pd.DataFrame({
        "MACD":   macd_line,
        "Signal": signal_line,
        "Hist":   histogram,
    })

df = yf.download("AAPL", period="1y", auto_adjust=True)[["Close"]]
df.columns = ["Close"]
macd_df = compute_macd(df["Close"])
df = pd.concat([df, macd_df], axis=1)

print("=== MACD 최근 5행 ===")
print(df.tail().round(4))
print(f"\nMACD 값 범위: {df['MACD'].min():.3f} ~ {df['MACD'].max():.3f}")
```

---

## 🧪 LAB 2 – MACD 차트 시각화 (13:00 – 15:00)

```python
# macd_chart.py
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def compute_macd(close, fast=12, slow=26, signal=9):
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    sig  = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - sig
    return macd, sig, hist

df = yf.download("005930.KS", period="1y", auto_adjust=True)[["Close"]]
df.columns = ["Close"]
df["MACD"], df["Signal"], df["Hist"] = compute_macd(df["Close"])
df = df.dropna()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9),
                                gridspec_kw={"height_ratios": [2, 1]},
                                sharex=True)

# 주가
ax1.plot(df.index, df["Close"], linewidth=1.5, color="steelblue", label="Close")
ax1.set_title("삼성전자 – MACD(12,26,9)", fontsize=13)
ax1.set_ylabel("Price (KRW)")
ax1.legend()
ax1.grid(alpha=0.3)

# MACD
ax2.plot(df.index, df["MACD"],   label="MACD",   color="blue", linewidth=1.5)
ax2.plot(df.index, df["Signal"], label="Signal", color="orange", linewidth=1.2)
ax2.axhline(0, color="gray", linewidth=0.8, linestyle="--")

# 히스토그램 색깔 (양수=초록, 음수=빨강)
colors = ["green" if v >= 0 else "red" for v in df["Hist"]]
ax2.bar(df.index, df["Hist"], color=colors, alpha=0.5, width=1, label="Histogram")
ax2.set_ylabel("MACD")
ax2.legend()
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("macd_chart.png", dpi=150)
plt.show()
```

---

## 🧪 LAB 3 – MACD 크로스오버 전략 (15:00 – 17:00)

```python
# macd_strategy.py
import yfinance as yf
import pandas as pd
import numpy as np

def compute_macd(close, fast=12, slow=26, signal=9):
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    sig  = macd.ewm(span=signal, adjust=False).mean()
    return macd, sig

df = yf.download("AAPL", period="5y", auto_adjust=True)[["Close"]]
df.columns = ["Close"]
df["MACD"], df["Signal_Line"] = compute_macd(df["Close"])
df = df.dropna()

# 크로스오버 신호
prev_diff = df["MACD"].shift(1) - df["Signal_Line"].shift(1)
curr_diff = df["MACD"] - df["Signal_Line"]

df["Buy"]  = (prev_diff < 0) & (curr_diff >= 0)  # 상향 돌파
df["Sell"] = (prev_diff > 0) & (curr_diff <= 0)  # 하향 돌파

# 포지션 관리
position, positions = 0, []
for _, row in df.iterrows():
    if row["Buy"]  and position == 0: position = 1
    if row["Sell"] and position == 1: position = 0
    positions.append(position)

df["Position"] = pd.Series(positions, index=df.index).shift(1)
df["Daily_Return"]    = df["Close"].pct_change()
df["Strategy_Return"] = df["Daily_Return"] * df["Position"]

df["Cum_BH"]   = (1 + df["Daily_Return"]).cumprod()
df["Cum_MACD"] = (1 + df["Strategy_Return"]).cumprod()
df = df.dropna()

buys  = df[df["Buy"]]
sells = df[df["Sell"]]
print(f"매수 신호: {len(buys)}회 | 매도 신호: {len(sells)}회")
print(f"Buy & Hold 수익률: {(df['Cum_BH'].iloc[-1]-1)*100:.2f}%")
print(f"MACD 전략 수익률:  {(df['Cum_MACD'].iloc[-1]-1)*100:.2f}%")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df.index, df["Cum_BH"],   label="Buy & Hold")
ax.plot(df.index, df["Cum_MACD"], label="MACD 전략")
ax.set_title("MACD 크로스오버 전략 vs Buy & Hold (5년)")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("macd_strategy.png", dpi=150)
plt.show()
```

---

## 📝 과제 (17:00 – 18:00)

1. MACD 파라미터를 (8,21,5)로 변경하고 기본값(12,26,9)과 수익률을 비교하세요.
2. MACD + RSI 복합 신호: MACD 상향 크로스 AND RSI < 50 조건으로만 매수하는 전략을 구현하세요.
3. 삼성전자 데이터로 같은 전략을 적용하고 결과를 비교하세요.

---

## ✅ 체크리스트

- [ ] MACD·시그널·히스토그램 계산 구현 성공
- [ ] MACD 차트 시각화(히스토그램 색상 포함) 완료
- [ ] 크로스오버 매매 신호 자동 탐지 성공
- [ ] MACD 전략 수익률 계산 성공
- [ ] 과제 제출

---

## 📚 참고자료

- [Investopedia – MACD](https://www.investopedia.com/terms/m/macd.asp)
- [StockCharts – MACD 가이드](https://school.stockcharts.com/doku.php?id=technical_indicators:moving_average_convergence_divergence_macd)
