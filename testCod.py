import sys
import os

# Автоматически добавляем корень проекта и папку со стратегией в пути Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'bybitOptionStratge'))

# Теперь оригинальные импорты отработают без ошибок
from logger import logger
from bybitOptionStratge.method_symbols import OptionAsset
from dotenv import load_dotenv
import ccxt
from bybitOptionStratge.bybit_client import BybitOptionBot

# Дальше ваши тестовые данные (open_futures1, open_options1 и т.д.)

open_futures1 = {'SOL': {'symbol': 'SOL/USDT:USDT', 'side': 'buy', 'size': 1.5, 'openPrice': 75.37941176, 'leverage': 10.0, 'initMargin': 11.5034122}, 'NEAR': {'symbol': 'NEAR/USDT:USDT', 'side': 'buy', 'size': 12.0, 'openPrice': 1.616, 'leverage': 1.0, 'initMargin': 19.5228}}
open_options1 = [{'symbol': 'SOL/USDT:USDT-260814-75-C', 'ccxt_symbol': 'SOL/USDT:USDT-260814-75-C', 'buyOrSell': 'sell', 'size': 3.0, 'entry_price': 0.94, 'hours_to_expiration': 132.35, 'strike': 75.0, 'type': 'CALL', 'futures_symbol': 'SOL/USDT:USDT', 'initMargin': 40.12063646}, {'symbol': 'SOL/USDT:USDT-260814-73-P', 'ccxt_symbol': 'SOL/USDT:USDT-260814-73-P', 'buyOrSell': 'sell', 'size': 3.0, 'entry_price': 1.0, 'hours_to_expiration': 132.35, 'strike': 73.0, 'type': 'PUT', 'futures_symbol': 'SOL/USDT:USDT', 'initMargin': 28.11017423}]

open_options2 = {'SOL': [{'symbol': 'SOL/USDT:USDT-260828-78-C', 'ccxt_symbol': 'SOL/USDT:USDT-260828-78-C', 'buyOrSell': 'sell', 'size': 4.0, 'entry_price': 1.33, 'hours_to_expiration': 217.03, 'strike': 78.0, 'type': 'CALL', 'futures_symbol': 'SOL/USDT:USDT', 'initMargin': 48.10864144}, {'symbol': 'SOL/USDT:USDT-260821-74-P', 'ccxt_symbol': 'SOL/USDT:USDT-260821-74-P', 'buyOrSell': 'sell', 'size': 4.0, 'entry_price': 0.87, 'hours_to_expiration': 49.03, 'strike': 74.0, 'type': 'PUT', 'futures_symbol': 'SOL/USDT:USDT', 'initMargin': 37.41257572}], 'XRP': [{'symbol': 'XRP/USDT:USDT-260820-1-C', 'ccxt_symbol': 'XRP/USDT:USDT-260820-1-C', 'buyOrSell': 'sell', 'size': 20.0, 'entry_price': 0.0071, 'hours_to_expiration': 25.03, 'strike': 1.0, 'type': 'CALL', 'futures_symbol': 'XRP/USDT:USDT', 'initMargin': 4.2830806}, {'symbol': 'XRP/USDT:USDT-260820-0.98-P', 'ccxt_symbol': 'XRP/USDT:USDT-260820-0.98-P', 'buyOrSell': 'sell', 'size': 20.0, 'entry_price': 0.0032, 'hours_to_expiration': 25.03, 'strike': 0.98, 'type': 'PUT', 'futures_symbol': 'XRP/USDT:USDT', 'initMargin': 3.5989536}]}
open_futures2 = {'XRP': {'symbol': 'XRP/USDT:USDT', 'side': 'sell', 'size': 10.0, 'openPrice': 1.0229, 'leverage': 10.0, 'initMargin': 1.0340519}, 'NEAR': {'symbol': 'NEAR/USDT:USDT', 'side': 'buy', 'size': 12.0, 'openPrice': 1.616, 'leverage': 1.0, 'initMargin': 19.4064}, 'SOL': {'symbol': 'SOL/USDT:USDT', 'side': 'buy', 'size': 1.5, 'openPrice': 76.25208792, 'leverage': 10.0, 'initMargin': 11.49544031}}

