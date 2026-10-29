"""
Репозитории: превращают данные Bybit в строки и пишут в PostgreSQL.
"""
from datetime import datetime
from psycopg2.extras import execute_values
from logger import logger
from bybitOptionStratge.method_symbols import OptionAsset


def _ts(ms):
    """Milliseconds -> datetime. None-safe."""
    if ms is None:
        return None
    return datetime.fromtimestamp(int(ms) / 1000)


def _num(value) -> float:
    """None -> 0.0, иначе float."""
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


class FuturesRepository:
    """Сохранение закрытых фьючерсных позиций."""

    def __init__(self, conn):
        self.conn = conn

    def _to_row(self, p: dict) -> tuple:
        return (
            p.get('orderId'),
            p.get('symbol'),
            p.get('side'),
            _num(p.get('qty')),
            _num(p.get('avgEntryPrice')),
            _num(p.get('avgExitPrice')),
            _num(p.get('closedPnl')),
            _num(p.get('openFee')),
            _num(p.get('closeFee')),
            _num(p.get('fundingFee')),
            _ts(p.get('createdTime')),
            _ts(p.get('updatedTime')),
        )

    def save_many(self, positions: list[dict]) -> int:
        if not positions:
            logger.info('FuturesRepository: нечего сохранять')
            return 0

        rows = [self._to_row(p) for p in positions]
        query = """
            INSERT INTO futures_positions
            (order_id, symbol, side, qty, avg_entry_price, avg_exit_price,
             closed_pnl, open_fee, close_fee, funding_fee,
             open_time, close_time)
            VALUES %s
            ON CONFLICT (order_id, close_time) DO NOTHING
        """
        with self.conn.cursor() as cur:
            execute_values(cur, query, rows)
        self.conn.commit()
        logger.info(f'FuturesRepository: сохранено {len(rows)} строк')
        return len(rows)


class OptionsRepository:
    """
    Сохранение закрытых опционных позиций.
    Использует OptionAsset + кэш, чтобы не сканировать markets N раз.
    """

    def __init__(self, conn, bot=None):
        self.conn = conn
        self.bot = bot
        self._asset_cache = {}

    def _get_asset(self, raw_symbol: str):
        if not self.bot or not raw_symbol:    # ← защита
            return None
        """OptionAsset с кэшем по raw_symbol."""
        if raw_symbol in self._asset_cache:
            return self._asset_cache[raw_symbol]

        try:
            asset = OptionAsset(
                raw_symbol=raw_symbol,
                exchange_instance=self.bot.exchange,
            )
        except Exception as e:
            logger.warning(f'OptionAsset упал на {raw_symbol}: {e}')
            asset = None

        self._asset_cache[raw_symbol] = asset
        return asset

    @staticmethod
    def _extract_expiry(raw_symbol: str):
        """
        Достаёт дату экспирации из нативного Bybit-символа.
        BTC-12JUN25-104019-C-USDT -> date(2025, 6, 12).
        """
        months = {
            'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
            'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12,
        }
        for part in raw_symbol.split('-'):
            if 5 <= len(part) <= 7:
                day_str = part[:-5]
                mon_str = part[-5:-2]
                yr_str = part[-2:]
                if day_str.isdigit() and mon_str in months and yr_str.isdigit():
                    try:
                        return datetime(
                            2000 + int(yr_str),
                            months[mon_str],
                            int(day_str),
                        ).date()
                    except ValueError:
                        return None
        return None

    @staticmethod
    def _delivery_fee(raw):
        """'' / None → None, '0.00000000' → 0.0, число → float."""
        if raw is None:
            return None
        if isinstance(raw, str):
            s = raw.strip()
            if not s:
                return None
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None

    def _to_row(self, t: dict) -> tuple:
       raw_deliv = t.get("deliveryFee")
       fee_deliv = self._delivery_fee(raw_deliv)
       return (
           t["symbol"],
           t.get("expiry"),
           t.get("strike"),
           t.get("type"),
           t.get("side"),
           t.get("qty"),
           t.get("entry"),
           t.get("exit"),
           t.get("pnl_usdt"),
           t.get("fees_usdt"),
           fee_deliv,
           t.get("exit") if fee_deliv is not None else None,
           t.get("open_time"),
           t.get("close_time"),
       )
       
    def save_many(self, positions: list[dict]) -> int:
        if not positions:
            logger.info('OptionsRepository: нечего сохранять')
            return 0

        rows = [self._to_row(p) for p in positions]
        query = """
         INSERT INTO options_positions
         (symbol, expiry_date, strike_price, option_type, side, qty,
        avg_entry_price, avg_exit_price, total_pnl, fees_usdt,
        delivery_fee, delivery_price, open_time, close_time)
        VALUES %s
        ON CONFLICT (symbol, side, close_time) DO NOTHING
        """
        with self.conn.cursor() as cur:
            execute_values(cur, query, rows)
        self.conn.commit()
        logger.info(f'OptionsRepository: сохранено {len(rows)} строк')
        return len(rows)