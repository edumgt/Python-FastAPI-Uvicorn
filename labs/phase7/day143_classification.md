# Day 143 – 분류 모델 (상승/하락 예측)

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (고급)

---

## 🎯 학습 목표

- Logistic Regression·Random Forest·XGBoost 분류 모델 구현
- 분류 성능 지표(Accuracy·Precision·Recall·F1·AUC) 이해
- 클래스 불균형 처리(class_weight, SMOTE)
- 확률 임계값 조정으로 매매 전략 최적화

---

## 📖 이론 (08:00 – 10:00)

### 1. 타겟 정의
```python
# 단순: 내일 상승=1, 하락=0
y = (close.shift(-1) > close).astype(int)

# 임계값: 0.5% 이상 상승만 매수 신호
y = (close.pct_change(-1) > 0.005).astype(int)
```

### 2. 분류 평가 지표
| 지표 | 공식 | 금융 관점 |
|------|------|-----------|
| Accuracy | 정답/전체 | 전체 예측 정확도 |
| Precision | TP/(TP+FP) | 매수 신호 중 실제 상승 비율 (허위신호 방지) |
| Recall | TP/(TP+FN) | 실제 상승 중 포착 비율 |
| AUC-ROC | 곡선 아래 면적 | 임계값 무관 종합 성능 |

### 3. XGBoost 특성
- Gradient Boosting 기반 앙상블
- 결측값 자동 처리
- 빠른 학습 속도, 높은 예측 성능
- 특성 중요도 제공

---

## 🧪 LAB 1 – 분류 모델 비교 (10:00 – 12:00)

```python
# classification.py
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (classification_report, roc_auc_score,
                              accuracy_score, confusion_matrix)
import matplotlib.pyplot as plt

def build_cls_features(symbol: str = "AAPL", period: str = "5y",
                        target_days: int = 1) -> pd.DataFrame:
    df = yf.download(symbol, period=period, auto_adjust=True)[["Close","Volume"]]
    close, volume = df["Close"].squeeze(), df["Volume"].squeeze()
    feat = pd.DataFrame(index=df.index)
    for d in [1,2,3,5,10]:
        feat[f"ret_{d}d"] = close.pct_change(d)
    for w in [5,20,60]:
        feat[f"ma_ratio_{w}"] = close / close.rolling(w).mean() - 1
    delta = close.diff()
    gain, loss = delta.clip(lower=0), (-delta).clip(lower=0)
    feat["rsi14"] = 100 - 100/(1 + gain.ewm(alpha=1/14,adjust=False).mean() /
                                     loss.ewm(alpha=1/14,adjust=False).mean())
    ema12 = close.ewm(span=12,adjust=False).mean()
    ema26 = close.ewm(span=26,adjust=False).mean()
    macd  = ema12 - ema26
    feat["macd_hist"] = macd - macd.ewm(span=9,adjust=False).mean()
    bb_mid = close.rolling(20).mean()
    feat["pct_b"]     = (close - (bb_mid - 2*close.rolling(20).std())) / (4*close.rolling(20).std())
    feat["vol_ratio"] = volume / volume.rolling(20).mean()
    feat["target"]    = (close.shift(-target_days) > close).astype(int)
    return feat.dropna()

df = build_cls_features("AAPL")
features = [c for c in df.columns if c != "target"]
X, y = df[features], df["target"]

split = int(len(X) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]

models = {
    "Logistic": Pipeline([("sc", StandardScaler()),
                           ("m", LogisticRegression(class_weight="balanced", max_iter=1000))]),
    "RandomForest": Pipeline([("sc", StandardScaler()),
                               ("m", RandomForestClassifier(n_estimators=300, max_depth=5,
                                                             class_weight="balanced", random_state=42))]),
    "XGBoost": Pipeline([("sc", StandardScaler()),
                          ("m", XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.05,
                                               scale_pos_weight=1, random_state=42,
                                               eval_metric="logloss", verbosity=0))]),
}

print(f"클래스 분포: 상승={y_test.mean()*100:.1f}%  하락={(1-y_test.mean())*100:.1f}%\n")
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    print(f"=== {name} ===")
    print(f"  Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(f"  AUC-ROC:  {roc_auc_score(y_test, y_prob):.4f}")
    print(classification_report(y_test, y_pred, target_names=["하락","상승"]))
```

---

## 🧪 LAB 2 – ROC 곡선 & 임계값 조정 (13:00 – 15:00)

