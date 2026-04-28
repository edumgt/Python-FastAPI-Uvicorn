# 🤖 자동매매 시스템 구축 – 6주 실전 로드맵

> **대상**: FastAPI / Python 기초 완료자 + 금융 데이터 기초 학습자  
> **목표**: EC2 서버에서 24시간 운용 가능한 AI 자동매매 시스템 완성  
> **브로커**: Alpaca (미국 주식 / 모의투자 → 실거래) + 키움증권 (국내 주식)

---

## 📋 전체 로드맵

```
1주차  환경 구축       EC2 + Alpaca API + 첫 매매
2주차  전략 통합       데이터 수집 + 이동평균 전략 + 텔레그램 알림
3주차  AI 모델 통합    RandomForest/XGBoost 학습 + 서버 배포
4주차  리스크 & 로그   DB 매매 기록 + 손실 한도 + 시스템 정지
5주차  안정성 강화     systemd + CloudWatch + 자동 백업
6주차  실전 운용       Paper Testing → 소액 실전 → 점진적 증액
```

---

## 📁 프로젝트 디렉터리 구조

```
autotrader/
├── trading/                    # 핵심 모듈 패키지
│   ├── __init__.py
│   ├── alpaca_client.py        # Alpaca REST API
│   ├── kiwoom_client.py        # 키움증권 OpenAPI+
│   ├── auto_trader.py          # 신호·주문 오케스트레이터
│   ├── telegram_notifier.py    # 텔레그램 알림
│   ├── ml_strategy.py          # RandomForest/XGBoost 전략
│   ├── risk_manager.py         # 리스크 관리 (MDD·손실 한도)
│   └── trade_logger.py         # SQLite 매매 기록
├── models/                     # 학습된 ML 모델 (.pkl)
├── data/                       # trading.db (SQLite)
├── logs/                       # 로그 파일
├── scripts/
│   └── autotrader.service      # systemd 서비스 파일
├── main.py                     # 메인 실행 진입점
├── requirements.txt
└── .env                        # API 키 (gitignore 필수)
```

---

## 🟢 1단계 (1주차) – 환경 구축

> **목표**: EC2에서 Alpaca Paper Trading 으로 SPY 첫 매매 성공

### 환경 설치

```bash
# EC2 (Amazon Linux 2023)
sudo dnf install python3.11 python3.11-pip git -y
git clone https://github.com/edumgt/Python-FastAPI-Uvicorn.git
cd Python-FastAPI-Uvicorn

python3.11 -m venv venv && source venv/bin/activate
pip install alpaca-py yfinance pandas python-dotenv apscheduler
```

### `.env` 설정

```env
# .env  (chmod 600 .env)
ALPACA_API_KEY=PKxxxxxxxxxxxxxxxxxxxxxxxx
ALPACA_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TELEGRAM_BOT_TOKEN=         # 2주차 이후 추가
TELEGRAM_CHAT_ID=           # 2주차 이후 추가
KIWOOM_ACCOUNT_NO=          # 국내 주식 사용 시
```

### 가장 단순한 매매 코드 (SPY 매수만)

```python
# main_week1.py
"""1단계: 단순 SPY 매수 전략"""
from dotenv import load_dotenv
load_dotenv()

from trading.alpaca_client import AlpacaTrader

trader  = AlpacaTrader(paper=True)
account = trader.get_account()
print(f"잔액: ${account.cash:,.2f}")

# SPY 포지션 없으면 1주 매수
position = trader.get_position("SPY")
if position is None:
    order = trader.market_order("SPY", qty=1, side="buy")
    print(f"SPY 매수 완료: {order.order_id}")
else:
    print(f"SPY 보유 중: {position.qty}주 (손익: ${position.unrealized_pl:+,.2f})")
```

### 참고 Lab 파일

- `labs/phase7/day137_alpaca_api.md`
- `labs/phase7/day137_kiwoom_api.md`

---

## 🟡 2단계 (2주차) – 데이터 + 전략 + 텔레그램

> **목표**: 이동평균 전략으로 자동 신호 생성 + 텔레그램 알림 수신

