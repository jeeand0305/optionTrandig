
import logging
import os

# =====================================================================
# КЛАСС КАСТОМНОГО СТИЛИСТА ДЛЯ КОНСОЛИ (ANSI ESCAPE CODES)
# =====================================================================
# Этот класс отвечает за то, чтобы раскрашивать логи в терминале VS Code.
# Цвета нужны, чтобы вы ночью сразу видели глазами критические ошибки.
class CustomFormatter(logging.Formatter):
    # Задаем цветовые схемы в формате ANSI
    grey = "\x1b[38;20m"       # Для отладочных сообщений (DEBUG)
    yellow = "\x1b[33;20m"     # Для предупреждений (WARNING)
    red = "\x1b[31;20m"        # Для обычных ошибок API (ERROR)
    bold_red = "\x1b[31;1m"    # Для критических ситуаций / Маржин-коллов (CRITICAL)
    green = "\x1b[32;20m"      # Для успешных действий и ордеров (INFO)
    reset = "\x1b[0m"          # Сброс цвета обратно в стандартный белый
    
    # Шаблон текста: [ГОД-МЕСЯЦ-ДЕНЬ ЧАС:МИНУТЫ:СЕКУНДЫ] УРОВЕНЬ: Ваше сообщение
    log_format = "[%(asctime)s] %(levelname)s: %(message)s"

    # Связываем каждый уровень логирования с его цветом
    FORMATS = {
        logging.DEBUG: grey + log_format + reset,
        logging.INFO: green + log_format + reset,
        logging.WARNING: yellow + log_format + reset,
        logging.ERROR: red + log_format + reset,
        logging.CRITICAL: bold_red + log_format + reset
    }

    def format(self, record):
        """Этот метод автоматически выбирает цвет в зависимости от важности лога."""
        log_fmt = self.FORMATS.get(record.levelno)
        # Настраиваем формат времени (datefmt), убирая миллисекунды для чистоты
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


# =====================================================================
# ГЛАВНАЯ ФУНКЦИЯ НАСТРОЙКИ СИСТЕМЫ ЛОГИРОВАНИЯ
# =====================================================================
def setup_logger(name="RatioBot"):
    """
    Создает и настраивает объект логгера.
    Разделяет потоки: в файл пишет чистый текст, в консоль — цветной.
    """
    logger = logging.getLogger(name)
    
    # ПРЕДОХРАНИТЕЛЬ: Если бот случайно вызовет эту функцию дважды, 
    # мы не будем добавлять дублирующие обработчики, иначе логи будут двоиться.
    if logger.hasHandlers():
        return logger
        
    # Задаем базовый порог чувствительности. INFO означает, что бот 
    # будет записывать всё, что важнее или равно INFO (INFO, WARNING, ERROR, CRITICAL).
    logger.setLevel(logging.INFO)

    # -----------------------------------------------------------------
    # ТОЧКА НАСТРОЙКИ ПОТОКА №1: ЗАПИСЬ В ТЕКСТОВЫЙ ФАЙЛ (bot.log)
    # -----------------------------------------------------------------
    # Для файла цветовые коды ANSI НЕ НУЖНЫ (они превратятся в нечитаемые символы),
    # поэтому здесь используется стандартный чистый текстовый формат.
    file_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Указываем имя файла и кодировку utf-8, чтобы русский текст не ломался
    file_handler = logging.FileHandler("bot.log", mode='w', encoding="utf-8")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)

    # -----------------------------------------------------------------
    # ТОЧКА НАСТРОЙКИ ПОТОКА №2: ВЫВОД В КОНСОЛЬ VS CODE (ЦВЕТНОЙ)
    # -----------------------------------------------------------------
    console_handler = logging.StreamHandler()
    # Подключаем наш кастомный класс с цветами
    console_handler.setFormatter(CustomFormatter())
    console_handler.setLevel(logging.INFO)

    # -----------------------------------------------------------------
    # ОБЪЕДИНЕНИЕ СИСТЕМЫ
    # -----------------------------------------------------------------
    # Прикрепляем оба канала (файл и консоль) к нашему главному логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# =====================================================================
# СОЗДАНИЕ ГЛОБАЛЬНОГО ОБЪЕКТА ДЛЯ ИМПОРТА
# =====================================================================
# Мы один раз инициализируем логгер прямо внутри этого файла.
# Теперь в любом другом файле проекта вам достаточно написать:
# `from logger import logger` и использовать готовый объект.
logger = setup_logger()












# import logging
# import os
# from dotenv import load_dotenv
# import logging
# import requests

# load_dotenv()
# API_TELEGRAM = os.getenv("TELEGRAM_BOT_TOKEN")
# ID_TELEGRAM = os.getenv("TELEGRAM_CHAT_ID")

