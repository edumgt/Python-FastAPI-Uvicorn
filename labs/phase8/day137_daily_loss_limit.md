# Day 137 – 일일 손실 한도 구현 + 자동 거래 중단

> **소요시간**: 8시간 | **Phase**: 8 – 자동매매 시스템 실전 | **Week 4**

---

## 🎯 학습 목표

- `RiskManager` 의 일일 손실 한도(daily_loss_limit) 동작 원리 이해
- 손실 한도 초과 시 자동 거래 중단 메커니즘 구현
- 텔레그램 알림과 연동하여 실시간 리스크 모니터링
- 다음 날 자동 재개 로직 이해

---

## 📖 이론 (08:00 – 10:00)

### 1. 왜 일일 손실 한도가 필요한가?

```
자동매매 봇이 잘못된 신호를 연속으로 받으면:

  10:00  매수 SPY → 즉시 1% 하락
  10:05  재매수   → 추가 1% 하락
  10:10  또 매수  → 또 하락 ...

일 손실 한도 없이는 하루에 자산의 5~10%를 잃을 수 있음!

  일손실 2% 한도 → 약 $2,000 손실 시 당일 거래 중단
  → 사람이 직접 확인하고 다음 날 재개
```

### 2. 리스크 한도 설계 원칙

| 한도 유형 | 추천 설정 | 설명 |
|-----------|-----------|------|
| 일일 손실 한도 | 1~2% | 당일 자산 대비 손실률 |
| MDD 한도 | 5~10% | 전체 고점 대비 최대 낙폭 |
| 단일 종목 비중 | 10~20% | 한 종목에 몰빵 금지 |
| 일일 거래 횟수 | 5~20건 | 과도한 거래 방지 |
| 쿨다운 | 60~300초 | 같은 종목 연속 매매 방지 |

### 3. 자동 거래 중단 흐름

```
매 주문 전:
  ① rm.update_portfolio_value(현재_자산)
  ② rm.can_trade() → False 이면 주문 스킵
  ③ 텔레그램 경고 전송

자동 해제 (다음 날):
  ④ _reset_daily_if_needed() 날짜 변경 감지
  ⑤ "일일 손실" 정지 → 자동 해제
  ⑥ "MDD 초과" 정지 → 수동 해제 필요 (rm.force_resume())
```

---

## 🧪 LAB 1 – 손실 한도 시뮬레이션 (10:00 – 12:00)

```python
# lab_daily_loss_sim.py
"""일일 손실 한도 동작 시뮬레이션"""
from trading.risk_manager import RiskManager

rm = RiskManager(
    daily_loss_limit=0.02,    # 2% 손실 시 중단
    max_mdd_limit=0.10,
    max_position_pct=0.20,
    max_trades_per_day=10,
    cooldown_seconds=5,       # 테스트용 짧게 설정
)

rm.set_portfolio_value(10_000_000)  # 초기 1,000만원

print("=== 일일 손실 한도 시뮬레이션 ===\n")
print(f"  초기 자산       : {10_000_000:,}원")
print(f"  일일 손실 한도  : 2% (= {10_000_000*0.02:,.0f}원)")
print()

# 자산 변화 시뮬레이션
scenarios = [
    (10_050_000, "오전 10:00 – 소폭 상승 (+0.5%)"),
    (9_980_000,  "오전 11:00 – 소폭 하락 (-0.2%)"),
    (9_900_000,  "오후 01:00 – 추가 하락 (-1.0%)"),
    (9_800_000,  "오후 02:00 – 손실 확대 (-2.0%) ← 한도"),
    (9_750_000,  "오후 03:00 – 추가 하락 (-2.5%)"),
]

for value, desc in scenarios:
    rm.update_portfolio_value(value)
    snap    = rm.get_snapshot()
    tradable = rm.can_trade()
    status  = "✅ 거래 가능" if tradable else "🚫 거래 중단"

    print(f"  {desc}")
    print(f"    자산: {value:,}원 | 일손익: {snap.daily_pnl:+,}원 ({snap.daily_pnl_pct*100:+.2f}%) | {status}")
    if not tradable:
        print(f"    ⚠️  정지 사유: {rm.stop_reason}")
        break
    print()

print("\n─── 최종 상태 ───")
rm.print_status()
```

---

## 🧪 LAB 2 – 전략 + 리스크 관리 통합 (13:00 – 15:00)

