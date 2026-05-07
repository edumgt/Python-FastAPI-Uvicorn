# Day 126 – 데이터 시각화 (matplotlib & plotly)

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (초급)

---

## 🎯 학습 목표

- `matplotlib`으로 주가 라인 차트·거래량 바 차트 작성
- 이동평균선을 차트에 겹쳐 표시
- `plotly`로 인터랙티브 캔들스틱 차트 생성
- 서브플롯(subplot)으로 가격·지표 동시 표시

---

## 📖 이론 (08:00 – 10:00)

### 1. matplotlib 기본 구조
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df.index, df["Close"], label="Close")
ax.set_title("주가 차트")
ax.set_xlabel("날짜")
ax.set_ylabel("가격(원)")
ax.legend()
plt.tight_layout()
plt.show()
```

### 2. plotly express & graph_objects
```python
import plotly.graph_objects as go

fig = go.Figure(data=[go.Candlestick(
    x=df.index, open=df["Open"], high=df["High"],
    low=df["Low"], close=df["Close"]
)])
fig.show()
```

### 3. 서브플롯
```python
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(12, 8))
gs = GridSpec(2, 1, height_ratios=[3, 1])
ax1 = fig.add_subplot(gs[0])  # 가격
ax2 = fig.add_subplot(gs[1])  # 거래량
```

---

## 🧪 LAB 1 – 주가 + 이동평균선 차트 (10:00 – 12:00)

```python
# chart_ma.py
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

df = yf.download("AAPL", period="1y", auto_adjust=True)

df["MA20"] = df["Close"].rolling(20).mean()
df["MA60"] = df["Close"].rolling(60).mean()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8),
                                gridspec_kw={"height_ratios": [3, 1]},
                                sharex=True)

# 가격 + 이동평균선
ax1.plot(df.index, df["Close"], label="Close", linewidth=1.5, color="steelblue")
ax1.plot(df.index, df["MA20"], label="MA20", linewidth=1.2, color="orange", linestyle="--")
ax1.plot(df.index, df["MA60"], label="MA60", linewidth=1.2, color="red", linestyle="--")
ax1.set_title("Apple (AAPL) – 주가 & 이동평균선", fontsize=14)
ax1.set_ylabel("Price (USD)")
ax1.legend()
ax1.grid(alpha=0.3)

# 거래량
colors = ["green" if c >= o else "red"
          for c, o in zip(df["Close"].squeeze(), df["Open"].squeeze())]
ax2.bar(df.index, df["Volume"].squeeze(), color=colors, alpha=0.7, width=1)
ax2.set_ylabel("Volume")
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("aapl_chart.png", dpi=150)
print("차트 저장: aapl_chart.png")
plt.show()
```

---

## 🧪 LAB 2 – plotly 캔들스틱 차트 (13:00 – 15:00)

```python
# candlestick.py
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

df = yf.download("005930.KS", period="6mo", auto_adjust=True)
df["MA20"] = df["Close"].rolling(20).mean()
df["MA60"] = df["Close"].rolling(60).mean()

fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                    vertical_spacing=0.05,
                    row_heights=[0.7, 0.3])

# 캔들스틱
fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["Open"].squeeze(), high=df["High"].squeeze(),
    low=df["Low"].squeeze(), close=df["Close"].squeeze(),
    name="OHLC"
), row=1, col=1)

# 이동평균선
fig.add_trace(go.Scatter(x=df.index, y=df["MA20"].squeeze(),
                         name="MA20", line=dict(color="orange", width=1.5)),
              row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["MA60"].squeeze(),
                         name="MA60", line=dict(color="red", width=1.5)),
              row=1, col=1)

# 거래량
fig.add_trace(go.Bar(x=df.index, y=df["Volume"].squeeze(),
                     name="Volume", marker_color="steelblue"),
              row=2, col=1)

fig.update_layout(
    title="삼성전자 (005930.KS) – 캔들스틱 차트",
    xaxis_rangeslider_visible=False,
    height=600
)
fig.write_html("samsung_chart.html")
print("인터랙티브 차트 저장: samsung_chart.html")
fig.show()
```

---

## 🧪 LAB 3 – 다중 종목 수익률 비교 차트 (15:00 – 17:00)

```python
# multi_chart.py
import yfinance as yf
import matplotlib.pyplot as plt

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]
data = yf.download(tickers, period="1y", auto_adjust=True)["Close"]

# 정규화: 첫날 기준 수익률
normalized = (data / data.iloc[0] * 100).round(2)

fig, ax = plt.subplots(figsize=(14, 6))
for ticker in tickers:
    col = ticker if ticker in normalized.columns else normalized.columns[0]
    ax.plot(normalized.index, normalized[col], label=ticker, linewidth=1.5)

ax.axhline(y=100, color="gray", linestyle="--", linewidth=0.8)
ax.set_title("미국 빅테크 1년 상대 수익률 (기준=100)", fontsize=13)
ax.set_ylabel("상대 가격 (시작=100)")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("bigtech_compare.png", dpi=150)
print("차트 저장: bigtech_compare.png")
plt.show()
```

---

## 📝 과제 (17:00 – 18:00)

1. 관심 종목 3개를 선택해 `plotly`로 캔들스틱 + 거래량 서브플롯 차트를 만들고 HTML로 저장하세요.
2. 같은 종목들의 1년 수익률을 정규화하여 비교 라인 차트를 `matplotlib`으로 작성하세요.
3. 이동평균선(MA5, MA20)이 교차하는 날짜를 수직선(`axvline`)으로 표시하세요.

---

## ✅ 체크리스트

- [ ] `matplotlib`으로 주가 + 거래량 차트 생성 성공
- [ ] `plotly`로 인터랙티브 캔들스틱 차트 생성 성공
- [ ] 다중 종목 정규화 비교 차트 작성
- [ ] 차트를 PNG·HTML 파일로 저장 성공
- [ ] 과제 제출

---

## 📚 참고자료

- [matplotlib 공식 문서](https://matplotlib.org/stable/index.html)
- [plotly 공식 문서](https://plotly.com/python/)
- [plotly 금융 차트 가이드](https://plotly.com/python/candlestick-charts/)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day126+visualization
