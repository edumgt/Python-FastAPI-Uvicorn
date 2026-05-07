# Day 123 – 한국 증권 API (FinanceDataReader & KIS Open API)

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (초급)

---

## 🎯 학습 목표

- `FinanceDataReader`로 국내·해외 주가 데이터 수집
- KIS(한국투자증권) Open API 기초 구조 이해
- 종목 목록(상장 주식 리스트) 조회
- API 인증(OAuth2) 흐름 파악

---

## 📖 이론 (08:00 – 10:00)

### 1. FinanceDataReader
- KRX, KOSPI, NASDAQ, S&P500 등 주가·인덱스 데이터 무료 제공
- 설치: `pip install finance-datareader`

```python
import FinanceDataReader as fdr

# 삼성전자 2023~2024
df = fdr.DataReader("005930", "2023-01-01", "2024-12-31")

# S&P 500 인덱스
sp500 = fdr.DataReader("US500", "2023")

# 상장 종목 목록
krx_list = fdr.StockListing("KRX")
```

### 2. KIS Open API 개요
- 한국투자증권에서 제공하는 REST API
- 무료 계좌 개설 후 App Key / App Secret 발급
- OAuth 2.0 Bearer 토큰 방식 인증

### 3. API 요청 흐름
```
1. App Key + App Secret → POST /oauth2/tokenP → access_token 발급
2. access_token을 Authorization 헤더에 포함
3. 원하는 API 엔드포인트 호출 (현재가, 잔고, 주문 등)
```

---

## 🧪 LAB 1 – FinanceDataReader 기초 (10:00 – 12:00)

```python
# fdr_basic.py
import FinanceDataReader as fdr
import pandas as pd

# 국내 주식
stocks = {
    "삼성전자": "005930",
    "SK하이닉스": "000660",
    "NAVER": "035420",
}

results = []
for name, code in stocks.items():
    df = fdr.DataReader(code, "2024-01-01")
    ret = (df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100
    results.append({"종목": name, "코드": code,
                    "시작": df["Close"].iloc[0],
                    "현재": df["Close"].iloc[-1],
                    "수익률(%)": round(ret, 2)})

print(pd.DataFrame(results).to_string(index=False))

# 인덱스 비교
indices = {"KOSPI": "KS11", "NASDAQ": "IXIC", "S&P500": "US500"}
for name, code in indices.items():
    idx = fdr.DataReader(code, "2024-01-01")
    print(f"{name}: {idx['Close'].iloc[-1]:,.2f}")
```

---

## 🧪 LAB 2 – 상장 종목 목록 탐색 (13:00 – 15:00)

```python
# stock_listing.py
import FinanceDataReader as fdr

# KOSPI 상장 종목
kospi = fdr.StockListing("KOSPI")
print(f"KOSPI 상장 종목 수: {len(kospi)}")
print(kospi[["Symbol", "Name", "Sector", "Industry"]].head(10))

# 시가총액 상위 10개
if "Marcap" in kospi.columns:
    top10 = kospi.nlargest(10, "Marcap")[["Name", "Symbol", "Marcap"]]
    top10["Marcap(조원)"] = (top10["Marcap"] / 1e12).round(1)
    print("\n=== 시가총액 상위 10 ===")
    print(top10[["Name", "Symbol", "Marcap(조원)"]].to_string(index=False))

# 섹터별 종목 수
if "Sector" in kospi.columns:
    sector_count = kospi["Sector"].value_counts().head(10)
    print("\n=== 섹터별 종목 수 (상위 10) ===")
    print(sector_count)
```

---

## 🧪 LAB 3 – KIS API 토큰 발급 시뮬레이션 (15:00 – 17:00)

```python
# kis_api_demo.py
# 실제 거래를 위해서는 KIS 계좌 개설 및 API 키 발급 필요
# 아래는 모의투자(paper trading) 서버를 사용하는 구조 예시

import requests
import json
import os

KIS_BASE_URL = "https://openapivts.koreainvestment.com:29443"  # 모의투자 서버

def get_access_token(app_key: str, app_secret: str) -> str:
    """OAuth2 Bearer 토큰 발급"""
    url = f"{KIS_BASE_URL}/oauth2/tokenP"
    headers = {"Content-Type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": app_key,
        "appsecret": app_secret,
    }
    # 실제 키가 없으면 요청 생략
    if app_key == "YOUR_APP_KEY":
        print("[시뮬레이션] 실제 APP KEY가 필요합니다.")
        print(f"요청 URL: {url}")
        print(f"요청 Body: {json.dumps(body, indent=2)}")
        return "SIMULATED_TOKEN"
    resp = requests.post(url, headers=headers, json=body, timeout=10)
    return resp.json()["access_token"]

def get_current_price(token: str, stock_code: str) -> dict:
    """국내 주식 현재가 조회"""
    url = f"{KIS_BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "Authorization": f"Bearer {token}",
        "tr_id": "VTTC8801R",  # 모의투자 현재가 TR
    }
    params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": stock_code}
    print(f"[시뮬레이션] GET {url}")
    print(f"  params: {params}")
    return {"stck_prpr": "75000", "stck_hgpr": "76000", "stck_lwpr": "74500"}

app_key = os.getenv("KIS_APP_KEY", "YOUR_APP_KEY")
app_secret = os.getenv("KIS_APP_SECRET", "YOUR_APP_SECRET")

token = get_access_token(app_key, app_secret)
price_info = get_current_price(token, "005930")
print(f"\n삼성전자 현재가: {price_info.get('stck_prpr', 'N/A')}원")
```

---

## 📝 과제 (17:00 – 18:00)

1. `FinanceDataReader`로 KOSDAQ 상장 종목 목록을 가져와 섹터별 분포를 출력하세요.
2. 최근 1년간 KOSPI·KOSDAQ·S&P500 지수를 비교하는 수익률 표를 작성하세요.
3. KIS Open API 공식 문서를 참고하여, 모의투자 계좌를 신청하고 API Key를 발급받은 후 `.env` 파일에 저장하는 방법을 정리하세요.

---

## ✅ 체크리스트

- [ ] `FinanceDataReader` 설치 및 국내 주가 데이터 수집 성공
- [ ] 상장 종목 목록 조회 및 섹터 분석 완료
- [ ] KIS API 요청 구조 이해 (URL, 헤더, 파라미터)
- [ ] `.env`를 활용한 API Key 관리 방법 습득
- [ ] 과제 제출

---

## 📚 참고자료

- [FinanceDataReader GitHub](https://github.com/FinanceData/FinanceDataReader)
- [KIS Open API 문서](https://apiportal.koreainvestment.com)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day123+korean+api
