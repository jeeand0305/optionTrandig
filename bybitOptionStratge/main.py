import sys
import os

# Находим путь к корневой директории ProjectOption
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Теперь твои оригинальные импорты сработают без ошибок!
import bybit_client
import analytics
import configBybit
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
    # V 4. получаем и выбираем дату экспирации опционов (ДАТЫ)
    # V 5. виаулизация опционов выбраной экспирацию страйков, премий, симбол
    # V 6. выбираем колл или пут оционы
    # V 7. выбираем покупка или продажа опциона
    # V 8. открываем ордер
    # 9. проверям наличие продоных опционов
    # 10. сравниваем страк и тик прайс
    # 11. открываем хэдж фючом если опцион заходит в деньги
    # 12. отслеживаем открыт ли фючь и если опцион в деньгах
    # 13. закрываем фючь 
    #     13.1. если вышла дата экспирации опциона
    #     13.2. если если опцион зашел вне денег
        
        
        
        
    # ========================================================================
    # 1 Получения баланса 
    logger.warning(f"1 Получения баланса ")
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
    logger.warning(f"2. получаем список монет")
    # Получаем список всех доступных монет для опционов
    allCoine=clientBybit.get_all_option_coins()
    logger.info(f'Выбери монету из списка для работы: {allCoine}')


    # ======================================================================
     # 3. отбираем монеты 
    logger.warning(f"3. отбираем монеты ")
    # ВЫЗОВ ЗАЩИЩЕННОГО ВВОДА монеты для торговли опциона )
    nameCoin = analytics.get_valid_coin_input(all_coins=allCoine)
    nameFullOption=nameCoin
    
    # Получаем доступные даты экспирации для выбранной монеты
    allDatesExpiration=clientBybit.get_option_expiration_dates(
        base_coin=nameCoin)
    
    
    # ==================================================================
    # 4. получаем страки опционов (ДАТЫ)
    # ввести ключ даты экспирации
    logger.warning(f"4. получаем дату экспирации опционов (ДАТЫ)")    
    logger.debug(f'Выберете из представленызх дату экспернации оптион ')
    for key, volme in  allDatesExpiration.items():
        logger.info(f"ключь {key} эксперация {volme}")
    # logger.info(f'Выберете из представленызх дату экспернации оптион '
    #             f'{allDatesExpiration}')
    
    dateExpertion=analytics.get_valid_date_input(
        allDateExpiration=allDatesExpiration)
    logger.info(f"Вы выбрали дату: {dateExpertion}")
    dateBybitExper=analytics.format_date_to_bybit(dateExpertion)
    nameFullOption=nameFullOption + '-' + dateBybitExper 
    
    ticCallPutStrikePrice=clientBybit.get_option_strikes(
        base_coin=nameCoin, expiration_date=dateExpertion) 
    logger.debug(f" ticCallPutStrikePrice {ticCallPutStrikePrice} ")

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
        expiration_date=dateExpertion)
    
    # Извлекаем текущую цену спота из словаря
    spot_price = ticCallPutStrikePrice.get('ticPrice')
    
    
    # ===================================================================
    # 5. виаулизация опционов выбраной экспирацию страйков, премий, симбол 
    logger.warning(f"5. виаулизация опционов выбраной экспирацию"
                   f"страйков, премий, симбол")
    
    # тест функции генирации опциона с премией
    strikeSellPut4=analytics.generate_option_grid_premiums(
        ticCallPutStrikePrice=ticCallPutStrikePrice,
        nameFullOption=nameFullOption,
        sigma_=sigma_,
        calculatorT=calculatorT)
    
    print(f"ticPrice {strikeSellPut4['ticPrice']} ")
    
    for key, volmes in strikeSellPut4.items():
        if key == 'calls_grid':
            count=0
            print('Call')
            for volme in volmes:
                print(f"{count} {volme}")
                count+=1
        elif key == 'puts_grid':
            count=0
            print('Put')
            for volme in volmes:
                print(f"{count} {volme}")
                count+=1
  
  
    # ==============================================================
    logger.warning(f"6. выбираем колл или пут оционы")
    # собираю симбол опциона
    symbolOptionBybit = analytics.allSymbolBybitOption(
        dataTicPrice=strikeSellPut4,
        nameOptin=nameFullOption)
    
    
    # ==============================================================
    logger.warning(f" 7. выбираем покупка или продажа опциона")
    logger.debug(f"1 symbolOptionBybit {symbolOptionBybit}")
    symbolOptionBybit2 = analytics.selctionBuySell(
        dataTicStrikePremiumSymbol=symbolOptionBybit)
    logger.info(f"2 symbolOptionBybit {symbolOptionBybit2}")
    
    #  покупка опциона 
    # =============================================================  
    logger.warning(f"8. открываем ордер")
    # Универсальный алгоритм преследования цены (Chase) 
    # для неликвидных опционов.
    success = clientBybit.chase_order(
        symbol=symbolOptionBybit2['symbol'],          # Сделай 'O' большой
        side=symbolOptionBybit2['buyOrSell'],        # Сделай 'O' большой
        qty=analytics.selctionQty(),
        price_limit=symbolOptionBybit2['premium'],    # Сделай 'O' большой
        check_interval_sec=30,
        slippage_step_pct=1,
        max_slippage_pct=20)   
   

    logger.info(f"{success}")
    

def main2():
    clientBybit=bybit_client.BybitOptionBot()
    count = 0    
    while count < 10:
        
        
        optionsAll = clientBybit.get_active_open_options3()
        futuresAll = clientBybit.get_active_futures_positions()
        
        clientBybit.process_hedging_logic3(
            optionsAll=optionsAll,
            futuresAll=futuresAll)
        
        # clientBybit.aggregate_coin_data(nameCoin='SOL',
        #                                 optionsList=optionsAll['SOL'],
        #                                 futuresAll=futuresAll['SOL'])
        
        time.sleep(60)
        count +=1
        
    
    ...    
    
    
# ============================================================
# ТОЧКА ЗАПУСКА
# ============================================================
if __name__ == "__main__":
    logger.info("Запуск инициализации торгового робота...")
    

    main2()
    
    # main()
    
    # Создаем экземпляр нашего бота
    # bot = BybitOptionBot()
    
    # # Проверяем баланс и выводим цену Solana
    # margin = bot.check_connection_and_balance()
    # if margin is not None:
    #     bot.get_sol_price()
