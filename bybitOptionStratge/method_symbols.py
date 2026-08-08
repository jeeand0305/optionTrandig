from datetime import datetime
import ccxt
from logger import logger

class OptionAsset:
    """
    Полностью универсальный кроссплатформенный парсер на базе CCXT.
    Сам находит метаданные (страйк, тип, символы) для любой биржи мира.
    """
    def __init__(self, raw_symbol: str, exchange_instance=None):
        self.raw_symbol = raw_symbol.strip().upper()
        self.exchange = exchange_instance
        
        # Финальные очищенные поля
        self.coin = ""
        self.strike = 0.0
        self.type = ""
        self.ccxt_symbol = ""
        self.futures_symbol = ""

        # Если нам передали экземпляр биржи и в нем загружены рынки
        if self.exchange and hasattr(self.exchange, 'markets') and self.exchange.markets:
            self._parse_via_ccxt()
        else:
            # Если биржи нет под рукой (например, в изолированном тесте) — откатываемся на простой разбор
            self._parse_fallback()


    def _parse_via_ccxt(self):
        """
        Универсальный сканер кэша CCXT. 
        Забирает параметры с конца строки, полностью защищая робота от 
        аномалий синтаксиса Bybit v5 (слово 'Options', суффиксы валют).
        """
        parts = self.raw_symbol.split('-')
        
        # Проверяем, что в строке есть косая черта или двоеточие (признак готового CCXT-формата)
        is_ccxt_format = "/" in self.raw_symbol or ":" in self.raw_symbol

        if not is_ccxt_format:
            # === ВЕТКА А: СЫРОЙ/МАТЕМАТИЧЕСКИЙ ФОРМАТ (напр. 'XRPUSDT-Options-4AUG26-1.1-C') ===
            if len(parts) >= 4:
                # Ювелирный сбор параметров с конца строки
                opt_type = parts[-1].upper()        # Последний элемент: всегда тип ноги 'C' или 'P'
                strike_str = parts[-2]             # Предпоследний элемент: всегда страйк ('1.1', '74')
                
                # Извлекаем чистую монету из первого сегмента (напр. из 'XRPUSDT' или 'SOLUSDT')
                raw_coin = parts[0].upper()
                base_coin = raw_coin.replace("USDT", "").replace("USDC", "").replace("/USDT", "").replace("/USDC", "")
                
                self.coin = base_coin
                self.strike = float(strike_str)
                self.type = opt_type
                
                # Сканируем загруженные рынки биржи для поиска нативного CCXT-имени инструмента
                for market_symbol, market_data in self.exchange.markets.items():
                    logger.info(f"market symbol {market_symbol}")
                    logger.info(f"market data {market_data}")
                    if market_data.get('option'):
                        try:
                            market_strike = market_data.get('strike')
                            if market_strike is None or market_strike == "":
                                continue
                            market_strike_float = float(market_strike)
                        except (ValueError, TypeError):
                            continue

                        # Сверяем очищенные параметры с кэшем биржи
                        if (market_data.get('base') == base_coin and 
                            market_strike_float == self.strike and 
                            market_data.get('optionType', '').upper() == opt_type):
                            
                            self.ccxt_symbol = market_symbol
                            
                            # Тянем имя фьючерса для хеджирования
                            linear_info = market_data.get('linear', {})
                            if isinstance(linear_info, dict) and 'symbol' in linear_info:
                                self.futures_symbol = linear_info['symbol']
                            else:
                                self.futures_symbol = f"{base_coin}/USDT:USDT"
                            return
                
                # Запасной шаблон сборки, если контракт только что создан и его еще нет в общем кэше
                self.ccxt_symbol = self.raw_symbol 
                self.futures_symbol = f"{base_coin}/USDT:USDT"
            else:
                raise ValueError(f"Недостаточно сегментов для разбора сырого формата опциона: {self.raw_symbol}")
                
        else:
            # === ВЕТКА Б: ЧИСТЫЙ CCXT-ФОРМАТ С СЕРВЕРА (напр. 'XRP/USDT:USDT-260804-1.1-C') ===
            self.ccxt_symbol = self.raw_symbol
            market_data = self.exchange.markets.get(self.raw_symbol)
            
            if market_data:
                # Если биржа нашла прямой ключ в оперативной памяти CCXT
                self.coin = market_data.get('base', '')
                try:
                    self.strike = float(market_data.get('strike', 0.0))
                except (ValueError, TypeError):
                    self.strike = 0.0
                self.type = market_data.get('optionType', 'C').upper()
                
                linear_info = market_data.get('linear', {})
                if isinstance(linear_info, dict) and 'symbol' in linear_info:
                    self.futures_symbol = linear_info['symbol']
                else:
                    self.futures_symbol = f"{self.coin}/USDT:USDT"
            else:
                # Отказоустойчивый парсер-разделитель с конца строки для CCXT-символов вне кэша
                if len(parts) >= 3:
                    self.type = parts[-1].upper()   # 'C' или 'P'
                    try:
                        self.strike = float(parts[-2]) # Страйк
                    except (ValueError, TypeError):
                        self.strike = 0.0
                    
                    # Извлекаем монету из левой части до косой черты (напр. из 'SOL/USDT:USDT')
                    raw_base = parts[0]
                    if "/" in raw_base:
                        self.coin = raw_base.split('/')[0].upper()
                    else:
                        self.coin = raw_base.upper()
                        
                    if "USDC" in self.raw_symbol:
                        self.futures_symbol = f"{self.coin}/USDC:USDC"
                    else:
                        self.futures_symbol = f"{self.coin}/USDT:USDT"


    def _parse_fallback(self):
        """Запасной ручной вариант, если нет связи с биржей"""
        parts = self.raw_symbol.replace('/', '-').replace(':', '-').split('-')
        # (Тут остается простой линейный сплит строки для тестов на ПК)
        self.coin = parts[0]
        self.type = parts[-1]
        self.strike = float(parts[-2]) if len(parts) >= 2 else 0.0
        self.ccxt_symbol = self.raw_symbol


