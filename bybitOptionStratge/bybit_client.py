import ccxt, os
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


        
# bybitOpt = BybitOptionBot()

# getD = bybitOpt.get_historical_closes_candals("DOGE")
# getD = bybitOpt.fetch_option_market_data('BTC')
# getD = bybitOpt.check_connection_and_balance()
# getD = bybitOpt.get_all_option_coins()
# getD = bybitOpt.get_option_expiration_dates()
# getD = bybitOpt.get_ticker_by_symbol('sol')
# getD = bybitOpt.get_option_strikes(base_coin="BTC", expiration_date='2026-07-10')
# getD = bybitOpt.get_option_premium_prices2(strikes_grid={'ticPrice': 63042.5, 'strikeCall': [63500.0, 64000.0, 64500.0, 65000.0], 'strikePut': [63000.0, 62500.0, 62000.0, 61500.0]})



# logger.info(f"{getD}")

