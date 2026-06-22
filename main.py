import os
import time
import logging
import ccxt
from dotenv import load_dotenv

# =====================================================================
# ЭТАП 1: НАСТРОЙКА ОКРУЖЕНИЯ И ЛОГИРОВАНИЯ
# =====================================================================
# Загружаем переменные из файла .env
load_dotenv()

API_KEY = os.getenv("BYBIT_API_KEY")
SECRET_KEY = os.getenv("BYBIT_SECRET_KEY")
IS_TESTNET = os.getenv("IS_TESTNET", "True").lower() == "true"

# Настраиваем логирование: вывод и в файл bot.log, и в консоль VS Code
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RatioBot")

# =====================================================================
# ЭТАП 2: ИНИЦИАЛИЗАЦИЯ БИРЖИ (CCXT)
# =====================================================================
class BybitOptionBot:
    def __init__(self):
        # Настройка параметров подключения к Bybit
        exchange_config = {
            'apiKey': API_KEY,
            'secret': SECRET_KEY,
            'enableRateLimit': True,  # Защита от бана за частые запросы
            'options': {
                'defaultType': 'swap',  # По умолчанию работаем с фьючерсами (swap)
            }
        }
        
        self.exchange = ccxt.bybit(exchange_config)
        
        # Если в .env указано True, переключаем библиотеку в демо-режим (Testnet)
        if IS_TESTNET:
            self.exchange.set_sandbox_mode(True)
            logger.info("Бот запущен в режиме ТЕСТНЕТА (Демо-счет).")
        else:
            logger.info("ВНИМАНИЕ: Бот запущен на РЕАЛЬНОМ счету!")

    def check_connection_and_balance(self):
        """Проверяет подключение к бирже и выводит доступную маржу."""
        try:
            # Запрашиваем баланс Единого Торгового Аккаунта (UTA)
            balance = self.exchange.fetch_balance()
            
            # Извлекаем свободные USDT для маржи фьючерсов
            usdt_free = balance.get('USDT', {}).get('free', 0.0)
            logger.info(f"Успешное подключение к API Bybit!")
            logger.info(f"Доступная маржа для защиты позиции: {usdt_free} USDT")
            return usdt_free
        except Exception as e:
            logger.error(f"Ошибка подключения к бирже. Проверьте API-ключи: {e}")
            return None

    def get_sol_price(self):
        """Получает текущую цену Solana для мониторинга краев."""
        try:
            # Символ бессрочного фьючерса Solana на Bybit по стандартам CCXT
            ticker = self.exchange.fetch_ticker('SOL/USDT:USDT')
            current_price = ticker['last']
            logger.info(f"Текущая цена SOL: {current_price} USDT")
            return current_price
        except Exception as e:
            logger.error(f"Не удалось получить цену Solana: {e}")
            return None

# =====================================================================
# ТОЧКА ЗАПУСКА
# =====================================================================
if __name__ == "__main__":
    logger.info("Запуск инициализации торгового робота...")
    
    # Создаем экземпляр нашего бота
    bot = BybitOptionBot()
    
    # Проверяем баланс и выводим цену Solana
    margin = bot.check_connection_and_balance()
    if margin is not None:
        bot.get_sol_price()
