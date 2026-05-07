# Day 140 – 중급 종합 리뷰 & 코드 리뷰 세션

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (중급 마무리)

---

## 🎯 학습 목표

- Day 131~139 핵심 기술적 분석·백테스트 개념 복습
- 코드 리뷰: 룩어헤드 바이어스·거래비용 처리 점검
- 중급 단계 퀴즈 및 디버깅 실습
- 고급 과정(머신러닝) 예습 및 학습 계획 수립

---

## 📖 이론 복습 (08:00 – 10:00)

### 핵심 개념 정리

| 주제 | 핵심 내용 |
|------|-----------|
| 이동평균(MA) | SMA·EMA 차이, 골든/데드크로스 신호 |
| RSI | 14일 기준, 70 과매수·30 과매도, Wilder EWM |
| MACD | EMA(12)-EMA(26), Signal EMA(9), 히스토그램 |
| 볼린저밴드 | 20일 SMA ± 2σ, %B, Bandwidth |
| 스토캐스틱 | %K·%D, 80/20 기준 |
| ATR | True Range 14일 EWM, 손절가 설정에 활용 |
| 백테스트 기초 | `.shift(1)` 룩어헤드 방지, 거래비용 차감 |
| 백테스트 성과 | CAGR·Sharpe·Sortino·Calmar·MDD·승률 |
| 자동매매 | 신호 생성 → 포지션 관리 → 손절·익절 |
| 포트폴리오 | 등비중·변동성 역비례, 분기 리밸런싱 |

---

## 🧪 LAB 1 – 종합 지표 계산기 (10:00 – 12:00)

```python
# tech_indicator_suite.py
import yfinance as yf
import pandas as pd
import numpy as np

def all_indicators(symbol: str, period: str = "1y") -> pd.DataFrame:
    """모든 기술적 지표를 한 번에 계산"""
    df = yf.download(symbol, period=period, auto_adjust=True)
    df = df[["Open","High","Low","Close","Volume"]].copy()
    close, high, low = df["Close"].squeeze(), df["High"].squeeze(), df["Low"].squeeze()

    # MA
    for w in [5, 20, 60]:
        df[f"SMA{w}"] = close.rolling(w).mean()
        df[f"EMA{w}"] = close.ewm(span=w, adjust=False).mean()

    # RSI
    delta = close.diff()
    gain, loss = delta.clip(lower=0), (-delta).clip(lower=0)
    df["RSI14"] = 100 - 100 / (1 + gain.ewm(alpha=1/14, adjust=False).mean() /
                                     loss.ewm(alpha=1/14, adjust=False).mean())

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["MACD"]     = ema12 - ema26
    df["MACD_Sig"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"]= df["MACD"] - df["MACD_Sig"]

    # 볼린저밴드
    df["BB_mid"]   = close.rolling(20).mean()
    df["BB_std"]   = close.rolling(20).std()
    df["BB_upper"] = df["BB_mid"] + 2 * df["BB_std"]
    df["BB_lower"] = df["BB_mid"] - 2 * df["BB_std"]
    df["%B"]       = (close - df["BB_lower"]) / (df["BB_upper"] - df["BB_lower"])

    # ATR
    prev_close = close.shift(1)
    tr = pd.concat([high-low, (high-prev_close).abs(), (low-prev_close).abs()], axis=1).max(axis=1)
    df["ATR14"] = tr.ewm(alpha=1/14, adjust=False).mean()

    return df.dropna()

df = all_indicators("AAPL")
print(f"총 컬럼 수: {len(df.columns)}")
print(df.tail(3).T)
```

---

## 🧪 LAB 2 – 퀴즈 & 디버깅 실습 (13:00 – 15:00)

### 퀴즈 (직접 풀어보세요)

**Q1.** 아래 코드의 문제점은?
```python
# 룩어헤드 바이어스가 있는 코드
df["Signal"] = np.where(df["MA5"] > df["MA20"], 1, 0)
df["Return"] = df["Close"].pct_change() * df["Signal"]
```

**Q2.** RSI 계산 시 `ewm(alpha=1/14)` 대신 `rolling(14).mean()`을 쓰면 어떻게 다른가?

**Q3.** 볼린저밴드에서 `%B` 값이 1.2라면 어떤 상황인가?

**Q4.** 샤프지수가 1.5이고 소르티노가 0.8이라면, 이 전략의 특징은?

**Q5.** 워크포워드 테스트에서 훈련 성과는 좋지만 검증 성과가 나쁜 이유는?

---

