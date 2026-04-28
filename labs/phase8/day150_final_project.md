# Day 150 – 최종 프로젝트 발표: AI 자동매매 시스템 EC2 배포

> **소요시간**: 8시간 | **Phase**: 8 – 자동매매 시스템 실전 | **Week 6 마지막**

---

## 🎯 학습 목표

- 6주 동안 구축한 AI 자동매매 시스템 전체를 EC2에 통합 배포
- Paper Trading 성과 분석 및 발표 자료 작성
- Live Trading 전환 의사 결정 기준 수립
- 향후 개선 로드맵 제시

---

## 📋 최종 프로젝트 요구사항

### 필수 구현 항목 (Pass/Fail)

| 항목 | 확인 방법 | 모듈 |
|------|-----------|------|
| ✅ Alpaca Paper Trading 연동 | 계좌 조회 + 주문 실행 확인 | `AlpacaTrader` |
| ✅ MA 크로스 또는 RSI 전략 | 신호 생성 → 주문 실행 | `AutoTrader` |
| ✅ 텔레그램 알림 | 체결·에러·일일 결산 수신 | `TelegramNotifier` |
| ✅ AI 모델 (RF 또는 XGBoost) | 학습된 모델로 신호 생성 | `MLStrategy` |
| ✅ 일일 손실 한도 | 2% 초과 시 자동 중단 | `RiskManager` |
| ✅ SQLite 매매 기록 | DB 저장 + CSV 내보내기 | `TradeLogger` |
| ✅ systemd 서비스 | 부팅 자동 시작 + 재시작 | `autotrader.service` |

### 우수 구현 항목 (가산점)

- MDD 자동 정지 구현
- 키움증권 시뮬레이션 연동
- CloudWatch 로그 모니터링 설정
- 자동 S3 백업
- 멀티 전략 포트폴리오 (MA + AI 혼합)

---

## 🧪 LAB 1 – 최종 통합 시스템 코드 (08:00 – 10:00)

