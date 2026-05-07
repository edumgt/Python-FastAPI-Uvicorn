# Alpaca API 연동 – 1단계: 환경 구축 & 첫 자동매매

> **소요시간**: 8시간 | **Phase**: 7 – 자동매매 실전 (보충 자료)

---

## 🎯 학습 목표

- AWS EC2 인스턴스 생성 및 Python 환경 구성
- Alpaca Paper Trading API 키 발급 및 연동
- `trading/alpaca_client.py` 모듈 활용
- SPY 단순 매수 코드 작성 → 자동화 기반 마련

---

## 📖 이론 (08:00 – 10:00)

### 1. Alpaca 란?

| 항목 | 내용 |
|------|------|
| 서비스 | 미국 주식 알고리즘 트레이딩 플랫폼 |
| Paper Trading | 실제 돈 없이 모의투자 가능 (무료) |
| API 방식 | REST + WebSocket |
| 공식 SDK | `alpaca-py` (Python 3.10+) |
| 공식 문서 | https://docs.alpaca.markets |

### 2. EC2 인스턴스 선택 가이드

```
추천 스펙: t3.small (vCPU 2, RAM 2GB) – 월 약 $15
운영체제: Amazon Linux 2023 또는 Ubuntu 22.04 LTS
보안그룹: SSH(22번) 만 허용 (My IP 한정)
```

### 3. Paper vs Live Trading

```
Paper Trading (모의):
  URL: https://paper-api.alpaca.markets
  특징: 실제 돈 없음, 실시간 가격 반영, 무제한 테스트

Live Trading (실거래):
  URL: https://api.alpaca.markets
  특징: 실제 자금 사용, 최소 입금 없음, PDT 룰 주의
```

### 4. API 인증 흐름

```
1. https://app.alpaca.markets 회원가입
2. Paper Trading → API Keys → Generate New Key
3. API Key + Secret Key 발급 (1회만 표시, 반드시 저장)
4. .env 파일에 저장:
     ALPACA_API_KEY=PKxxx...
     ALPACA_SECRET_KEY=xxx...
5. AlpacaTrader(paper=True) 로 연결
```

---

## 🧪 LAB 1 – EC2 + Python 환경 구성 (10:00 – 12:00)

### EC2 접속 및 환경 설치

```bash
# 로컬 PC → EC2 접속
ssh -i my-key.pem ec2-user@<EC2_PUBLIC_IP>

# Python 3.11 설치 (Amazon Linux 2023)
sudo dnf install python3.11 python3.11-pip -y
python3.11 --version

# 프로젝트 디렉터리 생성
mkdir ~/autotrader && cd ~/autotrader

# 가상환경 생성 및 활성화
python3.11 -m venv venv
source venv/bin/activate

# 필수 패키지 설치
pip install alpaca-py python-dotenv yfinance pandas

# 환경변수 파일 생성 (.gitignore 에 반드시 추가)
cat > .env << 'EOF'
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
EOF
chmod 600 .env   # 소유자만 읽기 가능
```

### 패키지 임포트 확인

```python
# check_env.py
from dotenv import load_dotenv
import os

load_dotenv()

api_key    = os.getenv("ALPACA_API_KEY", "")
secret_key = os.getenv("ALPACA_SECRET_KEY", "")

if api_key and secret_key:
    print("✅ 환경변수 설정 완료")
    print(f"   API Key: {api_key[:8]}...")
else:
    print("❌ .env 파일을 확인하세요")
```

---

## 🧪 LAB 2 – 계좌 조회 & 첫 매수 (13:00 – 15:00)

