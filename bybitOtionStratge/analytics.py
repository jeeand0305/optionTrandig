import math
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


def calculate_black_scholes_fast3(S, K, r, sigma, T, option_type='C'):
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
    
    logger.info(f'premoium3 {premium}' )
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
        
        logger.info(f"Рассчитана волатильность для"
                    f"{base_coin} за {window} дней:"
                    f"{round(sigma, 4)}")
        return round(sigma, 4)
    
    except Exception as e:
          # Если произошла непредвиденная 
          # ошибка в расчетах — страхуем робота дефолt   
        logger.error(f"Рассчитана волатильность "
                     f"для {base_coin} за {window}"
                     f"дней: {round(sigma, 4)}")
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
                              f"в словоре (или 'EXIT' для выхода): ")
            
            if date_expirition == 'EXIT' or 'exit' == date_expirition:
                logger.info("Выход из программы по требованию пользователя.")
                return None
            
            if int(date_expirition):
                logger.info(f"Вы ввели не целое число")
                date_expirition = int(date_expirition)
                # Проверяем, есть ли введенная монета в списке доступных на Bybit
                if date_expirition in allDateExpiration:
                    return allDateExpiration[date_expirition]
            else:
                # Если нет в словоре, принудительно вызываем исключение (ValueError)
                   raise ValueError(f"Нет такого ключа '{date_expirition}' в Bybit!")
                
        except ValueError as err:
            # Перехватываем нашу ошибку ввода и показываем пользователю, не роняя скрипт
            logger.warning(f"Ошибка ввода: {err} Пожалуйста, попробуйте еще раз.")
        except Exception as e:
            # Перехватываем любые критические непредвиденные ошибки (например, Ctrl+C)
            logger.error(f"Непредвиденная ошибка при вводе: {e}")
            

  
# test work coda   
# _______________________________________________________
# from bybit_client import BybitOptionBot
# listP = [85.23, 85.37, 84.31, 86.16, 87.34, 82.44, 81.27, 74.23, 71.62, 68.87, 63.63, 62.2, 66.5, 66.82, 64.98, 63.19,66.92, 66.82, 68.92, 71.27, 73.98, 75.01]
# bybitCandals=BybitOptionBot().get_historical_closes(
#     base_coin='DOGE'
# )
# logger.info(f'listP {type(listP[0])}')
# logger.info(f'bybitCandals {type(bybitCandals[0])}')
# volatilityPrice = calculateVolatilityFromPrices(
#     prices=bybitCandals,
#     base_coin='DOGE-20JUN26-0.009-C', 
# )    
# logger.info(f'calculateVolatilityFromPrices'
#             f'{volatilityPrice}')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        