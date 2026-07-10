import analytics
import bybit_client
import configBybit
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
    nameFullOption=''
    clientBybit=bybit_client.BybitOptionBot()
    mybalance=clientBybit.check_connection_and_balance()  
       
    # Проверка на случай, если метод вернул None из-за ошибки подключения
    if not mybalance:
        logger.error("Не удалось получить баланс. Завершение работы.")
        return    
   
    # получение баланса на счете  
    logger.info(f'My Balance + margin {mybalance["total_equity"]} '
                f' margin {mybalance["total_margin"]}')
    
    # Получаем список всех доступных монет для опционов
    allCoine=clientBybit.get_all_option_coins()
    logger.info(f'Выбери монету из списка для работы: {allCoine}')

    # ВЫЗОВ ЗАЩИЩЕННОГО ВВОДА монеты для торговли опциона )
    nameCoin = analytics.get_valid_coin_input(all_coins=allCoine)
    nameFullOption=nameCoin
    
    # Получаем доступные даты экспирации для выбранной монеты
    allDatesExpiration=clientBybit.get_option_expiration_dates(
        base_coin=nameCoin)
    logger.info(f'Выберете из представленызх дату экспернации оптион '
                f'{allDatesExpiration}')
    
    # ввести ключ даты экспирации
    dateExpertion=analytics.get_valid_date_input(
        allDateExpiration=allDatesExpiration)
    logger.info(f"Вы выбрали дату: {dateExpertion}")
    dateBybitExper=analytics.format_date_to_bybit(dateExpertion)
    nameFullOption=nameFullOption + '-' + dateBybitExper 
    
    ticCallPutStrikePrice=clientBybit.get_option_strikes(
        base_coin=nameCoin, expiration_date=dateExpertion) 
    logger.info(f" ticCallPutStrikePrice {ticCallPutStrikePrice} ")
    
    # минимальная стоимость опциона 
    logger.info(f" минимальная объем (buy or sell) опциона"
                f"{configBybit.priceCoinMinOrder[nameCoin.upper()]} ")
    
    # Расчет волотильности
        # а. последние 30 свечей
    сandals30=clientBybit.get_historical_closes_candals(
        base_coin=nameCoin)
        # б. 
    sigma_=analytics.calculateVolatilityFromPrices(
        prices=сandals30,
        base_coin=nameCoin)  
        # в.
    calculatorT=analytics.calculate_time_to_expiration(
        expiration_date=dateExpertion
    )
    
    # Стоимость премии опционов
    
        # =====================================================================
    # ЭТАП 2: РАСЧЕТ ПРЕМИЙ ОПЦИОНОВ (CALL И PUT)
    # =====================================================================
    # Извлекаем текущую цену спота из словаря
    spot_price = ticCallPutStrikePrice.get('ticPrice')
    
    # Создаем новые чистые списки, куда запишем страйки вместе с рассчитанными премиями
    calculated_calls = []
    calculated_puts = []

    # 1. Расчет для CALL опционов
    if 'strikeCall' in ticCallPutStrikePrice:
        for idx, strike in enumerate(ticCallPutStrikePrice['strikeCall']):
            premia_call = analytics.calculate_black_scholes_fast3(
                S=spot_price,
                K=strike,
                sigma=sigma_,
                r=0.02,
                T=calculatorT,
                option_type='call' # убедитесь, что ваша функция принимает тип опциона
            )
            # Сохраняем в структуре: [{Номер: [Страйк, Премия]}]
            calculated_calls.append({idx + 1: [strike, premia_call]})

    # 2. Расчет для PUT опционов
    if 'strikePut' in ticCallPutStrikePrice:
        for idx, strike in enumerate(ticCallPutStrikePrice['strikePut']):
            premia_put = analytics.calculate_black_scholes_fast3(
                S=spot_price,
                K=strike,
                sigma=sigma_,
                r=0.02,
                T=calculatorT,
                option_type='put'
            )
            calculated_puts.append({idx + 1: [strike, premia_put]})

    # Обновляем наш словарь финальными массивами данных
    ticCallPutStrikePrice['strikeCall'] = calculated_calls
    ticCallPutStrikePrice['strikePut'] = calculated_puts
    
    logger.info(f"Расчет премий завершен успешно. {ticCallPutStrikePrice}")

    symbolOptionBybit = analytics.allSymbolBybitOption(
        dataTicPrice=ticCallPutStrikePrice,
        nameOptin=nameFullOption)
    
    logger.info(f"symbolOptionBybit {symbolOptionBybit}")

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
