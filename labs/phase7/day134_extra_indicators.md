# Day 134 – 추가 지표 (볼린저밴드·스토캐스틱·ATR)

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (중급)

---

## 🎯 학습 목표

- 볼린저밴드(Bollinger Bands)의 구조와 돌파 전략 구현
- 스토캐스틱(Stochastic Oscillator) 계산 및 활용
- ATR(Average True Range)으로 변동성 측정
- 다중 지표 조합 대시보드 구성

---

## 📖 이론 (08:00 – 10:00)

### 1. 볼린저밴드
```
중간선 (BB_mid) = 20일 SMA
상단선 (BB_upper) = BB_mid + 2 × σ20
하단선 (BB_lower) = BB_mid - 2 × σ20
%B = (Close - BB_lower) / (BB_upper - BB_lower)
Bandwidth = (BB_upper - BB_lower) / BB_mid
```
- Close > Upper: 과열, 하락 반전 가능
- Close < Lower: 과매도, 반등 가능
- Bandwidth 수축 후 팽창: 큰 추세 시작 신호

### 2. 스토캐스틱
```
%K = (Close - Lowest_Low_n) / (Highest_High_n - Lowest_Low_n) × 100
%D = %K의 3일 SMA (시그널선)
```
- 80 이상: 과매수 / 20 이하: 과매도
- %K가 %D를 상향 돌파: 매수 신호

### 3. ATR (Average True Range)
```
TR  = max(High-Low, |High-Prev_Close|, |Low-Prev_Close|)
ATR = TR의 14일 EWM
```
- ATR이 클수록 변동성 높음 → 손절폭 설정에 활용

---

## 🧪 LAB 1 – 볼린저밴드 구현 및 전략 (10:00 – 12:00)

```python
# bollinger.py
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

df = yf.download("AAPL", period="1y", auto_adjust=True)[["Close"]]
df.columns = ["Close"]

# 볼린저밴드 계산
window = 20
df["BB_mid"]   = df["Close"].rolling(window).mean()
df["BB_std"]   = df["Close"].rolling(window).std()
df["BB_upper"] = df["BB_mid"] + 2 * df["BB_std"]
df["BB_lower"] = df["BB_mid"] - 2 * df["BB_std"]
df["%B"]       = (df["Close"] - df["BB_lower"]) / (df["BB_upper"] - df["BB_lower"])
df["BW"]       = (df["BB_upper"] - df["BB_lower"]) / df["BB_mid"]

# 매매 신호: 하단 터치 → 매수, 상단 터치 → 매도
df["Buy"]  = df["Close"] <= df["BB_lower"]
df["Sell"] = df["Close"] >= df["BB_upper"]

# 시각화
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8),
                                gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
ax1.plot(df.index, df["Close"],    label="Close",    color="steelblue", lw=1.5)
ax1.plot(df.index, df["BB_mid"],   label="BB_mid",   color="orange",    lw=1.2, ls="--")
ax1.plot(df.index, df["BB_upper"], label="BB_upper", color="red",       lw=1,   ls="--")
ax1.plot(df.index, df["BB_lower"], label="BB_lower", color="green",     lw=1,   ls="--")
ax1.fill_between(df.index, df["BB_lower"], df["BB_upper"], alpha=0.07, color="gray")
ax1.scatter(df.index[df["Buy"]],  df["Close"][df["Buy"]],  marker="^", color="lime", s=80, zorder=5)
ax1.scatter(df.index[df["Sell"]], df["Close"][df["Sell"]], marker="v", color="red",  s=80, zorder=5)
ax1.set_title("Apple – 볼린저밴드")
ax1.legend(fontsize=9)
ax1.grid(alpha=0.3)

ax2.plot(df.index, df["%B"], color="purple", lw=1.2)
ax2.axhline(1, color="red",   ls="--", lw=0.8)
ax2.axhline(0, color="green", ls="--", lw=0.8)
ax2.axhline(0.5, color="gray", ls=":", lw=0.8)
ax2.set_ylabel("%B")
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("bollinger.png", dpi=150)
plt.show()
```

---

## 🧪 LAB 2 – 스토캐스틱 구현 (13:00 – 15:00)

