# Day 129 – 미니 프로젝트: 종목 기본 분석 리포트 자동화

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (초급)

---

## 🎯 학습 목표

- 지금까지 배운 기술(yfinance, pandas, matplotlib, fpdf2)을 통합
- 종목별 기본 분석 리포트를 자동으로 PDF로 생성
- 데이터 수집 → 분석 → 시각화 → 문서화 파이프라인 구축

---

## 📋 프로젝트 요구사항

1. **입력**: 종목 심볼 리스트 (예: `["AAPL", "MSFT", "GOOGL"]`)
2. **수집**: yfinance로 1년 OHLCV + 재무 지표
3. **분석**: 연간 수익률, 변동성, PER·PBR·ROE, MA20·MA60
4. **시각화**: 주가 차트 (PNG) 자동 생성
5. **출력**: 종목별 1페이지 PDF 리포트 생성

---

## 📖 이론 (08:00 – 10:00)

### fpdf2 기초
```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=12)
pdf.cell(200, 10, "Hello, Finance Report!", align="C")
pdf.image("chart.png", x=10, y=30, w=190)
pdf.output("report.pdf")
```

### 프로젝트 구조
```
finance_report/
├── main.py          # 메인 실행 스크립트
├── collector.py     # 데이터 수집 모듈
├── analyzer.py      # 분석 모듈
├── visualizer.py    # 차트 생성 모듈
├── reporter.py      # PDF 생성 모듈
└── output/          # 생성된 파일 저장
    ├── charts/
    └── reports/
```

---

## 🧪 LAB 1 – 모듈 구현 (10:00 – 12:00)

```python
# collector.py
import yfinance as yf
import pandas as pd

def collect_stock_data(symbol: str, period: str = "1y") -> tuple[pd.DataFrame, dict]:
    """OHLCV 데이터와 기업 정보 수집"""
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period, auto_adjust=True)
    info = ticker.info
    return hist, info

def get_key_metrics(info: dict) -> dict:
    """핵심 재무 지표 추출"""
    def pct(val):
        return round((val or 0) * 100, 2)
    return {
        "Name": info.get("shortName", "N/A"),
        "Sector": info.get("sector", "N/A"),
        "Price": info.get("currentPrice", 0),
        "PER": round(info.get("trailingPE") or 0, 2),
        "PBR": round(info.get("priceToBook") or 0, 2),
        "ROE(%)": pct(info.get("returnOnEquity")),
        "DivYield(%)": pct(info.get("dividendYield")),
        "52W_High": info.get("fiftyTwoWeekHigh", 0),
        "52W_Low": info.get("fiftyTwoWeekLow", 0),
    }
```

```python
# analyzer.py
import pandas as pd
import numpy as np

def compute_metrics(df: pd.DataFrame) -> dict:
    """연간 수익률, 변동성, 샤프지수 계산"""
    close = df["Close"].squeeze()
    returns = close.pct_change().dropna()
    annual_return = (close.iloc[-1] / close.iloc[0] - 1) * 100
    annual_vol = returns.std() * np.sqrt(252) * 100
    sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
    mdd_val = ((close / close.cummax()) - 1).min() * 100
    return {
        "연수익률(%)": round(annual_return, 2),
        "연변동성(%)": round(annual_vol, 2),
        "샤프지수": round(sharpe, 3),
        "최대낙폭(%)": round(mdd_val, 2),
    }

def compute_ma(df: pd.DataFrame) -> pd.DataFrame:
    """이동평균선 추가"""
    df = df.copy()
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA60"] = df["Close"].rolling(60).mean()
    return df
```

---

## 🧪 LAB 2 – 차트 생성 & PDF 리포트 (13:00 – 15:00)

