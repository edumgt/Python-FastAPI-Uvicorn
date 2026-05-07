# Day 147 – LSTM 구현 (시계열 주가 예측)

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (고급)

---

## 🎯 학습 목표

- LSTM(Long Short-Term Memory) 작동 원리 이해
- Keras로 LSTM 기반 주가 예측 모델 구현
- 예측 성능 평가 및 시각화
- 단변량·다변량 LSTM 비교

---

## 📖 이론 (08:00 – 10:00)

### 1. RNN vs LSTM
| 구분 | RNN | LSTM |
|------|-----|------|
| 장기 의존성 | 기울기 소실 문제 | Cell State로 해결 |
| 속도 | 빠름 | 상대적으로 느림 |
| 복잡도 | 낮음 | 높음 |

### 2. LSTM 게이트 구조
- **Forget Gate**: 이전 Cell State에서 버릴 정보 결정
- **Input Gate**: 새로운 정보를 Cell State에 저장
- **Output Gate**: Cell State를 기반으로 출력 생성

### 3. 입력 형태
```python
# LSTM 입력: (batch_size, timesteps, features)
# 예: (32, 20, 1) → 32샘플, 20일치, 1개 특성
X = X.reshape(X.shape[0], X.shape[1], 1)  # 단변량
# 다변량: (32, 20, n_features)
```

---

## 🧪 LAB 1 – 단변량 LSTM (종가만 사용) (10:00 – 12:00)

```python
# lstm_univariate.py
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow import keras
from keras import layers, callbacks
import matplotlib.pyplot as plt

# 데이터 준비
df = yf.download("AAPL", period="5y", auto_adjust=True)[["Close"]]
close = df["Close"].squeeze().values.reshape(-1, 1)

scaler = MinMaxScaler()
scaled = scaler.fit_transform(close)

WINDOW = 20
split  = int(len(scaled) * 0.8)

def make_sequences(data: np.ndarray, window: int):
    X, y = [], []
    for i in range(len(data) - window):
        X.append(data[i:i+window])
        y.append(data[i+window, 0])
    return np.array(X), np.array(y)

X, y = make_sequences(scaled, WINDOW)
X_train, y_train = X[:split], y[:split]
X_test,  y_test  = X[split:], y[split:]

# LSTM 모델
def build_lstm(window: int, features: int = 1) -> keras.Model:
    model = keras.Sequential([
        layers.LSTM(64, return_sequences=True, input_shape=(window, features)),
        layers.Dropout(0.2),
        layers.LSTM(32, return_sequences=False),
        layers.Dropout(0.2),
        layers.Dense(16, activation="relu"),
        layers.Dense(1),
    ])
    model.compile(optimizer="adam", loss="mse")
    return model

model = build_lstm(WINDOW)
model.summary()

cb = [callbacks.EarlyStopping(monitor="val_loss", patience=15, restore_best_weights=True),
      callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=5, min_lr=1e-5)]

history = model.fit(X_train, y_train, epochs=100, batch_size=32,
                    validation_split=0.15, callbacks=cb, verbose=1)

# 예측 및 역변환
y_pred_scaled = model.predict(X_test)
y_pred = scaler.inverse_transform(y_pred_scaled)
y_actual = scaler.inverse_transform(y_test.reshape(-1, 1))

rmse = mean_squared_error(y_actual, y_pred, squared=False)
mape = np.abs((y_pred - y_actual) / y_actual).mean() * 100
print(f"\nRMSE: {rmse:.2f}  |  MAPE: {mape:.2f}%")

# 시각화
dates = df.index[WINDOW + split:]
fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(dates, y_actual, label="실제 주가", color="steelblue", lw=1.5)
ax.plot(dates, y_pred,   label="LSTM 예측", color="orange",    lw=1.5, linestyle="--")
ax.set_title(f"LSTM 단변량 주가 예측 – RMSE:{rmse:.2f}  MAPE:{mape:.2f}%")
ax.set_ylabel("Price (USD)")
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("lstm_univariate.png", dpi=150)
plt.show()
```

---

## 🧪 LAB 2 – 다변량 LSTM (여러 기술적 지표 포함) (13:00 – 15:00)