```python
# lab_strategy_with_risk.py
"""MA 전략 + 리스크 관리 + 텔레그램 통합"""
from dotenv import load_dotenv
load_dotenv()

from trading.alpaca_client import AlpacaTrader
from trading.risk_manager import RiskManager
from trading.telegram_notifier import TelegramNotifier

trader   = AlpacaTrader(paper=True)
notifier = TelegramNotifier()
rm       = RiskManager(
    daily_loss_limit=0.02,   # 2% 일일 한도
    max_mdd_limit=0.10,      # 10% MDD 한도
    max_position_pct=0.20,
    max_trades_per_day=10,
    cooldown_seconds=60,
)

WATCHLIST = ["SPY", "QQQ", "AAPL", "MSFT"]

def initialize():
    acc = trader.get_account()
    rm.set_portfolio_value(acc.portfolio_value)
    notifier.send_system_status(
        "START",
        f"리스크 관리 자동매매 시작\n"
        f"초기자산: ${acc.portfolio_value:,.0f}\n"
        f"일손실 한도: 2% | MDD: 10%",
    )
    print(f"초기화 완료: 자산 ${acc.portfolio_value:,.0f}")

def run_protected_strategy():
    """리스크 체크 후 전략 실행"""

    # ① 현재 자산 업데이트
    acc = trader.get_account()
    rm.update_portfolio_value(acc.portfolio_value)
    rm.print_status()

    # ② 시스템 정지 여부 확인
    if not rm.can_trade():
        msg = f"🚨 거래 시스템 정지\n사유: {rm.stop_reason}"
        notifier.send(msg)
        print(f"거래 중단: {rm.stop_reason}")
        return

    # ③ 종목별 신호 확인 및 주문
    for symbol in WATCHLIST:
        if not rm.can_trade(symbol):   # 쿨다운 체크
            print(f"  [{symbol}] 쿨다운 중 – 스킵")
            continue

        try:
            sig = trader.ma_cross_signal(symbol, fast=5, slow=20)

            if sig["signal"] == "BUY":
                pos = trader.get_position(symbol)
                if pos is None:
                    # ④ 포지션 사이징
                    size  = rm.position_size(symbol, price=sig["price"])
                    qty   = max(1, size.suggested_qty)

                    order = trader.market_order(symbol, qty=float(qty), side="buy")
                    rm.record_trade(symbol)   # ⑤ 거래 카운트 증가

                    notifier.send_trade(
                        symbol, "BUY", qty, sig["price"],
                        broker="alpaca", order_id=order.order_id,
                        note=f"포지션비중: {size.allowed_pct*100:.0f}%",
                    )

            elif sig["signal"] == "SELL":
                pos = trader.get_position(symbol)
                if pos:
                    trader.close_position(symbol)
                    rm.record_trade(symbol)
                    notifier.send_signal(symbol, "SELL", sig["price"])

            print(f"  [{symbol}] {sig['signal']} | ${sig['price']:,.2f}")

        except Exception as exc:
            notifier.send_error(f"run_strategy({symbol})", exc=exc)

if __name__ == "__main__":
    initialize()
    run_protected_strategy()
```

---

## 🧪 LAB 3 – 손실 한도 초과 시나리오 테스트 (15:00 – 17:00)

```python
# lab_halt_scenario.py
"""손실 한도 초과 → 정지 → 텔레그램 알림 → 자동 재개 흐름 검증"""
from trading.risk_manager import RiskManager
from trading.telegram_notifier import TelegramNotifier

notifier = TelegramNotifier(dry_run=True)  # 콘솔 출력만
rm = RiskManager(daily_loss_limit=0.01, max_mdd_limit=0.05)
rm.set_portfolio_value(1_000_000)

print("=== 시나리오: 일일 1% 손실 한도 초과 ===\n")

def simulate_trade(asset_after: float, desc: str):
    rm.update_portfolio_value(asset_after)
    snap = rm.get_snapshot()
    can  = rm.can_trade()

    print(f"[시뮬] {desc}")
    print(f"       자산: {asset_after:,} | 일손익: {snap.daily_pnl_pct*100:+.2f}% | "
          f"MDD: {snap.mdd*100:.2f}% | 거래가능: {'✅' if can else '🚫'}")

    if not can and snap.is_halted:
        notifier.send_error("리스크 한도 초과", exc=None)
        notifier.send(f"🚨 거래 중단: {rm.stop_reason}")
        print(f"       ↳ 텔레그램 경고 전송: {rm.stop_reason}\n")
    else:
        print()

simulate_trade(1_005_000, "소폭 상승 (+0.5%)")
simulate_trade(  998_000, "소폭 하락 (-0.2%)")
simulate_trade(  990_000, "손실 확대 (-1.0%) ← 한도 초과")
simulate_trade(  985_000, "추가 하락 (봇은 이미 정지 상태)")

# 수동 재개 (관리자가 확인 후)
print("=== 관리자 수동 재개 ===")
rm.force_resume()
print(f"재개 후 거래 가능: {rm.can_trade()}\n")

# 다음 날 자동 재개 시뮬레이션
print("=== 다음 날 자동 재개 (날짜 리셋) ===")
from unittest.mock import patch
import datetime

future = datetime.date.today().replace(day=datetime.date.today().day + 1)
with patch("trading.risk_manager.date") as mock_date:
    mock_date.today.return_value = future
    rm.update_portfolio_value(985_000)
    print(f"새 거래일 후 거래 가능: {rm.can_trade()}")
```

---

## 📝 과제 (17:00 – 18:00)

1. `daily_loss_limit=0.01` (1%)로 시뮬레이션하여 몇 번째 가격 변화에서 거래가 중단되는지 확인하세요.
2. `max_trades_per_day=3` 으로 설정하여 3건 이후 거래가 중단되는지 확인하세요.
3. `lab_strategy_with_risk.py` 를 실행하여 포지션 사이징이 올바르게 적용되는지 확인하세요.

---

## ✅ 체크리스트

- [ ] `daily_loss_limit` 시뮬레이션 – 한도 초과 시 거래 중단 확인
- [ ] 텔레그램 경고 알림 연동 확인
- [ ] 포지션 사이징 (`position_size()`) 동작 확인
- [ ] 쿨다운 (`cooldown_seconds`) 동작 확인
- [ ] `force_resume()` 수동 재개 동작 확인
- [ ] 일일 한도 정지 vs MDD 정지 차이점 이해

---

## 📚 참고자료

- [`trading/risk_manager.py`](../../trading/risk_manager.py)
- [Position Sizing (Investopedia)](https://www.investopedia.com/terms/p/position-sizing.asp)
- [MDD 이해](https://www.investopedia.com/terms/m/maximum-drawdown.asp)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day137+daily+loss+limit
