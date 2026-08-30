import sys
import os

# Находим путь к корневой директории всего проекта (ProjectOption)
# os.path.abspath(__file__) дает путь к bybit_client.py
# Первый dirname дает папку bybitOptionStratge, второй dirname дает ProjectOption
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Добавляем корень проекта в список путей поиска модулей Python
if project_root not in sys.path:
    sys.path.append(project_root)

# ТВОИ ОРИГИНАЛЬНЫЕ ИМПОРТЫ ТЕПЕРЬ СРАБОТАЮТ ВСЕГДА:
from logger import logger
from bybitOptionStratge.method_symbols import OptionAsset
import ccxt 
import os
import time
# from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from logger import logger
from dotenv import load_dotenv
# from bybitOptionStratege.method_symbols import OptionAsset
from bybitOptionStratge.method_symbols import OptionAsset


# COD WORK result list close candale days

load_dotenv()
API_KEY = os.getenv("BYBIT_API_KEY")
SECRET_KEY = os.getenv("BYBIT_SECRET_KEY")
IS_TESTNET = os.getenv("IS_TESTNET", "True").lower() == "true"


class BybitOptionBot:
    """
    Класс для работы с API Bybit через библиотеку CCXT.
    Отвечает только за получение сырых данных с биржи.
    """
    def __init__(self):
        # Инициализируем подключение к Bybit
        # Флаг loadAllOptions обязателен, 
        # чтобы CCXT подгружал опционные рынки
        
                # 1. Формируем единую конфигурацию
        exchange_config = {
            'apiKey': API_KEY,
            'secret': SECRET_KEY,
            'enableRateLimit': True,  # Защита от блокировок за частые запросы
            'options': {
                'adjustForTimeDifference': True,# АВТО-КОРРЕКЦИЯ ВРЕМЕНИ 
                'defaultType': 'option',    # Работаем по умолчанию с опционами
                'loadAllOptions': True      # Принудительно подгружаем опционные рынки
            }
        }
        
        # 2. Инициализируем подключение
        # Используем pro-версию ccxt (опционально, но рекомендуется для стабильности)
        self.exchange = ccxt.bybit(exchange_config)
        
        # Включаем тестовую сеть, если нужно (раскомментируйте для тестов)
        # self.exchange.set_sandbox_mode(True)
        
                # === КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: СКАЧИВАНИЕ СВЕЖИХ СТРАЙКОВ ===
        # === АБСОЛЮТНОЕ ИСПРАВЛЕНИЕ ЗАГРУЗКИ ОПЦИОНОВ В __init__ ===
        logger.info("Принудительно скачиваем опционную сетку Bybit...")
        try:
            if self.exchange:
                logger.info(f"Подключение к Bybit (Опционы + Торговля)")

        except Exception as e:
            logger.error(f"Не удалось обновить рынки при старте: {e}")
            raise e
        # ==========================================================

                
        logger.info("Подключение к Bybit (Опционы + Торговля) успешно инициализировано.")

        

    def get_historical_closes_candals(self, base_coin: str, window: int = 30) -> list:
        """
        Запрашивает исторические дневные свечи (1d) для спотовой пары на Bybit.
        
        :param base_coin: Имя монеты (например, 'BTC', 'DOGE')
        :param window: Размер окна для будущего расчета волатильности (например, 30 дней)
        :return: Чистый список цен закрытия (float) или пустой список при ошибке
        """
        # Формируем стандартный тикер спотового рынка Bybit (например, "BTC/USDT")
        market_ticker = f"{base_coin.upper()}/USDT"
        try:
            # Нам нужно на 1 свечу больше, чем окно расчета, 
            # чтобы Pandas смог посчитать самое первое изменение цены ( Close_t / Close_t-1 )
            limit = window + 1
            
            # Базовый метод CCXT для скачивания свечей (OHLCV)
            ohlcv = self.exchange.fetch_ohlcv(market_ticker, timeframe='1d', limit=limit)
        
            # Если биржа ничего не вернула или данных критически мало — прерываем работу
            if not ohlcv or len(ohlcv) < limit:
                logger.warning(f"Биржа вернула недостаточно свечей для пары {market_ticker}.")
                return []
                
            # Извлекаем только цены закрытия. 
            # В структуре CCXT свеча выглядит так: [timestamp, open, high, low, close, volume]
            # Индекс 4 — это цена закрытия (close)
            close_prices = [candle[4] for candle in ohlcv]
            
            logger.debug(f"Успешно скачано {len(close_prices)} свечей для {market_ticker}.")
            return close_prices
            
        except Exception as e:
            # Если упал интернет или Bybit выдал ошибку — логируем и возвращаем пустой список
            logger.error(f"Сетевая ошибка при скачивании свечей для {market_ticker}: {e}")
            return []


    def fetch_option_market_data(self, symbol="BTC"):
        """
        Метод для ПАРСИНГА данных.
        Получает текущие котировки (тикеры) для всех опционов по базовому активу (например, BTC).
        """
        try:
            logger.info(f"Запрос рыночных данных для опционов {symbol}...")
            # Загружаем рынки, если они еще не загружены в кэш CCXT
            self.exchange.load_markets()
            
            # Получаем тикеры. Для Bybit формат символа обычно: BTC-26DEC25-50000-C
            all_tickers = self.exchange.fetch_tickers(params={'base': symbol})
            
            # Фильтруем, чтобы оставить только опционы (на случай, если попало что-то еще)
            option_tickers = {k: v for k, v in all_tickers.items() if '-C' in k or '-P' in k}
            
            logger.info(f"Успешно получено {len(option_tickers)} опционных контрактов.")
            return option_tickers
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге опционных данных: {e}")
            return None
        

    def check_connection_and_balance(self): 
        """
            Проверяет подключение к бирже, выводит общую стоимость аккаунта 
            и показывает баланс по всем ненулевым активам.
            """
        dictBalance={}
        try:
            # Запрашиваем баланс Единого Торгового Аккаунта (UTA)
            balance = self.exchange.fetch_balance()
            

            # 1. Выводим общую информацию по аккаунту (если Bybit отдает её в info)
            # На UTA аккаунтах общая оценка обычно лежит в поле 'totalEquity' или 'totalMarginBalance'
            uta_info = balance.get('info', {}).get('result', {}).get('list', [{}])[0]
            dictBalance['total_equity'] = uta_info.get('totalEquity', 'N/A')
            dictBalance['total_margin'] = uta_info.get('totalMarginBalance', 'N/A')
            
            if dictBalance['total_equity'] != 'N/A':
                logger.debug(f"total akk+margin:  {dictBalance['total_equity']} USD"
                            f"total margin {dictBalance['total_margin']} USD")
        
            else:
                logger.warning(f' error get balance {uta_info}')        
            # Возвращаем весь словарь баланса, чтобы его можно было использовать дальше
            return dictBalance
            
        except Exception as e:
            logger.error(f"Ошибка подключения к бирже или получения баланса: {e}")
            return None


    def get_all_option_coins(self):
        """
        Парсит все доступные базовые монеты, на которые сейчас открыты опционы.
        Выводит один чистый лог со списком монет.
        """
        try:
            # Загружаем рынки с биржи
            markets = self.exchange.load_markets()
            
            # Собираем уникальные базовые активы (base) только для типа 'option'
            option_coins = set(
                market['base'] for market in markets.values()
                if market.get('type') == 'option' and 'base' in market
            )
            
            # Переводим в отсортированный список
            coins_list = sorted(list(option_coins))
            
            # Выводим один аккуратный лог
            logger.debug(f"Available option base coins: {', '.join(coins_list)}")
            return coins_list
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге базовых монет опционов: {e}")
            return []

    def get_option_expiration_dates(self, base_coin="BTC"):
        """
        Парсит и возвращает уникальные даты экспирации для указанной монеты.
        Выводит один чистый лог со списком дат, отсортированных по хронологии.
        """
        try:
            # Загружаем рынки с биржи
            markets = self.exchange.load_markets()
            
            # На Bybit даты зашиты в поле 'expiryDatetime' или в ID контракта
            expirations = set()
            for market in markets.values():
                if market.get('type') == 'option' and market.get('base') == base_coin:
                    # Извлекаем красивую строковую дату (например, '2026-07-03T08:00:00.000Z')
                    # и забираем из неё только саму дату YYYY-MM-DD
                    expiry_date = market.get('expiryDatetime')
                    if expiry_date:
                        expirations.add(expiry_date.split('T')[0])
            
            # Сортируем даты по порядку (от ближайшей к дальней)
            sorted_dates = sorted(list(expirations))
            dictSortedDates = {i:sorted_dates[i] for i in range(len(sorted_dates))}
            # Выводим один лаконичный лог
            logger.debug(f"{base_coin} expiration dates: {', '.join(sorted_dates)}")
            return dictSortedDates
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге дат экспирации для {base_coin}: {e}")
            return []

    def get_ticker_by_symbol(self, symbol='BTC'):
        symbol = symbol.upper() + 'USDT'
        """Максимально упрощенный метод. Передаем только готовый символ."""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            logger.info(f"{symbol} | Bid: {ticker.get('bid')} | Ask: {ticker.get('ask')}")
            ticker = ticker.get('bid')# + ticker.get('ask'))/2
            return ticker
        except Exception as e:
            logger.error(f"Ошибка получения цены для {symbol}: {e}")
            return None

    
    def get_option_strikes(self, base_coin="BTC", 
                           expiration_date="2026-06-29"):
        """
        Парсит и возвращает словарь со страйками:
        CALL — 4 ближайших страйка по возрастанию от текущей цены.
        PUT — 4 ближайших страйка по убыванию от текущей цены.
        """
        listCall = []
        listPut = []
        dateStrike = {}
        
        # Получаем текущую цену базового актива
        ticPrice = self.get_ticker_by_symbol(symbol=base_coin)
        
        # if isinstance(ticker_data, dict):
        #     ticPrice = float(ticker_data.get('last') or ticker_data.get('markPrice') or 0.0)
        # else:
        #     ticPrice = float(ticker_data)
            
        dateStrike['ticPrice'] = ticPrice
        
        try:
            markets = self.exchange.load_markets()
            # logger.info(f"markets[-1] {len(markets)} ")
            for symbol, market in markets.items():
                
                if market.get('type') == 'option' and market.get('base') == base_coin:
                    # logger.info(f"markets[-1] {markets} ")
                    expiry_date = market.get('expiryDatetime')
                    
                    if expiry_date and expiry_date.startswith(expiration_date):
                        strike = market.get('strike')
                        if strike is None:
                            continue
                        
                        strike = float(strike)
                        opt_type = market.get('optionType') or ('call' if symbol.endswith('-C') else 'put')
                        opt_type = opt_type.lower()

                        # 1. CALL: страйки выше текущей цены
                        if ticPrice < strike and opt_type == 'call':
                            if strike not in listCall:
                                listCall.append(strike)
                            
                        # 2. PUT: страйки ниже текущей цены
                        elif ticPrice > strike and opt_type == 'put':
                            if strike not in listPut:
                                listPut.append(strike)

            # =================================================================
            # СТРОГАЯ СОРТИРОВКА И ОГРАНИЧЕНИЕ ДО 4 СТРАЙКОВ
            # =================================================================
            
            # Сортируем CALL по возрастанию (от меньшего к большему) и берем первые 4
            dateStrike['strikeCall'] = sorted(listCall)[:4]
            
            # Сортируем PUT по убыванию (от большего к меньшему) и берем первые 4
            dateStrike['strikePut'] = sorted(listPut, reverse=True)[:4]
            
            # Чистый итоговый лог
            logger.debug(f"Сетка (4 страйка) для {base_coin} на {expiration_date}: {dateStrike}")
            
            return dateStrike
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге страйков для {base_coin} на {expiration_date}: {e}")
            return {}

  
    def get_option_premium_prices1(self, base_coin="BTC",
                                  expiration_date="2026-07-10", 
                                  strikes_grid=None):
        """
        Получает стоимость премий (Bid/Ask) для всей сетки страйков CALL и PUT.
        """
        if not strikes_grid:
            return {}

        try:
            # 1. Переводим дату из YYYY-MM-DD (2026-07-09) в формат Bybit (09JUL26)
            from datetime import datetime
            dt = datetime.strptime(expiration_date, "%Y-%m-%d")
            bybit_date_str = dt.strftime("%d%b%y").upper() # Пример: 09JUL26
            logger.info(f"bybit date str : {bybit_date_str}")
            # 2. Формируем список точных названий символов для биржи
            target_symbols = []
            
            # Собираем символы для CALL
            for strike in strikes_grid.get('strikeCall', []):
                strike_int = int(strike) if float(strike).is_integer() else strike
                target_symbols.append(f"{base_coin}-{bybit_date_str}-{strike_int}-C")
                
            # Собираем символы для PUT
            for strike in strikes_grid.get('strikePut', []):
                strike_int = int(strike) if float(strike).is_integer() else strike
                target_symbols.append(f"{base_coin}-{bybit_date_str}-{strike_int}-P")

            if not target_symbols:
                return {}

            # 3. Запрашиваем стоимости премий ОДНИМ пакетом
            logger.info(f"Запрос стоимости премий для {len(target_symbols)} контрактов...")
            tickers = self.exchange.fetch_tickers(target_symbols)
            
            logger.info("=" * 60)
            logger.info(f" СТОИМОСТЬ ПРЕМИЙ (ОПЦИОНЫ {base_coin} НА {expiration_date})")
            logger.info("=" * 60)
            
            # Выводим сначала CALL (сверху вниз по возрастанию страйка)
            logger.info("[ ОПЦИОНЫ CALL (Покупка рынка вверх) ]")
            for symbol in target_symbols:
                if symbol.endswith('-C'):
                    t = tickers.get(symbol, {})
                    bid = t.get('bid', 0.0) # Цена, за которую у вас купят опцион
                    ask = t.get('ask', 0.0) # Цена премия, которую вы платите при покупке
                    logger.info(f"  • {symbol} | Премия BUY (Ask): {ask} USD | Premium SELL (Bid): {bid} USD")

            logger.info("-" * 60)
            
            # Выводим PUT (сверху вниз по убыванию страйка)
            logger.info("[ ОПЦИОНЫ PUT (Покупка рынка вниз) ]")
            for symbol in target_symbols:
                if symbol.endswith('-P'):
                    t = tickers.get(symbol, {})
                    bid = t.get('bid', 0.0)
                    ask = t.get('ask', 0.0)
                    logger.info(f"  • {symbol} | Премия BUY (Ask): {ask} USD | Premium SELL (Bid): {bid} USD")
                    
            logger.info("=" * 60)
            return tickers

        except Exception as e:
            logger.error(f"Ошибка при получении стоимостей премий: {e}")
            return {}
  
  
    def get_option_premium_prices2(self, base_coin="BTC", expiration_date="2026-07-10", strikes_grid=None):
        """
        Получает стоимость премий (Bid/Ask) для актуальной сетки страйков CALL и PUT.
        Запрашивает все опционы разом, что гарантирует получение цен без сбоев CCXT.
        """
        if not strikes_grid:
            logger.warning("Сетка страйков пуста.")
            return {}

        try:
            # 1. Переводим дату из YYYY-MM-DD (2026-07-10) в формат Bybit (10JUL26)
            from datetime import datetime
            dt = datetime.strptime(expiration_date, "%Y-%m-%d")
            bybit_date_str = dt.strftime("%d%b%y").upper() # Результат: 10JUL26
            
            # 2. Формируем точный список символов, которые мы хотим отобразить
            target_symbols = []
            for strike in strikes_grid.get('strikeCall', []):
                target_symbols.append(f"{base_coin}-{bybit_date_str}-{int(strike)}-C")
            for strike in strikes_grid.get('strikePut', []):
                target_symbols.append(f"{base_coin}-{bybit_date_str}-{int(strike)}-P")

            # 3. Скачиваем ВСЕ опционные тикеры с биржи разом (это работает стабильно)
            logger.info("Загрузка актуальных котировок опционного рынка Bybit...")
            all_tickers = self.exchange.fetch_tickers(params={'category': 'option'})
            
            logger.info("=" * 60)
            logger.info(f" СТОИМОСТЬ ПРЕМИЙ (ОПЦИОНЫ {base_coin} НА {expiration_date})")
            logger.info("=" * 60)
            
            # 4. Вытаскиваем цены из общего массива котировок
            for side, label in [('-C', '[ ОПЦИОНЫ CALL (Вверх) ]'), ('-P', '[ ОПЦИОНЫ PUT (Вниз) ]')]:
                logger.info(label)
                for symbol in sorted(target_symbols):
                    if symbol.endswith(side):
                        # Ищем котировку в скачанном массиве по ключу символа
                        ticker = all_tickers.get(symbol, {})
                        
                        # Если CCXT хранит ключи без базовой монеты или в другом формате, 
                        # делаем резервный поиск по совпадению имени
                        if not ticker:
                            ticker = next((v for k, v in all_tickers.items() if symbol in k), {})

                        bid = ticker.get('bid', 0.0)
                        ask = ticker.get('ask', 0.0)
                        logger.info(f"  • {symbol} | Купить (Ask): {ask} USD | Продать (Bid): {bid} USD")
                logger.info("-" * 60)
                
            return all_tickers


        except Exception as e:
            logger.error(f"Ошибка при получении стоимостей премий: {e}")
            return {}
        
        
    def place_option_order(self, symbol: str, side: str, qty: float, price: float) -> dict:
        """
        Выставляет лимитный ордер на покупку или продажу опциона Bybit v5.
        
        :param symbol: Полный ID контракта Bybit v5 (например, "DOGE-17JUL26-0.009-C")
        :param side: Сторона сделки: 'buy' или 'sell'
        :param qty: Объем контракта (количество монет, например, 1000 для DOGE)
        :param price: Лимитная цена в USDT, по которой хотим войти
        :return: Ответ от биржи со статусом ордера или None при ошибке
        """
        # Принудительно приводим параметры к стандартным регистрам Bybit
        side = side.lower()         # 'buy' или 'sell'
        symbol = symbol.upper()     # Строго заглавные буквы
        
        # Проверка базовой валидности параметров перед отправкой
        if side not in ['buy', 'sell']:
            logger.error(f"Неверная сторона ордера: {side}. Допустимы только 'buy' или 'sell'.")
            return None

        try:
            logger.info(f"Отправка ордера: {side.upper()} {qty} {symbol} по цене {price}...")
            
            # Используем универсальный метод CCXT create_order с флагом категории опционов
            response = self.exchange.create_order(
                symbol=symbol,
                type='limit',       # Опционы на Bybit торгуются лимитными ордерами
                side=side,
                amount=qty,
                price=price,
                params={
                    'category': 'option',       # Указываем, что это рынок опционов Bybit v5
                    'timeInForce': 'GTC'        # Good 'Til Cancelled — ордер активен, пока не исполнится или не будет отменен
                }
            )
            
            # Проверяем успешность выставления ордера по ответу CCXT
            order_id = response.get('id')
            logger.info(f"Ордер успешно размещен! ID ордера: {order_id}")
            return response

        except Exception as e:
            logger.error(f"Ошибка при выставлении ордера на {symbol}: {e}")
            return None


    def place_option_order2(self, symbol: str, side: str,
                            qty: float, price: float) -> dict:
        """
        Выставляет лимитный ордер на покупку или продажу опциона.
        Использует исключительно универсальные стандарты CCXT для кроссплатформенности.
        
        ВХОДНЫЕ ДАННЫЕ (INPUT DATA):
        ----------------------------
        :param symbol: Биржевая маркировка контракта. Принимает чистый ID от Bybit 
                       в формате строки. Пример: "BTC-14JUL26-63000-C" (без точек в страйке).
        :param side:   Сторона сделки. Строка: 'buy' (покупка опциона / лонг волатильности) 
                       или 'sell' (продажа опциона / шорт волатильности / сбор премии).
        :param qty:    Объем ордера в количестве контрактов/монет (тип float или int). 
                       Пример: 0.01 для Биткоина или 1000.0 для DOGE.
        :param price:  Лимитная цена ордера (тип float). Это расчетная стоимость премии опциона, 
                       полученная из Блэка-Шоулза. Пример: 150.9 (а не цена самого спота BTC).
                       
        :return:       Словарь с ответом от биржи и параметрами ордера или None при ошибке.
        """
        try:
            # --- ШАГ 1: АВТОМАТИЧЕСКАЯ КОНВЕРТАЦИЯ СИМВОЛА В СТАНДАРТ CCXT ---
            # Принудительно переводим строку в верхний регистр (Caps Lock) и делим по дефисам
            # Из строки "BTC-14JUL26-63000-C" получаем список: ['BTC', '14JUL26', '63000', 'C']
            parts = symbol.upper().split('-')
            
            if len(parts) == 4:
                base_coin, date_str, strike, option_type = parts
                
                # Конвертируем текстовую дату из формата Bybit "14JUL26" в объект даты Python
                parsed_date = datetime.strptime(date_str, "%d%b%y")
                # Переводим дату в цифровой формат CCXT "260714" (ГодМесяцДень)
                ccxt_date = parsed_date.strftime("%y%m%d")
                
                # Собираем официальный кроссплатформенный символ CCXT, который поймет любая биржа.
                # Результат сборки: "BTC/USDT:USDT-260714-63000-C"
                ccxt_symbol = f"{base_coin}/USDT:USDT-{ccxt_date}-{strike}-{option_type}"
            else:
                # Если символ уже изначально пришел в правильном формате CCXT
                ccxt_symbol = symbol

            safe_price = float(self.exchange.price_to_precision(ccxt_symbol, price))
            # Логируем промежуточные данные для отладки в консоли
            logger.info(f"Входной биржевой символ: {symbol} -> Сконвертирован в CCXT: {ccxt_symbol}")
            logger.info(f"Параметры ордера: {side.upper()} {qty} контрактов по лимитной цене {price}")
            
            # --- ШАГ 2: ОТПРАВКА УНИФИЦИРОВАННОГО ОРДЕРА ЧЕРЕЗ CCXT ---
            # Этот метод одинаков для ВСЕХ бирж в библиотеке CCXT
            response = self.exchange.create_order(
                symbol=ccxt_symbol,         # Передаем наш собранный универсальный символ
                type='limit',               # Опционы на криптобиржах торгуются только лимитными ордерами
                side=side.lower(),          # Приводим сторону строго к маленьким буквами ('buy' или 'sell')
                amount=qty,                 # Объем контракта
                price=safe_price,                # Цена премии
                params={
                    'category': 'option',   # Специфичный маркер Bybit v5 API (другие биржи его проигнорируют)
                    'timeInForce': 'GTC'    # Ордер «Good 'Til Cancelled» — висит в стакане, пока не исполнится или не отменится
                }
            )
            
            # Извлекаем уникальный ID созданного ордера из ответа CCXT
            order_id = response.get('id')
            logger.info(f"Ордер успешно размещен на бирже! Присвоен ID ордера: {order_id}")
            return response

        except Exception as e:
            # Ловим любые сетевые ошибки, нехватку маржи или неверные параметры, не останавливая бота
            logger.error(f"Критическая ошибка CCXT при выставлении ордера на {symbol}: {e}")
            return None
        
        