```python
# quiz_debug.py – 각 문제를 코드로 검증해보세요

# Q1 수정 예시
import numpy as np, pandas as pd

prices = pd.Series([100,105,103,108,110,107,112,115,113,118])
ma3 = prices.rolling(3).mean()
ma5 = prices.rolling(5).mean()

# 잘못된 방식 (룩어헤드)
signal_wrong = np.where(ma3 > ma5, 1, 0)
# 올바른 방식
signal_right = pd.Series(np.where(ma3 > ma5, 1, 0)).shift(1).values

daily_return = prices.pct_change()
ret_wrong = (daily_return * signal_wrong).dropna()
ret_right = (daily_return * pd.Series(signal_right, index=prices.index)).dropna()

print(f"잘못된 누적: {(1+ret_wrong).prod():.4f}")
print(f"올바른 누적: {(1+ret_right).prod():.4f}")
```

---

## 🧪 LAB 3 – 전략 요약 보고서 자동화 (15:00 – 17:00)

```python
# review_report.py
import yfinance as yf
import pandas as pd
import numpy as np

def backtest_summary(symbol: str, period: str = "3y") -> dict:
    df = yf.download(symbol, period=period, auto_adjust=True)[["Close"]].dropna()
    df.columns = ["Close"]
    close = df["Close"].squeeze()

    # 지표
    ma5  = close.rolling(5).mean()
    ma20 = close.rolling(20).mean()
    rsi  = (lambda c, p=14: 100 - 100/(1 + c.diff().clip(lower=0).ewm(alpha=1/p,adjust=False).mean() /
            (-c.diff()).clip(lower=0).ewm(alpha=1/p,adjust=False).mean()))(close)

    # 신호
    buy  = (ma5 > ma20) & (rsi < 65)
    sell = (ma5 < ma20) | (rsi > 75)
    pos = pd.Series(0, index=df.index)
    state = 0
    for i in range(len(pos)):
        if buy.iloc[i] and state == 0:  state = 1
        elif sell.iloc[i] and state == 1: state = 0
        pos.iloc[i] = state
    pos = pos.shift(1)

    daily = close.pct_change()
    ret   = (daily * pos - pos.diff().abs() * 0.001).dropna()
    cum   = (1 + ret).cumprod()
    n     = len(ret)
    cagr  = (cum.iloc[-1]**(252/n)-1)*100
    vol   = ret.std()*np.sqrt(252)*100
    mdd   = ((cum/cum.cummax())-1).min()*100

    return {"Symbol":symbol, "CAGR(%)":round(cagr,2), "Vol(%)":round(vol,2),
            "Sharpe":round(cagr/vol,3) if vol else 0, "MDD(%)":round(mdd,2)}

symbols = ["AAPL","MSFT","NVDA","005930.KS"]
rows = []
for s in symbols:
    try: rows.append(backtest_summary(s))
    except Exception as e: print(f"{s}: {e}")

df_out = pd.DataFrame(rows)
print(df_out.to_string(index=False))
df_out.to_csv("intermediate_review.csv", index=False, encoding="utf-8-sig")
```

---

## 📝 과제 (17:00 – 18:00)

1. 퀴즈 5문항의 답을 코드로 검증하고 설명하세요.
2. Day 131~139 중 가장 어려웠던 개념을 선택하고, 자신의 말로 설명하는 글을 작성하세요.
3. 고급 과정에서 배울 LSTM 모델의 입력 데이터를 어떻게 준비해야 할지 계획을 세우세요.

---

## ✅ 중급 과정 최종 체크리스트

- [ ] MA·RSI·MACD·볼린저밴드·스토캐스틱·ATR 구현 가능
- [ ] 룩어헤드 바이어스 없는 백테스트 구현 가능
- [ ] CAGR·Sharpe·MDD·승률 성과 지표 계산 가능
- [ ] 포지션 관리(손절·익절) 로직 구현 가능
- [ ] 다종목 백테스트 및 성과 대시보드 생성 가능
- [ ] 포트폴리오 자산 배분 및 리밸런싱 구현 가능

---

## 📚 다음 단계 (고급 – Day 141~150) 예습

- scikit-learn: `pip install scikit-learn`
- xgboost: `pip install xgboost`
- tensorflow: `pip install tensorflow`
- statsmodels: `pip install statsmodels`
- optuna: `pip install optuna`

```python
# 설치 확인
import sklearn, xgboost, tensorflow, statsmodels, optuna
print(f"sklearn:     {sklearn.__version__}")
print(f"xgboost:     {xgboost.__version__}")
print(f"tensorflow:  {tensorflow.__version__}")
print(f"statsmodels: {statsmodels.__version__}")
print(f"optuna:      {optuna.__version__}")
```

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day140+review+intermediate
