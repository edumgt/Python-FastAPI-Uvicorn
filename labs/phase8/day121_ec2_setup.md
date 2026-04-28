# Day 121 – EC2 인스턴스 생성 + Python 환경 구성

> **소요시간**: 8시간 | **Phase**: 8 – 자동매매 시스템 실전 | **Week 1**

---

## 🎯 학습 목표

- AWS EC2 인스턴스 생성 및 SSH 접속
- Python 3.11 + 가상환경 + 자동매매 패키지 설치
- `.env` 보안 설정 및 디렉터리 구조 구성
- `trading/` 패키지 동작 확인

---

## 📖 이론 (08:00 – 10:00)

### 1. 자동매매 시스템 아키텍처

```
로컬 PC (개발·분석·모델 학습)
    ↓  git push / scp
EC2 서버 (24시간 자동 실행)
    ├── trading/          자동매매 Python 패키지
    ├── models/           학습된 ML 모델
    ├── data/trading.db   SQLite 매매 기록
    ├── logs/             로그 파일
    ├── main.py           메인 진입점
    └── .env              API 키 (gitignore 필수)
            ↓  API 호출
    Alpaca Markets (미국 주식)
    키움증권 OpenAPI+ (국내 주식, Windows)
            ↓  실행 결과
    텔레그램 알림 → 내 스마트폰
```

### 2. EC2 인스턴스 선택 기준

| 스펙 | 선택 이유 |
|------|-----------|
| **t3.small** (권장) | vCPU 2, RAM 2GB – 월 약 $15, 단순 전략용 |
| t3.medium | vCPU 2, RAM 4GB – ML 추론 포함 시 |
| t3.large  | vCPU 2, RAM 8GB – LSTM 모델 + 다종목 |

### 3. 보안 원칙

```
✅  해야 할 것:
  - .env 는 .gitignore 에 반드시 추가
  - chmod 600 .env  (소유자만 읽기)
  - EC2 보안그룹 SSH(22) → My IP 만 허용
  - API 키는 .env 파일로만 관리

❌  절대 금지:
  - 소스코드에 API 키 직접 입력
  - GitHub 에 .env 파일 커밋
  - 보안그룹 0.0.0.0/0:22 허용
```

---

## 🧪 LAB 1 – EC2 인스턴스 생성 (10:00 – 12:00)

### AWS 콘솔 절차

```
1. AWS 콘솔 → EC2 → Launch Instance
2. Name: autotrader-server
3. AMI: Amazon Linux 2023 (64-bit x86)
4. Instance type: t3.small
5. Key pair: 새 키페어 생성 → autotrader-key.pem 다운로드
6. 보안그룹:
     - SSH(22) → My IP
     - (다른 포트 불필요)
7. 스토리지: 20GB gp3
8. Launch Instance
```

### SSH 접속

```bash
# 로컬 PC
chmod 400 autotrader-key.pem

ssh -i autotrader-key.pem ec2-user@<EC2_PUBLIC_IP>
# ✅ Amazon Linux 2023 배너가 보이면 성공
```

---

## 🧪 LAB 2 – Python 환경 설치 (13:00 – 15:00)

```bash
# EC2 접속 후 실행

# ── 시스템 업데이트 ──────────────────────────────────────
sudo dnf update -y
sudo dnf install python3.11 python3.11-pip git -y

python3.11 --version   # Python 3.11.x 확인

# ── 프로젝트 디렉터리 ────────────────────────────────────
mkdir -p ~/autotrader/{models,data,logs}
cd ~/autotrader

# ── 가상환경 ─────────────────────────────────────────────
python3.11 -m venv venv
source venv/bin/activate

# ── 패키지 설치 ──────────────────────────────────────────
pip install --upgrade pip

pip install \
  alpaca-py \
  yfinance \
  pandas numpy \
  scikit-learn xgboost joblib \
  python-telegram-bot \
  python-dotenv \
  apscheduler

pip list | grep -E "alpaca|yfinance|sklearn"

# ── .env 파일 생성 ────────────────────────────────────────
cat > .env << 'EOF'
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
KIWOOM_ACCOUNT_NO=
EOF

chmod 600 .env
echo ".env" >> .gitignore
```

---

## 🧪 LAB 3 – trading 패키지 업로드 및 동작 확인 (15:00 – 17:00)

### 로컬에서 EC2 로 파일 전송

```bash
# 로컬 PC 에서 실행
scp -i autotrader-key.pem -r trading/ \
    ec2-user@<EC2_IP>:~/autotrader/
```

### EC2 에서 패키지 동작 확인

```python
# check_packages.py
"""모든 trading 모듈 임포트 확인"""
print("모듈 임포트 테스트...")

tests = [
    ("alpaca_client",     "from trading.alpaca_client import AlpacaTrader"),
    ("kiwoom_client",     "from trading.kiwoom_client import KiwoomTrader"),
    ("auto_trader",       "from trading.auto_trader import AutoTrader"),
    ("telegram_notifier", "from trading.telegram_notifier import TelegramNotifier"),
    ("ml_strategy",       "from trading.ml_strategy import MLStrategy"),
    ("risk_manager",      "from trading.risk_manager import RiskManager"),
    ("trade_logger",      "from trading.trade_logger import TradeLogger"),
]

for name, stmt in tests:
    try:
        exec(stmt)
        print(f"  ✅ {name}")
    except ImportError as e:
        print(f"  ❌ {name}: {e}")
    except Exception as e:
        print(f"  ⚠️  {name}: {e}")

print("\n환경변수 확인...")
import os
from dotenv import load_dotenv
load_dotenv()

keys = ["ALPACA_API_KEY", "ALPACA_SECRET_KEY", "TELEGRAM_BOT_TOKEN"]
for k in keys:
    v = os.getenv(k, "")
    status = "✅ 설정됨" if v else "⚠️  미설정"
    print(f"  {k}: {status}")
```

```bash
python check_packages.py
```

---

## 📝 과제 (17:00 – 18:00)

1. EC2 인스턴스를 생성하고 SSH 접속에 성공하세요.
2. `check_packages.py` 를 실행하여 모든 모듈이 ✅ 임포트됨을 확인하세요.
3. Alpaca Paper Trading 계좌를 생성하고 API 키를 `.env` 에 설정하세요.

---

## ✅ 체크리스트

- [ ] EC2 t3.small 인스턴스 생성 완료
- [ ] SSH 접속 성공 (키페어 파일 안전 보관)
- [ ] Python 3.11 + venv 설치 완료
- [ ] 자동매매 패키지 전체 설치 완료
- [ ] `.env` 설정 + `chmod 600` 완료
- [ ] `check_packages.py` 실행 – 전체 ✅ 확인
- [ ] Alpaca API 키 발급 완료

---

## 📚 참고자료

- [AWS EC2 시작 가이드](https://docs.aws.amazon.com/ec2/latest/userguide/EC2_GetStarted.html)
- [Alpaca 회원가입](https://app.alpaca.markets)
- [alpaca-py 공식 문서](https://docs.alpaca.markets/docs/getting-started)
