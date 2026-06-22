import time
from pybit.unified_trading import WebSocket
from logger import logger

# Используем самый ликвидный бессрочный фьючерс для проверки вывода цен в тестнете
TEST_SYMBOL = "DOGEUSDT"

def handle_websocket_message(message):
    if "data" in message:
        ticker_data = message["data"]
        topic = message.get("topic", "")
        symbol = topic.replace("tickers.", "")
        
        # Для фьючерсов на Bybit используется поле lastPrice
        current_price = ticker_data.get("lastPrice")
        bid = ticker_data.get("bid1Price")
        ask = ticker_data.get("ask1Price")
        
        if current_price:
            logger.info(f"🔥 [{symbol}] Живая цена БА: {current_price} USDT | Bid: {bid} | Ask: {ask}")
            
    elif "ret_msg" in message and message["ret_msg"] == "subscribe":
        logger.info(f"✅ Успешная подписка на живой поток цен фьючерса.")

def main():
    count=0
    logger.info("Проверка потока цен через Pybit WebSocket (Линейный рынок)...")
    
    # Подключаемся к фьючерсному сокету тестнета
    ws = WebSocket(
        testnet=False,
        channel_type="linear"
    )
    
    ws.ticker_stream(
        symbol=TEST_SYMBOL,
        callback=handle_websocket_message
    )
    
    logger.info("Соединение удерживается. Ожидание первого изменения цены фьючерса...")
    
    try:
        while True:
            count+=1
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Тест остановлен пользователем.")
        
        

if __name__ == "__main__":
    main()