# =================================================
# функция котороя открывает стратегию "бетман" и 
# перебирает премии чтоб улучшить вход
# =================================================


    def chase_order(self, symbol: str, 
             side: str, 
             qty: float, 
             price_limit: float, 
             check_interval_sec: int = 5,
             slippage_step_pct: float = 1.0,   # Шаг уступки в % (Step 1%)
             max_slippage_pct: float = 5.0) -> bool:  # Максимальная общая уступка в 
        
        """
         Универсальный алгоритм преследования цены (Chase) для неликвидных опционов.
        :param symbol: Код опциона в формате CCXT (например, "SOL-14JUL26-77-C")
        :param side: 'buy' (для Long ног) или 'sell' (для Short ног)
        :param qty: Количество контрактов
        :param price_limit: Максимальная цена для buy (не переплачивать) или минимальная цена для sell (не отдавать дешево)
        :param check_interval_sec: Пауза между проверками стакана
        :param slippage_step_pct: float = 1.0,   # Шаг уступки в % (Step 1%)
        :param max_slippage_pct: float = 5.0) -> bool:  # Максимальная общая уступка в  
        :return: True если полностью исполнен, False если отменен по лимиту цены
        """

        side = side.lower()
        logger.info(f"Запуск Чистого Chase Order [{side.upper()}] для {symbol}. Базовый лимит: {price_limit}")

        # === ШАГ 1: ПЕРЕВОД СИМВОЛА В ВАШ СТАНДАРТ CCXT ДЛЯ ЗАПРОСА СТАКАНА ===
        # peresobiraem symbol pod CCXT
        parts = symbol.upper().split('-')
        if len(parts) == 4:
            base_coin, date_str, strike, option_type = parts
            parsed_date = datetime.strptime(date_str, "%d%b%y")
            ccxt_symbol = f"{base_coin}/USDT:USDT-{parsed_date.strftime('%y%m%d')}-{strike}-{option_type}"
        else:
            ccxt_symbol = symbol

        # === ШАГ 2: ДИНАМИЧЕСКИЙ ПОДБОР ПАРАМЕТРОВ С БИРЖИ (Вместо хардкода монет) ===
        try:
            # Берем спецификацию контракта из памяти CCXT
            market = self.exchange.market(ccxt_symbol)
            
            # Автоматически вытаскиваем точный шаг цены (напр. 0.0001 для XRP, 0.01 для SOL)
            tick_size = float(market['precision']['price'])
            
            # Автоматически вытаскиваем количество знаков после запятой (напр. 4 или 2)
            decimals = int(market['precision']['price_decimals']) if 'price_decimals' in market['precision'] else 4
            
            logger.info(f"⚙️ Биржа вернула параметры для {ccxt_symbol}: Шаг цены={tick_size}, Округление={decimals}")
        except Exception as e:
            logger.error(f"❌ Не удалось динамически получить параметры рынка для {ccxt_symbol}: {e}")
            logger.warning("Применяем защитные настройки по умолчанию (шаг 0.0001, 4 знака).")
            tick_size = 0.0001
            decimals = 4

        # === ШАГ 3: ОПРЕДЕЛЕНИЕ СТАРТОВОЙ ЦЕНЫ ВХОДА БЕЗ ПЕРЕБОРОВ ===
        if side == 'buy':
            # Для покупки: стартуем на 1 шаг выше лучшего покупателя в стакане
            try:
                orderbook = self.exchange.fetch_order_book(ccxt_symbol)
                best_bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else 0.0
            except Exception:
                best_bid = 0.0
            current_target_price = round(best_bid + tick_size, decimals)
            
            if current_target_price > price_limit * 1.7: #perschitivaem premia  do 40%
                logger.warning(f"Рынок слишком дорогой для старта покупки"
                               f"({current_target_price} > {price_limit}). Отмена.")
                return False
        else:
            # === ДЛЯ КОНКРЕТНОГО SELL ===
            # 1. Стартуем продажи строго сверху — с вашей теоретической премии!
            current_target_price = round(price_limit, decimals)
            
            # 2. Запрашиваем стакан только для защитной проверки безопасности
            try:
                orderbook = self.exchange.fetch_order_book(ccxt_symbol)
                best_ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else 999999.0
            except Exception:
                best_ask = current_target_price
            
            # 3. ЗАЩИТА: Если реальный рынок (best_ask) упал на самое дно (ниже 70% от теории),
            # то выставлять ордер по теории нет смысла — его никто не купит, а если упадет dynamic_limit, 
            # мы продадим за бесценок. Отменяем сделку.
            if best_ask < price_limit * 0.3:
                logger.warning(f"Рынок слишком дешев для продажи. Лучший Ask в стакане"
                               f" ({best_ask}) ниже 70% от теории"
                               f" ({round(price_limit * 0.7, decimals)}). Отмена.")
                return False
                
            logger.info(f"Выставляем ордер SELL сразу в стакан по теоретической цене: "
                        f" {current_target_price}. (Рыночный Ask: {best_ask})")
            
            

        # === ШАГ 4: МГНОВЕННОЕ РАЗМЕЩЕНИЕ СТАРТОВОГО ОРДЕРА ===
        # Вызываем вашу проверенную функцию place_option_order2
        response = self.place_option_order2(symbol, side, qty, current_target_price)
        if not response or 'id' not in response:
            logger.error("Не удалось разместить стартовый ордер на бирже.")
            return False
            
        order_id = response['id']
        accumulated_slippage = 0.0  # Суммарный процент уступки маркету

        # === ШАГ 5: ОСНОВНОЙ ЦИКЛ ПРЕСЛЕДОВАНИЯ ВНУТРИ СТАКАНА ===
        while True:
            # Уважаем задержку времени, переданную из интерфейса main.py
            time.sleep(check_interval_sec)

            # --- ИСПРАВЛЕНИЕ: ЖЕЛЕЗОБЕТОННАЯ ПРОВЕРКА ЧЕРЕЗ АКТИВНЫЕ ПОЗИЦИИ ---
            # Вызываем ваш метод проверки живых открытых опционов
            live_positions = self.get_active_open_options()
            
            # Ищем, появилась ли наша нога в списке реальных позиций на балансе
            # Сравниваем строго с исходным красивым именем (напр. SOL-31JUL26-76-P)
            is_position_opened = any(pos['symbol'] == symbol for pos in live_positions)

            if is_position_opened:
                logger.info(f"🎉 ПОДТВЕРЖДЕНО ПОЗИЦИЕЙ: Опцион {symbol} успешно прошел и удерживается на балансе аккаунта!")
                return True

            # --- ЗАПАСНАЯ ПРОВЕРКА ЧЕРЕЗ СТАТУС ОРДЕРА ---
            # Вызываем функцию check_order_status (с params={'category': 'option'} внутри)
            status = self.check_order_status(order_id, ccxt_symbol)
            
            if status == 'closed':
                logger.info(f"🎉 Нога {symbol} [{side.upper()}] ПОЛНОСТЬЮ ИСПОЛНЕНА по данным статуса ордера!")
                return True

            if status == 'canceled':
                logger.warning(f"Ордер {order_id} был неожиданно отменен.")
                return False

            if status == 'error':
                logger.info("Временный сбой сети при проверке ордера. Ждем следующий круг...")
                continue

            # --- ШАГ 5: ОБНОВЛЕНИЕ СТАКАНА И СДВИГ ЦЕНЫ НА 1% (Если сделка еще не прошла) ---
            try:
                orderbook = self.exchange.fetch_order_book(ccxt_symbol)
            except Exception:
                continue

            # Логика плавного скольжения лимитки для ПРОДАЖИ (Sell)
            if side == 'sell':
                best_ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else 999999.0
                
                # Если нас перебили конкуренты и цена Ask ушла ниже нашего ордера
                if best_ask < current_target_price:
                    accumulated_slippage += slippage_step_pct
                    
                    if accumulated_slippage > max_slippage_pct:
                        logger.warning(f"Достигнут предел уступки ({max_slippage_pct}%). Снимаем ордер с торгов.")
                        self._safe_cancel(order_id, ccxt_symbol)
                        return False
                        
                    # Делаем скидку 1% от изначальной теоретической стоимости
                    new_target_price = round(price_limit * (1 - accumulated_slippage / 100), decimals)
                    logger.info(f"Ордер не исполнен. Уступаем рынку -{slippage_step_pct}%. Снижаем цену SELL до: {new_target_price}")
                    
                    # Отменяем старый ордер и выставляем новый ниже по цене
                    self._safe_cancel(order_id, ccxt_symbol)
                    response = self.place_option_order2(symbol, side, qty, new_target_price)
                    if response and 'id' in response:
                        order_id = response['id']
                        current_target_price = new_target_price

            # Логика плавного скольжения лимитки для ПОКУПКИ (Buy)
            else:  # buy
                best_bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else 0.0
                
                # Если покупатели подняли ставки выше нашего ордера
                if best_bid > current_target_price:
                    accumulated_slippage += slippage_step_pct
                    
                    if accumulated_slippage > max_slippage_pct:
                        logger.warning(f"Достигнут предел уступки для покупки. Снимаем ордер.")
                        self._safe_cancel(order_id, ccxt_symbol)
                        return False
                        
                    # Повышаем планку нашего бюджета на +1%
                    new_target_price = round(price_limit * (1 + accumulated_slippage / 100), decimals)
                    logger.info(f"Покупатели перебили нас. Повышаем цену BUY до: {new_target_price}")
                    
                    # Отменяем старый ордер и выставляем новый выше по цене
                    self._safe_cancel(order_id, ccxt_symbol)
                    response = self.place_option_order2(symbol, side, qty, new_target_price)
                    if response and 'id' in response:
                        order_id = response['id']
                        current_target_price = new_target_price
                        

    def check_order_status(self, order_id: str, symbol: str) -> str:
        """
        Отдельная защищенная функция для проверки текущего статуса ордера на Bybit.
        Универсально проверяет формат символа и защищает от варнингов CCXT.
        """
        # === КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ ТУТ ===
        # Проверяем: если символ уже в формате CCXT (содержит '/' или ':')
        if "/" in symbol or ":" in symbol:
            ccxt_symbol = symbol
        else:
            # Если пришел "грязный" символ от математики (напр. XRP-27JUL26-1.12-C)
            try:
                parts = symbol.upper().split('-')
                if len(parts) == 4:
                    base_coin, date_str, strike, option_type = parts
                    parsed_date = datetime.strptime(date_str, "%d%b%y")
                    ccxt_symbol = f"{base_coin}/USDT:USDT-{parsed_date.strftime('%y%m%d')}-{strike}-{option_type}"
                else:
                    ccxt_symbol = symbol
            except Exception:
                ccxt_symbol = symbol

        try:
            # Передаем обязательный параметр category: option
            order_info = self.exchange.fetch_order(
                order_id, 
                ccxt_symbol, 
                params={'category': 'option'}
            )
            # Возвращает статус: 'open', 'closed' (filled) или 'canceled'
            return order_info.get('status', 'open')
            
        except Exception as e:
            logger.warning(f"Временный сбой сети при fetch_order для {order_id}: {e}")
            return 'error'



    def _replace_order(self, old_id: str, symbol: str, side: str, qty: float, new_price: float) -> str:
        """Внутренний метод перевыставления ордера через Cancel + Create"""
        self._safe_cancel(old_id, symbol)
        try:
            new_order = self.exchange.create_order(
                symbol=symbol, type='limit', side=side, amount=qty, price=new_price
            )
            logger.info(f"Лимит сдвинут до: {new_price} USDT (Новый ID: {new_order['id']})")
            return new_order['id']
        except Exception as e:
            logger.error(f"Критическая ошибка при перевыставлении ордера: {e}")
            # Возвращаем старый ID, чтобы цикл попытался обработать его или завершиться
            return old_id

    def _safe_cancel(self, order_id: str, symbol: str):
        """Внутренний безопасный метод отмены ордера"""
        try:
            self.exchange.cancel_order(order_id, symbol)
        except Exception:
            # Игнорируем ошибку, если ордер исполнился прямо в момент отмены
            pass

    def analyze_open_options(self, base_currency: str = "DOGE") -> dict:
        """
        Синхронный анализ аккаунта на наличие открытых позиций, ордеров и маржи.
        
        :param base_currency: Название базового актива (DOGE, SOL, BTC)
        :return: Словарь с результатами анализа
        """
        logger.info(f"Запуск синхронного анализа аккаунта для опционов {base_currency}...")
        
        # Шаблон итогового отчета
        report = {
            "has_open_positions": False,
            "has_open_orders": False,
            "free_margin_usdt": 0.0,
            "existing_positions": [],
            "existing_orders": []
        }

        # 1. ПРОВЕРКА СВОБОДНОЙ МАРЖИ (Unified Trading Account)
        try:
            balance = self.exchange.fetch_balance()
            # Для Единого торгового аккаунта Bybit баланс маржи лежит в параметрах USDT или USDC
            usdt_wallet = balance.get('USDT', {})
            report["free_margin_usdt"] = float(usdt_wallet.get('free', 0.0))
            logger.info(f"Доступная свободная маржа: {report['free_margin_usdt']} USDT")
        except Exception as e:
            logger.error(f"Не удалось получить баланс маржи: {e}")

        # 2. ПРОВЕРКА ОТКРЫТЫХ ПОЗИЦИЙ
        try:
            # Для Единого маржинального аккаунта Bybit передаем subType: linear или option
            positions = self.exchange.fetch_positions(params={"subType": "option"}) 
            
            for pos in positions:
                symbol = pos.get('symbol', '')
                # Ищем опционы, в названии которых есть наша монета (например, DOGE-15JUL26-0.076-C)
                if base_currency in symbol and '-' in symbol:
                    contracts = float(pos.get('contracts', 0.0))
                    
                    # Если позиция имеет объем (не закрыта)
                    if contracts != 0:
                        report["has_open_positions"] = True
                        report["existing_positions"].append({
                            "symbol": symbol,
                            "side": pos.get('side'),
                            "size": contracts,
                            "entry_price": pos.get('entryPrice')
                        })
                        logger.warning(f"⚠️ Найдена открытая позиция: {symbol} | Размер: {contracts} | Сторона: {pos['side']}")
                        
            if not report["has_open_positions"]:
                logger.info(f"Открытых позиций по опционам {base_currency} не обнаружено.")
                
        except Exception as e:
            logger.error(f"Ошибка при анализе открытых позиций: {e}")

        # 3. ПРОВЕРКА АКТИВНЫХ ОРДЕРОВ В СТАКАНЕ
        try:
            # Запрашиваем только открытые лимитные ордера в категории опционов
            open_orders = self.exchange.fetch_open_orders(params={"category": "option"})
            
            for order in open_orders:
                symbol = order.get('symbol', '')
                if base_currency in symbol:
                    report["has_open_orders"] = True
                    report["existing_orders"].append({
                        "id": order.get('id'),
                        "symbol": symbol,
                        "side": order.get('side'),
                        "price": order.get('price'),
                        "qty": order.get('amount')
                    })
                    logger.warning(f"⚠️ Найден активный ордер в стакане: {symbol} (ID: {order['id']})")
                    
            if not report["has_open_orders"]:
                logger.info(f"Активных ордеров по опционам {base_currency} в стакане нет.")
                
        except Exception as e:
            logger.error(f"Ошибка при анализе открытых ордеров: {e}")

        return report
    
    
    def get_active_open_options(self) -> list:
        """
        Находит все открытые позиции по опционам на аккаунте, 
        которые еще НЕ вышли из срока экспирации (активные живые контракты).
        
        Возвращает привычный формат символа (напр. SOL-31JUL26-76-P) и направление buy/sell.
        :return: Список словарей с параметрами активных опционов
        """
        logger.info("Запуск проверки открытых и неэкспирированных опционов...")
        active_options = []
        
        # Получаем текущее время сервера Bybit в миллисекундах
        try:
            current_timestamp = self.exchange.milliseconds()
        except Exception:
            current_timestamp = int(datetime.utcnow().timestamp() * 1000)

        try:
            # Запрашиваем только открытые позиции по опционам
            positions = self.exchange.fetch_positions(params={
                "category" : "linear",
                "settleCoin" : "USDT"})
                
                # "subType": "option"})
            
            for pos in positions:
                ccxt_symbol = pos.get('symbol', '') # Приходит: SOL/USDT:USDT-260731-76-P
                contracts = float(pos.get('contracts', 0.0)) # Объем позиции
                
                # Проверяем, что позиция действительно удерживается (объем не равен нулю)
                if contracts != 0:
                    
                    # === 1. ПЕРЕВОД ВНУТРЕННЕГО ИМЕНИ CCXT В ВАШ СТАНДАРТНЫЙ SYMBOL ===
                    # Из "SOL/USDT:USDT-260731-76-P" вытаскиваем "260731-76-P"
                    if '-' in ccxt_symbol:
                        symbol_parts = ccxt_symbol.split('-')
                        base_coin = ccxt_symbol.split('/')[0] # 'SOL'
                        
                        ccxt_date = symbol_parts[1]   # '260731'
                        strike = symbol_parts[2]      # '76'
                        option_type = symbol_parts[3] # 'P'
                        
                        # Конвертируем инвертированную дату "260731" обратно в формат Bybit "31JUL26"
                        try:
                            parsed_date = datetime.strptime(ccxt_date, "%y%m%d")
                            bybit_date_str = parsed_date.strftime("%d%b%y").upper() # '31JUL26'
                            
                            # Собираем ваш стандартный красивый символ
                            clean_symbol = f"{base_coin}-{bybit_date_str}-{strike}-{option_type}"
                        except Exception:
                            clean_symbol = ccxt_symbol # Если сбой, оставляем как есть
                    else:
                        clean_symbol = ccxt_symbol

                    # === 2. ОПРЕДЕЛЕНИЕ СТРОГОГО НАПРАВЛЕНИЯ BUY ИЛИ SELL ===
                    # В CCXT для позиций: pos['side'] возвращает 'long' (покупка) или 'short' (продажа)
                    raw_side = pos.get('side', '').lower()
                    buy_or_sell = 'buy' if raw_side == 'long' else 'sell'

                    # === 3. БЛОК ПРОВЕРКИ ДАТЫ ЭКСПИРАЦИИ ===
                    try:
                        parts = ccxt_symbol.split('-')
                        if len(parts) >= 2:
                            date_str = parts[1] # "260731"
                            
                            # Экспирация на Bybit всегда фиксируется в 08:00 UTC
                            exp_date = datetime.strptime(date_str, "%y%m%d").replace(hour=8, minute=0)
                            exp_timestamp = int(exp_date.timestamp() * 1000)
                            
                            # Если время жизни контракта больше текущего — опцион активен!
                            if exp_timestamp > current_timestamp:
                                time_left_hours = (exp_timestamp - current_timestamp) / (1000 * 60 * 60)
                                
                                # Добавляем опцион в финальный массив с вашими точными ключами
                                active_options.append({
                                    "symbol": clean_symbol,                     # Напр: SOL-31JUL26-76-P
                                    "buyOrSell": buy_or_sell,                   # Напр: 'sell' или 'buy'
                                    "size": contracts,                          # Объем контрактов
                                    "entry_price": float(pos.get('entryPrice', 0.0)),
                                    "hours_to_expiration": round(time_left_hours, 2)
                                })
                                logger.debug(f"🟢 Найдена живая позиция: {clean_symbol} | Действие: {buy_or_sell.upper()} | Осталось: {round(time_left_hours, 2)} ч.")
                            else:
                                logger.warning(f"🔴 Опцион {clean_symbol} находится в процессе экспирации. Игнорируем.")
                    except Exception as e:
                        logger.error(f"Ошибка парсинга времени для {ccxt_symbol}: {e}")
                        continue
                        
            logger.debug(f"Анализ завершен. Найдено активных неэкспирированных опционов: {len(active_options)}")
            
        except Exception as e:
            logger.error(f"Критическая ошибка fetch_positions: {e}")
            
        return active_options
    
    def get_active_open_options2(self) -> list:
        """
        Находит все открытые позиции по опционам на аккаунте, 
        которые еще НЕ вышли из срока экспирации (активные живые контракты).
        
        ОТБОР И ФИЛЬТРАЦИЯ (КРИТИЧЕСКИ ДЛЯ ДЕЛЬТА-ХЕДЖА):
        -----------------------------------------------
        Функция автоматически ИСКЛЮЧАЕТ из выдачи все опционы, для которых 
        на бирже Bybit включен встроенный режим авто-хеджирования DDH (Dynamic Delta Hedging).
        Это защищает кастомный модуль хеджирования от конфликтов с автоматикой биржи.
        Опционы под защитой DDH (например, SOL, DOGE) логируются и игнорируются.
        
        Возвращает привычный формат символа (напр. SOL-31JUL26-76-P) и направление buy/sell.
        :return: Список словарей с параметрами активных НЕЗАЩИЩЕННЫХ опционов
        """

        logger.info("Запуск универсальной проверки открытых опционов...")
        active_options = []
        
        try:
            current_timestamp = self.exchange.milliseconds()
        except Exception:
            current_timestamp = int(datetime.utcnow().timestamp() * 1000)

        try:
            # === УНИВЕРСАЛЬНЫЙ СТАНДАРТ CCXT ===
            # Для Bybit эти параметры обязательны, а другие биржи (Deribit/OKX) 
            # их просто проигнорируют и вернут список позиций по своим правилам!
            positions = self.exchange.fetch_positions(params={
                "category": "linear",
                "settleCoin": "USDT"
            })
            
            logger.info(f"Успешно получено {len(positions)} позиций через стандарт CCXT.")
            
            for pos in positions:
                # CCXT автоматически приводит ответ любой биржи к единому стандарту!
                # На любой бирже имя будет в 'symbol', а объем в 'contracts'
                ccxt_symbol = pos.get('symbol', '')
                contracts = float(pos.get('contracts', 0.0))
                
                # Фильтруем только открытые опционы
                # (В USDT-опционах Bybit и в опционах Deribit всегда есть дефис и тип ноги C/P)
                if contracts != 0 and "-" in ccxt_symbol and ("-C" in ccxt_symbol or "-P" in ccxt_symbol):
                    
                    # Наш умный OptionAsset сам разберется с синтаксисом конкретной биржи
                    asset = OptionAsset(raw_symbol=ccxt_symbol, exchange_instance=self.exchange)
                    
                    raw_side = pos.get('side', '').lower()
                    buy_or_sell = 'buy' if raw_side == 'long' else 'sell'
                    
                    # CCXT стандартизирует даже время экспирации! Поле 'expiry' есть в market-данных любой биржи
                    market_data = self.exchange.markets.get(ccxt_symbol, {})
                    expiry_timestamp = market_data.get('expiry', 0)
                    
                    if expiry_timestamp == 0 or expiry_timestamp > current_timestamp:
                        time_left_hours = (expiry_timestamp - current_timestamp) / (1000 * 60 * 60) if expiry_timestamp > 0 else 99.0
                        
                        active_options.append({
                            "symbol": asset.raw_symbol,
                            "buyOrSell": buy_or_sell,
                            "size": contracts,
                            "entry_price": float(pos.get('entryPrice', 0.0)), # В стандарте CCXT цена всегда в entryPrice
                            "hours_to_expiration": round(time_left_hours, 2),
                            "strike": asset.strike,
                            "type": asset.type,
                            "futures_symbol": asset.futures_symbol
                        })
                        logger.info(f"🟢 Найдена позиция: {ccxt_symbol} | Объем: {contracts} | {buy_or_sell.upper()}")
            
            logger.info(f"Анализ завершен. Найдено активных опционов: {len(active_options)}")

        except Exception as e:
            logger.error(f"Критическая ошибка fetch_positions: {e}")
            
        return active_options

  
    def set_futures_leverage(self, base_currency: str, leverage: int = 10) -> bool:
        """
        Отдельная функция для принудительной установки кредитного плеча на фьючерсах Bybit.
        Рекомендуется вызывать ОДИН РАЗ при старте бота или выборе монеты.
        
        :param base_currency: Название монеты (MNT, DOGE, SOL, BTC)
        :param leverage: Размер кредитного плеча (например, 5, 10, 20)
        :return: True если успешно или уже установлено, False при критической ошибке
        """
        base_currency = base_currency.upper()
        futures_symbol = f"{base_currency}/USDT:USDT"
        
        logger.info(f"⚙️ Запрос на установку плеча {leverage}x для фьючерса {futures_symbol}...")
        
        try:
            # Вызываем метод CCXT v5 для Единого торгового аккаунта
            self.exchange.set_leverage(
                leverage=leverage,
                symbol=futures_symbol,
                params={'category': 'linear'}
            )
            logger.info(f"✅ Кредитное плечо {leverage}x для {futures_symbol} успешно подтверждено биржей.")
            return True
            
        except Exception as e:
            # Bybit v5 API возвращает ошибку, если вы пытаетесь установить то же самое плечо, 
            # которое уже выбрано в терминале. Мы это обрабатываем как УСПЕХ.
            err_msg = str(e).lower()
            if "leverage not modified" in err_msg or "110043" in err_msg or "not modified" in err_msg:
                logger.info(f"ℹ️ Плечо {leverage}x для {futures_symbol} уже установлено на аккаунте. Пропускаем.")
                return True
                
            logger.error(f"❌ Не удалось установить плечо для {futures_symbol}: {e}")
            return False
    

    def place_futures_hedge_order(self,
                                  base_currency: str, 
                                  side: str, 
                                  qty: float) -> dict:

        """
        Открывает фьючерсную позицию (линейный бессрочный контракт) для хеджирования опционов.
        Работает напрямую по API Bybit в обход локального кэша CCXT.
        
        ВХОДНЫЕ ДАННЫЕ:
        ---------------
        :param base_currency: Название монеты крупными буквами. Пример: 'DOGE', 'SOL', 'BTC'.
        :param side:          Направление хэджа. Строка: 'buy' (Long-хэдж) или 'sell' (Short-хэдж).
        :param qty:           Объем хэджа в количестве монет базового актива. Пример: 500.0 или 1.0.
        """
        # Принудительно форматируем входные строки к стандартам биржи
        base_currency = base_currency.upper()
        side = side.lower()
        
        # Строим линейный символ, который Bybit v5 API ожидает в категории 'linear'
        # Из 'DOGE' получаем 'DOGE/USDT:USDT'
        futures_symbol = f"{base_currency}/USDT:USDT"
        
        logger.info(f"⚡ Подготовка модуля хеджирования: {side.upper()} {qty} фьючерсов {futures_symbol}")

        try:
            # === ШАГ 1: КОРРЕКЦИЯ ЛОТНОСТИ (ОБЪЕМА) ДЛЯ РАЗНЫХ МОНЕТ ===
            # Так как мы обходим кэш markets, робот сам знает структуру контрактов Bybit:
            if "DOGE" in futures_symbol:
                safe_qty = int(qty)       # Для DOGE объем может быть только целым (минимальный шаг = 1 монета)
            elif "BTC" in futures_symbol:
                safe_qty = round(qty, 3)  # Для Биткоина шаг объема очень мелкий (до 0.001 BTC)
            # elif "MNT" in futures_symbol: 
            #     safe_qty = round(qty, 2)
            else:
                safe_qty = round(qty, 1)  # Для Соланы и Эфира лотность идет до 1 знака (напр. 0.1 SOL)

            # === КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: ОПРЕДЕЛЯЕМ ИНДЕКС ДЛЯ HEDGE MODE ===
            # Bybit v5 требует: 1 - для Long (buy), 2 - для Short (sell)
            position_index = 1 if side == 'buy' else 2
            
            # === ШАГ 2: ОТПРАВКА СРОЧНОГО МАРКЕТ-ОРДЕРА ===
            # Мы используем тип 'market', чтобы хэдж сработал мгновенно по стакану.
            response = self.exchange.create_order(
                symbol=futures_symbol,
                type='market',            # Исполняется моментально по текущей рыночной цене
                side=side,                # 'buy' или 'sell'
                amount=safe_qty,          # Скорректированный объем лота
                params={
                    'category': 'linear',  # Указываем Bybit, что это рынок бессрочных фьючерсов
                    'positionIdx': position_index
                }
            )
            
            order_id = response.get('id', 'Неизвестный ID')
            logger.info(f"🎯 Фьючерсный хедж успешно размещен на бирже! Присвоен ID ордера: {order_id}")
            return response

        except Exception as e:
            logger.error(f"❌ Критическая ошибка при открытии фьючерсного хеджа для {futures_symbol}: {e}")
            return None
    
    def get_active_futures_positions(self) -> dict:
        """
        Находит все активные открытые фьючерсные позиции (Linear Perpetual USDT) 
        на аккаунте.
        
        :return: Словарь вида {'BTC': {'side': 'buy', 'size': 0.1},
        'XRP': {'side': 'sell', 'size': 500}}
        """
        logger.info("Сканирование аккаунта на наличие открытых фьючерсов хеджа...")
        active_futures = {}

        try:
            # Запрашиваем позиции Единого аккаунта из сектора linear
            positions = self.exchange.fetch_positions(params={
                "category": "linear",
                "settleCoin": "USDT"
            })
            
            if isinstance(positions, dict):
                positions_list = positions.get('result', {}).get('list', [])
            elif isinstance(positions, list):
                positions_list = positions
            else:
                positions_list = []

            for pos in positions_list:
                logger.debug(f"fucher-pos {pos}")
                symbol = pos.get('symbol', '') # Напр: "XRPUSDT" или "SOLUSDT"
                try:
                    contracts = float(pos.get('size', pos.get('contracts', 0.0)))
                    entryPrice = float(pos.get('entryPrice', ''))
                    leverage = float(pos.get("leverage", ""))
                    initialMargin = float(pos.get('initialMargin', ''))
                except Exception:
                    contracts = 0.0

                # ФИЛЬТР ЧИСТОГО ФЬЮЧЕРСА: объем не равен 0, и в названии НЕТ опционных дефисов
                if contracts != 0 and "-" not in symbol:
                    # Извлекаем чистый тикер монеты (убираем суффикс 'USDT')
                    coin = symbol.replace("USDT", "").upper()
                    
                    raw_side = pos.get('side', '').lower()
                    # Приводим к единому стандарту направления сделок
                    side = 'buy' if raw_side in ['long', 'buy'] else 'sell'
                    
                    active_futures[coin[0:-2]] = {
                        "symbol": symbol,       # "XRPUSDT"
                        "side": side,           # "buy" (Long) или "sell" (Short)
                        "size": abs(contracts), # Объем фьючерса
                        "openPrice": entryPrice, # price sell or buy 
                        "leverage": leverage, 
                        "initMargin": initialMargin #count init cach
                    }
                    logger.debug(f"🏴‍☠️ Найдена активная фьючерсная позиция: {symbol} | {side.upper()} | Объем: {abs(contracts)}")

            logger.info(f"Сканирование завершено. Всего открытых фьючерсов: {len(active_futures)}")
            
        except Exception as e:
            logger.error(f"❌ Крах при получении фьючерсных позиций: {e}")
            
        return active_futures

        
        
    def process_hedging_logic(self, buffer_pct: float = 0.005) -> bool:
        # nuzno sdelat provercu na nalichie otcritogo fuchersa
        # i size chtob ponimat skolko docupat fuchrsa
        # esli fuchers otcrit i on zashishaet position to continue
        # esli zashls za stryke i no fuchers zashishaem position
        
        """
        Шаги 10, 12, 13 плана: Автоматическое дельта-хеджирование проданных опционов.
        Полностью обновлено с использованием универсального ядра OptionAsset.
        
        :param buffer_pct: Зазор безопасности в долях (0.005 = 0.5%) для защиты от шума на страйке.
        :return: True если цикл проверок прошел успешно, False при критической ошибке.
        
        list_coin = ["btc", "eth", "xrp", "sol", "doge"]
 

        open_options = [{
        'symbol': 'SOL/USDT:USDT-260807-73-P', 
        'ccxt_symbol': 'SOL/USDT:USDT-260807-73-P', 
        'buyOrSell': 'sell', 
        'size': 2.0, 
        'entry_price': 1.49, 
        'hours_to_expiration': 61.84, 
        'strike': 73.0, 
        'type': 'PUT', 

        'futures_symbol': 'SOL/USDT:USDT'}, {'symbol': 'SOL/USDT:USDT-260807-74-C', 
        'ccxt_symbol': 'SOL/USDT:USDT-260807-74-C', 'buyOrSell': 'sell', 'size': 2.0, 
        'entry_price': 1.26, 'hours_to_expiration': 61.84, 'strike': 74.0,
        'type': 'CALL', 'futures_symbol': 'SOL/USDT:USDT'}]

        open_futures = {
            'SOL': {
                'symbol': 'SOL/USDT:USDT', 
                'side': 'buy', 
                'size': 0.3, 
                }}

            сценарии:
            0.9. опционый лист сравнивать с наличие фюча 
            falce
            1. нет опциону, нет фучерса
            true 
            2. нет опциона, фючерс на другой монете
            true
            3. нет опциона, фучерс на монете
            falce 
            4. option put sell < future  < option coll sell если опцион и фучерс одной монеты 
            false 
            5. option put sell > future 
            true 
            6. option call sell < future 
            true
            7.option size != future size
            falce 
                """
        dictOptions = {}
        
        logger.info(f"⏳ Запуск фонового сканирования рисков портфеля. Буфер защиты: {buffer_pct * 100}%")
        
        # Шаг 9: Получаем список всех живых открытых опционов с реального баланса Bybit
        # Этот метод уже возвращает базово отфильтрованные опционы портфеля
        listOptions = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE']
        open_options = self.get_active_open_options3()
        open_fuctures = self.get_active_futures_positions() #true data
        logger.info(f"open_options {open_options}"
                    f"open_futures {open_fuctures}")

        if not open_options:
            logger.info("ℹ️ На аккаунте нет открытых опционов. Хеджирование не требуется.")
            return True

        for opt in open_options:
            # Вытаскиваем исходную сырую строку позиции (напр: XRPUSDT-Options-4AUG26-1.1-C)
            raw_symbol = opt["symbol"] 
            buy_or_sell = opt["buyOrSell"]
            qty = opt["size"] # Объем позиции (всегда положительный float, благодаря abs())

            # Хеджируем ТОЛЬКО проданные (Short / SELL) крылья, так как их риск неограничен!
            if buy_or_sell != 'sell':
                continue

            # === СТЫКОВКА С METHOD_SYMBOLS: Мгновенно получаем объект со всеми метаданными ===
            # Нам больше не нужно резать строки дефисами внутри этой функции!
            asset = OptionAsset(raw_symbol=raw_symbol, exchange_instance=self.exchange)

            # --- ШАГ 10: ЗАПРАС ТЕКУЩЕГО СПОТА (ticPrice) ДЛЯ ЭТОЙ МОНЕТЫ ---
            # Запрашиваем цену базового фьючерса, имя которого (напр. 'XRP/USDT:USDT') объект уже знает
            
            
            try:
                ticker_info = self.exchange.fetch_ticker(asset.futures_symbol)
                current_spot_price = float(ticker_info['last'])
                logger.debug(f" tik price  {current_spot_price}")
            except Exception as e:
                logger.error(f"❌ Не удалось получить текущий спот для {asset.futures_symbol}: {e}")
                continue



            logger.info(f" asset.type, asset.strike, buffer_amount"
                        f"{asset.coin, asset.type, asset.strike}")
            # === АНАЛИЗ ДЛЯ ПРОДАННОГО ОПЦИОНА CALL (Защита от пампа/роста рынка) ===
            logger.debug(f"asset.type == 'CALL'"
                        f"{asset.type} == C")
            if asset.type == 'CALL':
                # Если цена спота улетела выше страйка + буфер
                logger.info(f"CALL current_spot_price > (asset.strike - buffer_amount)"
                            f" {current_spot_price} > {asset.strike}")
                if current_spot_price > (asset.strike):
                    logger.warning(
                        f"🚨 КРИТИЧЕСКАЯ ЗОНА: Спот {current_spot_price}" 
                        f"пробил страйк Call {asset.strike}! "
                        f"Включаем экстренный Long-хедж фьючерсом."
                    )
                    # Шаг 11: Открываем Long-фьючерс (используем очищенное имя монеты и объем ноги)
                    self.place_futures_hedge_order(base_currency=asset.coin, side='buy', qty=qty)
                else:
                    logger.info(
                        f"🟢 Опцион {asset.coin} Call {asset.strike} вне опасности. "
                        f"Спот: {current_spot_price} (Порог защиты: {round(asset.strike , 4)})"
                    )

            # === АНАЛИЗ ДЛЯ ПРОДАННОГО ОПЦИОНА PUT (Защита от дампа/падения рынка) ===
            elif asset.type == 'PUT':
                # Если цена спота рухнула ниже страйка - буфер
                logger.info(f"PUT current_spot_price < (asset.strike + buffer_amount):"
                            f"{current_spot_price} < {asset.strike}")
                if current_spot_price < (asset.strike ):
                    logger.warning(
                        f"🚨 КРИТИЧЕСКАЯ ЗОНА: Спот {current_spot_price}"
                        f" упал ниже страйка Put {asset.strike}! "
                        f"Включаем экстренный Short-хедж фьючерсом."
                    )
                    # Шаг 11: Открываем Short-фьючерс
                    self.place_futures_hedge_order(base_currency=asset.coin, side='sell', qty=qty)
                else:
                    logger.info(
                        f"🟢 Опцион {asset.coin} Put {asset.strike} вне опасности. "
                        f"Спот: {current_spot_price} (Порог защиты: {round(asset.strike, 4)})"
                    )
                    
        return True

    
    def get_active_open_options3(self) -> dict:
        """
        УНИВЕРСАЛЬНЫЙ АВТОНОМНЫЙ МЕТОД СБОРА ПОЗИЦИЙ (Шаг 9 плана).
        
        Сам запрашивает ВСЕ позиции с Bybit v5. В скобках ничего передавать НЕ НАДО.
        Сам находит символы в балансе и парсит их через OptionAsset.
        Никаких ошибок 'Missing parameters' или 'list object has no attribute get' здесь больше нет.
        """
        # Принудительно импортируем наш отлаженный универсальный класс-парсер

        logger.info("Запуск проверки открытых, неэкспирированных и живых опционов...")
        active_options = []
        list_active_option = []
        total_active_option = {}
        
        
        try:
            current_timestamp = self.exchange.milliseconds()
        except Exception:
            current_timestamp = int(datetime.utcnow().timestamp() * 1000)

        try:
            # Универсальный вызов CCXT. Задаем параметры строго для Единого аккаунта Bybit
            positions = self.exchange.fetch_positions(params={
                "category": "option",
                "settleCoin": "USDT"
            })
            
            logger.debug(f"postions {positions}")
            # ЖЕЛЕЗОБЕТОННЫЙ ПРЕДОХРАНИТЕЛЬ: Bybit может вернуть как список, так и словарь
            if isinstance(positions, dict):
                positions_list = positions.get('result', {}).get('list', [])
            elif isinstance(positions, list):
                positions_list = positions
            else:
                positions_list = []

            # Перебираем каждую позицию, которую Bybit САМА выдала из нашего баланса
            for pos in positions_list:
                # logger.info(f"pos {pos}")
                # Биржа сама поставляет нам имя контракта (symbol) и объем (contracts)
                pos_symbol = pos.get('symbol', '')
                initMargin = float(pos.get('initialMargin', ''))
                # В зависимости от версии CCXT объем может лежать в contracts или size
                try:
                    contracts = float(pos.get('contracts', pos.get('size', 0.0)))
                except Exception:
                    contracts = 0.0
                
                # Фильтруем: берем только реальные открытые опционы альткоинов (с дефисом и C/P)
                if contracts != 0 and "-" in pos_symbol and ("-C" in pos_symbol or "-P" in pos_symbol):
                    
                    # === РЕШЕНИЕ КОНФЛИКТА: Скармливаем парсеру переменную pos_symbol, которую взяли из баланса Bybit ===
                    asset = OptionAsset(raw_symbol=pos_symbol, exchange_instance=self.exchange)
                    
                    # Определяем направление сделки
                    raw_side = pos.get('side', '').lower()
                    buy_or_sell = 'buy' if raw_side == 'long' or raw_side == 'buy' else 'sell'
                    
                    # Подтягиваем время жизни из кэша CCXT
                    market_data = self.exchange.markets.get(asset.ccxt_symbol, {})
                    expiry_timestamp = market_data.get('expiry', 0)
                    
                    if expiry_timestamp == 0 or expiry_timestamp > current_timestamp:
                        time_left_hours = (expiry_timestamp - current_timestamp) / (1000 * 60 * 60) if expiry_timestamp > 0 else 99.0
                        
                        # Собираем чистый, готовый для математики Шага 10 словарь
                        active_options.append({
                            "symbol": asset.raw_symbol,                 # Имя от математики
                            "ccxt_symbol": asset.ccxt_symbol,           # Имя для стаканов
                            "buyOrSell": buy_or_sell,                   # 'buy' или 'sell'
                            "size": contracts,                          # Объем сделки
                            "entry_price": float(pos.get('entryPrice', pos.get('avgPrice', 0.0))),
                            "hours_to_expiration": round(time_left_hours, 2),
                            "strike": asset.strike,                      # Чистый флоат страйка
                            "type": asset.type,                          # 'C' или 'P'
                            "futures_symbol": asset.futures_symbol,       # Имя фьючерса для хеджа
                            "initMargin": initMargin
                        })
                        logger.debug(f"🟢 Успешно взят на контроль опцион: {asset.raw_symbol} | {buy_or_sell.upper()} | Страйк: {asset.strike}")
                         
            logger.info(f"Анализ аккаунта завершен. Живых опционов в портфеле: {len(active_options)}")
            
        except Exception as e:
            logger.error(f"Критическая ошибка при сканировании позиций Bybit: {e}")
        
        active_optionsDict = self.separate(listData=active_options)    
        return active_optionsDict
    
    def separate(self, listData: list) -> dict:
        # 1. Создаем финальный пустой словарь портфеля
        portfolio_dict = {}

        # 2. Бежим циклом по входящему плоскому списку
        for data_ in listData:
            
                        # Шаг 1: Извлекаем сырые данные без подмен (по дефолту везде возвращается None)
            raw_symbol = data_.get('symbol', None)
            raw_strike = data_.get('strike', None)
            raw_size   = data_.get('size', None)
            
            # Проверяем оба возможных ключа направления, которые может вернуть биржа/парсер
            raw_side   = data_.get('buyOrSell', data_.get('side', None))

            # Шаг 2: ЕДИНЫЙ БАРЬЕР БЕЗОПАСНОСТИ СТРОГО ЧЕРЕЗ 'is None' (Guard Clause)
            # Если хотя бы одно из четырех критических полей равно None — контракт бракуется
            if raw_symbol is None or raw_strike is None or raw_size is None or raw_side is None:
                logger.error(
                    f"❌ [ОТБРАКОВКА] Обнаружен None в критических полях опциона! "
                    f"Symbol: {raw_symbol} | Strike: {raw_strike} | Size: {raw_size} | Side: {raw_side}. Пропуск контракта."
                )
                continue  # Мгновенно сбрасываем контракт, код не идет дальше и не падает!

            # === ИСПОЛЬЗУЕМ КЛАСС OptionAsset ДЛЯ ИЗВЛЕЧЕНИЯ МОНЕТЫ ===
            asset = OptionAsset(raw_symbol=data_["symbol"], exchange_instance=self.exchange)

            # Получаем чистое имя монеты из свойства asset.coin
            coin_key = asset.coin.upper().strip()

            # --- УСЛОВНЫЙ ОПЕРАТОР: Инициализация ключа монеты ---
            # Если этой папки-монеты еще нет в словаре, создаем для нее пустой list[]
            if coin_key not in portfolio_dict:
                portfolio_dict[coin_key] = []

            # --- СБОРКА ---
            # Добавляем опцион в список ЕГО монеты (и buy, и sell)
            portfolio_dict[coin_key].append(data_)
        logger.debug(f"{portfolio_dict}")
        return portfolio_dict
    
    
    def execute_hedge_adjustment(self, nameCoin: str, target_side: str, delta: float):
        """
        УНИВЕРСАЛЬНЫЙ ИСПОЛНИТЕЛЬ ОРДЕРОВ (Шаг 11 плана):
        Принимает монету, целевую сторону защиты (buy/sell) и рассчитанную дельту объемов.
        Самостоятельно принимает решение: добрать позицию или частично сократить излишек.
        """
        # Округляем дельту до 4 знаков (защита от биржевого микро-мусора в плавающей точке)
        delta = round(delta, 4)
        
        # Если дельта после округления равна нулю — никаких действий на бирже не требуется
        if delta == 0.0:
            return

        # Приводим целевую сторону к нижнему регистру для стандартизации протокола CCXT
        clean_target_side = target_side.lower().strip()

        # --- ВНЕШНИЙ ТЕХНИЧЕСКИЙ ЩИТ ДЛЯ ЗАЩИТЫ ОТ СБОЕВ API БИРЖИ ---
        try:
            # === СЦЕНАРИЙ 1: ДЕЛЬТА ПОЛОЖИТЕЛЬНАЯ (НЕХВАТКА ОБЪЕМА ХЕДЖА) ===
            # Нам необходимо ДОКУПИТЬ фьючерсы в ту же сторону, куда направлен риск
            if delta > 0:
                logger.warning(
                    f"⚡ [ОРДЕР ДОБОРА] Нехватка хэджа по монете {nameCoin}! "
                    f"Отправляем рыночный приказ {clean_target_side.upper()} на объем: {delta}"
                )
                
                # Твой вызов CCXT для отправки рыночного ордера на добор:
                # self.place_market_order(symbol=nameCoin, side=clean_target_side, qty=delta)

            # === СЦЕНАРИЙ 2: ДЕЛЬТА ОТРИЦАТЕЛЬНАЯ (ИЗЛИШЕК / ПЕРЕХЕДЖ) ===
            # Математика зафиксировала лишние фьючерсы. Нам нужно ЧАСТИЧНО СОКРАТИТЬ позицию
            elif delta < 0:
                # Переводим отрицательное значение дельты в чистый модуль объема для ордера
                actual_qty = abs(delta)
                
                # --- УСЛОВНЫЕ ОПЕРАТОРЫ ПЕРЕВОРОТА НАПРАВЛЕНИЯ ДЛЯ ЗАКРЫТИЯ ---
                # Если целевая сторона хэджа LONG (buy), то закрывать излишек нужно ордером SELL
                if clean_target_side == 'buy':
                    order_side = 'sell'
                # Если целевая сторона хэджа SHORT (sell), то закрывать излишек нужно ордером BUY
                elif clean_target_side == 'sell':
                    order_side = 'buy'
                else:
                    logger.error(f"❌ Критическая аномалия направления clean_target_side: {clean_target_side}")
                    return

                logger.info(
                    f"⚡ [ОРДЕР СОКРАЩЕНИЯ] Зафиксирован перехедж по монете {nameCoin}! "
                    f"Отправляем рыночный приказ {order_side.upper()} на частичное закрытие объема: {actual_qty}"
                )
                
                # Твой вызов CCXT для отправки встречного ордера на сокращение:
                # self.place_market_order(symbol=nameCoin, side=order_side, qty=actual_qty)

        except Exception as order_error:
            # Если Bybit отклонит ордер (Rate Limit, Margin Call) — блок except удержит робота на плаву
            logger.error(f"💥 Критический сбой API при исполнении хэдж-ордера по {nameCoin}: {order_error}")


    
    # no Test  
    def analizCallStrike0(self, optionsSellCall: list, nameCoin: str):
        analizCallBool = True
        """
        ЗАЩИТА CALL-НОГИ: Анализирует риски роста рынка выше страйка.
        """
        # Если при роллировании на аккаунте временно нет 
        # CALL-опционов — выходим
        if not optionsSellCall:
            return

        # Нам нужен минимальный страйк (ближайший рубеж обороны)
        # Мы его уже умеем искать без жестких индексов
        call_strike = float('inf')
        total_call_size = 0.0
        for call_opt in optionsSellCall:
            call_strike = min(call_strike, float(call_opt.get('strike', float('inf'))))
            total_call_size += float(call_opt.get('size', 0.0))

        ticPrice = self.ticPrice
        open_futures = self.futures.get(nameCoin)
        
        

        # --- УСЛОВНЫЙ ОПЕРАТОР: Пробит ли страйк CALL вверх? ---
        if call_strike < ticPrice:
            logger.warning(f"🚨 [CALL RISK] Цена {ticPrice} "
                           f" выше страйка CALL {call_strike}"
                           f" ! Требуется LONG хедж.")
            
            if open_futures:
                delta_OptAndFutu = open_futures['size'] - optionsSellCall['size'] 
                if call_strike < open_futures['openPrice'] < ticPrice:
                    analizCallBool = False
                    return analizCallBool
                    
                elif call_strike < ticPrice < open_futures['openPrice']:
                    logger.error(f" 1. close open futuers {open_futures}"
                                 f" open new Futures po luchey price")
                    analizCallBool = False
                    return analizCallBool
                
                else: 
                    logger.error(f"1 ne validnie danie"
                                 f"2 ne ponythnaya problema")                
                
            
            # Сценарий А: Фьючерса на аккаунте нет совсем — ОТКРЫВАЕМ С НУЛЯ
            elif open_futures is None:
                logger.error(f"➕ Открываем НОВЫЙ фьючерс BUY на"
                             f" объем {total_call_size}")
                # [Вызов ордера на покупку всего объема total_call_size]
                
            # Сценарий Б: Фьючерс уже есть — сравниваем объемы
            else:
                fut_size = float(open_futures.get('size', 0.0))
                fut_side = open_futures.get('side', '').lower()
                
                # Если фьючерс стоит в BUY, проверяем дельту (хватает ли объема?)
                if fut_side == 'buy':
                    delta = total_call_size - fut_size
                    if delta > 0:
                        logger.warning(f"⚡ Нехватка хеджа! Докупаем фьючерс BUY на объем: {delta}")
                        # [Вызов ордера на дозакупку дельты]
                    elif delta < 0:
                        logger.info(f"⚡ Перехедж! Сбрасываем лишний фьючерс SELL на объем: {abs(delta)}")
                        # [Вызов ордера на частичное закрытие излишка]

    
