import math, re
import numpy as np 
import pandas as pd
from datetime import datetime, timezone
from logger import logger
from scipy.stats import norm
import time
from functools import wraps
from functools import wraps
from setuptools import setup
from Cython.Build import cythonize
from datetime import datetime, timezone



def benchmark_timer(func):
    """
    Декоратор для точного измерения времени выполнения функции в микросекундах.
    """
    @wraps(func) # Сохраняет имя и документацию исходной функции
    def wrapper(*args, **kwargs):
        # Засекаем время СТАРТА (высокоточный таймер)
        start_time = time.perf_counter()
        
        # Выполняем саму функцию
        result = func(*args, **kwargs)
        
        # Засекаем время ОКОНЧАНИЯ
        end_time = time.perf_counter()
        
        # Считаем разницу и переводим в микросекунды (1 секунда = 1,000,000 мкс)
        execution_time_mcs = (end_time - start_time) * 1_000_000
        
        # Выводим результат в консоль бота
        logger.info(f"[⏱️ TIMER] Функция '{func.__name__}' выполнилась за {execution_time_mcs:.2f} мкс")
        
        # Возвращаем результат работы функции, чтобы бот работал дальше
        return result
    return wrapper


def calculate_time_to_expiration(expiration_date='2026-07-17') -> float:
    """
    Рассчитывает параметр T (время до экспирации в долях года)
    для формулы Блэка-Шоулза.
    Учитывает, что экспирация на Bybit происходит строго в 08:00 UTC.
    
    :param expiration_date: Строка даты в формате 'YYYY-MM-DD'
    (например, '2026-07-17')
    :return: float (доля года, например, 0.0191). 
    Если опцион истек, возвращает 0.0
    """
    try:
        # 1. Задаем точное время экспирации на Bybit (08:00:00 UTC)
        # Добавляем хвост времени к строке даты пользователя
        expiry_str = f"{expiration_date} 08:00:00"
        
        # Переводим в объект datetime (работаем строго в UTC)
        expiry_dt = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
        
        # 2. Получаем текущее точное время в UTC
        # Внимание: для точности Блэка-Шоулза важно использовать UTC время, а не локальное на ПК
        current_dt = datetime.utcnow()
        
        # 3. Находим чистую разницу во времени
        time_delta = expiry_dt - current_dt
        
        # Переводим разницу в дни (включая остаток в часах, минутах и секундах через total_seconds)
        days_remaining = time_delta.total_seconds() / 86400.0
        
        # Если опцион уже экспирировался (время в прошлом), возвращаем 0
        if days_remaining <= 0:
            logger.warning(f"Опцион на дату {expiration_date} уже экспирирован.")
            return 0.0
        
        # 4. Рассчитываем долю года (дней / 365.25)
        # Использование 365.25 учитывает високосные года, что принято в финансах
        T = days_remaining / 365.25
        
        logger.info(f"До экспирации {expiration_date} осталось: {days_remaining:.2f} дней (T = {T:.4f} долей года)")
        return T
        
    except Exception as e:
        logger.error(f"Ошибка при расчете параметра T для даты {expiration_date}: {e}")
        return 0.0


