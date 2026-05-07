# Day 149 – 리스크 관리

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (고급)

---

## 🎯 학습 목표

- VaR(Value at Risk)·CVaR 계산 방법 이해 및 구현
- 포지션 사이징 원칙(Kelly, Fixed Fractional) 적용
- 손절·익절 자동 설정 전략 구현
- 전략 리스크 대시보드 구성

---

## 📖 이론 (08:00 – 10:00)

### 1. VaR (Value at Risk)
```
VaR(95%) = 하루 손실이 이 금액을 초과할 확률이 5%
```

```python
# 역사적 VaR
var_95 = np.percentile(returns, 5)   # 하위 5% 분위수

# 정규 분포 VaR
from scipy import stats
var_norm_95 = returns.mean() + stats.norm.ppf(0.05) * returns.std()

# CVaR (Conditional VaR, Expected Shortfall)
cvar_95 = returns[returns <= var_95].mean()
```

### 2. 포지션 사이징
```python
# Fixed Fractional (총 자산의 고정 비율)
risk_pct    = 0.01   # 1% 위험
stop_loss   = 0.05   # 5% 손절
position_pct= risk_pct / stop_loss   # 20% 투자

# Kelly Criterion
win_rate = 0.55; avg_win = 0.08; avg_loss = 0.05
kelly = win_rate / avg_loss - (1 - win_rate) / avg_win
half_kelly = kelly / 2  # 안전을 위해 절반 사용
```

### 3. ATR 기반 동적 손절
```python
stop = entry_price - 2 * atr   # 2 ATR 손절
size = risk_amount / (entry_price - stop)  # 주수 계산
```

---

## 🧪 LAB 1 – VaR & CVaR 계산 (10:00 – 12:00)

```python
# var_cvar.py
import yfinance as yf
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# 포트폴리오 구성 (단순 등비중 예시)
tickers = ["AAPL", "MSFT", "NVDA", "GOOGL", "GLD"]
data = yf.download(tickers, period="3y", auto_adjust=True)["Close"].dropna()
weights = np.array([0.20] * 5)

# 일간 포트폴리오 수익률
daily_returns = data.pct_change().dropna()
portfolio_ret = (daily_returns * weights).sum(axis=1)

CAPITAL = 100_000_000  # 1억원

def compute_var_cvar(returns: pd.Series, capital: float,
                      confidence: float = 0.95) -> dict:
    alpha = 1 - confidence

    # 역사적 방법
    var_hist  = np.percentile(returns, alpha * 100)
    cvar_hist = returns[returns <= var_hist].mean()

    # 정규 분포 방법
    mu, sigma = returns.mean(), returns.std()
    var_norm  = mu + stats.norm.ppf(alpha) * sigma
    cvar_norm = mu - sigma * stats.norm.pdf(stats.norm.ppf(alpha)) / alpha

    # 금액 변환
    return {
        "VaR(역사적)":    round(var_hist * capital, 0),
        "CVaR(역사적)":   round(cvar_hist * capital, 0),
        "VaR(정규분포)":  round(var_norm * capital, 0),
        "CVaR(정규분포)": round(cvar_norm * capital, 0),
        "VaR_pct(역사적)":  f"{var_hist*100:.2f}%",
    }

print(f"포트폴리오 일간 수익률 통계:")
print(f"  평균: {portfolio_ret.mean()*100:.3f}%  표준편차: {portfolio_ret.std()*100:.3f}%")
print(f"\n=== VaR / CVaR 분석 (신뢰수준 95%) ===")
result = compute_var_cvar(portfolio_ret, CAPITAL, 0.95)
for k, v in result.items():
    print(f"  {k}: {v:,.0f}원" if isinstance(v, float) else f"  {k}: {v}")

# 분포 시각화
fig, ax = plt.subplots(figsize=(11, 5))
ax.hist(portfolio_ret * 100, bins=100, edgecolor="white", color="steelblue", alpha=0.7)
var_pct  = np.percentile(portfolio_ret, 5) * 100
cvar_pct = portfolio_ret[portfolio_ret <= portfolio_ret.quantile(0.05)].mean() * 100
ax.axvline(var_pct,  color="orange", ls="--", lw=2, label=f"VaR 95%: {var_pct:.2f}%")
ax.axvline(cvar_pct, color="red",    ls="--", lw=2, label=f"CVaR 95%: {cvar_pct:.2f}%")
ax.set_title("포트폴리오 일간 수익률 분포 & VaR")
ax.set_xlabel("일간 수익률(%)"); ax.set_ylabel("빈도")
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("var_cvar.png", dpi=150)
plt.show()
```

