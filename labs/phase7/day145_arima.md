# Day 145 – 시계열 분석 (ARIMA)

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (고급)

---

## 🎯 학습 목표

- 정상성(Stationarity) 개념과 ADF 검정
- ARIMA(p,d,q) 모델 구조 이해 및 파라미터 결정
- ACF·PACF 플롯으로 AR·MA 차수 결정
- `auto_arima`로 자동 파라미터 선택 및 예측

---

## 📖 이론 (08:00 – 10:00)

### 1. 정상성(Stationarity)
- 평균·분산·공분산이 시간에 무관하게 일정한 시계열
- 주가 수준(level): 비정상 → **차분**으로 정상화
- 로그 수익률: 대부분 정상

```python
from statsmodels.tsa.stattools import adfuller
adf_result = adfuller(series)
# p-value < 0.05 → 정상 (단위근 없음)
```

### 2. ARIMA(p, d, q)
| 파라미터 | 의미 |
|---------|------|
| p (AR) | 과거 p개 자기 시차 |
| d (I) | 차분 횟수 (비정상→정상) |
| q (MA) | 과거 q개 오차 시차 |

### 3. 파라미터 결정 방법
- **d**: ADF 검정 → 유의할 때까지 차분
- **p**: PACF 플롯 → 유의한 시차 수
- **q**: ACF 플롯 → 유의한 시차 수
- **auto_arima** (pmdarima): AIC 기준 자동 탐색

---

## 🧪 LAB 1 – 정상성 검정 (10:00 – 12:00)

```python
# stationarity.py
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

df = yf.download("AAPL", period="5y", auto_adjust=True)[["Close"]]
close = df["Close"].squeeze()

# 변환
series = {
    "주가(원본)": close,
    "로그 주가": np.log(close),
    "1차 차분": close.diff().dropna(),
    "로그 수익률": np.log(close).diff().dropna(),
}

print("=== ADF 정상성 검정 ===")
for name, s in series.items():
    result = adfuller(s.dropna(), autolag="AIC")
    pvalue = result[1]
    stationary = "✅ 정상" if pvalue < 0.05 else "❌ 비정상"
    print(f"  {name:15s}: p-value={pvalue:.6f}  {stationary}")

# ACF·PACF 플롯 (로그 수익률)
log_ret = np.log(close).diff().dropna()
fig, axes = plt.subplots(2, 1, figsize=(12, 7))
plot_acf(log_ret,  lags=30, ax=axes[0], title="ACF – 로그 수익률")
plot_pacf(log_ret, lags=30, ax=axes[1], title="PACF – 로그 수익률")
plt.tight_layout()
plt.savefig("acf_pacf.png", dpi=150)
plt.show()
```

---

## 🧪 LAB 2 – ARIMA 모델 적합 (13:00 – 15:00)

```python
# arima_fit.py
import yfinance as yf
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.stats.diagnostic import acorr_ljungbox
import matplotlib.pyplot as plt

df = yf.download("AAPL", period="3y", auto_adjust=True)[["Close"]]
log_ret = np.log(df["Close"].squeeze()).diff().dropna()

# 훈련/테스트 분리
split = int(len(log_ret) * 0.8)
train, test = log_ret.iloc[:split], log_ret.iloc[split:]

# ARIMA(2,0,2) 적합 (로그 수익률은 이미 정상)
model = ARIMA(train, order=(2, 0, 2))
result = model.fit()
print(result.summary())

# 진단 통계
lb = acorr_ljungbox(result.resid, lags=10, return_df=True)
print(f"\n잔차 Ljung-Box 검정 (p>0.05이면 OK):")
print(lb.round(4))

# 예측
n_forecast = len(test)
forecast = result.forecast(steps=n_forecast)

# 시각화
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8))
ax1.plot(train.index[-60:], train.iloc[-60:], label="훈련(마지막 60일)", alpha=0.7)
ax1.plot(test.index, test, label="실제", color="steelblue")
ax1.plot(test.index, forecast, label="ARIMA 예측", color="orange", linestyle="--")
ax1.set_title("ARIMA(2,0,2) – 로그 수익률 예측")
ax1.legend()
ax1.grid(alpha=0.3)

ax2.plot(result.resid, lw=0.8, color="gray")
ax2.axhline(0, color="black", lw=0.8)
ax2.set_title("잔차(Residuals)")
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("arima_result.png", dpi=150)
plt.show()
```

