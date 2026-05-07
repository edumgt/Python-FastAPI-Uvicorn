# Day 146 – 딥러닝 기초 (TensorFlow/Keras 환경 구성)

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (고급)

---

## 🎯 학습 목표

- 신경망(Neural Network) 기본 구조 이해
- TensorFlow 2.x + Keras API로 간단한 NN 구성
- 금융 데이터용 배치 생성(Windowed Dataset) 이해
- Dense 레이어로 주가 방향 분류 모델 구현

---

## 📖 이론 (08:00 – 10:00)

### 1. 신경망 기본 구조
```
입력층 (특성) → 은닉층 (ReLU) → 출력층 (Sigmoid/Softmax)
```

### 2. Keras Sequential API
```python
from tensorflow import keras
from keras import layers

model = keras.Sequential([
    layers.Input(shape=(n_features,)),
    layers.Dense(64, activation="relu"),
    layers.Dropout(0.3),
    layers.Dense(32, activation="relu"),
    layers.Dropout(0.2),
    layers.Dense(1, activation="sigmoid"),  # 이진 분류
])

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy", keras.metrics.AUC(name="auc")]
)
```

### 3. 시계열 데이터 배치 (Windowed Dataset)
```python
# 슬라이딩 윈도우: 과거 N일 데이터 → 내일 예측
def create_sequences(X, y, window=20):
    Xs, ys = [], []
    for i in range(len(X) - window):
        Xs.append(X[i:i+window])
        ys.append(y[i+window])
    return np.array(Xs), np.array(ys)
```

---

## 🧪 LAB 1 – TensorFlow 환경 확인 & 간단한 NN (10:00 – 12:00)

```python
# dl_setup.py
import tensorflow as tf
from tensorflow import keras
from keras import layers
import numpy as np
import pandas as pd

print(f"TensorFlow 버전: {tf.__version__}")
print(f"GPU 사용 가능: {len(tf.config.list_physical_devices('GPU')) > 0}")

# XOR 문제로 NN 기초 확인
X_xor = np.array([[0,0],[0,1],[1,0],[1,1]], dtype=np.float32)
y_xor = np.array([0, 1, 1, 0],             dtype=np.float32)

model = keras.Sequential([
    layers.Dense(8, activation="relu", input_shape=(2,)),
    layers.Dense(1, activation="sigmoid"),
])
model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
model.fit(X_xor, y_xor, epochs=200, verbose=0)
print("\nXOR 예측:", model.predict(X_xor).round(2).flatten())

# 금융 분류용 NN 구조 정의
def build_classifier(n_features: int, units: list = [64, 32],
                      dropout: float = 0.3) -> keras.Model:
    inputs = keras.Input(shape=(n_features,))
    x = inputs
    for u in units:
        x = layers.Dense(u, activation="relu")(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(dropout)(x)
    output = layers.Dense(1, activation="sigmoid")(x)
    model = keras.Model(inputs, output)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="binary_crossentropy",
        metrics=["accuracy", keras.metrics.AUC(name="auc")]
    )
    return model

model = build_classifier(n_features=12)
model.summary()
```

---

## 🧪 LAB 2 – Dense NN으로 주가 방향 분류 (13:00 – 15:00)

