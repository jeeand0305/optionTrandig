from pybit.unified_trading import HTTP
from logger import logger
import ccxt
from pprint import pformat
import math
import pandas as pd
 # Добавили импорт numpy для работы с рядами Pandas
import numpy as np
from datetime import datetime
import re

class BybitOptionBot:
    def __init__(self):
        """
         Инициализируем биржу один раз при создании объекта бота.
        Объект сохраняется внутри класса как self.exchange.
        """
        self.exchange = ccxt.bybit({
            'enableRateLimit':True,
            'options':{
                'loadAllOptions': True
            }
        })
        logger.info(f'Инициализация подключения к Bybit')
        

    def tickerOnline(self, symbol='DOGE/USDT'):
        try:
            # Запрашиваем данные тикера
            ticker = self.exchange.fetch_ticker(symbol)
            
            # Получаем текущую цену
            current_price = ticker['last']
            logger.info(f"Текущая цена {symbol}: {current_price}")
            return current_price
        
        except Exception as e:
            logger.info(f"Ошибка при получении цены: {e}")
            return None
    
    def fetch_options_json_board(self, symbol: str, date_option: str):
        """no optimal result
        symbol: имя базового актива, например "DOGE", "BTC" или "SOL"
        date_option: дата экспирации в формате Bybit, например "26JUN26"
        """
        # Переводим аргументы в верхний регистр для исключения ошибок синтаксиса
        asset = symbol.upper()
        target_date = date_option.upper()

        logger.info(f"Отправка точечного REST-запроса JSON доски опционов {asset} на {target_date}...")

        try:
            # Инициализируем официальный HTTP-клиент Bybit БЕЗ ПРОКСИ
            session = HTTP(testnet=True)

            # 1. Запрашиваем ОНЛАЙН цену самого базового актива (фьючерса), чтобы знать текущий тик
            future_data = session.get_tickers(category="linear", symbol=f"{asset}USDT")
            current_tick = float(future_data['result']['list'][0]['lastPrice'])
            logger.info(f"🟢 Текущая онлайн-цена {asset}: {current_tick} USDT")

            # 2. Скачиваем ВСЮ доску опционов Bybit по выбранному ассету ОДНИМ JSON-пакетом
            response = session.get_tickers(
                category="option",
                baseCoin=asset
            )

            all_options_list = response['result']['list']
            
            logger.info(f"Успешно получен JSON. Всего опционов в списке: {len(all_options_list)}")
            for i in range(len(all_options_list)):
                if all_options_list[i]['symbol'] == 'DOGE-26JUN26-0.06-C-USDT':
                    print(all_options_list[i])
                    for key in all_options_list[i]:
                        logger.info(f"json_ {key } {all_options_list[i][key]}")
                
            print("-" * 80)
            print(f"{'Тикер опциона':<25} | {'Bid (Покупка)':<14} | {'Ask (Продажа)':<14} | {'Страйк':<10}")
            print("-" * 80)

            lower_strike_symbol = None
            max_strike_below_market = -1.0

            # 3. Парсим полученный JSON-массив
            for option in all_options_list:
                opt_symbol = option.get('symbol', '')
                
                # Фильтруем строго по переданной дате и по Put-опционам (P) для поиска нижних страйков
                if target_date in opt_symbol and opt_symbol.endswith("-P"):
                    bid = option.get('bid1Price', '0')
                    ask = option.get('ask1Price', '0')
                    
                    # Извлекаем цифру страйка из имени тикера
                    try:
                        # Разбираем строку вида 'DOGE-26JUN26-0.080-P' -> получаем '0.080' -> конвертируем в float
                        strike_price = float(opt_symbol.split('-')[2])
                    except:
                        continue

                    # Выводим текущую сетку цен в консоль
                    print(f"{opt_symbol:<25} | {bid:<14} | {ask:<14} | {strike_price:<10}")

                    # Математический фильтр: Ищем страйк, который МЕНЬШЕ онлайн-цены, но максимально БЛИЗОК к ней
                    if strike_price < current_tick and strike_price > max_strike_below_market:
                        max_strike_below_market = strike_price
                        lower_strike_symbol = opt_symbol

            print("-" * 80)
            if lower_strike_symbol:
                logger.info(f"🎯 Алгоритм выбрал из JSON оптимальный нижний контракт: {lower_strike_symbol}")
                return lower_strike_symbol
            else:
                logger.warning("Подходящий страйк ниже рыночной цены в полученном JSON не найден.")
                return None

        except Exception as e:
            logger.error(f"Ошибка при работе с REST API JSON: {e}")
            return None



    def get_bybit_options_data(self, symbol_="SOL"):
        count=0
        # 1. Инициализируем Bybit с флагом загрузки опционов

        logger.info("Загружаем рынки с Bybit (это может занять около 5-10 секунд)...")
        try:
            marketOption = self.exchange.fetch_option_chain(symbol_)
            markets = self.exchange.load_markets()
            logger.info(f'marketOption - {len(marketOption)}')
        except Exception as e:
            logger.error(f"Ошибка при загрузке рынков с биржи: {e}")
            return

        for i in marketOption:
            count+=1
            if count <5:
                logger.info(f" {i} itercia {marketOption[i]}")
        
        # 2. Фильтруем инструменты и собираем только опционы по BTC
        btc_options = []
        for symbol, market in markets.items():
            if market.get('type') == 'option' and market.get('base') == 'BTC':
                btc_options.append({
                    'symbol': symbol,                     # Формат CCXT (BTC/USDC:USDC-260626-70000-C)
                    'id': market['id'],                   # Родной тикер Bybit (BTC-26JUN26-70000-C)
                    'strike': market['strike'],           # Страйк опциона
                    'option_type': market['optionType'], # 'call' или 'put'
                    'expiry': market['expiryDatetime']    # Дата экспирации
                })

        logger.info(f"Найдено активных опционов на BTC: {len(btc_options)}")
        
        if not btc_options:
            logger.warning("Активные опционы не найдены.")
            return

        # Логируем структуру первых трех найденных опционов для примера
        logger.info("--- Пример структуры первых 3 опционов: ---")
        logger.info(f"\n{pformat(btc_options[:3])}")

        # 3. Получаем текущую рыночную цену (тикер) конкретного опциона
        # Берем первый опцион из полученного списка
        sample_symbol = btc_options[0]['symbol']
        logger.info(f"Запрашиваем рыночный тикер для опциона: {sample_symbol}")
        
        try:
            ticker = self.exchange.fetch_ticker(sample_symbol)
            logger.info("--- Данные котировок (Ticker) успешно получены ---")
            logger.info(f"Последняя цена сделки (Last): {ticker.get('last')}")
            logger.info(f"Лучшее предложение покупки (Bid): {ticker.get('bid')}")
            logger.info(f"Лучшее предложение продажи (Ask): {ticker.get('ask')}")
            logger.info(f"Объем за 24 часа: {ticker.get('baseVolume')}")
            
        except Exception as e:
            logger.error(f"Не удалось получить тикер для {sample_symbol}: {e}")


    def volotility4(self, sample_symbol="DOGEUSDT-17JUN26-0.009-C", window=30):
        usredKoeffcent = 0.70
        """
        Расчет Исторической Волатильности (HV) с помощью CCXT, Pandas и Numpy.
        """

        clean_symbol = (sample_symbol.upper().
        replace('/', '').replace(':', ''))
        if '-' in clean_symbol:
            base_coin = clean_symbol.split('-')[0]
        else:
            base_coin = clean_symbol
               
        if base_coin.endswith('USDT') and base_coin != 'USDT':
            base_coin = base_coin.replace('USDT', '')   
        
        smart_defaults = {
            'BTC': 0.50,
            'ETH': 0.60,
            'SOL': 0.75,
            'DOGE': 0.85    } 
        fallback_value = smart_defaults.get(base_coin, usredKoeffcent)
        market_ticker = f'{base_coin}/USDT' 
        
        try:
            limit = window + 1
            ohlcv = self.exchange.fetch_ohlcv(
                market_ticker, timeframe='1d', limit=limit)
            
            if not ohlcv or len(ohlcv) < limit:
                logger.warning(f"Недостаточно истории свечей для {market_ticker}. Дефолт {fallback_value}")
                return fallback_value

            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # ИСПРАВЛЕНО: Используем np.log вместо math.log для работы с Series
            df['log_return'] = np.log(df['close'] / df['close'].shift(1))
            
            # Считаем стандартное отклонение (Pandas .std() по умолчанию использует ddof=1)
            daily_std = df['log_return'].tail(window).std()
            
            # Переводим в годовую волатильность
            sigma = daily_std * math.sqrt(365)

            if pd.isna(sigma) or sigma <= 0:
                return fallback_value

            logger.info(f"Рассчитана волатильность через Pandas для {base_coin} ({window}d): {round(sigma, 4)}")
            return round(sigma, 4)

        except Exception as e:
            logger.error(f"Ошибка расчета HV для {market_ticker}: {e}. Дефолт {fallback_value}")
            return fallback_value
        
    