#  notest   
    def analizCoridorStrikes0(self, 
                             optinsList: list,
                             nameCoin: str):
        '''
        1. proveryaem o nalichie ticPrice v coridore
        esli TRUE . proveryem futures esli OPEN futures close zacrivem TRUE and TRUE
        2. proveryem o nalichie 
        
        '''
        optionsSellPut = []
        optionsSellCall = [] 
        dictPutSellAnaliz = {}
        total_call_size = 0.0
        total_put_size = 0.0
        
        open_futures = self.futures.get(nameCoin)
        # ticPrice = self.ticPrice pod zamenu
        ticPrice = float(input(f"input tic price coin {nameCoin} :")) 
        
        for option in optinsList:
            if option.get('symbol') is None:
                continue
            
            asset = OptionAsset(raw_symbol=option["symbol"], 
                                exchange_instance=self.exchange)
            
            if option.get('buyOrSell', '').lower() == 'sell':
                asset_type = asset.type.upper().strip()
                
                # Исправлено: безопасное разделение по типам без IndexError
                if "PUT" in asset_type or asset_type.startswith('P'):
                    optionsSellPut.append(option)
                    total_put_size += float(option.get('size', 0.0))
                    
                elif "CALL" in asset_type or asset_type.startswith('C'):
                    optionsSellCall.append(option)
                    total_call_size += float(option.get('size', 0.0))
        
        dictPutSellAnaliz['optSellCall'] = optionsSellCall
        dictPutSellAnaliz['optSellPut'] = optionsSellPut
        
        # logger.info(f" dictPutSellAnaliz {dictPutSellAnaliz} ")
        # =====================================================================
        # КУСОК 2: ИТЕРАЦИОННЫЙ РАСЧЕТ ГРАНИЦ КОРРИДОРА (ЗАЩИТА РОЛЛИРОВАНИЯ)
        # =====================================================================
        
        # Находим МАКСИМАЛЬНЫЙ страйк среди проданных PUT (нижняя граница риска)
        # Если при роллировании список пуст — put_strike останется 0.0 (код не упадет)
        put_strike = 0.0
        for put_opt in optionsSellPut:
            put_strike = max(put_strike, float(put_opt.get('strike', 0.0)))
            
        # Находим МИНИМАЛЬНЫЙ страйк среди проданных CALL (верхняя граница риска)
        # Если при роллировании список пуст — call_strike останется бесконечностью
        call_strike = float('inf')
        for call_opt in optionsSellCall:
            call_strike = min(call_strike, float(call_opt.get('strike', float('inf'))))
        logger.info(f" put_strike {put_strike}"
                    f" call_strike {call_strike}")   
        
        # Возвращаем верхнюю заглушку в безопасное числовое состояние
        if call_strike == float('inf'):
            call_strike = 999999.0
        
        # =====================================================================
        # КУСОК 3: МАТЕМАТИЧЕСКИЕ СЦЕНАРИИ С ПРАВИЛЬНЫМИ ФЛАГАМИ ТРЕВОГИ
        # =====================================================================

                # === ТОЧЕЧНЫЙ АНАЛИЗ ВЫВЕРНУТОГО КОРРИДОРА (PUT > CALL) ===
        if put_strike > call_strike:
            logger.warning(f"⚠️ [ИНВЕРСИЯ СТРАЙКОВ] По монете {nameCoin} "
                           f" вывернут коридор: {put_strike} > {call_strike}")
            
            # Вычисляем математическую середину 
            mid_price = (put_strike + call_strike) / 2  # (101 + 99) / 2 = 100
            
            # Собираем актуальные данные по открытому фьючерсу (наш технический щит)
            fut_size = 0.0
            fut_side = 'none'
            if open_futures:
                fut_size = float(open_futures.get('size', 0.0))
                fut_side = open_futures.get('side', '').lower().strip()

            # --- ВЕТВЛЕНИЕ ОТНОСИТЕЛЬНО СЕРЕДИНЫ С УЧЕТОМ ОБЪЕМОВ ---
            if ticPrice > mid_price:
                # Зона 100+: Целевой хэдж должен быть строго BUY (LONG)
                # Берем суммарный объем всех проданных CALL опционов
                target_qty = total_call_size 
                delta = target_qty - fut_size if fut_side == 'buy' else target_qty
                
                # work posle pernosav bybit_client
                # self.execute_hedge_adjustment(
                #     nameCoin=nameCoin, 
                #     target_side='buy',
                #     delta=delta)
                
                dictPutSellAnaliz['analizeBool'] = False
                return dictPutSellAnaliz
                
               
            # Если фьючерса нет или он стоит в противоположную сторону (SELL)
            elif ticPrice < mid_price:
                target_qty = total_put_size
                # Дельта равна target_qty, а исполнитель сам закроет старый SELL (шорт)
                delta = target_qty - fut_size if fut_side == 'sell' else target_qty
            
                # Отправляем рассчитанную дельту в наш универсальный исполнитель
                # self.execute_hedge_adjustment(nameCoin=nameCoin, target_side='sell', delta=delta)

                dictPutSellAnaliz['analizeBool'] = False # Сами всё исполнили, в главные подфункции не пускаем
                return dictPutSellAnaliz
                
            else:
                # Зона <100: Целевой хэдж должен быть строго SELL (SHORT)
                target_qty = total_put_size
                
                # Если фьючерс уже стоит в SELL — считаем разницу
                if fut_side == 'sell':
                    delta = target_qty - fut_size
                else:
                    delta = target_qty
                    
                self.execute_hedge_adjustment(nameCoin=nameCoin, target_side='sell', delta=delta)
                
                dictPutSellAnaliz['analizeBool'] = False
                return dictPutSellAnaliz
            
         
    def aggregate_coin_data0(self, optinsList: list, nameCoin: str) -> dict:
        """
        ФУНКЦИЯ-АГРЕГАТОР (Версия 4.0 — Максимальная оптимизация):
        Строго за ОДИН проход по списку собирает массивы ног, накапливает общие объёмы,
        находит критические страйки и формирует эталонный паспорт данных монеты coin_data.
        """
        optionsSellPut = []
        optionsSellCall = []
        total_call_size = 0.0
        total_put_size = 0.0
        
        # Стартовые маркеры для поиска страйков «на лету» внутри единого цикла
        put_strike = 0.0
        call_strike = float('inf')

        # =====================================================================
        # 🔥 ВСЁ В ОДИН ПРОХОД: СБОР НОГ, ОБЪЁМОВ И СТРАЙКОВ ОДНОВРЕМЕННО 🔥
        # =====================================================================
        for option in optinsList:
            # Защитный барьер (Guard Clause): отсекаем битый мусор API Bybit
            if option.get('symbol') is None:
                continue

            # Инициализируем парсер OptionAsset строго ОДИН раз для контракта
            asset = OptionAsset(raw_symbol=option["symbol"], exchange_instance=self.exchange)

            # Нас интересуют исключительно проданные опционы (Short позиции)
            if option.get('buyOrSell', '').lower() == 'sell':
                asset_type = asset.type.upper().strip()
                current_strike = float(option.get('strike', 0.0))

                # --- РАСПРЕДЕЛЕНИЕ И НАКОПЛЕНИЕ ПО PUT-НОГЕ ---
                if "PUT" in asset_type or asset_type.startswith('P'):
                    optionsSellPut.append(option)
                    total_put_size += float(option.get('size', 0.0))
                    # На ходу ищем МАКСИМАЛЬНЫЙ пут-страйк (нижний край коридора)
                    put_strike = max(put_strike, current_strike)
                    
                # --- РАСПРЕДЕЛЕНИЕ И НАКОПЛЕНИЕ ПО CALL-НОГЕ ---
                elif "CALL" in asset_type or asset_type.startswith('C'):
                    optionsSellCall.append(option)
                    total_call_size += float(option.get('size', 0.0))
                    # На ходу ищем МИНИМАЛЬНЫЙ колл-страйк (верхний край коридора)
                    call_strike = min(call_strike, current_strike)

        # =====================================================================
        # СТЕРИЛИЗАЦИЯ СТРАЙКОВ (Убираем хардкод и бесконечности из паспорта)
        # =====================================================================
        # Если при роллировании PUT-ноги нет, пускай put_strike будет честным 0.0
        if not optionsSellPut:
            put_strike = None
            
        # If call list is empty, clear infinity indicator to None for cleaner data consistency
        if not optionsSellCall:
            call_strike = None

        # =====================================================================
        # СБОРКА ЭТАЛОННОГО ПАСПОРТА ДАННЫХ МОНЕТЫ
        # =====================================================================
        coin_data = {
            'nameCoin': nameCoin,
            'optionsSellCall': optionsSellCall,
            'optionsSellPut': optionsSellPut,
            'total_call_size': total_call_size,
            'total_put_size': total_put_size,
            'put_strike': put_strike,
            'call_strike': call_strike,
            'ticPrice': self.ticPrice.get_ticker_by_symbol(symbol=nameCoin),                    # Текущий тик рынка
            'open_futures': self.futures.get(nameCoin)    # Безопасный фьючерс без KeyError
        }

        return coin_data
   
 
    
    def is_futures_data_valid0(self, futures_dict) -> bool:
        # Шаг 1: Проверка внешней коробки (Аналогично опционам)
        if futures_dict is None:
            logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА: Данные self.futures равны None!")
            return False

        if not isinstance(futures_dict, dict):
            logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: Нарушен тип self.futures!")
            return False

        # Шаг 2: Внутренний аудит полей (Таможня для каждого открытого фьючерса)
        # Создаем список для сброса сломанных монет, чтобы не индусить
        corrupted_coins = []
        
        for coin_name, fut_info in futures_dict.items():
            # Извлекаем внутренние параметры фьючерса БЕЗ подмен (дефолт None)
            raw_size  = fut_info.get('size', None)
            raw_side  = fut_info.get('side', None)
            raw_price = fut_info.get('openPrice', None)

            # УСЛОВНЫЙ ОПЕРАТОР: Проверка внутренностей на None
            if raw_size is None or raw_side is None or raw_price is None:
                logger.error(f"❌ [ФЬЮЧЕРС БРАК] У монеты {coin_name} поля содержат None!")
                corrupted_coins.append(coin_name)

        # Шаг 3: Очистка. Выжигаем только сломанные монеты, а здоровые оставляем в работе
        for bad_coin in corrupted_coins:
            del futures_dict[bad_coin]
        return True
    
    
    def is_options_data_valid0(self, options_dict) -> bool:
        """
        ВАЛИДАТОР ОПЦИОНОВ: Проверяет целостность внешней структуры портфеля.
        Защищает главный диспетчер от критического падения при итерации.
        """
        # 1. Защита от полного отсутствия ответа (Сбой сети / таймаут API Bybit)
        if options_dict is None:
            logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА: Данные self.options равны None! Робот ослеп.")
            return False

        # 2. Защита структуры (Гарантируем, что это dict, а не сломанная строка/список)
        if not isinstance(options_dict, dict):
            logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: Структура self.options сломана! Ожидался dict, пришел {type(options_dict)}.")
            return False

        # Если коробка данных цела — возвращаем True (даже если портфель пустой {})
        return True
   
        

        
