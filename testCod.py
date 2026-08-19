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
                 ticPrice: float,
                 futures: dict,
                 options: list):
                        # 1. Формируем единую конфигурацию
        botBybit=BybitOptionBot()
        
        # 2. Инициализируем подключение
        # Используем pro-версию ccxt (опционально, но рекомендуется для стабильности)
        self.exchange = botBybit
        self.futures = futures # open_futures2 # botBybit.get_active_futures_positions()
        self.options = options # botBybit.get_active_open_options3() 
        self.ticPrice = ticPrice
        self.ddh_coins = ['SOL', 'DOGE']
        self.listData = listData
    
    def process_hedging_logic2(self) -> bool:
        """
        ГЛАВНЫЙ ДИСПЕТЧЕР (Версия 2): Проверяет данные, итерирует портфель по монетам
        и изолирует ошибки через try/except.
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
                
                # [Сюда стыкуется Кусок 3: вызов analizCoridorStrikes и запуск CALL/PUT веток]
                
            except Exception as coin_error:
                # Если на XRP произойдет технический или сетевой сбой — робот не упадет
                logger.error(f"💥 Критический сбой при обработке монеты {coin_upper}: {coin_error}")
                
                # Безопасно переходим к следующей монете в списке self.options
                continue  
            
                
        # Конец главного цикла сканирования портфеля
        return True
    

# no Test  
    def analizCallStrike(self, optionsSellCall: list, nameCoin: str):
        """
        ЗАЩИТА CALL-НОГИ: Анализирует риски роста рынка выше страйка.
        """
        # Если при роллировании на аккаунте временно нет CALL-опционов — выходим
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
        if ticPrice > call_strike:
            logger.warning(f"🚨 [CALL RISK] Цена {ticPrice} выше страйка CALL {call_strike}! Требуется LONG хедж.")
            
            # Сценарий А: Фьючерса на аккаунте нет совсем — ОТКРЫВАЕМ С НУЛЯ
            if open_futures is None:
                logger.error(f"➕ Открываем НОВЫЙ фьючерс BUY на объем {total_call_size}")
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
        ticPrice = self.ticPrice
        
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
            
        # Возвращаем верхнюю заглушку в безопасное числовое состояние
        if call_strike == float('inf'):
            call_strike = 999999.0
        
        if optionsSellPut['strike'] == optionsSellCall['strike']:
            dictPutSellAnaliz['analizeBool'] = True
            logger.info(f"optionsSellPut['strike'] == optionsSellCall['strike']")
            return dictPutSellAnaliz
        
        elif optionsSellPut['strike'] < open_futures['open_price'] < optionsSellCall['strike']:
            logger.info(f"optionsSellPut['strike'] < open_futures['open_price'] < optionsSellCall['strike']")
            logger.warning(f"close fuchers")
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
    pusto = TestClass(ticPrice=76.8,
                      futures=open_futures2,
                      options=open_options2
                  )
    hending = pusto.process_hedging_logic2()  
        
    
    print("hello bro")  
    





































    # def process_hedging_logic(self, buffer_pct: float = 0.005) -> bool:
    #     """
    #     Автоматическое дельта-хеджирование проданных опционов.
    #     Код полностью линеаризован (убраны спагетти-вложения) и защищен от ошибок строк.
    #     """
    #     logger.info(f"⏳ Запуск фонового сканирования рисков портфеля. Буфер защиты: {buffer_pct * 100}%")
        
    #     # Получаем актуальные данные из состояния класса
    #     open_options = self.options
    #     open_futures = self.futures
        
    #     if not open_options:
    #         logger.info("ℹ️ На аккаунте нет открытых опционов. Хеджирование не требуется.")
    #         return True

    #     for option_position in open_options:
    #         # Шаг 1: Работаем только с проданными опционами (Short / Sell)
    #         if option_position.get("buyOrSell") != 'sell':
    #             continue

    #         # Инициализируем универсальный объект метаданных и запрашиваем цену
    #         asset = OptionAsset(raw_symbol=option_position["symbol"], exchange_instance=self.exchange)
            
    #                     # === ВАРИАНТ Б: ИЗОЛЯЦИЯ МОНЕТ ПОД УПРАВЛЕНИЕМ ВСТРОЕННОГО DDH BYBIT ===
    #         # Список монет, на которых в приложении Bybit у тебя физически включен тумблер DDH
    #         coins_with_active_ddh = ['SOL', 'DOGE']
            
    #         if asset.coin.upper() in coins_with_active_ddh:
    #             logger.info(
    #                 f"ℹ️ Монета {asset.coin.upper()} находится под защитой встроенного DDH Bybit. "
    #                 f"Скрипт передает управление бирже. Пропуск."
    #             )
    #             continue # Робот не будет запрашивать цену и слать ордера по SOL/DOGE, исключая ошибку position mode!

    #         # Запрашиваем цену только для тех монет, которые ведем сами (XRP, BTC и т.д.)
    #         current_spot_price = BybitOptionBot().get_ticker_by_symbol(asset.futures_symbol)

    #         # ЗАЩИТА: Если биржа вернула None вместо цены, бот безопасно идет дальше, а не падает
    #         if current_spot_price is None: # is obratniy uslovniy operator !=
    #             logger.error(f"❌ Пропуск актива {asset.coin}: Текущая цена равна None!")
    #             continue

    #         qty_option = option_position["size"]
    #         asset_type_clean = asset.type.upper().strip()

    #         # БЕЗОПАСНАЯ ПРОВЕРКА СТРОК: .startswith() исключает ошибку IndexError, если строка пустая
    #         is_call_option = "CALL" in asset_type_clean or asset_type_clean.startswith("C")
    #         is_put_option = "PUT" in asset_type_clean or asset_type_clean.startswith("P")

    #         # Шаг 2: Проверка зоны безопасности (Guard Clauses)
    #         # Для CALL безопасность — когда спот снизу страйка. Для PUT — когда спот сверху страйка.
    #         if is_call_option and current_spot_price <= asset.strike:
    #             logger.info(f"🟢 Опцион {asset.coin} CALL {asset.strike} вне опасности. Спот: {current_spot_price}")
    #             continue
                
    #         if is_put_option and current_spot_price >= asset.strike:
    #             logger.info(f"🟢 Опцион {asset.coin} PUT {asset.strike} вне опасности. Спот: {current_spot_price}")
    #             continue

    #         # Шаг 3: Если код дошел сюда — страйк пробит! Мы в КРИТИЧЕСКОЙ ЗОНЕ
    #         logger.warning(f"🚨 КРИТИЧЕСКАЯ ЗОНА: Спот {current_spot_price} пробил страйк {asset.type} {asset.strike}!")

    #         # Настраиваем параметры торговой команды под конкретную ногу опциона
    #         if is_call_option:
    #             required_futures_side = 'buy'   # Рост рынка: нужен фьючерс в LONG
    #             bybit_position_index = 1        # Маркер Long-позиции для Hedge Mode на Bybit
    #         elif is_put_option:
    #             required_futures_side = 'sell'  # Падение рынка: нужен фьючерс в SHORT
    #             bybit_position_index = 2        # Маркер Short-позиции для Hedge Mode на Bybit
    #         else:
    #             logger.error(f"❌ Неизвестный тип опциона: {asset.type}. Пропуск.")
    #             continue

    #         # Шаг 4: Сценарий, когда фьючерса на аккаунте нет вообще
    #         if asset.coin not in open_futures:
    #             logger.error(f"❌ Защиты нет! Открываем НОВЫЙ фьючерс {required_futures_side.upper()} на полный объем {qty_option}")
                
    #             order_result = BybitOptionBot.place_futures_hedge_order(
    #                 base_currency=asset.coin, 
    #                 side=required_futures_side, 
    #                 qty=qty_option, 
    #                 positionIdx=bybit_position_index # Передаем 1 или 2, чтобы Bybit не ругался на режим хеджирования
    #             )
    #             logger.warning(f"🚀 Выставлен стартовый ордер хеджа: {order_result}")
    #             continue

    #         # Шаг 5: Анализ существующего фьючерса (если он есть в open_futures)
    #         futures_position_info = open_futures[asset.coin]
    #         qty_futures = futures_position_info['size']
    #         current_futures_side = futures_position_info['side'].lower()

    #         # Проверяем направление. Если под пробитый Call висит Short фьючерс — это аномалия портфеля
    #         if current_futures_side != required_futures_side:
    #             logger.error(f"❌ Конфликт! Фьючерс по {asset.coin} стоит в {current_futures_side.upper()}, а нужен {required_futures_side.upper()}!")
    #             continue

    #         # Если объемы идеально совпадают 1-к-1 — мы в дельта-нейтральности, ничего не делаем
    #         if qty_option == qty_futures:
    #             logger.info(f"✅ Идеальный хедж 1-к-1 для {asset.coin}. Объемы совпадают.")
    #             continue

    #         # Шаг 6: Динамическое регулирование объема (Докупить / Сбросить лишнее)
    #         delta_size = qty_option - qty_futures

    #         if delta_size > 0:
    #             # Фьючерса мало -> Наращиваем позицию в ту же сторону, куда открыт хедж
    #             trade_action_side = required_futures_side
    #             action_description = "наращивание (добор объема)"
    #         else:
    #             # Перехедж -> Нужно сбросить лишнее встречным ордером (для BUY шлем sell, для SELL шлем buy)
    #             trade_action_side = 'sell' if required_futures_side == 'buy' else 'buy'
    #             action_description = "снижение (частичная фиксация излишка)"

    #         # Отправляем точный корректирующий ордер на Bybit
    #         order_result = BybitOptionBot.place_futures_hedge_order(
    #             base_currency=asset.coin,
    #             side=trade_action_side,
    #             qty=abs(delta_size), # abs() гарантирует, что Bybit API получит только положительный объем
    #             positionIdx=bybit_position_index # Передаем правильную сторону позиции для Bybit Hedge Mode
    #         )
    #         logger.warning(f"⚡ Выполнено {action_description} хеджа: {order_result}")

    #     return True
    
    
   
    # МОЙ ПЕРВИЧНЫЙ ВАРИАНТ 
    # def process_hedging_logic(self, buffer_pct: float = 0.005) -> bool:
    #     # nuzno sdelat provercu na nalichie otcritogo fuchersa
    #     # i size chtob ponimat skolko docupat fuchrsa
    #     # esli fuchers otcrit i on zashishaet position to continue
    #     # esli zashls za stryke i no fuchers zashishaem position
        
    #     """
    #     Шаги 10, 12, 13 плана: Автоматическое дельта-хеджирование проданных опционов.
    #     Полностью обновлено с использованием универсального ядра OptionAsset.
        
    #     :param buffer_pct: Зазор безопасности в долях (0.005 = 0.5%) для защиты от шума на страйке.
    #     :return: True если цикл проверок прошел успешно, False при критической ошибке.
        
    #     list_coin = ["btc", "eth", "xrp", "sol", "doge"]
 
    #     """
    #     dictOptions = {}
        
    #     logger.info(f"⏳ Запуск фонового сканирования рисков портфеля. Буфер защиты: {buffer_pct * 100}%")
        
    #     # Шаг 9: Получаем список всех живых открытых опционов с реального баланса Bybit
    #     # Этот метод уже возвращает базово отфильтрованные опционы портфеля
    #     listOptions = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE']
    #     # open_options = self.get_active_open_options3()
    #     # open_fuctures = self.get_active_futures_positions() #true data
    #     open_options = self.options
    #     open_futures = self.futures
        
    #     print("="*33)
    #     logger.info(f"open_options {self.options}")
    #     print("="*33)
    #     logger.info(f"open_futures {open_futures}")
    #     print("="*33)
        
    #     if not open_options:
    #         logger.info("ℹ️ На аккаунте нет открытых опционов. Хеджирование не требуется.")
    #         return True

    #     for opt in open_options:
    #         # Вытаскиваем исходную сырую строку позиции (напр: XRPUSDT-Options-4AUG26-1.1-C)
    #         raw_symbol = opt["symbol"] 
    #         buy_or_sell = opt["buyOrSell"]
    #         qty_option = opt["size"] # Объем позиции (всегда положительный float, благодаря abs())

    #         # Хеджируем ТОЛЬКО проданные (Short / SELL) крылья, так как их риск неограничен!
    #         if buy_or_sell != 'sell':
    #             continue

    #         # === СТЫКОВКА С METHOD_SYMBOLS: Мгновенно получаем объект со всеми метаданными ===
    #         # Нам больше не нужно резать строки дефисами внутри этой функции!
    #         asset = OptionAsset(raw_symbol=raw_symbol, exchange_instance=self.exchange)

    #         # --- ШАГ 10: ЗАПРАС ТЕКУЩЕГО СПОТА (ticPrice) ДЛЯ ЭТОЙ МОНЕТЫ ---
    #         # Запрашиваем цену базового фьючерса, имя которого (напр. 'XRP/USDT:USDT')
    #         # объект уже знает
            
            
            
    #         current_spot_price = BybitOptionBot().get_ticker_by_symbol(asset.futures_symbol)


    #         logger.info(f" asset.coin, asset.type, asset.strike"
    #                     f"{asset.coin, asset.type, asset.strike}")
    #         # === АНАЛИЗ ДЛЯ ПРОДАННОГО ОПЦИОНА CALL (Защита от пампа/роста рынка) ===
    #         qty_futures = open_futures[asset.coin]['size']
            
    #         # === АНАЛИЗ ДЛЯ ПРОДАННОГО ОПЦИОНА CALL (Защита от пампа/роста рынка) ===
    #         if asset.type[0].upper() == 'C':
                
    #             # Проверяем, вышла ли цена спота выше страйка (зона убытка для Call Sell)
    #             if current_spot_price > asset.strike:
    #                 logger.warning(
    #                     f"🚨 КРИТИЧЕСКАЯ ЗОНА: Спот {current_spot_price}" 
    #                     f" пробил страйк Call {asset.strike}! "
    #                     f" Включаем экстренный Long-хедж фьючерсом."
    #                 )
                    
    #                 # ШАГ 1: Проверяем, открыт ли вообще какой-либо фьючерс по этой монете
    #                 if asset.coin in open_futures:
                        
    #                     # Безопасно вытаскиваем объем фьючерса (теперь ошибка KeyError исключена)
    #                     qty_futures = open_futures[asset.coin]['size']
                        
    #                     # ШАГ 2: Проверяем направление фьючерса. Для защиты CALL нам нужен только BUY (Long)
    #                     if open_futures[asset.coin]['side'].lower() == 'buy':
    #                         logger.info(f" фьючерс уже открыт: {open_futures[asset.coin]} ")
                            
    #                         # ШАГ 3: Сравниваем размеры позиций опциона и фьючерса
    #                         if qty_option != qty_futures:
                                
    #                             # Считаем математическую разницу объемов
    #                             deltaSizeFutureOption = qty_option - qty_futures
                                
    #                             # Сценарий А: Опцион больше фьючерса (Хеджа не хватает) -> ДОКУПАЕМ фьючерс
    #                             if deltaSizeFutureOption > 0:
    #                                 orderBuyFutu = BybitOptionBot.place_futures_hedge_order(
    #                                     base_currency=asset.coin, 
    #                                     side='buy', # Сигнал на покупку
    #                                     qty=deltaSizeFutureOption # Докупаем только нехватку
    #                                 )
    #                                 logger.warning(f"докупка фучерса {orderBuyFutu}")
                                
    #                             # Сценарий Б: Фьючерса больше чем нужно (Перехедж) -> ПРОДАЕМ лишний объем
    #                             elif deltaSizeFutureOption < 0:
    #                                 orderBuyFutu = BybitOptionBot.place_futures_hedge_order(
    #                                     base_currency=asset.coin, 
    #                                     side='sell', # Сигнал на продажу лишнего
    #                                     qty=abs(deltaSizeFutureOption) # abs() убирает минус, чтобы Bybit не выдал ошибку
    #                                 )
    #                                 logger.warning(f"продажа фучерса {orderBuyFutu}")  
                                 
    #                         # Сценарий В: Объемы идеально равны
    #                         elif qty_option == qty_futures: 
    #                             logger.info(f"✅ Идеальный хедж 1-к-1 для {asset.coin}.")
    #                             continue
                        
    #                     # Сработает, если фьючерс по монете есть, но он стоит в SHORT (ошибка стратегии)
    #                     else:
    #                         logger.error(
    #                             f"❌ Конфликт позиций! Фьючерс по {asset.coin} "
    #                             f"открыт в SELL, а для CALL нужен BUY!"
    #                         )
                    
    #                 # Сработает, если фьючерса по этой монете на аккаунте нет вообще
    #                 else:
    #                     logger.error(
    #                         f"❌ Защиты нет! Фьючерс по {asset.coin} отсутствует. "
    #                         f"Открываем НОВЫЙ long futures на полный объем {qty_option}"
    #                     )
    #                     # orderBuyFutu = BybitOptionBot.place_futures_hedge_order(base_currency=asset.coin, side='buy', qty=qty_option)
                
    #             # Спот ниже страйка — позиция приносит прибыль, делать ничего не нужно
    #             else:
    #                 logger.info(
    #                     f"🟢 Опцион {asset.coin} Call {asset.strike} вне опасности. "
    #                     f"Спот: {current_spot_price} (Порог защиты: {round(asset.strike, 4)})"
    #                 )


    #         # === АНАЛИЗ ДЛЯ ПРОДАННОГО ОПЦИОНА PUT (Защита от дампа/падения рынка) ===
    #         elif asset.type[0].upper() == 'P':
    #             # Если цена спота рухнула ниже страйка - буфер
    #             logger.info(f"PUT current_spot_price < (asset.strike + buffer_amount):"
    #                         f"{current_spot_price} < {asset.strike}")
    #             if current_spot_price < (asset.strike ):
    #                 logger.warning(
    #                     f"🚨 КРИТИЧЕСКАЯ ЗОНА: Спот {current_spot_price}"
    #                     f" упал ниже страйка Put {asset.strike}! "
    #                     f"Включаем экстренный Short-хедж фьючерсом."
    #                 )
    #                 # Шаг 11: Открываем Short-фьючерс
    #                 # self.place_futures_hedge_order(base_currency=asset.coin, side='sell', qty=qty)
    #                 logger.warning(f"open short futures")
    #             else:
    #                 logger.info(
    #                     f"🟢 Опцион {asset.coin} Put {asset.strike} вне опасности. "
    #                     f"Спот: {current_spot_price} (Порог защиты: {round(asset.strike, 4)})"
    #                 )
                    
    #     return True
    