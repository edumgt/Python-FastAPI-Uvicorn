# Day 141 – 머신러닝 기초 (scikit-learn 파이프라인)

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (고급)

---

## 🎯 학습 목표

- 금융 데이터를 ML 입력 형태로 변환 (특성 엔지니어링)
- scikit-learn 파이프라인 구성
- 훈련/검증/테스트 데이터 분리 (시계열 방식)
- 기본 모델로 예측 성능 베이스라인 설정

---

## 📖 이론 (08:00 – 10:00)

### 1. 금융 ML의 특수성
- **시계열 데이터**: 랜덤 셔플 금지, 시간 순서 유지
- **특성 누출(leakage)**: 미래 정보가 특성에 포함되지 않도록 주의
- **비정상성**: 주가 자체보다 수익률·지표를 특성으로 사용
- **클래스 불균형**: 상승/하락 비율이 비슷하지 않을 수 있음

### 2. 특성 엔지니어링
```python
# 사용 가능한 특성 예시
features = [
    "Return_1d",    # 1일 수익률
    "Return_5d",    # 5일 수익률
    "RSI14",        # RSI
    "MACD_Hist",    # MACD 히스토그램
    "%B",           # 볼린저밴드 %B
    "ATR14",        # ATR (변동성)
    "Vol_ratio",    # 거래량 / 20일 평균 거래량
    "MA_ratio",     # Close / MA20 비율
]
```

### 3. 시계열 데이터 분리
```python
# 랜덤 분리 (금지!)
# X_train, X_test = train_test_split(X, test_size=0.2)

# 시계열 분리 (올바른 방법)
split = int(len(X) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]
```

---

## 🧪 LAB 1 – 특성 엔지니어링 (10:00 – 12:00)

```python
# feature_engineering.py
import yfinance as yf
import pandas as pd
import numpy as np

def build_features(symbol: str, period: str = "5y") -> pd.DataFrame:
    df = yf.download(symbol, period=period, auto_adjust=True)
    df = df[["Open","High","Low","Close","Volume"]].copy()
    close  = df["Close"].squeeze()
    volume = df["Volume"].squeeze()
    high   = df["High"].squeeze()
    low    = df["Low"].squeeze()

    feat = pd.DataFrame(index=df.index)

    # 수익률 특성
    for d in [1, 2, 3, 5, 10, 20]:
        feat[f"ret_{d}d"] = close.pct_change(d)

    # MA 비율
    for w in [5, 20, 60]:
        ma = close.rolling(w).mean()
        feat[f"ma_ratio_{w}"] = close / ma - 1

    # RSI
    delta = close.diff()
    gain, loss = delta.clip(lower=0), (-delta).clip(lower=0)
    feat["rsi14"] = 100 - 100 / (1 + gain.ewm(alpha=1/14,adjust=False).mean() /
                                       loss.ewm(alpha=1/14,adjust=False).mean())

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd  = ema12 - ema26
    feat["macd_hist"] = macd - macd.ewm(span=9, adjust=False).mean()

    # 볼린저밴드 %B
    bb_mid = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    feat["pct_b"] = (close - (bb_mid - 2*bb_std)) / (4 * bb_std)

    # ATR
    prev_close = close.shift(1)
    tr = pd.concat([high-low, (high-prev_close).abs(), (low-prev_close).abs()], axis=1).max(axis=1)
    feat["atr_ratio"] = tr.ewm(alpha=1/14,adjust=False).mean() / close

    # 거래량 비율
    feat["vol_ratio"] = volume / volume.rolling(20).mean()

    # 타겟: 내일 수익률 방향 (1=상승, 0=하락)
    feat["target"] = (close.shift(-1) > close).astype(int)

    return feat.dropna()

df = build_features("AAPL")
print(f"특성 수: {df.shape[1]-1}개  |  샘플 수: {len(df)}")
print(f"상승 비율: {df['target'].mean()*100:.1f}%")
print(df.head(3).round(4))
```

