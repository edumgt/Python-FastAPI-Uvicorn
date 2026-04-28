# Day 135 – 백테스트 기초

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (중급)

---

## 🎯 학습 목표

- 백테스트(Backtesting)의 개념과 주의사항 이해
- pandas 기반 수동 백테스트 프레임워크 설계
- `backtesting.py` 라이브러리 기초 활용
- 룩어헤드 바이어스(look-ahead bias) 방지 방법 습득

---

## 📖 이론 (08:00 – 10:00)

### 1. 백테스트란?
- 과거 데이터에 매매 전략을 적용하여 가상의 수익률을 계산하는 과정
- "과거에 이 전략이 작동했다면 미래에도 가능성이 있다"는 가정

### 2. 주의사항
| 편향 | 설명 | 방지 방법 |
|------|------|-----------|
| **룩어헤드 바이어스** | 미래 데이터를 현재 의사결정에 사용 | `.shift(1)`으로 신호를 1일 지연 |
| **생존편향** | 현재 존재하는 종목만 분석 | 상장폐지 종목 포함 |
| **과적합** | 특정 구간에만 최적화 | 훈련/검증 데이터 분리 (워크포워드) |
| **거래비용 무시** | 수수료·슬리피지 미고려 | 거래마다 비용 차감 |

### 3. 백테스트 기본 구조
```python
# 1. 데이터 준비
# 2. 신호 생성 (매수/매도 시점)
# 3. 포지션 관리 (진입/청산)
# 4. 수익률 계산 (거래비용 포함)
# 5. 성과 지표 계산 (수익률, MDD, 샤프지수)
```

---

## 🧪 LAB 1 – 수동 백테스트 프레임워크 (10:00 – 12:00)

```python
# backtest_manual.py
import yfinance as yf
import pandas as pd
import numpy as np

class SimpleBacktest:
    """단순 롱온리 백테스트 클래스"""

    def __init__(self, df: pd.DataFrame, signal_col: str,
                 commission: float = 0.001):
        self.df = df.copy()
        self.signal_col = signal_col
        self.commission = commission  # 왕복 기준 거래비용

    def run(self) -> pd.DataFrame:
        df = self.df.copy()

        # 신호 다음날 실행 (룩어헤드 바이어스 방지)
        df["Position"] = df[self.signal_col].shift(1)
        df["Position"] = df["Position"].fillna(0)

        # 포지션 변경 여부 (거래비용 적용 시점)
        df["Trade"] = df["Position"].diff().abs()

        # 일간 수익률
        df["Daily_Return"]    = df["Close"].pct_change()
        df["Strategy_Return"] = df["Daily_Return"] * df["Position"]
        df["Strategy_Return"] -= df["Trade"] * self.commission  # 거래비용 차감

        # 누적 수익률
        df["Cum_BH"]  = (1 + df["Daily_Return"]).cumprod()
        df["Cum_Str"] = (1 + df["Strategy_Return"]).cumprod()
        return df.dropna()

    def metrics(self, df: pd.DataFrame) -> dict:
        ret = df["Strategy_Return"]
        cum = df["Cum_Str"]
        ann_ret = (cum.iloc[-1] ** (252/len(df)) - 1) * 100
        ann_vol = ret.std() * np.sqrt(252) * 100
        sharpe  = ann_ret / ann_vol if ann_vol > 0 else 0
        mdd     = ((cum / cum.cummax()) - 1).min() * 100
        n_trades= (df["Trade"] > 0).sum()
        return {
            "연수익률(%)": round(ann_ret, 2),
            "연변동성(%)": round(ann_vol, 2),
            "샤프지수": round(sharpe, 3),
            "최대낙폭(%)": round(mdd, 2),
            "거래 횟수": int(n_trades),
            "최종 누적수익률(%)": round((cum.iloc[-1]-1)*100, 2),
        }


# 데이터 및 전략 준비
df = yf.download("AAPL", period="3y", auto_adjust=True)[["Close"]]
df.columns = ["Close"]
df["MA5"]  = df["Close"].rolling(5).mean()
df["MA20"] = df["Close"].rolling(20).mean()
df["Signal"] = np.where(df["MA5"] > df["MA20"], 1, 0)

bt = SimpleBacktest(df, signal_col="Signal", commission=0.001)
result = bt.run()
metrics = bt.metrics(result)

print("=== MA5/MA20 전략 백테스트 결과 ===")
for k, v in metrics.items():
    print(f"  {k}: {v}")
```

---

## 🧪 LAB 2 – backtesting.py 라이브러리 활용 (13:00 – 15:00)