```python
# ~/autotrader/main_final.py
"""
Day 150 – AI 자동매매 시스템 최종 통합

포함 기능:
  - Alpaca Paper Trading (AlpacaTrader)
  - MA 크로스 + AI 혼합 전략
  - 텔레그램 알림 (TelegramNotifier)
  - 일일 손실·MDD 리스크 관리 (RiskManager)
  - SQLite 매매 기록 (TradeLogger)
  - systemd 자동 재시작 대응 (에러 복구)
"""
import logging
import time
from datetime import date
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/trader.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ── 모듈 임포트 ───────────────────────────────────────────
from trading.alpaca_client import AlpacaTrader
from trading.telegram_notifier import TelegramNotifier
from trading.risk_manager import RiskManager
from trading.trade_logger import TradeLogger, TradeRecord, DailySnapshot, SystemEvent

WATCHLIST = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA"]
USE_AI_MODEL = True   # False → MA 전략만 사용

# ── 전역 객체 초기화 ──────────────────────────────────────
trader   = AlpacaTrader(paper=True)
notifier = TelegramNotifier()
rm       = RiskManager(
    daily_loss_limit=0.02,
    max_mdd_limit=0.10,
    max_position_pct=0.20,
    max_trades_per_day=10,
    cooldown_seconds=300,
)
db = TradeLogger("data/trading.db")

# ── AI 모델 로드 (있으면) ─────────────────────────────────
ai_models = {}
if USE_AI_MODEL:
    from trading.ml_strategy import MLStrategy
    for symbol in WATCHLIST:
        model_path = f"models/{symbol.lower()}_rf.pkl"
        if Path(model_path).exists():
            ai_models[symbol] = MLStrategy.load(model_path)
            logger.info("AI 모델 로드: %s", model_path)

def get_signal(symbol: str) -> dict:
    """MA 전략 + AI 모델 혼합 신호 생성"""
    ma_sig = trader.ma_cross_signal(symbol, fast=5, slow=20)
    signal = ma_sig["signal"]

    if symbol in ai_models and signal != "HOLD":
        import yfinance as yf
        df = yf.download(symbol, period="6mo", auto_adjust=True, progress=False)
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

        ai_signal = ai_models[symbol].predict(df)
        proba      = ai_models[symbol].predict_proba(df)

        # MA + AI 일치할 때만 신호 유지
        if signal == "BUY"  and ai_signal != "BUY":  signal = "HOLD"
        if signal == "SELL" and ai_signal != "SELL": signal = "HOLD"

        logger.info("[%s] MA: %s | AI: %s | 최종: %s | 상승확률: %.1f%%",
                    symbol, ma_sig["signal"], ai_signal, signal,
                    proba.get("상승", 0)*100)

    return {**ma_sig, "signal": signal}

def run_strategy() -> None:
    """전략 1회 실행"""
    acc = trader.get_account()
    rm.update_portfolio_value(acc.portfolio_value)
    rm.print_status()

    if not rm.can_trade():
        notifier.send(f"🚨 거래 중단: {rm.stop_reason}")
        db.log_event(SystemEvent("WARNING", f"거래 중단: {rm.stop_reason}"))
        return

    for symbol in WATCHLIST:
        if not rm.can_trade(symbol):
            continue
        try:
            sig = get_signal(symbol)
            logger.info("[%s] 신호: %s | $%.2f", symbol, sig["signal"], sig["price"])

            if sig["signal"] == "BUY":
                pos = trader.get_position(symbol)
                if pos is None:
                    size  = rm.position_size(symbol, price=sig["price"])
                    qty   = max(1, size.suggested_qty)
                    order = trader.market_order(symbol, qty=float(qty), side="buy")
                    rm.record_trade(symbol)
                    db.log_trade(TradeRecord(
                        symbol=symbol, side="BUY", qty=qty,
                        price=sig["price"], amount=qty * sig["price"],
                        broker="alpaca", order_id=order.order_id,
                        strategy="MA+AI",
                    ))
                    notifier.send_trade(symbol, "BUY", qty, sig["price"],
                                        broker="alpaca", order_id=order.order_id)

            elif sig["signal"] == "SELL":
                pos = trader.get_position(symbol)
                if pos:
                    trader.close_position(symbol)
                    rm.record_trade(symbol)
                    db.log_trade(TradeRecord(
                        symbol=symbol, side="SELL", qty=pos.qty,
                        price=sig["price"], amount=pos.qty * sig["price"],
                        broker="alpaca", order_id="CLOSE",
                        strategy="MA+AI",
                    ))
                    notifier.send_signal(symbol, "SELL", sig["price"])

        except Exception as exc:
            logger.error("[%s] 오류: %s", symbol, exc)
            db.log_event(SystemEvent("ERROR", f"{symbol} 주문 실패", str(exc)))
            notifier.send_error(f"run_strategy({symbol})", exc=exc)

def save_daily_snapshot() -> None:
    """장 마감 후 일일 스냅샷 저장 및 알림"""
    acc   = trader.get_account()
    snap  = rm.get_snapshot()
    stats = db.get_daily_stats()

    db.save_daily_snapshot(DailySnapshot(
        snapshot_date=date.today().isoformat(),
        broker="alpaca",
        portfolio_value=acc.portfolio_value,
        cash=acc.cash,
        daily_pnl=snap.daily_pnl,
        daily_pnl_pct=snap.daily_pnl_pct,
        mdd=snap.mdd,
        trade_count=stats["count"],
    ))

    positions = trader.get_positions()
    notifier.send_daily_summary(
        broker="alpaca",
        portfolio_value=acc.portfolio_value,
        daily_pnl=snap.daily_pnl,
        trade_count=stats["count"],
        positions=[{"symbol": p.symbol, "qty": p.qty, "pnl": p.unrealized_pl}
                   for p in positions],
    )

def main() -> None:
    acc = trader.get_account()
    rm.set_portfolio_value(acc.portfolio_value)
    db.log_event(SystemEvent("START", "AI 자동매매 최종 시스템 시작",
                              f"paper=True | 감시종목: {WATCHLIST}"))
    notifier.send_system_status(
        "START",
        f"AI 자동매매 시스템 가동\n"
        f"초기자산: ${acc.portfolio_value:,.0f}\n"
        f"감시 종목: {', '.join(WATCHLIST)}\n"
        f"AI 모델: {len(ai_models)}개 로드됨",
    )

    retries = 0
    while retries < 5:
        try:
            while True:
                run_strategy()
                save_daily_snapshot()
                time.sleep(3600)
        except KeyboardInterrupt:
            notifier.send_system_status("STOP", "수동 종료")
            db.log_event(SystemEvent("STOP", "수동 종료"))
            break
        except Exception as exc:
            retries += 1
            logger.error("오류 (재시도 %d/5): %s", retries, exc)
            db.log_event(SystemEvent("ERROR", "메인 루프 오류", str(exc)))
            notifier.send_error("main_loop", exc=exc)
            time.sleep(60)

if __name__ == "__main__":
    main()
```

