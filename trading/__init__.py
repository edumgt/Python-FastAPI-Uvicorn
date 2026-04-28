"""
trading 패키지 – 자동매매 모듈 모음

제공 모듈:
  alpaca_client  – Alpaca Markets REST/WebSocket API 연동
  kiwoom_client  – 키움증권 OpenAPI+ 연동 (Windows 전용)
  auto_trader    – 공통 신호·포지션 관리 오케스트레이터
"""

from .alpaca_client import AlpacaTrader
from .kiwoom_client import KiwoomTrader
from .auto_trader import AutoTrader, Signal, SignalResult

__all__ = ["AlpacaTrader", "KiwoomTrader", "AutoTrader", "Signal", "SignalResult"]
