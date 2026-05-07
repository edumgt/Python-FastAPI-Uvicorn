# Day 142 – 회귀 모델 (주가 예측)

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (고급)

---

## 🎯 학습 목표

- 선형 회귀·Ridge·Lasso로 다음날 수익률 예측
- Random Forest Regressor로 예측 성능 향상
- 회귀 모델 평가 지표(RMSE, MAE, R²) 이해
- 예측값을 활용한 매매 전략 수익률 비교

---

## 📖 이론 (08:00 – 10:00)

### 1. 회귀 vs 분류
| 구분 | 출력 | 예시 |
|------|------|------|
| **회귀** | 연속값 | 내일 수익률 = +1.2% |
| **분류** | 이산값 | 내일 상승=1, 하락=0 |

### 2. 주요 회귀 모델
```python
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

# 모델 비교
models = {
    "Linear": LinearRegression(),
    "Ridge":  Ridge(alpha=1.0),
    "Lasso":  Lasso(alpha=0.001),
    "RF":     RandomForestRegressor(n_estimators=200),
}
```

### 3. 평가 지표
```python
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

rmse = mean_squared_error(y_true, y_pred, squared=False)
mae  = mean_absolute_error(y_true, y_pred)
r2   = r2_score(y_true, y_pred)
```

> ⚠️ 금융 데이터에서 R² < 0.05인 경우가 많음 – 낮은 R²도 유의미한 알파를 내포할 수 있음

---

## 🧪 LAB 1 – 선형 회귀 모델 (10:00 – 12:00)

```python
# regression_linear.py
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

def build_reg_features(symbol: str = "AAPL", period: str = "5y") -> pd.DataFrame:
    df = yf.download(symbol, period=period, auto_adjust=True)[["Close","Volume"]]
    close, volume = df["Close"].squeeze(), df["Volume"].squeeze()

    feat = pd.DataFrame(index=df.index)
    for d in [1, 2, 3, 5]:
        feat[f"ret_{d}d"] = close.pct_change(d)
    for w in [5, 20]:
        feat[f"ma_ratio_{w}"] = close / close.rolling(w).mean() - 1
    delta = close.diff()
    gain, loss = delta.clip(lower=0), (-delta).clip(lower=0)
    feat["rsi14"] = 100 - 100 / (1 + gain.ewm(alpha=1/14,adjust=False).mean() /
                                       loss.ewm(alpha=1/14,adjust=False).mean())
    feat["vol_ratio"] = volume / volume.rolling(20).mean()

    # 타겟: 다음날 수익률
    feat["target"] = close.pct_change().shift(-1)
    return feat.dropna()

df = build_reg_features("AAPL")
features = [c for c in df.columns if c != "target"]
X, y = df[features], df["target"]

split = int(len(X) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]

models = {
    "LinearReg": LinearRegression(),
    "Ridge(1.0)": Ridge(alpha=1.0),
    "Lasso(1e-4)": Lasso(alpha=1e-4),
}

for name, model in models.items():
    pipe = Pipeline([("scaler", StandardScaler()), ("model", model)])
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    r2   = r2_score(y_test, y_pred)
    # 예측 방향 정확도
    dir_acc = (np.sign(y_pred) == np.sign(y_test)).mean()
    print(f"{name:15s}  RMSE={rmse:.5f}  R²={r2:.4f}  방향정확도={dir_acc:.4f}")
```

---

## 🧪 LAB 2 – Random Forest Regressor (13:00 – 15:00)

