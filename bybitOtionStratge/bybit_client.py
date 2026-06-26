import ccxt, os
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
        # Флаг loadAllOptions обязателен, чтобы CCXT подгружал опционные рынки
        
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

        
        
        # history cooooood
        # self.exchange = ccxt.bybit({
        #     'options': {
        #         'loadAllOptions': True
        #     }
        # })
        # logger.info("Подключение к Bybit успешно инициализировано.")

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
            logger.info(f"ohlcv  {ohlcv}")
            
            # Если биржа ничего не вернула или данных критически мало — прерываем работу
            if not ohlcv or len(ohlcv) < limit:
                logger.warning(f"Биржа вернула недостаточно свечей для пары {market_ticker}.")
                return []
                
            # Извлекаем только цены закрытия. 
            # В структуре CCXT свеча выглядит так: [timestamp, open, high, low, close, volume]
            # Индекс 4 — это цена закрытия (close)
            close_prices = [candle[4] for candle in ohlcv]
            
            logger.info(f"Успешно скачано {len(close_prices)} свечей для {market_ticker}.")
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


    def get_option_strikes(self, base_coin="BTC", expiration_date="2026-07-03"):
        """
        Парсит и возвращает уникальные цены страйков для монеты на 
        конкретную дату экспирации.
        :param base_coin: Например, 'BTC' или 'ETH'
        :param expiration_date: Строка в формате 'YYYY-MM-DD' 
        (из метода get_option_expiration_dates)
        """
        try:
            # Загружаем рынки (используется кэш CCXT)
            markets = self.exchange.load_markets()
            
            strikes = set()
            for market in markets.values():
                # Фильтруем: тип опцион + нужная монета
                if market.get('type') == 'option' and market.get('base') == base_coin:
                    # Извлекаем дату экспирации из контракта
                    expiry_date = market.get('expiryDatetime')
                    if expiry_date and expiry_date.startswith(expiration_date):
                        # Забираем цену страйка (CCXT парсит её во float или int в поле 'strike')
                        strike_price = market.get('info', {}).get('strikePrice')
                        if strike_price:
                            # Сохраняем как float для правильной сортировки чисел
                            strikes.add(float(strike_price))
            
            # Сортируем страйки по возрастанию
            sorted_strikes = sorted(list(strikes))
            
            # Переводим в красивый строковый вид для лога (убираем лишние .0 у целых чисел)
            strikes_str = ", ".join([str(int(s) if s.is_integer() else s) for s in sorted_strikes])
            
            logger.info(f"{base_coin} strikes for {expiration_date}: {strikes_str}")
            return sorted_strikes
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге страйков для {base_coin} на {expiration_date}: {e}")
            return []

        
bybitOpt = BybitOptionBot()

# getD = bybitOpt.get_historical_closes_candals("DOGE")
# getD = bybitOpt.fetch_option_market_data('BTC')
# getD = bybitOpt.check_connection_and_balance()
# getD = bybitOpt.get_all_option_coins()
# getD = bybitOpt.get_option_expiration_dates()
getD = bybitOpt.get_option_strikes()#base_coin="SOL",
                                  # expiration_date='2026-06-27')

logger.info(f"{getD}")

