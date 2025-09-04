"""
Модуль запуска FastAPI приложения с управлением жизненным циклом
подключения к базе данных. Для контроля раюоты приложения и 
взаимодействия с БД настроено логирование.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import DatabaseSingleton
from app.routes.tasks_routes import router


# Настройка логирования
log_file_path = "app.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info("Приложение запускается.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Асинхронный контекстный менеджер, который управляет
    жизненным циклом подключения к БД в FastAPI приложении.
    """
    db = DatabaseSingleton.get_db()
    try:
        await db.connect()
        logger.info("Подключение к БД выполнено.")
        yield
    except Exception as exc:
        logger.error(f"Ошибка подключения к БД: {exc}.")
        raise RuntimeError(f"Ошибка подключения к БД: {exc}.")
    finally:
        await db.disconnect()
        logger.info("Отключение от БД выполнено.")


app = FastAPI(lifespan=lifespan)


app.include_router(router)
