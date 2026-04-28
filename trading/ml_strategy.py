"""
AI/ML 기반 매매 전략 모듈 (ML Strategy)
==========================================
RandomForest / XGBoost 모델로 주가 방향(상승/하락)을 예측하고
자동매매 신호를 생성합니다.

필요 패키지:
    pip install scikit-learn xgboost yfinance joblib

구조:
    FeatureBuilder   – OHLCV → 기술적 지표 특성 생성
    MLStrategy       – 모델 학습·저장·추론
    MLSignalAdapter  – AutoTrader 와 연결하는 어댑터
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# 선택적 임포트
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import train_test_split, TimeSeriesSplit
    from sklearn.metrics import classification_report, accuracy_score
    from sklearn.preprocessing import StandardScaler
    import joblib
    _SKLEARN_AVAILABLE = True
except ImportError:
    _SKLEARN_AVAILABLE = False

try:
    from xgboost import XGBClassifier
    _XGB_AVAILABLE = True
except ImportError:
    _XGB_AVAILABLE = False


# ---------------------------------------------------------------------------
# 특성 생성 (Feature Engineering)
# ---------------------------------------------------------------------------

class FeatureBuilder:
    """
    OHLCV DataFrame에서 기술적 지표 기반 특성(Feature)을 생성합니다.

    생성 특성 목록:
        MA5, MA20, MA60          – 이동평균
        EMA12, EMA26             – 지수이동평균
        MACD, MACD_Signal        – MACD
        RSI14                    – 상대강도지수
        BB_Width                 – 볼린저밴드 폭
        ATR14                    – 평균진폭
        Volume_Ratio             – 거래량 5일 평균 대비 비율
        Return_1d, Return_5d     – 1·5일 수익률
        Volatility_20            – 20일 변동성
    """

    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Parameters
        ----------
        df : pd.DataFrame  컬럼 Open, High, Low, Close, Volume 필수

        Returns
        -------
        pd.DataFrame  원본 + 특성 컬럼 추가 (NaN 행 제거됨)
        """
        close  = df["Close"]
        high   = df["High"]
        low    = df["Low"]
        volume = df["Volume"]

        out = df.copy()

        # ── 이동평균 ──────────────────────────────────────────────────
        for win in [5, 20, 60]:
            out[f"MA{win}"]  = close.rolling(win).mean()
            out[f"MA{win}_ratio"] = close / out[f"MA{win}"]   # 현재가/이평 비율

        # ── EMA / MACD ────────────────────────────────────────────────
        out["EMA12"] = close.ewm(span=12, adjust=False).mean()
        out["EMA26"] = close.ewm(span=26, adjust=False).mean()
        out["MACD"]  = out["EMA12"] - out["EMA26"]
        out["MACD_Signal"] = out["MACD"].ewm(span=9, adjust=False).mean()
        out["MACD_Hist"]   = out["MACD"] - out["MACD_Signal"]

        # ── RSI ───────────────────────────────────────────────────────
        delta   = close.diff()
        gain    = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
        loss    = (-delta).clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
        out["RSI14"] = 100 - 100 / (1 + gain / loss)

        # ── 볼린저밴드 ────────────────────────────────────────────────
        bb_mid         = close.rolling(20).mean()
        bb_std         = close.rolling(20).std()
        out["BB_Upper"] = bb_mid + 2 * bb_std
        out["BB_Lower"] = bb_mid - 2 * bb_std
        out["BB_Width"] = (out["BB_Upper"] - out["BB_Lower"]) / bb_mid
        out["BB_Pos"]   = (close - out["BB_Lower"]) / (out["BB_Upper"] - out["BB_Lower"] + 1e-9)

        # ── ATR (평균진폭) ────────────────────────────────────────────
        tr = pd.concat([
            high - low,
            (high - close.shift(1)).abs(),
            (low  - close.shift(1)).abs(),
        ], axis=1).max(axis=1)
        out["ATR14"] = tr.rolling(14).mean()

        # ── 거래량 ────────────────────────────────────────────────────
        out["Volume_MA5"]   = volume.rolling(5).mean()
        out["Volume_Ratio"] = volume / (out["Volume_MA5"] + 1e-9)

        # ── 수익률 / 변동성 ───────────────────────────────────────────
        out["Return_1d"]    = close.pct_change(1)
        out["Return_5d"]    = close.pct_change(5)
        out["Volatility_20"] = out["Return_1d"].rolling(20).std()

        return out.dropna()

    @property
    def feature_columns(self) -> list[str]:
        """모델 입력에 사용할 특성 컬럼 목록"""
        return [
            "MA5_ratio", "MA20_ratio", "MA60_ratio",
            "MACD", "MACD_Signal", "MACD_Hist",
            "RSI14", "BB_Width", "BB_Pos", "ATR14",
            "Volume_Ratio",
            "Return_1d", "Return_5d", "Volatility_20",
        ]


