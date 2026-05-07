# 키움증권 OpenAPI+ 연동

> **소요시간**: 8시간 | **Phase**: 7 – 자동매매 실전 (보충 자료)

---

## 🎯 학습 목표

- 키움증권 OpenAPI+ 아키텍처 이해
- `pykiwoom` 라이브러리 활용법 습득
- `trading/kiwoom_client.py` 모듈로 국내 주식 자동매매 구현
- 시뮬레이션 모드로 신호·주문 흐름 검증

---

## 📖 이론 (08:00 – 10:00)

### 1. 키움증권 OpenAPI+ 구조

```
사용자 PC (Windows)
  ├── 영웅문4 HTS (로그인 필수)
  ├── KOA Studio (API 테스트 도구)
  └── Python 코드
        └── pykiwoom
              └── COM 컴포넌트 (ocx)
                    └── 키움 서버 ↔ 시장 데이터 / 주문
```

| 항목 | 내용 |
|------|------|
| OS 제한 | **Windows 10/11 전용** |
| 언어 | Python (pykiwoom), C++, C# |
| 인증 | HTS 로그인 후 자동 연결 |
| 모의투자 | 별도 모의투자 계좌 신청 필요 |
| 공식 문서 | https://www.kiwoom.com/h/customer/download/VApiDocumentPage |

### 2. TR (Transaction Request) 개념

```
TR이란 서버에서 데이터를 요청하는 단위 코드입니다.

주요 TR 목록:
  opt10081  – 주식일봉차트조회
  opt10001  – 주식기본정보요청
  opw00001  – 예수금상세현황요청
  opw00018  – 계좌평가잔고내역요청
  KOA_NORMAL_BUY_KP_ORD – 주식 매수 주문
```

### 3. pykiwoom vs 직접 COM 접근

```python
# pykiwoom (권장) – pip install pykiwoom
from pykiwoom.kiwoom import Kiwoom
kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)  # 로그인 팝업

# win32com (직접)
import win32com.client
kiwoom = win32com.client.Dispatch("KHOPENAPI.KHOpenAPICtrl.1")
```

---

## 🧪 LAB 1 – 환경 설정 및 시뮬레이션 모드 (10:00 – 12:00)

```python
# kiwoom_setup_check.py
"""
macOS/Linux: simulate=True (yfinance 활용)
Windows + pykiwoom: simulate=False (실제 API)
"""
import sys
from trading.kiwoom_client import KiwoomTrader

print(f"운영체제: {sys.platform}")
print(f"pykiwoom 사용 가능: {'예' if sys.platform.startswith('win') else '아니오 (시뮬레이션 모드)'}")
print()

# 시뮬레이션 모드로 기본 동작 확인
trader = KiwoomTrader(simulate=True)
trader.login()

# 계좌 정보
acc = trader.get_account_info()
print("=== 계좌 정보 (시뮬레이션) ===")
print(f"  계좌번호 : {acc.account_no}")
print(f"  예수금   : {acc.deposit:,}원")
print(f"  총평가   : {acc.total_eval:,}원")

# 보유 종목
print("\n=== 보유 종목 ===")
for pos in acc.positions:
    print(f"  [{pos.symbol}] {pos.name}: {pos.qty}주 @ {pos.avg_price:,}원 "
          f"| 현재가: {pos.current_price:,}원 "
          f"| 손익: {pos.profit_loss:+,}원 ({pos.profit_loss_rate:+.2f}%)")
```

---

## 🧪 LAB 2 – 현재가 조회 & 신호 생성 (13:00 – 15:00)

