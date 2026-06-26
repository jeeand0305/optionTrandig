import math
from scipy.stats import norm
from logger import logger
import time
from functools import wraps
from functools import wraps
from setuptools import setup
from Cython.Build import cythonize
from datetime import datetime, timezone
# import setup

# setup(ext_modules=cythonize("bs_module.pyx"))

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

S_=0.08632
K_=0.06
r_=0.05 
sigma_=1.0047 
T_=16
option_type_='C'

@benchmark_timer
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
    T=T/365 #drob ot (countDay/1year)
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


@benchmark_timer
def calculate_time_to_expiry(expiry_str=None):
    dictData = {}
    
    # Задаем текущее время в UTC
    now = datetime.now(timezone.utc)
    dictData['nowDate'] = now
    
    # Проверка на пустой ввод
    if expiry_str is None:
        logger.info("expiry_str is None")
        return 0.0

    try:
        # Парсим дату и принудительно устанавливаем ей таймзону UTC
        expiry_date = datetime.strptime(expiry_str, "%y%m%d").replace(tzinfo=timezone.utc)
        dictData['expiry_date'] = expiry_date
    except ValueError as e:
        logger.error(f"Неверный формат даты: {e}")
        return 0.0
        
    # Считаем разницу
    time_delta = expiry_date - now
    seconds_left = time_delta.total_seconds()
    
    if seconds_left <= 0:
        return 0.0
        
    # Количество секунд в году (365 дней)
    seconds_in_year = 365 * 24 * 60 * 60
    dictData['division'] = seconds_left / seconds_in_year
    
    # logger.info(f'dictData: {dictData}')
    return dictData

# Исправлен синтаксис кавычек во внешней f-строке
logger.info(f"timeToExpir {calculate_time_to_expiry(expiry_str='260830')}")