```python
# dense_classifier.py
import yfinance as yf
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import layers, callbacks
import matplotlib.pyplot as plt
from classification import build_cls_features  # Day 143

df = build_cls_features("AAPL", period="5y")
features = [c for c in df.columns if c != "target"]
X_raw, y = df[features].values, df["target"].values

# 정규화
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
split = int(len(X_raw) * 0.8)
X_train_raw, X_test_raw = X_raw[:split], X_raw[split:]
y_train, y_test = y[:split], y[split:]
X_train = scaler.fit_transform(X_train_raw)
X_test  = scaler.transform(X_test_raw)

# 모델 구성
def build_model(n_features: int) -> keras.Model:
    inputs = keras.Input(shape=(n_features,))
    x = layers.Dense(128, activation="relu")(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(64, activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.2)(x)
    x = layers.Dense(32, activation="relu")(x)
    output = layers.Dense(1, activation="sigmoid")(x)
    model = keras.Model(inputs, output)
    model.compile(optimizer=keras.optimizers.Adam(1e-3),
                  loss="binary_crossentropy",
                  metrics=["accuracy", keras.metrics.AUC(name="auc")])
    return model

model = build_model(X_train.shape[1])

early_stop = callbacks.EarlyStopping(monitor="val_auc", patience=15,
                                      restore_best_weights=True, mode="max")
lr_sched   = callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5,
                                          patience=5, min_lr=1e-5)

history = model.fit(
    X_train, y_train,
    epochs=150, batch_size=64,
    validation_split=0.15,
    callbacks=[early_stop, lr_sched],
    class_weight={0: 1.0, 1: y_train.mean() / (1 - y_train.mean())},
    verbose=1
)

# 평가
from sklearn.metrics import roc_auc_score, accuracy_score
y_prob = model.predict(X_test).flatten()
y_pred = (y_prob >= 0.5).astype(int)
print(f"\nTest AUC: {roc_auc_score(y_test, y_prob):.4f}")
print(f"Test Acc: {accuracy_score(y_test, y_pred):.4f}")

# 학습 곡선
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.plot(history.history["loss"],     label="Train Loss")
ax1.plot(history.history["val_loss"], label="Val Loss")
ax1.set_title("Loss 학습 곡선"); ax1.legend(); ax1.grid(alpha=0.3)

ax2.plot(history.history["auc"],     label="Train AUC")
ax2.plot(history.history["val_auc"], label="Val AUC")
ax2.set_title("AUC 학습 곡선"); ax2.legend(); ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("dense_training.png", dpi=150)
plt.show()
```

---

## 🧪 LAB 3 – 슬라이딩 윈도우 데이터셋 준비 (15:00 – 17:00)

```python
# windowed_dataset.py
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler

df = yf.download("AAPL", period="5y", auto_adjust=True)[["Close"]]
close = df["Close"].squeeze().values.reshape(-1, 1)

scaler = MinMaxScaler()
close_scaled = scaler.fit_transform(close)

def create_sequences(data: np.ndarray, window: int = 20) -> tuple[np.ndarray, np.ndarray]:
    """슬라이딩 윈도우 – 시계열 입력/타겟 쌍 생성"""
    X, y = [], []
    for i in range(len(data) - window):
        X.append(data[i:i+window])       # 과거 window일
        y.append(data[i+window, 0])      # 다음날 종가
    return np.array(X), np.array(y)

X_seq, y_seq = create_sequences(close_scaled, window=20)
print(f"X_seq shape: {X_seq.shape}")  # (samples, 20, 1)
print(f"y_seq shape: {y_seq.shape}")

# 분류 타겟: 다음날 상승 여부
y_cls = (y_seq > np.roll(y_seq, 1))[1:]  # 전날 대비 상승=1
X_cls = X_seq[1:]

split = int(len(X_cls) * 0.8)
X_train, X_test = X_cls[:split], X_cls[split:]
y_train, y_test = y_cls[:split], y_cls[split:]

print(f"\n학습: {X_train.shape}  테스트: {X_test.shape}")
print(f"타겟 상승 비율: {y_train.mean()*100:.1f}%")
# → Day 147 LSTM에서 이 데이터를 사용
```

---

## 📝 과제 (17:00 – 18:00)

1. Dense NN 레이어 수(1개·3개·5개)에 따른 AUC 변화를 비교하세요.
2. `class_weight`를 조정하여 Recall(상승 탐지율)을 높이는 실험을 진행하세요.
3. `window=10·20·30`으로 슬라이딩 윈도우 크기를 변경하고 다음날 예측에 미치는 영향을 분석하세요.

---

## ✅ 체크리스트

- [ ] TensorFlow/Keras 환경 설치 및 버전 확인 완료
- [ ] Dense NN 분류 모델 구현 및 EarlyStopping 적용 성공
- [ ] 학습 곡선(Loss·AUC) 시각화 완료
- [ ] 슬라이딩 윈도우 데이터셋 생성 성공 (LSTM 준비)
- [ ] 과제 제출

---

## 📚 참고자료

- [TensorFlow 공식 튜토리얼](https://www.tensorflow.org/tutorials)
- [Keras 공식 문서](https://keras.io/guides/)
- [Deep Learning for Finance (O'Reilly)](https://www.oreilly.com/library/view/machine-learning-for/9781098115395/)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day146+dl+basics
