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
import time

# Дальше ваши тестовые данные (open_futures1, open_options1 и т.д.)


open_futures1 = {'SOL': {'symbol': 'SOL/USDT:USDT', 'side': 'buy', 'size': 1.5, 'openPrice': 75.37941176, 'leverage': 10.0, 'initMargin': 11.5034122}, 'NEAR': {'symbol': 'NEAR/USDT:USDT', 'side': 'buy', 'size': 12.0, 'openPrice': 1.616, 'leverage': 1.0, 'initMargin': 19.5228}}
open_options1 = [{'symbol': 'SOL/USDT:USDT-260814-75-C', 'ccxt_symbol': 'SOL/USDT:USDT-260814-75-C', 'buyOrSell': 'sell', 'size': 3.0, 'entry_price': 0.94, 'hours_to_expiration': 132.35, 'strike': 75.0, 'type': 'CALL', 'futures_symbol': 'SOL/USDT:USDT', 'initMargin': 40.12063646}, {'symbol': 'SOL/USDT:USDT-260814-73-P', 'ccxt_symbol': 'SOL/USDT:USDT-260814-73-P', 'buyOrSell': 'sell', 'size': 3.0, 'entry_price': 1.0, 'hours_to_expiration': 132.35, 'strike': 73.0, 'type': 'PUT', 'futures_symbol': 'SOL/USDT:USDT', 'initMargin': 28.11017423}]

open_options2 = ({'SOL': [{'symbol': 'SOL/USDT:USDT-260828-78-C', 'ccxt_symbol': 'SOL/USDT:USDT-260828-78-C', 
                'buyOrSell': 'sell', 'size': 4.0, 'entry_price': 1.33, 'hours_to_expiration': 217.03,
                'strike': 78.0, 'type': 'CALL', 'futures_symbol': 'SOL/USDT:USDT', 'initMargin': 48.10864144},
                {'symbol': 'SOL/USDT:USDT-260821-74-P', 'ccxt_symbol': 'SOL/USDT:USDT-260821-74-P',
                 'buyOrSell': 'sell', 'size': 4.0, 'entry_price': 0.87, 'hours_to_expiration': 49.03, 
                 'strike': 74.0, 'type': 'PUT', 'futures_symbol': 'SOL/USDT:USDT', 'initMargin': 37.41257572}], 
                  'XRP': [{'symbol': 'XRP/USDT:USDT-260820-1-C', 'ccxt_symbol': 'XRP/USDT:USDT-260820-1-C', 
                'buyOrSell': 'sell', 'size': 20.0, 'entry_price': 0.0071, 'hours_to_expiration': 25.03,
                'strike': 1.0, 'type': 'CALL', 'futures_symbol': 'XRP/USDT:USDT', 'initMargin': 4.2830806}, 
                {'symbol': 'XRP/USDT:USDT-260820-0.98-P', 'ccxt_symbol': 'XRP/USDT:USDT-260820-0.98-P', 
                 'buyOrSell': 'sell', 'size': 20.0, 'entry_price': 0.0032, 'hours_to_expiration': 25.03, 
                 'strike': 0.98, 'type': 'PUT', 'futures_symbol': 'XRP/USDT:USDT', 'initMargin': 3.5989536}]})

