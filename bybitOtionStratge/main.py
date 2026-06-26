import analytics, bybit_client
import os
import time
from logger import logger
import ccxt
from dotenv import load_dotenv

# =====================================================================
# ЭТАП 1: НАСТРОЙКА ОКРУЖЕНИЯ И ЛОГИРОВАНИЯ
# =====================================================================

def main():
    '''
    nalichie balance
    '''
    clientBybit=bybit_client.BybitOptionBot()
    mybalance=clientBybit.check_connection_and_balance()    
    logger.info(f'My Balance + margin {mybalance['total_equity']} '
                f' margin {mybalance['total_margin']}')
    
    allCoine=clientBybit.get_all_option_coins()
    logger.info(f'Выбери монету ищ списка для работы {allCoine}')

    nameCoin = input("Введт ниенования монеты из списка уазаных выше :")
    allDatesExpiration=clientBybit.get_option_expiration_dates(base_coin=nameCoin)
    logger.info(f'Выберете из представленызх дату экспернации оптион '
                f'{allDatesExpiration}')
# =====================================================================
# ТОЧКА ЗАПУСКА
# =====================================================================
if __name__ == "__main__":
    logger.info("Запуск инициализации торгового робота...")
    
    main()
    
    # Создаем экземпляр нашего бота
    # bot = BybitOptionBot()
    
    # # Проверяем баланс и выводим цену Solana
    # margin = bot.check_connection_and_balance()
    # if margin is not None:
    #     bot.get_sol_price()
