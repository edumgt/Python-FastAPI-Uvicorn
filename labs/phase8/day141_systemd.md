# Day 141 – systemd 서비스 등록 + 자동 재시작

> **소요시간**: 8시간 | **Phase**: 8 – 자동매매 시스템 실전 | **Week 5**

---

## 🎯 학습 목표

- systemd 서비스 파일 작성 및 자동매매 봇 등록
- EC2 재부팅 후 자동 시작 설정
- `journalctl` 로 로그 확인 방법 습득
- `Restart=on-failure` + 재시도 간격 설정으로 에러 복구 자동화

---

## 📖 이론 (08:00 – 10:00)

### 1. 왜 systemd인가?

```
문제: nohup python main.py & 방식

  ❌ EC2 재부팅 시 자동 시작 안 됨
  ❌ 크래시 시 자동 재시작 안 됨
  ❌ 로그 관리 어려움
  ❌ 시작/정지 명령 없음

해결: systemd 서비스

  ✅ 부팅 시 자동 시작 (systemctl enable)
  ✅ 크래시 시 자동 재시작 (Restart=on-failure)
  ✅ journalctl 로 중앙 로그 관리
  ✅ systemctl start/stop/restart/status
```

### 2. 서비스 파일 핵심 옵션

```ini
[Service]
Type=simple          # 단일 프로세스
Restart=on-failure   # 비정상 종료 시 재시작
RestartSec=30        # 재시작 대기 30초
StartLimitBurst=5    # 10분 내 최대 5회 재시작
StartLimitInterval=600

Environment=PATH=...  # 가상환경 경로
WorkingDirectory=...  # 작업 디렉터리
ExecStart=...         # 실행 명령
StandardOutput=append:/path/trader.log   # 로그 파일
```

### 3. 서비스 관리 명령

```bash
sudo systemctl start autotrader      # 시작
sudo systemctl stop autotrader       # 정지
sudo systemctl restart autotrader    # 재시작
sudo systemctl status autotrader     # 상태 확인
sudo systemctl enable autotrader     # 부팅 시 자동 시작 등록
sudo systemctl disable autotrader    # 자동 시작 해제

journalctl -u autotrader -f          # 실시간 로그
journalctl -u autotrader --since "1 hour ago"  # 최근 1시간
```

---

## 🧪 LAB 1 – 메인 실행 파일 준비 (10:00 – 12:00)

```python
# ~/autotrader/main.py
"""
자동매매 메인 진입점
systemd 에서 ExecStart 로 호출되는 파일
"""
import logging
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 로그 설정
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("logs/trader.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# 최대 재시도 설정
MAX_RETRIES    = 5
RETRY_INTERVAL = 60   # 초

def run_once():
    """전략 1회 실행 – 실제 로직은 여기서 호출"""
    from trading.alpaca_client import AlpacaTrader
    from trading.risk_manager import RiskManager
    from trading.telegram_notifier import TelegramNotifier

    trader   = AlpacaTrader(paper=True)
    notifier = TelegramNotifier()
    rm       = RiskManager(daily_loss_limit=0.02, max_mdd_limit=0.10)

    acc = trader.get_account()
    rm.update_portfolio_value(acc.portfolio_value)
    logger.info("자산: $%.2f | 거래가능: %s", acc.portfolio_value, rm.can_trade())

    if not rm.can_trade():
        notifier.send(f"🚨 거래 중단: {rm.stop_reason}")
        return

    watchlist = ["SPY", "QQQ", "AAPL"]
    for symbol in watchlist:
        try:
            sig = trader.ma_cross_signal(symbol)
            logger.info("[%s] 신호: %s | 가격: %.4f", symbol, sig["signal"], sig["price"])

            if sig["signal"] == "BUY":
                pos = trader.get_position(symbol)
                if pos is None:
                    order = trader.market_order(symbol, qty=1, side="buy")
                    notifier.send_trade(symbol, "BUY", 1, sig["price"],
                                        broker="alpaca", order_id=order.order_id)
                    rm.record_trade(symbol)
            elif sig["signal"] == "SELL":
                pos = trader.get_position(symbol)
                if pos:
                    trader.close_position(symbol)
                    notifier.send_signal(symbol, "SELL", sig["price"])
                    rm.record_trade(symbol)

        except Exception as exc:
            logger.error("[%s] 오류: %s", symbol, exc)
            notifier.send_error(f"run_once({symbol})", exc=exc)

def main():
    logger.info("=== 자동매매 시스템 시작 ===")

    retries = 0
    while retries < MAX_RETRIES:
        try:
            from trading.telegram_notifier import TelegramNotifier
            notifier = TelegramNotifier()
            notifier.send_system_status("START", f"봇 시작 (재시도: {retries}/{MAX_RETRIES})")

            while True:
                logger.info("전략 실행 시작...")
                run_once()
                logger.info("다음 실행까지 대기 (3600초)")
                time.sleep(3600)   # 1시간 대기

        except KeyboardInterrupt:
            logger.info("수동 종료")
            notifier.send_system_status("STOP", "수동 종료 (KeyboardInterrupt)")
            break
        except Exception as exc:
            retries += 1
            logger.error("치명적 오류 (재시도 %d/%d): %s", retries, MAX_RETRIES, exc)
            if retries < MAX_RETRIES:
                logger.info("%d초 후 재시도...", RETRY_INTERVAL)
                time.sleep(RETRY_INTERVAL)

    logger.critical("최대 재시도 초과 – 시스템 종료")

if __name__ == "__main__":
    main()
```

