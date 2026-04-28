"""
텔레그램 알림 모듈 (Telegram Notifier)
=========================================
매매 신호·체결·에러 발생 시 텔레그램 봇으로 알림을 전송합니다.

필요 패키지:
    pip install python-telegram-bot

환경변수 설정 (.env):
    TELEGRAM_BOT_TOKEN=<BotFather 에서 발급받은 토큰>
    TELEGRAM_CHAT_ID=<알림을 받을 채팅/채널 ID>

봇 생성 방법:
    1. 텔레그램에서 @BotFather 검색
    2. /newbot 명령으로 봇 생성 → Token 발급
    3. @userinfobot 에게 메시지 보내 Chat ID 확인

공식 문서: https://docs.python-telegram-bot.org
"""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# 선택적 임포트
try:
    import telegram
    _TELEGRAM_AVAILABLE = True
except ImportError:
    _TELEGRAM_AVAILABLE = False


class TelegramNotifier:
    """
    텔레그램 봇 알림 전송 클래스

    Parameters
    ----------
    token   : str | None  봇 토큰 (없으면 환경변수 TELEGRAM_BOT_TOKEN 사용)
    chat_id : str | None  채팅 ID (없으면 환경변수 TELEGRAM_CHAT_ID 사용)
    dry_run : bool        True → 실제 전송 없이 콘솔 출력만

    Examples
    --------
    >>> notifier = TelegramNotifier()
    >>> notifier.send("✅ SPY 매수 체결: $450.00 x 1주")
    >>> notifier.send_trade(symbol="SPY", side="BUY", qty=1, price=450.0)
    >>> notifier.send_error("API 연결 실패", exc=e)
    """

    def __init__(
        self,
        token: Optional[str] = None,
        chat_id: Optional[str] = None,
        dry_run: bool = False,
    ) -> None:
        self.token   = token   or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
        self.dry_run = dry_run

        if not self.dry_run and not _TELEGRAM_AVAILABLE:
            raise ImportError(
                "python-telegram-bot 이 설치되지 않았습니다.\n"
                "설치 명령: pip install python-telegram-bot"
            )

        if not self.dry_run and (not self.token or not self.chat_id):
            raise ValueError(
                "TELEGRAM_BOT_TOKEN 과 TELEGRAM_CHAT_ID 를 "
                "환경변수로 설정하거나 인자로 전달하세요."
            )

    # ------------------------------------------------------------------
    # 기본 전송
    # ------------------------------------------------------------------

    def send(self, message: str) -> bool:
        """
        텍스트 메시지 전송

        Parameters
        ----------
        message : str  전송할 메시지

        Returns
        -------
        bool  전송 성공 여부
        """
        if self.dry_run:
            print(f"[TelegramNotifier DRY-RUN] {message}")
            return True

        try:
            asyncio.run(self._async_send(message))
            return True
        except Exception as exc:
            logger.error("텔레그램 전송 실패: %s", exc)
            return False

    async def _async_send(self, message: str) -> None:
        bot = telegram.Bot(token=self.token)
        # HTML 특수문자 이스케이프 후 전송 (HTML 인젝션 방지)
        from html import escape
        safe_message = escape(message, quote=False)
        await bot.send_message(
            chat_id=self.chat_id,
            text=safe_message,
            parse_mode=None,   # 이스케이프된 평문 전송
        )

    # ------------------------------------------------------------------
    # 전용 메시지 포맷
    # ------------------------------------------------------------------

    def send_trade(
        self,
        symbol: str,
        side: str,
        qty: float,
        price: float,
        broker: str = "",
        order_id: str = "",
        note: str = "",
    ) -> bool:
        """
        매매 체결 알림

        Parameters
        ----------
        symbol   : 종목코드
        side     : "BUY" | "SELL"
        qty      : 수량
        price    : 체결가
        broker   : 브로커명 (예: "alpaca", "kiwoom")
        order_id : 주문번호
        note     : 추가 메모
        """
        emoji = "🟢 매수" if side.upper() == "BUY" else "🔴 매도"
        now   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            f"<b>{emoji} 체결 알림</b>",
            f"⏰ {now}",
            f"📌 종목: <code>{symbol}</code>",
            f"📊 수량: {qty}주",
            f"💰 가격: {price:,.4f}",
        ]
        if broker:
            lines.append(f"🏦 브로커: {broker}")
        if order_id:
            lines.append(f"🔖 주문ID: <code>{order_id}</code>")
        if note:
            lines.append(f"📝 {note}")

        return self.send("\n".join(lines))

    def send_signal(
        self,
        symbol: str,
        signal: str,
        price: float,
        indicators: Optional[dict] = None,
    ) -> bool:
        """
        매매 신호 알림 (미체결 포함)

        Parameters
        ----------
        symbol     : 종목코드
        signal     : "BUY" | "SELL" | "HOLD"
        price      : 현재가
        indicators : {"MA5": 100.0, "MA20": 98.5, "RSI": 42.1} 등
        """
        emoji_map = {"BUY": "📈", "SELL": "📉", "HOLD": "⏸️"}
        emoji = emoji_map.get(signal.upper(), "❓")
        now   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            f"<b>{emoji} {signal.upper()} 신호</b>",
            f"⏰ {now}",
            f"📌 종목: <code>{symbol}</code>",
            f"💰 현재가: {price:,.4f}",
        ]
        if indicators:
            for k, v in indicators.items():
                lines.append(f"  {k}: {v}")

        return self.send("\n".join(lines))

    def send_daily_summary(
        self,
        broker: str,
        portfolio_value: float,
        daily_pnl: float,
        trade_count: int,
        positions: Optional[list[dict]] = None,
    ) -> bool:
        """
        일일 결산 알림

        Parameters
        ----------
        broker          : 브로커명
        portfolio_value : 총 평가금액
        daily_pnl       : 당일 손익
        trade_count     : 당일 거래 건수
        positions       : 보유 포지션 목록 [{"symbol": ..., "qty": ..., "pnl": ...}]
        """
        pnl_emoji = "📈" if daily_pnl >= 0 else "📉"
        now       = datetime.now().strftime("%Y-%m-%d")
        lines     = [
            f"<b>📊 [{broker.upper()}] 일일 결산 – {now}</b>",
            f"💼 총 평가금액: {portfolio_value:,.0f}",
            f"{pnl_emoji} 당일 손익: {daily_pnl:+,.0f}",
            f"🔄 거래 건수: {trade_count}건",
        ]
        if positions:
            lines.append("\n<b>보유 포지션:</b>")
            for pos in positions[:5]:  # 상위 5개만 표시
                pnl = pos.get("pnl", 0)
                sym = pos.get("symbol", "?")
                qty = pos.get("qty", 0)
                lines.append(f"  • {sym}: {qty}주 (손익: {pnl:+,.0f})")
            if len(positions) > 5:
                lines.append(f"  … 외 {len(positions) - 5}개 종목")

        return self.send("\n".join(lines))

    def send_error(self, context: str, exc: Optional[Exception] = None) -> bool:
        """
        에러 알림

        Parameters
        ----------
        context : 에러 발생 상황 설명
        exc     : 예외 객체 (있으면 타입·메시지 포함)
        """
        now   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            "<b>🚨 자동매매 시스템 에러</b>",
            f"⏰ {now}",
            f"📍 위치: {context}",
        ]
        if exc:
            lines.append(f"❌ 오류: <code>{type(exc).__name__}: {exc}</code>")

        return self.send("\n".join(lines))

    def send_system_status(self, status: str, detail: str = "") -> bool:
        """
        시스템 상태 알림 (시작·정지·재시작 등)

        Parameters
        ----------
        status : "START" | "STOP" | "RESTART" | "WARNING"
        detail : 상세 메시지
        """
        emoji_map = {
            "START":   "🟢 시스템 시작",
            "STOP":    "🔴 시스템 정지",
            "RESTART": "🔄 시스템 재시작",
            "WARNING": "⚠️ 경고",
        }
        label = emoji_map.get(status.upper(), f"ℹ️ {status}")
        now   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [f"<b>{label}</b>", f"⏰ {now}"]
        if detail:
            lines.append(detail)

        return self.send("\n".join(lines))


# ---------------------------------------------------------------------------
# 예제 실행
# ---------------------------------------------------------------------------

def _demo() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    notifier = TelegramNotifier(dry_run=True)  # dry_run=False 로 실제 전송

    notifier.send_system_status("START", "자동매매 봇이 시작되었습니다.")
    notifier.send_signal("SPY", "BUY", 450.23, {"MA5": 449.5, "MA20": 445.0, "RSI": 42.1})
    notifier.send_trade("SPY", "BUY", qty=1, price=450.23, broker="alpaca", order_id="abc-123")
    notifier.send_daily_summary(
        broker="alpaca",
        portfolio_value=100_450,
        daily_pnl=450,
        trade_count=3,
        positions=[
            {"symbol": "SPY",  "qty": 1, "pnl": 230},
            {"symbol": "AAPL", "qty": 2, "pnl": 120},
            {"symbol": "MSFT", "qty": 1, "pnl": 100},
        ],
    )
    notifier.send_error("daily_signal_check()", exc=ValueError("API 응답 없음"))


if __name__ == "__main__":
    _demo()
