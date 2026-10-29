"""
Точка входа ETL.
Разовый запуск: получили — записали — вышли.
Торговый цикл не поднимается.
"""
import sys
import os
import argparse
import pybit
import time

# СНАЧАЛА добавляем корень проекта в sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ПОТОМ импортируем всё остальное
from logger import logger
from directorDB.config import load_db_config
from directorDB.db import get_connection, create_schema
from directorDB.extract import fetch_futures_positions, fetch_options_positions
from directorDB.repository import FuturesRepository, OptionsRepository
from bybitOptionStratge.bybit_client import BybitOptionBot
from pybit.unified_trading import HTTP
from logger import logger
from dotenv import load_dotenv
from datetime import datetime, timedelta
from datetime import timezone
from decimal import Decimal
import re
# COD WORK result list close candale days

load_dotenv()
API_KEY = os.getenv("BYBIT_API_KEY")
SECRET_KEY = os.getenv("BYBIT_SECRET_KEY")
IS_TESTNET = os.getenv("IS_TESTNET", "True").lower() == "true"


def parse_option_symbol(sym: str):
    """
    Разбирает тикер опциона Bybit вида BASE-DDMMMYY-STRIKE-[C|P]-SETTLE.

    Примеры:
        DOGE-28AUG26-0.094-C-USDT
        SOL-28AUG26-78-C-USDT
        BTC-27JUN25-100000-P-USDT

    Возвращает dict с полями base/expiry/strike/type/settle,
    либо None, если строка не соответствует формату (например, фьючерс).
    """
    # Группы:
    #   1) BASE   — тикер базового актива (DOGE, SOL, BTC, ...)
    #   2) DDMMMYY — дата экспирации: день + 3-буквенный месяц + 2-значный год
    #   3) STRIKE — страйк; допускаем точку для мелких цен (0.094)
    #   4) C|P    — тип опциона: Call / Put
    #   5) SETTLE — валюта расчёта (обычно USDT)
    m = re.match(r"^([A-Z]+)-(\d{2}[A-Z]{3}\d{2})-([\d.]+)-([CP])-([A-Z]+)$", sym)
    if not m:
        return None

    base, exp, strike, typ, settle = m.groups()

    # "%d%b%y" — день, локализованное англ. сокращение месяца, 2-значный год.
    # Bybit всегда отдаёт месяц в верхнем регистре (AUG), а %b ждёт 'Aug' —
    # поэтому приводим к title-case.
    expiry = datetime.strptime(exp.title(), "%d%b%y").date()

    return {
        "base": base,          # базовый актив: "DOGE"
        "expiry": expiry,      # дата экспирации: date(2026, 8, 28)
        "strike": float(strike),  # страйк: 0.094
        "type": "Call" if typ == "C" else "Put",
        "settle": settle,      # валюта расчёта: "USDT"
    }

def to_dt(ms: int) -> datetime:
    """Переводит таймстемп Bybit (миллисекунды epoch) в aware-datetime UTC."""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def parse_closed_pnl(resp: dict) -> dict:
    """
    Разбирает ответ Bybit v5/position/closed-pnl (category=option)
    в удобную структуру: список сделок + агрегаты по странице.
    """
    # Проверяем успешность ответа API: retCode != 0 — ошибка, покажем retMsg
    assert resp.get("retCode") == 0, resp.get("retMsg")
    r = resp["result"]  # внутри result лежат nextPageCursor, category и list

    trades = []
    for it in r["list"]:
        # Метаданные из символа опциона: base/expiry/strike/type/settle.
        # Если формат не совпал (например, фьючерс) — оставляем пустой dict.
        meta = parse_option_symbol(it["symbol"]) or {}

        # Все денежные значения API отдаёт строками; считаем в Decimal,
        # чтобы избежать ошибок округления float при суммировании комиссий.
        qty = Decimal(it["qty"])                    # кол-во контрактов
        entry = Decimal(it["avgEntryPrice"])        # средняя цена входа (премия)
        exit_ = Decimal(it["avgExitPrice"])         # средняя цена выхода
        fee_open = Decimal(it["totalOpenFee"])      # комиссия за открытие
        fee_close = Decimal(it["totalCloseFee"])    # комиссия за закрытие (0 при экспирации)
        fee_deliv = it.get("deliveryFee")      # комиссия за расчёт при экспирации
        
        fee_deliv_db = None if (fee_deliv is None or (isinstance(fee_deliv, str) 
                                and fee_deliv.strip() == "")) else fee_deliv
        # print(f"fee_deliv {fee_deliv_db}")
        _fee_or_zero = lambda v: 0.0 if v is None or (isinstance(v, str) and v.strip() == "") else float(v)
        
        trades.append({
            "symbol": it["symbol"],
            **meta,                                 # base, expiry, strike, type, settle
            "side": it["side"],                     # "Buy" / "Sell"
            "qty": float(qty),                      # наружу отдаём float — удобно для pandas/JSON
            "entry": float(entry),
            "exit": float(exit_),
            "open_time": to_dt(it["openTime"]),     # aware UTC
            "close_time": to_dt(it["closeTime"]),   # aware UTC
            # Суммарные комиссии по сделке (open + close + delivery) в USDT
            "fees_usdt": float(fee_open + fee_close + Decimal(_fee_or_zero(v=fee_deliv))),
            # будет или 0 , None, 0.576
            "deliveryFee": fee_deliv_db,
            # totalPnl уже учитывает комиссии — используем как источник истины
            "pnl_usdt": float(Decimal(it["totalPnl"])),
            # Время удержания позиции в часах (closeTime - openTime в мс → часы)
            "hold_hours": (it["closeTime"] - it["openTime"]) / 3_600_000,
        })

    return {
        # Курсор для следующей страницы; пустая строка/None — данных больше нет
        # "next_cursor": r.get("nextPageCursor"),
        # "category": r.get("category"),
        "trades": trades,
        # Агрегаты по текущей странице; для полной истории суммируйте по всем страницам
        "totals": {
            "pnl": sum(t["pnl_usdt"] for t in trades),
            "fees": sum(t["fees_usdt"] for t in trades),
            "count": len(trades),
        },
    }