---

## 🧪 LAB 3 – auto_arima & 예측 구간 (15:00 – 17:00)

```python
# auto_arima_demo.py
# pip install pmdarima
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

try:
    from pmdarima import auto_arima
except ImportError:
    print("pip install pmdarima 필요")
    raise

df = yf.download("AAPL", period="3y", auto_adjust=True)[["Close"]]
close = df["Close"].squeeze()
log_price = np.log(close)

# 훈련/테스트 분리
split = int(len(log_price) * 0.85)
train_log = log_price.iloc[:split]
test_log  = log_price.iloc[split:]
n_test    = len(test_log)

# auto_arima: AIC 기준 최적 파라미터 자동 선택
print("auto_arima 파라미터 탐색 중...")
model = auto_arima(
    train_log, d=1, seasonal=False,
    information_criterion="aic",
    stepwise=True, suppress_warnings=True, error_action="ignore"
)
print(f"최적 파라미터: {model.order}")
print(model.summary())

# 예측 (95% 신뢰구간 포함)
forecast_log, conf_int = model.predict(n_periods=n_test, return_conf_int=True)

# 로그→원래 주가로 역변환
forecast_price = np.exp(forecast_log)
actual_price   = np.exp(test_log.values)
lower_price    = np.exp(conf_int[:, 0])
upper_price    = np.exp(conf_int[:, 1])

fig, ax = plt.subplots(figsize=(13, 6))
ax.plot(close.index[split-30:split], close.iloc[split-30:split],
        color="steelblue", label="실제 (훈련 끝부분)")
ax.plot(test_log.index, actual_price,   color="steelblue",
        label="실제 (테스트)", alpha=0.8)
ax.plot(test_log.index, forecast_price, color="orange",
        linestyle="--", label=f"ARIMA{model.order} 예측")
ax.fill_between(test_log.index, lower_price, upper_price,
                alpha=0.15, color="orange", label="95% 신뢰구간")
ax.set_title(f"auto_arima{model.order} – 주가 예측")
ax.set_ylabel("Price (USD)")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("auto_arima.png", dpi=150)
plt.show()

# 예측 정확도
rmse = np.sqrt(((forecast_price - actual_price)**2).mean())
mape = np.abs((forecast_price - actual_price) / actual_price).mean() * 100
print(f"\nRMSE: {rmse:.2f}  |  MAPE: {mape:.2f}%")
```

---

## 📝 과제 (17:00 – 18:00)

1. 삼성전자 주가에 `auto_arima`를 적용하고 최적 파라미터와 MAPE를 확인하세요.
2. GARCH 모델(`arch` 라이브러리)을 사용하여 변동성 예측을 구현해보세요.
3. ARIMA 예측 방향(상승/하락)의 정확도를 계산하고, 이를 매매 신호로 활용한 수익률을 측정하세요.

---

## ✅ 체크리스트

- [ ] ADF 검정으로 정상성 확인 완료
- [ ] ACF·PACF 플롯 생성 및 파라미터 결정 완료
- [ ] ARIMA 모델 적합 및 잔차 진단 완료
- [ ] `auto_arima`로 최적 파라미터 자동 탐색 성공
- [ ] 과제 제출

---

## 📚 참고자료

- [statsmodels ARIMA](https://www.statsmodels.org/stable/generated/statsmodels.tsa.arima.model.ARIMA.html)
- [pmdarima (auto_arima)](https://alkaline-ml.com/pmdarima/)
- [Investopedia – ARIMA](https://www.investopedia.com/terms/a/autoregressive-integrated-moving-average-arima.asp)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day145+arima
