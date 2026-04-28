# Day 131 – 이동평균선 (MA: Moving Average)

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (중급)

---

## 🎯 학습 목표

- SMA(단순이동평균)와 EMA(지수이동평균) 차이 이해 및 구현
- 골든크로스·데드크로스 매매 신호 탐지
- 이동평균 기반 트렌드 추세 분석
- 매매 신호를 차트에 시각화

---

## 📖 이론 (08:00 – 10:00)

### 1. SMA vs EMA
| 구분 | SMA (단순이동평균) | EMA (지수이동평균) |
|------|-------------------|-------------------|
| 계산 | N일 종가 단순 평균 | 최근 값에 더 높은 가중치 |
| 반응 속도 | 느림 | 빠름 |
| 활용 | 장기 추세 파악 | 단기 매매 신호 |

```python
# SMA
sma = df["Close"].rolling(window=N).mean()

# EMA (pandas ewm)
ema = df["Close"].ewm(span=N, adjust=False).mean()
```

### 2. 골든크로스 & 데드크로스
- **골든크로스**: 단기 MA가 장기 MA를 **상향** 돌파 → 매수 신호
- **데드크로스**: 단기 MA가 장기 MA를 **하향** 돌파 → 매도 신호

```python
# 이전과 현재 상태 비교
prev_diff = ma_short.shift(1) - ma_long.shift(1)
curr_diff = ma_short - ma_long
golden_cross = (prev_diff < 0) & (curr_diff >= 0)
dead_cross   = (prev_diff > 0) & (curr_diff <= 0)
```

### 3. 다중 이동평균 전략 (5·20·60일)
- 5일 > 20일 > 60일: 강한 상승추세
- 5일 < 20일 < 60일: 강한 하락추세

---

## 🧪 LAB 1 – SMA & EMA 계산 (10:00 – 12:00)

```python
# ma_basic.py
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

df = yf.download("AAPL", period="1y", auto_adjust=True)[["Close"]]
df.columns = ["Close"]

# SMA 계산
for w in [5, 20, 60]:
    df[f"SMA{w}"] = df["Close"].rolling(window=w).mean()

# EMA 계산
for s in [12, 26]:
    df[f"EMA{s}"] = df["Close"].ewm(span=s, adjust=False).mean()

print("=== 최근 5행 ===")
print(df.tail())

# 시각화
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(df.index, df["Close"],  label="Close",  linewidth=1.5, alpha=0.8)
ax.plot(df.index, df["SMA5"],   label="SMA5",   linewidth=1.2, linestyle="-")
ax.plot(df.index, df["SMA20"],  label="SMA20",  linewidth=1.2, linestyle="--")
ax.plot(df.index, df["SMA60"],  label="SMA60",  linewidth=1.2, linestyle="-.")
ax.plot(df.index, df["EMA12"],  label="EMA12",  linewidth=1.2, linestyle=":", alpha=0.8)
ax.set_title("SMA vs EMA Comparison", fontsize=13)
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("ma_comparison.png", dpi=150)
plt.show()
```

---

## 🧪 LAB 2 – 골든크로스·데드크로스 탐지 (13:00 – 15:00)

```python
# cross_signal.py
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

df = yf.download("005930.KS", period="2y", auto_adjust=True)[["Close"]]
df.columns = ["Close"]

df["MA5"]  = df["Close"].rolling(5).mean()
df["MA20"] = df["Close"].rolling(20).mean()

# 크로스 탐지
prev = df["MA5"].shift(1) - df["MA20"].shift(1)
curr = df["MA5"] - df["MA20"]
df["Golden"] = (prev < 0) & (curr >= 0)
df["Dead"]   = (prev > 0) & (curr <= 0)

golden = df[df["Golden"]]
dead   = df[df["Dead"]]

print(f"골든크로스 발생: {len(golden)}회")
print(golden.index.date.tolist())
print(f"\n데드크로스 발생: {len(dead)}회")
print(dead.index.date.tolist())

# 시각화
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(df.index, df["Close"], label="Close", linewidth=1.2, color="steelblue", alpha=0.8)
ax.plot(df.index, df["MA5"],   label="MA5",   linewidth=1.2, color="orange")
ax.plot(df.index, df["MA20"],  label="MA20",  linewidth=1.2, color="red")

# 크로스 마커
ax.scatter(golden.index, golden["Close"], marker="^", color="lime",
           s=120, zorder=5, label="골든크로스")
ax.scatter(dead.index,   dead["Close"],   marker="v", color="red",
           s=120, zorder=5, label="데드크로스")

ax.set_title("삼성전자 – 골든/데드크로스 신호", fontsize=13)
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("cross_signals.png", dpi=150)
plt.show()
```

---

## 🧪 LAB 3 – 이동평균 전략 간단 시뮬레이션 (15:00 – 17:00)

```python
# ma_strategy.py
import yfinance as yf
import pandas as pd
import numpy as np

df = yf.download("AAPL", period="2y", auto_adjust=True)[["Close"]]
df.columns = ["Close"]

df["MA5"]  = df["Close"].rolling(5).mean()
df["MA20"] = df["Close"].rolling(20).mean()

# 신호: MA5 > MA20 이면 매수 포지션 (1), 아니면 현금 (0)
df["Signal"] = np.where(df["MA5"] > df["MA20"], 1, 0)
df["Signal"] = df["Signal"].shift(1)  # 신호 다음날 진입 (미래 데이터 사용 방지)

# 일간 수익률
df["Daily_Return"]   = df["Close"].pct_change()
df["Strategy_Return"]= df["Daily_Return"] * df["Signal"]

# 누적 수익률
df["Buy_Hold"]  = (1 + df["Daily_Return"]).cumprod()
df["MA_Strategy"]= (1 + df["Strategy_Return"]).cumprod()

df = df.dropna()
print(f"Buy & Hold 수익률: {(df['Buy_Hold'].iloc[-1]-1)*100:.2f}%")
print(f"MA 전략 수익률:    {(df['MA_Strategy'].iloc[-1]-1)*100:.2f}%")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df.index, df["Buy_Hold"],   label="Buy & Hold")
ax.plot(df.index, df["MA_Strategy"],label="MA5/MA20 전략")
ax.set_title("MA 전략 vs Buy & Hold")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("ma_strategy_result.png", dpi=150)
plt.show()
```

---

## 📝 과제 (17:00 – 18:00)

1. 코스피 대표 종목에서 최근 2년간 골든크로스 신호가 발생한 날짜와 이후 1개월 수익률을 계산하세요.
2. SMA(5·20)와 EMA(5·20) 전략의 수익률을 비교하세요.
3. 3중 MA(5·20·60일) 조건이 모두 정렬될 때만 진입하는 전략을 구현하세요.

---

## ✅ 체크리스트

- [ ] SMA와 EMA 계산 및 비교 완료
- [ ] 골든크로스·데드크로스 자동 탐지 구현
- [ ] MA 전략 vs Buy & Hold 수익률 비교
- [ ] 차트 저장 성공
- [ ] 과제 제출

---

## 📚 참고자료

- [Investopedia – Moving Average](https://www.investopedia.com/terms/m/movingaverage.asp)
- [Investopedia – Golden Cross](https://www.investopedia.com/terms/g/goldencross.asp)
- [pandas ewm](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.ewm.html)
