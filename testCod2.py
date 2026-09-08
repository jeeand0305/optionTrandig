import sys
import os
import numpy as np

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
import time

# Дальше ваши тестовые данные (open_futures1, open_options1 и т.д.)


open_futures1 = {'SOL': {'symbol': 'SOL/USDT:USDT', 'side': 'buy', 'size': 1.5, 'openPrice': 75.37941176, 'leverage': 10.0, 'initMargin': 11.5034122}, 'NEAR': {'symbol': 'NEAR/USDT:USDT', 'side': 'buy', 'size': 12.0, 'openPrice': 1.616, 'leverage': 1.0, 'initMargin': 19.5228}}
open_options1 = [{'symbol': 'SOL/USDT:USDT-260814-75-C', 'ccxt_symbol': 'SOL/USDT:USDT-260814-75-C', 'buyOrSell': 'sell', 'size': 3.0, 'entry_price': 0.94, 'hours_to_expiration': 132.35, 'strike': 75.0, 'type': 'CALL', 'futures_symbol': 'SOL/USDT:USDT', 'initMargin': 40.12063646}, {'symbol': 'SOL/USDT:USDT-260814-73-P', 'ccxt_symbol': 'SOL/USDT:USDT-260814-73-P', 'buyOrSell': 'sell', 'size': 3.0, 'entry_price': 1.0, 'hours_to_expiration': 132.35, 'strike': 73.0, 'type': 'PUT', 'futures_symbol': 'SOL/USDT:USDT', 'initMargin': 28.11017423}]

invers_open_options2 = ({'SOL': [{'symbol': 'SOL/USDT:USDT-260828-78-P', 'ccxt_symbol': 'SOL/USDT:USDT-260828-78-P', 
                'buyOrSell': 'sell', 'size': 4.0, 'entry_price': 1.33, 'hours_to_expiration': 217.03,
                'strike': 78.0, 'type': 'PUT', 'futures_symbol': 'SOL/USDT:USDT', 'initMargin': 48.10864144},
                {'symbol': 'SOL/USDT:USDT-260821-74-C', 'ccxt_symbol': 'SOL/USDT:USDT-260821-74-C',
                 'buyOrSell': 'sell', 'size': 4.0, 'entry_price': 0.87, 'hours_to_expiration': 49.03, 
                 'strike': 74.0, 'type': 'CALL', 'futures_symbol': 'SOL/USDT:USDT', 'initMargin': 37.41257572}], 
                  'XRP': [{'symbol': 'XRP/USDT:USDT-260820-1-C', 'ccxt_symbol': 'XRP/USDT:USDT-260820-1-C', 
                'buyOrSell': 'sell', 'size': 20.0, 'entry_price': 0.0071, 'hours_to_expiration': 25.03,
                'strike': 1.0, 'type': 'CALL', 'futures_symbol': 'XRP/USDT:USDT', 'initMargin': 4.2830806}, 
                {'symbol': 'XRP/USDT:USDT-260820-0.98-P', 'ccxt_symbol': 'XRP/USDT:USDT-260820-0.98-P', 
                 'buyOrSell': 'sell', 'size': 20.0, 'entry_price': 0.0032, 'hours_to_expiration': 25.03, 
                 'strike': 0.98, 'type': 'PUT', 'futures_symbol': 'XRP/USDT:USDT', 'initMargin': 3.5989536}]})