# ---------------------------------------------------------------------------
# 레이블 생성
# ---------------------------------------------------------------------------

def make_labels(
    close: pd.Series,
    forward_days: int = 5,
    threshold: float = 0.01,
) -> pd.Series:
    """
    N일 후 수익률 기반 3-class 레이블 생성

    Parameters
    ----------
    close        : 종가 Series
    forward_days : 예측 대상 기간 (일)
    threshold    : 상승/하락 판정 임계값 (기본 1%)

    Returns
    -------
    pd.Series  레이블: 1(상승) | 0(보합) | -1(하락)
    """
    future_return = close.shift(-forward_days) / close - 1
    labels = pd.Series(0, index=close.index)
    labels[future_return >  threshold] =  1
    labels[future_return < -threshold] = -1
    return labels


# ---------------------------------------------------------------------------
# MLStrategy
# ---------------------------------------------------------------------------

@dataclass
class ModelResult:
    """학습 결과"""
    model_type: str
    accuracy: float
    report: str
    feature_importance: dict = field(default_factory=dict)


class MLStrategy:
    """
    RandomForest / XGBoost 기반 방향성 예측 전략

    Parameters
    ----------
    model_type    : "rf" (RandomForest) | "xgb" (XGBoost) | "gb" (GradientBoosting)
    forward_days  : 예측 대상 기간 (일, 기본 5)
    threshold     : 상승/하락 판정 임계값 (기본 1%)
    model_dir     : 모델 저장 디렉터리 (기본 ./models)

    Examples
    --------
    >>> import yfinance as yf
    >>> df = yf.download("SPY", period="5y", auto_adjust=True)

    >>> strategy = MLStrategy(model_type="rf")
    >>> result = strategy.train(df)
    >>> print(f"정확도: {result.accuracy:.4f}")
    >>> strategy.save("spy_rf_model.pkl")

    >>> strategy2 = MLStrategy.load("spy_rf_model.pkl")
    >>> signal = strategy2.predict(df)  # "BUY" | "SELL" | "HOLD"
    """

    def __init__(
        self,
        model_type: str = "rf",
        forward_days: int = 5,
        threshold: float = 0.01,
        model_dir: str = "models",
    ) -> None:
        if not _SKLEARN_AVAILABLE:
            raise ImportError("pip install scikit-learn joblib 을 먼저 실행하세요.")

        self.model_type   = model_type.lower()
        self.forward_days = forward_days
        self.threshold    = threshold
        self.model_dir    = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self._fb      = FeatureBuilder()
        self._scaler  = StandardScaler()
        self._model   = self._build_model()
        self._trained = False

    def _build_model(self):
        if self.model_type == "rf":
            return RandomForestClassifier(
                n_estimators=200,
                max_depth=6,
                min_samples_leaf=10,
                random_state=42,
                n_jobs=-1,
            )
        elif self.model_type == "xgb":
            if not _XGB_AVAILABLE:
                raise ImportError("pip install xgboost 을 먼저 실행하세요.")
            return XGBClassifier(
                n_estimators=200,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                eval_metric="mlogloss",
                random_state=42,
                n_jobs=-1,
            )
        elif self.model_type == "gb":
            return GradientBoostingClassifier(
                n_estimators=200,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.8,
                random_state=42,
            )
        else:
            raise ValueError(f"지원하지 않는 모델 타입: {self.model_type}")

    # ------------------------------------------------------------------
    # 학습
    # ------------------------------------------------------------------

    def train(self, df: pd.DataFrame) -> ModelResult:
        """
        모델 학습

        Parameters
        ----------
        df : OHLCV DataFrame (Open, High, Low, Close, Volume)

        Returns
        -------
        ModelResult  학습 결과
        """
        feat_df = self._fb.build(df)
        labels  = make_labels(feat_df["Close"], self.forward_days, self.threshold)

        # 레이블이 없는 마지막 N행 제거
        valid_idx = feat_df.index[:-self.forward_days]
        X = feat_df.loc[valid_idx, self._fb.feature_columns]
        y = labels.loc[valid_idx]

        # 시계열 분할 (미래 데이터 누수 방지)
        split = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split], X.iloc[split:]
        y_train, y_test = y.iloc[:split], y.iloc[split:]

        X_train_sc = self._scaler.fit_transform(X_train)
        X_test_sc  = self._scaler.transform(X_test)

        self._model.fit(X_train_sc, y_train)
        self._trained = True

        preds    = self._model.predict(X_test_sc)
        accuracy = accuracy_score(y_test, preds)
        report   = classification_report(
            y_test, preds,
            target_names=["하락(-1)", "보합(0)", "상승(1)"],
            zero_division=0,
        )

        # 특성 중요도
        feat_imp = {}
        if hasattr(self._model, "feature_importances_"):
            for col, imp in zip(self._fb.feature_columns, self._model.feature_importances_):
                feat_imp[col] = round(float(imp), 4)
            feat_imp = dict(sorted(feat_imp.items(), key=lambda x: x[1], reverse=True))

        logger.info("모델 학습 완료 – 정확도: %.4f", accuracy)
        return ModelResult(
            model_type=self.model_type,
            accuracy=accuracy,
            report=report,
            feature_importance=feat_imp,
        )

    # ------------------------------------------------------------------
    # 예측
    # ------------------------------------------------------------------

    def predict(self, df: pd.DataFrame) -> str:
        """
        최신 데이터로 신호 예측

        Parameters
        ----------
        df : 최근 OHLCV DataFrame (최소 60행 이상 권장)

        Returns
        -------
        str  "BUY" | "SELL" | "HOLD"
        """
        if not self._trained:
            raise RuntimeError("모델이 학습되지 않았습니다. train() 을 먼저 호출하세요.")

        feat_df = self._fb.build(df)
        if feat_df.empty:
            return "HOLD"

        X_latest = feat_df.iloc[[-1]][self._fb.feature_columns]
        X_sc     = self._scaler.transform(X_latest)
        label    = int(self._model.predict(X_sc)[0])

        label_map = {1: "BUY", -1: "SELL", 0: "HOLD"}
        return label_map.get(label, "HOLD")

    def predict_proba(self, df: pd.DataFrame) -> dict:
        """
        클래스별 확률 반환

        Returns
        -------
        dict  {"하락": 0.2, "보합": 0.3, "상승": 0.5}
        """
        if not self._trained:
            raise RuntimeError("모델이 학습되지 않았습니다.")

        feat_df = self._fb.build(df)
        if feat_df.empty:
            return {"하락": 0.0, "보합": 1.0, "상승": 0.0}

        X_latest = feat_df.iloc[[-1]][self._fb.feature_columns]
        X_sc     = self._scaler.transform(X_latest)
        proba    = self._model.predict_proba(X_sc)[0]
        classes  = self._model.classes_

        label_map = {-1: "하락", 0: "보합", 1: "상승"}
        return {label_map[int(c)]: round(float(p), 4) for c, p in zip(classes, proba)}

    # ------------------------------------------------------------------
    # 저장 / 불러오기
    # ------------------------------------------------------------------

    def save(self, filename: str = "model.pkl") -> Path:
        """모델 + 스케일러 저장"""
        path = self.model_dir / filename
        joblib.dump({"model": self._model, "scaler": self._scaler, "config": {
            "model_type": self.model_type,
            "forward_days": self.forward_days,
            "threshold": self.threshold,
        }}, path)
        logger.info("모델 저장: %s", path)
        return path

    @classmethod
    def load(cls, path: str) -> "MLStrategy":
        """저장된 모델 불러오기"""
        data = joblib.load(path)
        cfg  = data.get("config", {})
        strategy = cls(
            model_type=cfg.get("model_type", "rf"),
            forward_days=cfg.get("forward_days", 5),
            threshold=cfg.get("threshold", 0.01),
        )
        strategy._model   = data["model"]
        strategy._scaler  = data["scaler"]
        strategy._trained = True
        logger.info("모델 불러오기: %s", path)
        return strategy