---

## 🧪 LAB 2 – 포지션 사이징 (13:00 – 15:00)

```python
# position_sizing.py
import numpy as np
import pandas as pd

def fixed_fractional(capital: float, risk_pct: float,
                      stop_pct: float) -> dict:
    """고정 비율 포지션 사이징"""
    risk_amount   = capital * risk_pct
    invest_amount = capital * (risk_pct / stop_pct)
    return {"투자금액": invest_amount, "위험금액": risk_amount,
            "투자비율": invest_amount / capital}

def kelly_criterion(win_rate: float, avg_win: float,
                     avg_loss: float) -> dict:
    """켈리 기준 포지션 사이징"""
    kelly     = win_rate / avg_loss - (1 - win_rate) / avg_win
    half_kelly= max(0, kelly / 2)
    return {"kelly_fraction": kelly, "half_kelly": half_kelly,
            "권장 투자비율": f"{half_kelly*100:.1f}%"}

def atr_position(entry: float, atr: float, risk_amount: float,
                  multiplier: float = 2.0) -> dict:
    """ATR 기반 포지션 사이징"""
    stop_loss = entry - multiplier * atr
    risk_per_share = entry - stop_loss
    shares = int(risk_amount / risk_per_share) if risk_per_share > 0 else 0
    return {"진입가": entry, "손절가": stop_loss,
            "주당위험": risk_per_share, "매수수량": shares,
            "총투자금": shares * entry}

# 예시 시나리오
CAPITAL = 50_000_000  # 5000만원

print("=== Fixed Fractional (1% 위험, 5% 손절) ===")
ff = fixed_fractional(CAPITAL, risk_pct=0.01, stop_pct=0.05)
for k, v in ff.items():
    print(f"  {k}: {v:,.0f}원" if isinstance(v, (int, float)) else f"  {k}: {v}")

print("\n=== Kelly Criterion (승률 55%, 평균 이익 8%, 평균 손실 5%) ===")
kc = kelly_criterion(win_rate=0.55, avg_win=0.08, avg_loss=0.05)
for k, v in kc.items(): print(f"  {k}: {v}")

print("\n=== ATR 포지션 사이징 ===")
entry_price = 75_000; atr_value = 1_200
risk_money  = CAPITAL * 0.01  # 1% 위험
ap = atr_position(entry_price, atr_value, risk_money, multiplier=2.0)
for k, v in ap.items():
    print(f"  {k}: {v:,.0f}원" if isinstance(v, (int, float)) else f"  {k}: {v}")

# 포지션 사이징 시뮬레이션 비교
print("\n=== 자산 1%를 위험으로 설정 시 다른 stop_pct 비교 ===")
df_comp = pd.DataFrame([
    {"stop_pct(%)": sp*100,
     "투자비율(%)": round(0.01/sp*100, 1),
     "투자금액": round(CAPITAL * 0.01/sp, 0)}
    for sp in [0.02, 0.03, 0.05, 0.07, 0.10]
])
print(df_comp.to_string(index=False))
```

---

## 🧪 LAB 3 – 리스크 통합 대시보드 (15:00 – 17:00)

