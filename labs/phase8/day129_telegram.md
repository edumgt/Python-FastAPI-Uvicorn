# Day 129 – 텔레그램 봇 알림 연동

> **소요시간**: 8시간 | **Phase**: 8 – 자동매매 시스템 실전 | **Week 2**

---

## 🎯 학습 목표

- 텔레그램 봇 생성 및 토큰·Chat ID 발급
- `TelegramNotifier` 모듈로 체결·신호·에러·일일 결산 알림 전송
- 매매 전략과 텔레그램 알림을 통합한 완전한 자동매매 루프 구현

---

## 📖 이론 (08:00 – 10:00)

### 1. 텔레그램 봇 알림이 필요한 이유

```
자동매매 봇은 24시간 EC2 에서 실행됩니다.
사람이 화면을 보지 않아도 스마트폰으로 즉시 확인이 필요한 이벤트:

  📈 매수 체결     → 언제, 몇 주, 얼마에 샀는지
  📉 매도 체결     → 수익/손실 확인
  🚨 에러 발생     → API 장애, 네트워크 오류
  ⚠️  리스크 경고  → 손실 한도 접근, MDD 초과 직전
  📊 일일 결산     → 하루 성과 요약 (장 마감 후)
```

### 2. 봇 생성 절차

```
1. 텔레그램 → @BotFather 검색 → 채팅 시작
2. /newbot 입력
3. 봇 이름 입력: autotrader_alert_bot
4. 사용자명 입력: myautotrader_bot  (전 세계 유일해야 함)
5. Token 발급: 1234567890:ABCdefGhIJKlmNOPqrsTUVwxyz
6. .env 에 저장:
     TELEGRAM_BOT_TOKEN=1234567890:ABCdefGhIJKlmNOPqrsTUVwxyz

7. Chat ID 확인:
     방법 A: @userinfobot 에 /start 전송 → id 확인
     방법 B: 브라우저에서
       https://api.telegram.org/bot{TOKEN}/getUpdates
       → result[0].message.chat.id

8. .env 에 추가:
     TELEGRAM_CHAT_ID=987654321
```

### 3. TelegramNotifier 메서드 목록

| 메서드 | 용도 |
|--------|------|
| `send(message)` | 임의 텍스트 전송 |
| `send_trade(...)` | 체결 알림 (종목·수량·가격·주문ID) |
| `send_signal(...)` | 신호 알림 (BUY/SELL/HOLD + 지표값) |
| `send_daily_summary(...)` | 일일 결산 (자산·손익·거래수·포지션) |
| `send_error(...)` | 에러 알림 (위치 + 예외 타입·메시지) |
| `send_system_status(...)` | 시스템 상태 (START/STOP/RESTART) |

---

## 🧪 LAB 1 – 봇 기본 동작 확인 (10:00 – 12:00)

```python
# test_telegram.py
from dotenv import load_dotenv
load_dotenv()

from trading.telegram_notifier import TelegramNotifier

# ── 기본 연결 테스트 ──────────────────────────────────────
notifier = TelegramNotifier()   # .env 에서 자동 로드

# 기본 메시지
notifier.send("🤖 자동매매 봇 텔레그램 연결 성공!")

# 시스템 상태 알림
notifier.send_system_status("START", "EC2 자동매매 봇 시작\nPaper Trading 모드")

# 신호 알림
notifier.send_signal(
    symbol="SPY",
    signal="BUY",
    price=450.23,
    indicators={"MA5": 449.5, "MA20": 445.0, "RSI": 42.1},
)

# 체결 알림
notifier.send_trade(
    symbol="SPY", side="BUY",
    qty=1, price=450.23,
    broker="alpaca", order_id="abc-123-456",
    note="MA 크로스 + RSI 42 – 매수 조건 충족",
)

# 에러 알림 테스트
try:
    raise ConnectionError("Alpaca API 응답 없음 (Timeout)")
except Exception as exc:
    notifier.send_error("market_order('SPY')", exc=exc)

print("✅ 텔레그램 테스트 완료 – 스마트폰을 확인하세요!")
```

---

## 🧪 LAB 2 – 전략 + 텔레그램 통합 (13:00 – 15:00)

