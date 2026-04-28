# Day 139 – 미니 프로젝트: MA + RSI 복합 전략 백테스트

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (중급)

---

## 🎯 학습 목표

- MA·RSI·MACD 지표를 결합한 복합 전략 설계
- 다종목 동시 백테스트 실행
- 성과 대시보드(차트 + 지표표) 자동 생성
- 워크포워드 테스트로 과적합 방지 검증

---

## 📋 프로젝트 요구사항

1. **전략**: MA5 > MA20 AND RSI < 65 → 매수 / MA5 < MA20 OR RSI > 75 → 매도
2. **대상 종목**: 미국 대형주 5개 + 한국 대형주 3개
3. **기간**: 최근 5년 (훈련 3년 + 검증 2년)
4. **성과 지표**: CAGR·Sharpe·MDD·승률·거래 횟수
5. **출력**: 성과 대시보드 PNG + 결과 CSV

---

## 📖 이론 (08:00 – 10:00)

### 복합 전략 설계 원칙
- **추세 필터** (MA): 추세 방향 확인
- **모멘텀 필터** (RSI): 진입 시점의 모멘텀 확인
- **두 조건 모두 충족할 때만 진입** → 거래 횟수 감소, 신뢰도 향상

```
매수 조건: MA5 > MA20 (상승추세)  AND  30 < RSI < 65 (과열 아닌 상승 모멘텀)
매도 조건: MA5 < MA20 (하락추세)  OR   RSI > 75      (과매수 구간)
```

---

## 🧪 LAB 1 – 전략 & 백테스트 모듈 (10:00 – 12:00)

```python
# strategy.py
import pandas as pd
import numpy as np

def compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain, loss = delta.clip(lower=0), (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    return 100 - 100 / (1 + avg_gain / avg_loss)

def generate_signals(df: pd.DataFrame) -> pd.Series:
    """MA+RSI 복합 전략 신호 생성"""
    close = df["Close"].squeeze()
    ma5   = close.rolling(5).mean()
    ma20  = close.rolling(20).mean()
    rsi   = compute_rsi(close)

    buy_cond  = (ma5 > ma20) & (rsi > 30) & (rsi < 65)
    sell_cond = (ma5 < ma20) | (rsi > 75)

    signal = pd.Series(0, index=df.index)
    position = 0
    for i in range(len(signal)):
        if buy_cond.iloc[i] and position == 0:
            position = 1
        elif sell_cond.iloc[i] and position == 1:
            position = 0
        signal.iloc[i] = position

    return signal.shift(1)  # 룩어헤드 바이어스 방지

def run_backtest(df: pd.DataFrame, commission: float = 0.001) -> dict:
    """백테스트 실행 및 성과 지표 반환"""
    signal = generate_signals(df)
    close  = df["Close"].squeeze()
    daily  = close.pct_change()
    trade  = signal.diff().abs()
    ret    = daily * signal - trade * commission
    ret    = ret.dropna()

    cum = (1 + ret).cumprod()
    bh  = (1 + daily.dropna()).cumprod()

    n = len(ret)
    cagr    = (cum.iloc[-1] ** (252/n) - 1) * 100
    ann_vol = ret.std() * np.sqrt(252) * 100
    sharpe  = cagr / ann_vol if ann_vol > 0 else 0
    peak    = cum.cummax()
    mdd     = ((cum - peak) / peak).min() * 100

    # 개별 거래 수익률
    in_trade, trades_ret = False, []
    entry_val = 0
    for i in range(1, len(signal)):
        if signal.iloc[i] == 1 and not in_trade:
            in_trade, entry_val = True, close.iloc[i]
        elif (signal.iloc[i] == 0) and in_trade:
            trades_ret.append(close.iloc[i]/entry_val - 1)
            in_trade = False

    win_rate = (np.array(trades_ret) > 0).mean() * 100 if trades_ret else 0

    return {
        "CAGR(%)": round(cagr, 2),
        "Sharpe": round(sharpe, 3),
        "MDD(%)": round(mdd, 2),
        "Ann.Vol(%)": round(ann_vol, 2),
        "거래수": len(trades_ret),
        "승률(%)": round(win_rate, 1),
        "BH수익률(%)": round((bh.iloc[-1]-1)*100, 2),
        "cum_strategy": cum,
        "cum_bh": bh.reindex(cum.index),
    }
```

---

## 🧪 LAB 2 – 다종목 백테스트 실행 (13:00 – 15:00)