def parse_option_ticker(ticker: str) -> dict:
    # Регулярное выражение для поиска: Базовый_актив - Дата - Страйк - Тип
    # Поддерживает форматы 'SOL/USDT:USDT-260621-74-C' и 'SOL-260621-74-C'
    pattern = r"([^:-]+)(?:/[^:-]+:[^:-]+)?-(\d{6})-(\d+(?:\.\d+)?)-([CPcp])"
    match = re.match(pattern, ticker)
    if not match:
        raise ValueError(f"Неверный формат тикера опциона: {ticker}")
    base_asset = match.group(1)  # Например: SOL
    date_str = match.group(2)  # Например: 260621 (ГГММДД)
    strike = float(match.group(3))  # Например: 74.0
    option_type_letter = match.group(4).upper()  # Например: C
    # Преобразуем строку '260621' (YYMMDD) в полноценную дату
    expiration_date = datetime.strptime(date_str, "%y%m%d").date()
    # Маппинг типа опциона
    option_type = "Call" if option_type_letter == "C" else "Put"
    return {
        "ticker": ticker,
        "base_asset": base_asset,
        "expiration_date": expiration_date,  # Объект datetime.date
        "expiration_str": expiration_date.strftime("%y%m%d"),
        "strike": strike,
        "type": option_type,
    }

    # === ПРИМЕР РАБОТЫ ===