### 텔레그램 봇 설정

```
1. 텔레그램 → @BotFather → /newbot → Token 발급
2. @userinfobot → Chat ID 확인
3. .env 에 TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID 추가
```

### 통합 전략 실행 코드

```python
# main_week2.py
"""2단계: MA 전략 + 텔레그램 알림"""
from dotenv import load_dotenv
load_dotenv()

from trading.alpaca_client import AlpacaTrader
from trading.telegram_notifier import TelegramNotifier

trader   = AlpacaTrader(paper=True)
notifier = TelegramNotifier()            # .env 에서 토큰 로드

# 감시 목록
WATCHLIST = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA"]

def run_strategy():
    for symbol in WATCHLIST:
        try:
            ma_sig  = trader.ma_cross_signal(symbol, fast=5, slow=20)
            rsi_sig = trader.rsi_signal(symbol, period=14)

            # 복합 조건: MA 크로스 AND RSI < 70 (과매수 아님)
            if ma_sig["signal"] == "BUY" and rsi_sig["rsi"] < 70:
                pos = trader.get_position(symbol)
                if pos is None:                       # 미보유 시만 매수
                    order = trader.market_order(symbol, qty=1, side="buy")
                    notifier.send_trade(
                        symbol=symbol, side="BUY",
                        qty=1, price=ma_sig["price"],
                        broker="alpaca", order_id=order.order_id,
                    )

            elif ma_sig["signal"] == "SELL":
                pos = trader.get_position(symbol)
                if pos:                               # 보유 시 전량 청산
                    trader.close_position(symbol)
                    notifier.send_signal(symbol, "SELL", ma_sig["price"])

        except Exception as exc:
            notifier.send_error(f"run_strategy({symbol})", exc=exc)

if __name__ == "__main__":
    notifier.send_system_status("START", "2단계 자동매매 시작")
    run_strategy()
```

### 스케줄러 설정

```python
# scheduler_week2.py
from apscheduler.schedulers.blocking import BlockingScheduler
from main_week2 import run_strategy, notifier
from trading.alpaca_client import AlpacaTrader

trader = AlpacaTrader(paper=True)

def daily_summary():
    acc = trader.get_account()
    positions = trader.get_positions()
    notifier.send_daily_summary(
        broker="alpaca",
        portfolio_value=acc.portfolio_value,
        daily_pnl=acc.portfolio_value - 100_000,  # 초기 자산 기준
        trade_count=len(positions),
        positions=[{"symbol": p.symbol, "qty": p.qty, "pnl": p.unrealized_pl}
                   for p in positions],
    )

scheduler = BlockingScheduler(timezone="America/New_York")
scheduler.add_job(run_strategy,   "cron", day_of_week="mon-fri", hour=10, minute=0)
scheduler.add_job(daily_summary,  "cron", day_of_week="mon-fri", hour=16, minute=0)
scheduler.start()
```

---

## 🔵 3단계 (3주차) – AI 모델 통합

> **목표**: RandomForest/XGBoost 로 방향성 예측 → 서버에 모델 배포

### 로컬에서 모델 학습 (main_week3_train.py)

```python
# main_week3_train.py  – 로컬 PC 에서 실행
"""3단계: ML 모델 학습 및 저장"""
import yfinance as yf
from trading.ml_strategy import MLStrategy

SYMBOLS = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA"]

for symbol in SYMBOLS:
    print(f"\n[{symbol}] 모델 학습 중...")
    df = yf.download(symbol, period="5y", auto_adjust=True, progress=False)
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()

    for model_type in ["rf", "xgb"]:
        strategy = MLStrategy(model_type=model_type, forward_days=5)
        result   = strategy.train(df)
        path     = strategy.save(f"{symbol.lower()}_{model_type}.pkl")
        print(f"  [{model_type}] 정확도: {result.accuracy:.4f} | 저장: {path}")

print("\n✅ 모든 모델 학습 완료. models/ 폴더를 EC2 에 업로드하세요.")
```

