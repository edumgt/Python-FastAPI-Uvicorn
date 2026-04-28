"""
키움증권 OpenAPI+ 연동 모듈
===============================
키움증권 OpenAPI+를 통해 국내 주식 자동매매를 구현하는 래퍼 클래스

⚠️  중요 제약 사항
  - 키움증권 OpenAPI+는 Windows 전용 COM 컴포넌트입니다.
  - HTS(영웅문4) 설치 및 로그인이 선행되어야 합니다.
  - pykiwoom 라이브러리를 사용합니다: pip install pykiwoom

실행 환경:
  Windows 10/11  (macOS/Linux 에서는 시뮬레이션 모드로 동작)

필요 패키지:
    pip install pykiwoom  (Windows 전용)

환경변수 설정 (.env):
    KIWOOM_ACCOUNT_NO=<계좌번호 10자리>   예: 1234567890
    KIWOOM_ACCOUNT_PW=<계좌 비밀번호 4자리>

공식 문서:
    https://www.kiwoom.com/h/customer/download/VApiDocumentPage
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

# ---------------------------------------------------------------------------
# 플랫폼 감지 및 선택적 임포트
# ---------------------------------------------------------------------------
_IS_WINDOWS = sys.platform.startswith("win")

try:
    if _IS_WINDOWS:
        from pykiwoom.kiwoom import Kiwoom  # type: ignore
        _PYKIWOOM_AVAILABLE = True
    else:
        _PYKIWOOM_AVAILABLE = False
except ImportError:
    _PYKIWOOM_AVAILABLE = False


# ---------------------------------------------------------------------------
# 데이터 모델
# ---------------------------------------------------------------------------

@dataclass
class KiwoomOrderResult:
    """주문 결과"""
    order_no: str          # 주문번호
    symbol: str            # 종목코드
    qty: int               # 주문 수량
    price: int             # 주문 가격 (0 = 시장가)
    side: str              # "매수" | "매도"
    order_type: str        # "시장가" | "지정가"
    status: str = "접수"


@dataclass
class KiwoomPositionInfo:
    """보유 종목 정보"""
    symbol: str            # 종목코드 (예: "005930")
    name: str              # 종목명 (예: "삼성전자")
    qty: int               # 보유 수량
    avg_price: int         # 평균 매수가
    current_price: int     # 현재가
    profit_loss: int       # 평가 손익(원)
    profit_loss_rate: float  # 수익률 (%)


@dataclass
class KiwoomAccountInfo:
    """계좌 잔고 정보"""
    account_no: str        # 계좌번호
    deposit: int           # 예수금
    available: int         # 출금 가능 금액
    total_eval: int        # 총평가금액
    total_profit_loss: int # 총손익
    positions: list[KiwoomPositionInfo] = field(default_factory=list)


# ---------------------------------------------------------------------------
# KiwoomTrader 클래스
# ---------------------------------------------------------------------------

class KiwoomTrader:
    """
    키움증권 OpenAPI+ 자동매매 클라이언트

    Windows 환경에서만 실제 API 호출이 가능합니다.
    다른 환경에서는 시뮬레이션(Dry-Run) 모드로 동작합니다.

    Parameters
    ----------
    account_no : str | None
        계좌번호 (없으면 환경변수 KIWOOM_ACCOUNT_NO 사용)
    simulate : bool
        True → 모의투자(시뮬레이션) 모드 강제 사용

    Examples
    --------
    >>> trader = KiwoomTrader()  # Windows에서 실제 연결
    >>> trader.login()
    >>> price = trader.get_current_price("005930")
    >>> print(f"삼성전자 현재가: {price:,}원")
    >>> order = trader.market_buy("005930", qty=1)
    """

    # 주문 구분 코드 (키움 TR 규격)
    _ORDER_TYPE_MAP = {
        "시장가":  "03",
        "지정가":  "00",
        "조건부지정가": "05",
    }
    # 매매 구분
    _SIDE_MAP = {
        "매수": 1,
        "매도": 2,
    }

    def __init__(
        self,
        account_no: Optional[str] = None,
        simulate: bool = False,
    ) -> None:
        self.account_no = account_no or os.getenv("KIWOOM_ACCOUNT_NO", "")
        self.simulate   = simulate or not _IS_WINDOWS or not _PYKIWOOM_AVAILABLE
        self._kiwoom: Optional[object] = None

        if self.simulate:
            mode = "시뮬레이션" if not _IS_WINDOWS else "시뮬레이션(pykiwoom 미설치)"
            print(f"[KiwoomTrader] {mode} 모드로 동작합니다.")
        else:
            print("[KiwoomTrader] 실거래 모드 – 키움 OpenAPI+ 연결 중...")

    # ------------------------------------------------------------------
    # 연결 / 로그인
    # ------------------------------------------------------------------

    def login(self) -> bool:
        """
        키움증권 OpenAPI+ 로그인

        Returns
        -------
        bool  로그인 성공 여부
        """
        if self.simulate:
            print("[시뮬레이션] 로그인 성공 (모의)")
            return True

        try:
            self._kiwoom = Kiwoom()
            self._kiwoom.CommConnect(block=True)
            state = self._kiwoom.GetConnectState()
            if state == 1:
                print("[KiwoomTrader] 로그인 성공")
                return True
            print("[KiwoomTrader] 로그인 실패")
            return False
        except Exception as exc:
            print(f"[KiwoomTrader] 로그인 오류: {exc}")
            return False

    # ------------------------------------------------------------------
    # 시세 조회
    # ------------------------------------------------------------------

    def get_current_price(self, symbol: str) -> int:
        """
        국내 주식 현재가 조회

        Parameters
        ----------
        symbol : str  종목코드 (예: "005930" – 삼성전자)

        Returns
        -------
        int  현재가 (원)
        """
        if self.simulate:
            # 시뮬레이션: yfinance를 이용한 가격 조회
            return self._get_price_from_yfinance(symbol)

        price_str: str = self._kiwoom.GetMasterLastPrice(symbol)
        return abs(int(price_str.replace(",", "").strip()))

    def _get_price_from_yfinance(self, symbol: str) -> int:
        """시뮬레이션 모드: yfinance로 KRX 종목 현재가 조회"""
        try:
            import yfinance as yf
            ticker = f"{symbol}.KS" if not symbol.endswith(".KS") else symbol
            data = yf.download(ticker, period="1d", auto_adjust=True, progress=False)
            if data.empty:
                ticker = f"{symbol}.KQ"
                data = yf.download(ticker, period="1d", auto_adjust=True, progress=False)
            price = float(data["Close"].iloc[-1])
            return int(price)
        except Exception:
            return 0

    def get_ohlcv(self, symbol: str, days: int = 60) -> pd.DataFrame:
        """
        국내 주식 일봉 OHLCV 데이터 조회

        Parameters
        ----------
        symbol : str  종목코드
        days   : int  최근 N일치

        Returns
        -------
        pd.DataFrame  컬럼: Open, High, Low, Close, Volume
        """
        if self.simulate:
            return self._get_ohlcv_from_yfinance(symbol, days)

        df = self._kiwoom.block_request(
            "opt10081",
            종목코드=symbol,
            기준일자="",
            수정주가구분=1,
            output="주식일봉차트조회",
            next=0,
        )
        df = df.rename(columns={
            "시가": "Open", "고가": "High", "저가": "Low",
            "현재가": "Close", "거래량": "Volume",
        })
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = df[col].abs().astype(float)
        return df.head(days)[["Open", "High", "Low", "Close", "Volume"]]

    def _get_ohlcv_from_yfinance(self, symbol: str, days: int) -> pd.DataFrame:
        """시뮬레이션 모드: yfinance로 KRX 종목 OHLCV 조회"""
        try:
            import yfinance as yf
            ticker = f"{symbol}.KS" if not symbol.endswith((".KS", ".KQ")) else symbol
            df = yf.download(ticker, period=f"{days}d", auto_adjust=True, progress=False)
            if df.empty:
                ticker = f"{symbol}.KQ"
                df = yf.download(ticker, period=f"{days}d", auto_adjust=True, progress=False)
            df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
            df.index.name = "Date"
            return df
        except Exception as exc:
            print(f"[시뮬레이션] OHLCV 조회 실패: {exc}")
            return pd.DataFrame()

    # ------------------------------------------------------------------
    # 계좌 잔고 조회
    # ------------------------------------------------------------------

    def get_account_info(self) -> KiwoomAccountInfo:
        """
        계좌 잔고 및 보유 종목 조회

        Returns
        -------
        KiwoomAccountInfo
        """
        if self.simulate:
            return KiwoomAccountInfo(
                account_no=self.account_no or "0000000000",
                deposit=10_000_000,
                available=9_500_000,
                total_eval=10_500_000,
                total_profit_loss=500_000,
                positions=[
                    KiwoomPositionInfo(
                        symbol="005930", name="삼성전자",
                        qty=10, avg_price=70_000, current_price=73_000,
                        profit_loss=30_000, profit_loss_rate=4.29,
                    )
                ],
            )

        # 실제 API: OPW00001 (예수금상세현황요청)
        deposit_data = self._kiwoom.block_request(
            "opw00001",
            계좌번호=self.account_no,
            비밀번호="",
            비밀번호입력매체구분="00",
            조회구분=2,
            output="예수금상세현황",
            next=0,
        )
        deposit = int(str(deposit_data.get("예수금", "0")).replace(",", ""))
        available = int(str(deposit_data.get("출금가능금액", "0")).replace(",", ""))

        # OPW00018 (계좌평가잔고내역요청)
        balance_data = self._kiwoom.block_request(
            "opw00018",
            계좌번호=self.account_no,
            비밀번호="",
            비밀번호입력매체구분="00",
            조회구분=1,
            output="계좌평가잔고개요",
            next=0,
        )
        total_eval = int(str(balance_data.get("총평가금액", "0")).replace(",", ""))
        total_pl   = int(str(balance_data.get("총손익금액", "0")).replace(",", ""))

        # 보유 종목 목록
        stock_data = self._kiwoom.block_request(
            "opw00018",
            계좌번호=self.account_no,
            비밀번호="",
            비밀번호입력매체구분="00",
            조회구분=1,
            output="계좌평가잔고개별합산",
            next=0,
        )
        positions: list[KiwoomPositionInfo] = []
        if not stock_data.empty:
            for _, row in stock_data.iterrows():
                positions.append(KiwoomPositionInfo(
                    symbol=str(row.get("종목번호", "")).lstrip("A"),
                    name=str(row.get("종목명", "")),
                    qty=int(str(row.get("보유수량", "0")).replace(",", "")),
                    avg_price=int(str(row.get("매입단가", "0")).replace(",", "")),
                    current_price=abs(int(str(row.get("현재가", "0")).replace(",", ""))),
                    profit_loss=int(str(row.get("손익금액", "0")).replace(",", "")),
                    profit_loss_rate=float(str(row.get("손익율", "0")).replace(",", "").replace("%", "")),
                ))

        return KiwoomAccountInfo(
            account_no=self.account_no,
            deposit=deposit,
            available=available,
            total_eval=total_eval,
            total_profit_loss=total_pl,
            positions=positions,
        )

    # ------------------------------------------------------------------
    # 주문
    # ------------------------------------------------------------------

    def market_buy(self, symbol: str, qty: int) -> KiwoomOrderResult:
        """
        시장가 매수

        Parameters
        ----------
        symbol : str  종목코드
        qty    : int  매수 수량
        """
        return self._send_order(symbol, qty, price=0, side="매수", order_type="시장가")

    def market_sell(self, symbol: str, qty: int) -> KiwoomOrderResult:
        """
        시장가 매도

        Parameters
        ----------
        symbol : str  종목코드
        qty    : int  매도 수량
        """
        return self._send_order(symbol, qty, price=0, side="매도", order_type="시장가")

    def limit_buy(self, symbol: str, qty: int, price: int) -> KiwoomOrderResult:
        """
        지정가 매수

        Parameters
        ----------
        symbol : str  종목코드
        qty    : int  매수 수량
        price  : int  지정가 (원)
        """
        return self._send_order(symbol, qty, price=price, side="매수", order_type="지정가")

    def limit_sell(self, symbol: str, qty: int, price: int) -> KiwoomOrderResult:
        """
        지정가 매도

        Parameters
        ----------
        symbol : str  종목코드
        qty    : int  매도 수량
        price  : int  지정가 (원)
        """
        return self._send_order(symbol, qty, price=price, side="매도", order_type="지정가")

    def _send_order(
        self, symbol: str, qty: int, price: int, side: str, order_type: str
    ) -> KiwoomOrderResult:
        """내부 공통 주문 처리"""
        if self.simulate:
            current = self.get_current_price(symbol)
            exec_price = price if price > 0 else current
            print(
                f"[시뮬레이션] {side} 주문: {symbol} {qty}주 @ "
                f"{'시장가' if price == 0 else f'{exec_price:,}원'}"
            )
            return KiwoomOrderResult(
                order_no="SIM-0001",
                symbol=symbol,
                qty=qty,
                price=exec_price,
                side=side,
                order_type=order_type,
                status="시뮬레이션 체결",
            )

        order_no = self._kiwoom.SendOrder(
            "자동매매주문",
            "0101",                              # 화면번호
            self.account_no,
            self._SIDE_MAP[side],                # 1: 매수, 2: 매도
            symbol,
            qty,
            price,
            self._ORDER_TYPE_MAP[order_type],    # 호가구분
            "",                                  # 원주문번호
        )
        return KiwoomOrderResult(
            order_no=str(order_no),
            symbol=symbol,
            qty=qty,
            price=price,
            side=side,
            order_type=order_type,
            status="접수",
        )

    # ------------------------------------------------------------------
    # 신호 생성 (공통 MA + RSI 기반)
    # ------------------------------------------------------------------

    def ma_cross_signal(
        self, symbol: str, fast: int = 5, slow: int = 20
    ) -> dict:
        """
        MA 크로스 신호 생성

        Returns
        -------
        dict  {"symbol", "signal"("BUY"|"SELL"|"HOLD"), "price", "MA{fast}", "MA{slow}"}
        """
        df = self.get_ohlcv(symbol, days=max(slow * 3, 90))
        if df.empty:
            return {"symbol": symbol, "signal": "HOLD", "price": 0}

        df[f"MA{fast}"]  = df["Close"].rolling(fast).mean()
        df[f"MA{slow}"] = df["Close"].rolling(slow).mean()
        df = df.dropna()

        if len(df) < 2:
            return {"symbol": symbol, "signal": "HOLD", "price": 0}

        latest = df.iloc[-1]
        prev   = df.iloc[-2]

        if (prev[f"MA{fast}"] <= prev[f"MA{slow}"]) and (latest[f"MA{fast}"] > latest[f"MA{slow}"]):
            signal = "BUY"
        elif (prev[f"MA{fast}"] >= prev[f"MA{slow}"]) and (latest[f"MA{fast}"] < latest[f"MA{slow}"]):
            signal = "SELL"
        else:
            signal = "HOLD"

        return {
            "symbol":      symbol,
            "signal":      signal,
            "price":       int(latest["Close"]),
            f"MA{fast}":   round(float(latest[f"MA{fast}"]), 0),
            f"MA{slow}":  round(float(latest[f"MA{slow}"]), 0),
        }


# ---------------------------------------------------------------------------
# 예제 실행 (직접 실행 시)
# ---------------------------------------------------------------------------

def _demo() -> None:
    """
    키움증권 자동매매 데모 (시뮬레이션 모드)
    실거래 환경: KIWOOM_ACCOUNT_NO 환경변수 설정 + Windows에서 실행
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    # 시뮬레이션 모드로 실행 (Windows가 아니어도 동작)
    trader = KiwoomTrader(simulate=True)
    trader.login()

    print("\n=== 계좌 정보 ===")
    acc = trader.get_account_info()
    print(f"  계좌번호 : {acc.account_no}")
    print(f"  예수금   : {acc.deposit:,}원")
    print(f"  총평가   : {acc.total_eval:,}원")
    print(f"  총손익   : {acc.total_profit_loss:+,}원")

    print("\n=== 보유 종목 ===")
    for pos in acc.positions:
        print(
            f"  [{pos.symbol}] {pos.name}: {pos.qty}주 @ {pos.avg_price:,}원 | "
            f"현재가: {pos.current_price:,}원 | "
            f"손익: {pos.profit_loss:+,}원 ({pos.profit_loss_rate:+.2f}%)"
        )

    print("\n=== 종목 신호 확인 ===")
    watchlist = {
        "005930": "삼성전자",
        "000660": "SK하이닉스",
        "035420": "NAVER",
    }
    for code, name in watchlist.items():
        sig = trader.ma_cross_signal(code)
        print(
            f"  [{code}] {name}: 현재가 {sig['price']:,}원 | "
            f"MA5={sig.get('MA5', 'N/A'):,} MA20={sig.get('MA20', 'N/A'):,} | "
            f"신호: {sig['signal']}"
        )

    print("\n=== 시뮬레이션 주문 ===")
    order = trader.market_buy("005930", qty=1)
    print(f"  주문번호: {order.order_no} | {order.side} {order.qty}주 | 상태: {order.status}")


if __name__ == "__main__":
    _demo()