listData = [{'symbol': 'SOL/USDT:USDT-260828-78-C', 'ccxt_symbol': 'SOL/USDT:USDT-260828-78-C', 'buyOrSell': 'sell', 'size': 4.0, 'entry_price': 1.33, 'hours_to_expiration': 219.21, 'strike': 78.0, 'type': 'CALL', 'futures_symbol': 'SOL/USDT:USDT', 'initMargin': 47.19072183}, {'symbol': 'XRP/USDT:USDT-260820-1-C', 'ccxt_symbol': 'XRP/USDT:USDT-260820-1-C', 'buyOrSell': 'sell', 'size': 20.0, 'entry_price': 0.0071, 'hours_to_expiration': 27.21, 'strike': 1.0, 'type': 'CALL', 'futures_symbol': 'XRP/USDT:USDT', 'initMargin': 4.23712076}, {'symbol': 'XRP/USDT:USDT-260820-0.98-P', 'ccxt_symbol': 'XRP/USDT:USDT-260820-0.98-P', 'buyOrSell': 'sell', 'size': 20.0, 'entry_price': 0.0032, 'hours_to_expiration': 27.21, 'strike': 0.98, 'type': 'PUT', 'futures_symbol': 'XRP/USDT:USDT', 'initMargin': 3.66835796}, {'symbol': 'SOL/USDT:USDT-260821-74-P', 'ccxt_symbol': 'SOL/USDT:USDT-260821-74-P', 'buyOrSell': 'sell', 'size': 4.0, 'entry_price': 0.87, 'hours_to_expiration': 51.21, 'strike': 74.0, 'type': 'PUT', 'futures_symbol': 'SOL/USDT:USDT', 'initMargin': 37.92337951}]
      

load_dotenv()
API_KEY = os.getenv("BYBIT_API_KEY")
SECRET_KEY = os.getenv("BYBIT_SECRET_KEY")
IS_TESTNET = os.getenv("IS_TESTNET", "True").lower() == "true"

class TestClass:
    
    
    def __init__(self, 
                #  ticPrice: float,
                 futures: dict,
                 options: list):
                        # 1. Формируем единую конфигурацию
        botBybit=BybitOptionBot()
        
        # 2. Инициализируем подключение
        # Используем pro-версию ccxt (опционально, но рекомендуется для стабильности)
        self.exchange = botBybit
        self.futures = futures # open_futures2 # botBybit.get_active_futures_positions()
        self.options = options # botBybit.get_active_open_options3() 
        # self.ticPrice = ticPrice
        self.ddh_coins = ['DOGE']
        self.listData = listData
    
    def process_hedging_logic2(self) -> bool:
        """
        ГЛАВНЫЙ ДИСПЕТЧЕР (Версия 2): Проверяет данные, 
        итерирует портфель по монетам
        и изолирует ошибки через try/except.
        анализируем дание есть проблема True.
        если проблемти нет или перекрыта фючерсом возможная 
        потери применяем False
        """
        logger.info("⏳ Запуск фонового сканирования рисков портфеля.")

        # 1. kusok Вызов внешних универсальных валидаторов структуры
        if not self.is_options_data_valid(options_dict=self.options): 
            return False
            
        if not self.is_futures_data_valid(futures_dict=self.futures):
            return False

        # Если портфель опционов валиден, но пуст — штатный выход
        if not self.options:
            logger.info("ℹ️ Портфель опционов пуст. Хеджирование не требуется.")
            return True
        
        
        # 2 kusok Перебираем сгруппированный словарь опционов по монетам
        for coin_name, options_list in self.options.items():
            coin_upper = coin_name.upper()
            
            # Динамический фильтр: проверяем монету по списку из __init__
            # Если ты решишь отключить DDH на бирже, просто сотри монету из self.ddh_coins при старте
            if coin_upper in self.ddh_coins:
                logger.info(f"ℹ️ {coin_upper} управляется встроенным DDH Bybit. Пропуск.")
                continue
            
            # --- ВНУТРЕННИЙ ЩИТ БЕЗОПАСНОСТИ ДЛЯ КАЖДОЙ МОНЕТЫ ---
            try:
                logger.info(f"🔍 Сканирование рисков для монеты: {coin_upper}")
                coridor_result = self.analizCoridorStrikes(
                    optinsList=options_list,
                    nameCoin=coin_upper)
                
                # vihod iz hegera
                if coridor_result['analizeBool'] == False:
                    return False
                
                # prodolzaem iskat ne zashisheni kray
                # elif coridor_result['analizeBool'] == True:
                #     analizCall_result = self.analizCallStrike(
                #         optionsSellCall=coridor_result['optSellCall'],
                #         nameCoin=coin_upper)
                    
                #     if analizCall_result == False:
                #         return False
                    
                    # elif analizCall_result['analizeBool'] == False:
                    #     return False
                    
                
                # [Сюда стыкуется Кусок 3: вызов analizCoridorStrikes и запуск CALL/PUT веток]
                
            except Exception as coin_error:
                # Если на XRP произойдет технический или сетевой сбой — робот не упадет
                logger.error(f"💥 Критический сбой при обработке монеты {coin_upper}: {coin_error}")
                
                # Безопасно переходим к следующей монете в списке self.options
                logger.info(f" {coin_name } hedgirovanie prossplo uspeshno")
                continue  
            
            
        # Конец главного цикла сканирования портфеля
        return True
    

