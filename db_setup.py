import os
from sqlalchemy_utils import database_exists, create_database, drop_database
import pytest
from dotenv import load_dotenv
import logging
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker


load_dotenv()

os.environ["TESTING"] = "True"

from app.db import SQLALCHEMY_DATABASE_URL as db


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

logger.info(db)


@pytest.fixture
def temp_db():
    try:
        create_database(db)
        logger.info("БД создана")
        base_dir = os.path.dirname(__file__)
        logger.info(base_dir)
        alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))
        logger.info(alembic_cfg)
        command.upgrade(alembic_cfg, "head")
        logger.info("Миграции выполнены")
        yield db
    finally:
        drop_database(db)
        logger.info("БД удалена")


def test_database_connection(temp_db):
    assert database_exists(db), "База данных не существует"

def check_table_exists(engine, table_name):
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def test_tasks_table_exists(temp_db):
    # Создаем движок и сессию для подключения к БД
    engine = create_engine(db)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Проверяем наличие таблицы 'tasks'
    assert check_table_exists(engine, 'tasks'), "Таблица 'tasks' не существует"

if __name__ == "__main__":
    pytest.main([__file__])