```python
# risk_dashboard.py
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

tickers = ["AAPL", "MSFT", "NVDA", "GLD", "TLT"]
data    = yf.download(tickers, period="3y", auto_adjust=True)["Close"].dropna()
weights = np.array([0.25, 0.25, 0.20, 0.15, 0.15])

daily = data.pct_change().dropna()
port  = (daily * weights).sum(axis=1)
cum   = (1 + port).cumprod()
peak  = cum.cummax()
dd    = (cum - peak) / peak * 100

var95  = np.percentile(port, 5) * 100
cvar95 = port[port <= np.percentile(port, 5)].mean() * 100

fig = plt.figure(figsize=(16, 10))
gs  = fig.add_gridspec(3, 3, hspace=0.45, wspace=0.35)

# 1. 누적 수익률
ax1 = fig.add_subplot(gs[0, :2])
ax1.plot(cum, color="steelblue", lw=1.5)
ax1.set_title("포트폴리오 누적 수익률")
ax1.grid(alpha=0.3)

# 2. 드로다운
ax2 = fig.add_subplot(gs[1, :2])
ax2.fill_between(dd.index, dd, 0, color="red", alpha=0.4)
ax2.set_title("드로다운(%)")
ax2.grid(alpha=0.3)

# 3. 수익률 분포 + VaR
ax3 = fig.add_subplot(gs[2, :2])
ax3.hist(port*100, bins=80, color="steelblue", edgecolor="w", alpha=0.7)
ax3.axvline(var95,  color="orange", ls="--", lw=2, label=f"VaR95%: {var95:.2f}%")
ax3.axvline(cvar95, color="red",    ls="--", lw=2, label=f"CVaR95%: {cvar95:.2f}%")
ax3.set_title("수익률 분포 & VaR"); ax3.legend(); ax3.grid(alpha=0.3)

# 4. 지표 요약 텍스트
ax4 = fig.add_subplot(gs[:, 2])
ax4.axis("off")
n = len(port)
cagr = (cum.iloc[-1]**(252/n) - 1)*100
vol  = port.std()*np.sqrt(252)*100
sharpe = cagr / vol if vol else 0
mdd  = dd.min()
summary_text = (
    f"{'='*25}\n포트폴리오 리스크 요약\n{'='*25}\n\n"
    f"CAGR:       {cagr:.2f}%\n"
    f"연변동성:   {vol:.2f}%\n"
    f"Sharpe:     {sharpe:.3f}\n"
    f"MDD:        {mdd:.2f}%\n\n"
    f"VaR(95%):   {var95:.2f}%\n"
    f"CVaR(95%):  {cvar95:.2f}%\n\n"
    f"비중 설정\n{'-'*20}"
)
for t, w in zip(tickers, weights):
    summary_text += f"\n{t}: {w*100:.0f}%"
ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes,
         fontsize=10, verticalalignment="top", fontfamily="monospace",
         bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

plt.suptitle("포트폴리오 리스크 관리 대시보드", fontsize=14)
plt.savefig("risk_dashboard.png", dpi=130, bbox_inches="tight")
plt.show()
```

---

## 📝 과제 (17:00 – 18:00)

1. 보유 종목 포트폴리오에서 VaR가 가장 큰 종목을 찾고, 해당 종목의 비중을 줄이면 포트폴리오 VaR가 어떻게 변하는지 분석하세요.
2. Kelly Criterion으로 계산한 포지션 사이징 전략과 고정 1% 위험 전략을 5년 백테스트로 비교하세요.
3. ATR 손절 배수(1.5·2.0·2.5·3.0)에 따른 수익률·승률·MDD를 비교하세요.

---

## ✅ 체크리스트

- [ ] 역사적·정규분포 VaR/CVaR 계산 구현 성공
- [ ] Fixed Fractional·Kelly·ATR 포지션 사이징 구현 성공
- [ ] 리스크 대시보드 시각화 완료
- [ ] VaR 시각화 및 분포 분석 완료
- [ ] 과제 제출

---

## 📚 참고자료

- [Investopedia – VaR](https://www.investopedia.com/terms/v/var.asp)
- [Investopedia – Kelly Criterion](https://www.investopedia.com/articles/trading/04/091504.asp)
- [Investopedia – Position Sizing](https://www.investopedia.com/terms/p/positionsizing.asp)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day149+risk+management