open_options2 = ({'SOL': [{'symbol': 'SOL/USDT:USDT-260828-78-C', 'ccxt_symbol': 'SOL/USDT:USDT-260828-78-C', 
                'buyOrSell': 'sell', 'size': 4.0, 'entry_price': 1.33, 'hours_to_expiration': 217.03,
                'strike': 78.0, 'type': 'CALL', 'futures_symbol': 'SOL/USDT:USDT', 'initMargin': 48.10864144},
                {'symbol': 'SOL/USDT:USDT-260821-74-P', 'ccxt_symbol': 'SOL/USDT:USDT-260821-74-P',
                 'buyOrSell': 'sell', 'size': 4.0, 'entry_price': 0.87, 'hours_to_expiration': 49.03, 
                 'strike': 74.0, 'type': 'PUT', 'futures_symbol': 'SOL/USDT:USDT', 'initMargin': 37.41257572}], 
                  'XRP': [{'symbol': 'XRP/USDT:USDT-260820-1-C', 'ccxt_symbol': 'XRP/USDT:USDT-260820-1-C', 
                'buyOrSell': 'buy', 'size': 20.0, 'entry_price': 0.0071, 'hours_to_expiration': 25.03,
                'strike': 1.0, 'type': 'CALL', 'futures_symbol': 'XRP/USDT:USDT', 'initMargin': 4.2830806}, 
                {'symbol': 'XRP/USDT:USDT-260820-0.98-P', 'ccxt_symbol': 'XRP/USDT:USDT-260820-0.98-P', 
                 'buyOrSell': 'sell', 'size': 20.0, 'entry_price': 0.0032, 'hours_to_expiration': 25.03, 
                 'strike': 0.98, 'type': 'PUT', 'futures_symbol': 'XRP/USDT:USDT', 'initMargin': 3.5989536}]})

