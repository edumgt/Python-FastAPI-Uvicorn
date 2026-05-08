"""딥러닝 (LSTM / MLP) 주가 예측 API 라우터"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/dl", tags=["DL Strategy"])

_dl_strategy = None  # DLStrategy instance


def _get():
    if _dl_strategy is None:
        raise HTTPException(
            status_code=503,
            detail="모델 미학습. POST /api/dl/train 을 먼저 호출하세요.",
        )
    return _dl_strategy


# ---------------------------------------------------------------------------
# 요청 모델
# ---------------------------------------------------------------------------

class DLTrainReq(BaseModel):
    ticker:       str   = Field(default="005930", description="종목 코드 (Naver 또는 yfinance)")
    source:       str   = Field(default="naver",  description="데이터 소스: naver | yfinance")
    pages:        int   = Field(default=30, ge=5, le=100, description="네이버 수집 페이지 수 (naver 전용)")
    period:       str   = Field(default="3y",  description="기간 (yfinance 전용, 예: 3y)")
    model_type:   str   = Field(default="auto", description="lstm | mlp | auto")
    seq_len:      int   = Field(default=20, ge=5, le=60, description="LSTM 시퀀스 길이")
    forward_days: int   = Field(default=5, ge=1, le=20)
    threshold:    float = Field(default=0.01, ge=0.001, le=0.1)
    epochs:       int   = Field(default=30, ge=5, le=200, description="LSTM 학습 에폭 (lstm 전용)")


class DLPredictReq(BaseModel):
    ticker:  str = Field(default="005930")
    source:  str = Field(default="naver", description="naver | yfinance")
    pages:   int = Field(default=10, ge=1, le=50)
    period:  str = Field(default="6mo")


# ---------------------------------------------------------------------------
# 데이터 로더 헬퍼
# ---------------------------------------------------------------------------

def _load_data(ticker: str, source: str, pages: int = 10, period: str = "3y"):
    """소스에 따라 OHLCV DataFrame 반환"""
    if source == "naver":
        try:
            from trading.naver_crawler import NaverFinanceCrawler
        except ImportError as e:
            raise HTTPException(status_code=503, detail=str(e))
        crawler = NaverFinanceCrawler()
        try:
            df = crawler.get_daily_ohlcv(ticker, pages=pages)
        except ImportError as e:
            raise HTTPException(status_code=503, detail=str(e))
        if df.empty:
            raise HTTPException(status_code=404, detail=f"데이터 없음: {ticker}")
        # DL 모듈이 OHLCV 컬럼명 그대로 사용하므로 rename 불필요
        return df
    else:
        try:
            import yfinance as yf
        except ImportError:
            raise HTTPException(status_code=503, detail="pip install yfinance")
        df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
        if df.empty:
            raise HTTPException(status_code=404, detail=f"데이터 없음: {ticker}")
        return df


# ---------------------------------------------------------------------------
# 엔드포인트
# ---------------------------------------------------------------------------

@router.post("/train")
def train(req: DLTrainReq):
    """
    LSTM 또는 MLP 딥러닝 모델을 학습합니다.

    - **source=naver**: 네이버 금융 크롤링 데이터 (국내 주식)
    - **source=yfinance**: yfinance 데이터 (해외 주식)
    - **model_type=auto**: TensorFlow 설치 시 LSTM, 없으면 MLP 자동 선택
    """
    global _dl_strategy

    df = _load_data(req.ticker, req.source, req.pages, req.period)

    try:
        from trading.dl_strategy import DLStrategy
    except ImportError as e:
        raise HTTPException(status_code=503, detail=str(e))

    try:
        _dl_strategy = DLStrategy(
            model_type=req.model_type,
            seq_len=req.seq_len,
            forward_days=req.forward_days,
            threshold=req.threshold,
        )
        kwargs = {}
        if _dl_strategy.model_type == "lstm":
            kwargs["epochs"]     = req.epochs
            kwargs["batch_size"] = 32
        result = _dl_strategy.train(df, **kwargs)
    except (ImportError, ValueError) as e:
        raise HTTPException(status_code=503, detail=str(e))

    return {
        "status":       "ok",
        "ticker":       req.ticker,
        "model_type":   result.model_type,
        "accuracy":     round(result.accuracy, 4),
        "report":       result.report,
        "history":      result.history,
    }


@router.post("/predict")
def predict(req: DLPredictReq):
    """
    학습된 딥러닝 모델로 최신 데이터를 기반으로 방향성 신호를 예측합니다.
    """
    df     = _load_data(req.ticker, req.source, req.pages, req.period)
    signal = _get().predict(df)
    price  = float(df["Close"].iloc[-1])
    return {"ticker": req.ticker, "signal": signal, "price": round(price, 2)}


@router.post("/predict-proba")
def predict_proba(req: DLPredictReq):
    """
    학습된 딥러닝 모델로 클래스별 확률(상승/보합/하락)을 반환합니다.
    """
    df    = _load_data(req.ticker, req.source, req.pages, req.period)
    proba = _get().predict_proba(df)
    price = float(df["Close"].iloc[-1])
    return {"ticker": req.ticker, "price": round(price, 2), "probabilities": proba}


@router.get("/info")
def model_info():
    """현재 로드된 딥러닝 모델 정보를 반환합니다."""
    if _dl_strategy is None:
        return {"trained": False}
    return {
        "trained":    True,
        "model_type": _dl_strategy.model_type,
    }