```python
# threshold_tuning.py
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, precision_recall_curve
import matplotlib.pyplot as plt
from xgboost import XGBClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from classification import build_cls_features

df = build_cls_features("AAPL")
features = [c for c in df.columns if c != "target"]
X, y = df[features], df["target"]
split = int(len(X) * 0.8)

model = Pipeline([("sc", StandardScaler()),
                   ("m", XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.05,
                                        random_state=42, eval_metric="logloss", verbosity=0))])
model.fit(X.iloc[:split], y.iloc[:split])
y_prob = model.predict_proba(X.iloc[split:])[:, 1]
y_test = y.iloc[split:]

# ROC 곡선
fpr, tpr, thresholds_roc = roc_curve(y_test, y_prob)

# 임계값에 따른 Precision/Recall
precisions, recalls, thresholds_pr = precision_recall_curve(y_test, y_prob)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].plot(fpr, tpr, color="blue", lw=1.5, label="ROC Curve")
axes[0].plot([0,1],[0,1], "r--", lw=0.8)
axes[0].set_title("ROC Curve")
axes[0].set_xlabel("False Positive Rate"); axes[0].set_ylabel("True Positive Rate")
axes[0].legend(); axes[0].grid(alpha=0.3)

axes[1].plot(thresholds_pr, precisions[:-1], label="Precision")
axes[1].plot(thresholds_pr, recalls[:-1],    label="Recall")
axes[1].axvline(x=0.5, color="gray", ls="--", lw=0.8, label="threshold=0.5")
axes[1].set_title("임계값 vs Precision/Recall")
axes[1].set_xlabel("Threshold")
axes[1].legend(); axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig("roc_threshold.png", dpi=150)
plt.show()

# 최적 임계값 탐색 (Precision 우선: 허위 매수 신호 최소화)
best_thr = thresholds_pr[np.argmax(precisions[:-1] * (precisions[:-1] > 0.55))] \
           if np.any(precisions[:-1] > 0.55) else 0.5
print(f"Precision>55% 유지하는 최적 임계값: {best_thr:.3f}")
y_pred_tuned = (y_prob >= best_thr).astype(int)
print(f"  예측 매수 신호 수: {y_pred_tuned.sum()} / {len(y_pred_tuned)}")
```

---

## 🧪 LAB 3 – XGBoost 전략 수익률 계산 (15:00 – 17:00)

```python
# xgb_strategy.py
import yfinance as yf
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from classification import build_cls_features

df = build_cls_features("AAPL", period="5y")
features = [c for c in df.columns if c != "target"]
X, y = df[features], df["target"]

close = yf.download("AAPL", period="5y", auto_adjust=True)["Close"].squeeze().loc[X.index]

split = int(len(X) * 0.7)
train_end, test_start = split, split

model = Pipeline([("sc", StandardScaler()),
                   ("m", XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.05,
                                        random_state=42, eval_metric="logloss", verbosity=0))])
model.fit(X.iloc[:train_end], y.iloc[:train_end])
y_prob = model.predict_proba(X.iloc[test_start:])[:, 1]

# 임계값 0.55 이상일 때만 매수
threshold = 0.55
signal = (y_prob >= threshold).astype(float)

daily = close.pct_change().iloc[test_start:]
daily = daily.reindex(X.iloc[test_start:].index)
trade  = np.abs(np.diff(np.concatenate([[0], signal])))
ret    = daily.values * signal - trade * 0.001

cum_str = (1 + ret).cumprod()
cum_bh  = (1 + daily.values).cumprod()

n = len(ret)
print(f"전략 CAGR: {(cum_str[-1]**(252/n)-1)*100:.2f}%")
print(f"B&H  CAGR: {(cum_bh[-1] **(252/n)-1)*100:.2f}%")
print(f"매수 신호 비율: {signal.mean()*100:.1f}%")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(12,5))
ax.plot(X.iloc[test_start:].index, cum_bh,  label="Buy & Hold")
ax.plot(X.iloc[test_start:].index, cum_str, label=f"XGB 전략 (thr={threshold})")
ax.set_title("XGBoost 분류 전략 vs Buy & Hold")
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("xgb_strategy.png", dpi=150)
plt.show()
```

---

## 📝 과제 (17:00 – 18:00)

1. 타겟을 "3일 후 2% 이상 상승"으로 바꾸고 XGBoost 모델의 AUC를 확인하세요.
2. SMOTE (`imblearn`)를 적용하여 클래스 불균형을 처리하고 Recall 변화를 비교하세요.
3. 여러 임계값(0.45~0.65, 0.05 간격)을 적용하며 수익률·거래횟수·Precision을 표로 비교하세요.

---

## ✅ 체크리스트

- [ ] Logistic·RF·XGBoost 분류 모델 비교 완료
- [ ] ROC 곡선 시각화 완료
- [ ] 임계값 조정으로 Precision 개선 성공
- [ ] XGBoost 전략 수익률 vs Buy & Hold 비교 완료
- [ ] 과제 제출

---

## 📚 참고자료

- [XGBoost 공식 문서](https://xgboost.readthedocs.io)
- [sklearn ROC Curve](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_curve.html)
- [imbalanced-learn (SMOTE)](https://imbalanced-learn.org)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day143+classification
