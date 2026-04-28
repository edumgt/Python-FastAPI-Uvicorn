# Day 138 – 포트폴리오 구성 & 리밸런싱

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (중급)

---

## 🎯 학습 목표

- 포트폴리오 분산 투자의 효과(상관관계, 공분산) 이해
- 등비중·변동성 역비례·평균-분산 최적화 구현
- 정기 리밸런싱 시뮬레이션
- 상관관계 히트맵 시각화

---

## 📖 이론 (08:00 – 10:00)

### 1. 분산 투자 효과
- 상관관계가 낮은 자산을 혼합하면 포트폴리오 변동성 감소
- 공분산: `cov(r_i, r_j)` – 자산 간 수익률 동조 정도
- 분산: `σ_p² = w^T Σ w` (w: 비중 벡터, Σ: 공분산 행렬)

### 2. 자산 배분 방법
| 방법 | 설명 |
|------|------|
| 등비중 (Equal Weight) | 모든 자산에 동일 비중 |
| 변동성 역비례 | 1/σ로 비중 설정 (변동성 낮은 자산에 더 투자) |
| 최소 분산 | 포트폴리오 변동성 최소화 (최적화 필요) |
| 최대 샤프 | 샤프지수 최대화 (효율적 프런티어 상 최적) |

### 3. 리밸런싱 주기
- **월간**: 변동성 높은 자산군 (암호화폐)
- **분기**: 주식 포트폴리오
- **반기/연간**: 장기 ETF 포트폴리오

---

## 🧪 LAB 1 – 상관관계 분석 (10:00 – 12:00)

```python
# correlation.py
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

tickers = {
    "AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Google",
    "BTC-USD": "Bitcoin", "GLD": "Gold ETF", "TLT": "국채 ETF",
    "VNQ": "부동산 ETF", "SPY": "S&P500",
}

data = yf.download(list(tickers.keys()), period="3y", auto_adjust=True)["Close"]
data.columns = [tickers.get(c, c) for c in data.columns]
returns = data.pct_change().dropna()

# 상관관계 행렬
corr = returns.corr()
print("=== 상관관계 행렬 ===")
print(corr.round(2))

# 히트맵
fig, ax = plt.subplots(figsize=(10, 8))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdYlGn",
            center=0, vmin=-1, vmax=1, square=True, ax=ax,
            linewidths=0.5, cbar_kws={"shrink": 0.8})
ax.set_title("자산 간 상관관계 히트맵 (최근 3년)", fontsize=13)
plt.tight_layout()
plt.savefig("correlation_heatmap.png", dpi=150)
plt.show()

# 분산 투자 관점: 낮은 상관관계 조합 찾기
pairs = [(a, b, corr.loc[a, b]) for a in corr.columns for b in corr.columns if a < b]
pairs.sort(key=lambda x: abs(x[2]))
print("\n=== 상관관계가 낮은 자산 조합 (Top 5) ===")
for a, b, c in pairs[:5]:
    print(f"  {a} & {b}: {c:.3f}")
```

---

## 🧪 LAB 2 – 자산 배분 전략 비교 (13:00 – 15:00)

```python
# asset_allocation.py
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

tickers = ["AAPL", "MSFT", "GLD", "TLT", "SPY"]
data = yf.download(tickers, period="5y", auto_adjust=True)["Close"]
data = data.dropna()
returns = data.pct_change().dropna()

def backtest_portfolio(returns: pd.DataFrame, weights: np.ndarray,
                        rebalance_freq: str = "QE",
                        cost: float = 0.001) -> pd.Series:
    """포트폴리오 백테스트 (리밸런싱 포함)"""
    portfolio_returns = []
    rebalance_dates = returns.resample(rebalance_freq).last().index
    for date, daily_ret in returns.iterrows():
        if date in rebalance_dates:
            # 리밸런싱: 거래비용 발생
            daily_return = float(daily_ret @ weights) - cost
        else:
            daily_return = float(daily_ret @ weights)
        portfolio_returns.append(daily_return)
    return pd.Series(portfolio_returns, index=returns.index)

# 1. 등비중
w_equal = np.array([1/len(tickers)] * len(tickers))

# 2. 변동성 역비례
vol = returns.std()
w_vol_inv = (1/vol) / (1/vol).sum()

# 3. S&P500 100% (벤치마크)
spy_idx = tickers.index("SPY")
w_spy = np.zeros(len(tickers)); w_spy[spy_idx] = 1.0

strategies = {
    "등비중": backtest_portfolio(returns, w_equal),
    "변동성역비례": backtest_portfolio(returns, w_vol_inv.values),
    "S&P500": backtest_portfolio(returns, w_spy),
}

print("=== 비중 설정 ===")
for t, we, wv in zip(tickers, w_equal, w_vol_inv.values):
    print(f"  {t:6s}  등비중:{we*100:.1f}%  변동성역비례:{wv*100:.1f}%")

fig, ax = plt.subplots(figsize=(13, 6))
for name, ret in strategies.items():
    cum = (1 + ret).cumprod()
    ann = (cum.iloc[-1] ** (252/len(ret)) - 1) * 100
    ax.plot(ret.index, cum, label=f"{name} ({ann:.1f}% CAGR)")
ax.set_title("자산 배분 전략 비교", fontsize=13)
ax.set_ylabel("누적 수익률 (시작=1)")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("portfolio_comparison.png", dpi=150)
plt.show()
```

