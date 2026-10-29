"""
Забор Closed P&L с Bybit.
Принимает готовый BybitOptionBot (только как источник exchange).
"""
import ccxt
from datetime import datetime, timedelta
from logger import logger


def fetch_closed_pnl_paged(bot, category: str, start_ms: int) -> list[dict]:
    """
    Универсальный постраничный забор Closed P&L через бота.
    category: 'linear' для USDT-фьючерсов, 'option' для опционов.
    """
    all_positions, cursor = [], None
    page = 0

    while True:
        page += 1
        params = {
            'category': category,
            'startTime': start_ms,
            'limit': 100,
        }
        if cursor:
            params['cursor'] = cursor

        logger.info(f"Bybit {category} closed-pnl, стр.{page}")

        try:
            response = bot.exchange.privateGetV5PositionClosedPnl(params)
        except ccxt.BaseError as e:
            logger.error(f'Ошибка CCXT при получении closed-pnl: {e}')
            break

        data = response['result']['list']
        if not data:
            break

        all_positions.extend(data)
        cursor = response['result'].get('nextPageCursor')
        if not cursor:
            break

    logger.info(f'Bybit {category}: получено {len(all_positions)} записей')
    return all_positions


def fetch_futures_positions(bot, days_back: int = 7) -> list[dict]:
    """История закрытых фьючерсных позиций за N дней."""
    start_ms = int(
        (datetime.now() - timedelta(days=days_back)).timestamp() * 1000
    )
    logger.info(f'Запрос фьючерсов за {days_back} дн.')
    return fetch_closed_pnl_paged(bot, 'linear', start_ms)


def fetch_options_positions(bot, days_back: int = 7) -> list[dict]:
    """История закрытых опционных позиций за N дней."""
    start_ms = int(
        (datetime.now() - timedelta(days=days_back)).timestamp() * 1000
    )
    logger.info(f'Запрос опционов за {days_back} дн.')
    return fetch_closed_pnl_paged(bot, 'option', start_ms)