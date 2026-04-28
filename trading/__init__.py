"""
trading 패키지 – 자동매매 모듈 모음

제공 모듈:
  alpaca_client     – Alpaca Markets REST API 연동 (미국 주식)
  kiwoom_client     – 키움증권 OpenAPI+ 연동 (국내 주식, Windows 전용)
  auto_trader       – 공통 신호·포지션 관리 오케스트레이터
  telegram_notifier – 텔레그램 알림 (체결·신호·에러·일일 결산)
  ml_strategy       – RandomForest / XGBoost 기반 AI 매매 전략
  risk_manager      – 일일 손실 한도·MDD 한도·포지션 사이징·시스템 정지
  trade_logger      – SQLite 기반 매매 기록·일일 스냅샷·CSV 내보내기
"""

from .alpaca_client import AlpacaTrader
from .kiwoom_client import KiwoomTrader
from .auto_trader import AutoTrader, Signal, SignalResult
from .telegram_notifier import TelegramNotifier
from .ml_strategy import MLStrategy, FeatureBuilder, MLSignalAdapter
from .risk_manager import RiskManager, PositionSizeResult
from .trade_logger import TradeLogger, TradeRecord, DailySnapshot, SystemEvent

__all__ = [
    "AlpacaTrader",
    "KiwoomTrader",
    "AutoTrader",
    "Signal",
    "SignalResult",
    "TelegramNotifier",
    "MLStrategy",
    "FeatureBuilder",
    "MLSignalAdapter",
    "RiskManager",
    "PositionSizeResult",
    "TradeLogger",
    "TradeRecord",
    "DailySnapshot",
    "SystemEvent",
]