```python
# backtest_lib.py
# pip install backtesting
import yfinance as yf
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas_ta as ta  # 또는 직접 계산

class MACrossStrategy(Strategy):
    fast = 5
    slow = 20

    def init(self):
        close = self.data.Close
        self.ma_fast = self.I(lambda x: x.rolling(self.fast).mean(), close)
        self.ma_slow = self.I(lambda x: x.rolling(self.slow).mean(), close)

    def next(self):
        if crossover(self.ma_fast, self.ma_slow):
            self.buy()
        elif crossover(self.ma_slow, self.ma_fast):
            self.sell()


# 데이터 준비 (backtesting.py는 OHLCV 컬럼 필요)
df = yf.download("AAPL", period="5y", auto_adjust=True)
df.columns = ["Open","High","Low","Close","Volume"]
df.index.name = "Date"

bt = Backtest(df, MACrossStrategy, cash=100000, commission=0.001)
stats = bt.run()
print(stats)

# 파라미터 최적화
stats_opt = bt.optimize(fast=range(3, 15, 2), slow=range(10, 40, 5),
                         maximize="Sharpe Ratio",
                         constraint=lambda p: p.fast < p.slow)
print("\n=== 최적 파라미터 ===")
print(f"fast={stats_opt._strategy.fast}, slow={stats_opt._strategy.slow}")
print(f"최적 샤프지수: {stats_opt['Sharpe Ratio']:.3f}")
```

---

## 🧪 LAB 3 – 훈련/검증 분리 백테스트 (워크포워드) (15:00 – 17:00)

```python
# walkforward.py
import yfinance as yf
import pandas as pd
import numpy as np

def compute_strategy_return(df: pd.DataFrame, fast: int, slow: int,
                             cost: float = 0.001) -> pd.Series:
    df = df.copy()
    df["Signal"]   = np.where(df["Close"].rolling(fast).mean() >
                               df["Close"].rolling(slow).mean(), 1, 0)
    df["Position"] = df["Signal"].shift(1)
    df["Trade"]    = df["Position"].diff().abs()
    df["Ret"]      = df["Close"].pct_change() * df["Position"] - df["Trade"] * cost
    return df["Ret"].dropna()

df = yf.download("AAPL", period="5y", auto_adjust=True)[["Close"]]
df.columns = ["Close"]

# 70% 훈련 / 30% 검증
split = int(len(df) * 0.7)
train, test = df.iloc[:split], df.iloc[split:]

print(f"훈련: {train.index[0].date()} ~ {train.index[-1].date()} ({len(train)}일)")
print(f"검증: {test.index[0].date()}  ~ {test.index[-1].date()}  ({len(test)}일)")

best_sharpe, best_fast, best_slow = -999, 5, 20
for fast in range(3, 20, 2):
    for slow in range(fast+5, 60, 5):
        ret = compute_strategy_return(train, fast, slow)
        sharpe = ret.mean() / ret.std() * np.sqrt(252) if ret.std() > 0 else -999
        if sharpe > best_sharpe:
            best_sharpe, best_fast, best_slow = sharpe, fast, slow

print(f"\n최적 파라미터 (훈련): fast={best_fast}, slow={best_slow}, Sharpe={best_sharpe:.3f}")

test_ret = compute_strategy_return(test, best_fast, best_slow)
test_sharpe = test_ret.mean() / test_ret.std() * np.sqrt(252)
test_cum    = (1 + test_ret).prod() - 1
print(f"검증 샤프지수: {test_sharpe:.3f}")
print(f"검증 수익률:   {test_cum*100:.2f}%")
```

---

## 📝 과제 (17:00 – 18:00)

1. `SimpleBacktest` 클래스를 RSI 전략에도 적용하고 MA 전략과 성과를 비교하세요.
2. 거래비용을 0%, 0.05%, 0.1%, 0.5%로 변화시키면서 수익률에 미치는 영향을 분석하세요.
3. 훈련(3년)/검증(1년) 기간을 설정하고 최적화 파라미터의 실전 성능 저하 여부를 확인하세요.

---

## ✅ 체크리스트

- [ ] 룩어헤드 바이어스 개념 이해 및 `.shift(1)` 적용 확인
- [ ] `SimpleBacktest` 클래스 구현 및 실행 성공
- [ ] `backtesting.py` 라이브러리로 전략 최적화 성공
- [ ] 훈련/검증 분리 백테스트 구현 성공
- [ ] 과제 제출

---

## 📚 참고자료

- [backtesting.py 공식 문서](https://kernc.github.io/backtesting.py/)
- [Investopedia – 백테스트](https://www.investopedia.com/terms/b/backtesting.asp)
- [Look-Ahead Bias 설명](https://www.investopedia.com/terms/l/lookaheadbias.asp)