open_futures2 = ({'XRP': {'symbol': 'XRP/USDT:USDT', 'side': 'sell', 'size': 10.0, 'openPrice': 1.0229, 
                          'leverage': 10.0, 'initMargin': 1.0340519}, 'NEAR': {'symbol': 'NEAR/USDT:USDT',
                'side': 'buy', 'size': 12.0, 'openPrice': 1.616, 'leverage': 1.0, 'initMargin': 19.4064},
                'SOL': {'symbol': 'SOL/USDT:USDT', 'side': 'buy', 'size': 1.5, 'openPrice': 79.25208792, 
                        'leverage': 10.0, 'initMargin': 11.49544031}})

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
        self.ticPrice = botBybit
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
                time.sleep(5)
                # ШАГ 1: Агрегируем данные (создаем coin_data один раз)
                coin_data = self.aggregate_coin_data(
                    optinsList=options_list, nameCoin=coin_upper)
            
                logger.info(f" coin-data {coin_data}")
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
                # coridor_result = self.analizCoridorStrikes(coin_data)

                # if coridor_result['analizeBool'] == True:
                #     self.analizCallStrike(coin_data)
                #     self.analizPutStrike(coin_data)
                
                
                # [Сюда стыкуется Кусок 3: вызов analizCoridorStrikes и запуск CALL/PUT веток]
                
            except Exception as coin_error:
                # Если на XRP произойдет технический или сетевой сбой — робот не упадет
                logger.error(f"💥 Критический сбой при обработке монеты {coin_upper}: {coin_error}")
                
                # Безопасно переходим к следующей монете в списке self.options
                logger.info(f" {coin_name } hedgirovanie prossplo uspeshno")
                continue  
            
            
        # Конец главного цикла сканирования портфеля
        return True
    
    # no test
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
            if total_put_size == fut_size and fut_side == 'buy': 
                return 
            
            elif total_put_size != fut_size and fut_side != 'buy':            
                # Компактный тернарный оператор вычисляет точную дельту с учетом позиции
                delta = (total_put_size - fut_size if fut_side == 'buy' 
                         else total_put_size)

                logger.info(
                    f"📈 [ИНВЕРСИЯ ТРЕНДА] Текущий тик {ticPrice} >= "
                    f" Середины {mid_price}. "
                    f"Целевой хэдж: BUY (LONG) | Необходимый объем: "
                    f" | Рассчитанная дельта ордера: {delta}" )

                # Передаем рассчитанную дельту в наш универсальный исполнитель ордеров
                self.execute_hedge_adjustment(nameCoin=nameCoin,
                                              target_side='buy',
                                              delta=delta)
                return
        # --- СЦЕНАРИЙ Б: ЦЕНА УПАЛА НИЖЕ МАТЕМАТИЧЕСКОЙ СЕРЕДИНЫ (<100) ---
        elif ticPrice <= mid_price:
            if total_call_size == fut_size and fut_side == 'sell': 
                return 
                        
            elif total_call_size != fut_size and fut_side != 'buy': 
                # Целевой объем хэджа должен жестко равняться объему PUT-ноги


                # Компактный тернарный оператор вычисляет точную дельту для шорт-позиции
                delta = (total_put_size - fut_size if fut_side == 'sell' 
                         else total_put_size)

                logger.info(
                    f"📉 [ИНВЕРСИЯ ТРЕНДА] Текущий тик {ticPrice} < "
                    f" Середины {mid_price}. "
                    f"Целевой хэдж: SELL (SHORT) | Необходимый объем: "
                    f"  | Рассчитанная дельта ордера: {delta}" )

                # Передаем рассчитанную дельту в наш универсальный исполнитель ордеров
                self.execute_hedge_adjustment(nameCoin=nameCoin, target_side='sell', delta=delta)

                # Команда выполнена, ранний выход в диспетчер обеспечен, флаги больше не плодим
                return
            else:
                logger.warning(f" bag v function analiz_inverted_corridor")
                return

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
        total_call_size = 0.0
        total_put_size = 0.0
        
        open_futures = self.futures.get(nameCoin)
        # ticPrice = self.ticPrice pod zamenu
        ticPrice = float(input(f"input tic price coin {nameCoin} :")) 
        
        for option in optinsList:
            if option.get('symbol') is None:
                continue
            
            asset = OptionAsset(raw_symbol=option["symbol"], 
                                exchange_instance=self.exchange)
            
            if option.get('buyOrSell', '').lower() == 'sell':
                asset_type = asset.type.upper().strip()
                
                # Исправлено: безопасное разделение по типам без IndexError
                if "PUT" in asset_type or asset_type.startswith('P'):
                    optionsSellPut.append(option)
                    total_put_size += float(option.get('size', 0.0))
                    
                elif "CALL" in asset_type or asset_type.startswith('C'):
                    optionsSellCall.append(option)
                    total_call_size += float(option.get('size', 0.0))
        
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
        
        # =====================================================================
        # КУСОК 3: МАТЕМАТИЧЕСКИЕ СЦЕНАРИИ С ПРАВИЛЬНЫМИ ФЛАГАМИ ТРЕВОГИ
        # =====================================================================

                # === ТОЧЕЧНЫЙ АНАЛИЗ ВЫВЕРНУТОГО КОРРИДОРА (PUT > CALL) ===
        if put_strike > call_strike:
            logger.warning(f"⚠️ [ИНВЕРСИЯ СТРАЙКОВ] По монете {nameCoin} "
                           f" вывернут коридор: {put_strike} > {call_strike}")
            
            # Вычисляем математическую середину 
            mid_price = (put_strike + call_strike) / 2  # (101 + 99) / 2 = 100
            
            # Собираем актуальные данные по открытому фьючерсу (наш технический щит)
            fut_size = 0.0
            fut_side = 'none'
            if open_futures:
                fut_size = float(open_futures.get('size', 0.0))
                fut_side = open_futures.get('side', '').lower().strip()

            # --- ВЕТВЛЕНИЕ ОТНОСИТЕЛЬНО СЕРЕДИНЫ С УЧЕТОМ ОБЪЕМОВ ---
            if ticPrice > mid_price:
                # Зона 100+: Целевой хэдж должен быть строго BUY (LONG)
                # Берем суммарный объем всех проданных CALL опционов
                target_qty = total_call_size 
                delta = target_qty - fut_size if fut_side == 'buy' else target_qty
                
                # work posle pernosav bybit_client
                # self.execute_hedge_adjustment(
                #     nameCoin=nameCoin, 
                #     target_side='buy',
                #     delta=delta)
                
                dictPutSellAnaliz['analizeBool'] = False
                return dictPutSellAnaliz
                
               
            # Если фьючерса нет или он стоит в противоположную сторону (SELL)
            elif ticPrice < mid_price:
                target_qty = total_put_size
                # Дельта равна target_qty, а исполнитель сам закроет старый SELL (шорт)
                delta = target_qty - fut_size if fut_side == 'sell' else target_qty
            
                # Отправляем рассчитанную дельту в наш универсальный исполнитель
                # self.execute_hedge_adjustment(nameCoin=nameCoin, target_side='sell', delta=delta)

                dictPutSellAnaliz['analizeBool'] = False # Сами всё исполнили, в главные подфункции не пускаем
                return dictPutSellAnaliz
                
            else:
                # Зона <100: Целевой хэдж должен быть строго SELL (SHORT)
                target_qty = total_put_size
                
                # Если фьючерс уже стоит в SELL — считаем разницу
                if fut_side == 'sell':
                    delta = target_qty - fut_size
                else:
                    delta = target_qty
                    
                self.execute_hedge_adjustment(nameCoin=nameCoin, target_side='sell', delta=delta)
                
                dictPutSellAnaliz['analizeBool'] = False
                return dictPutSellAnaliz
            
         
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
                logger.error(f"close futures {nameCoin}")
                dictPutSellAnaliz['analizeBool'] = False
        
        # Сценарий 2: Текущая цена входа фьючерса И рыночный тик находятся внутри коридора
        if open_futures:
            fut_open_price = float(open_futures.get('openPrice', 0.0))
            
            # 1. Проверяем цену входа фьючерса (полукоридоры с защитой от None)
            is_fut_above_put = (put_strike is None) or (fut_open_price > put_strike)
            is_fut_below_call = (call_strike is None) or (fut_open_price < call_strike)
            is_futures_safe = is_fut_above_put and is_fut_below_call
            
            # 2. ТВОЙ НОВЫЙ ЩИТ: Проверяем, что текущий тик рынка ТОЖЕ в безопасности!
            is_tic_above_put = (put_strike is None) or (ticPrice > put_strike)
            is_tic_below_call = (call_strike is None) or (ticPrice < call_strike)
            is_ticker_safe = is_tic_above_put and is_tic_below_call
            
            # ИСПОЛНЕНИЕ: Закрываем хэдж, ТОЛЬКО если и фьючерс, и рынок в полной безопасности!
            if is_futures_safe and is_ticker_safe:
                logger.info(f"✅ И фьючерс ({fut_open_price}), и тик рынка ({ticPrice}) внутри коридора. Хэдж полностью лишний.")
                
                # Вот теперь «дворника» можно вызывать со спокойной душой!
                self.execute_dehedging_cleanup(nameCoin=nameCoin)
                
                dictPutSellAnaliz['analizeBool'] = False 
                return dictPutSellAnaliz

            
        # Сценарий 3: Текущий рыночный тик находится строго внутри безопасного диапазона
        is_tic_above_put = (put_strike is None) or (ticPrice > put_strike)
        is_tic_below_call = (call_strike is None) or (ticPrice < call_strike)
        
        if is_tic_above_put and is_tic_below_call:
            logger.info(f"🟢 Текущий тик {ticPrice} находится внутри безопасного коридора ({put_strike} - {call_strike})")
            dictPutSellAnaliz['analizeBool'] = False # БЕЗОПАСНОСТЬ: Рынок в норме, ничего не трогаем
            return dictPutSellAnaliz            
            
        # Сценарий 4: Каскадный вылет цены за пределы страйков (Зона риска пробития)
        else:
            logger.warning(
                f"⚠️ Цена {ticPrice} ЗА ПРЕДЕЛАМИ зоны безопасности! "
                f"Коридор риска: {put_strike if put_strike is not None else 'МИН'} - {call_strike if call_strike is not None else 'МАКС'}"
            )
            dictPutSellAnaliz['analizeBool'] = True # ТРЕВОГА: Коридор пробит! Включаем защиту CALL/PUT веток!
            return dictPutSellAnaliz

    
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
            
        # If call list is empty, clear infinity indicator to None for cleaner data consistency
        if not optionsSellCall:
            call_strike = None

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
            'ticPrice': self.ticPrice.get_ticker_by_symbol(symbol=nameCoin),                    # Текущий тик рынка
            'open_futures': self.futures.get(nameCoin)    # Безопасный фьючерс без KeyError
        }

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
    pusto = TestClass(
                      futures=open_futures2,
                      options=open_options2
                  )
    hending = pusto.process_hedging_logic2()  
        
    
    print("hello bro")  
    