# ---------------------------------------------------------------------------
# AutoTrader 연동 어댑터
# ---------------------------------------------------------------------------

class MLSignalAdapter:
    """
    MLStrategy 신호를 AutoTrader 의 ma_cross_signal() 형식으로 변환하는 어댑터

    Parameters
    ----------
    strategy : MLStrategy  학습된 모델
    data_fn  : callable    symbol → pd.DataFrame (OHLCV) 반환 함수

    Examples
    --------
    >>> import yfinance as yf
    >>> strategy = MLStrategy.load("models/spy_rf.pkl")
    >>> adapter = MLSignalAdapter(strategy, lambda s: yf.download(s, period="6mo"))
    >>> result = adapter.get_signal("SPY")
    """

    def __init__(self, strategy: MLStrategy, data_fn) -> None:
        self.strategy = strategy
        self.data_fn  = data_fn

    def get_signal(self, symbol: str) -> dict:
        """AutoTrader 호환 신호 딕셔너리 반환"""
        df     = self.data_fn(symbol)
        signal = self.strategy.predict(df)
        proba  = self.strategy.predict_proba(df)
        price  = float(df["Close"].iloc[-1]) if not df.empty else 0.0

        return {
            "symbol": symbol,
            "signal": signal,
            "price":  round(price, 4),
            "prob_up":   proba.get("상승", 0.0),
            "prob_down": proba.get("하락", 0.0),
            "prob_hold": proba.get("보합", 0.0),
        }


