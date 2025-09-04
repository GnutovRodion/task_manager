"""
Модуль для управления асинхронным подключением к базе данных
PostgreSQL с использованием паттерна Singleton.
В данном модуле реализован класс 'DatabaseSingleton', который
гарантирует создание единственного экземпляра подключения к БД.
Конфигурация подключения загружается из переменных окружения,
поддерживается переключение между основной и тестовой БД через
переменную окружения 'TESTING'
"""

import os

import databases
from dotenv import load_dotenv


load_dotenv()


DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
TESTING = os.environ.get("TESTING", "False").lower() == "true"

if TESTING:
    DB_NAME = os.getenv("TEST_DB_NAME", "test_db_name")
else:
    DB_NAME = os.getenv("POSTGRES_DB", "db_name")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
)


class DatabaseSingleton:
    """Singleton-класс, управляющий подключением к БД."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = databases.Database(SQLALCHEMY_DATABASE_URL)
        return cls._instance

    async def connect(self):
        if not self.is_connected:
            await self._instance.connect()

    async def disconnect(self):
        if self.is_connected:
            await self._instance.disconnect()

    @property
    def is_connected(self):
        return self._instance.is_connected if self._instance else False

    @classmethod
    def get_db(cls):
        return cls._instance
