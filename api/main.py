"""
Python Trading Sample – FastAPI 백엔드
========================================
실행 방법:
    uvicorn api.main:app --reload --port 8000

브라우저에서 http://localhost:8000 접속
API 문서: http://localhost:8000/docs
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.routers import (
    alpaca,
    auto_trader,
    kiwoom,
    ml_strategy,
    risk_manager,
    telegram_notifier,
    trade_logger,
)

app = FastAPI(
    title="Python Trading API",
    description="자동매매 모듈 FastAPI 테스트 서버",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(risk_manager.router)
app.include_router(trade_logger.router)
app.include_router(telegram_notifier.router)
app.include_router(kiwoom.router)
app.include_router(alpaca.router)
app.include_router(ml_strategy.router)
app.include_router(auto_trader.router)

# 정적 파일 (프론트엔드)
_STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(_STATIC)), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(str(_STATIC / "index.html"))


@app.get("/health")
def health():
    return {"status": "ok"}
