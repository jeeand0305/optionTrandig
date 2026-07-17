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
    # V 1 Получения баланса
    # V 2. получаем список монет
    # V 3. отбираем монеты 
    # V 4. получаем страки опционов (ДАТЫ)
    # V 5. виаулизация опционов выбраной экспирацию страйков, премий, симбол
    # 6. выбираем колл или пут оционы
    # 7. выбираем покупка или продажа опциона
    # 8. открываем ордер
    # 9. проверям наличие продоных опционов
    # 10. сравниваем страк и тик прайс
    # 11. открываем хэдж фючом если опцион заходит в деньги
    # 12. отслеживаем открыт ли фючь и если опцион в деньгах
    # 13. закрываем фючь 
    #     13.1. если вышла дата экспирации опциона
    #     13.2. если если опцион зашел вне денег
        
        
        
        
    # ========================================================================
    # 1 Получения баланса 
    logger.info(f"1 Получения баланса ")
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
    
    
    # ==========================================================================
    # 2. получаем список монет
    logger.info(f"2. получаем список монет")
    # Получаем список всех доступных монет для опционов
    allCoine=clientBybit.get_all_option_coins()
    logger.info(f'Выбери монету из списка для работы: {allCoine}')


    # ======================================================================
     # 3. отбираем монеты 
    logger.info(f"3. отбираем монеты ")
    # ВЫЗОВ ЗАЩИЩЕННОГО ВВОДА монеты для торговли опциона )
    nameCoin = analytics.get_valid_coin_input(all_coins=allCoine)
    nameFullOption=nameCoin
    
    # Получаем доступные даты экспирации для выбранной монеты
    allDatesExpiration=clientBybit.get_option_expiration_dates(
        base_coin=nameCoin)
    logger.info(f'Выберете из представленызх дату экспернации оптион '
                f'{allDatesExpiration}')
    
    
    # ==================================================================
    # 4. получаем страки опционов (ДАТЫ)
    # ввести ключ даты экспирации
    logger.info(f"4. получаем страки опционов (ДАТЫ)")
    dateExpertion=analytics.get_valid_date_input(
        allDateExpiration=allDatesExpiration)
    logger.info(f"Вы выбрали дату: {dateExpertion}")
    dateBybitExper=analytics.format_date_to_bybit(dateExpertion)
    nameFullOption=nameFullOption + '-' + dateBybitExper 
    
    ticCallPutStrikePrice=clientBybit.get_option_strikes(
        base_coin=nameCoin, expiration_date=dateExpertion) 
    logger.info(f" ticCallPutStrikePrice {ticCallPutStrikePrice} ")
    

    # ===================================================================
    # 5. виаулизация опционов выбраной экспирацию страйков, премий, симбол 
    logger.info(f"5. виаулизация опционов выбраной экспирацию страйков, премий, симбол")
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
    
    # Извлекаем текущую цену спота из словаря
    spot_price = ticCallPutStrikePrice.get('ticPrice')
    
    
    # ==================================================
    # тест функции генирации опциона с премией
    strikeSellPut4=analytics.generate_option_grid_premiums(
        ticCallPutStrikePrice=ticCallPutStrikePrice,
        nameFullOption=nameFullOption,
        sigma_=sigma_,
        calculatorT=calculatorT
    )
    logger.info(f"тест функции генирации опциона с "
                f"премией  {strikeSellPut4}")
  
    
    
    # # Создаем новые чистые списки, куда запишем страйки вместе с рассчитанными премиями
    # calculated_calls = []
    # calculated_puts = []

    # # 1. Расчет для CALL опционов
    # if 'strikeCall' in ticCallPutStrikePrice:
    #     for idx, strike in enumerate(ticCallPutStrikePrice['strikeCall']):
    #         premia_call = analytics.calculate_black_scholes_fast3(
    #             S=spot_price,
    #             K=strike,
    #             sigma=sigma_,
    #             r=0.02,
    #             T=calculatorT,
    #             option_type='call' # убедитесь, что ваша функция принимает тип опциона
    #         )
    #         # Сохраняем в структуре: [{Номер: [Страйк, Премия]}]
    #         calculated_calls.append({idx + 1: [strike, premia_call]})

    # # 2. Расчет для PUT опционов
    # if 'strikePut' in ticCallPutStrikePrice:
    #     for idx, strike in enumerate(ticCallPutStrikePrice['strikePut']):
    #         premia_put = analytics.calculate_black_scholes_fast3(
    #             S=spot_price,
    #             K=strike,
    #             sigma=sigma_,
    #             r=0.02,
    #             T=calculatorT,
    #             option_type='put'
    #         )
    # #         calculated_puts.append({idx + 1: [strike, premia_put]})

    # # Обновляем наш словарь финальными массивами данных
    # ticCallPutStrikePrice['strikeCall'] = calculated_calls
    # ticCallPutStrikePrice['strikePut'] = calculated_puts
    
    logger.info(f"Расчет премий завершен успешно. {ticCallPutStrikePrice}")

    # собираю симбол опциона
    symbolOptionBybit = analytics.allSymbolBybitOption(
        dataTicPrice=ticCallPutStrikePrice,
        nameOptin=nameFullOption)
    
    logger.info(f"symbolOptionBybit {symbolOptionBybit}")
    
    #  покупка опциона 
    
    # order_result = clientBybit.place_option_order2(
    #     symbol=strikeSellPut4['calls_grid'][1]['symbol'],
    #     side='sell',
    #     qty=configBybit.priceCoinMinOrder[nameCoin.upper()],
    #     price=strikeSellPut4['calls_grid'][1]['premium'],   ) 
        
    # )
    # order_result = clientBybit.chase_order(
    #     symbol=
    # )
# ============================================================
# ТОЧКА ЗАПУСКА
# ============================================================
if __name__ == "__main__":
    logger.info("Запуск инициализации торгового робота...")
    
    main()
    
    # Создаем экземпляр нашего бота
    # bot = BybitOptionBot()
    
    # # Проверяем баланс и выводим цену Solana
    # margin = bot.check_connection_and_balance()
    # if margin is not None:
    #     bot.get_sol_price()