```python
# kiwoom_signal.py
from dotenv import load_dotenv
load_dotenv()

from trading.kiwoom_client import KiwoomTrader

trader = KiwoomTrader(simulate=True)  # Windows 실거래: simulate=False
trader.login()

# 종목 목록
watchlist = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "035420": "NAVER",
    "051910": "LG화학",
    "005380": "현대차",
}

print("=== 오늘의 매매 신호 ===\n")
for code, name in watchlist.items():
    price = trader.get_current_price(code)
    sig   = trader.ma_cross_signal(code, fast=5, slow=20)

    emoji = {"BUY": "📈", "SELL": "📉", "HOLD": "⏸️"}.get(sig["signal"], "?")
    print(f"{emoji} [{code}] {name:<10} "
          f"현재가: {price:>8,}원 | "
          f"MA5: {sig.get('MA5', 0):>8,.0f} | "
          f"MA20: {sig.get('MA20', 0):>8,.0f} | "
          f"신호: {sig['signal']}")

# 매수 신호 종목만 주문 (시뮬레이션)
print("\n=== 매수 신호 종목 주문 ===")
for code, name in watchlist.items():
    sig = trader.ma_cross_signal(code)
    if sig["signal"] == "BUY":
        order = trader.market_buy(code, qty=1)
        print(f"  [{code}] {name}: 매수 주문 → {order.status}")
```

---

## 🧪 LAB 3 – 실거래 환경 구성 (Windows) (15:00 – 17:00)

### 실거래 환경 설정 순서 (Windows 전용)

```
1. 키움증권 홈페이지에서 증권 계좌 개설
2. 영웅문4 HTS 설치 및 로그인
3. OpenAPI+ 신청: 영웅문 → 계좌관리 → OpenAPI 서비스 신청
4. KOA Studio 설치 (테스트 도구)
5. pip install pykiwoom
6. .env 에 계좌번호 설정
```

```python
# kiwoom_live.py (Windows 전용)
"""
Windows 환경에서 실제 키움 API 사용 예시
⚠️  반드시 모의투자 계좌로 먼저 테스트하세요!
"""
import os
from dotenv import load_dotenv

load_dotenv()

# simulate=False → 실제 pykiwoom COM 연결
from trading.kiwoom_client import KiwoomTrader

trader = KiwoomTrader(
    account_no=os.getenv("KIWOOM_ACCOUNT_NO"),
    simulate=False,   # Windows 실거래 모드
)

# 로그인 (영웅문4 실행 상태여야 함)
success = trader.login()
if not success:
    print("로그인 실패 – 영웅문4를 먼저 실행하세요")
    exit(1)

# 삼성전자 현재가 조회
price = trader.get_current_price("005930")
print(f"삼성전자 현재가: {price:,}원")

# 지정가 매수 (삼성전자 1주)
order = trader.limit_buy("005930", qty=1, price=price - 100)
print(f"주문번호: {order.order_no} | 상태: {order.status}")
```

### 모의투자 서버 접속

```python
# 키움증권은 별도 모의투자 계좌가 필요합니다
# 영웅문4 → F8 (모의투자 서버 접속)
# 계좌번호 앞자리로 실거래/모의투자 구분:
#   8로 시작: 실거래
#   그 외:    모의투자 (서버 설정에 따라 다름)
```

---

## 📝 과제 (17:00 – 18:00)

1. 시뮬레이션 모드로 `kiwoom_signal.py` 를 실행하여 5개 종목 신호를 출력하세요.
2. OHLCV 데이터를 수집하여 RSI 지표를 추가로 계산하고 복합 신호를 만들어보세요.
3. (Windows 사용자) 실제 모의투자 계좌로 지정가 주문을 1건 체결해보세요.

---

## ✅ 체크리스트

- [ ] `KiwoomTrader(simulate=True)` 시뮬레이션 모드 동작 확인
- [ ] 현재가 조회 및 MA 크로스 신호 생성 성공
- [ ] 5개 종목 일괄 신호 확인 완료
- [ ] (Windows) pykiwoom 설치 및 로그인 성공
- [ ] 과제 제출

---

## 📚 참고자료

- [키움 OpenAPI+ 공식 가이드](https://www.kiwoom.com/h/customer/download/VApiDocumentPage)
- [pykiwoom GitHub](https://github.com/sharebook-kr/pykiwoom)
- [KOA Studio 다운로드](https://www.kiwoom.com)
- [키움 모의투자 신청](https://www.kiwoom.com/h/customer/service/VPaperTradingPage)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day137+kiwoom+api
