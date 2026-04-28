# Day 136 – 백테스트 심화 (수익률·샤프지수·MDD)

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (중급)

---

## 🎯 학습 목표

- 전략 성과 지표(CAGR·샤프지수·소르티노·칼마·MDD) 직접 계산
- 드로다운 차트 시각화
- 다전략 성과 비교 대시보드 구성
- 거래 내역(Trade Log) 기록 및 분석

---

## 📖 이론 (08:00 – 10:00)

### 1. 핵심 성과 지표
| 지표 | 공식 | 의미 |
|------|------|------|
| **CAGR** | (최종가/시작가)^(252/N) - 1 | 연평균 복리 수익률 |
| **Sharpe** | CAGR / 연간 변동성 | 위험 조정 수익률 |
| **Sortino** | CAGR / 하방 변동성 | 손실만 고려한 리스크 조정 |
| **Calmar** | CAGR / |MDD| | 최대낙폭 대비 수익률 |
| **MDD** | max((고점-현재)/고점) | 최대 낙폭 |
| **Win Rate** | 수익 거래 / 전체 거래 | 승률 |

### 2. MDD 계산
```python
cum  = (1 + daily_returns).cumprod()
peak = cum.cummax()
drawdown = (cum - peak) / peak          # 현재 낙폭
mdd  = drawdown.min()                   # 최대낙폭
```

---

## 🧪 LAB 1 – 성과 지표 계산기 (10:00 – 12:00)

```python
# metrics.py
import numpy as np
import pandas as pd

def performance_metrics(returns: pd.Series,
                         risk_free: float = 0.04) -> dict:
    """전략 성과 지표 계산"""
    n = len(returns)
    cum = (1 + returns).cumprod()

    # CAGR
    cagr = (cum.iloc[-1] ** (252/n) - 1) * 100

    # Sharpe
    ann_ret = returns.mean() * 252
    ann_vol = returns.std() * np.sqrt(252)
    sharpe  = (ann_ret - risk_free) / ann_vol if ann_vol > 0 else 0

    # Sortino (하방 변동성만)
    neg_ret = returns[returns < 0]
    down_vol = neg_ret.std() * np.sqrt(252) if len(neg_ret) > 0 else 1e-9
    sortino  = (ann_ret - risk_free) / down_vol

    # MDD
    peak = cum.cummax()
    dd   = (cum - peak) / peak
    mdd  = dd.min() * 100

    # Calmar
    calmar = cagr / abs(mdd) if mdd != 0 else 0

    # 최장 MDD 기간
    dd_series = dd[dd < 0]
    max_dd_duration = 0
    if not dd_series.empty:
        is_dd = (dd < 0).astype(int)
        runs = is_dd.groupby((is_dd != is_dd.shift()).cumsum()).sum()
        max_dd_duration = int(runs.max())

    return {
        "CAGR(%)": round(cagr, 2),
        "Sharpe Ratio": round(sharpe, 3),
        "Sortino Ratio": round(sortino, 3),
        "Calmar Ratio": round(calmar, 3),
        "MDD(%)": round(mdd, 2),
        "MDD 최장기간(일)": max_dd_duration,
        "연변동성(%)": round(ann_vol * 100, 2),
        "총거래일": n,
    }


# 예시 테스트
import yfinance as yf

df = yf.download("AAPL", period="5y", auto_adjust=True)[["Close"]]
df.columns = ["Close"]
df["MA5"]  = df["Close"].rolling(5).mean()
df["MA20"] = df["Close"].rolling(20).mean()
df["Signal"]   = np.where(df["MA5"] > df["MA20"], 1, 0)
df["Position"] = df["Signal"].shift(1)
df["Daily"]    = df["Close"].pct_change()
df["Str_Ret"]  = df["Daily"] * df["Position"]
df = df.dropna()

print("=== Buy & Hold ===")
for k, v in performance_metrics(df["Daily"]).items():
    print(f"  {k}: {v}")

print("\n=== MA5/20 전략 ===")
for k, v in performance_metrics(df["Str_Ret"]).items():
    print(f"  {k}: {v}")
```

---

## 🧪 LAB 2 – 드로다운 차트 (13:00 – 15:00)

