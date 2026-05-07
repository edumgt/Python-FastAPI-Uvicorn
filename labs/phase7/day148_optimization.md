# Day 148 – 전략 최적화 (Optuna & 하이퍼파라미터 튜닝)

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (고급)

---

## 🎯 학습 목표

- `Optuna` 라이브러리로 ML 하이퍼파라미터 자동 최적화
- 베이지안 최적화(TPE) vs 그리드 서치 비교
- 특성 선택(RFE, Permutation Importance) 적용
- Pruning(조기 중단)으로 효율적인 탐색

---

## 📖 이론 (08:00 – 10:00)

### 1. 하이퍼파라미터 튜닝 방법
| 방법 | 설명 | 효율성 |
|------|------|--------|
| 그리드 서치 | 모든 조합 탐색 | 낮음 (조합 수 지수적 증가) |
| 랜덤 서치 | 무작위 샘플링 | 중간 |
| 베이지안 최적화 | 과거 결과로 다음 탐색점 결정 | 높음 |
| Optuna (TPE) | 베이지안 + 조기 중단 | 매우 높음 |

### 2. Optuna 기본 구조
```python
import optuna

def objective(trial):
    # 탐색 공간 정의
    n_estimators = trial.suggest_int("n_estimators", 50, 500)
    max_depth    = trial.suggest_int("max_depth", 2, 10)
    lr           = trial.suggest_float("lr", 1e-4, 1e-1, log=True)
    # 모델 학습 및 평가
    return auc_score   # 최대화

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=50)
print(study.best_params)
```

---

## 🧪 LAB 1 – XGBoost 하이퍼파라미터 Optuna 최적화 (10:00 – 12:00)

```python
# optuna_xgb.py
import yfinance as yf
import pandas as pd
import numpy as np
import optuna
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from classification import build_cls_features  # Day 143

optuna.logging.set_verbosity(optuna.logging.WARNING)

df = build_cls_features("AAPL", period="5y")
features = [c for c in df.columns if c != "target"]
X, y = df[features], df["target"]

split = int(len(X) * 0.8)
X_train, y_train = X.iloc[:split], y.iloc[:split]
X_test,  y_test  = X.iloc[split:], y.iloc[split:]

tscv = TimeSeriesSplit(n_splits=5)

def objective(trial: optuna.Trial) -> float:
    params = {
        "n_estimators":    trial.suggest_int("n_estimators", 50, 500),
        "max_depth":       trial.suggest_int("max_depth", 2, 8),
        "learning_rate":   trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
        "subsample":       trial.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree":trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "min_child_weight":trial.suggest_int("min_child_weight", 1, 10),
        "random_state": 42, "eval_metric": "logloss", "verbosity": 0,
    }
    scores = []
    for train_idx, val_idx in tscv.split(X_train):
        Xtr, Xvl = X_train.iloc[train_idx], X_train.iloc[val_idx]
        ytr, yvl = y_train.iloc[train_idx], y_train.iloc[val_idx]
        scaler = StandardScaler()
        Xtr_s  = scaler.fit_transform(Xtr)
        Xvl_s  = scaler.transform(Xvl)
        model  = XGBClassifier(**params)
        model.fit(Xtr_s, ytr)
        prob = model.predict_proba(Xvl_s)[:, 1]
        scores.append(roc_auc_score(yvl, prob))
    return np.mean(scores)

study = optuna.create_study(direction="maximize",
                             sampler=optuna.samplers.TPESampler(seed=42))
study.optimize(objective, n_trials=50, show_progress_bar=True)

print(f"\n최적 AUC (CV): {study.best_value:.4f}")
print(f"최적 파라미터: {study.best_params}")

# 최적 파라미터로 테스트 세트 평가
best_model = XGBClassifier(**study.best_params, random_state=42,
                            eval_metric="logloss", verbosity=0)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)
best_model.fit(X_train_s, y_train)
y_prob = best_model.predict_proba(X_test_s)[:, 1]
print(f"테스트 AUC: {roc_auc_score(y_test, y_prob):.4f}")
```

---

## 🧪 LAB 2 – Optuna 시각화 & 파라미터 중요도 (13:00 – 15:00)