```python
# visualizer.py
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

def save_chart(df, symbol: str, output_dir: str = "output/charts") -> str:
    os.makedirs(output_dir, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7),
                                    gridspec_kw={"height_ratios": [3, 1]},
                                    sharex=True)
    close = df["Close"].squeeze()
    ax1.plot(df.index, close, label="Close", linewidth=1.5, color="steelblue")
    if "MA20" in df.columns:
        ax1.plot(df.index, df["MA20"].squeeze(), label="MA20", color="orange", linestyle="--")
    if "MA60" in df.columns:
        ax1.plot(df.index, df["MA60"].squeeze(), label="MA60", color="red", linestyle="--")
    ax1.set_title(f"{symbol} – Price & Moving Averages", fontsize=13)
    ax1.set_ylabel("Price")
    ax1.legend(fontsize=9)
    ax1.grid(alpha=0.3)

    vol = df["Volume"].squeeze()
    ax2.bar(df.index, vol, color="steelblue", alpha=0.6, width=1)
    ax2.set_ylabel("Volume")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, f"{symbol}_chart.png")
    plt.savefig(path, dpi=120)
    plt.close()
    return path
```

```python
# reporter.py
from fpdf import FPDF
import os

def generate_report(symbol: str, key_metrics: dict, perf_metrics: dict,
                    chart_path: str, output_dir: str = "output/reports") -> str:
    os.makedirs(output_dir, exist_ok=True)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, f"Stock Analysis Report: {symbol}", align="C", ln=True)

    pdf.set_font("Helvetica", size=11)
    pdf.ln(2)
    pdf.cell(0, 8, f"Company: {key_metrics['Name']}  |  Sector: {key_metrics['Sector']}", ln=True)
    pdf.ln(3)

    # 재무 지표 테이블
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Key Financial Metrics", ln=True)
    pdf.set_font("Helvetica", size=10)
    for k, v in key_metrics.items():
        if k not in ("Name", "Sector"):
            pdf.cell(60, 7, f"{k}:", border=0)
            pdf.cell(0, 7, str(v), ln=True)

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Performance Metrics (1 Year)", ln=True)
    pdf.set_font("Helvetica", size=10)
    for k, v in perf_metrics.items():
        pdf.cell(60, 7, f"{k}:", border=0)
        pdf.cell(0, 7, str(v), ln=True)

    # 차트 삽입
    pdf.ln(4)
    if os.path.exists(chart_path):
        pdf.image(chart_path, x=10, w=190)

    out_path = os.path.join(output_dir, f"{symbol}_report.pdf")
    pdf.output(out_path)
    return out_path
```

---

## 🧪 LAB 3 – 메인 실행 스크립트 (15:00 – 17:00)

```python
# main.py
from collector import collect_stock_data, get_key_metrics
from analyzer import compute_metrics, compute_ma
from visualizer import save_chart
from reporter import generate_report

SYMBOLS = ["AAPL", "MSFT", "NVDA"]

for symbol in SYMBOLS:
    print(f"\n처리 중: {symbol}")
    hist, info = collect_stock_data(symbol, period="1y")
    if hist.empty:
        print(f"  데이터 없음. 건너뜀.")
        continue

    key_metrics  = get_key_metrics(info)
    perf_metrics = compute_metrics(hist)
    hist_ma      = compute_ma(hist)
    chart_path   = save_chart(hist_ma, symbol)
    report_path  = generate_report(symbol, key_metrics, perf_metrics, chart_path)
    print(f"  리포트 저장: {report_path}")
    print(f"  수익률: {perf_metrics['연수익률(%)']:.2f}%  |  샤프: {perf_metrics['샤프지수']:.3f}")

print("\n✅ 모든 리포트 생성 완료!")
```

---

## 📝 과제 (17:00 – 18:00)

1. 분석 대상을 확장하여 국내 주식(삼성전자 등)도 포함하세요.
2. 리포트에 "투자 의견" 섹션을 추가하세요 (PER·ROE 기준으로 자동 판단: 매수/중립/주의).
3. 여러 종목의 수익률 비교 차트를 마지막 페이지에 추가하세요.

---

## ✅ 체크리스트

- [ ] `collector`, `analyzer`, `visualizer`, `reporter` 모듈 분리 구현
- [ ] PNG 차트 자동 저장 성공
- [ ] PDF 리포트 자동 생성 성공
- [ ] 3개 이상 종목 리포트 생성 성공
- [ ] 과제 제출

---

## 📚 참고자료

- [fpdf2 공식 문서](https://pyfpdf.github.io/fpdf2/)
- [matplotlib savefig](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html)
- [yfinance history](https://yfinance.readthedocs.io/en/stable/reference/yfinance.scrapers.history.html)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day129+project+report
