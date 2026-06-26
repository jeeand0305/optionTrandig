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
       
    # Проверка на случай, если метод вернул None из-за ошибки подключения
    if not mybalance:
        logger.error("Не удалось получить баланс. Завершение работы.")
        return    
    
    logger.info(f'My Balance + margin {mybalance["total_equity"]} '
                f' margin {mybalance["total_margin"]}')
    
    # Получаем список всех доступных монет для опционов
    allCoine=clientBybit.get_all_option_coins()
    logger.info(f'Выбери монету ищ списка для работы {allCoine}')

    # ВЫЗОВ ЗАЩИЩЕННОГО ВВОДА (Вместо старого nameCoin = input())
    nameCoin = analytics.get_valid_coin_input(all_coins=allCoine)
    
    # Получаем доступные даты экспирации для выбранной монеты
    allDatesExpiration=clientBybit.get_option_expiration_dates(base_coin=nameCoin)
    logger.info(f'Выберете из представленызх дату экспернации оптион '
                f'{allDatesExpiration}')
    
    # ввести ключ даты экспирации
    dateExpertion=analytics.get_valid_date_input(
        allDateExpiration=allDatesExpiration)
    logger.info(f" {dateExpertion}")
    
    
    
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