```python
# optuna_viz.py
import optuna
import matplotlib.pyplot as plt

# LAB 1의 study 객체 재사용 (또는 다시 실행)
# from optuna_xgb import study  # 동일 세션이라면 재사용 가능

# Optuna 내장 시각화 (matplotlib 기반)
try:
    from optuna.visualization.matplotlib import (
        plot_optimization_history, plot_param_importances,
        plot_contour, plot_slice
    )
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 최적화 이력
    ax1 = axes[0, 0]
    ax1.plot([t.value for t in study.trials], marker="o", ms=3, lw=1)
    ax1.axhline(study.best_value, color="red", ls="--", lw=0.8)
    ax1.set_title("Optuna 최적화 이력")
    ax1.set_xlabel("Trial"); ax1.set_ylabel("AUC")
    ax1.grid(alpha=0.3)

    # 파라미터 중요도 (FAnova 기반)
    importance = optuna.importance.get_param_importances(study)
    ax2 = axes[0, 1]
    names  = list(importance.keys())[:8]
    values = [importance[n] for n in names]
    ax2.barh(names[::-1], values[::-1], color="steelblue")
    ax2.set_title("파라미터 중요도 (Optuna)")
    ax2.grid(alpha=0.3, axis="x")

    # 학습률 vs AUC 산점도
    ax3 = axes[1, 0]
    lrs  = [t.params.get("learning_rate", None) for t in study.trials if t.value]
    vals = [t.value for t in study.trials if t.value]
    ax3.scatter(lrs, vals, alpha=0.5, s=20)
    ax3.set_xscale("log"); ax3.set_xlabel("learning_rate"); ax3.set_ylabel("AUC")
    ax3.set_title("learning_rate vs AUC")
    ax3.grid(alpha=0.3)

    # max_depth vs AUC
    ax4 = axes[1, 1]
    depths = [t.params.get("max_depth", None) for t in study.trials if t.value]
    ax4.scatter(depths, vals, alpha=0.5, s=20, color="orange")
    ax4.set_xlabel("max_depth"); ax4.set_ylabel("AUC")
    ax4.set_title("max_depth vs AUC")
    ax4.grid(alpha=0.3)

    plt.suptitle("Optuna 하이퍼파라미터 최적화 분석", fontsize=13)
    plt.tight_layout()
    plt.savefig("optuna_analysis.png", dpi=150)
    plt.show()

except Exception as e:
    print(f"시각화 오류: {e}")
    print("Optuna 웹 대시보드: optuna.create_study().dashboard()")
```

---

## 🧪 LAB 3 – 특성 선택 (Permutation Importance) (15:00 – 17:00)

```python
# feature_selection.py
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.inspection import permutation_importance
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
from classification import build_cls_features

df = build_cls_features("AAPL", period="5y")
features = [c for c in df.columns if c != "target"]
X, y = df[features], df["target"]
split = int(len(X) * 0.8)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X.iloc[:split])
X_test_s  = scaler.transform(X.iloc[split:])
y_train, y_test = y.iloc[:split].values, y.iloc[split:].values

model = RandomForestClassifier(n_estimators=200, max_depth=5,
                                class_weight="balanced", random_state=42)
model.fit(X_train_s, y_train)

# Permutation Importance (테스트 세트 기준)
perm = permutation_importance(model, X_test_s, y_test,
                               n_repeats=10, random_state=42, scoring="roc_auc")
imp_df = pd.DataFrame({"feature": features,
                         "importance": perm.importances_mean,
                         "std": perm.importances_std}).sort_values("importance", ascending=False)

print("=== Permutation Importance (Top 10) ===")
print(imp_df.head(10).to_string(index=False))

# 중요도 낮은 특성 제거
threshold = 0.0
selected = imp_df[imp_df["importance"] > threshold]["feature"].tolist()
print(f"\n선택된 특성 수: {len(selected)} / {len(features)}")

# 선택된 특성만으로 재학습
X_sel_train = X_train_s[:, [features.index(f) for f in selected]]
X_sel_test  = X_test_s[:, [features.index(f) for f in selected]]
model_sel   = RandomForestClassifier(n_estimators=200, max_depth=5,
                                      class_weight="balanced", random_state=42)
model_sel.fit(X_sel_train, y_train)

from sklearn.metrics import roc_auc_score
full_auc = roc_auc_score(y_test, model.predict_proba(X_test_s)[:, 1])
sel_auc  = roc_auc_score(y_test, model_sel.predict_proba(X_sel_test)[:, 1])
print(f"\n전체 특성 AUC:    {full_auc:.4f}")
print(f"선택 특성 AUC:    {sel_auc:.4f}")

# 시각화
fig, ax = plt.subplots(figsize=(10, 6))
imp_df.head(15).plot(kind="barh", x="feature", y="importance",
                      xerr="std", ax=ax, color="steelblue", legend=False)
ax.set_title("Permutation Importance (상위 15 특성)")
ax.set_xlabel("AUC 감소량")
ax.invert_yaxis()
ax.grid(alpha=0.3, axis="x")
plt.tight_layout()
plt.savefig("permutation_importance.png", dpi=150)
plt.show()
```

---

## 📝 과제 (17:00 – 18:00)

1. LSTM 모델의 하이퍼파라미터(units, dropout, learning_rate, window_size)를 Optuna로 최적화하세요.
2. 최적 파라미터와 기본 파라미터의 테스트 성능 차이를 비교하세요.
3. 중요도가 낮은 특성을 제거한 모델과 전체 특성 모델의 수익률을 비교하세요.

---

## ✅ 체크리스트

- [ ] Optuna로 XGBoost 하이퍼파라미터 최적화 성공
- [ ] Optuna 최적화 이력 및 파라미터 중요도 시각화 완료
- [ ] Permutation Importance 기반 특성 선택 완료
- [ ] 특성 선택 전후 AUC 비교 완료
- [ ] 과제 제출

---

## 📚 참고자료

- [Optuna 공식 문서](https://optuna.readthedocs.io)
- [sklearn permutation_importance](https://scikit-learn.org/stable/modules/permutation_importance.html)
- [베이지안 최적화 이해](https://distill.pub/2020/bayesian-optimization/)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day148+optimization