```python
# strategy_with_telegram.py
"""MA 크로스 전략 + 텔레그램 알림 통합"""
from dotenv import load_dotenv
load_dotenv()

from trading.alpaca_client import AlpacaTrader
from trading.telegram_notifier import TelegramNotifier

trader   = AlpacaTrader(paper=True)
notifier = TelegramNotifier()

WATCHLIST = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA"]

def run_strategy() -> None:
    acc = trader.get_account()
    buy_count = 0
    sell_count = 0

    for symbol in WATCHLIST:
        try:
            ma  = trader.ma_cross_signal(symbol, fast=5, slow=20)
            rsi = trader.rsi_signal(symbol)

            # BUY: MA 골든크로스 + RSI < 70 (과매수 아님)
            if ma["signal"] == "BUY" and rsi["rsi"] < 70:
                pos = trader.get_position(symbol)
                if pos is None:
                    order = trader.market_order(symbol, qty=1, side="buy")
                    notifier.send_trade(
                        symbol=symbol, side="BUY",
                        qty=1, price=ma["price"],
                        broker="alpaca", order_id=order.order_id,
                        note=f"MA크로스+RSI({rsi['rsi']:.1f})",
                    )
                    buy_count += 1

            # SELL: MA 데드크로스
            elif ma["signal"] == "SELL":
                pos = trader.get_position(symbol)
                if pos:
                    trader.close_position(symbol)
                    notifier.send_signal(
                        symbol=symbol, signal="SELL",
                        price=ma["price"],
                        indicators={
                            f"MA5": ma["MA5"],
                            f"MA20": ma["MA20"],
                            "수익률": f"{pos.unrealized_plpc*100:+.2f}%",
                        },
                    )
                    sell_count += 1

        except Exception as exc:
            notifier.send_error(f"run_strategy({symbol})", exc=exc)

    print(f"전략 완료: 매수 {buy_count}건, 매도 {sell_count}건")

def send_daily_summary() -> None:
    """장 마감 후 일일 결산 전송"""
    acc       = trader.get_account()
    positions = trader.get_positions()

    notifier.send_daily_summary(
        broker="alpaca",
        portfolio_value=acc.portfolio_value,
        daily_pnl=acc.portfolio_value - 100_000,  # 초기 자산 100K 기준
        trade_count=len(positions),
        positions=[
            {"symbol": p.symbol, "qty": p.qty, "pnl": p.unrealized_pl}
            for p in positions
        ],
    )

if __name__ == "__main__":
    notifier.send_system_status("START", f"전략 실행 시작\n감시 종목: {', '.join(WATCHLIST)}")
    run_strategy()
    send_daily_summary()
```

---

## 🧪 LAB 3 – 스케줄러 + 텔레그램 자동화 (15:00 – 17:00)

```python
# scheduler_with_telegram.py
"""
APScheduler + 텔레그램 알림 통합 스케줄러
  - 10:00 ET: 신호 확인 및 매매
  - 16:00 ET: 일일 결산 전송
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
load_dotenv()

from strategy_with_telegram import run_strategy, send_daily_summary, notifier

scheduler = BlockingScheduler(timezone="America/New_York")

# 장 시작 30분 후 매매
scheduler.add_job(
    run_strategy, "cron",
    day_of_week="mon-fri", hour=10, minute=0,
    id="morning_strategy",
)

# 장 마감 직후 결산
scheduler.add_job(
    send_daily_summary, "cron",
    day_of_week="mon-fri", hour=16, minute=5,
    id="daily_summary",
)

try:
    notifier.send_system_status("START", "스케줄러 시작\n10:00 매매 | 16:05 결산")
    print("✅ 스케줄러 실행 중 (Ctrl+C 로 종료)")
    scheduler.start()
except KeyboardInterrupt:
    notifier.send_system_status("STOP", "스케줄러 수동 종료")
    print("종료됨")
```

```bash
# EC2 에서 백그라운드 실행
mkdir -p logs
nohup python scheduler_with_telegram.py > logs/scheduler.log 2>&1 &
echo "PID: $!"
tail -f logs/scheduler.log
```

---

## 📝 과제 (17:00 – 18:00)

1. 텔레그램 봇을 생성하고 `test_telegram.py` 를 실행하여 스마트폰에서 5가지 메시지를 모두 수신하세요.
2. `strategy_with_telegram.py` 를 실행하여 SPY 외 2종목 이상의 신호와 체결 알림을 확인하세요.
3. 에러 상황(API 키 미설정 등)을 의도적으로 발생시켜 에러 알림이 전송되는지 확인하세요.

---

## ✅ 체크리스트

- [ ] 텔레그램 봇 생성 및 Token 발급 완료
- [ ] Chat ID 확인 및 `.env` 설정 완료
- [ ] `send_system_status`, `send_signal`, `send_trade`, `send_error`, `send_daily_summary` 모두 수신 확인
- [ ] 전략 실행 + 텔레그램 알림 통합 동작 확인
- [ ] EC2 에서 `nohup` 백그라운드 실행 성공

---

## 📚 참고자료

- [python-telegram-bot 공식 문서](https://docs.python-telegram-bot.org)
- [BotFather 가이드](https://core.telegram.org/bots/features#botfather)
- [APScheduler 문서](https://apscheduler.readthedocs.io)
