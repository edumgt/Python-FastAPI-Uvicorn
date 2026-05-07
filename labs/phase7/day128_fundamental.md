# Day 128 – 기본적 분석 (PER·PBR·EPS·ROE)

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (초급)

---

## 🎯 학습 목표

- PER·PBR·EPS·ROE·배당수익률 등 핵심 투자 지표 계산 및 해석
- `yfinance`로 재무 지표 자동 수집
- 동일 섹터 내 종목 비교 분석 (스크리닝)
- 저평가 종목을 판단하는 기준 수립

---

## 📖 이론 (08:00 – 10:00)

### 1. 핵심 가치 지표
| 지표 | 계산식 | 해석 |
|------|--------|------|
| **EPS** | 순이익 / 발행주식수 | 높을수록 수익성 좋음 |
| **PER** | 주가 / EPS | 낮을수록 저평가 (동종업계 비교 필수) |
| **BPS** | 순자산 / 발행주식수 | 주당 청산가치 |
| **PBR** | 주가 / BPS | 1 미만이면 청산가치 이하 |
| **ROE** | 순이익 / 자기자본 × 100 | 높을수록 자본 효율성 좋음 |
| **배당수익률** | 연간배당금 / 주가 × 100 | 높을수록 배당 매력 |

### 2. 기본적 분석 판단 기준 (일반적)
- PER: 업종 평균 대비 낮으면 저평가 신호
- PBR < 1: 청산 가치 이하 (가치 투자 관심 구간)
- ROE > 15%: 우수한 자본 효율
- 배당수익률 > 시장 평균: 배당주 매력

### 3. 워런 버핏식 스크리닝 기준 (예시)
- ROE ≥ 15% (3년 연속)
- 부채비율 ≤ 50%
- PER ≤ 업종 평균
- EPS 꾸준히 성장

---

## 🧪 LAB 1 – yfinance 재무 지표 수집 (10:00 – 12:00)

```python
# fundamental.py
import yfinance as yf
import pandas as pd

tickers = ["AAPL", "MSFT", "GOOGL", "META", "AMZN"]
fields = [
    "currentPrice", "trailingPE", "forwardPE", "priceToBook",
    "trailingEps", "returnOnEquity", "dividendYield",
    "debtToEquity", "revenueGrowth", "earningsGrowth",
    "marketCap", "sector"
]

rows = []
for symbol in tickers:
    info = yf.Ticker(symbol).info
    row = {"Symbol": symbol}
    for f in fields:
        val = info.get(f, None)
        if isinstance(val, float):
            if f in ("dividendYield", "returnOnEquity", "revenueGrowth", "earningsGrowth"):
                val = round(val * 100, 2)  # 백분율로 변환
            else:
                val = round(val, 2)
        row[f] = val
    rows.append(row)

df = pd.DataFrame(rows).set_index("Symbol")
print(df.to_string())
```

---

## 🧪 LAB 2 – 섹터 비교 스크리닝 (13:00 – 15:00)

```python
# screening.py
import yfinance as yf
import pandas as pd

# 반도체 섹터 대표 종목
semis = ["NVDA", "AMD", "INTC", "QCOM", "AVGO", "TSM", "ASML", "MU"]

rows = []
for symbol in semis:
    try:
        info = yf.Ticker(symbol).info
        rows.append({
            "Symbol": symbol,
            "Name": info.get("shortName", ""),
            "Price": info.get("currentPrice", None),
            "PER": info.get("trailingPE", None),
            "PBR": info.get("priceToBook", None),
            "ROE(%)": round((info.get("returnOnEquity") or 0) * 100, 1),
            "EPS": info.get("trailingEps", None),
            "배당수익률(%)": round((info.get("dividendYield") or 0) * 100, 2),
            "MarketCap(B$)": round((info.get("marketCap") or 0) / 1e9, 1),
        })
    except Exception as e:
        print(f"{symbol} 오류: {e}")

df = pd.DataFrame(rows).set_index("Symbol")
print("=== 반도체 섹터 기본적 분석 ===")
print(df.to_string())

# 스크리닝: ROE > 20% AND PER < 35
screened = df[(df["ROE(%)"] > 20) & (df["PER"].notna()) & (df["PER"] < 35)]
print(f"\n스크리닝 결과 (ROE>20%, PER<35): {len(screened)}개 종목")
print(screened[["Name","PER","PBR","ROE(%)"]].to_string())
```

---

## 🧪 LAB 3 – 재무제표 분석 (15:00 – 17:00)

```python
# financials.py
import yfinance as yf
import pandas as pd

ticker = yf.Ticker("AAPL")

# 연간 재무제표
income = ticker.financials          # 손익계산서
balance = ticker.balance_sheet      # 대차대조표
cashflow = ticker.cashflow          # 현금흐름표

def safe_get(df, row):
    """행 이름이 있으면 첫 번째 열 값 반환"""
    if df is None or df.empty:
        return None
    for idx in df.index:
        if row.lower() in str(idx).lower():
            return df.loc[idx].iloc[0]
    return None

print("=== Apple 연간 핵심 지표 ===")
revenue = safe_get(income, "Total Revenue")
net_income = safe_get(income, "Net Income")
total_equity = safe_get(balance, "Stockholders Equity")
total_debt = safe_get(balance, "Total Debt")

if revenue:
    print(f"매출액:   ${revenue/1e9:.1f}B")
if net_income:
    print(f"순이익:   ${net_income/1e9:.1f}B")
    if revenue:
        print(f"순이익률: {net_income/revenue*100:.1f}%")
if total_equity and net_income:
    print(f"ROE:      {net_income/total_equity*100:.1f}%")
if total_debt and total_equity:
    print(f"부채비율: {total_debt/total_equity*100:.1f}%")

# EPS 추이 확인
if income is not None and not income.empty:
    print("\n=== 연도별 순이익 추이 ===")
    for col in income.columns:
        ni = income.loc[[i for i in income.index if "Net Income" in str(i)]]
        if not ni.empty:
            print(f"  {col.year}: ${ni[col].values[0]/1e9:.1f}B")
```

---

## 📝 과제 (17:00 – 18:00)

1. KOSPI 대형주 5종목을 선택하여 PER·PBR·ROE를 조회하고 비교표를 작성하세요.
2. 동일 섹터(예: 반도체, 바이오) 내에서 "저PER + 고ROE" 조건으로 스크리닝하세요.
3. 본인이 선택한 1개 종목의 최근 3년간 EPS 성장률을 계산하고, 성장세를 판단하세요.

---

## ✅ 체크리스트

- [ ] PER·PBR·ROE·EPS 개념 이해 완료
- [ ] `yfinance`로 재무 지표 자동 수집 성공
- [ ] 섹터 비교 스크리닝 코드 작성
- [ ] 재무제표(손익계산서) 분석 성공
- [ ] 과제 제출

---

## 📚 참고자료

- [Investopedia – PER](https://www.investopedia.com/terms/p/price-earningsratio.asp)
- [Investopedia – ROE](https://www.investopedia.com/terms/r/returnonequity.asp)
- [yfinance financials](https://yfinance.readthedocs.io/en/stable/reference/yfinance.scrapers.financials.html)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day128+fundamental