### EC2 에 모델 업로드

```bash
# 로컬 → EC2 모델 파일 전송
scp -i my-key.pem models/*.pkl ec2-user@<EC2_IP>:~/autotrader/models/
```

### AI 신호 기반 매매 (main_week3.py)

```python
# main_week3.py  – EC2 에서 실행
"""3단계: ML 모델 기반 자동매매"""
from dotenv import load_dotenv
load_dotenv()

import yfinance as yf
from trading.ml_strategy import MLStrategy, MLSignalAdapter
from trading.alpaca_client import AlpacaTrader
from trading.telegram_notifier import TelegramNotifier

trader   = AlpacaTrader(paper=True)
notifier = TelegramNotifier()

def get_data(symbol: str):
    df = yf.download(symbol, period="6mo", auto_adjust=True, progress=False)
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    return df[["Open", "High", "Low", "Close", "Volume"]].dropna()

WATCHLIST = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA"]

def run_ml_strategy():
    for symbol in WATCHLIST:
        try:
            strategy = MLStrategy.load(f"models/{symbol.lower()}_rf.pkl")
            adapter  = MLSignalAdapter(strategy, get_data)
            result   = adapter.get_signal(symbol)

            print(f"[{symbol}] {result['signal']} | "
                  f"상승: {result['prob_up']*100:.1f}% | "
                  f"하락: {result['prob_down']*100:.1f}%")

            # 상승 확률 60% 이상 시 매수
            if result["signal"] == "BUY" and result["prob_up"] >= 0.60:
                pos = trader.get_position(symbol)
                if pos is None:
                    order = trader.market_order(symbol, qty=1, side="buy")
                    notifier.send_trade(symbol, "BUY", 1, result["price"],
                                        broker="alpaca", order_id=order.order_id,
                                        note=f"RF 상승확률 {result['prob_up']*100:.1f}%")

            elif result["signal"] == "SELL" and result["prob_down"] >= 0.60:
                pos = trader.get_position(symbol)
                if pos:
                    trader.close_position(symbol)
                    notifier.send_signal(symbol, "SELL", result["price"],
                                         {"하락확률": f"{result['prob_down']*100:.1f}%"})
        except Exception as exc:
            notifier.send_error(f"ML {symbol}", exc=exc)

if __name__ == "__main__":
    run_ml_strategy()
```

---

## 🟠 4단계 (4주차) – 리스크 관리 + 매매 기록

> **목표**: DB 매매 일지 + 일일 손실 한도 + MDD 자동 정지

### 통합 실행 코드 (main_week4.py)