```python
# drawdown_chart.py
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = yf.download("AAPL", period="5y", auto_adjust=True)[["Close"]]
df.columns = ["Close"]
df["MA5"]  = df["Close"].rolling(5).mean()
df["MA20"] = df["Close"].rolling(20).mean()
df["Pos"]  = np.where(df["MA5"] > df["MA20"], 1, 0)
df["Pos"]  = df["Pos"].shift(1)
df["Ret"]  = df["Close"].pct_change()
df["SRet"] = df["Ret"] * df["Pos"]
df = df.dropna()

def calc_drawdown(ret: pd.Series) -> pd.Series:
    cum  = (1 + ret).cumprod()
    peak = cum.cummax()
    return (cum - peak) / peak * 100

bh_dd  = calc_drawdown(df["Ret"])
str_dd = calc_drawdown(df["SRet"])
bh_cum  = (1 + df["Ret"]).cumprod()
str_cum = (1 + df["SRet"]).cumprod()

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# 누적수익률
axes[0,0].plot(df.index, bh_cum,  label="Buy & Hold", color="steelblue")
axes[0,0].plot(df.index, str_cum, label="MA 전략",    color="orange")
axes[0,0].set_title("누적 수익률")
axes[0,0].legend()
axes[0,0].grid(alpha=0.3)

# 드로다운
axes[0,1].fill_between(df.index, bh_dd,  0, alpha=0.4, color="red",    label="Buy & Hold")
axes[0,1].fill_between(df.index, str_dd, 0, alpha=0.4, color="orange", label="MA 전략")
axes[0,1].set_title("드로다운(%)")
axes[0,1].legend()
axes[0,1].grid(alpha=0.3)

# 수익률 분포
axes[1,0].hist(df["Ret"]*100,  bins=80, alpha=0.6, label="Buy & Hold", edgecolor="w")
axes[1,0].hist(df["SRet"]*100, bins=80, alpha=0.6, label="MA 전략",   edgecolor="w")
axes[1,0].set_title("일간 수익률 분포")
axes[1,0].legend()
axes[1,0].grid(alpha=0.3)

# 연도별 수익률
df["Year"] = df.index.year
annual = df.groupby("Year").apply(lambda g: (1+g["SRet"]).prod() - 1) * 100
colors = ["green" if v >= 0 else "red" for v in annual]
axes[1,1].bar(annual.index, annual.values, color=colors, edgecolor="w")
axes[1,1].set_title("연도별 전략 수익률(%)")
axes[1,1].axhline(0, color="black", lw=0.8)
axes[1,1].grid(alpha=0.3, axis="y")

plt.suptitle("MA5/MA20 전략 성과 대시보드", fontsize=14)
plt.tight_layout()
plt.savefig("performance_dashboard.png", dpi=150)
plt.show()
```

---

## 🧪 LAB 3 – 거래 내역 기록 (15:00 – 17:00)

```python
# trade_log.py
import yfinance as yf
import pandas as pd
import numpy as np

df = yf.download("AAPL", period="3y", auto_adjust=True)[["Close"]]
df.columns = ["Close"]
df["RSI"] = (lambda close, p=14:
    100 - 100/(1 + close.diff().clip(lower=0).ewm(alpha=1/p, adjust=False).mean() /
              (-close.diff()).clip(lower=0).ewm(alpha=1/p, adjust=False).mean()))(df["Close"])
df = df.dropna()

trades = []
position = 0
buy_price = 0

for date, row in df.iterrows():
    if row["RSI"] < 35 and position == 0:
        position  = 1
        buy_price = row["Close"]
        trades.append({"Type":"BUY", "Date":date, "Price":round(buy_price,2),
                        "P&L":None, "Return(%)":None})
    elif row["RSI"] > 65 and position == 1:
        sell_price = row["Close"]
        pl = sell_price - buy_price
        ret = (sell_price / buy_price - 1) * 100
        trades.append({"Type":"SELL","Date":date,"Price":round(sell_price,2),
                        "P&L":round(pl,2),"Return(%)":round(ret,2)})
        position = 0

trade_df = pd.DataFrame(trades)
sells = trade_df[trade_df["Type"]=="SELL"]
print(f"총 거래: {len(sells)}회")
print(f"승률: {(sells['Return(%)'] > 0).mean()*100:.1f}%")
print(f"평균 수익률: {sells['Return(%)'].mean():.2f}%")
print(f"최대 수익: {sells['Return(%)'].max():.2f}%")
print(f"최대 손실: {sells['Return(%)'].min():.2f}%")
print("\n거래 내역:")
print(trade_df.to_string(index=False))
```

---

## 📝 과제 (17:00 – 18:00)

1. MA·RSI·MACD 세 가지 전략의 성과 지표를 표로 비교하세요 (CAGR, Sharpe, MDD).
2. 연도별 수익률 차트에서 특정 전략이 폭락장(예: 코로나 2020년)에서 어떻게 동작했는지 분석하세요.
3. Sortino Ratio와 Sharpe Ratio의 차이가 큰 전략을 찾고 그 이유를 설명하세요.

---

## ✅ 체크리스트

- [ ] CAGR·Sharpe·Sortino·Calmar·MDD 계산 함수 구현
- [ ] 드로다운 차트 시각화 완료
- [ ] 거래 내역 기록 및 승률·평균 수익률 계산 완료
- [ ] 성과 대시보드(4개 차트) 저장 성공
- [ ] 과제 제출

---

## 📚 참고자료

- [Investopedia – Sharpe Ratio](https://www.investopedia.com/terms/s/sharperatio.asp)
- [Investopedia – MDD](https://www.investopedia.com/terms/m/maximum-drawdown.asp)
- [Investopedia – Sortino Ratio](https://www.investopedia.com/terms/s/sortinoratio.asp)
