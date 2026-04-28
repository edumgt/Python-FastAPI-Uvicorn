# Day 121 – 금융 데이터 개요

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (초급)

---

## 🎯 학습 목표

- 주식·ETF·암호화폐의 차이와 특성 이해
- 금융 시장 구조 및 거래소 개념 파악
- OHLCV 데이터(시가·고가·저가·종가·거래량) 이해
- 수익률·변동성 기본 계산 방법 습득

---

## 📖 이론 (08:00 – 10:00)

### 1. 금융 상품 종류
| 종류 | 설명 | 예시 |
|------|------|------|
| 주식 (Stock) | 기업 소유권의 일부 | 삼성전자, Apple (AAPL) |
| ETF | 인덱스·섹터를 추종하는 펀드 | KODEX 200, SPY |
| 암호화폐 | 블록체인 기반 디지털 자산 | Bitcoin (BTC), Ethereum (ETH) |

### 2. OHLCV 데이터
```
Open  : 시가 (장 시작 가격)
High  : 고가 (당일 최고 가격)
Low   : 저가 (당일 최저 가격)
Close : 종가 (장 마감 가격)
Volume: 거래량
```

### 3. 수익률 계산
```
단순 수익률 = (현재가 - 매수가) / 매수가 × 100 (%)
로그 수익률 = ln(현재가 / 전일가)
```

### 4. 시장 구조
- **장내 시장**: KRX(한국거래소), NYSE, NASDAQ
- **장외 시장(OTC)**: 직접 거래
- **암호화폐 거래소**: 업비트, 바이낸스, 코인베이스

---

## 🧪 LAB 1 – 수익률 계산기 (10:00 – 12:00)

```python
# finance_basics.py

def simple_return(buy_price: float, current_price: float) -> float:
    """단순 수익률(%) 계산"""
    return (current_price - buy_price) / buy_price * 100

def log_return(prev_price: float, curr_price: float) -> float:
    """로그 수익률 계산"""
    import math
    return math.log(curr_price / prev_price)

def cumulative_return(prices: list[float]) -> float:
    """누적 수익률(%) 계산"""
    return (prices[-1] / prices[0] - 1) * 100

# 예시 실행
prices = [50000, 52000, 51000, 55000, 53000]
print(f"단순 수익률: {simple_return(prices[0], prices[-1]):.2f}%")
print(f"누적 수익률: {cumulative_return(prices):.2f}%")

returns = [log_return(prices[i], prices[i+1]) for i in range(len(prices)-1)]
print(f"로그 수익률 목록: {[f'{r:.4f}' for r in returns]}")
```

---

## 🧪 LAB 2 – 변동성 계산 (13:00 – 15:00)

```python
# volatility.py
import math
import statistics

prices = [50000, 52000, 51000, 55000, 53000, 56000, 54000]

# 일별 로그 수익률
log_returns = [math.log(prices[i+1] / prices[i]) for i in range(len(prices)-1)]

# 변동성 = 표준편차
daily_vol = statistics.stdev(log_returns)
annual_vol = daily_vol * math.sqrt(252)  # 연간화

print(f"일별 변동성: {daily_vol:.4f}")
print(f"연간 변동성: {annual_vol:.4f} ({annual_vol*100:.2f}%)")

# 최고/최저
print(f"최고가: {max(prices):,}원")
print(f"최저가: {min(prices):,}원")
print(f"가격 범위: {max(prices) - min(prices):,}원")
```

---

## 🧪 LAB 3 – 금융 용어 사전 JSON 만들기 (15:00 – 17:00)

```python
# finance_glossary.py
import json

glossary = {
    "OHLCV": "Open(시가)·High(고가)·Low(저가)·Close(종가)·Volume(거래량)",
    "PER": "주가수익비율 = 주가 / EPS (낮을수록 저평가)",
    "PBR": "주가순자산비율 = 주가 / BPS (1 미만이면 청산가치 이하)",
    "ROE": "자기자본이익률 = 순이익 / 자기자본 × 100",
    "EPS": "주당순이익 = 순이익 / 발행주식수",
    "MA" : "이동평균선 – 일정 기간 종가의 평균",
    "RSI": "상대강도지수 – 0~100, 70 이상 과매수·30 이하 과매도",
    "MACD": "이동평균 수렴·발산 – 추세 전환 신호 지표",
    "ETF": "Exchange Traded Fund – 거래소에 상장된 펀드",
    "MDD": "최대낙폭 – 고점 대비 최대 하락률",
}

with open("finance_glossary.json", "w", encoding="utf-8") as f:
    json.dump(glossary, f, ensure_ascii=False, indent=2)

with open("finance_glossary.json", encoding="utf-8") as f:
    loaded = json.load(f)

for term, definition in loaded.items():
    print(f"[{term}] {definition}")
```

---

## 📝 과제 (17:00 – 18:00)

1. 삼성전자(005930) 최근 5일 종가를 직접 조사하여 리스트로 작성하세요.
2. 단순 수익률, 로그 수익률, 일별 변동성을 계산하세요.
3. 본인이 관심 있는 금융 상품 3가지를 선택하고 간단한 소개를 JSON 파일로 저장하세요.

---

## ✅ 체크리스트

- [ ] OHLCV 개념 이해 완료
- [ ] 단순·로그 수익률 계산 코드 작성
- [ ] 변동성 계산 코드 작성
- [ ] 금융 용어 사전 JSON 저장 성공
- [ ] 과제 제출

---

## 📚 참고자료

- [KRX 한국거래소](https://www.krx.co.kr)
- [Investopedia – OHLC](https://www.investopedia.com/terms/o/ohlc.asp)
- [업비트 개발자 센터](https://docs.upbit.com)