# ticker_example = "1000PEPE/USDT:USDT-260621-74-C"
# parsed_dict = parse_option_ticker(ticker_example)

# print(parsed_dict)



datePremiOption={'ticPrice': 64037.8, 'strikeCall': [{1: [64500.0, 337.2674277589067]}, {2: [65000.0, 188.83543651414584]}, {3: [65500.0, 96.8167915415379]}, {4: [66000.0, 45.25932589810873]}], 'strikePut': [{1: [64000.0, 511.58644054009346]}, {2: [63500.0, 302.85820732749926]}, {3: [63000.0, 162.9691942745667]}, {4: [62500.0, 78.89558092515563]}]}

# ==============================================================================
# ТОЧКА ВХОДА ДЛЯ ТЕСТИРОВАНИЯ ФУНКЦИИ
# ==============================================================================

if __name__ == "__main__":
    
    logger.info(f"{datePremiOption['strikeCall'][0][1][0]}")

    # bybitOption = BybitOptionBot()
    
    # ТЕСТ: Передаем символ в ОФИЦИАЛЬНОМ формате Bybit v5 (БЕЗ слова USDT в названии)
    # logger.info(f"Результат функции: {bybitOption.volotility4('SOL/USDT-21JUN26-0.09-C')}")
    
    # test cherz websocet pybit 
    # logger.info(f' bybitOption.fetch_options_json_board  {bybitOption.fetch_options_json_board("DOGE", "30JUN26")}')

    # test chrez websoket ccxt
    # logger.info(f'get_CCXT_btc {bybitOption.get_bybit_options_data()}')
    
    # test ticker price ccxt
    # logger.info(f'tickers request {bybitOption.tickerOnline('SOL/USDT')}')
    
    
    """
    {'symbol': 'DOGE-26JUN26-0.06-C-USDT', 'bid1Price': '0.02005', 
    'bid1Size': '100', 'bid1Iv': '0', 'ask1Price': '0.05005',
    'ask1Size': '100', 'ask1Iv': '5', 'lastPrice': '0', 
    'highPrice24h': '0', 'lowPrice24h': '0', 'markPrice': '0.02560348',
    'indexPrice': '0.08514508', 'markIv': '1.0015',
    'underlyingPrice': '0.08526', 'openInterest': '0',
    'turnover24h': '0', 'volume24h': '0', 'totalVolume': '0',
    'totalTurnover': '0', 'delta': '0.95795728',
    'gamma': '4.84898997', 'vega': '0.00001658',
    'theta': '-0.00004843', 'predictedDeliveryPrice': '0',
    'change24h': '0'}
    
    """
    