---

## 🧪 LAB 3 – 리밸런싱 시뮬레이션 (15:00 – 17:00)

```python
# rebalancing.py
import yfinance as yf
import pandas as pd
import numpy as np

tickers = ["AAPL", "MSFT", "GLD", "TLT"]
data = yf.download(tickers, period="3y", auto_adjust=True)["Close"].dropna()
target_weights = np.array([0.30, 0.30, 0.20, 0.20])  # 목표 비중

capital = 10_000_000  # 1000만원
shares = (capital * target_weights / data.iloc[0]).astype(int)
print("=== 초기 매수 ===")
for t, s, p in zip(tickers, shares, data.iloc[0]):
    print(f"  {t}: {s}주 × {p:.2f} = {s*p:,.0f}원")

rebalance_dates = data.resample("QE").last().index  # 분기 리밸런싱
log = []

for date in data.index:
    prices = data.loc[date].values
    portfolio_value = float((shares * prices).sum())

    if date in rebalance_dates:
        new_shares = (portfolio_value * target_weights / prices).astype(int)
        diff = new_shares - shares
        cost = sum(abs(d * p) * 0.001 for d, p in zip(diff, prices))  # 0.1% 수수료
        shares = new_shares
        log.append({"날짜": date.date(), "자산가치": portfolio_value,
                     "리밸런싱": "Y", "거래비용": round(cost, 0)})
    else:
        log.append({"날짜": date.date(), "자산가치": portfolio_value,
                     "리밸런싱": "N", "거래비용": 0})

log_df = pd.DataFrame(log).set_index("날짜")
rebal_log = log_df[log_df["리밸런싱"]=="Y"]
print(f"\n=== 리밸런싱 이력 ({len(rebal_log)}회) ===")
print(rebal_log[["자산가치","거래비용"]].to_string())
print(f"\n최종 자산: {log_df['자산가치'].iloc[-1]:,.0f}원")
print(f"총 수익률: {(log_df['자산가치'].iloc[-1]/capital-1)*100:.2f}%")
```

---

## 📝 과제 (17:00 – 18:00)

1. 한국 주식(삼성전자·SK하이닉스·NAVER)과 미국 ETF(SPY·TLT·GLD)를 혼합한 글로벌 포트폴리오를 설계하고 3년 수익률을 계산하세요.
2. 월간·분기·연간 리밸런싱 주기를 비교하여 어느 주기가 가장 성과가 좋은지 분석하세요.
3. `scipy.optimize`를 활용한 최소 분산 포트폴리오 비중을 구현하고 등비중과 비교하세요.

---

## ✅ 체크리스트

- [ ] 상관관계 분석 및 히트맵 시각화 완료
- [ ] 등비중·변동성 역비례 자산 배분 구현 성공
- [ ] 분기 리밸런싱 시뮬레이션 완료
- [ ] 포트폴리오 비교 차트 저장 성공
- [ ] 과제 제출

---

## 📚 참고자료

- [Investopedia – 포트폴리오 다양화](https://www.investopedia.com/terms/d/diversification.asp)
- [Investopedia – 리밸런싱](https://www.investopedia.com/terms/r/rebalancing.asp)
- [Modern Portfolio Theory](https://www.investopedia.com/terms/m/modernportfoliotheory.asp)