```python
# stochastic.py
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def compute_stochastic(df: pd.DataFrame, k_period: int = 14,
                        d_period: int = 3) -> pd.DataFrame:
    """스토캐스틱 %K, %D 계산"""
    low_min  = df["Low"].rolling(k_period).min()
    high_max = df["High"].rolling(k_period).max()
    pct_k = (df["Close"] - low_min) / (high_max - low_min) * 100
    pct_d = pct_k.rolling(d_period).mean()
    return pd.DataFrame({"Stoch_K": pct_k, "Stoch_D": pct_d})

df = yf.download("005930.KS", period="1y", auto_adjust=True)[["Open","High","Low","Close"]]
df.columns = ["Open","High","Low","Close"]
stoch = compute_stochastic(df)
df = pd.concat([df, stoch], axis=1).dropna()

# 크로스 신호
prev_diff = df["Stoch_K"].shift(1) - df["Stoch_D"].shift(1)
curr_diff = df["Stoch_K"] - df["Stoch_D"]
df["Buy"]  = (prev_diff < 0) & (curr_diff >= 0) & (df["Stoch_K"] < 20)
df["Sell"] = (prev_diff > 0) & (curr_diff <= 0) & (df["Stoch_K"] > 80)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8),
                                gridspec_kw={"height_ratios": [2, 1]}, sharex=True)
ax1.plot(df.index, df["Close"], lw=1.5, color="steelblue")
ax1.scatter(df.index[df["Buy"]],  df["Close"][df["Buy"]],  marker="^", color="lime", s=100, zorder=5)
ax1.scatter(df.index[df["Sell"]], df["Close"][df["Sell"]], marker="v", color="red",  s=100, zorder=5)
ax1.set_title("삼성전자 – 스토캐스틱 매매 신호")
ax1.grid(alpha=0.3)

ax2.plot(df.index, df["Stoch_K"], label="%K", color="blue",   lw=1.5)
ax2.plot(df.index, df["Stoch_D"], label="%D", color="orange", lw=1.2, ls="--")
ax2.axhline(80, color="red",   ls="--", lw=0.8)
ax2.axhline(20, color="green", ls="--", lw=0.8)
ax2.fill_between(df.index, 80, 100, alpha=0.07, color="red")
ax2.fill_between(df.index, 0, 20,  alpha=0.07, color="green")
ax2.set_ylim(0, 100)
ax2.legend()
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("stochastic.png", dpi=150)
plt.show()
```

---

## 🧪 LAB 3 – ATR 기반 손절가 설정 (15:00 – 17:00)

```python
# atr.py
import yfinance as yf
import pandas as pd
import numpy as np

def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """ATR 계산"""
    high, low, close = df["High"], df["Low"], df["Close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low  - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1/period, adjust=False).mean()

df = yf.download("AAPL", period="6mo", auto_adjust=True)[["Open","High","Low","Close"]]
df.columns = ["Open","High","Low","Close"]
df["ATR14"] = compute_atr(df)
df = df.dropna()

# ATR 기반 손절가 / 목표가 계산 (매수 시점 = 마지막 종가 기준)
entry_price = df["Close"].iloc[-1]
atr = df["ATR14"].iloc[-1]
stop_loss   = entry_price - 2 * atr   # 2 ATR 아래
target      = entry_price + 3 * atr   # 3 ATR 위

print(f"진입가:  ${entry_price:.2f}")
print(f"ATR14:   ${atr:.2f}")
print(f"손절가:  ${stop_loss:.2f}  (진입가 대비 -{2*atr/entry_price*100:.2f}%)")
print(f"목표가:  ${target:.2f}   (진입가 대비 +{3*atr/entry_price*100:.2f}%)")
print(f"Risk/Reward: 1 : {3/2:.1f}")

# ATR 이동 추이 확인
print(f"\nATR 최근 5일:\n{df['ATR14'].tail().round(2)}")
```

---

## 📝 과제 (17:00 – 18:00)

1. 볼린저밴드 Bandwidth(%B)가 최저점에서 반등하는 "스퀴즈 이후 돌파" 전략을 구현하세요.
2. 스토캐스틱(%K)이 20 아래에서 상향 크로스 AND RSI < 35 AND 볼린저밴드 하단 이하 조건의 복합 신호를 탐지하세요.
3. ATR을 이용해 포지션 사이징: 총 자산의 1%를 리스크로 설정할 때 매수 가능 수량을 계산하세요.

---

## ✅ 체크리스트

- [ ] 볼린저밴드 계산 및 %B 시각화 완료
- [ ] 스토캐스틱 %K·%D 계산 및 크로스 신호 탐지 완료
- [ ] ATR 계산 및 손절가·목표가 설정 완료
- [ ] 복합 지표 차트 저장 성공
- [ ] 과제 제출

---

## 📚 참고자료

- [Investopedia – 볼린저밴드](https://www.investopedia.com/terms/b/bollingerbands.asp)
- [Investopedia – 스토캐스틱](https://www.investopedia.com/terms/s/stochasticoscillator.asp)
- [Investopedia – ATR](https://www.investopedia.com/terms/a/atr.asp)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day134+extra+indicators
