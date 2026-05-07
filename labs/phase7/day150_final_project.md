# Day 150 – 최종 프로젝트: AI 기반 투자 분석 시스템

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (최종)

---

## 🎯 프로젝트 목표

Phase 7 전 과정을 통합하여 실전에서 사용 가능한 **AI 기반 투자 분석 시스템**을 개발하고 발표합니다.

---

## 📋 프로젝트 요구사항

### 필수 기능
| 번호 | 기능 | 관련 Day |
|------|------|----------|
| 1 | 멀티 종목 데이터 자동 수집 (국내·해외) | 121-123 |
| 2 | 기술적 지표 계산 (MA·RSI·MACD·볼린저밴드) | 131-134 |
| 3 | 기본적 분석 지표 수집 (PER·PBR·ROE) | 128 |
| 4 | ML 모델로 상승/하락 방향 예측 (XGBoost 또는 LSTM) | 143-147 |
| 5 | 백테스트 실행 및 성과 지표 계산 | 135-136 |
| 6 | 리스크 관리 (VaR·포지션 사이징) | 149 |
| 7 | 종합 리포트 생성 (PDF 또는 HTML 대시보드) | 129 |

### 선택 기능 (추가 점수)
- 실시간 신호 알림 (이메일·슬랙)
- Optuna 하이퍼파라미터 최적화 자동화
- FastAPI REST API로 서비스 노출
- 다중 전략 앙상블 (MA+RSI+ML 복합)

---

## 📁 프로젝트 구조

```
ai_investment_system/
├── main.py                  # 메인 실행 진입점
├── config.py                # 설정 (종목 목록, 기간, 파라미터)
├── data/
│   ├── collector.py         # yfinance / FinanceDataReader 데이터 수집
│   └── preprocessor.py      # 결측값 처리, 스케일링
├── indicators/
│   ├── technical.py         # MA, RSI, MACD, BB, ATR
│   └── fundamental.py       # PER, PBR, ROE 수집
├── models/
│   ├── classifier.py        # XGBoost 분류 모델
│   ├── lstm_model.py        # LSTM 시계열 모델
│   └── trainer.py           # 훈련·평가·저장 파이프라인
├── backtest/
│   ├── engine.py            # 백테스트 엔진 (룩어헤드 방지)
│   └── metrics.py           # CAGR, Sharpe, MDD, 승률
├── risk/
│   └── manager.py           # VaR, CVaR, 포지션 사이징
├── report/
│   ├── pdf_reporter.py      # fpdf2 PDF 리포트 생성
│   └── dashboard.py         # matplotlib 대시보드
└── requirements.txt
```

---

## 🧪 LAB 1 – 시스템 설계 & 핵심 모듈 통합 (08:00 – 12:00)

```python
# config.py
from dataclasses import dataclass, field

@dataclass
class Config:
    # 분석 대상
    symbols: list[str] = field(default_factory=lambda: [
        "AAPL", "MSFT", "NVDA", "GOOGL",
        "005930.KS", "000660.KS",
    ])
    period: str = "5y"

    # 기술적 지표
    ma_periods:  list[int] = field(default_factory=lambda: [5, 20, 60])
    rsi_period:  int = 14
    bb_period:   int = 20
    atr_period:  int = 14

    # 백테스트
    commission:  float = 0.001
    train_ratio: float = 0.7
    val_ratio:   float = 0.15

    # 리스크 관리
    risk_pct:    float = 0.01   # 1% 위험
    var_confidence: float = 0.95
    atr_stop_mult:  float = 2.0

    # ML 모델
    xgb_n_estimators: int = 300
    xgb_max_depth:    int = 4
    xgb_lr:           float = 0.05
    window_size:      int = 20   # LSTM 시퀀스 길이

cfg = Config()
```