```python
# main_week4.py
"""4단계: 리스크 관리 + SQLite 매매 기록"""
from dotenv import load_dotenv
load_dotenv()

import yfinance as yf
from trading.alpaca_client import AlpacaTrader
from trading.telegram_notifier import TelegramNotifier
from trading.risk_manager import RiskManager
from trading.trade_logger import TradeLogger, TradeRecord, DailySnapshot, SystemEvent
from datetime import date

trader   = AlpacaTrader(paper=True)
notifier = TelegramNotifier()
rm       = RiskManager(
    daily_loss_limit=0.02,    # 2% 일일 손실 한도
    max_mdd_limit=0.10,       # 10% MDD 한도
    max_position_pct=0.20,    # 단일 종목 20%
    max_trades_per_day=10,
)
db       = TradeLogger("data/trading.db")

WATCHLIST = ["SPY", "QQQ", "AAPL"]

def initialize():
    """봇 시작 시 초기화"""
    acc = trader.get_account()
    rm.set_portfolio_value(acc.portfolio_value)
    db.log_event(SystemEvent("START", "4단계 자동매매 시작",
                              f"초기자산={acc.portfolio_value:,.0f}"))
    notifier.send_system_status("START",
        f"초기자산: ${acc.portfolio_value:,.0f}\n일일 손실한도: 2% | MDD: 10%")

def run_strategy():
    # 현재 자산 업데이트 및 리스크 체크
    acc = trader.get_account()
    rm.update_portfolio_value(acc.portfolio_value)
    rm.print_status()

    if not rm.can_trade():
        notifier.send_error("리스크 한도 초과", exc=None)
        notifier.send(f"🚨 거래 중단: {rm.stop_reason}")
        return

    for symbol in WATCHLIST:
        if not rm.can_trade(symbol):
            continue
        try:
            from trading.alpaca_client import AlpacaTrader
            ma_sig = trader.ma_cross_signal(symbol)

            if ma_sig["signal"] == "BUY":
                pos = trader.get_position(symbol)
                if pos is None:
                    # 포지션 사이징
                    size  = rm.position_size(symbol, ma_sig["price"])
                    qty   = max(1, size.suggested_qty)
                    order = trader.market_order(symbol, qty=float(qty), side="buy")

                    # DB 저장
                    db.log_trade(TradeRecord(
                        symbol=symbol, side="BUY", qty=qty,
                        price=ma_sig["price"], amount=qty * ma_sig["price"],
                        broker="alpaca", order_id=order.order_id,
                        strategy="MA_CROSS",
                    ))
                    rm.record_trade(symbol)
                    notifier.send_trade(symbol, "BUY", qty, ma_sig["price"],
                                        broker="alpaca", order_id=order.order_id)

            elif ma_sig["signal"] == "SELL":
                pos = trader.get_position(symbol)
                if pos:
                    trader.close_position(symbol)
                    db.log_trade(TradeRecord(
                        symbol=symbol, side="SELL", qty=pos.qty,
                        price=ma_sig["price"], amount=pos.qty * ma_sig["price"],
                        broker="alpaca", order_id="CLOSE",
                        strategy="MA_CROSS",
                    ))
                    rm.record_trade(symbol)
                    notifier.send_signal(symbol, "SELL", ma_sig["price"])

        except Exception as exc:
            db.log_event(SystemEvent("ERROR", f"{symbol} 주문 실패", str(exc)))
            notifier.send_error(f"주문({symbol})", exc=exc)

def save_daily_snapshot():
    """장 마감 후 일일 스냅샷 저장"""
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

if __name__ == "__main__":
    initialize()
    run_strategy()
```

---

## 🔴 5단계 (5주차) – 안정성 강화

> **목표**: systemd 서비스로 자동 재시작 + CloudWatch 모니터링 + 일일 백업

### systemd 서비스 등록

```ini
# /etc/systemd/system/autotrader.service
[Unit]
Description=자동매매 봇 서비스
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/autotrader
Environment=PATH=/home/ec2-user/autotrader/venv/bin
ExecStart=/home/ec2-user/autotrader/venv/bin/python main_week4.py
Restart=on-failure
RestartSec=30
StandardOutput=append:/home/ec2-user/autotrader/logs/trader.log
StandardError=append:/home/ec2-user/autotrader/logs/error.log

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 등록 및 시작
sudo systemctl daemon-reload
sudo systemctl enable autotrader.service
sudo systemctl start autotrader.service

# 상태 확인
sudo systemctl status autotrader.service
journalctl -u autotrader.service -f    # 실시간 로그
```

### 자동 재시작 + 에러 복구 전략

```python
# main.py  – 메인 진입점 (5단계)
"""
Restart 조건:
  - API 연결 실패 → 60초 후 재시도
  - 예외 발생    → 로그 기록 + 텔레그램 알림 + 30초 후 재시도
  - MDD 초과     → 텔레그램 경고 + 시스템 정지 (수동 재개 필요)
"""
import time
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    filename="logs/trader.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

from trading.telegram_notifier import TelegramNotifier

notifier = TelegramNotifier()

MAX_RETRIES    = 5
RETRY_INTERVAL = 60   # 초

def main_loop():
    retries = 0
    while retries < MAX_RETRIES:
        try:
            from main_week4 import initialize, run_strategy
            initialize()
            while True:
                run_strategy()
                time.sleep(3600)   # 1시간 대기
        except KeyboardInterrupt:
            notifier.send_system_status("STOP", "수동 종료")
            break
        except Exception as exc:
            retries += 1
            logging.error("오류 발생 (시도 %d/%d): %s", retries, MAX_RETRIES, exc)
            notifier.send_error("main_loop", exc=exc)
            if retries < MAX_RETRIES:
                time.sleep(RETRY_INTERVAL)

    notifier.send_system_status("STOP", f"최대 재시도 횟수({MAX_RETRIES}) 초과")

if __name__ == "__main__":
    main_loop()
```