---

## 🧪 LAB 2 – Paper Trading 성과 분석 발표 자료 (10:00 – 14:00)

```python
# performance_report.py
"""Paper Trading 기간 성과 분석 리포트"""
import pandas as pd
from trading.trade_logger import TradeLogger

db = TradeLogger("data/trading.db")
trades    = db.get_trades()
snapshots = db.get_snapshots(days=90)

if not trades:
    print("거래 내역 없음 – 최소 1주일 Paper Trading 후 실행하세요")
    exit()

df = pd.DataFrame(trades)
df["executed_at"] = pd.to_datetime(df["executed_at"])
df["pnl"] = df.apply(
    lambda r: r["amount"] if r["side"] == "SELL" else -r["amount"], axis=1
)
df = df.sort_values("executed_at")

snap_df = pd.DataFrame(snapshots) if snapshots else pd.DataFrame()

print("\n" + "="*60)
print("  📊 AI 자동매매 시스템 – Paper Trading 성과 리포트")
print("="*60)

print(f"\n【 거래 현황 】")
print(f"  분석 기간 : {df['executed_at'].min().date()} ~ {df['executed_at'].max().date()}")
print(f"  총 거래   : {len(df)}건")
print(f"  매수      : {len(df[df['side']=='BUY'])}건")
print(f"  매도      : {len(df[df['side']=='SELL'])}건")

wins  = df[df["pnl"] > 0]
loses = df[df["pnl"] < 0]
print(f"\n【 수익성 지표 】")
print(f"  총 손익   : {df['pnl'].sum():+,.0f}")
print(f"  승률      : {len(wins)/len(df)*100:.1f}%")
print(f"  평균 수익 : {wins['pnl'].mean():+,.0f}")
print(f"  평균 손실 : {loses['pnl'].mean():+,.0f}")
if loses["pnl"].mean() != 0:
    print(f"  손익비    : {abs(wins['pnl'].mean()/loses['pnl'].mean()):.2f}:1")

if not snap_df.empty:
    snap_df["snapshot_date"] = pd.to_datetime(snap_df["snapshot_date"])
    snap_df = snap_df.sort_values("snapshot_date")
    initial = snap_df["portfolio_value"].iloc[0]
    final   = snap_df["portfolio_value"].iloc[-1]
    total_return = (final / initial - 1) * 100
    max_mdd = snap_df["mdd"].max() * 100
    print(f"\n【 포트폴리오 지표 】")
    print(f"  초기 자산 : ${initial:,.0f}")
    print(f"  최종 자산 : ${final:,.0f}")
    print(f"  총 수익률 : {total_return:+.2f}%")
    print(f"  최대 MDD  : {max_mdd:.2f}%")

# 종목별 성과
print(f"\n【 종목별 성과 】")
db.print_summary(days=90)

# CSV 내보내기
csv_path = db.export_trades_csv("data/final_report.csv")
print(f"\n✅ 전체 거래 내역 CSV: {csv_path}")
print("="*60)
```

---

## 🧪 LAB 3 – Live Trading 전환 체크리스트 (14:00 – 16:00)

