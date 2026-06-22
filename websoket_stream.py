import asyncio
import ccxt.pro as ccxtpro
from logger import logger
import config

class BybitWebSocketStream:
    def __init__(self):
        """Инициализация WebSocket-подключения к Bybit через CCXT Pro"""
        self.exchange = ccxtpro.bybit({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'swap',# Подключаемся к потоку бессрочных фьючерсов
                'subType': "linear", #warring
            }
        })
        
        # Переключаем вебсокет в тестнет, если это указано в config
        if config.IS_TESTNET:
            self.exchange.set_sandbox_mode(True)
            
        self.current_price = None  # Сюда записывается актуальная цена из WS
        self.is_running = True

    async def start_price_stream(self):
        """Бесконечный асинхронный цикл чтения цены из WebSocket"""
        logger.info(f"Установка WebSocket соединения с Bybit для {config.SYMBOL}...")
        
        while self.is_running:
            try:
                # Метод watch_ticker открывает WebSocket-канал и ждет пуш от биржи
                ticker = await self.exchange.watch_ticker(config.SYMBOL)
                
                # Обновляем переменную последней рыночной ценой (last)
                if ticker and 'last' in ticker:
                    self.current_price = float(ticker['last'])
                    
            except Exception as e:
                logger.error(f"Ошибка в WebSocket потоке цены: {e}")
                # Если связь оборвалась, ждем 5 секунд и пробуем переподключиться
                await asyncio.sleep(5)
                
        # Закрываем соединение при остановке
        await self.exchange.close()

    def get_latest_price(self):
        """Метод для внешних модулей (main.py), чтобы быстро забрать текущую цену из памяти"""
        return self.current_price

    def stop(self):
        """Остановка потока"""
        self.is_running = False

# =====================================================================
# БЛОК ИЗОЛИРОВАННОГО ТЕСТИРОВАНИЯ ВЕБСОКЕТА
# =====================================================================
# =====================================================================
# БЛОК ИЗОЛИРОВАННОГО ТЕСТИРОВАНИЯ ВЕБСОКЕТА (ИСПРАВЛЕННЫЙ)
# =====================================================================
async def test_main():
    stream = BybitWebSocketStream()
    
    # 1. Запускаем стрим цены в фоновом режиме как отдельную задачу
    price_task = asyncio.create_task(stream.start_price_stream())
    
    logger.info("Ждем первые данные от WebSocket (5 секунд)...")
    await asyncio.sleep(5)
    
    # 2. 5 раз с интервалом в 2 секунды проверяем обновление цены в памяти
    for i in range(1, 6):
        price = stream.get_latest_price()
        if price is not None:
            logger.info(f"[Тест {i}/5] Успешно заменено в памяти -> Цена {config.SYMBOL}: {price} USDT")
        else:
            logger.warning(f"[Тест {i}/5] Цена в памяти еще пустая (None). Проверьте интернет или тикер.")
        await asyncio.sleep(2)
        
    # 3. КОРРЕКТНОЕ ЗАКРЫТИЕ: Сначала останавливаем цикл внутри класса
    stream.stop()
    
    # Ждем, пока фоновая задача price_task сама завершится и вызовет `await self.exchange.close()`
    logger.info("Ожидание корректного закрытия сессии WebSocket Bybit...")
    await price_task 
    
    logger.info("--- ТЕСТ WEBSOCKET УСПЕШНО ЗАВЕРШЕН БЕЗ УТЕЧЕК ПАМЯТИ ---")

if __name__ == "__main__":
    # Запуск асинхронного теста
    asyncio.run(test_main())