```python
# main.py
from config import Config
from data.collector import collect_all
from data.preprocessor import build_features
from models.trainer import train_and_evaluate
from backtest.engine import run_backtest
from backtest.metrics import compute_metrics
from risk.manager import RiskManager
from report.pdf_reporter import generate_report

def main():
    cfg = Config()
    print("="*60)
    print("AI 기반 투자 분석 시스템 시작")
    print("="*60)

    all_results = []
    for symbol in cfg.symbols:
        print(f"\n[{symbol}] 분석 중...")

        # 1. 데이터 수집
        df_raw, info = collect_all(symbol, cfg.period)
        if df_raw is None or df_raw.empty:
            print(f"  ⚠ 데이터 없음. 건너뜀.")
            continue

        # 2. 특성 생성
        df_feat = build_features(df_raw, cfg)

        # 3. ML 모델 학습 및 예측
        model, metrics_ml, y_prob = train_and_evaluate(df_feat, cfg)

        # 4. 백테스트 (ML 신호 기반)
        bt_result = run_backtest(df_feat, y_prob, cfg)
        perf      = compute_metrics(bt_result["strategy_ret"])

        # 5. 리스크 분석
        rm = RiskManager(bt_result["strategy_ret"], cfg.var_confidence)
        risk_metrics = rm.compute()

        # 6. 결과 수집
        result = {
            "symbol": symbol, "info": info,
            "ml_metrics": metrics_ml, "perf": perf,
            "risk": risk_metrics, "bt": bt_result,
        }
        all_results.append(result)

        # 요약 출력
        print(f"  ML AUC:   {metrics_ml.get('auc', 0):.4f}")
        print(f"  CAGR:     {perf.get('CAGR(%)', 0):.2f}%")
        print(f"  Sharpe:   {perf.get('Sharpe', 0):.3f}")
        print(f"  VaR(95%): {risk_metrics.get('VaR_pct', 0):.2f}%")

    # 7. 리포트 생성
    print(f"\n📄 리포트 생성 중 ({len(all_results)}개 종목)...")
    generate_report(all_results, output_path="ai_investment_report.pdf")
    print("✅ 완료: ai_investment_report.pdf")

if __name__ == "__main__":
    main()
```

---

## 🧪 LAB 2 – 앙상블 전략 & FastAPI 서비스 (13:00 – 16:00)

```python
# models/ensemble.py
import pandas as pd
import numpy as np
from typing import Protocol

class SignalModel(Protocol):
    def predict_proba(self, X) -> np.ndarray: ...

class EnsembleSignal:
    """여러 모델의 신호를 앙상블"""

    def __init__(self, models: list[tuple[str, SignalModel, float]]):
        """
        models: [(이름, 모델, 가중치), ...]
        """
        self.models = models
        total_w = sum(w for _, _, w in models)
        self.weights = [w / total_w for _, _, w in models]

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        ensemble_prob = np.zeros(len(X))
        for (_, model, _), weight in zip(self.models, self.weights):
            prob = model.predict_proba(X)[:, 1]
            ensemble_prob += weight * prob
        return (ensemble_prob >= threshold).astype(int), ensemble_prob
```

```python
# api/main.py (FastAPI – 선택 구현)
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yfinance as yf
import pandas as pd

app = FastAPI(title="AI Investment Signal API", version="1.0")

@app.get("/signal/{symbol}")
async def get_signal(symbol: str, period: str = Query(default="3mo")):
    """종목 심볼에 대한 현재 매매 신호 반환"""
    df = yf.download(symbol, period=period, auto_adjust=True)[["Close"]].squeeze()
    if df.empty:
        return JSONResponse(status_code=404, content={"error": "데이터 없음"})

    close = df if isinstance(df, pd.Series) else df["Close"]
    ma5   = close.rolling(5).mean()
    ma20  = close.rolling(20).mean()
    delta = close.diff()
    gain, loss = delta.clip(lower=0), (-delta).clip(lower=0)
    rsi   = 100 - 100/(1 + gain.ewm(alpha=1/14,adjust=False).mean() /
                         loss.ewm(alpha=1/14,adjust=False).mean())

    trend = "상승" if float(ma5.iloc[-1]) > float(ma20.iloc[-1]) else "하락"
    rsi_v = float(rsi.iloc[-1])
    rsi_signal = "과매도(매수고려)" if rsi_v < 30 else ("과매수(매도고려)" if rsi_v > 70 else "중립")

    return {
        "symbol": symbol,
        "current_price": round(float(close.iloc[-1]), 2),
        "trend": trend,
        "rsi": round(rsi_v, 2),
        "rsi_signal": rsi_signal,
        "signal": "매수" if (trend == "상승" and rsi_v < 65) else "관망",
    }

@app.get("/portfolio/var")
async def portfolio_var(
    symbols: str = Query(default="AAPL,MSFT,GLD"),
    period:  str = Query(default="1y"),
):
    """포트폴리오 VaR 계산"""
    ticker_list = symbols.split(",")
    data = yf.download(ticker_list, period=period, auto_adjust=True)["Close"].dropna()
    weights = [1/len(ticker_list)] * len(ticker_list)
    returns = (data.pct_change().dropna() * weights).sum(axis=1)
    import numpy as np
    var95 = float(np.percentile(returns, 5)) * 100
    return {
        "symbols": ticker_list, "weights": weights,
        "VaR_95_pct": round(var95, 3),
        "description": "하루 손실이 이 비율을 초과할 확률이 5%"
    }
```

