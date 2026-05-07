# Day 122 – Yahoo Finance API (yfinance)

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (초급)

---

## 🎯 학습 목표

- `yfinance` 라이브러리 설치 및 기본 사용법 습득
- 주식·ETF·암호화폐 OHLCV 데이터 다운로드
- Ticker 정보(재무제표·배당 등) 조회
- 다운로드된 DataFrame 구조 이해

---

## 📖 이론 (08:00 – 10:00)

### 1. yfinance 란?
- Yahoo Finance 데이터를 Python에서 무료로 가져오는 라이브러리
- 설치: `pip install yfinance`
- 지원 데이터: OHLCV, 재무제표, 배당, 주요 지표

### 2. Ticker 심볼 규칙
| 시장 | 규칙 | 예시 |
|------|------|------|
| 미국 주식 | 심볼 그대로 | `AAPL`, `TSLA`, `MSFT` |
| 한국 주식 | 종목코드 + `.KS` | `005930.KS` (삼성전자) |
| ETF | 심볼 그대로 | `SPY`, `QQQ` |
| 암호화폐 | 심볼 + `-USD` | `BTC-USD`, `ETH-USD` |

### 3. 주요 메서드
```python
import yfinance as yf

ticker = yf.Ticker("AAPL")
ticker.history(period="1y")          # OHLCV 데이터
ticker.info                          # 기업 정보 딕셔너리
ticker.financials                    # 재무제표
ticker.dividends                     # 배당 이력
ticker.actions                       # 분할·배당 이벤트
```

---

## 🧪 LAB 1 – 주가 데이터 다운로드 (10:00 – 12:00)

```python
# yfinance_basic.py
import yfinance as yf

# 단일 종목 – Apple
aapl = yf.Ticker("AAPL")
df = aapl.history(period="6mo")      # 최근 6개월

print(df.head())
print(f"\n행 수: {len(df)}")
print(f"컬럼: {df.columns.tolist()}")
print(f"기간: {df.index[0].date()} ~ {df.index[-1].date()}")

# 한국 주식 – 삼성전자
samsung = yf.Ticker("005930.KS")
kr_df = samsung.history(period="3mo")
print(f"\n삼성전자 최근 종가: {kr_df['Close'].iloc[-1]:,.0f}원")

# 여러 종목 한 번에
tickers = yf.download(["AAPL", "MSFT", "GOOGL"], period="1y")
print(f"\n멀티 티커 shape: {tickers.shape}")
print(tickers["Close"].tail())
```

---

## 🧪 LAB 2 – 기업 정보 & 재무 데이터 조회 (13:00 – 15:00)

```python
# ticker_info.py
import yfinance as yf

ticker = yf.Ticker("AAPL")
info = ticker.info

# 주요 정보 출력
fields = [
    "shortName", "sector", "industry",
    "marketCap", "trailingPE", "priceToBook",
    "dividendYield", "fiftyTwoWeekHigh", "fiftyTwoWeekLow",
    "currentPrice"
]

print("=== Apple 기업 정보 ===")
for field in fields:
    val = info.get(field, "N/A")
    print(f"{field:25s}: {val}")

# 재무제표
print("\n=== 연간 재무제표 (매출·순이익) ===")
fin = ticker.financials
if fin is not None and not fin.empty:
    for col in fin.columns[:3]:
        print(f"\n[{col.year}년]")
        for row in ["Total Revenue", "Net Income"]:
            if row in fin.index:
                print(f"  {row}: {fin.loc[row, col]:,.0f} USD")
```

---

## 🧪 LAB 3 – 암호화폐 & ETF 데이터 비교 (15:00 – 17:00)

```python
# crypto_etf.py
import yfinance as yf
import pandas as pd

assets = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "S&P500 ETF": "SPY",
    "Nasdaq ETF": "QQQ",
}

summary = []
for name, symbol in assets.items():
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1y")
    if hist.empty:
        continue
    start_price = hist["Close"].iloc[0]
    end_price = hist["Close"].iloc[-1]
    annual_return = (end_price / start_price - 1) * 100
    volatility = hist["Close"].pct_change().std() * (252 ** 0.5) * 100
    summary.append({
        "자산": name,
        "심볼": symbol,
        "시작가": round(start_price, 2),
        "현재가": round(end_price, 2),
        "연수익률(%)": round(annual_return, 2),
        "연변동성(%)": round(volatility, 2),
    })

df = pd.DataFrame(summary)
print(df.to_string(index=False))
```

---

## 📝 과제 (17:00 – 18:00)

1. 본인이 관심 있는 주식 3종목(국내·해외 각 1종목 이상)의 1년 OHLCV 데이터를 다운로드하세요.
2. 각 종목의 연간 수익률과 변동성을 계산하여 비교표를 출력하세요.
3. `ticker.info`에서 PER(trailingPE)과 PBR(priceToBook)을 추출하여 출력하세요.

---

## ✅ 체크리스트

- [ ] `yfinance` 설치 및 기본 데이터 다운로드 성공
- [ ] 한국 주식 (`.KS`) 데이터 조회 성공
- [ ] `ticker.info`에서 재무 지표 추출 성공
- [ ] 암호화폐·ETF 비교표 출력 성공
- [ ] 과제 제출

---

## 📚 참고자료

- [yfinance 공식 GitHub](https://github.com/ranaroussi/yfinance)
- [yfinance 문서](https://yfinance.readthedocs.io)
- [Yahoo Finance 티커 검색](https://finance.yahoo.com)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day122+yfinance