invertor_open_futures2 = ({'XRP': {'symbol': 'XRP/USDT:USDT', 'side': 'sell', 'size': 10.0, 'openPrice': 1.0229, 
                          'leverage': 10.0, 'initMargin': 1.0340519},
                  'NEAR': {'symbol': 'NEAR/USDT:USDT', 'side': 'buy', 'size': 12.0, 'openPrice': 1.616, 
                           'leverage': 1.0, 'initMargin': 19.4064},
                  'SOL': {'symbol': 'SOL/USDT:USDT', 'side': 'buy', 'size': 1.25, 'openPrice': 78, 
                        'leverage': 10.0, 'initMargin': 11.49544031}})

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
        self.ddh_coins = ['DOGE', 'SOL']
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
                # time.sleep(5)
                # ШАГ 1: Агрегируем данные (создаем coin_data один раз)
                coin_data = self.aggregate_coin_data(
                    optinsList=options_list, nameCoin=coin_upper)
            
                # logger.info(f" coin-data {coin_data}")
                # === ТВОЯ ИДЕЯ: Проверка условного оператора НА ВЕРХНЕМ УРОВНЕ ===
                # Диспетчер сам видит, вывернут ли коридор
                if (coin_data['put_strike'] is not None 
                    and coin_data['call_strike'] is not None):   
                    if coin_data['put_strike'] > coin_data['call_strike']:
                    # Запускаем инверсию ТОЛЬКО если проблема РЕАЛЬНО высветилась!
                        self.analiz_inverted_corridor(coin_data)

                        logger.warning(f"🚨 Форс-мажор по {coin_upper} обработан перехватчиком. Ранний выход.")
                        continue # Мгновенно переходим к следующей монете, штатный код заблокирован

                # -----------------------------------------------------------------
                # ШАГ 3: ШТАТНЫЙ РЕЖИМ (Сюда бот дойдет, только если инверсии НЕТ)
                # -----------------------------------------------------------------
                    if coin_data['put_strike'] <= coin_data['call_strike']:
                        coridor_result = self.analizCoridorStrikes2(coin_data)
                        logger.info(f" coridor_result {coridor_result}")
                        
                        if coridor_result['analizeBool'] == False:
                            continue
                        
                    if coin_data['call_strike'] <= coin_data['ticPrice']:
                        call_result = self.analizCallStrike(coin_data)
                        logger.info(f"call_result {call_result}")
                        
                        if call_result['analizeBool'] == False:
                            logger.info(f"✅ {coin_upper} хеджирование прошло успешно")
                            continue
                        
                    if coin_data['put_strike'] >= coin_data['ticPrice']:
                        self.analizPutStrike(coin_data)
                        logger.info(f"✅ {coin_upper} хеджирование прошло успешно")
                        continue                    
                
                # если всего один продоный страйк КОЛ или ПУТ
                elif (coin_data['put_strike'] == None 
                    or coin_data['call_strike'] == None): 

                    if (coin_data['call_strike'] != None 
                        and coin_data['call_strike'] <= coin_data['ticPrice']):
                        call_result = self.analizCallStrike(coin_data)
                        logger.info(f"call_result {call_result}")
                        
                        if call_result['analizeBool'] == False:
                            logger.info(f"✅ {coin_upper} хеджирование прошло успешно")
                            continue
                        
                    if (coin_data['put_strike'] != None 
                        and coin_data['put_strike'] >= coin_data['ticPrice']):
                        self.analizPutStrike(coin_data)
                        logger.info(f"✅ {coin_upper} хеджирование прошло успешно")
                        continue   
                                
            except Exception as coin_error:
                # Если на XRP произойдет технический или сетевой сбой — робот не упадет
                logger.error(f"💥 Критический сбой при обработке монеты {coin_upper}: {coin_error}")
                
                # Безопасно переходим к следующей монете в списке self.options
                logger.info(f" {coin_name } hedgirovanie prossplo uspeshno")
                continue  
            
            
        # Конец главного цикла сканирования портфеля
        return True
    

    def execute_hedge_adjustment(self, nameCoin: str, target_side: str, delta: float):
        """
        УНИВЕРСАЛЬНЫЙ ИСПОЛНИТЕЛЬ ОРДЕРОВ (Шаг 11 плана):
        Принимает монету, целевую сторону защиты (buy/sell) и рассчитанную дельту объемов.
        Самостоятельно принимает решение: добрать позицию или частично сократить излишек.
        """
        # Округляем дельту до 4 знаков (защита от биржевого микро-мусора в плавающей точке)
        
        logger.info(f" delta {delta}")
        delta = round(delta, 4)
        
        # Если дельта после округления равна нулю — никаких действий на бирже не требуется
        if delta == 0.0:
            return

        # Приводим целевую сторону к нижнему регистру для стандартизации протокола CCXT
        clean_target_side = target_side.lower().strip()

        # --- ВНЕШНИЙ ТЕХНИЧЕСКИЙ ЩИТ ДЛЯ ЗАЩИТЫ ОТ СБОЕВ API БИРЖИ ---
        try:
            # === СЦЕНАРИЙ 1: ДЕЛЬТА ПОЛОЖИТЕЛЬНАЯ (НЕХВАТКА ОБЪЕМА ХЕДЖА) ===
            # Нам необходимо ДОКУПИТЬ фьючерсы в ту же сторону, куда направлен риск
            if delta > 0:
                logger.warning(
                    f"⚡ [ОРДЕР ДОБОРА] Нехватка хэджа по монете {nameCoin}! "
                    f"Отправляем рыночный приказ {clean_target_side.upper()} на объем: {delta}"
                )
                
                # Твой вызов CCXT для отправки рыночного ордера на добор:
                # self.place_market_order(symbol=nameCoin, side=clean_target_side, qty=delta)

            # === СЦЕНАРИЙ 2: ДЕЛЬТА ОТРИЦАТЕЛЬНАЯ (ИЗЛИШЕК / ПЕРЕХЕДЖ) ===
            # Математика зафиксировала лишние фьючерсы. Нам нужно ЧАСТИЧНО СОКРАТИТЬ позицию
            elif delta < 0:
                # Переводим отрицательное значение дельты в чистый модуль объема для ордера
                actual_qty = abs(delta)
                
                # --- УСЛОВНЫЕ ОПЕРАТОРЫ ПЕРЕВОРОТА НАПРАВЛЕНИЯ ДЛЯ ЗАКРЫТИЯ ---
                # Если целевая сторона хэджа LONG (buy), то закрывать излишек нужно ордером SELL
                if clean_target_side == 'buy':
                    order_side = 'sell'
                # Если целевая сторона хэджа SHORT (sell), то закрывать излишек нужно ордером BUY
                elif clean_target_side == 'sell':
                    order_side = 'buy'
                else:
                    logger.error(f"❌ Критическая аномалия направления clean_target_side: {clean_target_side}")
                    return

                logger.info(
                    f"⚡ [ОРДЕР СОКРАЩЕНИЯ] Зафиксирован перехедж по монете {nameCoin}! "
                    f"Отправляем рыночный приказ {order_side.upper()} на частичное закрытие объема: {actual_qty}"
                )
                
                # Твой вызов CCXT для отправки встречного ордера на сокращение:
                # self.place_market_order(symbol=nameCoin, side=order_side, qty=actual_qty)

        except Exception as order_error:
            # Если Bybit отклонит ордер (Rate Limit, Margin Call) — блок except удержит робота на плаву
            logger.error(f"💥 Критический сбой API при исполнении хэдж-ордера по {nameCoin}: {order_error}")


    def analizCallStrike(self, coin_data: dict, midStrike = None):
        """
        ЗАЩИТА CALL-НОГИ (Версия 4.0 — С полным переворотом позиции):
        Анализирует риски пробития рынка вверх выше минимального страйка CALL.
        Если на аккаунте висит враждебный SHORT фьючерс, полностью гасит его в ноль
        и переворачивается в LONG на весь объем проданной сетки CALL.
        """
        dictPutSellAnaliz = {}
        
        # 1. Защитный барьер: если при роллировании CALL-ноги нет на аккаунте — мгновенно выходим
        if not coin_data['optionsSellCall'] or coin_data['call_strike'] is None:
            dictPutSellAnaliz['analizeBool'] = True
            return dictPutSellAnaliz
    
        
        # 2. Мгновенная распаковка готовых чистых данных из агрегатора
        nameCoin        = coin_data['nameCoin']
        call_strike     = coin_data['call_strike']
        total_call_size = coin_data['total_call_size']
        ticPrice        = coin_data['ticPrice']
        open_futures    = coin_data['open_futures']
        
        if midStrike:
            call_strike = midStrike
            logger.info(f" сработол call_strike {call_strike} "
                    f" защита midStrike {midStrike}  обратний инверсионый опцион ")

        # === УСЛОВНЫЙ ОПЕРАТОР: ТРИГГЕР ПРОБИТИЯ СТРАЙКА CALL ВВЕРХ ===
        if ticPrice >= call_strike:
            logger.warning(f"🚨 [ПАНИКА CALL] Цена {ticPrice} выше страйка CALL {call_strike}! Активирован LONG хэдж.")
            
            # Извлекаем текущие параметры открытого фьючерса (actual size)
            fut_size = 0.0
            fut_side = 'none'
            if open_futures:
                fut_size = float(open_futures.get('size', 0.0))
                fut_side = open_futures.get('side', '').lower().strip()
                logger.info(f" fut_side {fut_side}, fut_size {fut_size}")

            # --- УМНЫЙ РАСЧЕТ ДЕЛЬТЫ С УЧЕТОМ НАПРАВЛЕНИЯ ПОЗИЦИИ ---
            if fut_side == 'buy':
                # Стоим в нужную сторону (BUY) — просто добираем нехватку лотов
                delta = total_call_size - fut_size
            elif fut_side == 'sell':
                # Цена летит вверх, а у нас SHORT! Складываем объемы для полного переворота
                delta = total_call_size + fut_size
            else:
                # Фьючерса нет совсем — берем чистый объем CALL-ноги
                delta = total_call_size

            # -----------------------------------------------------------------
            # КАСКАД УСЛОВНЫХ ОПЕРАТОРОВ ИСПОЛНЕНИЯ (Твоя структура)
            # -----------------------------------------------------------------
            
            # БАРЬЕР 1: Если хэдж уже идеально набран и стоит в BUY — мгновенно выходим!
            if total_call_size == fut_size and fut_side == 'buy': 
                logger.debug(f"ℹ️ [CALL] Хэдж по {nameCoin} уже идеально равен риску ({fut_size}).")
                dictPutSellAnaliz['analizeBool'] = False
                return dictPutSellAnaliz
            
            # БАРЬЕР 2: Если есть перекос объемов ИЛИ направления (включая встречный шорт)
            elif total_call_size != fut_size or fut_side != 'buy':            
                logger.info(
                    f"📈 [КОМАНДА CALL] Текущий тик {ticPrice} > CALL Страйка {call_strike}. "
                    f"Целевой хэдж: BUY (LONG) | Цель: {total_call_size} | Дельта переворота/добора: {delta}"
                )

                # Отправляем приказ в наш универсальный исполнитель ордеров
                self.execute_hedge_adjustment(nameCoin=nameCoin, target_side='buy', delta=delta)
                dictPutSellAnaliz['analizeBool'] = False
                return dictPutSellAnaliz 


    def analizPutStrike(self, coin_data: dict, midStrike = None):
        """
        ЗАЩИТА PUT-НОГИ (Версия 4.0 — С полным переворотом позиции):
        Анализирует риски пробития рынка вниз ниже максимального страйка PUT.
        Если на аккаунте висит враждебный LONG фьючерс, полностью гасит его в ноль
        и переворачивается в SHORT на весь объем проданной сетки PUT.
        """
        # 1. Защитный барьер: если при роллировании PUT-ноги нет на аккаунте — мгновенно выходим
        if not coin_data['optionsSellPut'] or coin_data['put_strike'] is None:
            return

        # 2. Мгновенная распаковка готовых чистых данных из агрегатора
        nameCoin       = coin_data['nameCoin']
        put_strike     = coin_data['put_strike']
        total_put_size = coin_data['total_put_size']
        ticPrice       = coin_data['ticPrice']
        open_futures   = coin_data['open_futures']
        
        if midStrike:
            put_strike = midStrike
            logger.info(f" сработол put_strike {put_strike} "
                        f" защита midStrike {midStrike}  обратний инверсионый опцион ")
        # === УСЛОВНЫЙ ОПЕРАТОР: ТРИГГЕР ПРОБИТИЯ СТРАЙКА PUT ВНИЗ ===
        if ticPrice <= put_strike:
            logger.warning(f"🚨 [ПАНИКА PUT] Цена {ticPrice} ниже страйка PUT {put_strike}! Активирован SHORT хэдж.")
            
            # Извлекаем текущие параметры открытого фьючерса (actual size)
            fut_size = 0.0
            fut_side = 'none'
            if open_futures:
                fut_size = float(open_futures.get('size', 0.0))
                fut_side = open_futures.get('side', '').lower().strip()

            # --- УМНЫЙ РАСЧЕТ ДЕЛЬТЫ С УЧЕТОМ НАПРАВЛЕНИЯ ПОЗИЦИИ ---
            if fut_side == 'sell':
                # Стоим в нужную сторону (SELL) — просто добираем нехватку лотов шорта
                delta = total_put_size - fut_size
            elif fut_side == 'buy':
                # Цена падает, а у нас LONG! Складываем объемы для полного переворота
                delta = total_put_size + fut_size
            else:
                # Фьючерса нет совсем — берем чистый объем PUT-ноги
                delta = total_put_size

            # -----------------------------------------------------------------
            # КАСКАД УСЛОВНЫХ ОПЕРАТОРОВ ИСПОЛНЕНИЯ (Твоя структура)
            # -----------------------------------------------------------------
            
            # БАРЬЕР 1: Если хэдж уже идеально набран и стоит в SELL — мгновенно выходим!
            if total_put_size == fut_size and fut_side == 'sell': 
                logger.debug(f"ℹ️ [PUT] Хэдж по {nameCoin} уже идеально равен риску ({fut_size}).")
                
                return 
            
            # БАРЬЕР 2: Если есть перекос объемов ИЛИ направления (включая встречный лонг)
            elif total_put_size != fut_size or fut_side != 'sell':            
                logger.info(
                    f"📉 [КОМАНДА PUT] Текущий тик {ticPrice} < PUT Страйка {put_strike}. "
                    f"Целевой хэдж: SELL (SHORT) | Цель: {total_put_size} | Дельта переворота/добора: {delta}"
                )

                # Отправляем приказ в наш универсальный исполнитель ордеров
                self.execute_hedge_adjustment(nameCoin=nameCoin, target_side='sell', delta=delta)
                return

            
    def analizCoridorStrikes2(self, coin_data: dict) -> dict:
        """
        ШТАТНЫЙ АНАЛИЗ КОРРИДОРА (Версия 3.0 — Стерильная):
        Принимает готовый паспорт coin_data. Рассчитывает стандартные сценарии 
        положения цены и выносит вердикт о необходимости запуска защиты ног.
        """
        dictPutSellAnaliz = {}
        
        # 1. Мгновенная распаковка готовых чистых данных (Ноль циклов for внутри!)
        nameCoin = coin_data['nameCoin']
        optionsSellCall = coin_data['optionsSellCall']
        optionsSellPut = coin_data['optionsSellPut']
        put_strike = coin_data['put_strike']
        call_strike = coin_data['call_strike']
        ticPrice = coin_data['ticPrice']
        open_futures = coin_data['open_futures']

        # =====================================================================
        # МАТЕМАТИЧЕСКИЕ СЦЕНАРИИ СРАВНЕНИЯ (КАСКАДНЫЙ ВОДОПАД УСЛОВИЙ)
        # =====================================================================

        # Сценарий 1: Страйки совпали (Классический Straddle: 1.0 == 1.0)
        # Срабатывает только если в портфеле присутствуют обе ноги одновременно
        if put_strike is not None and call_strike is not None and put_strike == call_strike:
            logger.info(f"📊 [Straddle] Страйки PUT и CALL совпали для {nameCoin}: {put_strike}")
            dictPutSellAnaliz['analizeBool'] = True # ТРЕВОГА: Передаем монету на защиту ног
            return dictPutSellAnaliz
        
        # Сценарий 2: Текущая цена входа открытого фьючерса находится внутри коридора
        # Защита от KeyError: блок выполняется только если фьючерс реально существует

        if open_futures:
            fut_open_price = float(open_futures.get('openPrice', 0.0))
            
            if put_strike < ticPrice < call_strike:
                logger.warning(f" нужно срочно закрыть фючерс {nameCoin}"
                             f" тик цена в коридоре между страками  ")
                dictPutSellAnaliz['analizeBool'] = False   
                return dictPutSellAnaliz
            
            elif ticPrice <= put_strike :
                logger.warning(f" тик цена {ticPrice} вышла из коридора put {put_strike}"
                               f" страйков или равна страйку анализ производим " )             
                dictPutSellAnaliz['analizeBool'] = True
                return dictPutSellAnaliz
                
            elif call_strike <= ticPrice:
                logger.warning(f" тик цена {ticPrice} вышла из коридора call {call_strike}"
                               f" страйков или равна страйку анализ производим " )    
                dictPutSellAnaliz['analizeBool'] = True
                return dictPutSellAnaliz
            
            else:
                logger.error(f" что то отволилось при открытом фюче "
                               f" analizCoridorStrike2")
                dictPutSellAnaliz['analizeBool'] = True
                return dictPutSellAnaliz

        elif  put_strike < ticPrice < call_strike:
            logger.info(f" тик прайсе в коридоре фючерс закрыт "
                        f"{open_futures}")
            dictPutSellAnaliz['analizeBool'] = False
            return dictPutSellAnaliz 
                        
        # Сценарий 4: Каскадный вылет цены за пределы страйков (Зона риска пробития)
        else:
            logger.warning(
                f"⚠️ Цена {ticPrice} ЗА ПРЕДЕЛАМИ зоны безопасности! ")
            dictPutSellAnaliz['analizeBool'] = True # ТРЕВОГА: Коридор пробит! Включаем защиту CALL/PUT веток!
            return dictPutSellAnaliz

   
    def analiz_inverted_corridor(self, coin_data: dict):
        """
        ПЕРЕХВАТЧИК ФОРС-МАЖОРА (Версия 3.0 — Без внутренних циклов):
        Вызывается главным диспетчером только при подтвержденной инверсии страйков.
        Рассчитывает дельту объема относительно средней точки и отправляет приказ
        универсальному исполнителю ордеров.
        """
        # 1. Мгновенная распаковка готовых параметров из паспорта данных coin_data
        # Ноль повторных тяжелых циклов for или регулярных выражений внутри!
        nameCoin        = coin_data['nameCoin']
        put_strike      = coin_data['put_strike']
        call_strike     = coin_data['call_strike']
        ticPrice        = coin_data['ticPrice']
        total_call_size = coin_data['total_call_size']
        total_put_size  = coin_data['total_put_size']
        open_futures    = coin_data['open_futures']

        logger.warning(
            f"⚠️ [АВАРИЙНЫЙ КОНТУР] Активирован перехватчик инверсии по монете {nameCoin}! "
            f"Текущие страйки портфеля перевернуты: PUT ({put_strike}) > CALL ({call_strike})"
        )

        # 2. Вычисляем математическую середину диапазона (Midpoint)
        # В твоем примере: (101 + 99) / 2 = 100
        mid_price = (put_strike + call_strike) / 2

        # 3. Извлекаем актуальные параметры открытого фьючерса (Защитный технический щит)
        fut_size = 0.0
        fut_side = 'none'
        if open_futures:
            fut_size = float(open_futures.get('size', 0.0))
            fut_side = open_futures.get('side', '').lower().strip()

        # =====================================================================
        # КУСОК ВЕТВЛЕНИЯ ОТНОСИТЕЛЬНО СЕРЕДИНЫ И АВТОМАТИЧЕСКОГО РАСЧЕТА ДЕЛЬТЫ
        # =====================================================================
        
        # --- СЦЕНАРИЙ А: ЦЕНА НАХОДИТСЯ НА СЕРЕДИНЕ ИЛИ ВЫШЕ (100+) ---
        if mid_price < ticPrice:
            # if total_put_size == fut_size and fut_side == 'buy':
            logger.info(f"work inversi CALL")
            self.analizCallStrike(coin_data=coin_data, midStrike=mid_price)
            return 
            
            # if total_put_size != fut_size and fut_side != 'buy':            
            #     # Компактный тернарный оператор вычисляет точную дельту с учетом позиции
            #     delta = (total_put_size - fut_size if fut_side == 'buy' 
            #              else total_put_size)

            #     logger.info(
            #         f"📈 [ИНВЕРСИЯ ТРЕНДА] Текущий тик {ticPrice} >= "
            #         f" Середины {mid_price}. "
            #         f"Целевой хэдж: BUY (LONG) | Необходимый объем: "
            #         f" | Рассчитанная дельта ордера: {delta}" )

            #     # Передаем рассчитанную дельту в наш универсальный исполнитель ордеров
            #     self.execute_hedge_adjustment(nameCoin=nameCoin,
            #                                   target_side='buy',
            #                                   delta=delta)
            #     return
            
            
        # --- СЦЕНАРИЙ Б: ЦЕНА УПАЛА НИЖЕ МАТЕМАТИЧЕСКОЙ СЕРЕДИНЫ (<100) ---
        elif ticPrice <= mid_price:
            logger.info(f"work inversi PUT")
            self.analizPutStrike(coin_data=coin_data, midStrike=mid_price)
            return 
        
            # if total_call_size == fut_size and fut_side == 'sell': 
            #     return 
                        
            # elif total_call_size != fut_size and fut_side != 'buy': 
            #     # Целевой объем хэджа должен жестко равняться объему PUT-ноги


            #     # Компактный тернарный оператор вычисляет точную дельту для шорт-позиции
            #     delta = (total_put_size - fut_size if fut_side == 'sell' 
            #              else total_put_size)

            #     logger.info(
            #         f"📉 [ИНВЕРСИЯ ТРЕНДА] Текущий тик {ticPrice} < "
            #         f" Середины {mid_price}. "
            #         f"Целевой хэдж: SELL (SHORT) | Необходимый объем: "
            #         f"  | Рассчитанная дельта ордера: {delta}" )

            #     # Передаем рассчитанную дельту в наш универсальный исполнитель ордеров
            #     self.execute_hedge_adjustment(nameCoin=nameCoin, target_side='sell', delta=delta)

            #     # Команда выполнена, ранний выход в диспетчер обеспечен, флаги больше не плодим
            #     return
        else:
            logger.warning(f" bag v function analiz_inverted_corridor")
            return
   
    
    def aggregate_coin_data(self, optinsList: list, nameCoin: str) -> dict:
        """
        ФУНКЦИЯ-АГРЕГАТОР (Версия 4.0 — Максимальная оптимизация):
        Строго за ОДИН проход по списку собирает массивы ног, накапливает общие объёмы,
        находит критические страйки и формирует эталонный паспорт данных монеты coin_data.
        """
        optionsSellPut = []
        optionsSellCall = []
        total_call_size = 0.0
        total_put_size = 0.0
        
        # Стартовые маркеры для поиска страйков «на лету» внутри единого цикла
        put_strike = 0.0
        call_strike = float('inf')

        # =====================================================================
        # 🔥 ВСЁ В ОДИН ПРОХОД: СБОР НОГ, ОБЪЁМОВ И СТРАЙКОВ ОДНОВРЕМЕННО 🔥
        # =====================================================================
        for option in optinsList:
            # Защитный барьер (Guard Clause): отсекаем битый мусор API Bybit
            if option.get('symbol') is None:
                continue

            # Инициализируем парсер OptionAsset строго ОДИН раз для контракта
            asset = OptionAsset(raw_symbol=option["symbol"], exchange_instance=self.exchange)

            # Нас интересуют исключительно проданные опционы (Short позиции)
            if option.get('buyOrSell', '').lower() == 'sell':
                asset_type = asset.type.upper().strip()
                current_strike = float(option.get('strike', 0.0))

                # --- РАСПРЕДЕЛЕНИЕ И НАКОПЛЕНИЕ ПО PUT-НОГЕ ---
                if "PUT" in asset_type or asset_type.startswith('P'):
                    optionsSellPut.append(option)
                    total_put_size += float(option.get('size', 0.0))
                    # На ходу ищем МАКСИМАЛЬНЫЙ пут-страйк (нижний край коридора)
                    put_strike = max(put_strike, current_strike)
                    
                # --- РАСПРЕДЕЛЕНИЕ И НАКОПЛЕНИЕ ПО CALL-НОГЕ ---
                elif "CALL" in asset_type or asset_type.startswith('C'):
                    optionsSellCall.append(option)
                    total_call_size += float(option.get('size', 0.0))
                    # На ходу ищем МИНИМАЛЬНЫЙ колл-страйк (верхний край коридора)
                    call_strike = min(call_strike, current_strike)

        # =====================================================================
        # СТЕРИЛИЗАЦИЯ СТРАЙКОВ (Убираем хардкод и бесконечности из паспорта)
        # =====================================================================
        # Если при роллировании PUT-ноги нет, пускай put_strike будет честным 0.0
        if not optionsSellPut:
            put_strike = None
            # put_strike = 0.0
            
        # If call list is empty, clear infinity indicator to None for cleaner data consistency
        if not optionsSellCall:
            call_strike = None
            # call_strike = float("inf")

        # =====================================================================
        # СБОРКА ЭТАЛОННОГО ПАСПОРТА ДАННЫХ МОНЕТЫ
        # =====================================================================
        
        coin_data = {
            'nameCoin': nameCoin,
            'optionsSellCall': optionsSellCall,
            'optionsSellPut': optionsSellPut,
            'total_call_size': total_call_size,
            'total_put_size': total_put_size,
            'put_strike': put_strike,
            'call_strike': call_strike,
            'ticPrice': self.ticPrice, # float(input(f" inter tic price coin {nameCoin} :")),                  # Текущий тик рынка
            'open_futures': self.futures.get(nameCoin)    # Безопасный фьючерс без KeyError
        }
        
        # for key, volme in  coin_data.items():
        #     print(key , volme)

        return coin_data
   
    
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
    
# Пробегаем от 0.0 до 1.0 (стоп-число 1.1 не включается в итерацию)
    for tic in np.arange(0.9, 1.1, 0.01):
        print(round(tic, 1))
    # for tic in range(72, 80):
        time.sleep(1)
        print("=" * 33)
        pusto = TestClass(
                        futures=invertor_open_futures2,
                        options= open_options2, # invers_open_options2, #
                        ticPrice=float(float(format(tic, ".2f")))
                        
                    )
        hending = pusto.process_hedging_logic2()  
        
    
    print("hello bro")  
    































