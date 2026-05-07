# Day 132 – RandomForest 모델 학습 + 시계열 교차검증

> **소요시간**: 8시간 | **Phase**: 8 – 자동매매 시스템 실전 | **Week 3**

---

## 🎯 학습 목표

- `MLStrategy(model_type='rf')` 로 RandomForest 주가 방향성 예측 모델 학습
- 시계열 데이터 누수(Data Leakage) 방지 방법 이해
- 특성 중요도 분석으로 유효한 지표 선별
- 학습된 모델을 저장하고 실시간 신호 예측에 활용

---

## 📖 이론 (08:00 – 10:00)

### 1. 왜 주식 예측에 RandomForest인가?

| 모델 | 장점 | 단점 | 주식 적합성 |
|------|------|------|------------|
| Linear Regression | 빠름, 해석 쉬움 | 비선형 관계 포착 불가 | ⚠️  낮음 |
| RandomForest | 비선형, 과적합 저항, 특성 중요도 | 느림 | ✅ 높음 |
| XGBoost | 최고 성능, 부스팅 | 하이퍼파라미터 복잡 | ✅ 높음 |
| LSTM | 시계열 특화 | 학습 어려움, GPU 필요 | ⚠️  복잡 |

### 2. 시계열 교차검증 vs 일반 교차검증

```
❌  일반 K-Fold: 미래 데이터가 과거 학습에 사용 → 데이터 누수!

     [   fold1   ] [   fold2   ] [   fold3   ]
     Train/Test 무작위 분할 → 미래 → 과거 방향 오염

✅  시계열 분할 (Walk-Forward):

     [Train──────] [Test]
     [Train──────────] [Test]
     [Train──────────────] [Test]

     과거 → 미래 방향 유지, 실제 운용 환경과 동일
```

### 3. 레이블 설계 전략

```python
# 5일 후 1% 이상 상승 → BUY(1)
# 5일 후 1% 이상 하락 → SELL(-1)
# 그 외               → HOLD(0)

future_return = close.shift(-5) / close - 1
label = 0
if future_return > 0.01:  label = 1   # BUY
if future_return < -0.01: label = -1  # SELL
```

---

## 🧪 LAB 1 – 특성 생성 및 레이블 확인 (10:00 – 12:00)

```python
# lab_feature_check.py
import yfinance as yf
from trading.ml_strategy import FeatureBuilder, make_labels

# ── 데이터 수집 ───────────────────────────────────────────
df_raw = yf.download("SPY", period="5y", auto_adjust=True, progress=False)
df_raw.columns = [c[0] if isinstance(c, tuple) else c for c in df_raw.columns]
df_raw = df_raw[["Open", "High", "Low", "Close", "Volume"]].dropna()
print(f"원본 데이터: {len(df_raw)}행")

# ── 특성 생성 ─────────────────────────────────────────────
fb = FeatureBuilder()
df  = fb.build(df_raw)
print(f"특성 추가 후: {len(df)}행")
print(f"\n특성 컬럼 ({len(fb.feature_columns)}개):")
for col in fb.feature_columns:
    print(f"  {col:25s}: min={df[col].min():+.4f}  max={df[col].max():+.4f}")

# ── 레이블 분포 ───────────────────────────────────────────
labels = make_labels(df["Close"], forward_days=5, threshold=0.01)
dist   = labels.value_counts().sort_index()
print(f"\n레이블 분포 (5일/1% 기준):")
print(f"  하락(-1): {dist.get(-1, 0):4d}행  ({dist.get(-1, 0)/len(labels)*100:.1f}%)")
print(f"  보합( 0): {dist.get(0,  0):4d}행  ({dist.get(0,  0)/len(labels)*100:.1f}%)")
print(f"  상승(+1): {dist.get(1,  0):4d}행  ({dist.get(1,  0)/len(labels)*100:.1f}%)")
```

---

## 🧪 LAB 2 – RandomForest 학습 & 평가 (13:00 – 15:00)