```python
# live_trading_checklist.py
"""
Paper Trading → Live Trading 전환 전 최종 점검
모든 항목이 ✅ 일 때만 Live 전환 권장
"""
import os
from dotenv import load_dotenv
load_dotenv()

from trading.alpaca_client import AlpacaTrader
from trading.risk_manager import RiskManager
from trading.trade_logger import TradeLogger

print("="*55)
print("  Live Trading 전환 체크리스트")
print("="*55)

checks = []

# 1. Paper Trading 성과 검증
db     = TradeLogger("data/trading.db")
snaps  = db.get_snapshots(days=30)

if len(snaps) >= 20:
    import pandas as pd
    snap_df   = pd.DataFrame(snaps)
    win_days  = (snap_df["daily_pnl"] > 0).mean()
    max_mdd   = snap_df["mdd"].max()

    checks.append(("Paper 30일 이상 운용", len(snaps) >= 20))
    checks.append((f"일 승률 55%+ ({win_days*100:.1f}%)", win_days >= 0.55))
    checks.append((f"MDD 10% 미만 ({max_mdd*100:.2f}%)", max_mdd < 0.10))
else:
    checks.append(("Paper 30일 이상 운용 (데이터 부족)", False))

# 2. 시스템 안정성
checks.append(("systemd 서비스 등록", os.path.exists("/etc/systemd/system/autotrader.service")))
checks.append(("자동 백업 스크립트 존재", os.path.exists("scripts/backup.sh")))
checks.append(("로그 파일 존재", os.path.exists("logs/trader.log")))

# 3. 환경변수 설정
api_key    = os.getenv("ALPACA_API_KEY", "")
secret_key = os.getenv("ALPACA_SECRET_KEY", "")
tg_token   = os.getenv("TELEGRAM_BOT_TOKEN", "")
checks.append(("Alpaca API Key 설정", bool(api_key and api_key != "your_api_key_here")))
checks.append(("Telegram Token 설정", bool(tg_token)))

# 4. ML 모델
checks.append(("ML 모델 파일 존재 (SPY)", os.path.exists("models/spy_rf.pkl")))

# 결과 출력
print()
all_pass = True
for label, result in checks:
    status = "✅" if result else "❌"
    print(f"  {status} {label}")
    if not result:
        all_pass = False

print()
if all_pass:
    print("  🎉 모든 항목 통과! Live Trading 전환 준비 완료")
    print()
    print("  전환 방법:")
    print("    1. AlpacaTrader(paper=False) 로 변경")
    print("    2. 초기 투자금: $500~$1,000 (소액) 권장")
    print("    3. order_qty = 1 (최소 수량) 유지")
    print("    4. daily_loss_limit = 0.01 (1% 강화) 권장")
else:
    print("  ⚠️  미통과 항목을 먼저 완료하세요!")
print("="*55)
```

---

## 📊 발표 구성 (16:00 – 18:00)

| 시간 | 내용 | 분 |
|------|------|----|
| 발표 1 | 시스템 아키텍처 설명 | 5분 |
| 발표 2 | Paper Trading 30일 성과 (승률·MDD·손익비) | 5분 |
| 발표 3 | AI 모델 특성 중요도 및 정확도 | 3분 |
| 발표 4 | systemd 자동 재시작 데모 | 2분 |
| 발표 5 | 텔레그램 알림 수신 화면 공유 | 2분 |
| 발표 6 | Live Trading 전환 계획 | 3분 |
| Q&A   | 질의응답 | 5분 |

---

## ✅ 최종 체크리스트 (Phase 8 전체)

- [ ] **1주차**: EC2 + Alpaca API + 첫 주문 성공
- [ ] **2주차**: MA 전략 자동화 + 텔레그램 알림 정상 수신
- [ ] **3주차**: ML 모델 학습 (RF or XGBoost) + EC2 배포
- [ ] **4주차**: SQLite 기록 + 일일 손실 한도 자동 정지 검증
- [ ] **5주차**: systemd 자동 재시작 + 장애 시뮬레이션 성공
- [ ] **6주차**: 성과 리포트 출력 + Live 전환 체크리스트 모두 ✅
- [ ] **Day 150**: 최종 발표 완료

---

## 🚀 Phase 8 완료 후 다음 단계

```
📌 단기 (1~3개월):
   - Paper Trading 지속 검증 → 전략 안정화
   - XGBoost 모델 추가 → RF + XGBoost 앙상블
   - 국내 주식 키움증권 연동 추가

📌 중기 (3~6개월):
   - 소액 Live Trading ($500~$1,000)
   - 샤프지수 1.0 이상 유지 전략 선별
   - FastAPI 대시보드 추가 (성과 웹 시각화)

📌 장기 (6개월+):
   - LSTM 딥러닝 전략 고도화
   - 다자산 포트폴리오 (주식 + ETF + 암호화폐)
   - 클라우드 MLOps (SageMaker, Vertex AI)
```

---

## 📚 참고자료

- [`labs/phase7/autotrading_roadmap.md`](../phase7/autotrading_roadmap.md)
- [`trading/` 패키지 전체 문서](../../trading/__init__.py)
- [Alpaca Live Trading 가이드](https://docs.alpaca.markets/docs/trading)
- [AWS Cost Explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/) – EC2 비용 모니터링