def calculate_black_scholes_fast3(S, K, sigma, T, option_type='C', r=0.0):
    """
    Универсальный расчет теоретической стоимости опционов Call и Put.
     S     : Текущая цена актива (underlyingPrice) -func
     K     : Страйк опциона (strike)
     r     : Безрисковая ставка (например, 0.05)
     sigma : Подразумеваемая волатильность (markIv, например, 1.0047) -func
     T     : Время до экспирации в долях года (дней / 365) -func
     option_type : 'Call' или 'Put' (регистр не важен)
    Ультрабыстрая функция расчета опциона.
    Принимает типы: 'C' (Call) или 'P' (Put).
    """
    
    # Приводим к верхнему регистру (на случай, если передали маленькую 'c' или 'p')
    option_type = option_type.upper()
    
    # Если бот случайно передал полное слово 'Call' или 'Put', берём только первую букву
    if len(option_type) > 1:
        option_type = option_type[0]
        
    # Проверка на корректность типа данных
    if option_type not in ['C', 'P']:
        raise ValueError("Тип опциона должен быть 'C' (Call) или 'P' (Put)")
    
    # Обработка экспирации (T = 0)
    if T <= 0:
        if option_type == 'C':
            return max(0.0, S - K) 
        else:
            return max(0.0, K - S)
            
    # Расчет базовых коэффициентов d1 и d2
    d1 = (math.log(S / K) + (r + (sigma ** 2) / 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    # Быстрый расчет нормального распределения через функцию ошибок Си
    cdf_d1 = 0.5 * (1.0 + math.erf(d1 / 1.4142135623730951))
    cdf_d2 = 0.5 * (1.0 + math.erf(d2 / 1.4142135623730951))
    
    # Финальный расчет премии
    if option_type == 'C':
        premium = S * cdf_d1 - K * math.exp(-r * T) * cdf_d2
    else:
        premium = K * math.exp(-r * T) * (1.0 - cdf_d2) - S * (1.0 - cdf_d1)
    
    logger.debug(f'premoium3 {premium}' )
    return premium


def parseBaseCoin(contractSymbol: str):
    base_coin = ''
    """
    Динамически вырезает имя базового актива 
    (например, BTC, DOGE) из любой маркировки.
    Успешно обрабатывает форматы: 'DOGE-17JUN26-0.009-C',
    'BTC-26JUN26-70000-C' и др.
    """
    # Переводим в верхний регистр и очищаем от возможных спецсимволов CCXT
    clean = contractSymbol.upper().replace('/', '').replace(':', '') 
    
    if '-' in clean:
        base_coin = clean.split('-')[0]
    else:
        base_coin = clean
        
    if base_coin.endswith('USDT') and base_coin != 'USDT':
        base_coin = base_coin.replace('USDT', '')
    logger.info(f' base_coin  = {base_coin} ') 
    return base_coin


def calculateVolatilityFromPrices(prices: list, 
                                  base_coin: str, 
                                  window: int = 30) -> float:
    """
    Считает Историческую Годовую Волатильность (HV) 
    на основе списка цен закрытия.
    Использует векторные вычисления Pandas и Numpy.
    """
    # Справочник "Умных дефолтов" на случай, если 
    # сетевой модуль не смог скачать свечи.
    # Защищает робота от зависания, выдавая 
    # адекватную норму для каждой монеты.
    smart_defaults = {
        'BTC': 0.50,   # 50% годовых
        'ETH': 0.60,   # 60% годовых
        'SOL': 0.75,   # 75% годовых
        'MNT': 0.77,
        'XRP': 0.77,
        'DOGE': 0.85   # 85% годовых
    }
    
     # Если монета редкая и её нет в словаре, 
     # ставим средний дефолт альткоинов (70%)
    fallback_value = smart_defaults.get(base_coin, 0.70)
    
    # Проверка: если список цен пустой или 
    # сломался интернет — сразу выдаем умный дефолт
    if not prices or len(prices) < (window+1): 
        logger.warning(f"prices {prices}. " 
                       f"base_coin  {base_coin} "
                       f"fallbsck value {fallback_value} "
                       f"window {window}")
        return fallback_value
    
    try:
        #1. download data v table pandas cherz Dataframe
        df = pd.DataFrame(prices, columns=['close'])
        
        # 2. Считаем логарифмическую доходность: 
        # ln(Цена_сегодня / Цена_вчера)
        # Метод .shift(1) сдвигает цены на 1 день назад, 
        # позволяя делить текущую строку на предыдущую
        # np.log осуществляет векторный расчет логарифма 
        # по всему столбцу мгновенно
        df['log_return'] = np.log(df['close'] 
                                  / df['close'].shift(1)) 
        
        # 3. Находим стандартное отклонение
        # (Standard Deviation) за выбранное окно (30 дней)
        # Метод .tail(window) отсекает только последние
        # нужные нам дни
        # Метод .std() в Pandas по умолчанию использует
        # ddof=1 (несмещенная финансовая оценка) 
        daily_std = df['log_return'].tail(window).std()
        
        # 4. Аннуализация: переводим дневную волатильность
        # в годовую (Sigma)
        # Так как крипторынок работает без выходных, 
        # в году ровно 365 торговых дней
        sigma = daily_std * math.sqrt(365)
        
         # Защитная проверка: если 
         # в расчетах проскочил NaN или бесконечност
        if pd.isna(sigma) or sigma <=0:
            logger.warning(f'Ошибка математических расчетов '
                           f'(NaN). Для {base_coin} применен' 
                           f'дефолт {fallback_value}')
            return fallback_value
        
        logger.info(f"Рассчитана волатильность для "
                    f"{base_coin} за {window} дней: "
                    f"{round(sigma, 4)}")
        return round(sigma, 4)
    
    except Exception as e:
          # Если произошла непредвиденная 
          # ошибка в расчетах — страхуем робота дефолt   
        logger.error(f"Рассчитана волатильность "
                     f"для  {base_coin} за {window}"
                     f"дней:  {round(sigma, 4)}")
        return fallback_value
  
  
  
# =====================================================
#              analytics data
# ====================================================
  
def get_valid_coin_input(all_coins):
    """
    Защищенная функция для ввода монеты.
    Цикл не выпустит пользователя, пока он не введет корректный актив.
    """
    while True:
        try:
            # Запрашиваем ввод, очищаем от пробелов и переводим в верхний регистр
            name_coin = input("Введите наименование монеты из списка указанных выше (или 'EXIT' для выхода): ").strip().upper()
            
            if name_coin == 'EXIT':
                logger.info("Выход из программы по требованию пользователя.")
                return None
                
            # Проверяем, есть ли введенная монета в списке доступных на Bybit
            if name_coin in all_coins:
                return name_coin
            else:
                # Если монеты нет в списке, принудительно вызываем исключение (ValueError)
                raise ValueError(f"Монеты '{name_coin}' нет в списке доступных опционов Bybit!")
                
        except ValueError as err:
            # Перехватываем нашу ошибку ввода и показываем пользователю, не роняя скрипт
            logger.warning(f"Ошибка ввода: {err} Пожалуйста, попробуйте еще раз.")
        except Exception as e:
            # Перехватываем любые критические непредвиденные ошибки (например, Ctrl+C)
            logger.error(f"Непредвиденная ошибка при вводе: {e}")
            
            
def get_valid_date_input(allDateExpiration=dict):
    """
    Защищенная функция для ввода монеты.
    Цикл не выпустит пользователя, пока он не введет корректный актив.
    """
    while True:
        try:
            # Запрашиваем ввод, очищаем от пробелов и переводим в верхний регистр
            date_expirition = input(f"Выбери дату экспирации и введите номер указанных"
                              f"в словоре (или 'EXIT' для выхода): ").strip()
            
            if date_expirition.upper() == 'EXIT':
                logger.info("Выход из программы по требованию пользователя.")
                return None
            
            # Переводим строковый ввод пользователя в целое число (int)
            chosen_key = int(date_expirition)
            
            # ИСПРАВЛЕНО: Прямо проверяем, есть ли этот числовой ключ в словаре
            # Теперь ключ 0 обрабатывается идеально
            if chosen_key in allDateExpiration:
                return allDateExpiration[chosen_key]
            else:
                # Если нет в словоре, принудительно вызываем исключение (ValueError)
                   raise ValueError(f"Нет такого ключа '{date_expirition}' в Bybit!")
                
        except ValueError as err:
            # Перехватываем нашу ошибку ввода и показываем пользователю, не роняя скрипт
            logger.warning(f"Ошибка ввода: {err} Пожалуйста, попробуйте еще раз.")
        except Exception as e:
            # Перехватываем любые критические непредвиденные ошибки (например, Ctrl+C)
            logger.error(f"Непредвиденная ошибка при вводе: {e}")
            

def parse_option_ticker(ticker: str) -> dict:
    # Регулярное выражение для поиска: 
    # Базовый_актив - Дата - Страйк - Тип
    # Поддерживает форматы 'SOL/USDT:USDT-260621-74-C'
    # и 'SOL-260621-74-C'
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
        "type": option_type, }
    
  
def format_date_to_bybit(date_str: str) -> str:
    """
    Конвертирует стандартную дату '2026-07-11' в формат Bybit '11JUL26'.
    """
    try:
        # 1. Парсим входящую строку в объект даты
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
        
        # 2. Форматируем в нужный вид: 
        # %d - день (11), %b - короткое имя месяца (JUL), %y - две цифры года (26)
        bybit_date = parsed_date.strftime("%d%b%y")
        
        # 3. Принудительно делаем буквы заглавными (Bybit API v5 требует только капс)
        return bybit_date.upper()
        
    except Exception as e:
        print(f"Ошибка конвертации даты {date_str}: {e}")
        return ""


def allSymbolBybitOption(dataTicPrice:dict,
                         nameOptin=str,):
    """
    собираем симбол для байбит

    """

    while True:
        try:
            # Запрашиваем ввод, очищаем от пробелов и переводим в верхний регистр
            callAndPut = input(f"Введи Put или Call опцион"
                                    f"(или 'EXIT' для выхода): ").upper()
            
            if callAndPut == 'EXIT':
                logger.info("Выход из программы по требованию пользователя.")
                return None
            
            if callAndPut == 'CALL':
                nameOptin=nameOptin+'-'+str(dataTicPrice['strikeCall'][0][1][0])
                return nameOptin + '-' + 'C'
            
            elif callAndPut == 'PUT':
                nameOptin=nameOptin+'-'+str(dataTicPrice['strikePut'][0][1][0])
                return nameOptin + '-' + 'P'
                
        except ValueError as err:
            # Перехватываем нашу ошибку ввода и показываем пользователю, не роняя скрипт
            logger.warning(f"Ошибка ввода: {err} Пожалуйста, попробуйте еще раз.")
        except Exception as e:
            # Перехватываем любые критические непредвиденные ошибки (например, Ctrl+C)
            logger.error(f"Непредвиденная ошибка при вводе: {e}")
            
       
def generate_option_grid_premiums(
        ticCallPutStrikePrice: dict, 
        nameFullOption: str, 
        sigma_: float, 
        calculatorT: float) -> dict:
    
    """
    [ФУНКЦИЯ ДЛЯ АНАЛИТИКИ] 
    Пробегает по всей сетке страйков, рассчитывает 
    премии для Call и Put,
    и динамически привязывает к ним готовый для биржи 
    текстовый символ контракта.
    """
    spot_price = ticCallPutStrikePrice.get('ticPrice', 0.0)
    calculated_calls = []
    calculated_puts = []

    # 1. Расчет для CALL опционов
    if 'strikeCall' in ticCallPutStrikePrice:
        for strike in ticCallPutStrikePrice['strikeCall']:
            premia_call = calculate_black_scholes_fast3(
                S=spot_price, 
                K=strike, 
                sigma=sigma_, 
                r=0.02, 
                T=calculatorT, 
                option_type='call'
            )
            clean_strike = f"{float(strike):g}"
            trade_symbol = f"{nameFullOption}-{clean_strike}-C"
            
            calculated_calls.append({
                'strike': float(clean_strike),
                'premium': premia_call,
                'symbol': trade_symbol
            })

    # 2. Расчет для PUT опционов
    if 'strikePut' in ticCallPutStrikePrice:
        for strike in ticCallPutStrikePrice['strikePut']:
            premia_put = calculate_black_scholes_fast3(
                S=spot_price, K=strike, sigma=sigma_, r=0.02, T=calculatorT, option_type='put'
            )
            clean_strike = f"{float(strike):g}"
            trade_symbol = f"{nameFullOption}-{clean_strike}-P"
            
            calculated_puts.append({
                'strike': float(clean_strike),
                'premium': premia_put,
                'symbol': trade_symbol
            })

    return {
        'ticPrice': spot_price,
        'calls_grid': calculated_calls,
        'puts_grid': calculated_puts
    }
