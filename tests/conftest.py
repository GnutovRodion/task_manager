"""
Модуль с фикстурами для тестирования FastAPI-приложения
с использованием pytest.
В данном модуле определены фикстуры для создания тестовой 
базы данных PostgreSQL, управления сессиями БД,
настройки тестового клиента FastAPI и предоставления невалидных
параметров для тестирования валидации входных данных.
Модуль использует переменную окружения TESTING для переключения
на тестовую БД, обеспечивая изоляцию тестов и безопасность основной БД.
"""


import os

import pytest
from sqlalchemy import create_engine
from fastapi.testclient import TestClient
from sqlalchemy.orm import scoped_session, sessionmaker
from alembic import command
from alembic.config import Config
from sqlalchemy_utils import create_database, drop_database

# Устанавливаем os.environ, чтобы использовать тестовую БД
os.environ["TESTING"] = "True"
from app.db import SQLALCHEMY_DATABASE_URL as db
from app.main import app


@pytest.fixture(scope="module")
def temp_db():
    """Создает временную тестовую БД."""
    try:
        create_database(db)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))
        command.upgrade(alembic_cfg, "head")
        yield db
    finally:
        drop_database(db)


@pytest.fixture(scope="function")
def db_session(temp_db):
    """Создает и возвращает сессию БД для тестов."""
    engine = create_engine(temp_db)
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()
    yield session
    session.close()
    Session.remove()


@pytest.fixture(scope="function")
def client():
    """Создает тестовый клиент с подключением к тестовой БД."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def bad_params():
    """Возвращает невалидные параметры."""
    return [
        ({"name": ""}, "empty_name"),
        ({
            "name": "a" * 257
        }, 
            "long_name"
        ),
        ({
            "name": "create_bad_task_1",
            "status": "Почти готово"
        },
            "bad_status"
        ),
        ({
            "uuid": 123,
            "name": "create_bad_task_2"
        },
            "manual_uuid"
        ),
        ({
            "name": "create_bad_task_3",
            "new_field": "value"
        },
            "extra_field"
        )
    ]
