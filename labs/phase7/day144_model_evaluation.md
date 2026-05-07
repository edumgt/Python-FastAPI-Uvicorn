# Day 144 – 모델 평가 (교차검증·과적합 진단)

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (고급)

---

## 🎯 학습 목표

- 시계열 교차검증(`TimeSeriesSplit`) 구현
- 학습 곡선으로 과적합·과소적합 진단
- 혼동행렬 시각화 및 분류 리포트 해석
- 정규화(Ridge·L1)로 과적합 완화

---

## 📖 이론 (08:00 – 10:00)

### 1. 시계열 교차검증
```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)
for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
    # 모델 학습 및 평가
```

### 2. 과적합 진단
- **훈련 정확도 ≫ 검증 정확도**: 과적합
- **훈련 정확도 ≈ 검증 정확도 (낮은 값)**: 과소적합
- 학습 곡선: 샘플 수 증가에 따른 성능 변화 확인

### 3. 정규화 방법
| 방법 | 효과 |
|------|------|
| L2(Ridge) | 계수를 0에 가깝게 축소 |
| L1(Lasso) | 일부 계수를 0으로 만들어 특성 선택 효과 |
| ElasticNet | L1+L2 결합 |
| RF max_depth | 트리 깊이 제한 |
| XGB early_stopping | 검증 성능 악화 시 조기 중단 |

---

## 🧪 LAB 1 – TimeSeriesSplit 교차검증 (10:00 – 12:00)

```python
# timeseries_cv.py
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score
from classification import build_cls_features  # Day 143 모듈

df = build_cls_features("AAPL", period="5y")
features = [c for c in df.columns if c != "target"]
X, y = df[features], df["target"]

tscv = TimeSeriesSplit(n_splits=5, gap=1)  # gap=1: 신호 다음날 진입

model = Pipeline([
    ("sc", StandardScaler()),
    ("m",  RandomForestClassifier(n_estimators=200, max_depth=5,
                                   class_weight="balanced", random_state=42)),
])

fold_results = []
for fold, (train_idx, val_idx) in enumerate(tscv.split(X), 1):
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
    model.fit(X_train, y_train)
    y_prob = model.predict_proba(X_val)[:, 1]
    y_pred = model.predict(X_val)
    auc  = roc_auc_score(y_val, y_prob)
    acc  = (y_pred == y_val).mean()
    fold_results.append({"Fold":fold, "Train size":len(train_idx),
                          "Val size":len(val_idx), "AUC":round(auc,4), "Acc":round(acc,4)})
    print(f"Fold {fold}: AUC={auc:.4f}  Acc={acc:.4f}  "
          f"Train:{len(train_idx)}  Val:{len(val_idx)}")

df_res = pd.DataFrame(fold_results)
print(f"\n평균 AUC: {df_res['AUC'].mean():.4f} ± {df_res['AUC'].std():.4f}")
print(f"평균 Acc: {df_res['Acc'].mean():.4f} ± {df_res['Acc'].std():.4f}")
```

---

## 🧪 LAB 2 – 학습 곡선 (과적합 진단) (13:00 – 15:00)