# no Test  
    def analizCallStrike(self, optionsSellCall: list, nameCoin: str):
        analizCallBool = True
        """
        ЗАЩИТА CALL-НОГИ: Анализирует риски роста рынка выше страйка.
        """
        # Если при роллировании на аккаунте временно нет 
        # CALL-опционов — выходим
        if not optionsSellCall:
            return

        # Нам нужен минимальный страйк (ближайший рубеж обороны)
        # Мы его уже умеем искать без жестких индексов
        call_strike = float('inf')
        total_call_size = 0.0
        for call_opt in optionsSellCall:
            call_strike = min(call_strike, float(call_opt.get('strike', float('inf'))))
            total_call_size += float(call_opt.get('size', 0.0))

        ticPrice = self.ticPrice
        open_futures = self.futures.get(nameCoin)

        # --- УСЛОВНЫЙ ОПЕРАТОР: Пробит ли страйк CALL вверх? ---
        if call_strike < ticPrice:
            logger.warning(f"🚨 [CALL RISK] Цена {ticPrice} "
                           f" выше страйка CALL {call_strike}"
                           f" ! Требуется LONG хедж.")
            
            if open_futures:
                delta_OptAndFutu = open_futures['size'] - optionsSellCall['size'] 
                if call_strike < open_futures['openPrice'] < ticPrice:
                    analizCallBool = False
                    return analizCallBool
                    
                elif call_strike < ticPrice < open_futures['openPrice']:
                    logger.error(f" 1. close open futuers {open_futures}"
                                 f" open new Futures po luchey price")
                    analizCallBool = False
                    return analizCallBool
                
                else: 
                    logger.error(f"1 ne validnie danie"
                                 f"2 ne ponythnaya problema")                
                
            
            # Сценарий А: Фьючерса на аккаунте нет совсем — ОТКРЫВАЕМ С НУЛЯ
            elif open_futures is None:
                logger.error(f"➕ Открываем НОВЫЙ фьючерс BUY на"
                             f" объем {total_call_size}")
                # [Вызов ордера на покупку всего объема total_call_size]
                
            # Сценарий Б: Фьючерс уже есть — сравниваем объемы
            else:
                fut_size = float(open_futures.get('size', 0.0))
                fut_side = open_futures.get('side', '').lower()
                
                # Если фьючерс стоит в BUY, проверяем дельту (хватает ли объема?)
                if fut_side == 'buy':
                    delta = total_call_size - fut_size
                    if delta > 0:
                        logger.warning(f"⚡ Нехватка хеджа! Докупаем фьючерс BUY на объем: {delta}")
                        # [Вызов ордера на дозакупку дельты]
                    elif delta < 0:
                        logger.info(f"⚡ Перехедж! Сбрасываем лишний фьючерс SELL на объем: {abs(delta)}")
                        # [Вызов ордера на частичное закрытие излишка]

    
    
