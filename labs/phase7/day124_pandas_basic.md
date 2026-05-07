# Day 124 – pandas 기초

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (초급)

---

## 🎯 학습 목표

- `pandas` Series와 DataFrame 생성·조회·수정
- 인덱싱(`iloc`, `loc`), 슬라이싱, 조건 필터링
- 집계 함수(mean, sum, describe) 활용
- CSV 파일 읽기/쓰기

---

## 📖 이론 (08:00 – 10:00)

### 1. Series vs DataFrame
```python
import pandas as pd

# Series – 1차원 배열 (인덱스 + 값)
s = pd.Series([100, 200, 150], index=["Mon", "Tue", "Wed"])

# DataFrame – 2차원 테이블 (행 인덱스 + 열 이름)
df = pd.DataFrame({
    "Open":  [50000, 51000, 52000],
    "Close": [51000, 50500, 53000],
    "Volume":[100000, 85000, 120000],
})
```

### 2. 인덱싱
```python
df["Close"]          # 열 선택
df[["Open","Close"]] # 여러 열

df.iloc[0]           # 0번째 행 (정수 위치)
df.loc["2024-01-02"] # 라벨 기반 행 선택

df[df["Close"] > 51000]  # 조건 필터링
```

### 3. 집계 함수
```python
df["Close"].mean()   # 평균
df["Close"].std()    # 표준편차
df.describe()        # 기술 통계량
```

---

## 🧪 LAB 1 – DataFrame 생성 & 기본 조회 (10:00 – 12:00)

```python
# pandas_basic.py
import pandas as pd

# 주가 데이터 생성
data = {
    "Date":  ["2024-01-02","2024-01-03","2024-01-04","2024-01-05","2024-01-08"],
    "Open":  [73800, 74200, 74000, 73500, 74500],
    "High":  [74500, 75000, 74800, 74200, 75200],
    "Low":   [73500, 73800, 73200, 73000, 74300],
    "Close": [74200, 74800, 73600, 74000, 75100],
    "Volume":[12500000, 9800000, 14200000, 11000000, 10500000],
}

df = pd.DataFrame(data)
df["Date"] = pd.to_datetime(df["Date"])
df = df.set_index("Date")

print("--- 기본 정보 ---")
print(df.info())
print("\n--- 상위 3행 ---")
print(df.head(3))
print("\n--- 기술 통계 ---")
print(df.describe())

# 조건 필터링: 종가 74000 이상
high_close = df[df["Close"] >= 74000]
print(f"\n종가 74,000 이상인 날: {len(high_close)}일")
print(high_close[["Close", "Volume"]])
```

---

## 🧪 LAB 2 – 열 추가 & 집계 (13:00 – 15:00)

```python
# pandas_transform.py
import pandas as pd

df = pd.read_csv("stock_data.csv", index_col="Date", parse_dates=True) \
    if __import__("os").path.exists("stock_data.csv") \
    else pd.DataFrame({
        "Open":  [50000,51000,52000,51500,53000],
        "High":  [51500,52000,53000,52500,54000],
        "Low":   [49500,50500,51500,51000,52000],
        "Close": [51000,51500,52500,52000,53500],
        "Volume":[1000000,900000,1200000,800000,1100000],
    }, index=pd.date_range("2024-01-02", periods=5, freq="B"))

# 새 열 추가
df["Change"] = df["Close"].diff()               # 전일 대비 변화
df["Return(%)"] = df["Close"].pct_change() * 100  # 일간 수익률
df["Range"] = df["High"] - df["Low"]            # 당일 가격 범위

print(df.round(2))

# 주별 집계
df_weekly = df["Close"].resample("W").agg(["first","last","max","min"])
df_weekly.columns = ["시가","종가","최고","최저"]
print("\n=== 주별 집계 ===")
print(df_weekly)
```

---

## 🧪 LAB 3 – CSV 저장 & 불러오기 (15:00 – 17:00)

```python
# csv_io.py
import pandas as pd
import yfinance as yf

# 데이터 다운로드
df = yf.download("AAPL", period="3mo", auto_adjust=True)
df = df[["Open","High","Low","Close","Volume"]]

# CSV 저장
df.to_csv("aapl_3mo.csv")
print(f"저장 완료: aapl_3mo.csv ({len(df)}행)")

# CSV 불러오기
loaded = pd.read_csv("aapl_3mo.csv", index_col="Date", parse_dates=True)
print(f"\n불러온 행 수: {len(loaded)}")
print(loaded.tail())

# 기본 통계
print("\n=== 기술 통계 ===")
print(loaded["Close"].describe())
print(f"\n최고 종가: {loaded['Close'].max():.2f}")
print(f"최저 종가: {loaded['Close'].min():.2f}")
print(f"평균 종가: {loaded['Close'].mean():.2f}")
```

---

## 📝 과제 (17:00 – 18:00)

1. `yfinance`로 삼성전자(005930.KS) 최근 6개월 데이터를 다운로드하고 CSV로 저장하세요.
2. 저장된 CSV를 읽어 일간 수익률 열을 추가하고, 수익률이 2% 이상인 날만 필터링하세요.
3. `describe()`로 기술 통계를 출력하고 가장 변동성이 큰 날을 찾으세요.

---

## ✅ 체크리스트

- [ ] Series·DataFrame 생성 및 조회 성공
- [ ] `iloc`, `loc`, 조건 필터링 실습 완료
- [ ] 새 열 추가(diff, pct_change) 성공
- [ ] CSV 저장·불러오기 성공
- [ ] 과제 제출

---

## 📚 참고자료

- [pandas 공식 문서](https://pandas.pydata.org/docs/)
- [pandas 10분 빠른 시작](https://pandas.pydata.org/docs/user_guide/10min.html)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day124+pandas+basic