# # =====================================================================
# # КЛАСС КАСТОМНОГО СТИЛИСТА ДЛЯ КОНСОЛИ (ANSI ESCAPE CODES)
# # =====================================================================
# # Этот класс отвечает за то, чтобы раскрашивать логи в терминале VS Code.
# # Цвета нужны, чтобы вы ночью сразу видели глазами критические ошибки.
# class CustomFormatter(logging.Formatter):
#     # Задаем цветовые схемы в формате ANSI
#     grey = "\x1b[38;20m"       # Для отладочных сообщений (DEBUG)
#     yellow = "\x1b[33;20m"     # Для предупреждений (WARNING)
#     red = "\x1b[31;20m"        # Для обычных ошибок API (ERROR)
#     bold_red = "\x1b[31;1m"    # Для критических ситуаций / Маржин-коллов (CRITICAL)
#     green = "\x1b[32;20m"      # Для успешных действий и ордеров (INFO)
#     reset = "\x1b[0m"          # Сброс цвета обратно в стандартный белый
    
#     # Шаблон текста: [ГОД-МЕСЯЦ-ДЕНЬ ЧАС:МИНУТЫ:СЕКУНДЫ] УРОВЕНЬ: Ваше сообщение
#     log_format = "[%(asctime)s] %(levelname)s: %(message)s"

#     # Связываем каждый уровень логирования с его цветом
#     FORMATS = {
#         logging.DEBUG: grey + log_format + reset,
#         logging.INFO: green + log_format + reset,
#         logging.WARNING: yellow + log_format + reset,
#         logging.ERROR: red + log_format + reset,
#         logging.CRITICAL: bold_red + log_format + reset
#     }

# # КЛАСС ПАРАЛЛЕЛЬНОЙ ОТПРАВКИ КРИТИЧЕСКИХ ЛОГОВ В TELEGRAM
# # =====================================================================
# class TelegramBotHandler(logging.Handler):
#     """
#     Кастомный обработчик (Handler) для отправки важных системных алертов
#     в Telegram-чат. Защищен от сетевых зависаний таймаутом.
#     """
#     def __init__(self, token: str, chat_id: str):
#         super().__init__()
#         self.token = token
#         self.chat_id = chat_id
#         # Жесткий порог: в Telegram летят логи строго от WARNING и выше
#         self.setLevel(logging.INFO) 

#     def emit(self, record):
#         """
#         Метод вызывается автоматически логгером Python 
#         при каждом срабатывании logger.warning(), logger.error() или logger.critical().
#         """
#         try:
#             # Превращаем системный лог в чистую строку текста без ANSI-кодов
#             log_message = self.format(record)
            
#             # Подставляем визуальный якорь-эмодзи в зависимости от уровня опасности
#             if record.levelno == logging.WARNING:
#                 emoji = "🚨 [ТРЕВОГА]"
#             elif record.levelno >= logging.ERROR:
#                 emoji = "💥 [КРИТИЧЕСКИЙ СБОЙ]"
#             else:
#                 emoji = "ℹ️ [ИНФО]"

#             full_text = f"{emoji}\n{log_message}"
#             url = f"https://telegram.org{self.token}/sendMessage"
            
#             # Отправляем HTTP-запрос. timeout=2.0 гарантирует, что если сервера ТГ лагают,
#             # торговое ядро отвиснет через 2 секунды и продолжит защищать опционы!
#             requests.post(url, data={'chat_id': self.chat_id, 'text': full_text}, timeout=2.0)
            
#         except Exception as tg_err:
#             # Если упал домашний интернет или заблокирован ТГ — просто глушим ошибку в консоль.
#             # Торговый робот ни в коем случае не должен упасть из-за сетевого сбоя мессенджера!
#             print(f"Ошибка отправки сообщения в Telegram: {tg_err}")

#     def format(self, record):
#         """Этот метод автоматически выбирает цвет в зависимости от важности лога."""
#         log_fmt = self.FORMATS.get(record.levelno)
#         # Настраиваем формат времени (datefmt), убирая миллисекунды для чистоты
#         formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
#         return formatter.format(record)


# # =====================================================================
# # ГЛАВНАЯ ФУНКЦИЯ НАСТРОЙКИ СИСТЕМЫ ЛОГИРОВАНИЯ
# # =====================================================================
# def setup_logger(name="RatioBot"):
#     """
#     Создает и настраивает объект логгера.
#     Разделяет потоки: в файл пишет чистый текст, в консоль — цветной.
#     """
#     logger = logging.getLogger(name)
    
#     # ПРЕДОХРАНИТЕЛЬ: Если бот случайно вызовет эту функцию дважды, 
#     # мы не будем добавлять дублирующие обработчики, иначе логи будут двоиться.
#     if logger.hasHandlers():
#         return logger
        
#     # Задаем базовый порог чувствительности. INFO означает, что бот 
#     # будет записывать всё, что важнее или равно INFO (INFO, WARNING, ERROR, CRITICAL).
#     logger.setLevel(logging.INFO)