---

## 🧪 LAB 3 – 발표 준비 & 시스템 데모 (16:00 – 18:00)

### 발표 구성 (20분)

1. **프로젝트 개요** (3분)
   - 목표: "어떤 종목을 살까?"에 AI로 답하기
   - 시스템 아키텍처 다이어그램

2. **기술 스택** (2분)
   - 데이터: yfinance, FinanceDataReader
   - 분석: pandas, scikit-learn, XGBoost, TensorFlow
   - 시각화: matplotlib, plotly
   - 서비스: FastAPI

3. **핵심 모듈 시연** (10분)
   - 데이터 수집 → 지표 계산 → ML 예측 → 백테스트 → 리스크 분석
   - 생성된 PDF 리포트 시연

4. **결과 분석** (3분)
   - 가장 성과 좋은 종목 및 전략
   - 한계점 및 개선 방향

5. **Q&A** (2분)

---

## 📝 최종 제출물

| 파일 | 내용 |
|------|------|
| `ai_investment_report.pdf` | 분석 대상 모든 종목의 PDF 리포트 |
| `backtest_results.csv` | 백테스트 성과 요약 |
| `strategy_dashboard.png` | 전략 대시보드 |
| `requirements.txt` | 사용 패키지 목록 |
| `README.md` | 프로젝트 설명 및 실행 방법 |

---

## ✅ 최종 체크리스트 (Phase 7 전체)

### 초급 (Day 121-130)
- [ ] 금융 데이터(OHLCV, 재무) 자유롭게 수집 가능
- [ ] pandas 시계열 분석 가능 (resample, rolling, shift)
- [ ] 기본적 분석 지표 (PER·PBR·ROE) 계산 가능

### 중급 (Day 131-140)
- [ ] MA·RSI·MACD·볼린저밴드 구현 및 신호 탐지 가능
- [ ] 백테스트 프레임워크 구축 (룩어헤드 방지, 거래비용 포함)
- [ ] CAGR·Sharpe·MDD 등 성과 지표 계산 가능
- [ ] 포트폴리오 자산 배분 및 리밸런싱 구현 가능

### 고급 (Day 141-150)
- [ ] scikit-learn 파이프라인으로 ML 모델 구축 가능
- [ ] XGBoost 분류 모델로 방향 예측 가능
- [ ] LSTM으로 시계열 주가 예측 가능
- [ ] Optuna 하이퍼파라미터 최적화 가능
- [ ] VaR·CVaR·포지션 사이징 계산 가능
- [ ] 최종 프로젝트 완성 및 발표

---

## 📚 추가 학습 로드맵

- **Transformer 모델**: Temporal Fusion Transformer (TFT)
- **강화학습**: 자동매매 RL (FinRL, Stable-Baselines3)
- **대안 데이터**: 뉴스 감성분석(NLP), 위성 데이터
- **클라우드 배포**: AWS, GCP에서 실시간 신호 서비스
- **논문**: "Attention Is All You Need", "A Deep Learning Framework for Financial Time Series"

---

*🎓 Phase 7 금융 데이터 분석 & 머신러닝 과정 완료!*  
*"데이터로 보고, AI로 판단하고, 리스크를 관리하라."*

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day150+final+project