# ---------------------------------------------------------------------------
# 예제 실행
# ---------------------------------------------------------------------------

def _demo() -> None:
    try:
        import yfinance as yf
    except ImportError:
        print("yfinance 미설치. pip install yfinance")
        return

    print("=== ML 전략 데모 (SPY 5년치 학습) ===\n")

    df = yf.download("SPY", period="5y", auto_adjust=True, progress=False)
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()

    strategy = MLStrategy(model_type="rf", forward_days=5)
    result   = strategy.train(df)

    print(f"모델 유형   : {result.model_type}")
    print(f"검증 정확도 : {result.accuracy:.4f} ({result.accuracy*100:.2f}%)")
    print("\n분류 리포트:")
    print(result.report)

    print("특성 중요도 (상위 5):")
    for feat, imp in list(result.feature_importance.items())[:5]:
        print(f"  {feat:<20} {imp:.4f}")

    recent_df = yf.download("SPY", period="6mo", auto_adjust=True, progress=False)
    recent_df.columns = [c[0] if isinstance(c, tuple) else c for c in recent_df.columns]
    signal = strategy.predict(recent_df)
    proba  = strategy.predict_proba(recent_df)

    print(f"\n최근 신호: {signal}")
    print(f"  상승 확률: {proba['상승']*100:.1f}%")
    print(f"  보합 확률: {proba['보합']*100:.1f}%")
    print(f"  하락 확률: {proba['하락']*100:.1f}%")

    model_path = strategy.save("spy_rf_model.pkl")
    print(f"\n모델 저장 완료: {model_path}")


if __name__ == "__main__":
    _demo()