#     # -----------------------------------------------------------------
#     # ТОЧКА НАСТРОЙКИ ПОТОКА №1: ЗАПИСЬ В ТЕКСТОВЫЙ ФАЙЛ (bot.log)
#     # -----------------------------------------------------------------
#     # Для файла цветовые коды ANSI НЕ НУЖНЫ (они превратятся в нечитаемые символы),
#     # поэтому здесь используется стандартный чистый текстовый формат.
#     file_formatter = logging.Formatter(
#         '[%(asctime)s] %(levelname)s: %(message)s', 
#         datefmt='%Y-%m-%d %H:%M:%S'
#     )
    
#     # Указываем имя файла и кодировку utf-8, чтобы русский текст не ломался
#     file_handler = logging.FileHandler("bot.log", encoding="utf-8")
#     file_handler.setFormatter(file_formatter)
#     file_handler.setLevel(logging.INFO)

#     # -----------------------------------------------------------------
#     # ТОЧКА НАСТРОЙКИ ПОТОКА №2: ВЫВОД В КОНСОЛЬ VS CODE (ЦВЕТНОЙ)
#     # -----------------------------------------------------------------
#     console_handler = logging.StreamHandler()
#     # Подключаем наш кастомный класс с цветами
#     console_handler.setFormatter(CustomFormatter())
#     console_handler.setLevel(logging.INFO)

#     # -----------------------------------------------------------------
#     # ОБЪЕДИНЕНИЕ СИСТЕМЫ
#     # -----------------------------------------------------------------
#     # Прикрепляем оба канала (файл и консоль) к нашему главному логгеру
#     logger.addHandler(file_handler)
#     logger.addHandler(console_handler)

#     return logger


# def setup_logger(name="RatioBot"):
#     """
#     Создает и настраивает объект логгера.
#     Разделяет потоки: в файл и Telegram пишет чистый текст, в консоль — цветной.
#     """
#     logger = logging.getLogger(name)
    
#     # ПРЕДОХРАНИТЕЛЬ: Если бот случайно вызовет эту функцию дважды, 
#     # мы не будем добавлять дублирующие обработчики, иначе логи будут двоиться.
#     if logger.hasHandlers():
#         return logger
        
#     # Задаем базовый порог чувствительности глобального логгера
#     logger.setLevel(logging.INFO)

#     # -----------------------------------------------------------------
#     # ТОЧКА НАСТРОЙКИ ПОТОКА №1: ЗАПИСЬ В ТЕКСТОВЫЙ ФАЙЛ (bot.log)
#     # -----------------------------------------------------------------
#     # Для файла цветовые коды ANSI НЕ НУЖНЫ, используем чистый текстовый формат
#     file_formatter = logging.Formatter(
#         '[%(asctime)s] %(levelname)s: %(message)s', 
#         datefmt='%Y-%m-%d %H:%M:%S'
#     )
    
#     # Указываем имя файла и кодировку utf-8, чтобы русский текст не ломался на диске
#     file_handler = logging.FileHandler("bot.log", encoding="utf-8")
#     file_handler.setFormatter(file_formatter)
#     file_handler.setLevel(logging.INFO)
#     logger.addHandler(file_handler)

#     # -----------------------------------------------------------------
#     # ТОЧКА НАСТРОЙКИ ПОТОКА №2: ВЫВОД В КОНСОЛЬ VS CODE (ЦВЕТНОЙ)
#     # -----------------------------------------------------------------
#     console_handler = logging.StreamHandler()
#     console_handler.setFormatter(CustomFormatter())
#     console_handler.setLevel(logging.INFO)
#     logger.addHandler(console_handler)

#     # -----------------------------------------------------------------
#     # 🔥 ТОЧКА НАСТРОЙКИ ПОТОКА №3: ОТПРАВКА В TELEGRAM (ПО ПРЕДОХРАНИТЕЛЮ) 🔥
#     # -----------------------------------------------------------------
#     # Безопасно извлекаем ключи из переменных окружения твоего .env файла
#     TG_TOKEN   = API_TELEGRAM
#     TG_CHAT_ID = ID_TELEGRAM

#     # Включаем Telegram-канал только если в .env файле реально заполнены оба поля
#     if TG_TOKEN and TG_CHAT_ID:
#         tg_handler = TelegramBotHandler(token=TG_TOKEN, chat_id=TG_CHAT_ID)
        
#         # Переиспользуем твой чистый текстовый file_formatter (без ANSI-мусора!)
#         tg_handler.setFormatter(file_formatter)
        
#         # Подключаем Telegram к глобальной системе логгера
#         logger.addHandler(tg_handler)
#         logger.info("📱 Системный Telegram-канал уведомлений успешно активирован из .env")
#     else:
#         logger.warning("⚠️ Ключи Telegram не найдены в .env. Алерты идут только в файл и консоль.")

#     return logger

# # =====================================================================
# # СОЗДАНИЕ ГЛОБАЛЬНОГО ОБЪЕКТА ДЛЯ ИМПОРТА
# # =====================================================================
# # Мы один раз инициализируем логгер прямо внутри этого файла.
# # Теперь в любом другом файле проекта вам достаточно написать:
# # `from logger import logger` и использовать готовый объект.
# logger = setup_logger()



