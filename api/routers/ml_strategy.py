"""ML Strategy API 라우터"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/ml", tags=["ML Strategy"])

_strategy = None  # MLStrategy instance


def _get():
    if _strategy is None:
        raise HTTPException(
            status_code=503,
            detail="모델이 아직 학습되지 않았습니다. POST /api/ml/train 을 먼저 호출하세요.",
        )
    return _strategy


# -------------------------------------------------------------------
# 요청 모델
# -------------------------------------------------------------------
class TrainReq(BaseModel):
    ticker: str = "SPY"
    period: str = "5y"
    model_type: str = "rf"
    forward_days: int = 5
    threshold: float = 0.01


class PredictReq(BaseModel):
    ticker: str
    period: str = "6mo"


class SaveReq(BaseModel):
    filename: str = "model.pkl"


class LoadReq(BaseModel):
    path: str


# -------------------------------------------------------------------
# 엔드포인트
# -------------------------------------------------------------------
@router.post("/train")
def train(req: TrainReq):
    global _strategy
    try:
        import yfinance as yf
    except ImportError:
        raise HTTPException(status_code=503, detail="yfinance 미설치. pip install yfinance")

    try:
        from trading.ml_strategy import MLStrategy
    except ImportError as e:
        raise HTTPException(status_code=503, detail=str(e))

    df = yf.download(req.ticker, period=req.period, auto_adjust=True, progress=False)
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    if df.empty:
        raise HTTPException(status_code=400, detail=f"데이터 없음: {req.ticker}")

    _strategy = MLStrategy(model_type=req.model_type, forward_days=req.forward_days, threshold=req.threshold)
    result = _strategy.train(df)

    return {
        "status": "ok",
        "ticker": req.ticker,
        "model_type": result.model_type,
        "accuracy": round(result.accuracy, 4),
        "report": result.report,
        "feature_importance": dict(list(result.feature_importance.items())[:10]),
    }


@router.post("/predict")
def predict(req: PredictReq):
    try:
        import yfinance as yf
    except ImportError:
        raise HTTPException(status_code=503, detail="yfinance 미설치")

    df = yf.download(req.ticker, period=req.period, auto_adjust=True, progress=False)
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    if df.empty:
        raise HTTPException(status_code=400, detail=f"데이터 없음: {req.ticker}")

    signal = _get().predict(df)
    price = float(df["Close"].iloc[-1])
    return {"ticker": req.ticker, "signal": signal, "price": round(price, 4)}


@router.post("/predict-proba")
def predict_proba(req: PredictReq):
    try:
        import yfinance as yf
    except ImportError:
        raise HTTPException(status_code=503, detail="yfinance 미설치")

    df = yf.download(req.ticker, period=req.period, auto_adjust=True, progress=False)
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    if df.empty:
        raise HTTPException(status_code=400, detail=f"데이터 없음: {req.ticker}")

    proba = _get().predict_proba(df)
    price = float(df["Close"].iloc[-1])
    return {"ticker": req.ticker, "price": round(price, 4), "probabilities": proba}


@router.get("/features")
def features():
    try:
        from trading.ml_strategy import FeatureBuilder
        return {"features": FeatureBuilder().feature_columns}
    except ImportError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/save")
def save(req: SaveReq):
    path = _get().save(req.filename)
    return {"status": "ok", "path": str(path)}


@router.post("/load")
def load(req: LoadReq):
    global _strategy
    try:
        from trading.ml_strategy import MLStrategy
        _strategy = MLStrategy.load(req.path)
        return {"status": "ok", "path": req.path}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