---

## 🧪 LAB 2 – scikit-learn 파이프라인 구성 (13:00 – 15:00)

```python
# sklearn_pipeline.py
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score

# 특성 준비 (위 LAB에서 build_features 가져오기)
from feature_engineering import build_features

df = build_features("AAPL", period="5y")
features = [c for c in df.columns if c != "target"]
X, y = df[features], df["target"]

# 시계열 분리
split = int(len(X) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]

# 파이프라인 1: Logistic Regression
pipe_lr = Pipeline([
    ("scaler", StandardScaler()),
    ("model",  LogisticRegression(max_iter=1000, random_state=42)),
])
pipe_lr.fit(X_train, y_train)
y_pred_lr = pipe_lr.predict(X_test)

# 파이프라인 2: Decision Tree
pipe_dt = Pipeline([
    ("scaler", StandardScaler()),
    ("model",  DecisionTreeClassifier(max_depth=5, random_state=42)),
])
pipe_dt.fit(X_train, y_train)
y_pred_dt = pipe_dt.predict(X_test)

# 결과 비교
for name, y_pred in [("Logistic Regression", y_pred_lr), ("Decision Tree", y_pred_dt)]:
    print(f"\n=== {name} ===")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(f"ROC-AUC:  {roc_auc_score(y_test, y_pred):.4f}")
    print(classification_report(y_test, y_pred, target_names=["하락","상승"]))
```

---

## 🧪 LAB 3 – 특성 중요도 분석 (15:00 – 17:00)

```python
# feature_importance.py
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import pandas as pd

from feature_engineering import build_features

df = build_features("AAPL", period="5y")
features = [c for c in df.columns if c != "target"]
X, y = df[features], df["target"]

split = int(len(X) * 0.8)
X_train, y_train = X.iloc[:split], y.iloc[:split]
X_test,  y_test  = X.iloc[split:], y.iloc[split:]

# Random Forest (특성 중요도 분석에 유용)
pipe = Pipeline([("scaler", StandardScaler()),
                  ("model", RandomForestClassifier(n_estimators=200, max_depth=6,
                                                   random_state=42))])
pipe.fit(X_train, y_train)

importances = pd.Series(pipe.named_steps["model"].feature_importances_,
                         index=features).sort_values(ascending=False)

print("=== 특성 중요도 (상위 10) ===")
print(importances.head(10).round(4))

# 시각화
fig, ax = plt.subplots(figsize=(10, 6))
importances.head(15).plot(kind="barh", ax=ax, color="steelblue")
ax.set_title("Random Forest 특성 중요도 (Top 15)")
ax.set_xlabel("Importance")
ax.invert_yaxis()
ax.grid(alpha=0.3, axis="x")
plt.tight_layout()
plt.savefig("feature_importance.png", dpi=150)
plt.show()
```

---

## 📝 과제 (17:00 – 18:00)

1. 특성에 "요일 더미 변수"(월~금)를 추가하고 특성 중요도가 어떻게 바뀌는지 확인하세요.
2. 타겟을 "5일 후 수익률 방향"으로 바꾸고 동일한 파이프라인을 실행하세요.
3. 삼성전자 데이터에 동일한 파이프라인을 적용하고 AAPL과 정확도를 비교하세요.

---

## ✅ 체크리스트

- [ ] 금융 특성 15개 이상 생성 성공
- [ ] 시계열 방식 훈련/테스트 분리 적용
- [ ] `sklearn.Pipeline`으로 전처리 + 모델 연결 성공
- [ ] Random Forest 특성 중요도 시각화 완료
- [ ] 과제 제출

---

## 📚 참고자료

- [scikit-learn Pipeline](https://scikit-learn.org/stable/modules/compose.html)
- [sklearn.model_selection.TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)
- [Advances in Financial Machine Learning – Marcos López de Prado](https://www.amazon.com/Advances-Financial-Machine-Learning-Marcos/dp/1119482089)
