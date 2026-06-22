import asyncio
import aiohttp
from logger import logger

async def test_proxy_connection():
    # === ВСТАВЬТЕ СЮДА ВАШ ПОЛУЧЕННЫЙ ПРОКСИ ДЛЯ ТЕСТА ===
    # Формат: http://логин:пароль@ip_адрес:порт
    # Если прокси бесплатный без пароля, то просто: http://ip_адрес:порт
    proxy_url = "http://username:password@proxy_ip:proxy_port"
    
    test_url = "https://bybit.com"
    
    logger.info(f"Тестирование прокси-канала: {proxy_url}")
    
    # Отключаем системный DNS, пуская запрос строго через удаленный прокси
    connector = aiohttp.TCPConnector(use_dns_cache=False)
    
    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            logger.info("Отправка тестового запроса к шлюзу Bybit...")
            
            async with session.get(test_url, proxy=proxy_url, timeout=10) as response:
                status = response.status
                text = await response.text()
                
                if status == 200:
                    logger.info("🔥 УСПЕХ! Прокси работает отлично. Bybit вернул цену BTC.")
                    logger.info(f"Ответ сервера (кусочек): {text[:100]}...")
                else:
                    logger.warning(f"❌ Bybit ответил ошибкой {status}. Возможно IP в черном списке Cloudflare.")
                    
    except aiohttp.ClientHttpProxyError as e:
        logger.error(f"❌ Ошибка авторизации или подключения к самому прокси: {e}")
    except asyncio.TimeoutError:
        logger.error("❌ Таймаут соединения: прокси слишком медленный или мертв.")
    except Exception as e:
        logger.error(f"❌ Сетевой сбой. Прокси не справился с DNS/SSL: {e}")

if __name__ == "__main__":
    asyncio.run(test_proxy_connection())