```python
# lstm_multivariate.py
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow import keras
from keras import layers, callbacks
import matplotlib.pyplot as plt

df = yf.download("AAPL", period="5y", auto_adjust=True)[["Close","Volume"]]
close  = df["Close"].squeeze()
volume = df["Volume"].squeeze()

# 특성 준비
feat = pd.DataFrame(index=df.index)
feat["Close"]      = close
feat["Volume"]     = volume
feat["MA5_ratio"]  = close / close.rolling(5).mean() - 1
feat["MA20_ratio"] = close / close.rolling(20).mean() - 1
delta = close.diff()
gain, loss = delta.clip(lower=0), (-delta).clip(lower=0)
feat["RSI14"]  = 100 - 100/(1 + gain.ewm(alpha=1/14,adjust=False).mean() /
                                  loss.ewm(alpha=1/14,adjust=False).mean())
feat["BB_pct"] = (close - (close.rolling(20).mean() - 2*close.rolling(20).std())) / \
                  (4 * close.rolling(20).std())
feat = feat.dropna()

WINDOW = 20
split  = int(len(feat) * 0.8)

# 정규화 (각 특성 독립적으로)
scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()
X_all = scaler_X.fit_transform(feat.values)
y_all = scaler_y.fit_transform(feat[["Close"]].values)

def make_sequences(X, y, window):
    Xs, ys = [], []
    for i in range(len(X) - window):
        Xs.append(X[i:i+window])
        ys.append(y[i+window, 0])
    return np.array(Xs), np.array(ys)

X_seq, y_seq = make_sequences(X_all, y_all, WINDOW)
X_train, y_train = X_seq[:split], y_seq[:split]
X_test,  y_test  = X_seq[split:], y_seq[split:]

n_features = X_seq.shape[2]

model = keras.Sequential([
    layers.LSTM(128, return_sequences=True, input_shape=(WINDOW, n_features)),
    layers.Dropout(0.2),
    layers.LSTM(64, return_sequences=True),
    layers.Dropout(0.2),
    layers.LSTM(32),
    layers.Dense(16, activation="relu"),
    layers.Dense(1),
])
model.compile(optimizer="adam", loss="mse")

cb = [callbacks.EarlyStopping(monitor="val_loss", patience=15, restore_best_weights=True)]
model.fit(X_train, y_train, epochs=100, batch_size=32, validation_split=0.15,
          callbacks=cb, verbose=1)

y_pred_scaled = model.predict(X_test)
y_pred  = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1))
y_actual= scaler_y.inverse_transform(y_test.reshape(-1, 1))

rmse = mean_squared_error(y_actual, y_pred, squared=False)
mape = np.abs((y_pred - y_actual) / y_actual).mean() * 100
print(f"다변량 LSTM – RMSE:{rmse:.2f}  MAPE:{mape:.2f}%")

dates = feat.index[WINDOW + split:]
fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(dates, y_actual, label="실제", color="steelblue")
ax.plot(dates, y_pred,   label="LSTM 예측", color="orange", linestyle="--")
ax.set_title(f"다변량 LSTM – RMSE:{rmse:.2f}  MAPE:{mape:.2f}%")
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("lstm_multivariate.png", dpi=150)
plt.show()
```

---

## 🧪 LAB 3 – LSTM 방향 예측 전략 (15:00 – 17:00)

```python
# lstm_strategy.py
import numpy as np
import matplotlib.pyplot as plt

# lstm_univariate.py의 y_actual, y_pred 활용
# 예측값 방향 → 매매 신호
direction_pred   = np.sign(np.diff(y_pred.flatten()))    # 예측 방향
direction_actual = np.sign(np.diff(y_actual.flatten()))  # 실제 방향

dir_accuracy = (direction_pred == direction_actual).mean() * 100
print(f"방향 예측 정확도: {dir_accuracy:.2f}%")

# 매매 전략
signal = (direction_pred > 0).astype(float)  # 상승 예측 → 매수
actual_returns = np.diff(y_actual.flatten()) / y_actual.flatten()[:-1]
strategy_returns = actual_returns * signal
bh_returns       = actual_returns

cum_str = (1 + strategy_returns).cumprod()
cum_bh  = (1 + bh_returns).cumprod()

n = len(strategy_returns)
print(f"전략 CAGR: {(cum_str[-1]**(252/n)-1)*100:.2f}%")
print(f"B&H  CAGR: {(cum_bh[-1] **(252/n)-1)*100:.2f}%")

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(cum_bh,  label="Buy & Hold")
ax.plot(cum_str, label="LSTM 방향 전략")
ax.set_title("LSTM 예측 기반 매매 전략")
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("lstm_strategy.png", dpi=150)
plt.show()
```

---

## 📝 과제 (17:00 – 18:00)

1. LSTM 레이어를 1개·2개·3개로 변경하면서 MAPE 차이를 비교하세요.
2. 삼성전자(005930.KS) 데이터에 동일한 단변량 LSTM을 적용하고 MAPE를 확인하세요.
3. 예측 오차(RMSE)가 큰 구간의 특성(이벤트·뉴스·변동성)을 분석하세요.

---

## ✅ 체크리스트

- [ ] 단변량 LSTM 구현 및 예측 성공
- [ ] 다변량 LSTM (기술적 지표 포함) 구현 성공
- [ ] 단변량/다변량 RMSE·MAPE 비교 완료
- [ ] LSTM 방향 전략 수익률 계산 성공
- [ ] 과제 제출

---

## 📚 참고자료

- [Keras LSTM 가이드](https://keras.io/api/layers/recurrent_layers/lstm/)
- [Understanding LSTM – Colah's Blog](https://colah.github.io/posts/2015-08-Understanding-LSTMs/)
- [TensorFlow 시계열 예측 튜토리얼](https://www.tensorflow.org/tutorials/structured_data/time_series)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day147+lstm
