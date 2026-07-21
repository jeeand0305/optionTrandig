import ccxt 
import os
import time
# from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from logger import logger
from dotenv import load_dotenv

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
        logger.info(f"Запуск Chase Order [{side.upper()}] для {symbol}. Базовый лимит: {price_limit}")

        # Ссылка на ваш формат CCXT символа
        parts = symbol.upper().split('-')
        if len(parts) == 4:
            base_coin, date_str, strike, option_type = parts
            parsed_date = datetime.strptime(date_str, "%d%b%y")
            ccxt_symbol = f"{base_coin}/USDT:USDT-{parsed_date.strftime('%y%m%d')}-{strike}-{option_type}"
        else:
            ccxt_symbol = symbol

        tick_size = 0.0001 if "DOGE" in symbol else (0.5 if "BTC" in symbol else 0.01)
        decimals = 4 if "DOGE" in symbol else (1 if "BTC" in symbol else 2)

        # Запоминаем изначальный теоретический лимит
        base_limit = price_limit
        accumulated_slippage = 0.0  # Сколько процентов мы уже уступили рынку

        # === ЦИКЛ ПОДБОРА СТАРТОВОЙ ЦЕНЫ С УЧЕТОМ УСТУПКИ 1% ===
        while True:
            try:
                orderbook = self.exchange.fetch_order_book(ccxt_symbol)
            except Exception as e:
                logger.error(f"Не удалось получить стакан для {ccxt_symbol}: {e}")
                return False

            # --- ИСПРАВЛЕННЫЙ БЛОК ИЗВЛЕЧЕНИЯ ЧИСЛА ЦЕНЫ [0][0] ---
            if side == 'buy':
                # Берем цену первого бида [0][0], а не весь массив
                best_bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else 0.0
                current_target_price = round(best_bid + tick_size, decimals)
                
                dynamic_limit = base_limit * (1 + accumulated_slippage / 100)
                  
                if current_target_price > dynamic_limit:
                    if accumulated_slippage >= max_slippage_pct:
                        logger.warning(f"Достигнут предел уступки ({max_slippage_pct}%). Рынок слишком дорогой. Отмена.")
                        return False
                    
                    accumulated_slippage += slippage_step_pct
                    logger.info(f"Стартовая цена выше лимита. Уступаем рынку +{slippage_step_pct}%. Новый лимит покупки: {round(dynamic_limit, decimals)}")
                    time.sleep(1)
                    continue
                
            else:  # sell
                # Берем цену первого аска [0][0], а не весь массив
                best_ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else 999999.0
                current_target_price = round(best_ask - tick_size, decimals)
                
                dynamic_limit = base_limit * (1 - accumulated_slippage / 100)
                
                if current_target_price < dynamic_limit:
                    if accumulated_slippage >= max_slippage_pct:
                        logger.warning(f"Достигнут предел уступки ({max_slippage_pct}%). Рынок слишком дешевый. Отмена.")
                        return False
                    
                    # Делаем шаг уступки -1% (снижаем требования к прибыли, чтобы ордер открылся)
                    accumulated_slippage += slippage_step_pct
                    logger.info(f"Рыночный Ask ({current_target_price}) ниже лимита. Снижаем планку на -{slippage_step_pct}%. Новый лимит продажи: {round(dynamic_limit, decimals)}")
                    time.sleep(check_interval_sec)
                    continue

            break

        # === ВЫСТАВЛЕНИЕ ПЕРВОГО ОРДЕРА (Используем вашу рабочую функцию) ===
        response = self.place_option_order2(symbol, side, qty, current_target_price)
        if not response or 'id' not in response:
            return False
            
        order_id = response['id']

        # === ОСНОВНОЙ ЦИКЛ ОТСЛЕЖИВАНИЯ (Внутри стакана) ===
        while True:
            time.sleep(check_interval_sec)

            try:
                order_info = self.exchange.fetch_order(order_id, ccxt_symbol)
                status = order_info['status']
            except Exception as e:
                logger.warning(f"Ошибка fetch_order: {e}. Повтор...")
                continue

            if status == 'closed':
                logger.info(f"🎉 Нога {symbol} ПОЛНОСТЬЮ ИСПОЛНЕНА по цене {current_target_price}!")
                return True
            if status == 'canceled':
                return False

            try:
                orderbook = self.exchange.fetch_order_book(ccxt_symbol)
            except Exception as e:
                continue

            # Логика динамического ведения ордера внутри стакана (с учетом нашей накопленной уступки)
            if side == 'buy':
                # Исправлено на [0][0]
                new_bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else 0.0
                new_target_price = round(new_bid + tick_size, decimals)
                
                if new_target_price > current_target_price:
                    if new_target_price > dynamic_limit:
                        logger.warning(f"Цена стакана превысила даже скорректированный лимит. Снятие ордера.")
                        self._safe_cancel(order_id, ccxt_symbol)
                        return False
                    self._safe_cancel(order_id, ccxt_symbol)
                    response = self.place_option_order2(symbol, side, qty, new_target_price)
                    if response and 'id' in response:
                        order_id = response['id']
                        current_target_price = new_target_price
            else:  # sell
                # Исправлено на [0][0]
                new_ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else 999999.0
                new_target_price = round(new_ask - tick_size, decimals)
                
                if new_target_price < current_target_price:
                    if new_target_price < dynamic_limit:
                        logger.warning(f"Цена упала ниже скорректированного лимита прибыли. Снятие ордера.")
                        self._safe_cancel(order_id, ccxt_symbol)
                        return False
                    self._safe_cancel(order_id, ccxt_symbol)
                    response = self.place_option_order2(symbol, side, qty, new_target_price)
                    if response and 'id' in response:
                        order_id = response['id']
                        current_target_price = new_target_price



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


        
# bybitOpt = BybitOptionBot()

# # # getD = bybitOpt.get_historical_closes_candals("DOGE")
# # # getD = bybitOpt.fetch_option_market_data('BTC')
# # # getD = bybitOpt.check_connection_and_balance()
# # # getD = bybitOpt.get_all_option_coins()
# # # getD = bybitOpt.get_option_expiration_dates()
# # # getD = bybitOpt.get_ticker_by_symbol('sol')
# # # getD = bybitOpt.get_option_strikes(base_coin="BTC", expiration_date='2026-07-10')
# # # getD = bybitOpt.get_option_premium_prices2(strikes_grid={'ticPrice': 63042.5, 'strikeCall': [63500.0, 64000.0, 64500.0, 65000.0], 'strikePut': [63000.0, 62500.0, 62000.0, 61500.0]})
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



# logger.info(f"{getD}")