def end_or_start_time(countWeekIteration:int = 3):
    '''
    end_time = int(datetime.now().timestamp()*1000)
    start_time = int((datetime.now() - timedelta(days=7)).timestamp()*1000)    
    '''
    listTimeEndStart=[]
    timeVremen=datetime.now()
    listTimeEndStart.append(int(timeVremen.timestamp()*1000))
    time.sleep(5)
    delta7days = timedelta(days = 7)
    for i in range(countWeekIteration):
        # time.sleep(5)
        timeVremen-=delta7days
        timeMicrSeond = int(timeVremen.timestamp()*1000)
        listTimeEndStart.append(timeMicrSeond)
        
    sortList = sorted(listTimeEndStart)
    print(sortList)   
    return sortList
        
        
def data_close_option(dataTime:list):
    """нужно перебрать недельными данными
    чтоб подставить
    
    """
    totalListOption = []
    end_time = int(datetime.now().timestamp()*1000)
    start_time = int((datetime.now() - timedelta(days=7)).timestamp()*1000)
    
    session = HTTP(
        testnet=False,
        api_key=API_KEY,
        api_secret=SECRET_KEY,)
    
    count = 0
    dataOptions = {}
    for i in range(len(dataTime)-1):
        start_time = dataTime[count]
        count+=1
        print(count)
        end_time = dataTime[count]
        time.sleep(5)
        if end_time:
            responce = session.get_closed_options_positions(
                category="option",
                startTime = start_time,
                endTime = end_time
                # symbol="SOLUSDT-19SEP26-112-P",
                # limit=1,
                )
            dataOptions[count] = responce
            # print(responce)
            parsC_P = parse_closed_pnl(resp=responce)
            print("=" *22)
            print(parsC_P)
            totalListOption.append(parsC_P)
                
    # print(responce)
    # parsC_P = parse_closed_pnl(resp=responce)
    
    
    return totalListOption        
            
            

def main(days_back: int = 7):
    logger.info(f'=== ETL: старт загрузки за {days_back} дней ===')

    # 1. Подключение к Bybit (только как источник exchange для Closed P&L)
    bot = BybitOptionBot()

    # 2. Extract
    futures = fetch_futures_positions(bot, days_back=days_back)
    options = fetch_options_positions(bot, days_back=days_back)
    logger.info(f'Фьючерсы: {len(futures)}, Опционы: {len(options)}')

    if not futures and not options:
        logger.warning('Данных нет — выходим')
        return

    # 3. Load
    db_cfg = load_db_config()
    conn = get_connection(db_cfg)
    try:
        create_schema(conn)

        saved_futures = FuturesRepository(conn).save_many(futures)
        saved_options = OptionsRepository(conn, bot).save_many(options)

        logger.info(f'Сохранено фьючерсов: {saved_futures}')
        logger.info(f'Сохранено опционов:  {saved_options}')
    finally:
        conn.close()
        logger.info('Соединение с БД закрыто')

    logger.info('=== ETL: завершено ===')

def run_etl(days_back: int = 7, weeks: int = 9):
    """Полный цикл: получить → распарсить → записать в БД."""
    times = end_or_start_time(countWeekIteration=weeks)
    pages = data_close_option(dataTime=times)

    flat_trades = []
    for page in pages:
        flat_trades.extend(page["trades"])

    logger.info(f"Собрано сделок: {len(flat_trades)}")
    if not flat_trades:
        logger.warning("Сделок нет — выходим")
        return 0

    db_cfg = load_db_config()
    conn = get_connection(db_cfg)
    try:
        create_schema(conn)
        saved = OptionsRepository(conn).save_many(flat_trades)
        logger.info(f"Вставлено строк: {len(flat_trades)}")
        return saved
    finally:
        conn.close()
        logger.info("Соединение с БД закрыто")


if __name__ == '__main__':
    run_etl()



        
        # 3 вкладываем пачкой

    
    
    
    # parser = argparse.ArgumentParser(description='Выгрузка истории Bybit в PostgreSQL')
    # parser.add_argument('--days', type=int, default=7,
    #                     help='За сколько дней выгружать (по умолчанию 7)')
    # args = parser.parse_args()

    # main(days_back=args.days)
    