---

## 🧪 LAB 2 – systemd 서비스 파일 작성 및 등록 (13:00 – 15:00)

```bash
# EC2 에서 실행

# ── 서비스 파일 작성 ──────────────────────────────────────
sudo tee /etc/systemd/system/autotrader.service << 'EOF'
[Unit]
Description=AI 자동매매 봇 서비스
Documentation=https://github.com/edumgt/Python-FastAPI-Uvicorn
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ec2-user
Group=ec2-user

WorkingDirectory=/home/ec2-user/autotrader
Environment="PATH=/home/ec2-user/autotrader/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"

ExecStart=/home/ec2-user/autotrader/venv/bin/python main.py

# 재시작 설정
Restart=on-failure
RestartSec=30
StartLimitBurst=5
StartLimitInterval=600

# 로그 설정
StandardOutput=append:/home/ec2-user/autotrader/logs/trader.log
StandardError=append:/home/ec2-user/autotrader/logs/error.log

# 보안 강화
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/home/ec2-user/autotrader

[Install]
WantedBy=multi-user.target
EOF

# ── 로그 디렉터리 생성 ────────────────────────────────────
mkdir -p ~/autotrader/logs

# ── 서비스 등록 및 시작 ──────────────────────────────────
sudo systemctl daemon-reload
sudo systemctl enable autotrader.service   # 부팅 시 자동 시작
sudo systemctl start autotrader.service    # 즉시 시작

# ── 상태 확인 ─────────────────────────────────────────────
sudo systemctl status autotrader.service

# ── 실시간 로그 ───────────────────────────────────────────
journalctl -u autotrader.service -f
# 또는
tail -f ~/autotrader/logs/trader.log
```

---

## 🧪 LAB 3 – 자동 재시작 테스트 + 에러 복구 검증 (15:00 – 17:00)

```bash
# 의도적으로 프로세스 죽이기 (자동 재시작 확인)
sudo systemctl status autotrader.service | grep "Main PID"
# Main PID: 12345 → PID 확인

sudo kill -9 12345   # 강제 종료

# 30초 후 자동 재시작 확인
sleep 35
sudo systemctl status autotrader.service
# ✅ Active: active (running) 이면 자동 재시작 성공

# 재시작 이력 확인
journalctl -u autotrader.service | grep -E "Started|Failed|Stopped"

# 서비스 정지
sudo systemctl stop autotrader.service

# EC2 재부팅 후 자동 시작 확인
sudo reboot
# (재접속 후)
sudo systemctl status autotrader.service
# ✅ Active: active (running) 이면 부팅 자동 시작 성공
```

### 서비스 관리 헬퍼 스크립트

```bash
# ~/autotrader/scripts/manage.sh
#!/bin/bash
case "$1" in
  start)   sudo systemctl start autotrader ;;
  stop)    sudo systemctl stop autotrader ;;
  restart) sudo systemctl restart autotrader ;;
  status)  sudo systemctl status autotrader ;;
  log)     journalctl -u autotrader -f ;;
  errors)  journalctl -u autotrader -p err --since "24 hours ago" ;;
  *)
    echo "사용법: $0 {start|stop|restart|status|log|errors}"
    exit 1
    ;;
esac

# 사용
# chmod +x scripts/manage.sh
# ./scripts/manage.sh start
# ./scripts/manage.sh log
```

---

## 📝 과제 (17:00 – 18:00)

1. `autotrader.service` 를 등록하고 `systemctl status` 로 `active (running)` 을 확인하세요.
2. `kill -9 <PID>` 로 강제 종료 후 30초 내 자동 재시작되는지 확인하세요.
3. EC2 를 재부팅한 후 SSH 재접속하여 서비스가 자동 시작됨을 확인하세요.

---

## ✅ 체크리스트

- [ ] `autotrader.service` 파일 작성 완료
- [ ] `systemctl enable` → 부팅 자동 시작 등록
- [ ] `systemctl start` → 서비스 실행 확인
- [ ] `journalctl -f` 실시간 로그 확인
- [ ] `kill -9` 후 자동 재시작 (30초 내) 확인
- [ ] EC2 재부팅 후 자동 시작 확인

---

## 📚 참고자료

- [systemd 서비스 공식 문서](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [journalctl 사용법](https://www.man7.org/linux/man-pages/man1/journalctl.1.html)
- [systemd 보안 옵션](https://www.freedesktop.org/software/systemd/man/systemd.exec.html)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day141+systemd