#  notest   
    def analizCoridorStrikes(self, 
                             optinsList: list,
                             nameCoin: str):
        '''
        1. proveryaem o nalichie ticPrice v coridore
        esli TRUE . proveryem futures esli OPEN futures close zacrivem TRUE and TRUE
        2. proveryem o nalichie 
        
        '''
        optionsSellPut = []
        optionsSellCall = [] 
        dictPutSellAnaliz = {}
        open_futures = self.futures.get(nameCoin)
        ticPrice = float(input(f"input tic price coin {nameCoin} :")) 
        
        for option in optinsList:
            asset = OptionAsset(raw_symbol=option["symbol"], 
                                exchange_instance=self.exchange)
            if option.get('buyOrSell', '').lower() == 'sell':
                asset_type = asset.type.upper().strip()
                
                # Исправлено: безопасное разделение по типам без IndexError
                if "PUT" in asset_type or asset_type.startswith('P'):
                    optionsSellPut.append(option)
                elif "CALL" in asset_type or asset_type.startswith('C'):
                    optionsSellCall.append(option)
        
        dictPutSellAnaliz['optSellCall'] = optionsSellCall
        dictPutSellAnaliz['optSellPut'] = optionsSellPut
        
        # logger.info(f" dictPutSellAnaliz {dictPutSellAnaliz} ")
        # =====================================================================
        # КУСОК 2: ИТЕРАЦИОННЫЙ РАСЧЕТ ГРАНИЦ КОРРИДОРА (ЗАЩИТА РОЛЛИРОВАНИЯ)
        # =====================================================================
        
        # Находим МАКСИМАЛЬНЫЙ страйк среди проданных PUT (нижняя граница риска)
        # Если при роллировании список пуст — put_strike останется 0.0 (код не упадет)
        put_strike = 0.0
        for put_opt in optionsSellPut:
            put_strike = max(put_strike, float(put_opt.get('strike', 0.0)))
            
        # Находим МИНИМАЛЬНЫЙ страйк среди проданных CALL (верхняя граница риска)
        # Если при роллировании список пуст — call_strike останется бесконечностью
        call_strike = float('inf')
        for call_opt in optionsSellCall:
            call_strike = min(call_strike, float(call_opt.get('strike', float('inf'))))
        logger.info(f" put_strike {put_strike}"
                    f" call_strike {call_strike}")   
        
        # Возвращаем верхнюю заглушку в безопасное числовое состояние
        if call_strike == float('inf'):
            call_strike = 999999.0
        
        if optionsSellPut[0]['strike'] == optionsSellCall[0]['strike']:
            dictPutSellAnaliz['analizeBool'] = True
            logger.info(f"optionsSellPut['strike'] == optionsSellCall['strike']")
            return dictPutSellAnaliz
        
        
        elif (optionsSellPut[0]['strike'] < open_futures['openPrice']
              < optionsSellCall[0]['strike']):
            logger.info(f"optionsSellPut['strike'] < open_futures['openPrice'] < optionsSellCall['strike']")
            logger.warning(f"close fuctures")
            dictPutSellAnaliz['analizeBool'] = True
            return dictPutSellAnaliz
        
        # =====================================================================
        # КУСОК 3: МАТЕМАТИЧЕСКИЕ СЦЕНАРИИ С ПРАВИЛЬНЫМИ ФЛАГАМИ ТРЕВОГИ
        # =====================================================================

        # Сценарий 1: Страйки совпали (Straddle)
        # Если страйки схлопнулись — коридора нет, это постоянная зона контроля
        if optionsSellPut and optionsSellCall and put_strike == call_strike:
            dictPutSellAnaliz['analizeBool'] = True # ТРЕВОГА/КОНТРОЛЬ: Передаем на защиту ног
            logger.info(f"📊 [Straddle] Страйки PUT и CALL совпали для {nameCoin}: {put_strike}")
            return dictPutSellAnaliz
        
        # Сценарий 2: Цена входа открытого фьючерса находится внутри коридора
        if open_futures:
            fut_open_price = float(open_futures.get('openPrice', 0.0))
            if put_strike < fut_open_price < call_strike:
                logger.info(f"✅ Цена входа фьючерса {fut_open_price} вернулась внутрь коридора ({put_strike} < {fut_open_price} < {call_strike})")
                logger.warning(f"🛑 [СИГНАЛ] Лишний фьючерс по {nameCoin} нужно ЗАКРЫТЬ!")
                dictPutSellAnaliz['analizeBool'] = False # БЕЗОПАСНОСТЬ: Активная защита ног НЕ нужна
                return dictPutSellAnaliz
        
        # Сценарий 3: Текущий рыночный тик находится строго внутри безопасного диапазона
        if put_strike < ticPrice < call_strike:
            logger.info(f"🟢 Текущий тик {ticPrice} находится внутри безопасного коридора ({put_strike} - {call_strike})")
            dictPutSellAnaliz['analizeBool'] = False # БЕЗОПАСНОСТЬ: Рынок в норме, защищать не надо
            return dictPutSellAnaliz            
            
        # Сценарий 4: Каскадный вылет цены за пределы страйков (Зона риска)
        else:
            display_put = put_strike if optionsSellPut else "МИН"
            display_call = call_strike if optionsSellCall else "МАКС"
            
            logger.warning(f"⚠️ Цена {ticPrice} за пределами зоны безопасности ({display_put} - {display_call})!")
            dictPutSellAnaliz['analizeBool'] = True # ТРЕВОГА: Коридор пробит! Включаем защиту CALL/PUT!
            return dictPutSellAnaliz
  
    
    
    def is_futures_data_valid(self, futures_dict) -> bool:
        # Шаг 1: Проверка внешней коробки (Аналогично опционам)
        if futures_dict is None:
            logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА: Данные self.futures равны None!")
            return False

        if not isinstance(futures_dict, dict):
            logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: Нарушен тип self.futures!")
            return False

        # Шаг 2: Внутренний аудит полей (Таможня для каждого открытого фьючерса)
        # Создаем список для сброса сломанных монет, чтобы не индусить
        corrupted_coins = []
        
        for coin_name, fut_info in futures_dict.items():
            # Извлекаем внутренние параметры фьючерса БЕЗ подмен (дефолт None)
            raw_size  = fut_info.get('size', None)
            raw_side  = fut_info.get('side', None)
            raw_price = fut_info.get('openPrice', None)

            # УСЛОВНЫЙ ОПЕРАТОР: Проверка внутренностей на None
            if raw_size is None or raw_side is None or raw_price is None:
                logger.error(f"❌ [ФЬЮЧЕРС БРАК] У монеты {coin_name} поля содержат None!")
                corrupted_coins.append(coin_name)

        # Шаг 3: Очистка. Выжигаем только сломанные монеты, а здоровые оставляем в работе
        for bad_coin in corrupted_coins:
            del futures_dict[bad_coin]
        return True
    
    
    def is_options_data_valid(self, options_dict) -> bool:
        """
        ВАЛИДАТОР ОПЦИОНОВ: Проверяет целостность внешней структуры портфеля.
        Защищает главный диспетчер от критического падения при итерации.
        """
        # 1. Защита от полного отсутствия ответа (Сбой сети / таймаут API Bybit)
        if options_dict is None:
            logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА: Данные self.options равны None! Робот ослеп.")
            return False

        # 2. Защита структуры (Гарантируем, что это dict, а не сломанная строка/список)
        if not isinstance(options_dict, dict):
            logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: Структура self.options сломана! Ожидался dict, пришел {type(options_dict)}.")
            return False

        # Если коробка данных цела — возвращаем True (даже если портфель пустой {})
        return True
   
        

if __name__ == "__main__":
    pusto = TestClass(
                      futures=open_futures2,
                      options=open_options2
                  )
    hending = pusto.process_hedging_logic2()  
        
    
    print("hello bro")  
    