```python
# first_trade.py
from dotenv import load_dotenv
load_dotenv()

from trading.alpaca_client import AlpacaTrader

# ─── 1. 클라이언트 초기화 (Paper Trading) ───
trader = AlpacaTrader(paper=True)

# ─── 2. 계좌 정보 확인 ───
account = trader.get_account()
print("=== 계좌 정보 ===")
print(f"  총 자산   : ${account.portfolio_value:,.2f}")
print(f"  현금 잔액 : ${account.cash:,.2f}")
print(f"  매수 여력 : ${account.buying_power:,.2f}")
print(f"  계좌 상태 : {account.status}")

# ─── 3. 보유 포지션 확인 ───
positions = trader.get_positions()
print(f"\n=== 보유 포지션 ({len(positions)}개) ===")
for pos in positions:
    pnl_pct = pos.unrealized_plpc * 100
    print(f"  {pos.symbol}: {pos.qty}주 @ ${pos.avg_entry_price:.2f} "
          f"| 평가손익: ${pos.unrealized_pl:,.2f} ({pnl_pct:+.2f}%)")

# ─── 4. SPY 1주 시장가 매수 ───
print("\n=== SPY 1주 시장가 매수 ===")
order = trader.market_order("SPY", qty=1, side="buy")
print(f"  주문ID: {order.order_id}")
print(f"  상태  : {order.status}")

# ─── 5. 신호 확인 ───
print("\n=== MA 크로스 신호 ===")
for sym in ["SPY", "QQQ", "AAPL"]:
    sig = trader.ma_cross_signal(sym)
    print(f"  [{sym}] 가격: ${sig['price']:,.2f} | 신호: {sig['signal']}")
```

---

## 🧪 LAB 3 – 자동화 스케줄러 설정 (15:00 – 17:00)

### APScheduler 기반 일일 신호 확인

```python
# scheduler.py
"""
매일 장 시작 30분 후(10:00 ET) 신호 확인 후 자동 주문
APScheduler 사용: pip install apscheduler
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

load_dotenv()

from trading.alpaca_client import AlpacaTrader

trader = AlpacaTrader(paper=True)

def check_and_trade() -> None:
    """장 시작 후 신호 확인 및 주문 실행"""
    watchlist = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA"]
    for symbol in watchlist:
        try:
            sig = trader.ma_cross_signal(symbol)
            rsi = trader.rsi_signal(symbol)
            print(f"[{symbol}] {sig['signal']} | RSI: {rsi['rsi']:.1f}")

            if sig["signal"] == "BUY" and rsi["rsi"] < 65:
                order = trader.market_order(symbol, qty=1, side="buy")
                print(f"  → 매수 완료: {order.order_id}")
            elif sig["signal"] == "SELL":
                pos = trader.get_position(symbol)
                if pos:
                    trader.close_position(symbol)
                    print(f"  → 청산 완료")
        except Exception as e:
            print(f"[{symbol}] 오류: {e}")

scheduler = BlockingScheduler(timezone="America/New_York")
# 미국 동부 시간 평일 10:00 (장 시작 30분 후)
scheduler.add_job(check_and_trade, "cron", day_of_week="mon-fri", hour=10, minute=0)

print("✅ 스케줄러 시작 (Ctrl+C 로 종료)")
scheduler.start()
```

### 백그라운드 실행 (nohup)

```bash
# EC2 에서 백그라운드 실행
nohup python scheduler.py > logs/trader.log 2>&1 &
echo "PID: $!"

# 실행 확인
tail -f logs/trader.log

# 프로세스 확인
ps aux | grep scheduler.py
```

---

## 📝 과제 (17:00 – 18:00)

1. `.env` 파일에 Alpaca Paper Trading API 키를 설정하고 계좌 조회를 성공시키세요.
2. `first_trade.py` 를 실행하여 SPY 1주 Paper Trading 주문을 체결시키세요.
3. RSI + MA 복합 조건으로 매수·매도 조건을 직접 수정해보세요.

---

## ✅ 체크리스트

- [ ] EC2 인스턴스 생성 및 SSH 접속 성공
- [ ] Python 가상환경 + alpaca-py 설치 완료
- [ ] Alpaca Paper Trading API 키 발급 및 `.env` 설정
- [ ] 계좌 정보 조회 성공
- [ ] SPY 시장가 매수 주문 체결 확인
- [ ] 스케줄러 백그라운드 실행 성공

---

## 📚 참고자료

- [Alpaca 공식 문서](https://docs.alpaca.markets)
- [alpaca-py GitHub](https://github.com/alpacahq/alpaca-py)
- [AWS EC2 시작 가이드](https://docs.aws.amazon.com/ec2/latest/userguide/EC2_GetStarted.html)
- [APScheduler 문서](https://apscheduler.readthedocs.io)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day137+alpaca+api