### CloudWatch 로그 설정

```bash
# CloudWatch Agent 설치 (Amazon Linux 2023)
sudo dnf install amazon-cloudwatch-agent -y

# 설정 파일 생성
cat > /opt/aws/amazon-cloudwatch-agent/etc/cloudwatch-config.json << 'EOF'
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/home/ec2-user/autotrader/logs/trader.log",
            "log_group_name": "/autotrader/logs",
            "log_stream_name": "trader-{instance_id}"
          },
          {
            "file_path": "/home/ec2-user/autotrader/logs/error.log",
            "log_group_name": "/autotrader/errors",
            "log_stream_name": "errors-{instance_id}"
          }
        ]
      }
    }
  }
}
EOF

sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config -m ec2 \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/cloudwatch-config.json -s
```

### DB 자동 백업 (cron)

```bash
# crontab -e
# 매일 오전 1시 DB 및 모델 백업
0 1 * * * /home/ec2-user/autotrader/scripts/backup.sh

# backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/home/ec2-user/backups/$DATE"
mkdir -p "$BACKUP_DIR"

cp data/trading.db "$BACKUP_DIR/"
cp models/*.pkl "$BACKUP_DIR/" 2>/dev/null || true
cp .env "$BACKUP_DIR/.env.bak"

# S3 업로드 (선택)
# aws s3 sync "$BACKUP_DIR" "s3://my-autotrader-backup/$DATE/"
echo "[$DATE] 백업 완료: $BACKUP_DIR"
```

---

## ⚫ 6단계 (6주차~) – 실전 운용

> **목표**: Paper Trading 검증 → 소액 실전 → 점진적 증액

### Paper Trading 검증 체크리스트 (1~3개월)

```
✅ 일일 승률 > 55% 유지 (30일 이상)
✅ MDD < 10% 유지
✅ 샤프지수 > 1.0
✅ 텔레그램 알림 정상 동작 (매일 확인)
✅ systemd 자동 재시작 동작 확인 (인위적 중단 테스트)
✅ 에러 발생 시 로그 기록 및 알림 정상 동작
✅ DB 백업 정상 동작 (매일 확인)
```

### Paper Trading 성과 분석

```python
# analyze_performance.py
from trading.trade_logger import TradeLogger
import pandas as pd

db = TradeLogger("data/trading.db")

# 전체 거래 내역 로드
trades = db.get_trades()
df = pd.DataFrame(trades)

if df.empty:
    print("거래 내역 없음")
else:
    df["pnl"] = df.apply(
        lambda r: r["amount"] if r["side"] == "SELL" else -r["amount"], axis=1
    )
    df["executed_at"] = pd.to_datetime(df["executed_at"])
    df = df.sort_values("executed_at")

    total_pnl   = df["pnl"].sum()
    win_rate    = (df["pnl"] > 0).mean() * 100
    avg_win     = df[df["pnl"] > 0]["pnl"].mean()
    avg_loss    = df[df["pnl"] < 0]["pnl"].mean()

    print("=== Paper Trading 성과 분석 ===")
    print(f"  총 거래 건수  : {len(df)}건")
    print(f"  총 손익       : {total_pnl:+,.2f}")
    print(f"  승률          : {win_rate:.1f}%")
    print(f"  평균 수익     : {avg_win:+,.2f}")
    print(f"  평균 손실     : {avg_loss:+,.2f}")
    print(f"  손익비        : {abs(avg_win/avg_loss):.2f}:1")

    # 월별 성과
    df["month"] = df["executed_at"].dt.to_period("M")
    monthly = df.groupby("month")["pnl"].agg(["sum", "count"])
    monthly.columns = ["손익", "거래수"]
    print("\n=== 월별 성과 ===")
    print(monthly.to_string())
```