```python
# regression_rf.py
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

from regression_linear import build_reg_features

df = build_reg_features("AAPL", period="5y")
features = [c for c in df.columns if c != "target"]
X, y = df[features], df["target"]

split = int(len(X) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]

# Random Forest
rf = Pipeline([("scaler", StandardScaler()),
               ("model", RandomForestRegressor(n_estimators=300, max_depth=5,
                                               random_state=42, n_jobs=-1))])
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)

# Gradient Boosting
gb = Pipeline([("scaler", StandardScaler()),
               ("model", GradientBoostingRegressor(n_estimators=200, max_depth=3,
                                                    learning_rate=0.05, random_state=42))])
gb.fit(X_train, y_train)
y_pred_gb = gb.predict(X_test)

for name, y_pred in [("Random Forest", y_pred_rf), ("Gradient Boosting", y_pred_gb)]:
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    r2   = r2_score(y_test, y_pred)
    dir_acc = (np.sign(y_pred) == np.sign(y_test)).mean()
    print(f"{name:20s}  RMSE={rmse:.5f}  R²={r2:.4f}  방향정확도={dir_acc:.4f}")

# 예측 vs 실제 시각화
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 7))
dates = y_test.index

ax1.plot(dates, y_test.values*100,  label="실제",  lw=1.5, alpha=0.7)
ax1.plot(dates, y_pred_rf*100,      label="RF예측", lw=1.0, alpha=0.8)
ax1.set_title("Random Forest – 실제 vs 예측 수익률(%)")
ax1.set_ylabel("일간 수익률(%)")
ax1.legend()
ax1.grid(alpha=0.3)

ax2.scatter(y_test.values*100, y_pred_rf*100, alpha=0.3, s=10, color="steelblue")
ax2.axline((0,0), slope=1, color="red", ls="--", lw=0.8)
ax2.set_title("실제 vs 예측 산점도")
ax2.set_xlabel("실제 수익률(%)"); ax2.set_ylabel("예측 수익률(%)")
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("rf_regression.png", dpi=150)
plt.show()
```

---

## 🧪 LAB 3 – 예측 기반 매매 전략 (15:00 – 17:00)

```python
# regression_strategy.py
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from regression_linear import build_reg_features

df = build_reg_features("AAPL", period="5y")
features = [c for c in df.columns if c != "target"]
X, y = df[features], df["target"]

# 훈련: 앞 60% / 검증: 뒤 40% (예측 전략 시뮬레이션)
train_end = int(len(X) * 0.6)
X_train, y_train = X.iloc[:train_end], y.iloc[:train_end]
X_test,  y_test  = X.iloc[train_end:], y.iloc[train_end:]

pipe = Pipeline([("scaler", StandardScaler()),
                  ("model",  RandomForestRegressor(n_estimators=200, max_depth=5, random_state=42))])
pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)

# 전략: 예측 수익률 > 0 이면 매수 (1), 아니면 현금 (0)
signal = (y_pred > 0).astype(float)
actual = y_test.values

strategy_ret = actual * signal - np.abs(np.diff(np.concatenate([[0], signal]))) * 0.001
bh_ret       = actual

cum_str = (1 + strategy_ret).cumprod()
cum_bh  = (1 + bh_ret).cumprod()

n = len(strategy_ret)
cagr_str = (cum_str[-1]**(252/n)-1)*100
cagr_bh  = (cum_bh[-1] **(252/n)-1)*100
dir_acc  = (np.sign(y_pred) == np.sign(actual)).mean() * 100

print(f"방향 예측 정확도: {dir_acc:.2f}%")
print(f"전략 CAGR:        {cagr_str:.2f}%")
print(f"Buy & Hold CAGR:  {cagr_bh:.2f}%")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(y_test.index, cum_bh,  label=f"Buy&Hold ({cagr_bh:.1f}%)")
ax.plot(y_test.index, cum_str, label=f"RF전략 ({cagr_str:.1f}%)")
ax.set_title("RF 회귀 기반 매매 전략 vs Buy & Hold")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("rf_strategy.png", dpi=150)
plt.show()
```

---

## 📝 과제 (17:00 – 18:00)

1. 예측 대상을 "1일 수익률"에서 "5일 수익률"로 변경하고 방향 정확도를 비교하세요.
2. 특성에 섹터 모멘텀(섹터 ETF 수익률)을 추가하고 예측 성능 변화를 확인하세요.
3. 예측 확신도 임계값을 다르게 설정 (예측값 > 0.005일 때만 매수)하고 수익률을 비교하세요.

---

## ✅ 체크리스트

- [ ] 선형 회귀·Ridge·Lasso 모델 비교 완료
- [ ] Random Forest·Gradient Boosting 회귀 구현 성공
- [ ] 방향 정확도(Direction Accuracy) 계산 완료
- [ ] 예측 기반 매매 전략 수익률 계산 성공
- [ ] 과제 제출

---

## 📚 참고자료

- [sklearn Linear Models](https://scikit-learn.org/stable/modules/linear_model.html)
- [sklearn Random Forest](https://scikit-learn.org/stable/modules/ensemble.html#forests-of-randomized-trees)
- [Advances in Financial ML – Feature Engineering](https://www.mlfinlab.com)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day142+regression
