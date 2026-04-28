# Day 127 – 데이터 정제

> **소요시간**: 8시간 | **Phase**: 7 – 금융 데이터 분석 & 머신러닝 (초급)

---

## 🎯 학습 목표

- 금융 데이터의 결측값(NaN) 탐지 및 처리 전략 선택
- 이상값(Outlier) 탐지 방법(Z-score, IQR)
- 데이터 정규화(`MinMaxScaler`)와 표준화(`StandardScaler`)
- 머신러닝 입력을 위한 특성 스케일링 이해

---

## 📖 이론 (08:00 – 10:00)

### 1. 결측값 처리 전략
```python
df.isna().sum()              # 결측값 개수 확인
df.dropna()                  # 결측값 행 제거
df.fillna(method="ffill")    # 전일 값으로 채우기 (forward fill)
df.fillna(df.mean())         # 평균으로 채우기
df.interpolate()             # 선형 보간
```

### 2. 이상값 탐지
```python
import numpy as np

# Z-score 방법 (|Z| > 3 이면 이상값)
z = (df["Close"] - df["Close"].mean()) / df["Close"].std()
outliers_z = df[np.abs(z) > 3]

# IQR 방법
Q1, Q3 = df["Close"].quantile(0.25), df["Close"].quantile(0.75)
IQR = Q3 - Q1
outliers_iqr = df[(df["Close"] < Q1 - 1.5*IQR) | (df["Close"] > Q3 + 1.5*IQR)]
```

### 3. 스케일링
```python
from sklearn.preprocessing import MinMaxScaler, StandardScaler

# MinMax: 0~1 범위로 압축 (LSTM 입력에 주로 사용)
scaler = MinMaxScaler()
scaled = scaler.fit_transform(df[["Close"]])

# Standard: 평균=0, 표준편차=1 (대부분의 ML 모델에 적합)
std_scaler = StandardScaler()
standardized = std_scaler.fit_transform(df[["Close"]])
```

---

## 🧪 LAB 1 – 결측값 탐지 및 처리 (10:00 – 12:00)

```python
# missing_values.py
import yfinance as yf
import pandas as pd
import numpy as np

df = yf.download("AAPL", period="2y", auto_adjust=True)[["Open","High","Low","Close","Volume"]]

# 인위적 결측값 삽입 (테스트용)
rng = np.random.default_rng(42)
miss_idx = rng.choice(df.index, size=10, replace=False)
df.loc[miss_idx, "Close"] = np.nan

print("=== 결측값 현황 ===")
print(df.isna().sum())
print(f"\n결측값 비율: {df['Close'].isna().mean()*100:.2f}%")

# 처리 방법 비교
df_drop  = df.dropna()
df_ffill = df.fillna(method="ffill")
df_interp= df.interpolate(method="time")

print(f"\n원본:   {len(df)}행")
print(f"dropna: {len(df_drop)}행")
print(f"ffill:  {len(df_ffill)}행 (결측 {df_ffill['Close'].isna().sum()}개)")
print(f"interp: {len(df_interp)}행 (결측 {df_interp['Close'].isna().sum()}개)")

# 금융 데이터에서는 ffill 또는 interpolate 권장
df_clean = df.fillna(method="ffill").dropna()
print(f"\n최종 정제 데이터: {len(df_clean)}행")
```

---

## 🧪 LAB 2 – 이상값 탐지 (13:00 – 15:00)

```python
# outlier_detection.py
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = yf.download("AAPL", period="5y", auto_adjust=True)[["Close"]]
df["Return"] = df["Close"].pct_change() * 100
df = df.dropna()

# Z-score 방법
df["Z_score"] = (df["Return"] - df["Return"].mean()) / df["Return"].std()
outliers_z = df[np.abs(df["Z_score"]) > 3]

# IQR 방법
Q1, Q3 = df["Return"].quantile(0.25), df["Return"].quantile(0.75)
IQR = Q3 - Q1
lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
outliers_iqr = df[(df["Return"] < lower) | (df["Return"] > upper)]

print(f"전체 데이터: {len(df)}일")
print(f"이상값 (Z-score |>3|): {len(outliers_z)}일")
print(f"이상값 (IQR): {len(outliers_iqr)}일")
print("\n=== Z-score 이상값 ===")
print(outliers_z[["Close","Return","Z_score"]].sort_values("Return"))

# 시각화
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4))
ax1.hist(df["Return"], bins=100, edgecolor="white", color="steelblue")
ax1.axvline(x=lower, color="red", linestyle="--", label="IQR 경계")
ax1.axvline(x=upper, color="red", linestyle="--")
ax1.set_title("일간 수익률 분포")
ax1.legend()

ax2.boxplot(df["Return"], vert=False)
ax2.set_title("수익률 Box Plot")
plt.tight_layout()
plt.savefig("outlier_analysis.png", dpi=150)
plt.show()
```

---

## 🧪 LAB 3 – 데이터 스케일링 (15:00 – 17:00)

```python
# scaling.py
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import matplotlib.pyplot as plt

df = yf.download("AAPL", period="2y", auto_adjust=True)[["Close","Volume"]].dropna()

# MinMaxScaler
mm_scaler = MinMaxScaler()
mm_scaled = mm_scaler.fit_transform(df)

# StandardScaler
std_scaler = StandardScaler()
std_scaled = std_scaler.fit_transform(df)

# 결과를 DataFrame으로
df_mm  = pd.DataFrame(mm_scaled,  columns=["Close_MM","Volume_MM"],  index=df.index)
df_std = pd.DataFrame(std_scaled, columns=["Close_Std","Volume_Std"], index=df.index)

print("=== MinMax 스케일링 결과 ===")
print(df_mm.describe().round(4))
print("\n=== Standard 스케일링 결과 ===")
print(df_std.describe().round(4))

# 역변환 (원래 단위 복원)
restored = mm_scaler.inverse_transform(mm_scaled)
print(f"\n역변환 Close (마지막): {restored[-1,0]:.2f} (원본: {df['Close'].iloc[-1]:.2f})")

# 시각화
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
df["Close"].plot(ax=axes[0], title="원본 Close")
df_mm["Close_MM"].plot(ax=axes[1], title="MinMax 스케일링 (0~1)")
df_std["Close_Std"].plot(ax=axes[2], title="Standard 스케일링 (μ=0, σ=1)")
plt.tight_layout()
plt.savefig("scaling_comparison.png", dpi=150)
plt.show()
```

---

## 📝 과제 (17:00 – 18:00)

1. 삼성전자 5년 데이터에서 일간 수익률 이상값(Z-score > 3)을 찾고, 해당 날짜의 뉴스(또는 이벤트)를 조사하세요.
2. OHLCV 모든 컬럼에 `MinMaxScaler`를 적용하고 역변환이 정확한지 검증하세요.
3. 결측값을 ffill·bfill·interpolate 세 가지 방법으로 각각 채운 후, 차이를 시각화하세요.

---

## ✅ 체크리스트

- [ ] 결측값 탐지 및 세 가지 처리 방법 비교 완료
- [ ] Z-score와 IQR 방법으로 이상값 탐지 성공
- [ ] `MinMaxScaler`·`StandardScaler` 적용 및 역변환 성공
- [ ] 이상값·스케일링 비교 차트 시각화 완료
- [ ] 과제 제출

---

## 📚 참고자료

- [sklearn 전처리 문서](https://scikit-learn.org/stable/modules/preprocessing.html)
- [pandas fillna](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html)
- [pandas interpolate](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html)
