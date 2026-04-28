# Day 130 – 초급 종합 리뷰 & 코드 리뷰 세션

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (초급 마무리)

---

## 🎯 학습 목표

- Day 121~129 핵심 개념 복습 및 빈틈 보완
- 미니 프로젝트 코드 리뷰 및 개선
- 초급 단계 퀴즈로 이해도 점검
- 중급 과정 예습 및 학습 계획 수립

---

## 📖 이론 복습 (08:00 – 10:00)

### 핵심 개념 정리

| 주제 | 핵심 내용 |
|------|-----------|
| 금융 데이터 기초 | OHLCV, 수익률, 변동성 계산 |
| yfinance | `Ticker.history()`, `Ticker.info`, 멀티 티커 다운로드 |
| FinanceDataReader | 국내 주식, 상장 목록, 인덱스 데이터 수집 |
| pandas 기초 | Series·DataFrame, iloc/loc, 조건 필터링 |
| pandas 시계열 | DatetimeIndex, resample, rolling, shift |
| 시각화 | matplotlib 라인·바 차트, plotly 캔들스틱 |
| 데이터 정제 | 결측값(ffill, interpolate), 이상값(Z-score, IQR), 스케일링 |
| 기본적 분석 | PER·PBR·ROE·EPS 계산 및 스크리닝 |
| 미니 프로젝트 | 데이터 수집 → 분석 → 시각화 → PDF 리포트 파이프라인 |

---

## 🧪 LAB 1 – 종합 실습: 퀵 분석 파이프라인 (10:00 – 12:00)

```python
# review_pipeline.py
import yfinance as yf
import pandas as pd
import numpy as np

def quick_analyze(symbol: str) -> dict:
    """단일 종목 빠른 분석"""
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1y", auto_adjust=True).squeeze()
    info = ticker.info

    close = hist["Close"] if isinstance(hist, pd.DataFrame) else hist

    # 결측값 처리
    close = close.fillna(method="ffill").dropna()

    # 이동평균
    ma20 = close.rolling(20).mean()
    ma60 = close.rolling(60).mean()
    trend = "상승추세" if close.iloc[-1] > ma20.iloc[-1] > ma60.iloc[-1] else "하락추세"

    # 수익률 및 변동성
    ret = (close.iloc[-1] / close.iloc[0] - 1) * 100
    vol = close.pct_change().std() * np.sqrt(252) * 100

    # MDD
    mdd = ((close / close.cummax()) - 1).min() * 100

    return {
        "종목": info.get("shortName", symbol),
        "현재가": round(close.iloc[-1], 2),
        "연수익률(%)": round(ret, 2),
        "연변동성(%)": round(vol, 2),
        "MDD(%)": round(mdd, 2),
        "PER": round(info.get("trailingPE") or 0, 2),
        "PBR": round(info.get("priceToBook") or 0, 2),
        "ROE(%)": round((info.get("returnOnEquity") or 0) * 100, 2),
        "추세": trend,
    }

symbols = ["AAPL", "MSFT", "NVDA", "005930.KS"]
results = [quick_analyze(s) for s in symbols]
df = pd.DataFrame(results)
print(df.to_string(index=False))
```

---

## 🧪 LAB 2 – 퀴즈 & 코드 점검 (13:00 – 15:00)

### 퀴즈 (직접 풀어보세요)

**Q1.** 다음 코드의 출력 결과는?
```python
import pandas as pd
s = pd.Series([10, 20, 30, 40, 50])
print(s.rolling(3).mean().iloc[2])
```

**Q2.** 아래 코드에서 `df_weekly`에 몇 개의 행이 있을까? (입력: 일별 5행 데이터)
```python
df_weekly = df.resample("W").last()
```

**Q3.** `MinMaxScaler`를 적용한 값의 범위는?

**Q4.** 다음 중 PBR < 1이 의미하는 것은?  
a) 과대평가  b) 청산 가치 이하  c) 적정 평가  d) 수익성 우수

**Q5.** Z-score 이상값 탐지에서 `|Z| > 3`은 어느 쪽 꼬리 %를 의미할까?

---

```python
# quiz_answers.py (LAB 시간에 직접 채워보세요)

# Q1 답:
q1 = None  # ?

# Q2 답:
q2 = None  # ?

# Q3 답:
q3 = None  # ?

# Q4 답:
q4 = None  # ?

# Q5 답:
q5 = None  # ?

print(f"Q1: {q1}")
print(f"Q2: {q2}")
print(f"Q3: {q3}")
print(f"Q4: {q4}")
print(f"Q5: {q5}")
```

---

## 🧪 LAB 3 – 미니 프로젝트 개선 & 코드 리뷰 (15:00 – 17:00)

### 개선 포인트 체크리스트

강사와 함께 Day 129 미니 프로젝트를 리뷰하며 아래 항목을 점검합니다.

- [ ] **모듈화**: 각 기능이 적절히 분리되어 있는가?
- [ ] **예외 처리**: 네트워크 오류나 빈 데이터 처리가 되어 있는가?
- [ ] **타입 힌트**: 함수 인자와 반환값에 타입 힌트가 있는가?
- [ ] **코드 중복**: 반복 코드는 함수로 추출했는가?
- [ ] **가독성**: 변수 이름이 의미 있고 주석이 적절한가?

```python
# 개선 예시: 예외 처리 추가
import yfinance as yf
import pandas as pd

def safe_collect(symbol: str) -> tuple[pd.DataFrame | None, dict]:
    """예외 처리가 포함된 안전한 데이터 수집"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1y", auto_adjust=True)
        info = ticker.info
        if hist.empty:
            print(f"[경고] {symbol}: 데이터가 비어 있습니다.")
            return None, {}
        return hist, info
    except Exception as e:
        print(f"[오류] {symbol}: {e}")
        return None, {}
```

---

## 📝 과제 (17:00 – 18:00)

1. 퀴즈 5문항의 답을 코드로 검증하고 결과를 설명하세요.
2. Day 129 미니 프로젝트에 예외 처리와 타입 힌트를 추가하여 개선된 버전을 제출하세요.
3. 중급 과정(Day 131~140)에서 배울 기술적 분석 지표 중 가장 궁금한 것을 선택하고, 왜 필요한지 간단히 설명하세요.

---

## ✅ 초급 과정 최종 체크리스트

- [ ] 금융 데이터(OHLCV, 재무 지표) 수집 자유롭게 가능
- [ ] pandas로 시계열 데이터 분석 가능
- [ ] matplotlib·plotly로 차트 생성 가능
- [ ] 결측값·이상값 탐지 및 처리 가능
- [ ] PER·PBR·ROE 등 기본적 분석 지표 이해 및 계산 가능
- [ ] 미니 프로젝트 (PDF 리포트) 완성

---

## 📚 참고자료

- [pandas Cheat Sheet](https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf)
- [matplotlib Gallery](https://matplotlib.org/stable/gallery/index.html)
- [Investopedia 금융 사전](https://www.investopedia.com/financial-term-dictionary-4769738)