# bybitOpt = BybitOptionBot()

#  getD = bybitOpt.get_historical_closes_candals("DOGE")
#  getD = bybitOpt.fetch_option_market_data('BTC')
#  getD = bybitOpt.check_connection_and_balance()
# getD = bybitOpt.get_all_option_coins()
# getD = bybitOpt.get_option_expiration_dates()
# getD = bybitOpt.get_ticker_by_symbol('sol')
# getD = bybitOpt.get_option_strikes(base_coin="BTC", expiration_date='2026-07-10')
# getD = bybitOpt.get_option_premium_prices2(strikes_grid={'ticPrice': 63042.5, 'strikeCall': [63500.0, 64000.0, 64500.0, 65000.0], 'strikePut': [63000.0, 62500.0, 62000.0, 61500.0]})
# getD = bybitOpt.place_option_order2(
#     symbol='SOL-31JUL26-77-C',
#     side='Sell',
#     qty=1.0,
#     price=1.85)
# getD = bybitOpt.analyze_open_options(base_currency='SOL')
# getD = bybitOpt.chase_order(
#     symbol="SOL-31JUL26-77-P",
#     side='sell',
#     qty=1.0,
#     price_limit=1.849953599160446,
#     check_interval_sec=10)
# getD = bybitOpt.get_active_open_options3()
# getD = bybitOpt.place_futures_hedge_order(
#     base_currency='MNT',
#     side="buy",
#     qty=50.0,)
# getD = bybitOpt.set_futures_leverage(
#     base_currency='SOL',
#     leverage=10)
# getD = bybitOpt.get_active_futures_positions()
# getD = bybitOpt.process_hedging_logic()



# logger.info(f"{getD}")

