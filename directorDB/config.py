"""
Настройки ETL. Все параметры — из .env.
Ничего не хардкодим, ничего не знаем про торговый контур.
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv
from logger import logger

# Загружаем .env один раз при импорте модуля
load_dotenv()


@dataclass
class DBConfig:
    """Настройки подключения к PostgreSQL."""
    dbname: str
    user: str
    password: str
    host: str = 'localhost'
    port: int = 5432


def load_db_config() -> DBConfig:
    """
    Читает настройки БД из переменных окружения.
    Падает с понятной ошибкой, если чего-то не хватает.
    """
    password = os.getenv('DB_PASSWORD')
    if not password:
        logger.error('DB_PASSWORD не задан в .env')
        raise ValueError('DB_PASSWORD не задан')

    cfg = DBConfig(
        dbname=os.getenv('DB_NAME', 'demo'),
        user=os.getenv('DB_USER', 'postgres'),
        password=password,
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '5432')),
    )
    logger.info(f'DB config: {cfg.host}:{cfg.port}/{cfg.dbname} (user={cfg.user})')
    return cfg