```python
# multi_backtest.py
import yfinance as yf
import pandas as pd
from strategy import run_backtest  # LAB 1 모듈

TICKERS = {
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "NVIDIA",
    "GOOGL": "Google", "AMZN": "Amazon",
    "005930.KS": "삼성전자", "000660.KS": "SK하이닉스", "035420.KS": "NAVER",
}

# 데이터 다운로드 (5년)
results = {}
for symbol, name in TICKERS.items():
    print(f"분석 중: {name} ({symbol})")
    df = yf.download(symbol, period="5y", auto_adjust=True)[["Close"]]
    if df.empty or len(df) < 100:
        print(f"  데이터 부족. 건너뜀.")
        continue
    df.columns = ["Close"]
    metrics = run_backtest(df)
    results[name] = metrics

# 결과 요약 테이블
summary = pd.DataFrame([
    {
        "종목": name,
        "CAGR(%)": m["CAGR(%)"],
        "Sharpe": m["Sharpe"],
        "MDD(%)": m["MDD(%)"],
        "승률(%)": m["승률(%)"],
        "거래수": m["거래수"],
        "BH수익률(%)": m["BH수익률(%)"],
    }
    for name, m in results.items()
])

summary = summary.sort_values("Sharpe", ascending=False)
print("\n=== 복합 전략 다종목 성과 비교 ===")
print(summary.to_string(index=False))
summary.to_csv("backtest_results.csv", index=False, encoding="utf-8-sig")
print("\n결과 저장: backtest_results.csv")
```

---

## 🧪 LAB 3 – 성과 대시보드 생성 (15:00 – 17:00)

```python
# dashboard.py
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd

def create_dashboard(results: dict, save_path: str = "strategy_dashboard.png"):
    n = len(results)
    ncols = min(3, n)
    nrows = (n + ncols - 1) // ncols + 1  # +1 for summary row

    fig = plt.figure(figsize=(18, 5 * nrows))
    gs = gridspec.GridSpec(nrows, ncols, figure=fig, hspace=0.5, wspace=0.35)

    names = list(results.keys())

    # 개별 종목 누적수익률 차트
    for idx, name in enumerate(names):
        row, col = divmod(idx, ncols)
        ax = fig.add_subplot(gs[row, col])
        m = results[name]
        ax.plot(m["cum_strategy"], label="전략", linewidth=1.5)
        ax.plot(m["cum_bh"],       label="B&H",  linewidth=1.2, linestyle="--", alpha=0.7)
        ax.set_title(f"{name}\nCAGR:{m['CAGR(%)']:.1f}% | Sharpe:{m['Sharpe']:.2f} | MDD:{m['MDD(%)']:.1f}%",
                     fontsize=9)
        ax.legend(fontsize=7)
        ax.grid(alpha=0.3)

    # 요약 비교 바 차트 (마지막 행)
    ax_sum = fig.add_subplot(gs[nrows-1, :])
    summary = pd.DataFrame([
        {"종목": k, "CAGR": v["CAGR(%)"], "Sharpe×10": v["Sharpe"]*10}
        for k, v in results.items()
    ])
    x = range(len(summary))
    ax_sum.bar([i-0.2 for i in x], summary["CAGR"],     width=0.4, label="CAGR(%)",    color="steelblue")
    ax_sum.bar([i+0.2 for i in x], summary["Sharpe×10"],width=0.4, label="Sharpe×10",  color="orange")
    ax_sum.set_xticks(x)
    ax_sum.set_xticklabels(summary["종목"], rotation=15, fontsize=9)
    ax_sum.axhline(0, color="black", lw=0.8)
    ax_sum.set_title("전략 성과 비교 (CAGR vs Sharpe×10)")
    ax_sum.legend()
    ax_sum.grid(alpha=0.3, axis="y")

    plt.suptitle("MA+RSI 복합 전략 성과 대시보드", fontsize=14, y=1.01)
    plt.savefig(save_path, dpi=130, bbox_inches="tight")
    print(f"대시보드 저장: {save_path}")
    plt.show()
```

---

## 📝 과제 (17:00 – 18:00)

1. 훈련(3년)/검증(2년) 기간을 나누어 훈련 구간과 검증 구간의 성과 차이를 분석하세요.
2. MACD 신호를 추가로 결합(MA + RSI + MACD 3중 조건)하고 성과를 비교하세요.
3. 가장 샤프지수가 높은 종목과 낮은 종목의 특성 차이를 분석하고 이유를 기술하세요.

---

## ✅ 체크리스트

- [ ] MA+RSI 복합 전략 신호 생성 구현 완료
- [ ] 8개 이상 종목 동시 백테스트 실행 성공
- [ ] 결과 CSV 저장 성공
- [ ] 성과 대시보드 PNG 생성 성공
- [ ] 과제 제출

---

## 📚 참고자료

- [Combining Technical Indicators – Investopedia](https://www.investopedia.com/articles/trading/11/using-macd-indicator.asp)
- [backtesting.py 고급 사용법](https://kernc.github.io/backtesting.py/doc/backtesting/index.html)
