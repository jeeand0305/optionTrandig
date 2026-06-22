import math
import numpy as np 
import pandas as pd
from datetime import datetime, timezone
from logger import logger


def parseBaseCoin(contractSymbol: str):
    base_coin = ''
    """
    Динамически вырезает имя базового актива (например, BTC, DOGE) из любой маркировки.
    Успешно обрабатывает форматы: 'DOGE-17JUN26-0.009-C', 'BTC-26JUN26-70000-C' и др.
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        