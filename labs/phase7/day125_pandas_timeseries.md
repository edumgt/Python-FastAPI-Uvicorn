# Day 125 – pandas 시계열 처리

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (초급)

---

## 🎯 학습 목표

- `DatetimeIndex`를 활용한 시계열 인덱싱 및 슬라이싱
- `resample()`로 일간→주간·월간 데이터 변환
- `rolling()`으로 이동 통계 계산
- `shift()`로 시차 데이터 생성 (lag feature)

---

## 📖 이론 (08:00 – 10:00)

### 1. DatetimeIndex
```python
import pandas as pd

idx = pd.date_range("2024-01-01", periods=10, freq="B")  # 영업일
df.index = pd.to_datetime(df.index)

# 슬라이싱
df["2024-01"]          # 1월 전체
df["2024-01":"2024-03"]  # 1월~3월
```

### 2. resample
```python
# 주간 OHLCV 집계
weekly = df["Close"].resample("W").last()  # 주말 종가
monthly = df.resample("ME").agg({
    "Open": "first", "High": "max",
    "Low": "min",  "Close": "last", "Volume": "sum"
})
```

### 3. rolling & ewm
```python
df["MA5"]  = df["Close"].rolling(window=5).mean()   # 5일 단순이동평균
df["MA20"] = df["Close"].rolling(window=20).mean()  # 20일 단순이동평균
df["EMA12"]= df["Close"].ewm(span=12).mean()        # 12일 지수이동평균
df["Std20"]= df["Close"].rolling(window=20).std()   # 20일 표준편차
```

### 4. shift
```python
df["Prev_Close"] = df["Close"].shift(1)   # 전일 종가 (1일 시차)
df["Return"]     = df["Close"] / df["Prev_Close"] - 1
```

---

## 🧪 LAB 1 – DatetimeIndex 슬라이싱 (10:00 – 12:00)

```python
# timeseries_index.py
import yfinance as yf
import pandas as pd

df = yf.download("AAPL", start="2023-01-01", end="2024-12-31", auto_adjust=True)
df = df[["Open","High","Low","Close","Volume"]]

print(f"전체 기간: {df.index[0].date()} ~ {df.index[-1].date()} ({len(df)}일)")

# 특정 월 슬라이싱
jan_2024 = df["2024-01"]
print(f"\n2024년 1월 데이터: {len(jan_2024)}일")
print(jan_2024["Close"])

# 분기별 평균 종가
quarterly = df["Close"].resample("QE").mean()
print("\n=== 분기별 평균 종가 ===")
print(quarterly.round(2))
```

---

## 🧪 LAB 2 – rolling & resample (13:00 – 15:00)

```python
# rolling_resample.py
import yfinance as yf
import pandas as pd

df = yf.download("005930.KS", period="1y", auto_adjust=True)[["Close","Volume"]]

# 이동평균 계산
df["MA5"]  = df["Close"].rolling(5).mean()
df["MA20"] = df["Close"].rolling(20).mean()
df["MA60"] = df["Close"].rolling(60).mean()

# 볼린저밴드 (20일)
df["BB_mid"]  = df["Close"].rolling(20).mean()
df["BB_upper"]= df["BB_mid"] + 2 * df["Close"].rolling(20).std()
df["BB_lower"]= df["BB_mid"] - 2 * df["Close"].rolling(20).std()

print("=== 이동평균 (최근 5행) ===")
print(df[["Close","MA5","MA20","MA60"]].tail())

# 월간 요약
monthly = df["Close"].resample("ME").agg(["first","last","max","min","mean"])
monthly.columns = ["시가","종가","최고","최저","평균"]
monthly["월수익률(%)"] = (monthly["종가"] / monthly["시가"] - 1) * 100
print("\n=== 월간 요약 ===")
print(monthly.round(1).tail(6))
```

---

## 🧪 LAB 3 – shift & 시차 특성 (15:00 – 17:00)

```python
# lag_features.py
import yfinance as yf
import pandas as pd

df = yf.download("AAPL", period="1y", auto_adjust=True)[["Close"]]

# 시차 특성 생성
for lag in [1, 2, 3, 5]:
    df[f"Close_lag{lag}"] = df["Close"].shift(lag)

# 일간 수익률
df["Return_1d"] = df["Close"].pct_change(1) * 100
df["Return_5d"] = df["Close"].pct_change(5) * 100

# 미래 수익률 (예측 타겟으로 사용)
df["Future_1d"] = df["Close"].shift(-1)
df["Target"]    = (df["Future_1d"] > df["Close"]).astype(int)  # 1=상승, 0=하락

print("=== 시차 특성 및 타겟 (최근 8행) ===")
cols = ["Close", "Close_lag1", "Return_1d", "Return_5d", "Target"]
print(df[cols].tail(8).round(2))

# 결측값 처리
df_clean = df.dropna()
print(f"\n결측값 제거 후: {len(df_clean)}행")
```

---

## 📝 과제 (17:00 – 18:00)

1. 코스피 지수(`KS11`)의 최근 2년 데이터를 가져와 주간·월간·분기별 수익률을 계산하세요.
2. 5일·20일·60일 이동평균선을 계산하고, 최근 골든크로스(5일이 20일을 상향 돌파) 날짜를 찾으세요.
3. `shift()`를 활용해 5일 후 종가 방향(상승=1, 하락=0)을 타겟 열로 추가하세요.

---

## ✅ 체크리스트

- [ ] `DatetimeIndex` 슬라이싱 실습 완료
- [ ] `resample()`로 주간·월간 집계 성공
- [ ] `rolling()`으로 이동평균·볼린저밴드 계산 성공
- [ ] `shift()`로 시차 특성 및 타겟 열 생성 성공
- [ ] 과제 제출

---

## 📚 참고자료

- [pandas 시계열 가이드](https://pandas.pydata.org/docs/user_guide/timeseries.html)
- [pandas resample](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html)
- [pandas rolling](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rolling.html)