```python
# learning_curve.py
import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit, learning_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import make_scorer, roc_auc_score
import matplotlib.pyplot as plt
from classification import build_cls_features

df = build_cls_features("AAPL", period="5y")
features = [c for c in df.columns if c != "target"]
X, y = df[features], df["target"]

models_to_compare = {
    "RF(depth=3)": RandomForestClassifier(n_estimators=100, max_depth=3, random_state=42),
    "RF(depth=10)": RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
    "RF(depth=None)": RandomForestClassifier(n_estimators=100, max_depth=None, random_state=42),
}

fig, axes = plt.subplots(1, 3, figsize=(17, 5))
tscv = TimeSeriesSplit(n_splits=5)
scorer = make_scorer(roc_auc_score, needs_proba=True)

for ax, (name, base_model) in zip(axes, models_to_compare.items()):
    model = Pipeline([("sc", StandardScaler()), ("m", base_model)])
    train_sizes, train_scores, val_scores = learning_curve(
        model, X, y, cv=tscv, scoring=scorer,
        train_sizes=np.linspace(0.3, 1.0, 8), n_jobs=-1
    )
    train_mean = train_scores.mean(axis=1)
    val_mean   = val_scores.mean(axis=1)
    train_std  = train_scores.std(axis=1)
    val_std    = val_scores.std(axis=1)

    ax.plot(train_sizes, train_mean, label="Train AUC", color="blue")
    ax.fill_between(train_sizes, train_mean-train_std, train_mean+train_std, alpha=0.1, color="blue")
    ax.plot(train_sizes, val_mean, label="Val AUC", color="orange")
    ax.fill_between(train_sizes, val_mean-val_std, val_mean+val_std, alpha=0.1, color="orange")
    ax.set_title(name)
    ax.set_xlabel("학습 데이터 크기")
    ax.set_ylabel("AUC-ROC")
    ax.legend(fontsize=8)
    ax.set_ylim(0.4, 0.8)
    ax.grid(alpha=0.3)

plt.suptitle("학습 곡선 비교 (과적합 진단)", fontsize=13)
plt.tight_layout()
plt.savefig("learning_curves.png", dpi=150)
plt.show()
```

---

## 🧪 LAB 3 – 혼동행렬 시각화 & 종합 리포트 (15:00 – 17:00)

```python
# confusion_matrix_viz.py
import numpy as np
import pandas as pd
from sklearn.metrics import (confusion_matrix, ConfusionMatrixDisplay,
                              classification_report, roc_auc_score)
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from classification import build_cls_features

df = build_cls_features("AAPL", period="5y")
features = [c for c in df.columns if c != "target"]
X, y = df[features], df["target"]
split = int(len(X) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]

models = {
    "Random Forest": Pipeline([("sc", StandardScaler()),
                                ("m", RandomForestClassifier(n_estimators=200, max_depth=5,
                                                             class_weight="balanced", random_state=42))]),
    "XGBoost": Pipeline([("sc", StandardScaler()),
                          ("m", XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.05,
                                               random_state=42, eval_metric="logloss", verbosity=0))]),
}

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
report_rows = []

for ax, (name, model) in zip(axes, models.items()):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(cm, display_labels=["하락","상승"])
    disp.plot(ax=ax, colorbar=False)
    auc = roc_auc_score(y_test, y_prob)
    ax.set_title(f"{name}\nAUC={auc:.4f}")

    report = classification_report(y_test, y_pred, output_dict=True)
    report_rows.append({"Model":name, "AUC":round(auc,4),
                         "Acc":round(report["accuracy"],4),
                         "Prec(상승)":round(report["1"]["precision"],4),
                         "Rec(상승)":round(report["1"]["recall"],4),
                         "F1(상승)":round(report["1"]["f1-score"],4)})

plt.tight_layout()
plt.savefig("confusion_matrices.png", dpi=150)
plt.show()

print("\n=== 모델 성능 요약 ===")
print(pd.DataFrame(report_rows).to_string(index=False))
```

---

## 📝 과제 (17:00 – 18:00)

1. `TimeSeriesSplit(n_splits=10)`으로 교차검증하고, 각 폴드의 AUC를 시간순으로 시각화하세요 (시간에 따른 성능 변화 확인).
2. XGBoost에 `early_stopping_rounds=20`을 적용하고 최적 트리 수를 확인하세요.
3. 혼동행렬에서 "거짓 매수 신호(FP)"가 많을 때와 "놓친 상승(FN)"이 많을 때 각각 수익률에 미치는 영향을 분석하세요.

---

## ✅ 체크리스트

- [ ] `TimeSeriesSplit` 교차검증 구현 성공
- [ ] 학습 곡선으로 과적합 진단 완료
- [ ] 혼동행렬 시각화 완료
- [ ] 모델 성능 종합 비교표 작성 완료
- [ ] 과제 제출

---

## 📚 참고자료

- [sklearn TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)
- [sklearn Learning Curve](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.learning_curve.html)
- [sklearn Confusion Matrix](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day144+model+evaluation