# === БЛОК ТЕСТИРОВАНИЯ ДЛЯ ТВОЕГО ПК ===
# if __name__ == "__main__":
#     print("🤖 Инициализируем проверки автоматического подбора...")
    
#     # Создаем тестовый инстанс Bybit БЕЗ ключей config (для load_markets они не нужны)
#     test_exchange = ccxt.deribit({
#         'enableRateLimit': True,
#         'options': {
#             'defaultType': 'option' # Указываем, что работаем с опционами
#         }
#     })
    
#     print(f"⏳ Скачиваем актуальную сетку опционов с биржи"
#           f"(это может занять пару секунд)...")
#     try:
#         test_exchange.load_markets()
#         print("✅ Рынки успешно загружены в память!")
#     except Exception as e:
#         print(f"❌ Ошибка подключения к бирже: {e}")
#         exit()

#     print("\n--- ТЕСТ 1: Входной символ от твоей математики ---")
#     # Допустим, твоя математика посчитала опцион на SOL или BTC (берем август, так как июль уже прошел)
#     # Пример формата: "SOL-28AUG26-70-P" (проверь актуальные даты на бирже, если пустой)
#     math_symbol = "DOGE-07AUG26-70-P" 
    
#     print(f"Подаем на вход: {math_symbol}")
#     asset1 = OptionAsset(raw_symbol=math_symbol, 
#                          exchange_instance=test_exchange)
    
#     print(f"1. Нашли в кэше CCXT:  {asset1.ccxt_symbol}")
#     print(f"2. Очищенная монета:  {asset1.coin}")
#     print(f"3. Число страйка:     {asset1.strike} (Тип: {type(asset1.strike).__name__})")
#     print(f"4. Тип опциона:       {asset1.type}")
#     print(f"5. Символ фьючерса:   {asset1.futures_symbol}")
    
#     print("-" * 50)

#     print("\n--- ТЕСТ 2: Входной символ из fetch_positions (CCXT формат) ---")
#     pos_symbol = "DOGE/USDT:USDT-260807-70-P"
#     print(f"Подаем на вход из баланса: {pos_symbol}")
    
#     asset2 = OptionAsset(raw_symbol=pos_symbol, exchange_instance=test_exchange)
#     print(f"1. Распознан как CCXT: {asset2.ccxt_symbol}")
#     print(f"2. Очищенная монета:  {asset2.coin}")
#     print(f"3. Число страйка:     {asset2.strike}")
#     print(f"4. Тип опциона:       {asset2.type}")
#     print(f"5. Символ фьючерса:   {asset2.futures_symbol}")
#     print("-" * 50)