```python
# lab_rf_train.py
import yfinance as yf
from trading.ml_strategy import MLStrategy

# ── 학습 데이터 ───────────────────────────────────────────
df = yf.download("SPY", period="5y", auto_adjust=True, progress=False)
df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()

# ── 모델 학습 ─────────────────────────────────────────────
print("=== RandomForest 모델 학습 (SPY 5년치) ===\n")
strategy = MLStrategy(
    model_type="rf",
    forward_days=5,    # 5일 후 방향성 예측
    threshold=0.01,    # ±1% 기준
)
result = strategy.train(df)

print(f"검증 정확도 : {result.accuracy:.4f} ({result.accuracy*100:.2f}%)")
print(f"\n분류 리포트:")
print(result.report)

# ── 특성 중요도 ───────────────────────────────────────────
print("특성 중요도 (상위 10개):")
for feat, imp in list(result.feature_importance.items())[:10]:
    bar = "█" * int(imp * 200)
    print(f"  {feat:<22} {imp:.4f} {bar}")

# ── 최근 신호 예측 ────────────────────────────────────────
recent = yf.download("SPY", period="6mo", auto_adjust=True, progress=False)
recent.columns = [c[0] if isinstance(c, tuple) else c for c in recent.columns]

signal = strategy.predict(recent)
proba  = strategy.predict_proba(recent)
price  = float(recent["Close"].iloc[-1])

print(f"\n=== 현재 신호 (SPY) ===")
print(f"  신호  : {signal}")
print(f"  현재가: ${price:,.2f}")
print(f"  상승 확률: {proba['상승']*100:.1f}%")
print(f"  보합 확률: {proba['보합']*100:.1f}%")
print(f"  하락 확률: {proba['하락']*100:.1f}%")

# ── 모델 저장 ─────────────────────────────────────────────
path = strategy.save("spy_rf_v1.pkl")
print(f"\n모델 저장: {path}")
```

---

## 🧪 LAB 3 – 다종목 학습 + 성능 비교 (15:00 – 17:00)

```python
# lab_multi_symbol_rf.py
"""여러 종목에 대해 RF 모델을 학습하고 성능을 비교합니다."""
import yfinance as yf
from trading.ml_strategy import MLStrategy

SYMBOLS = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA"]

results = {}
for symbol in SYMBOLS:
    print(f"\n[{symbol}] 학습 중...", end=" ")
    df = yf.download(symbol, period="5y", auto_adjust=True, progress=False)
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()

    strategy = MLStrategy(model_type="rf", forward_days=5)
    result   = strategy.train(df)
    strategy.save(f"{symbol.lower()}_rf.pkl")

    results[symbol] = {
        "accuracy": result.accuracy,
        "top_feature": list(result.feature_importance.keys())[0],
    }
    print(f"정확도: {result.accuracy:.4f}")

print("\n=== 종목별 RF 모델 성능 비교 ===")
print(f"{'종목':<8} {'정확도':>8} {'핵심 특성'}")
print("─" * 45)
for sym, info in sorted(results.items(), key=lambda x: -x[1]["accuracy"]):
    bar = "■" * int(info["accuracy"] * 20)
    print(f"{sym:<8} {info['accuracy']:>7.4f}  {bar}  {info['top_feature']}")
```

---

## 📝 과제 (17:00 – 18:00)

1. `lab_rf_train.py` 를 실행하여 SPY RF 모델을 학습하고 정확도를 기록하세요.
2. `forward_days` 를 3, 5, 10 으로 바꾸어 가며 정확도 변화를 비교하세요.
3. `threshold` 를 0.005, 0.01, 0.02 로 바꾸어 레이블 분포와 정확도 변화를 분석하세요.

---

## ✅ 체크리스트

- [ ] FeatureBuilder 특성 14개 생성 및 분포 확인
- [ ] make_labels 레이블 분포 확인 (상승/보합/하락 비율)
- [ ] RF 모델 학습 완료 (정확도 ≥ 45% 이상 목표)
- [ ] 특성 중요도 상위 5개 파악
- [ ] `spy_rf_v1.pkl` 저장 완료
- [ ] 5개 종목 다종목 학습 및 성능 비교 완료

---

## 📚 참고자료

- [scikit-learn RandomForest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)
- [시계열 교차검증](https://scikit-learn.org/stable/modules/cross_validation.html#time-series-split)
- [특성 중요도 해석](https://scikit-learn.org/stable/modules/permutation_importance.html)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day132+random+forest