### 실전 전환 가이드

```python
# live_config.py
"""
Paper → Live 전환 시 변경 사항

1. AlpacaTrader(paper=False)   ← 핵심!
2. 최소 자금 입금: Alpaca 최소 입금 없음 ($1~)
3. 추천 초기 자금: 50~100만원 ($500~$1,000)
4. 주문 수량 축소: order_qty = 1주 (소액 시작)
5. 리스크 한도 강화:
     daily_loss_limit = 0.01  (1% → 더 보수적)
     max_position_pct = 0.10  (10% → 분산 투자)
"""

# 실전 전환 코드 예시
from trading.alpaca_client import AlpacaTrader
from trading.risk_manager  import RiskManager

trader = AlpacaTrader(paper=False)  # ← Live Trading
rm = RiskManager(
    daily_loss_limit=0.01,   # 1% 일일 한도
    max_mdd_limit=0.05,      # 5% MDD 한도
    max_position_pct=0.10,   # 10% 단일 종목
    max_trades_per_day=5,    # 하루 5건 이하
)
```

### 점진적 증액 계획

| 단계 | 기간 | 투자금 | 목표 |
|------|------|--------|------|
| Paper | 1~3개월 | $0 | 승률 55%+, MDD 10% 이하 검증 |
| 소액 실전 | 3~6개월 | $500~$1,000 | 실전 심리 + 슬리피지 확인 |
| 중액 | 6~12개월 | $2,000~$5,000 | 복리 효과, 전략 정교화 |
| 본격 운용 | 12개월+ | $10,000+ | AI 모델 고도화, 다전략 포트폴리오 |

---

## 📦 전체 패키지 설치 명령

```bash
pip install \
  alpaca-py \
  pykiwoom \          # Windows 전용 (키움증권)
  yfinance \
  pandas numpy \
  scikit-learn xgboost joblib \
  python-telegram-bot \
  python-dotenv \
  apscheduler
```

---

## 🔒 보안 주의사항

```
⚠️  절대 금지 사항:
  - API 키를 소스 코드에 직접 입력 금지
  - API 키를 GitHub에 커밋 금지 (.gitignore 에 .env 추가 필수)
  - EC2 보안그룹에 0.0.0.0:22 허용 금지 (My IP 만 허용)
  - 실거래 첫날 소액($100 이하)으로 테스트 필수

✅  권장 사항:
  - chmod 600 .env (소유자만 읽기)
  - IAM 역할로 CloudWatch 권한 부여
  - 매일 백업 + S3 복제
  - 텔레그램 알림으로 24시간 모니터링
```

---

## 📚 참고자료

| 자료 | 링크 |
|------|------|
| Alpaca 공식 문서 | https://docs.alpaca.markets |
| alpaca-py SDK | https://github.com/alpacahq/alpaca-py |
| pykiwoom | https://github.com/sharebook-kr/pykiwoom |
| 키움 OpenAPI+ | https://www.kiwoom.com/h/customer/download/VApiDocumentPage |
| APScheduler | https://apscheduler.readthedocs.io |
| AWS CloudWatch Agent | https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring |
| systemd 서비스 | https://www.freedesktop.org/software/systemd/man/systemd.service.html |

---

## ✅ 6주 완료 체크리스트

- [ ] **1주차**: EC2 접속 + Alpaca API 연동 + SPY 첫 매수 체결
- [ ] **2주차**: MA 전략 자동화 + 텔레그램 알림 정상 수신
- [ ] **3주차**: ML 모델 학습 + 서버 배포 + AI 신호 생성
- [ ] **4주차**: SQLite DB 매매 기록 + 리스크 한도 자동 정지 동작 확인
- [ ] **5주차**: systemd 서비스 등록 + CloudWatch 로그 확인 + 자동 백업 설정
- [ ] **6주차**: Paper Trading 1개월 성과 분석 → 소액 실전 전환 여부 결정
